# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_mfw_req.h

## Purpose

`bnx2x_mfw_req.h` defines the host-side data contract used by the Broadcom/QLogic `bnx2x` Ethernet driver when management firmware (MFW/MCP) asks for driver information or when the driver publishes offload capabilities to management/NCSI OEM memory. It is a pure interface header: it declares constants, wire-format structs, feature bit masks, and the `union drv_info_to_mcp` buffer layout, but it implements no executable logic.

The header sits between the Linux driver, the MCP shared-memory protocol in `bnx2x_hsi.h`, and the CNIC/L5 offload integration paths. Its layouts are consumed as DMA-visible or firmware-readable records, so field order, field width, padding assumptions, and version/opcode values are part of the firmware ABI.

## Important APIs, Types, And Constants

- `PORT_0`, `PORT_1`, `PORT_MAX`, `NVM_PATH_MAX`: small topology constants used to index per-path/per-port capability arrays. `glob_ncsi_oem_data.fcoe_features` is sized as `[NVM_PATH_MAX][PORT_MAX]`, matching the driver use of `BP_PATH(bp)` and `BP_PORT(bp)`.
- `struct fcoe_capabilities`: four `u32` capability words describing FCoE resource limits and mode support. The masks encode values such as I/Os per connection, logins per port, exchanges, NPIV WWNs, targets, outstanding commands, and stateful/stateless capability flags.
- `struct glob_ncsi_oem_data`: NCSI OEM scratch layout containing a driver version word, reserved words, and the path/port-indexed `fcoe_capabilities` matrix. `bnx2x_main.c` writes FCoE capability data into this layout after CNIC FCoE registration when bootcode advertises FCoE feature support.
- `DRV_INFO_CUR_VER`: current driver-info request protocol version, set to `2`. `bnx2x_handle_drv_info_req()` rejects MFW requests whose `drv_info_control` version bits do not match this value.
- `enum drv_info_opcode`: request selector for management queries. Supported values are `ETH_STATS_OPCODE`, `FCOE_STATS_OPCODE`, and `ISCSI_STATS_OPCODE`.
- `struct eth_stats_info`: Ethernet per-function report. It includes the driver version string, up to three padded MAC-address slots, MTU, feature flags, LSO/offload counters, promiscuous-mode state, queue sizing/depth fields, IOV mode, NetQueue/VMQ count, and VF count.
- `struct fcoe_stats_info`: FCoE report. It includes driver version, padded MAC slots, QoS priority, queue sizing/depth fields, and split high/low 64-bit frame and byte counters.
- `struct iscsi_stats_info`: iSCSI report. It includes driver version, padded MAC slots, QoS priority, boot initiator/target identity and address fields, max frame size, queue sizing/depth fields, split high/low PDU and byte counters, and a PCP priority map table.
- `union drv_info_to_mcp`: shared response buffer overlay containing exactly one of the Ethernet, FCoE, or iSCSI report structs for the active management request.

The header relies on kernel fixed-width aliases such as `u8` and `u32`; it is included via `bnx2x.h` after Linux type headers and `bnx2x_hsi.h` are available.

## Control Flow

The main request path is driven by MCP attentions outside this header:

1. MFW sets shared-memory `drv_info_control` with a version and `drv_info_opcode`.
2. `bnx2x_handle_drv_info_req()` reads `drv_info_control`, compares the version against `DRV_INFO_CUR_VER`, and NACKs unsupported versions through `DRV_MSG_CODE_DRV_INFO_NACK`.
3. The driver locks `bp->drv_info_mutex`, clears `bp->slowpath->drv_info_to_mcp`, and switches on `ETH_STATS_OPCODE`, `FCOE_STATS_OPCODE`, or `ISCSI_STATS_OPCODE`.
4. The selected helper populates the corresponding union member:
   - `bnx2x_drv_info_ether_stat()` fills `struct eth_stats_info` from netdev state, feature flags, programmed MACs, queue sizes, boot mode, promiscuous mode, and SR-IOV VF count when enabled.
   - `bnx2x_drv_info_fcoe_stat()` fills `struct fcoe_stats_info` from FIP MAC, DCBX priority, firmware FCoE queue/statistics memory, and then notifies CNIC so the L5 driver can add storage-specific fields.
   - `bnx2x_drv_info_iscsi_stat()` fills `struct iscsi_stats_info` from CNIC iSCSI MAC and DCBX priority, then notifies CNIC so the L5 driver can add iSCSI-specific fields.
5. The driver writes the DMA address of `bp->slowpath->drv_info_to_mcp` into `drv_info_host_addr_lo/hi` in shared memory and ACKs with `DRV_MSG_CODE_DRV_INFO_ACK`.
6. If the MFW indication mechanism exists, the driver waits briefly for management to signal that it has finished reading the buffer; otherwise it records management ownership with `bp->drv_info_mng_owner`.

The FCoE capability path is separate from the per-request stats path. On `DRV_CTL_ULP_REGISTER_CMD`, when the CNIC ULP type is FCoE and the chip/bootcode/shared-memory gates pass, the driver computes the `glob_ncsi_oem_data.fcoe_features[path][port]` offset from `ncsi_oem_data_addr` and writes one `struct fcoe_capabilities` value, word by word, with `REG_WR()`.

## State And Persistence Behavior

This header defines transient firmware communication state rather than durable storage. `union drv_info_to_mcp` is embedded in `struct bnx2x_slowpath`, which is DMA-mapped and addressable by management firmware for the lifetime of the device instance. Before each driver-info request, the active union storage is zeroed and then populated with the selected report type.

Concurrency and lifetime are managed by consumers, not by this header. `bp->drv_info_mutex` protects `drv_info_to_mcp` from overlap between MCP request handling and version-update flows. `bp->drv_info_mng_owner` prevents some reuse when management has not released the shared buffer after an ACK.

The NCSI OEM FCoE capability data is more persistent from the driver's point of view: it is written into firmware/shared scratch space addressed by `ncsi_oem_data_addr`, indexed by path and port. The header's `glob_ncsi_oem_data` layout is therefore an external memory map, and changes to the structure shape would affect management firmware interpretation.

## Dependencies

- Linux kernel fixed-width integer types (`u8`, `u32`) supplied by the including driver headers.
- `bnx2x.h`, which includes this header and embeds `union drv_info_to_mcp` in `struct bnx2x_slowpath`.
- `bnx2x_hsi.h`, which defines MCP shared-memory structures, driver mailbox commands such as `DRV_MSG_CODE_DRV_INFO_ACK/NACK`, `REQ_BC_VER_4_FCOE_FEATURES`, and shared-memory control fields used by request consumers.
- `bnx2x_main.c`, which populates the Ethernet/FCoE/iSCSI structs, exports the DMA address to MFW, updates management-visible driver versions, and writes `fcoe_capabilities` into NCSI OEM scratch space.
- CNIC/offload integration through `../cnic_if.h` and `bnx2x_cnic_notify()`, because the FCoE and iSCSI reports are partially populated by L5 storage drivers and the FCoE capabilities originate from CNIC ULP registration data.
- Netdev, DCBX, SR-IOV, firmware statistics, and slowpath DMA state, which supply values copied into these report layouts.

## Integration Points

- MCP/MFW driver-info requests: `bnx2x_handle_drv_info_req()` treats `DRV_INFO_CUR_VER`, `enum drv_info_opcode`, and `union drv_info_to_mcp` as the protocol contract for responding to management queries.
- Slowpath DMA memory: `bnx2x_sp_mapping(bp, drv_info_to_mcp)` is published to shared memory so management can read the chosen stats struct.
- Management driver-version reporting: `bnx2x_update_mng_version()` reuses the same union and FCoE/iSCSI stat helpers to ask CNIC for storage driver version strings, then writes compact version words to `func_os_drv_ver`.
- CNIC ULP registration: FCoE registration can write `struct fcoe_capabilities` into the `glob_ncsi_oem_data` memory layout for external management discovery.
- Feature flags: Ethernet feature bits mirror netdev capabilities and boot mode, while FCoE/iSCSI priority fields mirror DCBX traffic-class state.

## Risks And Edge Cases

- Firmware ABI fragility: these structs are external layouts. Reordering fields, changing field sizes, or altering constants such as `DRV_INFO_CUR_VER` without matching firmware support can break MCP/NCSI consumers.
- Endianness ambiguity: comments specify big-endian EUI-48 MAC representation for Ethernet, but many numeric fields are plain host-populated `u32` values. Consumers must preserve the expected firmware ABI conventions.
- Padding and alignment assumptions: MAC fields are eight bytes while Ethernet addresses are six bytes, and the driver intentionally writes with `MAC_PAD` offsets. Incorrect padding logic can shift subsequent MAC slots or expose stale bytes.
- Partial reports: FCoE and iSCSI helpers return early when CNIC is not loaded. The surrounding request path still ACKs supported opcodes after zeroing the union, so management may receive an empty but protocol-valid storage report.
- Shared-buffer ownership: if management does not set the read-done indication, `drv_info_mng_owner` is set and later flows must avoid clobbering the buffer. Bugs here could race management reads against new driver writes.
- Counter consistency: FCoE counters are copied from several firmware statistic sources and accumulated into split high/low fields. Without an atomic snapshot, management may see values from slightly different moments.
- Bounds coupling: `NVM_PATH_MAX` and `PORT_MAX` must remain consistent with `BP_PATH(bp)` and `BP_PORT(bp)` outputs; otherwise the computed `fcoe_features[path][port]` scratch offset could address the wrong management slot.

## Test Signals

- Build coverage for `bnx2x` with and without `CONFIG_BNX2X_SRIOV` verifies that the header remains compatible with the driver include graph and conditional `vf_cnt` population.
- MCP request-path tests or hardware traces should exercise all `drv_info_opcode` values and confirm ACK for supported opcodes, NACK for unsupported opcodes, and NACK when the shared-memory version does not equal `DRV_INFO_CUR_VER`.
- DMA/shared-memory validation should confirm that `drv_info_host_addr_lo/hi` points at the slowpath `union drv_info_to_mcp` and that management reads the expected struct member for each opcode.
- Ethernet report checks should validate version truncation/padding, three padded MAC slots, MTU, checksum/TSO/boot-mode feature bits, promiscuous mode, queue sizes, and VF count under SR-IOV.
- FCoE/iSCSI report checks should cover CNIC-loaded and CNIC-not-loaded cases, DCBX priority propagation, L5 driver version population, and storage counter/identity field population.
- FCoE capability tests should verify that CNIC FCoE registration writes the expected `struct fcoe_capabilities` words to the `glob_ncsi_oem_data.fcoe_features[BP_PATH][BP_PORT]` scratch offset only when chip, shared-memory, and bootcode feature gates are satisfied.

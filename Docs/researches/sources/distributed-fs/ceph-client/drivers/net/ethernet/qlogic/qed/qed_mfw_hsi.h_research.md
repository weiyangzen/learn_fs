# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_mfw_hsi.h

## Purpose

`qed_mfw_hsi.h` defines the host software interface shared by the QED driver and management firmware. It is a firmware ABI header: scratchpad section descriptors, public shared-memory layouts, mailbox command and response codes, event message IDs, NVM image metadata, link/media bitfields, DCBX/LLDP data structures, TLV IDs, and persistent NVM configuration structures are all described here. `qed_mcp.c` relies on these definitions to locate firmware-owned shared memory and to pack or decode mailbox payloads.

The file is intentionally data-heavy and has little executable logic. Its correctness depends on exact structure layout, bit masks, offsets, and enum values matching the MFW image that owns the MCP scratchpad and NVM directory.

## Important Layouts and Types

Scratchpad addressing is based on `offsize_t` and macros `SECTION_OFFSET()`, `QED_SECTION_SIZE()`, `SECTION_ADDR()`, and `SECTION_OFFSIZE_ADDR()`. Offsets and sizes are encoded in dwords, then converted to byte addresses under `MCP_REG_SCRATCH`. `struct mcp_public_data` contains the public SHMEM sections used by the driver: per-PF driver mailboxes, per-PF MFW mailboxes, global data, path data, port data, and function data.

`struct public_drv_mb` is the driver-to-firmware mailbox. It contains `drv_mb_header`, `drv_mb_param`, `fw_mb_header`, `fw_mb_param`, pulse mailboxes, and `union drv_union_data`. Header fields split sequence numbers from command or response codes. `union drv_union_data` is the bounded inline payload for link configuration, WOL MAC, raw NVM/debug data, stats, resource info, BIST image attributes, load request/response, mdump retain data, attribute writes, LLDP stats, PCIe stats, and trace filters.

`struct public_mfw_mb` is the firmware-to-driver event channel. It exposes `sup_msgs`, a packed message array, and a matching acknowledgement array. `enum MFW_DRV_MSG_TYPE` defines event slots such as link change, VF disabled, LLDP/DCBX updates, recovery, bandwidth update, S-tag update, protocol stats requests, fan/temperature failure, transceiver state, critical error, TLV request, OEM configuration, generic IDC, and debug dump requests.

`struct public_global`, `struct public_path`, `struct public_port`, and `struct public_func` are the main shared-memory records consumed by the driver. Global fields include path/port counts, CMT teaming, temperatures, MFW version, running bundle, BMC/NCSI counters, and device attributes. Path fields include VF FLR disabled bitmap and process-kill counter. Port fields include link status, PHY configuration address, media type, LLDP/DCBX MIBs, transceiver data, EEE status, OEM/UFP config, pause flood monitor, NIG counters, and traffic class counters. Function fields include MTU, MSI-X count, function protocol/bandwidth config, virtual-link status, MAC, FCoE WWNs, outer VLAN/stag, VF-disabled ACK bitmap, driver ID, OEM function config, and driver version.

Link and PHY definitions include `struct eth_phy_cfg`, speed/autoneg constants, pause bits, loopback modes, EEE config, base FEC, extended FEC, and extended speed advertisement fields. Link state bits in `public_port.link_status` encode link up, speed/duplex, autoneg, PFC, partner advertised speeds, flow control, SFP fault, signal/fault flags, FEC active mode, and external PHY link state.

NVM definitions include `struct nvm_cfg1_glob`, `struct nvm_cfg1_port`, `struct nvm_cfg1_func`, `struct nvm_cfg1`, `struct nvm_cfg`, scratchpad/static-init descriptors, NVM image directory structures, VPD image format, hardware-set images, and NVM metadata binary option records. `enum nvm_image_type` maps image IDs such as MFW bundles, NVM_CFG1, default config, mdump, iSCSI/FCoE configs, PHY firmware, recovery, PLDM, key-certificate images, hardware dump, and idle check.

Mailbox command definitions are in `enum drv_msg_code_enum`; responses are in `enum fw_msg_code_enum`. Parameter masks describe NVM chunk offsets/sizes, VF MSI-X configuration, management updates, unload WOL modes, resource allocation protocol versions, BIST subcommands, feature support advertisement, transceiver I2C reads, NVM config options, debug data size, engine affinity, PPFID bitmap, and management lockdown status.

## Control Flow Implied by the HSI

The driver first reads the public section table from the MCP scratchpad, then uses section offsize descriptors to locate the PF, port, path, and global records relevant to its hardware function. It sends commands by writing `union_data`, `drv_mb_param`, and `drv_mb_header` with a new sequence number, then polls for `fw_mb_header` with the same sequence and a firmware response code. MFW events flow in the opposite direction through `public_mfw_mb.msg` and are acknowledged by copying observed message dwords into `public_mfw_mb.ack`.

Load arbitration uses `struct load_req_stc` and `struct load_rsp_stc` with driver role, lock timeout, force-load request, avoid-reset flag, existing driver version, firmware version, MFW HSI version, and driver-exists flag. Link setup uses `struct eth_phy_cfg`, while link indications are read from `public_port.link_status` and virtual link is read from `public_func.status`.

Persistent NVM operations use small mailbox payloads and parameter-encoded offsets/sizes. Larger semantic objects such as complete NVM images are discovered through BIST image attributes and NVM directory metadata, then read in chunks by the MCP implementation.

## State and Persistence Behavior

The HSI represents three state classes. Runtime volatile state lives in the MCP scratchpad public data: mailboxes, event bits, link state, DCBX/LLDP MIBs, process-kill counters, UFP/OEM settings, and function configuration reflected by firmware. Durable state lives in NVM image structures and `nvm_cfg1` configuration records. Diagnostic state spans MFW trace buffers, mdump retained data, debug-data mailbox payloads, hardware dump image types, and trace module metadata.

Because the header is the ABI contract, field additions are append-oriented and many structures include reserved arrays. Drivers must use advertised capabilities and response codes rather than assuming all fields or commands are supported by every MFW revision.

## Dependencies and Integration Points

This header assumes QED register constants such as `MCP_REG_SCRATCH`, `CPU_SPAD_BASE`, and `STATIC_INIT_BASE`, kernel integer types, `BIT()`, and common field macros supplied by surrounding QED/Linux includes. It is consumed directly by `qed_mcp.c` and indirectly by DCBX, NVM, debug, SR-IOV, link, and management code. It integrates firmware protocol with Linux-visible operations such as ethtool NVM access, devlink-style diagnostics, link settings, WoL, VF provisioning, and hardware recovery.

The TLV enum is an integration contract with management reporting. It spans device properties, configuration, port data, function data, FCoE, iSCSI, PCIe error reporting, NCSI counters, and RDMA driver version reporting.

## Risks and Edge Cases

The main risk is ABI drift. A changed mask, enum value, structure packing assumption, or section size can cause the driver to read the wrong shared-memory field or send a malformed mailbox payload. Since many fields are bit-packed, field macros must be used consistently and caller code must mask/shift with the HSI definitions rather than open-coded constants.

Endianness is subtle. Some mailbox event data is treated as big-endian by MFW, while normal register reads return host-order dwords after bus semantics. `qed_mcp.c` handles this explicitly for MFW messages and driver version/MAC payloads; new users of this header need to preserve those conventions.

Compatibility is also a concern. Older MFW may not support HSI version 2 load requests, feature-support commands, resource allocation versions, BIST image enumeration, debug-data send, engine config, PPFID bitmap, or enhanced system lockdown. The driver must handle `FW_MSG_CODE_UNSUPPORTED`, old-HSI refusal, and absent capability bits gracefully.

NVM structures describe durable firmware storage. Incorrect offsets, lengths, or directory sequence handling can corrupt firmware images or configuration. Tests and tooling should treat write paths as high risk and prefer read-only validation unless running in a controlled hardware lab.

## Test Signals

HSI validation signals include compile-time structure availability, command/response numeric matching with MFW documentation, SHMEM section size sanity, `sup_msgs` readiness, link status decode correctness for each speed/FEC/media combination, load request fallback behavior, unsupported-command handling, NVM image directory parsing, event ack writes, and feature bit negotiation. Hardware tests should exercise multiple MFW revisions to catch ABI drift and confirm that reserved/extended fields remain backward compatible.

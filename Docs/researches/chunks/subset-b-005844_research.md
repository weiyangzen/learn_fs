# sources/distributed-fs/ceph-client/include/linux/bnxt/hsi.h lines 5292-11301

## Scope

This chunk covers the tail half of Broadcom NetXtreme-C/E `hsi.h`, a generated host/software interface header for HWRM mailbox commands, DMA payloads, hardware statistics blocks, doorbell records, and firmware status registers. The range begins in the extended port-statistics area and runs to the end of the header guard.

The file is ABI definition rather than executable logic. Its "APIs" are packed request/response structs, command-specific error payloads, fixed-size statistics layouts, bit masks, enum-like constants, and address/handle fields that the bnxt driver and firmware must interpret identically.

## Purpose

The chunk defines the HWRM command surface used after basic function/port setup:

- Port, PHY, timestamp, loopback, ECN, LED, FDR, and MAC capability/statistics commands.
- Queue and QoS configuration for PFC, priority-to-CoS mapping, CoS bandwidth, DSCP-to-priority mapping, and PFC watchdog timeout.
- VNIC, RSS/TPA/placement, RSS/COS/LB context, ring, completion-ring moderation, and ring-group allocation commands.
- CFA classification/filtering/flow/tunnel/encapsulation/EEM commands, including L2, tunnel, n-tuple, decap, flow, VFR, advanced-flow capability, and tunnel destination-port management.
- Context, PCIe, and generic statistics commands.
- Firmware reset/status/time/structured-data/livepatch and forwarded-response commands.
- Temperature, WoL, debug, crashdump, coredump, ring debug, log flush, NVM read/write/update/variable/defrag, and self-test commands.
- Doorbell encoding structs and host communication firmware status records used outside the HWRM mailbox path.

## Important APIs, Types, and Data

Common HWRM command structs in this range follow the same ABI shape: request structs start with `req_type`, `cmpl_ring`, `seq_id`, `target_id`, and `resp_addr`; response structs start with `error_code`, `req_type`, `seq_id`, `resp_len`, and end with a `valid` byte. Drivers must fill DMA addresses, sizes, flags, enables, handles, and IDs in little-endian fields unless a field is explicitly network-endian.

Port and PHY definitions include `hwrm_port_qstats_ext_*`, `hwrm_port_lpbk_qstats_*`, `port_lpbk_stats`, `hwrm_port_ecn_qstats_*`, `port_stats_ecn`, clear-stat commands, `hwrm_port_ts_query_*`, `hwrm_port_phy_qcaps_*`, I2C/MDIO read/write commands, LED config/query/capability structs, `hwrm_port_phy_fdrstat_*`, and `hwrm_port_mac_qcaps_*`. These expose counter buffers, timestamp queries, PHY speed/EEE/PAM4 capabilities, external module register access, LED state/color/blink policy, and MAC offload capabilities.

Queue and QoS definitions include `hwrm_queue_qportcfg_*`, `hwrm_queue_qcfg_*`, `hwrm_queue_cfg_*`, PFC enable query/config commands, priority-to-CoS query/config commands, CoS bandwidth query/config commands, DSCP capability/query/config commands, and PFC watchdog timeout capability/config/query commands. Repeated per-priority and per-queue fields model the eight traffic classes/priorities common in DCB/PFC setups.

VNIC and ring definitions include `hwrm_vnic_alloc/update/free/cfg/qcaps`, TPA config/query, RSS config/query with RSS key and ring table DMA pointers, placement-mode config, RSS/COS/LB context alloc/free, `hwrm_ring_alloc/free/reset`, interrupt aggregation capability/query/config, and ring-group alloc/free. Important handles include `vnic_id`, `rss_ctx_idx`, `rss_cos_lb_ctx_id`, `ring_id`, `logical_ring_id`, `stat_ctx_id`, completion ring IDs, NQ IDs, and ring group IDs.

CFA and tunnel definitions include L2 filter alloc/free/config, RX mask programming, tunnel filter alloc/free, VXLAN IPv4/IPv6 and encapsulation data layouts, encap record alloc/free, n-tuple alloc/free/config, decap alloc/free, generic flow alloc/free/info/stats, VFR alloc/free, EEM capability/config/query/op, advanced flow management capabilities, and tunnel destination port query/alloc/free. Flow-like responses return firmware handles plus `flow_id` values with value/type/direction bit fields. Special flow IDs are defined as `DEFAULT_FLOW_ID`, `ROCEV1_FLOW_ID`, `ROCEV2_FLOW_ID`, and `ROCEV2_CNP_FLOW_ID`.

Statistics and management definitions include `ctx_hw_stats`, `ctx_hw_stats_ext`, stat-context alloc/free/query/clear commands, PCIe stats v1/v2, generic software/hardware stats, firmware reset/status/time commands, structured-data headers and DCBX application data, livepatch query/apply commands, forwarded response and forwarded async-event commands, temperature query, WoL filter allocation/query/free/reason commands, debug direct-read/capability/config/crashdump/coredump/ring/log commands, NVM directory/read/write/modify/update/variable/defrag commands, self-test query/execute/IRQ commands, `dbc_dbc`, `db_push_start`, `db_push_end`, `db_push_info`, `fw_status_reg`, `hcomm_status`, and `HCOMM_STATUS_STRUCT_LOC`.

Command-specific error structs are part of the ABI for richer diagnostics, including RSS config, VNIC placement, CFA RX mask, n-tuple/flow allocation, firmware structured-data get/set, livepatch, NVM write/install/get-variable/set-variable/defrag, and FDR status.

## Control Flow

The header does not implement control flow directly, but it encodes expected driver/firmware flows.

Resource lifecycles are allocate/configure/query/free. VNICs are allocated, optionally updated and configured for default rings, RSS/COS/LB rules, MRU, checksum completion mode, and placement modes, then freed. Rings are allocated from page-table DMA descriptors, associated with completion/rx/nq/stat contexts as needed, optionally reset or configured for moderation, and freed. Ring groups bind completion, rx, aggregate, and stat context IDs.

Receive steering and classification flow through capability discovery, filter/flow allocation, optional reconfiguration, statistics/info queries, and explicit free. L2/tunnel/n-tuple/decap/flow commands share a pattern of selector fields gated by `enables`, action flags such as drop/loopback/mirror/destination, returned handles, and counters. Tunnel destination-port commands query current ownership, allocate a UDP destination port or ULP dynamic parser slot, then free by type/id.

Statistics flows either return counters inline in the HWRM response or DMA them into host buffers. Port, PCIe, generic, DSCP, RSS, debug, coredump, WoL, NVM, and structured-data commands use host physical addresses and explicit lengths, so the caller must allocate, map, size, and keep buffers alive until firmware completion.

Firmware and persistent operations are sequenced through status/capability checks before mutation. Firmware reset reports the self-reset requirement; `hwrm_fw_qstatus_output` reports pending NVM option actions; livepatch query reports installed/active patch versions; NVM write/modify/install/defrag commands expose verification, reset-required, anti-rollback, space, signature, and checksum outcomes.

Doorbell records encode a separate MMIO/control path. `dbc_dbc` identifies queue index, XID, path, type, valid/debug bits, epoch, and toggle state. `db_push_start` and `db_push_end` encode push-buffer producer index fragments and path/type bits in a 64-bit doorbell value, with `db_push_info` carrying push size and index.

## State and Persistence Behavior

Most structs describe firmware-resident state, not kernel-owned persistent storage. Alloc commands create firmware objects identified by returned IDs or handles; free commands destroy them. Config commands mutate device state such as queue service profile, PFC enablement, CoS bandwidth, DSCP mapping, VNIC behavior, RSS key/table selection, TPA/GRO settings, ring interrupt moderation, filter actions, tunnel destination ports, EEM mode, WoL filters, crashdump destination, and firmware structured data.

Counter state is cumulative until explicitly cleared or masked according to command flags. Port/stat-context/generic counter query commands include counter-mask bits, and clear commands exist for port, loopback, and stat-context counters. Flow free returns packet/byte counts, while flow stats can batch up to ten handles/IDs.

Persistent or semi-persistent state is concentrated in NVM, firmware livepatch, WoL, crashdump configuration, and structured data. NVM directory entries, firmware packages, variables, defragmentation, batch updates, force flush, factory defaults, encryption/authentication modes, and install reset requirements can survive driver unload or device reset. WoL filters and wake reasons affect suspend/resume behavior. Crashdump and coredump commands expose diagnostic state after firmware failure.

The final `fw_status_reg` and `hcomm_status` structs model host-readable firmware health. `hcomm_status` contains a signature/version and an encoded location for `fw_status_reg`, while status bits mark ready, degraded image, recoverable failure, crashdump in progress/complete, shutdown, no-master crash, recovery, and manufacturing debug status.

## Dependencies and Integration Points

The definitions depend on Linux fixed-width and endian-annotated types such as `u8`, `u32`, `u64`, `__le16`, `__le32`, `__le64`, `__be16`, and `__be32`. Several nested arrays are marked `__packed`; callers must not assume natural C padding beyond the generated layout and documented byte sizes.

Integration is primarily with the bnxt Ethernet/RDMA stack and firmware HWRM mailbox layer. The driver builds these request structs, writes DMA-coherent response buffers, waits for completions, checks `error_code` and `valid`, decodes command-specific errors, and stores returned IDs in driver resources. Linux networking integrations include ethtool stats/self-tests, DCB/PFC/ETS controls, RSS and RX flow steering, XDP/RFS/ntuple offload, tunnel offload, WoL, devlink/firmware update diagnostics, coredump collection, and PCIe health reporting.

The chunk also bridges L2 and RoCE paths. Queue service profiles, PFC, RoCE-only/dual VNIC modes, RoCE flow IDs, doorbell path encodings, stat-context RoCE flags, and debug trace types all require coordination with RDMA upper-layer code and firmware path selection.

Endian integration is mixed by design. HWRM transport fields and most numeric handles are little-endian, while packet-header fragments embedded in encapsulation records use big-endian network order. Code that copies protocol headers into `hwrm_vxlan_ipv4_hdr`, `hwrm_vxlan_ipv6_hdr`, `hwrm_cfa_encap_data_vxlan`, or DCBX application data must preserve network byte order.

## Risks

ABI drift is the dominant risk. Because this is generated HSI, any field offset, size, endian annotation, valid byte location, mask value, enum value, or array length mismatch can cause firmware command failures or silent misconfiguration.

The `enables` masks are critical. Many request structs contain valid-looking fields that firmware must ignore unless the matching enable bit is set. Missing enable bits can make a config command appear successful while leaving state unchanged; extra enable bits can apply uninitialized data.

Resource leaks and stale handles are high risk. VNICs, RSS contexts, rings, ring groups, filters, flows, tunnel ports, encap records, stat contexts, EEM contexts, WoL filters, and NVM directory entries all use firmware-owned IDs. Reusing freed IDs, freeing in the wrong order, or losing IDs during reset recovery can leave firmware state inconsistent with the driver.

Host DMA address/length fields are security- and stability-sensitive. RSS tables, stat buffers, DSCP tables, multicast/VLAN tables, debug reads, coredump buffers, WoL patterns, structured data, livepatch payloads, and NVM buffers require correctly mapped memory, correct size units, and firmware-visible lifetime. Incorrect lengths can truncate diagnostics or expose stale memory contents to firmware DMA.

Counter semantics can mislead diagnostics. Some query flags include counter masks, clear commands reset hardware state, and flow free returns final counters. Tests and support tools must distinguish inline response counters from DMA-filled statistics blocks and from counters that were cleared, masked, or reset by firmware.

NVM and firmware commands have persistent blast radius. Write/modify/install/defrag/set-variable/livepatch/reset commands can alter boot images, options, patch state, or reset requirements. Result codes include authentication, anti-rollback, checksum, no-space, item-locked, unsupported-platform, and reset-required states that callers must surface accurately.

Mixed endian packet-header structs are easy to misuse. Treating network-order header fields as little-endian HWRM fields would create malformed encapsulation records or DCBX application selectors.

Debug and coredump commands can expose privileged device memory or sensitive crash data. Capability flags such as restricted register access, component disable flags, destination selection, compression flags, and sequence/more indicators need strict handling.

## Test and Validation Signals

Build validation should compile all bnxt users of this header with sparse/endian checks enabled, catching incorrect `__le*`/`__be*` assignments and struct member name drift.

ABI validation should compare generated struct sizes and key offsets against the firmware HSI specification for every command family in this chunk, especially large layouts such as queue port config, CoS bandwidth config/query, ring alloc, CFA flow info, PCIe stats v2, self-test list, and NVM device info.

Mailbox tests should verify the common request/response contract: correct `req_type`, sequence matching, response DMA address use, `resp_len`, `valid` byte handling, nonzero `error_code` paths, and command-specific error decoding.

Lifecycle tests should allocate/configure/query/free VNICs, RSS contexts, rings, ring groups, stat contexts, L2/tunnel/n-tuple/flow filters, encap records, tunnel destination ports, EEM state, and WoL filters. They should include reset recovery and repeated create/free loops to catch stale handles.

QoS tests should exercise PFC enable/watchdog, priority-to-CoS mapping, CoS bandwidth units/scales, DSCP table DMA upload/download, and asymmetric TX/RX path flags.

Data-path tests should validate RSS hash types, RSS key/table programming, ring-select modes, TPA/GRO/tunnel TPA flags, RX mask multicast/VLAN/promiscuous modes, ntuple/RFS/XDP conflicts, tunnel offload destination ports, and encapsulation header byte order.

Statistics tests should compare port, loopback, ECN, stat-context, PCIe, generic, flow, and debug ring counters before and after clear/reset/free operations. DMA-backed stats should verify firmware writes exactly the negotiated size.

Firmware/NVM/debug tests should cover status queries, self-reset status, livepatch query/apply error paths, structured-data bad-header/bad-id errors, NVM write/modify/install/variable/defrag result codes, WoL wake reason retrieval, temperature unavailable flags and thresholds, coredump list/retrieve pagination via `MORE`, and crashdump destination configuration.

Doorbell tests should validate bit packing for `dbc_dbc`, `db_push_start`, `db_push_end`, and `db_push_info` against producer index, XID, path, type, epoch/toggle, and push-buffer ping/pong behavior.

## Cross-Chunk Notes

This chunk starts mid-file and relies on earlier definitions for the HWRM transport constants, completion formats, initial port stats fields, and command IDs. The merge lane should combine it with preceding chunks for the complete `hsi.h` report, but this chunk is self-contained for the command families and terminal firmware/doorbell/status records it defines.

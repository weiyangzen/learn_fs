# subset-b-004380 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/cnic_defs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/cnic_defs.h

## Purpose
`cnic_defs.h` is a firmware/hardware ABI header for the Broadcom/QLogic CNIC storage-offload path used by the Ceph-client kernel source snapshot. It defines the kernel work queue entries, kernel completion queue entries, per-storm firmware contexts, FCoE task and connection records, iSCSI PDU/task/connection records, TCP offload context fragments, and L5 connection-manager/passive-open structures consumed by the CNIC driver and related Broadcom Ethernet drivers.

The file is not algorithmic application code. It is a layout contract between host driver code, DMA memory, and on-chip firmware. Most structures are deliberately shaped with `__BIG_ENDIAN`/`__LITTLE_ENDIAN` conditional member order, fixed-width integer fields, and companion mask/shift macros. A driver change that looks like ordinary C cleanup can break the device ABI.

## Important APIs, Types, and Functions
There are no functions. The public API is the set of opcodes, completion statuses, bit masks, enums, unions, and C structs used to build firmware commands and interpret completions.

The top-level command families include `L2_KWQE_OPCODE_VALUE_*`, `L4_KWQE_OPCODE_VALUE_*`, `L5CM_RAMROD_CMD_ID_*`, `FCOE_RAMROD_CMD_ID_*`, `L4_KCQE_OPCODE_VALUE_*`, and `L4_KCQE_COMPLETION_STATUS_*`. These identify flush/free operations, TCP connect/reset/close/update/init operations, page/offload operations, L5 connection manager ramrods, FCoE init/stat/connection ramrods, and KCQ completion classes.

L4/TCP work and completion entries include `struct l4_kcq`, `struct l4_kcq_upload_pg`, `struct l4_kwq_close_req`, `struct l4_kwq_connect_req1`, `struct l4_kwq_connect_req2`, `struct l4_kwq_connect_req3`, `struct l4_kwq_offload_pg`, `struct l4_kwq_reset_req`, `struct l4_kwq_update_pg`, and `struct l4_kwq_upload`. These describe the multi-WQE TCP connection setup sequence, IPv6 extension data, keepalive and MSS settings, L2 page/offload information, and close/reset/upload completions.

The per-storm aggregative and non-aggregative contexts include `cstorm_iscsi_ag_context`, `tstorm_fcoe_ag_context`, `tstorm_tcp_tcp_ag_context_section`, `tstorm_iscsi_ag_context`, `ustorm_fcoe_ag_context`, `ustorm_iscsi_ag_context`, `xstorm_fcoe_ag_context`, `xstorm_tcp_tcp_ag_context_section`, `xstorm_iscsi_ag_context`, and `xstorm_l5cm_ag_context`. These represent firmware-maintained state for Cstorm/Tstorm/Ustorm/Xstorm engines: queue membership, producer/consumer values, timers, decision rules, TCP sequence variables, offload state flags, and completion rules.

The FCoE section defines Fibre Channel headers and payloads (`fcoe_fc_hdr`, `fcoe_fcp_rsp_payload`, `fcoe_fcp_cmd_payload`, `fcoe_fc_frame`), KWQE/KCQE forms (`fcoe_kcqe`, `fcoe_kwqe_header`, `fcoe_kwqe_init1/2/3`, `fcoe_kwqe_conn_offload1/2/3/4`, `fcoe_kwqe_conn_enable_disable`, `fcoe_kwqe_conn_destroy`, `fcoe_kwqe_destroy`, `fcoe_kwqe_stat`, `union fcoe_kwqe`), task context entries (`fcoe_task_ctx_entry`, `fcoe_tce_*`, `fcoe_sqe`, `fcoe_xfrqe`), storm contexts (`ustorm_fcoe_st_context`, `xstorm_fcoe_st_context`, `fcoe_context`), and ramrod parameter wrappers (`fcoe_init_ramrod_params`, `fcoe_stat_ramrod_params`, `fcoe_conn_offload_ramrod_params`, `fcoe_conn_enable_disable_ramrod_params`).

The iSCSI section defines CQ doorbell state, host queue BDs, PDU header overlays, task contexts, and full connection context. Important types include `iscsi_cq_db_prod_pnd_cmpltn_cnt`, `iscsi_cq_db_*`, `cstorm_iscsi_st_context`, `ustorm_iscsi_st_context`, `tstorm_iscsi_st_context`, `xstorm_iscsi_st_context`, `iscsi_context`, `union iscsi_pdu_headers_little_endian`, `iscsi_hq_bd`, `iscsi_l2_ooo_data`, and `iscsi_task_context_entry`. The PDU header structs model command, data-out, login, logout, task-management, text, and NOP-out headers in firmware-visible layout.

The L5 connection-manager section defines IPv6 and socket-address buffers, active/passive connection buffers, port listener attributes, passive connection search entries, slow-path elements, termination variables, and out-of-order enums: `ip_v6_addr`, `l5cm_conn_addr_params`, `l5cm_active_conn_buffer`, `l5cm_hash_input_string`, `l5cm_opaque_buf`, `l5cm_pcs_entry`, `l5cm_spe`, `l5cm_term_vars`, `tstorm_l5cm_tcp_flags`, `xstorm_l5cm_tcp_flags`, `enum tcp_ooo_event`, and `enum tcp_tstorm_ooo`.

## Control Flow and State
The file has no direct runtime control flow, but it defines several firmware-driven flows. A TCP offload connect is represented as a sequence of `l4_kwq_connect_req1`, optional IPv6 `l4_kwq_connect_req2`, and `l4_kwq_connect_req3`, followed by KCQ completions such as `L4_KCQE_OPCODE_VALUE_CONNECT_COMPLETE`. Close and abort flows use `l4_kwq_close_req` and `l4_kwq_reset_req`, with corresponding close/reset completion or remote close/reset indications.

FCoE control flow is modeled as ramrod batches: init is split across `fcoe_kwqe_init1/2/3`, connection offload across `fcoe_kwqe_conn_offload1/2/3/4`, then enable/disable, destroy, statistics, and function teardown use their own KWQE forms. Firmware completions are returned through `fcoe_kcqe`, with `FCOE_KCQE_RAMROD_COMPLETION`, layer-code, and linked-entry flags.

iSCSI control flow is stateful across Cstorm/Ustorm/Tstorm/Xstorm contexts. Host queues, request queues, R2T queues, completion queues, PDU header overlays, digest flags, task tables, and TCP sequence variables persist in DMA-visible context memory. Firmware consumes `iscsi_hq_bd` headers, updates producer/consumer and pending-completion fields, and uses task-context unions to track read/write, R2T, and retransmit state.

L5 connection-manager flow captures active connect parameters and passive SYN/final-ACK reduction. Passive connections use a hash input string, opaque listener data, SYN/ACK-specific segment unions, PCS attributes, and a receive segment buffer. Termination state is shared with iSCSI-style TCP termination variables.

## State and Persistence Behavior
The persistent state is external to the C translation unit: host DMA rings, firmware context memory, status/completion queues, doorbell records, page-block lists, and hardware timer blocks. Structures such as `fcoe_context` and `iscsi_context` aggregate per-storm state and are expected to be written to firmware-visible memory at exact offsets. Producer/consumer indices, queue toggle bits, sequence counters, digest flags, task IDs, VLAN fields, TCP timers, and connection IDs survive across individual function calls because firmware and driver both update them over time.

The file uses explicit little-endian annotations for many FCoE fields and conditional byte ordering for many mixed-width records. That means persistence includes byte layout, not just semantic values. A host must initialize reserved fields and masks correctly because firmware may interpret entire words, not only named C members.

## Dependencies and Integration Points
This header assumes kernel fixed-width types (`u8`, `u16`, `u32`, `__le16`, `__le32`) and shared HSI helpers such as `struct regpair`, `struct spe_hdr`, and `struct timers_block_context`, which are provided by adjacent Broadcom HSI headers in the bnx2x/CNIC include chain. It is tightly coupled to `cnic_if.h` through common KWQE/KCQE concepts and to CNIC implementation files that fill KWQE arrays, post ramrods, handle completions, and allocate context memory.

Integration points include the CNIC core driver, Broadcom bnx2/bnx2x Ethernet drivers exposing CNIC offload hooks, iSCSI upper-layer protocol code, FCoE offload code, firmware loading/HSI version compatibility, PCI DMA allocation, interrupt/KCQ delivery, status block handling, and management of context IDs (`cid`, `pg_cid`, `l5_cid`, FCoE connection IDs, and iSCSI connection IDs).

## Risks
The dominant risk is ABI drift. Reordering fields, changing integer types, removing duplicate endian branches, adjusting reserved fields, or renaming masks without checking generated firmware expectations can corrupt firmware-visible command/context layout. Endian risk is high because many structs are manually reordered rather than purely using `__le*` fields.

Other risks include mismatched opcode/status values, incorrect layer-code bits, wrong linked-WQE flags in multi-entry commands, stale FCoE/iSCSI HSI versions, uninitialized reserved fields leaking into firmware decision bits, producer/consumer wrap mistakes, task-ID/toggle-bit misuse, DMA address truncation through high/low fields, VLAN bitfield confusion, digest negotiation mismatches, and TCP offload state divergence between host and storm contexts.

Security and reliability risk is concentrated where firmware interprets network-originated storage protocol headers. The iSCSI PDU overlays and FCoE task contexts need strict validation by callers before they are handed to hardware; this header itself cannot enforce bounds, digest validity, task table limits, or queue occupancy.

## Test Signals
Useful build-time signals include compiling both little-endian and big-endian configurations where possible, sparse/endian checking, struct size/offset assertions against firmware HSI documentation or generated values, and allmodconfig coverage for CNIC, bnx2x, iSCSI, and FCoE combinations.

Runtime signals include successful CNIC registration, TCP offload connect/close/reset completions, iSCSI login and data I/O under digest and non-digest modes, FCoE init/offload/enable/stat/destroy ramrod completions, KCQ layer/opcode decoding, error-path completions for timeout/parity/NIC errors, out-of-order TCP handling, IPv6 connect setup, VLAN-tagged offload traffic, stress with queue wraparound, and reset/remove/reprobe without stale context or DMA state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/cnic_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/cnic_if.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/cnic_if.h

## Purpose
`cnic_if.h` defines the in-kernel interface for the QLogic/Broadcom CNIC core network driver. It is the narrow contract between upper-layer protocol clients such as RDMA, iSCSI, FCoE, and L4 connection-management consumers, and the lower Broadcom Ethernet drivers that provide hardware queues, context memory, interrupts, and control operations.

The header exposes module version metadata, ULP type numbering, generic KWQE/KCQE container formats, driver/CNIC control commands, CNIC device/socket abstractions, and callback tables. It is source-level glue rather than a standalone driver implementation.

## Important APIs, Types, and Functions
ULP identifiers are `CNIC_ULP_RDMA`, `CNIC_ULP_ISCSI`, `CNIC_ULP_FCOE`, and `CNIC_ULP_L4`, with `MAX_CNIC_ULP_TYPE_EXT` and `MAX_CNIC_ULP_TYPE` defining supported bounds. Ring sizing uses `CNIC_PAGE_BITS`, `CNIC_PAGE_SIZE`, `CNIC_PAGE_ALIGN`, and `CNIC_PAGE_MASK`, capped at 16 KiB even on larger CPU page sizes.

`struct kwqe` and `struct kwqe_16` are generic work queue entries submitted to firmware. Their opcode and layer fields are extracted through masks such as `KWQE_OPCODE_MASK`, `KWQE_OPCODE_SHIFT`, `KWQE_OPCODE(x)`, and `KWQE_FLAGS_LAYER_MASK_*`. `struct kcqe` is the generic completion queue entry with completion, layer, next-entry, and opcode masks such as `KCQE_RAMROD_COMPLETION`, `KCQE_FLAGS_LAYER_MASK_*`, `KCQE_FLAGS_NEXT`, and `KCQE_OPCODE(op)`.

CNIC-to-driver and driver-to-CNIC control payloads are represented by `struct cnic_ctl_info`, `struct cnic_ctl_completion`, `struct drv_ctl_info`, `struct drv_ctl_spq_credit`, `struct drv_ctl_io`, `struct drv_ctl_l2_ring`, and `struct drv_ctl_register_data`. Command constants include `CNIC_CTL_STOP_CMD`, `CNIC_CTL_START_CMD`, stats retrieval commands, `DRV_CTL_IO_WR_CMD`, `DRV_CTL_CTX_WR_CMD`, `DRV_CTL_RET_*_SPQ_CREDIT_CMD`, L2 start/stop, iSCSI stopped notification, and ULP register/unregister.

Lower-driver callbacks are grouped in `struct cnic_eth_dev`: registration hooks, KWQE submission for 32-byte and 16-byte entries, driver control, FC NPIV table retrieval, IRQ metadata, PCI/MMIO information, context table sizing, connection limits, FCoE WWNs, and feature state flags such as `CNIC_DRV_STATE_NO_ISCSI`, `CNIC_DRV_STATE_NO_FCOE`, `CNIC_DRV_STATE_HANDLES_IRQ`, and `CNIC_DRV_STATE_USING_MSIX`.

Upper-layer and CNIC-core callbacks are grouped in `struct cnic_dev` and `struct cnic_ulp_ops`. `struct cnic_dev` exports device registration, KWQE submission, socket connection management (`cm_create`, `cm_destroy`, `cm_connect`, `cm_abort`, `cm_close`, `cm_select_dev`), iSCSI netlink receive, FC NPIV table access, device flags, limits, stats address, FCoE capabilities, and private data. `struct cnic_ulp_ops` lets ULP clients receive init/exit/start/stop, KCQE indication, network events, connection completion/close/abort callbacks, remote close/abort indications, iSCSI netlink send, and stats callbacks.

The only declared functions are `cnic_register_driver(int ulp_type, struct cnic_ulp_ops *ulp_ops)` and `cnic_unregister_driver(int ulp_type)`, used by ULP modules to bind and unbind from the CNIC core.

## Control Flow and State
The normal flow starts with an Ethernet driver registering CNIC support through callbacks in `cnic_eth_dev`, after which the CNIC core exposes a `cnic_dev` to interested ULPs. ULPs call `cnic_register_driver()` with a `cnic_ulp_ops` callback table. The CNIC core calls ULP init/start/stop/exit as devices transition up and down, and uses RCU-protected callback dispatch when invoking registered handlers.

Work submission flows from ULP or CNIC code through `cnic_dev.submit_kwqes()` or `submit_kwqes_16()` into lower-driver hooks `drv_submit_kwqes_32()` or `drv_submit_kwqes_16()`. Firmware completions return as `kcqe` arrays through `indicate_kcqes()`, with opcode and layer bits demultiplexing storage protocol or L4 events.

Connection-management flow uses `struct cnic_sock`. The caller creates a socket with source/destination address, ports, VLAN, MACs, MTU, CIDs, ULP type, keepalive parameters, TCP options, buffers, and flags. CNIC then schedules offload/connect/close/abort work and reports completion through `cm_*_complete`, `cm_remote_close`, or `cm_remote_abort` callbacks.

Control flow between CNIC and the Ethernet driver uses `cnic_ctl_info` and `drv_ctl_info` command unions. These commands cover start/stop, completions, stats, IO/context writes, context table updates, SPQ credit returns, L2 ring start/stop, and ULP registration state.

## State and Persistence Behavior
`struct cnic_dev` persists for the lifetime of a CNIC-capable network device and anchors the netdev, PCI device, MMIO register view, registration callbacks, feature limits, flags, reference count, MAC address, stats pointers, FCoE capabilities, and private CNIC implementation data. `CNIC_F_CNIC_UP`, `CNIC_F_BNX2_CLASS`, and `CNIC_F_BNX2X_CLASS` classify device state and hardware family.

`struct cnic_sock` persists per offloaded connection. Its state includes host and firmware CIDs, local/remote IP and port, MAC/VLAN data, offload flags, TCP options, keepalive timers, buffers, sequence seed, reference count, state word, and up to three embedded KWQEs used by the connection flow. Socket flags such as `SK_F_INUSE`, `SK_F_OFFLD_COMPLETE`, `SK_F_CONNECT_START`, `SK_F_CLOSING`, and `SK_F_HW_ERR` model lifecycle and error state.

`struct cnic_eth_dev` is the lower-driver capability snapshot. Its context table offsets, maximum connection counts, IRQ array, SPQ credit interfaces, and management firmware stats pointers must remain consistent with the lower driver and firmware for the lifetime of registration.

## Dependencies and Integration Points
The header includes `bnx2x/bnx2x_mfw_req.h` for management firmware request/capability structures such as `fcoe_capabilities` and `union drv_info_to_mcp`. It depends on Linux kernel networking, PCI, DMA, MMIO, socket, module, atomic, and list types supplied by includers.

Primary integration points are the CNIC core implementation, bnx2 and bnx2x lower Ethernet drivers, upper-layer iSCSI/FCoE/RDMA modules, netlink iSCSI control paths, PCI interrupt setup including MSI-X, firmware KCQ/KWQ rings, management firmware statistics blocks, and FC NPIV capability reporting.

The MMIO helpers `CNIC_WR`, `CNIC_WR16`, `CNIC_WR8`, `CNIC_RD`, and `CNIC_RD16` directly access `dev->regview + off` using kernel `read*`/`write*` APIs. They assume offsets and lifetime are validated by the caller and lower driver.

## Risks
The callback tables are cross-module ABI within the kernel source tree. Risk comes from changing function signatures, ULP numbering, state flags, command IDs, or KWQE/KCQE interpretation without updating all CNIC, lower-driver, and ULP consumers.

RCU notes on `cnic_ops` and `cnic_ulp_ops` are important: unregister paths must wait for in-flight calls before freeing modules or callback storage. Reference counts in `cnic_sock`, `cnic_dev`, and `cnic_ulp_ops` protect lifetimes, but this header cannot enforce correct get/put or RCU grace-period usage.

Hardware risk centers on MMIO and DMA-facing values. Bad context table offsets, wrong CIDs, stale SPQ credit accounting, incorrect IRQ ownership flags, or mixing bnx2 and bnx2x class assumptions can corrupt firmware state or lose completions. Page-size capping at 16 KiB also means callers must use CNIC ring sizing macros rather than raw `PAGE_SIZE` when programming rings.

## Test Signals
Build signals include all CNIC-capable configurations, module unload/reload, and consumers for iSCSI/FCoE/RDMA/L4 ULP slots. Runtime signals include lower-driver CNIC registration/unregistration, ULP register/unregister under load, netdev up/down transitions, MSI-X and non-MSI-X interrupt delivery, KWQE submission and KCQE completion decoding, SPQ credit return balance, CNIC start/stop commands, L2 ring start/stop, stats retrieval for iSCSI and FCoE, FC NPIV table retrieval, and connection create/connect/close/abort flows including remote close and hardware error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/cnic_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/genet/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/genet/Makefile

## Purpose
This Kbuild Makefile controls compilation of the Broadcom GENET Ethernet driver subdirectory. It declares that the `genet.o` module or built-in object is produced when `CONFIG_BCMGENET` is enabled, and it defines the component objects linked into that driver.

## Important APIs, Types, and Functions
There are no C APIs or functions. The build interface is Kbuild syntax:

`obj-$(CONFIG_BCMGENET) += genet.o` conditionally includes the GENET driver aggregate object based on the kernel configuration symbol.

`genet-objs := bcmgenet.o bcmmii.o bcmgenet_wol.o` tells Kbuild to link the aggregate from the core GENET driver object, Broadcom MII/PHY helper object, and wake-on-LAN support object.

The file begins with `# SPDX-License-Identifier: GPL-2.0-only`, giving the license identifier for the build metadata.

## Control Flow and State
There is no runtime control flow. Build-time flow is controlled by Kbuild: if `CONFIG_BCMGENET=y`, the objects are linked into the built-in kernel image; if `CONFIG_BCMGENET=m`, they are linked into the loadable `genet.ko` module; if unset, none of the listed objects are built for this driver.

There is no persistent runtime state in the Makefile. Its persistent effect is the composition of the compiled driver artifact and the dependency edges Kbuild uses for rebuilds.

## Dependencies and Integration Points
The file depends on the kernel Kbuild system and on the `CONFIG_BCMGENET` Kconfig symbol being defined elsewhere. It integrates with the parent Broadcom Ethernet driver Makefile, with the source files `bcmgenet.c`, `bcmmii.c`, and `bcmgenet_wol.c`, and with module/built-in link rules generated by Kbuild.

The ordering of `genet-objs` can matter if object-level init/exit sections or duplicate symbol resolution become relevant, although ordinary symbol references are resolved by the final link.

## Risks
The main risk is build coverage drift. Adding a new GENET source file without listing it here leaves code unlinked. Removing or renaming one of the component objects without updating this file breaks `CONFIG_BCMGENET` builds. Misusing `obj-y` versus `obj-$(CONFIG_BCMGENET)` would incorrectly force or omit the driver.

Because this file only builds the aggregate object, it does not validate whether optional features inside the source files are gated by their own Kconfig symbols. Feature-specific object splits would need explicit Makefile updates.

## Test Signals
The most direct tests are `CONFIG_BCMGENET=y` and `CONFIG_BCMGENET=m` kernel builds. Additional signals include checking that `genet.o` or `genet.ko` contains symbols from `bcmgenet.o`, `bcmmii.o`, and `bcmgenet_wol.o`, that clean/rebuild dependency tracking notices edits to each component, and that disabling `CONFIG_BCMGENET` omits the aggregate from the Broadcom Ethernet build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/genet/Makefile -->

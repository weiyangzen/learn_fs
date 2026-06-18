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

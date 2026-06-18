# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-mtk.h

## Purpose
Defines the private MediaTek xHCI host data model shared by the platform glue and the MediaTek bandwidth scheduler. It also describes the SSUSB IPPC register layout used to power and configure U2/U3 host ports.

## Important APIs, Types, And Functions
Key constants are `BULK_CLKS_NUM`, `BULK_VREGS_NUM`, `XHCI_MTK_MAX_ESIT`, `XHCI_MTK_BW_INDEX()`, and port limits `MU3C_U3_PORT_MAX` and `MU3C_U2_PORT_MAX`. Important types are `struct mu3h_sch_tt`, `struct mu3h_sch_bw_info`, `struct mu3h_sch_ep_info`, `struct mu3c_ippc_regs`, and `struct xhci_hcd_mtk`. The header exposes `hcd_to_mtk()` plus scheduler entry points `xhci_mtk_sch_init()`, `xhci_mtk_sch_exit()`, `xhci_mtk_add_ep()`, `xhci_mtk_drop_ep()`, `xhci_mtk_check_bandwidth()`, and `xhci_mtk_reset_bandwidth()`.

## Control Flow
The header has no runtime execution, but it shapes the flow used by `xhci-mtk.c` and scheduler code: platform setup fills `struct xhci_hcd_mtk`, scheduler init creates bandwidth domains, endpoint add/drop hooks allocate or release `struct mu3h_sch_ep_info`, and bandwidth check/reset hooks commit or roll back periodic endpoint reservations.

## State And Persistence
State is runtime-only. TT arrays track FS/LS split bus bandwidth, `mu3h_sch_bw_info` tracks per-microframe bandwidth domains, and `mu3h_sch_ep_info` stores per-endpoint ESIT, offsets, packet counts, CS count, burst mode, and budget table. `struct xhci_hcd_mtk` persists while the controller is bound and owns the scheduler hash/list roots and platform resources.

## Dependencies And Integration Points
Depends on Linux clock, hashtable, regulator, USB HCD, and xHCI private types. It is a private compile-time contract between the MediaTek platform driver and MediaTek scheduling code, while `hcd_to_mtk()` uses driver data installed by platform probe.

## Risks And Test Signals
Risks are layout drift with `xhci-mtk.c`, incorrect MMIO register typing/offsets, ESIT truncation over-allocating bandwidth, and flexible-array budget sizing bugs. Test signals include compile coverage with MediaTek xHCI enabled, periodic endpoint admission tests, TT split scheduling for FS/LS devices behind HS hubs, masked U2/U3 port probing, and KASAN coverage for scheduler allocations.

# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-mtk.c

## Purpose
Implements the MediaTek platform glue for xHCI host controllers. It powers and resets the SSUSB host block, enables MediaTek IPPC U2/U3 ports, applies SoC timing/FIFO quirks, parses Devicetree wakeup and LPM properties, creates the USB2 and optional USB3 root HCDs, and wires MediaTek bandwidth-scheduler overrides into the generic xHCI core.

## Important APIs, Types, And Functions
Driver entry points are `xhci_mtk_probe()`, `xhci_mtk_remove()`, `xhci_mtk_suspend()`, `xhci_mtk_resume()`, runtime PM callbacks, `xhci_mtk_init()`, and `xhci_mtk_exit()`. The xHCI override table installs `xhci_mtk_setup()` plus scheduler hooks `xhci_mtk_add_ep()`, `xhci_mtk_drop_ep()`, `xhci_mtk_check_bandwidth()`, and `xhci_mtk_reset_bandwidth()` from the MediaTek scheduler implementation. Hardware helpers include `xhci_mtk_ssusb_config()`, `xhci_mtk_host_enable()`, `xhci_mtk_host_disable()`, `xhci_mtk_set_frame_interval()`, `xhci_mtk_rxfifo_depth_set()`, `usb_wakeup_of_property_parse()`, and `usb_wakeup_set()`.

## Control Flow
Probe allocates `struct xhci_hcd_mtk`, gets regulators and six optional clocks, parses IRQs and DT flags, enables runtime PM, regulators, clocks, and optional reset, maps `mac` and optional `ippc` resources, creates the primary HCD, sets MTK interrupt moderation, and calls `usb_add_hcd()`. During primary setup, `xhci_mtk_ssusb_config()` resets the SSUSB IP, powers down the device side, reads U2/U3 port counts, enables non-masked host ports, and polls clock/reset status before generic xHCI setup. If dual root hubs are needed, probe creates and adds a shared HCD. Suspend stops root-hub polling, powers down ports and host IP, disables clocks, and arms syscon wake; resume reverses that and restarts polling.

## State And Persistence
All state is volatile kernel memory plus MMIO/syscon state. `struct xhci_hcd_mtk` stores the primary HCD, IPPC base, port counts and disable masks, regulators, clocks, wakeup regmap/version/base, LPM flags, and RX FIFO depth. Runtime PM state, wake IRQ configuration, root-hub polling bits, and xHCI quirk flags are re-created on probe/resume; nothing is persisted to disk.

## Dependencies And Integration Points
Depends on platform devices, Devicetree, regmap/syscon wake registers, reset, regulator and clock bulk APIs, runtime PM, wake IRQ helpers, and the generic xHCI HCD. It integrates with `xhci-mtk.h` scheduler data and the external `xhci-mtk-sch.c` implementation for periodic bandwidth accounting.

## Risks And Test Signals
Risks include incorrect IPPC port masks, clocks not stabilizing, wake syscon version mismatches, PM races around root-hub polling, regulator/clock unwind leaks, and MT8195 timing workaround regressions. Test signals include probe/remove on DT variants, USB2/USB3 enumeration with masked ports, suspend/resume and runtime autosuspend with wakeup IRQs, stream capability on non-broken controllers, isochronous scheduling, RX FIFO workaround behavior, and lockdep/PM trace coverage.

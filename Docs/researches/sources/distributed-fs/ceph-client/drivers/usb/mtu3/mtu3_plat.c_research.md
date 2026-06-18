# sources/distributed-fs/ceph-client/drivers/usb/mtu3/mtu3_plat.c

## Purpose

`mtu3_plat.c` is the MTU3 platform driver. It acquires device-tree resources, regulators, clocks, PHYs, MMIO, reset, wake IRQ, port masks, and role policy; initializes common resources; chooses host/gadget/dual-role startup; and implements system/runtime suspend and resume.

## Important APIs, Types, and Functions

Key functions include `ssusb_check_clocks()`, resource helpers `get_ssusb_rscs()`, `ssusb_rscs_init()`, `ssusb_rscs_exit()`, PHY helpers, `ssusb_ip_sw_reset()`, `ssusb_u3_drd_check()`, platform lifecycle `mtu3_probe()` and `mtu3_remove()`, and PM helpers `mtu3_suspend_common()`, `mtu3_resume_common()`, `mtu3_runtime_suspend()`, and `mtu3_runtime_resume()`.

## Control Flow

Probe allocates `ssusb_mtk`, sets a 32-bit DMA mask, reads regulators/clocks/PHYs/MMIO/IRQs/role properties, creates debugfs root, enables runtime PM, initializes common resources, registers wake IRQ, resets the controller, detects U3 DRD capability, applies compile-time role overrides, and starts peripheral, host, or both plus the OTG switch. On success it enables async suspend, autosuspends, then forbids runtime PM until later policy allows it. Remove resumes the device, tears down role-specific subsystems, releases common resources, removes debugfs, and disables PM.

## State and Persistence Behavior

Platform state is runtime `ssusb_mtk`: common resource handles, role mode, host flag, port masks, wakeup config, debugfs root, and child gadget/host state. Hardware power, clock, PHY, reset, wake, and port states are reprogrammed during probe and PM transitions. No state persists beyond driver lifetime.

## Dependencies and Integration Points

The file depends on platform devices, device tree properties, regulators `vusb33` and `vbus`, clock bulk APIs, PHY framework, reset control, runtime/system PM, wake IRQ helpers, host/gadget/DRD helpers from `mtu3_dr.h`, and debugfs helpers.

## Risks and Test Signals

Risks include error unwinding order, treating `vbus` as required for host-capable modes, runtime PM forbid semantics, wakeup sleep polling failures, role-specific suspend with connected gadget returning `-EBUSY`, and resource leaks after partial host/gadget initialization. Test signals include probe for peripheral/host/OTG device trees, missing optional clocks, multiple PHY init rollback, wake IRQ registration, reset failure paths, system suspend/resume in host and device roles, runtime suspend with wakeup disabled, and clean remove after successful OTG initialization.

# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-histb.c

Purpose: platform xHCI host driver for HiSilicon STB SoCs. It wraps the generic xHCI driver with SoC-specific MMIO configuration, clock/reset control, DMA mask setup, dual-HCD registration, and system sleep handling.

Important APIs and functions: `xhci_histb_probe()` and `xhci_histb_remove()` implement platform lifecycle. `xhci_histb_config()` programs USB2/USB3 PHY-related registers and threshold registers. `xhci_histb_clks_get()`, `xhci_histb_host_enable()`, and `xhci_histb_host_disable()` manage clock/reset sequencing. `xhci_histb_setup()` is a generic xHCI reset override. PM hooks are `xhci_histb_suspend()` and `xhci_histb_resume()`. Module entry/exit register the platform driver after `xhci_init_driver()`.

Control flow: probe checks `usb_disabled()`, allocates private state, fetches IRQ and MMIO resource, gets required clocks and soft reset, enables runtime PM, sets a 32-bit DMA mask, creates the primary HCD, enables clocks/resets, obtains `xhci`, creates the shared USB3 HCD, applies DT property quirks, registers USB2 then USB3 HCDs, and forbids runtime PM by default. Remove reverses HCD registration, disables wakeup, clocks, reset, and runtime PM. Suspend delegates to generic `xhci_suspend()` and disables host resources when wakeup is not allowed; resume re-enables resources then calls `xhci_resume()`.

State and persistence: `struct xhci_hcd_histb` is driver data attached to the controller device and owns MMIO, clocks, reset, and primary HCD pointer. Hardware register programming persists until reset/power loss; software state is runtime-only.

Dependencies and integration points: depends on platform device resources, OF matching (`hisilicon,hi3798cv200-xhci`), common clock framework, reset controller, PM runtime, USB HCD core, and generic xHCI setup/resume/suspend.

Risks: clock enable error unwinding must keep exact reverse order. `reset_control_deassert()` return is not checked, so reset-controller failures may be missed. Probe calls `pm_runtime_get_sync()` without checking a negative return. Register constants are SoC-specific and can be wrong for close variants. Runtime PM is enabled but then forbidden after probe, so power expectations should be explicit in board integration.

Test signals: probe/remove on matching DT; missing clock/reset/property failure paths; USB2/USB3 enumeration; DT properties `usb2-lpm-disable`, `usb3-lpm-capable`, and `imod-interval-ns`; system suspend/resume with and without wakeup enabled; DMA mask failure path on constrained platforms.

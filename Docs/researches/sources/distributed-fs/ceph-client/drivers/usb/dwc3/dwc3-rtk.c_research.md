# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-rtk.c

Purpose: Realtek DWC3 glue driver for `realtek,rtd-dwc3`. It programs wrapper workarounds, USB2/USB3 PHY routing, optional PM control registers, child DWC3 creation, and a wrapper-level USB role switch that synchronizes the DWC3 role and Realtek USB2 PHY switch bits.

Important APIs, types, and functions: `struct dwc3_rtk` stores device, wrapper MMIO, optional PM MMIO, child `struct dwc3 *`, current role, and optional role switch. `dwc3_rtk_init()` applies SOC-specific workarounds and PHY/DBUS setup. `switch_usb2_role()`, `switch_dwc3_role()`, `dwc3_rtk_set_role()`, and role-switch callbacks manage role transitions. `__get_dwc3_maximum_speed()` reads child maximum speed. `dwc3_rtk_probe_dwc3_core()` populates and locates the child core.

Control flow: probe maps wrapper and optional PM resources, then calls `dwc3_rtk_probe_dwc3_core()`. Core probing first runs wrapper init, populates the OF child, finds the `snps,dwc3` platform device and drvdata, reconciles DT `dr_mode` with core `dr_mode`, sets the initial role, optionally registers a userspace-controllable role switch, and programs USB2 role bits. Remove clears the child pointer, unregisters role switch, and depopulates children. Resume reruns wrapper init and reapplies the last role.

State and persistence: `cur_role` is the persistent software role and is re-applied after resume. Hardware state includes workaround bits for multi-request/DESC behavior, USB2 PLL and role-switch bits, USB3 disable/power-bias bits for high-speed-only configurations, and optional DBUS power-control enable.

Dependencies and integration: uses OF child population, `soc_device_match()` for Realtek family/revision workarounds, USB role-switch framework, DWC3 internals from `core.h`, PM sleep callbacks, and optional Realtek USB2/USB3 PHY softdeps.

Risks: the role switch calls into the child DWC3 role switch and then delays before changing wrapper USB2 bits; ordering is hardware-sensitive. SOC workaround matches are string-based and can miss new revisions. `rtk->dwc` is cleared before role-switch unregister, so callbacks must not race removal. High-speed-only paths disable USB3 PHY resources based on child `maximum-speed`, making DT correctness critical.

Test signals: verify each Realtek SOC workaround, high-speed-only PHY disablement, initial host/device role programming, userspace role switching, child probe failure unwind, resume reinitialization, and no role-switch callbacks after remove/shutdown.

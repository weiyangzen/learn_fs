# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-qcom-legacy.c

Purpose: legacy Qualcomm DWC3 glue driver for `qcom,dwc3` devices. It controls QSCRATCH VBUS override, resets, manually acquired clocks, optional extcon role notifications, interconnect bandwidth, wakeup PHY IRQs, and an OF-populated child `snps,dwc3` platform device.

Important APIs, types, and functions: `struct dwc3_qcom` stores parent device, QSCRATCH base, child `platform_device *dwc3`, clock array, resets, per-port wake IRQs, extcon devices/notifiers, PM flags, and interconnect paths. `dwc3_qcom_register_extcon()` wires VBUS and host extcon notifications. `dwc3_qcom_suspend()` and `_resume()` gate clocks/interconnects and enable/disable wake IRQs. `dwc3_qcom_of_register_core()` populates and locates the child core. `dwc3_qcom_clk_init()` manually obtains and enables clocks.

Control flow: probe asserts/deasserts resets, gets/enables clocks, maps QSCRATCH, sets up per-port IRQs, optionally selects UTMI as PIPE clock, populates the child DWC3 core, initializes interconnect bandwidth, reads child `dr_mode`, enables VBUS override unless host-only, registers extcon notifiers, initializes wakeup on parent and child, and enables then forbids runtime PM. Extcon callbacks toggle VBUS override and update `mode`. Suspend checks HS PHY L2 status, disables clocks and interconnects, then enables wake IRQs if host and wakeup is allowed; resume reverses that and clears L2 event bits.

State and persistence: state is split between parent QSCRATCH registers, child DWC3 device state, extcon role state, per-port cached USB2 speeds, and interconnect bandwidth handles. `is_suspended` prevents duplicate suspend. `pm_suspended` lets wake IRQs defer work to system resume.

Dependencies and integration: uses OF child population, extcon, reset controller, legacy clock APIs, interconnect framework, USB HCD root-hub inspection, platform IRQ names, and runtime/system PM. It integrates with DWC3 via child platform data and with host wake via PHY IRQs named `dp_hs_phy`, `dm_hs_phy`, `ss_phy`, and optional multiport variants.

Risks: this file intentionally differs from modern `dwc3-qcom.c`; mixing assumptions between them can break child lifecycle or PM. Host detection peeks into child `struct dwc3` and xHCI state, a layering violation with race potential during probe/remove. Extcon state drives VBUS override and mode but may conflict with role-switch based systems. Manual clock unwind must stay exact.

Test signals: test legacy `qcom,dwc3` DTs with and without extcon, one-port and multiport IRQ naming, runtime/system wake from suspended host, interconnect enable/disable errors, VBUS override in peripheral and host modes, and child depopulation/put on probe failures.

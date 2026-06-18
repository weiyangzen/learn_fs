# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-imx8mp.c

Purpose: NXP i.MX8MP USB3 glue driver that owns the HSIO wakeup block, optional USB glue registers, wrapper clocks, wake IRQ, and the child `snps,dwc3` core. It adds software-node xHCI quirks and installs a DWC3 glue callback to adjust runtime autosuspend before role changes.

Important APIs, types, and functions: `struct dwc3_imx8mp` persists the parent device, child DWC3 platform device, HSIO/glue MMIO bases, `hsio` and `suspend` clocks, IRQ, and suspend/wakeup flags. `imx8mp_configure_glue()` programs permanent-attach, port-power-control, over-current polarity, and power polarity properties. `dwc3_imx8mp_wakeup_enable()` and `_disable()` manage `USB_WAKEUP_CTRL`. `dwc3_imx8mp_interrupt()` handles wake events while suspended. `dwc3_imx_pre_set_role()` is exported through `dwc3_imx_glue_ops`.

Control flow: probe maps resource 0 as HSIO, optionally maps resource 1 as glue, enables both clocks, finds the `snps,dwc3` child, applies glue configuration, enables runtime PM, attaches the software node, populates the child core, retrieves the child platform data, sets `dwc3->glue_ops`, requests the wake IRQ, and marks the parent wake-capable. Remove puts the child device, depopulates children, removes the software node, and disables runtime PM. System and runtime suspend share `dwc3_imx8mp_suspend()`; resume restores wake bits, glue registers, clocks, runtime-PM state, and any disabled IRQ.

State and persistence: persistent state is MMIO configuration plus `pm_suspended` and `wakeup_pending`. The driver intentionally re-runs `imx8mp_configure_glue()` after resume because power loss can clear wrapper registers. Wake handling depends on the child `struct dwc3` role and `xhci` pointer.

Dependencies and integration: uses OF child population, platform resources, Linux clocks, runtime/system PM, wake IRQs, `device_add_software_node()`, and DWC3 internals from `core.h`. It integrates with xHCI in host mode by resuming the xHCI child from the wrapper IRQ, and with gadget mode by runtime-getting the DWC3 device.

Risks: `dwc3_imx8mp_interrupt()` assumes a valid child DWC3 pointer when suspended. Missing glue resource is tolerated but disables board-specific polarity and permanent-attach behavior. Clock sequencing and wake IRQ enable/disable paths are sensitive to system suspend versus autosuspend differences. Role-change autosuspend policy can break wake behavior if `dwc3->current_dr_role` lags the requested role.

Test signals: probe should create a child DWC3 core, expose xHCI quirks, and log missing optional glue resource only as a warning. Suspend/resume tests should cover host wake from DPDM/U3/SS connect, device wake from VBUS/session, i.MX95 out-of-band wake setup, runtime autosuspend, and role switches between host and device.

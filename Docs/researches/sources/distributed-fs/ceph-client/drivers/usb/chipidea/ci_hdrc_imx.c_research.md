# sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_imx.c

Purpose: implements the i.MX/NXP/S32G ChipIdea glue driver, translating device-tree match data and USBMISC resources into `ci_hdrc_platform_data`, clocks, PHYs, pinctrl, regulators, wakeup IRQs, runtime PM, and SoC-specific notifications.

Important APIs/types/functions: defines SoC flag tables, `struct ci_hdrc_imx_data`, `usbmisc_get_init_data`, clock helpers, `ci_hdrc_imx_notify_event`, wakeup IRQ handler, probe/remove/shutdown, and system/runtime PM callbacks.

Control flow: probe reads match flags, parses `fsl,usbmisc`, configures HSIC pinctrl/regulator, optional PM QoS, clocks, wakeup clock, USB PHY phandles, ULPI override handling, wakeup IRQ, USBMISC init, then calls `ci_hdrc_add_device`. Post-init records external ID/VBUS and available role for USBMISC. Remove and error paths unwind child device, PHY override, clocks, QoS, and USBMISC device references.

State and persistence: persistent glue state includes child `ci_pdev`, clocks, wakeup IRQ, USBMISC data, HSIC regulator/pinctrl, runtime PM support, low-power flag, PM QoS request, and SoC flag pointer.

Dependencies and integration: integrates with USBMISC helper functions, OF properties, clocks, USB PHY, pinctrl, regulators, PM QoS, runtime PM, out-of-band wakeup, and the ChipIdea core platform-device API.

Risks: many optional resources have deferred-probe paths. Clock and QoS unwinding must stay balanced. Wakeup IRQ and parent/child runtime PM sequencing can race with core suspend. USBMISC reference handling depends on `put_device`.

Test signals: boot/probe on i.MX variants, HSIC active/suspend notifications, charger detection and pullup events, runtime/system suspend-resume with wakeup IRQ, ULPI override platforms, and device-tree extcon/role-switch combinations.

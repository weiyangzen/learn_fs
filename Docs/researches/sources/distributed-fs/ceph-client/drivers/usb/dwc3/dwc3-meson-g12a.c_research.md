# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-meson-g12a.c

Purpose: Amlogic Meson USB control/glue driver for GXL, GXM, AXG, G12A, and A1 families. It configures USB2 per-port controls, USB3 glue registers, PHY modes, clocks, resets, optional VBUS regulator, OTG ID interrupt handling, and a userspace-visible role switch spanning DWC3 and DWC2 children.

Important APIs, types, and functions: `struct dwc3_meson_g12a_drvdata` selects clocks, PHY names, register-map setup, USB2 init, PHY mode operations, and post-init hooks per SoC. `struct dwc3_meson_g12a` stores regmaps, reset, PHYs, mode/role state, regulator, role-switch descriptors, and port counts. Core functions include `dwc3_meson_g12a_usb2_init_phy()`, `dwc3_meson_g12a_usb3_init()`, `dwc3_meson_g12a_usb_otg_apply_mode()`, `dwc3_meson_g12a_otg_mode_set()`, `dwc3_meson_g12a_irq_thread()`, `dwc3_meson_g12a_setup_regmaps()`, and `dwc3_meson_g12a_probe()`.

Control flow: probe maps the wrapper MMIO, selects drvdata from OF match data, gets optional VBUS, enables SoC clocks, resets the block, discovers optional PHYs and port counts, creates regmaps, enables VBUS, initializes wrapper registers for the initial `dr_mode`, initializes and powers PHYs, runs post-init for GXL-style hardware, populates children, registers OTG IRQ and role switch, then enables runtime PM. OTG IRQ reads `USB_R5` ID state and calls `dwc3_meson_g12a_otg_mode_set()` when the pin changes. Role-switch set maps USB host/device roles to PHY host/device modes and optional VBUS changes.

State and persistence: persisted state includes current `otg_mode`, `otg_phy_mode`, discovered `usb2_ports` and `usb3_ports`, role-switch handles, and hardware register programming. System suspend powers off/exits PHYs, disables host VBUS, and rearms reset; resume resets the block, reruns USB init, reinitializes/powers PHYs, restores VBUS, and reruns post-init.

Dependencies and integration: uses regmap over MMIO, reset controls, clk bulk APIs, generic PHY, regulator, OF child population, `usb_role_switch`, USB OTG helpers, and runtime/system PM. It links DWC3 and DWC2 children into a single role-switch descriptor with `usb2_port` and `udc` device references.

Risks: the GXL/GXM workaround for broken device-to-host switching uses host-port disable and a 500 ms sleep; manual OTG switching can still be fragile. The `gxl_drvdata` and `gxm_drvdata` clock/PHY table choices are easy to regress because they intentionally differ from G12A. Optional PHY arrays have fixed `PHY_COUNT`, so DT binding mismatches can silently change port counts. VBUS regulator changes must stay consistent with role state to avoid back-powering.

Test signals: test each compatible string, USB2-only A1/AXG cases, SuperSpeed initialization when a USB3 PHY exists, role switching from ID IRQ and userspace, VBUS regulator enable/disable, suspend/resume restoration, and child device reference cleanup during remove.

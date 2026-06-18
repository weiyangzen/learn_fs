# sources/distributed-fs/ceph-client/drivers/phy/allwinner/phy-sun4i-usb.c

Purpose: broad Allwinner sun4i/sun5i/sun6i/sun7i/sun8i/sun20i/sun50i USB2 PHY driver. It manages up to four PHYs, OTG ID/VBUS detection for PHY0, VBUS regulators, passby/PMU settings, SoC-specific calibration, and extcon reporting.

Important APIs, types, and functions: `struct sun4i_usb_phy_cfg` captures compatible-specific quirks such as PHYCTL offset, HSIC index, dual-route PHY0, SIDDQ placement, missing PHYs, and polling requirements. `struct sun4i_usb_phy_data` owns shared registers, extcon, GPIOs, power-supply notifier, delayed detection work, and per-PHY clocks/resets/regulators. PHY ops are `sun4i_usb_phy_init`, `exit`, `power_on`, `power_off`, and `set_mode`; exported helper `sun4i_usb_phy_set_squelch_detect` adjusts squelch bits.

Control flow: probe maps `phy_ctrl`, reads optional ID/VBUS GPIOs and power supply, creates and registers extcon, creates each non-missing PHY by acquiring reset, optional regulator, clocks, optional PMU resource, and registering the provider. It then requests GPIO IRQs or falls back to polling and registers a power-supply notifier. Init enables clocks, deasserts reset, handles PHY2 SIDDQ dependencies, programs calibration/tuning or base SIDDQ bits, enables passby, enables PHY0 pullups, and schedules detection. Detection work reads ID/VBUS, forces session-end transitions when needed, updates ISCR force bits, publishes extcon states, toggles passby and dual-route MUSB/EHCI routing, and reschedules polling when necessary.

State and persistence: runtime state includes regulator-on flags, PHY0 initialized flag, cached ID/VBUS values, force-session-end flag, delayed work, extcon state, and register programming. Nothing persists beyond driver lifetime.

Dependencies and integration: generic PHY, USB mode helpers, extcon, GPIO descriptors/IRQs, power supply, regulators, clocks, resets, workqueues, DT compatibles, and PMU MMIO resources.

Risks: OTG correctness depends on debouncing and prompt VBUS reporting within 100 ms. PHY0 route switching must match controller ownership. Multiple SoC quirks make regression risk high when adding compatibles. Cleanup manually cancels work and unregisters notifiers. Test signals include each compatible variant, regulator conflict with external VBUS, GPIO IRQ and polling modes, power-supply notification, PHY0 host/device/OTG mode changes, missing PHY phandle translation, suspend-like init/exit cycles, and squelch export users.

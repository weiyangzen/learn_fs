# sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson8b-usb2.c

Purpose: Implements USB2 PHY power sequencing for Meson8, Meson8b, Meson8m2, and GXBB, including USB clocks, optional shared reset, host/device role information, and ACA-based host ID detection for later variants.

Important APIs and types: `struct phy_meson8b_usb2_priv` stores regmap, `usb_dr_mode`, two clocks, optional reset, and match data. `struct phy_meson8b_usb2_match_data` selects whether host mode should enable ACA. The `phy_ops` implement power-on and power-off.

Control flow: probe maps registers, reads match data, gets `usb_general` and `usb` clocks, optional reset, and controller dual-role mode via `of_usb_get_dr_mode_by_phy()`, then creates a simple PHY. Power-on triggers reset, enables both clocks with rollback, selects 32 kHz/ref/FSEL settings, pulses power-on reset, enables SOF toggle, and in host mode clears IDDQ. If ACA is enabled it turns on ACA detection and fails when the ID pin floats. Power-off restores host IDDQ, disables clocks, rearms reset, and asserts power-on reset.

State and persistence: The role and variant are static after probe. Hardware is reinitialized each power-on; no runtime mode mutation is implemented.

Dependencies and integration: It depends on USB OF role parsing, clock/reset/regmap/generic PHY frameworks, and compatible-specific match data.

Risks and test signals: Missing role configuration is fatal. ACA failure disables clocks and re-arms reset but leaves an error path that should be verified for balanced resources. Test all compatible match data, host/device role behavior, ACA floating-pin detection, clock failure rollback, and USB enumeration after repeated power cycles.

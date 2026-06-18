# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-usb-hsic.c

Purpose: Provides a Qualcomm ULPI HSIC PHY driver that enables HSIC calibration, selects pinctrl state, and controls the HSIC clocks.

Important APIs/types/functions: `struct qcom_usb_hsic_phy` stores ULPI, generic PHY, pinctrl, and `phy`, `cal`, and `cal_sleep` clocks. PHY ops are `qcom_usb_hsic_phy_power_on()` and `_power_off()`.

Control flow: Probe gets pinctrl and all clocks, creates a PHY, attaches driver data, and registers an OF provider. Power-on enables clocks in order, writes the periodic IO calibration interval to `ULPI_HSIC_IO_CAL`, enables periodic calibration in `ULPI_HSIC_CFG`, selects the default pinctrl state, sets HSIC mode, and disables ULPI auto-resume. Power-off disables the three clocks.

State and persistence: The driver holds only resource handles. HSIC calibration interval, HSIC enable, pinmux state, and autoresume clearing persist in hardware/pinctrl until power-off or reconfiguration.

Dependencies and integration points: Depends on ULPI, generic PHY, pinctrl, and clocks. It is consumed by USB HSIC host controller wiring through OF PHY phandles.

Risks: Power-on ordering must keep clocks enabled before ULPI writes and pinctrl selection. There is no explicit pinctrl sleep-state restore on power-off. Any ULPI write failure unwinds clocks but leaves earlier register writes until next reset.

Test signals: Probe `qcom,usb-hsic-phy`, verify pinctrl default state selection, clock enable/disable balance, HSIC device enumeration, periodic calibration register values, and failure unwinding for missing clocks or pinctrl state.

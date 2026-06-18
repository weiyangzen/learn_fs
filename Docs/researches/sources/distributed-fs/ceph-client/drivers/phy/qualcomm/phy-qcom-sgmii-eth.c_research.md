# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-sgmii-eth.c

Purpose: Implements the Qualcomm DWMAC SGMII PHY driver for SA8775P-style Ethernet SerDes, supporting SGMII/1000BASE-X and 2500BASE-X operating modes.

Important APIs/types/functions: `struct qcom_dwmac_sgmii_phy_data` stores the MMIO regmap, reference clock, and current `phy_interface_t`. `qcom_dwmac_sgmii_phy_init_1g()` and `_init_2p5g()` program full PLL/TX/RX/PCS sequences. `qcom_dwmac_sgmii_phy_calibrate()`, `_power_on()`, `_power_off()`, `_set_mode()`, and `_validate()` implement the generic PHY ops.

Control flow: Probe maps a resource, wraps it in a relaxed 32-bit regmap, creates a PHY, gets `sgmi_ref`, registers an OF PHY provider, and defaults the interface to SGMII. Power-on enables the reference clock and calibrates for the selected interface. Calibration selects either the 1.25 Gbps or 3.125 Gbps table, starts the PCS, and polls C-ready, PCS-ready, SGMII-ready, and PLL-lock bits. `set_mode()` validates Ethernet mode and recalibrates immediately if the PHY is already powered.

State and persistence: State is limited to selected interface mode and reference clock state. Hardware PLL, CDR, TX/RX equalization, and PCS configuration persist until power-off or recalibration.

Dependencies and integration points: Depends on generic PHY, Linux PHY interface mode constants, clocks, platform MMIO, and QMP SGMII/QSERDES register headers. It is intended to be called by a DWMAC Ethernet controller PHY consumer.

Risks: Long register write tables are mode-sensitive and not self-validating. `set_mode()` recalibrates on a powered PHY, so link-mode switches rely on consumers sequencing traffic safely. Poll timeouts are the main observable failure signal for wrong clocks, bad tables, or missing hardware readiness.

Test signals: Probe the `qcom,sa8775p-dwmac-sgmii-phy` compatible, bring links up in SGMII, 1000BASE-X, and 2500BASE-X, verify refclk enable/disable balance, run repeated `set_mode()` while powered, and check timeout diagnostics for each readiness poll.

# sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson8-hdmi-tx.c

Purpose: Controls the Meson8/Meson8b/Meson8m2 HDMI transmitter PHY through HHI syscon registers and a TMDS clock.

Important APIs and types: `struct phy_meson8_hdmi_tx_priv` holds the HHI regmap and TMDS clock. The `phy_ops` provide init/exit for clock enable and power_on/power_off for HDMI PHY register programming.

Control flow: probe verifies a memory resource exists, obtains the parent syscon regmap, gets the TMDS clock, creates the PHY, and registers a simple provider. Init enables the TMDS clock. Power-on selects one of two vendor-derived `HDMI_CTL0` constants based on whether TMDS rate is at least 2.97 GHz, writes CTL0/CTL1, then performs the vendor-style three-cycle soft reset with 1-2 ms sleeps. Power-off writes a low-power CTL0 value.

State and persistence: There is no software state beyond resource pointers. PHY programming depends on the current TMDS clock rate at power-on.

Dependencies and integration: It depends on the parent HHI syscon node, generic PHY, and clock framework. It matches `amlogic,meson8-hdmi-tx-phy` for display/HDMI controller consumers.

Risks and test signals: Magic constants are derived from BSP behavior and have limited documentation. Test low and high TMDS rates, repeated power cycles, clock enable/disable balance, parent syscon failures, and HDMI link stability after the triple-reset sequence.

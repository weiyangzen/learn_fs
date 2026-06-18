<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-pxa-28nm-hsic.c -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-pxa-28nm-hsic.c

Purpose: Supports the Marvell/PXA1928 28 nm HSIC PHY with clock-managed PLL setup, HSIC enable, impedance calibration wait, and connect interrupt wait.

Important APIs and types: `struct mv_hsic_phy` holds the PHY, platform device, MMIO base, and clock. `wait_for_reg()` wraps `readl_poll_timeout()`. PHY callbacks are `mv_hsic_phy_init()`, `mv_hsic_phy_power_on()`, `mv_hsic_phy_power_off()`, and `mv_hsic_phy_exit()`.

Control flow: Probe gets the clock, maps registers, creates a PHY, and registers a simple provider. Init enables the clock, programs PLL reference/feedback/LPF fields, powers the PLL, and waits for PLL lock. Power-on clears the SE0-on-resume drive bit, enables HSIC, waits for impedance calibration done, and waits for connect interrupt. Power-off clears HSIC enable. Exit powers down the PLL and disables the clock.

State and persistence: Clock enable spans init to exit. Register bits persist across power-on/off; power-off disables HSIC but not the PLL, which is released by exit.

Dependencies and integration points: Uses generic PHY, platform MMIO, an unnamed clock, and `marvell,pxa1928-hsic-phy`. The HSIC USB controller drives lifecycle callbacks.

Risks: Timeout paths in power-on return errors but leave HSIC enable set. Connect interrupt timeout is treated as a warning return path. Init disables the clock only on lock failure, so callback pairing matters.

Test signals: PLL lock and calibration success, HSIC device connection, timeout injection for PLL/calibration/connect, clock enable balance over init/exit, and resume behavior with `S2H_DRV_SE0_4RESUME` cleared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-pxa-28nm-hsic.c -->

# sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-xpcs-wx.c

Purpose: Provides WangXun TXGBE-specific PMA/PCS mode switching for DesignWare XPCS hardware.

Important APIs, types, and functions: `txgbe_xpcs_switch_mode()` is called by the XPCS core when selecting 10GBASE-R, SGMII, or 1000BASE-X. Helpers program PMA registers for 10G (`txgbe_pma_config_10gbaser()`) or 1G/SGMII (`txgbe_pma_config_1g()`), poll PCS power-up (`txgbe_pcs_poll_power_up()`), wait for PMA init reset completion (`txgbe_pma_init_done()`), and detect LAN-reset mode quirks (`txgbe_xpcs_mode_quirk()`).

Control flow: If the target interface is supported and either differs from cached mode or hardware appears reset to 10G, the function polls PCS power-up, programs PCS/PMA MDIO control registers for 10G or 1G mode, applies a sequence of analog PMA tuning writes, triggers vendor PCS reset with VSMMD enabled, then waits for reset deassertion.

State and persistence behavior: `xpcs->interface` caches the selected mode, but hardware can revert during LAN reset, so mode quirk detection rereads PCS type. PMA register state persists until reset or mode change.

Dependencies and integration points: It depends on XPCS MDIO accessors, WangXun PMA register layout, and is invoked from `xpcs_switch_interface_mode()` for `WX_TXGBE_XPCS_PMA_10G_ID`.

Risks and edge cases: Poll timeouts are long and indicate hardware bring-up failure. The mode quirk path must catch external resets or phylink may believe the PCS is configured when it is not. Analog values are device-specific. Errors from many configuration writes are mostly ignored in the tuning helpers, so final poll/reset failures may be the first visible symptom.

Test signals: Mode switching 10GBASE-R to SGMII/1000BASE-X and back, LAN reset recovery, timeout paths for power-up and PMA init, MDIO error injection, link stability/BER at both speeds, and interrupt-driven non-polled XPCS operation with TXGBE.

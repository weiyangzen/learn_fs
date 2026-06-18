# sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-xpcs-nxp.c

Purpose: Provides NXP-specific PMA programming callbacks for DesignWare XPCS instances embedded in SJA1105/SJA1110 devices.

Important APIs, types, and functions: Exported-to-core functions are `nxp_sja1105_sgmii_pma_config()`, `nxp_sja1110_sgmii_pma_config()`, and `nxp_sja1110_2500basex_pma_config()`. Shared helper `nxp_sja1110_pma_config()` writes PLL dividers, transmitter amplitude/trim, lane termination, datapath, receiver PLL, signal detector, power/reset bits, and CTLE settings.

Control flow: The XPCS core calls these callbacks after mode-specific PCS configuration when a compatibility entry has `pma_config`. SJA1105 SGMII simply inverts TX polarity. SJA1110 variants program different PLL divider/CTLE values for SGMII versus 2500BASE-X, then release PMA power/reset.

State and persistence behavior: Register writes persist in vendor MMD PMA/PCS hardware until reset or reprogramming. No software state is stored here.

Dependencies and integration points: It depends on `struct dw_xpcs` accessors from `pcs-xpcs.h` and MDIO MMD vendor registers. It is linked into the XPCS module and referenced by compatibility tables in `pcs-xpcs.c`.

Risks and edge cases: Hard-coded analog values are silicon-specific and order-sensitive. Any write failure aborts later programming, potentially leaving a partially configured PMA. SJA1105 polarity inversion encodes a board/device assumption. Register field macros use wide constants for trim values and must remain correct on 16-bit writes.

Test signals: Hardware bring-up for SJA1105 SGMII and SJA1110 SGMII/2500BASE-X, MDIO failure injection at each write, link BER/eye validation, polarity tests, and regression after PCS reset or mode changes.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mscc-miim.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mscc-miim.c

Purpose: Microsemi/Microchip MIIM controller driver and setup helper for Ocelot/LAN966x switch MDIO blocks.

Important APIs/types/functions: `struct mscc_miim_dev` stores regmaps, status offset, optional PHY reset regmap/info, clock, bus frequency, and read-error policy. Exports `mscc_miim_setup`. Core callbacks are `mscc_miim_read`, `mscc_miim_write`, `mscc_miim_reset`, `mscc_miim_clk_set`, probe, and remove.

Control flow: reads wait for no pending command, issue a read command, wait for not busy, read data, and optionally treat hardware error bits as `-EIO`. Writes wait pending then issue a write command. Reset toggles SoC-specific PHY reset bits and delays 500 ms. Probe resets switch, creates regmaps from resources, calls setup, obtains optional PHY regmap/match data/clock, programs prescaler from `clock-frequency`, registers with OF MDIO, and stores bus.

State and persistence: runtime state is regmap-backed registers, optional clock enable, reset bits, and bus private data. No storage persists after unload.

Dependencies/integration: depends on REGMAP_MMIO, Ocelot MFD helpers, reset/clock frameworks, OF MDIO, and phylib. `mscc_miim_setup` lets other drivers reuse the MIIM callbacks with existing regmaps.

Risks and test signals: risks include high-resolution-timer fallback behavior, optional read-error ignore policy, prescaler bounds, long reset delay, and regmap creation failures. Tests should cover exported setup, register errors, clock-frequency validation, reset variants, and read error bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mscc-miim.c -->

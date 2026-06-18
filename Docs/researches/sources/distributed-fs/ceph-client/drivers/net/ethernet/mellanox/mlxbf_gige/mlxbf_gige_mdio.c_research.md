# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_mdio.c

## Purpose
`mlxbf_gige_mdio.c` implements the MDIO bus for BlueField GigE. It abstracts BF2 and BF3 MDIO gateway bit layouts, programs MDIO timing from core PLL registers, registers a `mii_bus`, and provides clause 22 read/write operations for the external PHY.

## Important APIs, Types, and Functions
The version table `mlxbf_gige_mdio_gw_t[]` maps gateway offsets and field masks into `struct mlxbf_gige_mdio_gw`. Important helpers are `calculate_i1clk()`, `mdio_period_map()`, `mlxbf_gige_mdio_create_cmd()`, `mlxbf_gige_mdio_read()`, `mlxbf_gige_mdio_write()`, `mlxbf_gige_mdio_cfg()`, `mlxbf_gige_mdio_probe()`, and `mlxbf_gige_mdio_remove()`.

## Control Flow and State
Probe rejects unsupported hardware versions, maps the MDIO resource, maps the shared clock resource or internal fallback resource, chooses the gateway table, configures MDC period and sampling registers, allocates a managed MDIO bus, installs read/write callbacks, and registers the bus. Reads and writes encode PHY address, register address, opcode, clause-22 start bit, data, and busy bit into the gateway register, poll until hardware clears busy, then clear the gateway register to release the MDIO lock. Reads fetch data from BF2's gateway register or BF3's separate data-read register.

State lives in gateway registers, timing configuration registers, `priv->mdio_io`, `priv->clk_io`, `priv->mdio_gw`, and the registered `mii_bus`. No firmware or disk-persistent state is written, but PHY register writes can alter link behavior.

## Dependencies and Integration Points
The file depends on platform resource mapping, raw MMIO access, polling helpers, PHYLIB `mii_bus`, ACPI-described resources, and BF2/BF3 MDIO layout headers. It feeds `phy_find_first()` and `phy_connect_direct()` in the main driver.

## Risks and Test Signals
Risks include wrong PLL-derived MDC timing, busy-bit timeout, failure to clear the gateway lock, BF2/BF3 mask/shift mismatches, resource conflicts on shared clock mapping, and only clause 22 support. Test signals include MDIO bus registration, PHY discovery, repeated MII reads/writes, timeout/error injection, BF2/BF3 timing register inspection, link negotiation, and clean remove/unregister paths.

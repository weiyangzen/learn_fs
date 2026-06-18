# sources/distributed-fs/ceph-client/drivers/net/dsa/mt7530-mmio.c

## Purpose

This file is the platform/MMIO transport driver for MT7530-family switch IP embedded in newer SoCs, including Airoha AN7583/EN7581 and MediaTek MT7988. It maps the switch register resource, creates an MMIO regmap, obtains a reset controller, invokes shared MT7530 DSA initialization, and registers the switch.

## Important APIs, Types, And Functions

The OF match table maps `"airoha,an7583-switch"`, `"airoha,en7581-switch"`, and `"mediatek,mt7988-switch"` to `mt753x_table[]` entries. `sw_regmap_config` defines a 16-bit register, 32-bit value, stride-4 switch regmap with `MT7530_CREV` as maximum register. `mt7988_probe()` allocates `struct mt7530_priv`, marks `priv->bus = NULL`, calls `mt7530_probe_common()`, obtains an unnamed reset control, maps MMIO resource 0 with `devm_platform_ioremap_resource()`, initializes `devm_regmap_init_mmio()`, and registers the DSA switch. Remove calls `mt7530_remove_common()`; shutdown calls `dsa_switch_shutdown()`.

## Control Flow

The platform driver probe path is short: allocate state, run common setup, acquire reset, map registers, create regmap, and register the switch. Once registered, the shared `mt753x_setup()` path calls the variant setup function from `mt753x_table[]`; for these compatibles that is `mt7988_setup()`, which resets the switch, applies AN7583-specific GEPHY connection tweaks if needed, resets switch PHYs, and uses MT7531-style common initialization.

## State And Persistence Behavior

State is devm-managed through platform device lifetime: `struct mt7530_priv`, reset controller, ioremapped base, and MMIO regmap. `priv->bus = NULL` is significant because shared code skips MDIO locking and reads live MMIO stats directly instead of using the delayed MDIO stats cache. Hardware state persists in the SoC switch register block until reset.

## Dependencies And Integration Points

The file depends on the platform bus, OF matching, reset framework, MMIO regmap, DSA, and the shared MT7530 implementation. It exports no symbols and is registered with `module_platform_driver()`. Shared code distinguishes this transport through `priv->bus == NULL`, affecting mutex behavior and statistics reads.

## Risks

The driver assumes one MMIO resource and one reset control. A bad compatible-to-variant mapping selects wrong capabilities and setup hooks. Because no MDIO bus exists at this layer, any PHY access goes through the shared indirect access functions configured in `mt753x_table[]`. The maximum register set in `sw_regmap_config` must cover all registers used by AN7583/EN7581/MT7988 paths.

## Test Signals

Useful tests include platform probe on each compatible, successful MMIO regmap reads of chip ID/trap registers, reset assertion/deassertion, DSA registration, live ethtool/stat reads without delayed cache, and AN7583-specific link bring-up after `AN7583_GEPHY_CONN_CFG` programming.

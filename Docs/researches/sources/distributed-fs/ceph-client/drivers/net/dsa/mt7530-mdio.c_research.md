# sources/distributed-fs/ceph-client/drivers/net/dsa/mt7530-mdio.c

## Purpose

This file is the MDIO transport driver for MediaTek MT7530, MT7621, and MT7531 switch variants. It allocates `struct mt7530_priv`, builds a regmap over an MDIO bus using MT7530 page/register addressing, handles reset/regulator resources for standalone versus MCM hardware, creates MT7531 SGMII PCS instances, and registers the shared DSA switch implementation from `mt7530.c`.

## Important APIs, Types, And Functions

`mt7530_regmap_write()` and `mt7530_regmap_read()` translate 32-bit switch register accesses into MDIO page register writes/reads via page register `0x1f`, low word register `r`, and high word register `0x10`. `mt7530_mdio_regmap_lock()` and `_unlock()` use nested MDIO locking for PCS regmaps. `mt7531_create_sgmii()` allocates per-port regmap configs for port 5/6 SGMII blocks and calls `mtk_pcs_lynxi_create()`.

The OF match table maps `"mediatek,mt7621"`, `"mediatek,mt7530"`, and `"mediatek,mt7531"` to `mt753x_table[]` entries. `mt7530_probe()` allocates state, calls `mt7530_probe_common()`, detects `"mediatek,mcm"`, obtains either reset control or reset GPIO, obtains core/io regulators for MT7530, initializes the MDIO regmap, assigns `create_sgmii` for MT7531, and calls `dsa_register_switch()`. Remove and shutdown paths disable regulators, call `mt7530_remove_common()`, destroy PCS instances, or shut down DSA.

## Control Flow

Probe begins from the MDIO driver core. Shared initialization sets up the DSA switch, operations, locks, and variant data. The transport-specific code then gathers reset and power resources, creates the regmap, installs the optional SGMII factory, and registers the switch. During shared DSA setup, `mt753x_setup()` in `mt7530.c` calls back into `priv->create_sgmii` for MT7531. Remove disables power rails, unregisters the switch through common removal, and tears down SGMII PCS objects.

## State And Persistence Behavior

Software state is held in devm-managed `struct mt7530_priv`, the MDIO regmap, regulator handles, optional reset GPIO or reset controller, and PCS pointers in `priv->ports[5]` and `[6]`. Hardware state is programmed through MDIO pages and survives until reset or power removal. `regmap_config.disable_locking = true` places locking responsibility on driver-level MDIO and DSA paths.

## Dependencies And Integration Points

The file depends on Linux MDIO, regmap, reset, regulator, GPIO, OF, DSA, and `pcs-mtk-lynxi`. Its key integration point is `mt7530_probe_common()`/`mt7530_remove_common()` and the exported `mt753x_table[]` from `mt7530.c`. It registers as an `mdio_driver`, not as a platform driver, and is selected by compatible strings in devicetree.

## Risks

The MDIO regmap translation assumes the switch page scheme and 32-bit split access order; broken locking or partial writes can corrupt register transactions. Remove disables `core_pwr` and `io_pwr` unconditionally, so error logs are possible if those pointers were not valid for a non-MT7530 path. SGMII PCS cleanup must match creation: if port 6 creation fails after port 5 succeeds, the error path destroys port 5. MCM detection changes reset sequencing, so devicetree must accurately describe the hardware.

## Test Signals

Probe should succeed for all three compatible strings with correct chip detection in shared setup. Signals include correct MDIO register reads through regmap, successful regulator enable/disable on MT7530, reset GPIO/control transitions, SGMII PCS creation on MT7531AE/BE, DSA switch registration, and clean shutdown via `dsa_switch_shutdown()`.

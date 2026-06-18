# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-ufs.c

## Purpose

This file is the Qualcomm QMP UFS PHY platform driver. It binds device-tree compatibles such as `qcom,sm8550-qmp-ufs-phy` to SoC-specific register programming tables, maps the PHY register blocks, exposes a Linux generic PHY, and sequences regulators, clocks, resets, register writes, and ready polling needed by the UFS host controller.

The file is mostly static initialization data. Its active logic is a small PHY state machine around those data tables:

- Select a `struct qmp_phy_cfg` from the OF match table.
- Map SERDES, PCS, TX, RX, and optional second-lane register windows.
- Register three fixed-rate symbol clocks for the UFS controller.
- On PHY use, enable supplies and clocks, program base and gear-specific tables, release reset, start SERDES, and poll PCS readiness.

## Important APIs, types, and data

- `struct qmp_ufs_offsets` describes offsets for single-register-space bindings: `serdes`, `pcs`, `tx`, `rx`, `tx2`, and `rx2`.
- `struct qmp_phy_cfg_tbls` groups SERDES/TX/RX/PCS initialization arrays and carries `max_gear` for overlay tables.
- `struct qmp_phy_cfg` is the per-compatible hardware description. It records lane count, offsets, max supported UFS HS gear, base tables, HS Series B tables, up to two gear overlays, regulator bulk definitions, per-generation PCS register layout, and `no_pcs_sw_reset`.
- `struct qmp_ufs` is runtime state: device pointer, selected cfg, mapped register bases, clocks, regulators, optional UFS reset, `struct phy`, and the last requested `mode`/`submode`.
- `qmp_phy_init_tbl` and `QMP_PHY_INIT_CFG()` come from shared QMP headers and drive the table writes via `qmp_configure()` and `qmp_configure_lane()`.
- `ufsphy_v2_regs_layout` through `ufsphy_v6_regs_layout` normalize PCS register offsets for reset, start, ready, and power-down registers.
- Per-SoC table families such as `sm8550_ufsphy_*`, `sm8650_ufsphy_*`, `sm8750_ufsphy_*`, and `milos_ufsphy_*` tune PLL, CDR, RX equalization, TX drive, Hibern8 timing, and advertised HS gear capabilities.

The exported integration surface is `qcom_qmp_ufs_phy_ops`:

- `.init = qmp_ufs_phy_init`
- `.power_on = qmp_ufs_power_on`
- `.power_off = qmp_ufs_power_off`
- `.calibrate = qmp_ufs_phy_calibrate`
- `.set_mode = qmp_ufs_set_mode`

## Control flow

Probe:

1. `qmp_ufs_probe()` allocates `struct qmp_ufs`, reads the OF match data, fetches all clocks via `devm_clk_bulk_get_all()`, and gets per-cfg supplies with `devm_regulator_bulk_get_const()`.
2. The driver supports two DT shapes. If a child node exists, `qmp_ufs_parse_dt_legacy()` maps parent resource 0 as SERDES and maps child resources by index for TX, RX, PCS, optional TX2/RX2, and optional `pcs_misc`. Without a child, `qmp_ufs_parse_dt()` maps one resource and derives block bases from `cfg->offsets`.
3. `qmp_ufs_register_clocks()` registers fixed-rate `rx_symbol_0`, `rx_symbol_1`, and `tx_symbol_0` clocks through an OF clock provider.
4. A generic PHY is created with `devm_phy_create()`, driver data is attached, and `devm_of_phy_provider_register()` publishes the PHY.

Runtime PHY operations:

1. `qmp_ufs_set_mode()` validates that the requested UFS gear submode is nonzero and within `cfg->max_supported_gear`, then stores mode/submode.
2. `qmp_ufs_power_on()` enables regulators and all clocks, then sets `SW_PWRDN` in the PCS power-down-control register to bring the active-low PHY power state up.
3. `qmp_ufs_phy_calibrate()` asserts the delayed `ufsphy` reset, writes the base register tables, applies the best matching gear overlay from `qmp_ufs_get_gear_overlay()`, optionally applies HS Series B overrides, deasserts reset, clears PCS software reset when present, starts SERDES, and waits up to `PHY_INIT_COMPLETE_TIMEOUT` for `PCS_READY`.
4. `qmp_ufs_power_off()` clears `SW_PWRDN`, disables clocks, and disables regulators.

`qmp_ufs_phy_init()` exists primarily for older hardware where `no_pcs_sw_reset` is true. It lazily requests the `"ufsphy"` reset to avoid a circular dependency between the UFS controller and its PHY.

## State and persistence behavior

The driver keeps only volatile kernel state in `struct qmp_ufs`. The persistent hardware programming is the register state written into the PHY while powered. There is no filesystem persistence or firmware handoff in this file.

`mode` and `submode` are stored until the next `set_mode()` call and influence calibration table overlays. If a consumer skips setting mode/submode or asks for an invalid gear, calibration may either use only base tables or fail earlier through `qmp_ufs_set_mode()`. The `ufs_reset` pointer is cached after the first successful lazy reset lookup.

## Dependencies and integration points

- Linux PHY framework: `devm_phy_create()`, `phy_set_drvdata()`, `devm_of_phy_provider_register()`, and the generic PHY callbacks.
- Device tree matching through `qmp_ufs_of_match_table`.
- Common QMP helpers and register definitions from `phy-qcom-qmp-common.h`, `phy-qcom-qmp.h`, PCS UFS headers, and QSERDES UFS headers.
- UFS mode constants from `<ufs/unipro.h>` such as `UFS_HS_G3`, `UFS_HS_G4`, and `UFS_HS_G5`.
- Regulators `vdda-phy` and `vdda-pll`, with SoC-specific initial load values.
- Reset framework for the delayed `"ufsphy"` reset.
- Clock framework for input clocks and fixed-rate UFS symbol clock providers.
- Platform resource mapping and legacy child-node mapping APIs.

## Risks and edge cases

- The register tables are hardware-tuning data. A wrong offset header, table value, lane count, or compatible-to-cfg association can cause silent link instability rather than a clear probe failure.
- `qmp_ufs_get_gear_overlay()` falls back to the lowest overlay when no exact gear match exists. That is deliberate, but a missing overlay `max_gear` can make a higher gear run with only base tuning.
- `qmp_ufs_set_mode()` rejects submode `0`. Consumers must set a valid UFS gear before calibration on paths that depend on overlays.
- Legacy binding resource indexes are fixed and differ between one-lane and two-lane configs. Device-tree mistakes can map the wrong block and lead to register writes into the wrong region.
- Some cfgs set `no_pcs_sw_reset`, which changes reset ownership and uses lazy reset acquisition. Reset naming or dependency mistakes can create deferred-probe or calibration failures.
- `qmp_ufs_power_on()` sets `SW_PWRDN` but does not program tables; table programming is in `.calibrate`, so the UFS host must call PHY ops in the expected order.

## Test signals

- Build coverage: `CONFIG_PHY_QCOM_QMP_UFS`, all included QMP register headers, and OF match table compile checks.
- Probe-time signals: successful regulator/clock/reset acquisition, successful ioremap path for both legacy and flat bindings, and symbol clock provider registration.
- Runtime signals: `phy initialization timed-out` from failed `PCS_READY` polling; regulator or clock enable errors; invalid submode errors.
- Hardware tests should include link bring-up for each compatible family, HS Series A/B mode selection, G4/G5 overlay selection, two-lane and one-lane devices, suspend/resume through the UFS stack, and repeated power-cycle/calibrate sequences.

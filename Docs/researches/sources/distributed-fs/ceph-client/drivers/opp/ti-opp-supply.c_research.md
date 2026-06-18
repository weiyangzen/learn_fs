<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/ti-opp-supply.c -->
# sources/distributed-fs/ceph-client/drivers/opp/ti-opp-supply.c

## Purpose
`ti-opp-supply.c` is a TI OMAP-specific platform driver that plugs a custom regulator transition callback into the generic OPP core. It supports OPP supply handling where a CPU VDD rail may need efuse-optimized voltage values and a second ABB/VBB rail must be sequenced with VDD.

## Important APIs, Types, And Functions
Private data types include `struct ti_opp_supply_optimum_voltage_table`, `struct ti_opp_supply_data`, and `struct ti_opp_supply_of_data`. The single static `opp_data` stores the optimized voltage table, absolute max voltage, and scratch arrays for old/new two-regulator supply values.

Key functions are `_store_optimized_voltages()`, `_free_optimized_voltages()`, `_get_optimal_vdd_voltage()`, `_opp_set_voltage()`, `ti_opp_config_regulators()`, and `ti_opp_supply_probe()`. The OF match table recognizes `"ti,omap-opp-supply"`, `"ti,omap5-opp-supply"`, and `"ti,omap5-core-opp-supply"`.

## Control Flow
Probe reads match data, stores it as driver data, optionally maps efuse registers and parses `ti,efuse-settings` plus `ti,absolute-max-voltage-uv`, then registers `ti_opp_config_regulators()` with the OPP core for CPU0 through `dev_pm_opp_set_config_regulators()`.

During an OPP transition, `ti_opp_config_regulators()` fetches new supplies, compares old and new OPP frequencies, maps nominal VDD to an optimized voltage if an efuse table exists, raises the minimum VDD when necessary, and programs rails. On scale-up it programs VDD before VBB; on scale-down it programs VBB before VDD. On failure it fetches old supplies and attempts to restore VBB then VDD.

## State And Persistence
The efuse-derived voltage table and absolute max voltage persist in global static `opp_data`. The OPP core stores the callback as part of the CPU OPP table configuration. Hardware-visible state is regulator voltage settings for VDD and VBB. There is no remove path in this file, so resource cleanup is only covered for probe failure.

## Dependencies And Integration Points
The driver depends on platform resources, OF properties, regulator consumers, CPU device lookup, OPP core regulator configuration APIs, and efuse register MMIO. It is loaded as a platform driver and affects CPU OPP transitions performed elsewhere.

## Risks
`opp_data` is global, so multiple instances would conflict. Probe assumes CPU0 is the target OPP device. `OPPDM_HAS_NO_ABB` is defined in match data but not used to reduce regulator count or alter sequencing, so DT/regulator configuration must still match the callback's two-regulator expectation. There is no driver remove cleanup for the OPP config token returned by `dev_pm_opp_set_config_regulators()`. Restore logic depends on old OPP supply data being valid.

## Test Signals
Test efuse parsing, missing/invalid `ti,efuse-settings`, absolute max voltage bounds, zero efuse fallback to reference voltage, scale-up and scale-down ordering, regulator failure restoration, two-regulator count warnings, probe failure cleanup, and behavior on OMAP5 core variants marked as no-ABB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/opp/ti-opp-supply.c -->

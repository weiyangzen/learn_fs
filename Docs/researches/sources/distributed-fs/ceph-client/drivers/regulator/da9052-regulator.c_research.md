# sources/distributed-fs/ceph-client/drivers/regulator/da9052-regulator.c

## Purpose
This provider supports DA9052 and DA9053 PMIC buck and LDO regulators. It supplies chip-specific descriptor tables, voltage mapping, DVC activation behavior, and buck current limit handling.

## Important APIs, Types, And Functions
`struct da9052_regulator_info` contains a `regulator_desc`, voltage step/range, and activate bit. `struct da9052_regulator` holds the parent MFD pointer, selected info, and registered `rdev`. The main helpers are `da9052_dcdc_get_current_limit()`, `da9052_dcdc_set_current_limit()`, `da9052_list_voltage()`, `da9052_map_voltage()`, `da9052_regulator_set_voltage_sel()`, and `da9052_regulator_set_voltage_time_sel()`.

`DA9052_DCDC()` and `DA9052_LDO()` generate descriptors using regmap-backed enable and voltage selector fields. `da9052_dcdc_ops` adds current limit operations for bucks; `da9052_ldo_ops` omits them.

## Control Flow
The platform driver registers at `subsys_initcall()`. Probe gets the MFD cell ID and parent `struct da9052`, selects the descriptor table based on chip ID, optionally reads platform regulator init data, passes the parent regmap to the regulator core, and registers the selected descriptor with `devm_regulator_register()`.

Voltage listing is normally linear from `min_uV` and `step_uV`, except DA9052 BUCK4 switches to 100 mV steps above 3.0 V. Mapping verifies overlap with the rail range, clamps the minimum upward, applies the BUCK4 high-voltage rule, and validates the resulting selector by listing it. Selector writes update the vsel field and, for DVC-controlled bucks/LDOs, set the matching GO bit in `DA9052_SUPPLY_REG`. Ramp time for those DVC rails is calculated from selector delta at 6.25 mV/us.

## State And Persistence
Static tables distinguish DA9052 from DA9053 variants. Dynamic state consists of the selected table entry and parent chip pointer. Hardware state is in PMIC registers; current-limit range selection depends on chip ID and buck ID.

## Dependencies And Integration Points
The driver depends on DA9052 MFD register accessors and regmap, MFD cell IDs, optional platform data, regulator core regmap selector helpers, and platform-driver lifecycle. OF headers are included for descriptors using `of_match`/`regulators_node`, although probe primarily uses MFD/platform data.

## Risks
Current-limit field placement differs for even and odd buck IDs, so ID/register alignment is critical. BUCK4 voltage mapping differs between DA9052 and DA9053. DVC-controlled rails require activate bits after selector writes; missed activation means the output may not change. Probe assumes `mfd_get_cell(pdev)` and parent driver data are valid.

## Test Signals
Test both DA9052 and DA9053 descriptor selection, BUCK4 mapping around 3.0 V, current limit get/set fields for even and odd bucks, DVC GO-bit writes, ramp-time calculations, enable/disable through regmap, and core constraint rejection for unsupported voltage/current ranges.

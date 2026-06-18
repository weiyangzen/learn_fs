# sources/distributed-fs/ceph-client/drivers/regulator/cros-ec-regulator.c

## Purpose
This provider exposes a ChromeOS EC controlled voltage regulator to the Linux regulator framework. Hardware operations are not local register writes; they are EC host commands keyed by a regulator index from DT.

## Important APIs, Types, And Functions
`struct cros_ec_regulator_data` owns a dynamically filled `regulator_desc`, the registered `regulator_dev`, the parent `cros_ec_device`, DT `reg` index, and a copied EC voltage table. Regulator ops are `cros_ec_regulator_enable()`, `disable()`, `is_enabled()`, `list_voltage()`, `get_voltage()`, and `set_voltage()`. `cros_ec_regulator_init_info()` sends `EC_CMD_REGULATOR_GET_INFO` to discover the name and supported millivolt table.

## Control Flow
Probe allocates driver data, fetches the EC device from the parent, reads regulator init data and the DT `reg` index, initializes descriptor owner/type/ops and `supply_name = "vin"`, then queries EC metadata. It registers one regulator with `devm_regulator_register()` and stores the driver data.

Enable/disable/is-enabled/get-voltage/set-voltage each creates the matching EC command parameter structure with the stored index and calls `cros_ec_cmd()`. Voltage setting converts the core's uV range to an exact mV-compatible range using round-up for the minimum and floor for the maximum; empty ranges return `-EINVAL`.

## State And Persistence
The cached state is the EC-provided descriptor name and voltage table. Actual enable and voltage state persists in the EC/hardware, not this driver. The regulator core tracks consumers and constraints around these EC operations.

## Dependencies And Integration Points
It depends on ChromeOS EC protocol structures and commands, OF regulator constraints, a DT `reg` property for the EC regulator index, and a `vin` upstream supply name. The descriptor name is runtime data returned by firmware, not a compile-time table.

## Risks
Firmware is the authority for names and voltage tables, so malformed EC responses can affect registration. The driver caps copied voltages to the response array size and terminates the name, which mitigates common response issues. No selector is returned from `set_voltage()`, so selector-aware consumers only have `list_voltage()` for enumeration. EC command latency/failure directly affects regulator API calls.

## Test Signals
Test with EC command tracing, successful DT init data parsing, correct `reg` index per node, voltage table sysfs enumeration, uV-to-mV boundary cases in `set_voltage`, enable/is-enabled consistency, and probe failure when EC commands are unavailable.

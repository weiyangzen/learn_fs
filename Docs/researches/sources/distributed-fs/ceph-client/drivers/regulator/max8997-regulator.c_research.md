<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max8997-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/max8997-regulator.c

## Purpose
Implements the regulator subdriver for Maxim MAX8997/MAX8966 PMICs. It exposes LDOs, bucks, safeout outputs, 32 kHz outputs, charger constant-voltage/current controls, and topoff current as Linux regulator devices behind the parent MFD I2C device.

## Important APIs, Types, And Functions
`struct max8997_data` stores parent `max8997_dev`, registered count, ramp delay, GPIO-DVS enable flags, cached BUCK1/2/5 DVS selector tables, three DVS GPIO descriptors, current DVS GPIO index, side-effect policy, and saved suspend states. `regulators[]` is the `struct regulator_desc` table. Key callbacks are `max8997_get_enable_register()`, `max8997_get_voltage_register()`, `max8997_set_voltage_ldobuck()`, `max8997_set_voltage_buck()`, `max8997_assess_side_effect()`, `max8997_set_voltage_charger_cv()`, `max8997_set_voltage_safeout_sel()`, current-limit helpers, and `max8997_reg_disable_suspend()`. Probe uses `max8997_pmic_dt_parse_pdata()`, `devm_gpiod_get_index()`, and `devm_regulator_register()`.

## Control Flow
The platform driver binds to `max8997-pmic`, gets the MFD parent data, optionally parses the `regulators` DT subnode and MAX8997-specific buck DVS properties, converts requested DVS voltages to hardware selectors, initializes all BUCK1/2/5 DVS slots to safe maximums, then writes configured DVS slots. If any BUCK1/2/5 rail uses GPIO-DVS, probe acquires three DVS GPIOs, sets their initial levels from the default DVS index, and enables GPIO-DVS bits in BUCK control registers. Each regulator operation resolves the target enable or voltage register by regulator ID, then reads or updates the parent I2C register. GPIO-DVS buck voltage changes pick a DVS index that contains the requested selector and minimizes voltage movement on other GPIO-DVS bucks.

## State And Persistence
Runtime state is held in `struct max8997_data` and in hardware registers. The DVS selector arrays mirror platform/DT configuration, `buck125_gpioindex` tracks the currently selected GPIO state, and `saved_states[]` stores old enable-register bytes when regulators are disabled for suspend. The driver does not persist state outside the PMIC; hardware register values and GPIO levels survive until changed by firmware, reset, suspend, or another driver path.

## Dependencies And Integration Points
Depends on the MAX8997 MFD core, MAX8997 private register helpers, GPIO consumer API, OF regulator parsing, platform devices, and the regulator framework. Integration surfaces are DT regulator child nodes named after descriptor names, properties such as `max8997,pmic-buck1-uses-gpio-dvs`, `max8997,pmic-buck125-default-dvs-idx`, `max8997,pmic-buck*-dvs-voltage`, and the parent MFD I2C client.

## Risks And Test Signals
Main risks are wrong DVS voltage arrays, invalid default DVS index, unintended cross-rail voltage movement when several bucks share GPIO-DVS, ignored I2C update failures during bulk DVS initialization, suspend disable behavior for special LDOs, and register descriptor drift against PMIC headers. Test by probing with and without OF data, registering every descriptor, sweeping LDO/buck voltage selections, exercising GPIO-DVS transitions while observing all three buck outputs, validating current limit and charger CV selectors, and suspend/resume tests for `set_suspend_disable()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/max8997-regulator.c -->

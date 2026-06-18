<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/sy7636a-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/sy7636a-regulator.c

Purpose: implements the SY7636A VCOM regulator child for e-paper power systems, exposing VCOM voltage readback, enable/disable, and power-good status.

Important APIs/types/functions: `struct sy7636a_data` stores parent regmap and GPIOs. `sy7636a_get_vcom_voltage_op()` reads low/high VCOM adjust registers, combines selector bits, and scales to microvolts. `sy7636a_get_status()` reads the `epd-pwr-good` GPIO. `sy7636a_vcom_volt_ops` provides get_voltage, regmap enable/disable/is_enabled, and get_status. `sy7636a_regulator_probe()` obtains resources and registers the `vcom` descriptor.

Control flow: probe gets the parent regmap, adopts the parent OF node, requires `epd-pwr-good`, allocates state, enables optional `vin` supply using `devm_regulator_get_enable_optional()`, obtains optional `enable` and `vcom-en` GPIOs with initial levels, waits if the chip enable GPIO was used, stores state, writes zero power-on delay, and registers the VCOM regulator. Runtime status comes from GPIO; enable state comes from the operation-mode register.

State and persistence: private state holds GPIO/regmap handles. The VCOM voltage is read-only from hardware adjustment registers; this driver does not implement set_voltage. Power sequencing side effects include enabling `vin`, optional enable GPIO, optional VCOM GPIO default low, and clearing power-on delay.

Dependencies and integration: depends on the SY7636A MFD parent, parent regmap, GPIO descriptors, regulator supply `vin`, OF child `vcom` under `regulators`, and e-paper panel consumers.

Risks and test signals: status read assumes `dev_get_drvdata(rdev->dev.parent)` returns the platform data set by this driver. The optional `vcom-en` GPIO is requested but not otherwise toggled. Test VCOM register combination/scaling, mandatory power-good GPIO absence, optional supply and GPIO behavior, regmap write of power-on delay, enable/disable bit, and status error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/sy7636a-regulator.c -->

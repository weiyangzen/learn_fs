# sources/distributed-fs/ceph-client/drivers/regulator/qcom_spmi-regulator.c

## Purpose
This driver controls Qualcomm SPMI PMIC regulators directly through the parent PMIC regmap. It supports many regulator logical types, voltage range encodings, mode encodings, OCP retry behavior for voltage switches, optional SAW voltage delegation, and PMIC-specific register-base tables for PM6125, PM660, PM8916, PM8941, PM8994, PMP8074, and related chips.

## Important APIs, Types, and Functions
`struct spmi_voltage_range` and `struct spmi_voltage_set_points` describe hardware voltage ranges and software selector spaces. `struct spmi_regulator_mapping` maps type/subtype/revision tuples to logical type, set points, ops, and HPM load threshold. `struct spmi_regulator` stores the regmap, base address, descriptor, set points, slew rate, DT pin-control defaults, OCP work state, and list node. Key functions include `spmi_vreg_read()`, `spmi_vreg_write()`, `spmi_regulator_select_voltage()`, selector conversion helpers, voltage get/set/list/map functions, mode/load/pull-down/soft-start/current-limit helpers, `spmi_regulator_vs_ocp_isr()`, SAW helpers, `spmi_regulator_match()`, `spmi_regulator_init_registers()`, `spmi_regulator_of_parse()`, and `qcom_spmi_regulator_probe()`.

## Control Flow
Probe gets the parent regmap, PMIC match table, optional `qcom,saw-reg` syscon, and then iterates static regulator entries. For each entry it skips SAW slave nodes, allocates `spmi_regulator`, sets register base/name/supply/of_parse callbacks, obtains optional OCP IRQ, and calls `spmi_regulator_match()` to read hardware revision/type/subtype and choose the correct ops and voltage set points. OF parsing applies pin control, pull-down, soft-start, OCP retry properties, and startup register settings. Runtime voltage mapping favors staying in the current range to avoid spikes, then writes range/select registers; modes and load requests update mode registers; OCP interrupts clear and re-enable switches immediately or after a retry delay until retries are exhausted.

## State and Persistence
Most state lives in PMIC registers. In memory the driver caches static description, set-point pointers, calculated `n_voltages`, slew rate, DT config, OCP retry counters/timestamps, and a list of registered regulators. Voltage and mode getters read hardware live. OCP recovery uses delayed work and volatile counters. There is no persistent storage beyond PMIC register state.

## Dependencies and Integration Points
The driver depends on regmap, OF/platform match data, regulator regmap helpers, delayed work, IRQs, syscon/regmap for SAW, and Qualcomm SPMI PMIC register layout. Integration points include DT regulator child nodes, named OCP IRQs, optional `qcom,saw-leader`/`qcom,saw-slave` properties, regulator constraints, and standard regulator sysfs/debug consumers.

## Risks and Test Signals
Risk areas include voltage range conversion mistakes, ignored `spmi_vreg_read()` return values in several read helpers, static/global `saw_regmap` and mutable `spmi_saw_ops`, continuing probe when a listed regulator is unsupported, OCP delayed-work lifetime, and PMIC table/register-base drift. Test signals include probe on each compatible, hardware type/subtype mismatch logs, selector round trips at range boundaries, current-range voltage changes, slew-time calculations, DT pin-control parsing, OCP IRQ retry exhaustion, SAW leader/slave behavior, and regmap fault injection.

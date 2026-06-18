<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps68470-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/tps68470-regulator.c

Purpose: Registers the TPS68470 camera PMIC regulators, covering CORE, ANA, VCM, VIO, VSIO, AUX1, and AUX2 rails used by ACPI/platform camera stacks.

Important APIs and types: `struct tps68470_regulator_data` stores the PMIC clock used by CORE. `TPS68470_REGULATOR()` builds descriptors. `tps68470_regulator_enable()` and `_disable()` wrap regmap enable with `clk_prepare_enable()` and `clk_disable_unprepare()` for the CORE buck. `tps68470_regulator_ops` and `tps68470_always_on_reg_ops` split normal rails from VIO, which has voltage programming but no enable operation.

Control flow: Probe allocates driver data, obtains `tps68470-clk`, sets parent-device regmap as the backing map, optionally applies platform init data per regulator, and registers all regulators. Built-in ordering uses `subsys_initcall()` so regulators and companion clock/GPIO providers appear before camera sensor drivers bind.

State and persistence: Driver state is only the clock pointer. Voltage and enable state live in TPS68470 registers. The CORE enable path has coupled regulator and clock state.

Dependencies and integration points: Depends on the TPS68470 MFD regmap, optional `struct tps68470_regulator_platform_data`, Linux clock framework, and regulator consumers for camera sensors and VCM devices.

Risks: CORE disable turns off the clock before calling `regulator_disable_regmap()`, so error handling cannot re-enable the clock if the PMIC write fails. Probe ordering is important on ACPI systems. VIO cannot be enabled or disabled through this driver, so constraints must reflect always-on hardware expectations.

Test signals: Built-in and module probe, missing clock deferral, CORE enable/disable clock sequencing, all voltage ranges, platform-data init constraints, and camera sensor probe ordering with ACPI-described TPS68470 systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/tps68470-regulator.c -->

# sources/distributed-fs/ceph-client/drivers/power/supply/intel_dc_ti_battery.c

## Purpose
This platform driver exposes battery telemetry for the Intel Dollar Cove TI PMIC coulomb counter on devices where ACPI battery handling is intentionally skipped. Because the PMIC counter is not autonomous across suspend or power-off, it delegates capacity estimation to `adc-battery-helper` and provides synchronized voltage/current samples to that helper.

## Important APIs, Types, and Functions
`struct dc_ti_battery_chip` embeds `struct adc_battery_helper` as its first member, then stores device, PMIC regmap, `VBAT` IIO channel, power supply, and coulomb-counter calibration terms. `dc_ti_battery_get_voltage_and_current_now()` enables the counter at a 15 ms interval, reads VBAT, waits for at least three samples, reads the latched accumulator and sample counter byte-by-byte, disables the counter, applies EEPROM gain and offset correction, and returns uV/uA values. `dc_ti_battery_hw_init()` calibrates the counter, reads PMIC revision, unlocks EEPROM, selects banks, validates trim revision, and loads `cc_gain` and `cc_offset`. Runtime PM operations are the helper suspend/resume callbacks.

## Control Flow
Probe first checks `acpi_quirk_skip_acpi_ac_and_battery()` and defers until ACPI glue provides a `monitored-battery` fwnode. It allocates state, gets the parent `intel_soc_pmic` regmap, obtains the `VBAT` IIO channel, optionally gets a charged GPIO, initializes PMIC hardware/calibration, registers the battery supply, then initializes the ADC helper with the sample callback and charged GPIO.

## State and Persistence
The driver persists EEPROM-derived calibration in `cc_gain` and `cc_offset`. The coulomb counter is normally disabled and only enabled for current sampling, so no long-term Linux-side accumulator is maintained. Capacity state lives in `adc-battery-helper`, while PMIC register state is touched during initialization and each current sample.

## Dependencies and Integration Points
It depends on the Dollar Cove TI PMIC MFD regmap, an IIO `VBAT` channel, the x86 ACPI battery quirk path, `adc-battery-helper`, optional `charged` GPIO, and runtime PM. The power-supply descriptor exposes the helper's standard property set and external-power notification hook.

## Risks
Register ordering matters: the PMIC latches the accumulator when `CC_ACC0` is read, so multi-register reads are intentionally avoided. Division by the sample counter assumes at least one sample was collected. EEPROM is relocked on the normal unsupported-trim path, but write/read errors before `out_relock` can leave the lock restoration best-effort only. Capacity is voltage-estimated, so current readings are momentary and not a full fuel-gauge state.

## Test Signals
Validate probe deferral, ACPI quirk gating, PMIC calibration on A0/A1 trim revisions, unsupported trim fallback, VBAT scaling, signed accumulator conversion, and current polarity. Runtime tests should confirm counter enable/disable writes around reads, helper suspend/resume behavior, and graceful errors on regmap or IIO failures.

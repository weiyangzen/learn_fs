# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_smu_sensors.c

## Purpose
Registers basic SMU ADC-backed sensors and a derived CPU power sensor as Windfarm sensors. It provides CPU temperature, current, voltage, slots power, and CPU power values using SMU SDB calibration partitions.

## Important APIs, Types, And Functions
`struct smu_ad_sensor` wraps one ADC index and `wf_sensor`. `smu_read_adc()` sends `SMU_CMD_READ_ADC` and expects a two-byte reply. Sensor ops scale ADC readings using SDB calibration: `smu_cputemp_get()`, `smu_cpuamp_get()`, `smu_cpuvolt_get()`, and `smu_slotspow_get()`. `struct smu_cpu_power_sensor` combines voltage and current sensors; `smu_cpu_power_get()` either fakes voltage, multiplies V and I, or applies a quadratic transform from `cpuvcp->power_quads`.

## Control Flow
Init requires `smu_present()`, fetches CPUVCP, CPUDIODE, SLOTSPOW, and debug-switch partitions, finds the SMU `sensors` child, creates recognized ADC sensors by OF type/location, tracks CPU voltage/current sensors, and registers `cpu-power` if both exist. Exit unregisters the derived power sensor first, then all basic ADC sensors.

## State, Dependencies, And Integration
Global pointers cache SDB partition data for calibration. `smu_ads` tracks registered basic sensors, and `smu_cpu_power` tracks the derived one. Dependencies include SMU command queue/completion, SDB partition APIs, OF traversal, Windfarm sensor references, and fixed-point arithmetic. PM81/PM91/PM121 and other SMU model loops consume `cpu-temp`, `cpu-current`, `cpu-voltage`, `cpu-power`, and `slots-power`.

## Risks And Test Signals
Calibration partitions are mandatory for some sensor types; missing partitions cause individual sensor creation to fail. The fake-voltage debug switch and quadratic transform are machine/version dependent. `smu_read_adc()` casts command buffer data to `u16 *`, so reply length and alignment matter. Test signals include SDB partition absence, ADC command status/reply length errors, faked voltage path, quadratic power path, derived sensor reference cleanup, and fixed-point output scaling.

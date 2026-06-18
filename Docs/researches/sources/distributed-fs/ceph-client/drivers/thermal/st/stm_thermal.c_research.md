# sources/distributed-fs/ceph-client/drivers/thermal/st/stm_thermal.c

Purpose: STM32 digital temperature sensor driver for `st,stm32-thermal`. It configures DTS calibration, reads factory values, converts frequency samples to temperature, supports thermal trip interrupts, and handles PM.

Important functions and types: `struct stm_thermal_sensor`, `stm_enable_irq()`, `stm_thermal_irq_handler()`, `stm_sensor_power_on()`, `stm_sensor_power_off()`, `stm_thermal_calibration()`, `stm_thermal_read_factory_settings()`, `stm_thermal_calculate_threshold()`, `stm_thermal_set_trips()`, `stm_thermal_get_temp()`, `stm_register_irq()`, `stm_thermal_prepare()`, `stm_thermal_probe()`, and PM callbacks.

Control flow: probe maps MMIO, gets `pclk`, disables and clears IRQs, prepares the sensor by reading factory settings and configuring calibration/prescaler, powers on continuous measurement, registers thermal zone 0, requests a threaded IRQ, enables IRQs, and adds hwmon sysfs.

Temperature path: factory settings provide calibration temperature `t0`, frequency `fmt0`, and ramp coefficient. `get_temp()` requires enabled mode, polls `DTS_DR` for nonzero period sample count, computes measured PTAT frequency from `pclk * sampling_time / periods`, and derives milli-Celsius from `(freqM - fmt0) * 1000 / ramp_coeff + t0`.

Trip and IRQ behavior: `set_trips()` converts low and high trip temperatures to threshold sample counts and writes `DTS_ITR1`. Sentinel values disable low/high tracking. The IRQ handler updates the thermal zone, re-enables IRQs based on current low/high flags, and acknowledges all DTS interrupt flags.

State and persistence: runtime state tracks mode, clock, threshold enable flags, IRQ, base, and factory calibration values. Suspend disables IRQs, stops/turns off sensor, and disables the clock. Resume repeats preparation, powers on, updates the zone, and reenables IRQs.

Dependencies and integration points: STM32 PCLK, MMIO registers, thermal OF, threaded IRQ, hwmon sysfs, and PM sleep ops.

Risks: `stm_enable_irq()` appears to map low-enabled to `HIGH_THRESHOLD` and high-enabled to `LOW_THRESHOLD`, which may be intentional hardware polarity but is easy to regress; threshold calculation divides by computed frequency and can fail if calibration is invalid; hwmon add is manual and removal only removes hwmon, relying on devm for zone; factory settings must be nonzero.

Test signals: validate factory calibration read on hardware; call `get_temp` before and after power state changes; set low/high trips and verify register bit placement; trigger IRQ and confirm ack/update; suspend/resume and check continuous measurement restarts; test invalid factory values.

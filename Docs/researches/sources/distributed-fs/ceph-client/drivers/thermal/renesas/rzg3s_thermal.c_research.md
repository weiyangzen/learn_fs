# sources/distributed-fs/ceph-client/drivers/thermal/renesas/rzg3s_thermal.c

Purpose: Renesas RZ/G3S TSU thermal driver. Unlike RZ/G2L, temperature samples are read through an IIO channel named `tsu`, while TSU control and OTP trim registers are managed through MMIO.

Important functions and types: `struct rzg3s_thermal_priv`, `rzg3s_thermal_get_temp()`, `rzg3s_thermal_set_mode()`, `rzg3s_thermal_change_mode()`, `rzg3s_thermal_read_calib()`, `rzg3s_thermal_probe()`, `rzg3s_thermal_suspend()`, and `rzg3s_thermal_resume()`.

Control flow: probe maps TSU MMIO, acquires the IIO channel, gets and deasserts reset, enables runtime PM with autosuspend, reads OTP calibration or fallback constants, registers thermal zone 0 with `get_temp` and `change_mode`, and adds hwmon sysfs. Initial mode is disabled until the thermal framework enables the zone.

Temperature path: `get_temp()` returns `-EAGAIN` while disabled. When enabled, it reads eight raw IIO samples with required inter-sample delay, averages them in milli units, applies the datasheet formula `(ts_code_ave - calib1) * 165 / (calib0 - calib1) - 40`, and rounds to 500 mC.

Mode and PM behavior: `change_mode()` toggles TSU hardware only when the mode changes. Enable writes `TSU_SM_EN`, waits at least 30 us, then writes output enable plus enable and waits at least 50 us. Disable writes zero. System suspend disables TSU and asserts reset; resume deasserts reset and restores the previous non-disabled mode.

State and persistence: persistent calibration comes from OTP trim registers. Runtime state tracks current `thermal_device_mode`, reset state, IIO channel, calibration values, and thermal-zone handle.

Dependencies and integration points: IIO consumer API, RZ/G2L ADC dependency, reset controller, runtime PM autosuspend, thermal OF, hwmon, and `renesas,r9a08g045-tsu`.

Risks: the driver stores `priv->mode` after calling `rzg3s_thermal_set_mode()` even if runtime PM resume failed inside the setter; denominator `calib0 - calib1` is assumed nonzero; thermal reads depend on the external IIO provider timing and availability; suspend disables hardware but preserves logical mode for resume.

Test signals: verify disabled reads return `-EAGAIN`; enable/disable through thermal zone mode; test IIO read failure propagation; boot with OTP and fallback calibration; suspend/resume with enabled and disabled modes; check hwmon registration.

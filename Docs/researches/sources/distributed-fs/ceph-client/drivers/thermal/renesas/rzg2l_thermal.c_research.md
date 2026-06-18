# sources/distributed-fs/ceph-client/drivers/thermal/renesas/rzg2l_thermal.c

Purpose: Renesas RZ/G2L TSU thermal sensor driver. It powers the TSU, reads OTP calibration or fallback values, averages ADC samples, applies curvature correction, registers one thermal zone, and exposes hwmon.

Important functions and types: `struct rzg2l_thermal_priv`, `rzg2l_thermal_get_temp()`, `rzg2l_thermal_init()`, `rzg2l_thermal_probe()`, `rzg2l_thermal_remove()`, and reset/runtime-PM cleanup helper `rzg2l_thermal_reset_assert_pm_disable_put()`.

Control flow: probe maps the MMIO resource, gets an exclusive reset, deasserts it, enables runtime PM, reads calibration registers `OTPTSUTRIM_REG(0/1)` with fallback to software constants, initializes TSU normal mode and conversion start, registers thermal zone 0, and adds hwmon sysfs.

Temperature path: each read samples `TSU_SAD` eight times at roughly 20 us intervals, averages the 12-bit codes, applies a scaled curvature correction, converts using `(dsensor - calib1) * 165 / (calib0 - calib1) - 40`, and rounds up to 500 mC.

State and persistence: persistent calibration lives in OTP trim registers. Driver state holds `calib0`, `calib1`, MMIO base, reset, and thermal zone. The remove path removes hwmon, drops runtime PM, and asserts reset.

Dependencies and integration points: platform MMIO, reset controller, runtime PM, OF thermal, hwmon, and `renesas,rzg2l-tsu` compatible.

Risks: if both calibration values are fallback or malformed, conversion accuracy changes; denominator `calib0 - calib1` is assumed nonzero; readl polling for conversion state must match hardware semantics; no explicit system sleep PM hooks are present beyond remove-time cleanup.

Test signals: verify OTP and fallback calibration paths; compare temperature rounding to 0.5 C; check reset assertion on remove/error; test thermal-zone registration and hwmon creation; fault conversion-start polling.

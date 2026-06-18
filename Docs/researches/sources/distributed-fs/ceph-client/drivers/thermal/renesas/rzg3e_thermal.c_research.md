# sources/distributed-fs/ceph-client/drivers/thermal/renesas/rzg3e_thermal.c

Purpose: Renesas RZ/G3E and RZ/T2H TSU thermal sensor driver. It uses runtime PM to power the sensor on demand, reads calibration either from a syscon phandle or secure monitor calls, performs single averaged conversions, programs comparator trips, and handles compare interrupts.

Important functions and types: `struct rzg3e_thermal_info`, `struct rzg3e_thermal_priv`, `rzg3e_thermal_power_on()`, `rzg3e_thermal_power_off()`, `rzg3e_thermal_code_to_temp()`, `rzg3e_thermal_temp_to_code()`, `rzg3e_thermal_get_temp()`, `rzg3e_thermal_set_trips()`, `rzg3e_thermal_irq()`, `rzg3e_thermal_get_syscon_trim()`, `rzg3e_thermal_get_smc_trim()`, and PM callbacks.

Control flow: probe allocates state, initializes a mutex, maps MMIO, obtains match data, reads trim values through the match-specific `get_trim`, validates calibration, verifies the TSU clock rate, gets an optional deasserted reset, requests named IRQ `adcmpi`, enables autosuspend runtime PM, registers thermal zone 0, registers the threaded IRQ, and adds hwmon.

Temperature path: `get_temp` resumes the device, locks hardware access, clears old conversion status, starts one conversion, polls for the averaged-data flag, reads 12-bit `TSU_SCRR`, clears the flag, converts code to milli-Celsius using two calibration points and match-specific temperature endpoints, then autosuspends.

Trip and IRQ behavior: `set_trips()` requires `low < high`, converts both trips to 12-bit codes, disables compare, clears pending compare flags, writes low/high limit registers, enables averaged-data compare mode, unmasks compare IRQ, and starts a conversion. The hard IRQ clears compare status and disables interrupts until the threaded handler updates the thermal zone with `THERMAL_TRIP_VIOLATED`.

State and persistence: trim values are stored in `trmval0`/`trmval1`; runtime state includes power mode, comparison registers, pending status, and reset line. Runtime suspend powers down and clears interrupts; system suspend powers off if active and asserts reset; resume deasserts reset and powers on if runtime-active.

Dependencies and integration points: ARM SMCCC for RZ/T2H trim reads, syscon regmap for RZ/G3E trim reads, clocks, resets, runtime PM, named IRQ, thermal OF, hwmon, and compatibles `renesas,r9a09g047-tsu` and `renesas,r9a09g077-tsu`.

Risks: trim reads are security/firmware or DT dependent; invalid equal or saturated trims fail probe; clock rate below 24 MHz is rejected; compare hardware requires low less than high, so callers passing sentinel extremes incorrectly can fail; autosuspend means every temp/trip path must balance runtime PM references.

Test signals: test syscon and SMC trim variants; verify invalid trim rejection; exercise get-temp under autosuspend; set low/high trips and trigger compare IRQ; suspend/resume while runtime-active and runtime-suspended; validate hwmon warning path does not fail probe.

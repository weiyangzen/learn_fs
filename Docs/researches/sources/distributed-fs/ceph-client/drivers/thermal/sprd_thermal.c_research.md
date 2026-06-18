# sources/distributed-fs/ceph-client/drivers/thermal/sprd_thermal.c

Purpose: Spreadtrum/Unisoc thermal controller driver for UMS512. It configures monitoring periods, reads efuse calibration, initializes child sensors, exposes each as an OF thermal zone, and enables hardware overheat protection.

Important types and functions: `struct sprd_thermal_data`, `struct sprd_thermal_sensor`, `struct sprd_thm_variant_data`, `sprd_thm_cal_read()`, `sprd_thm_sensor_calibration()`, `sprd_thm_rawdata_to_temp()`, `sprd_thm_temp_to_rawdata()`, `sprd_thm_set_ready()`, `sprd_thm_sensor_init()`, `sprd_thm_probe()`, PM helpers, and `sprd_thm_remove()`.

Control flow: probe gets match data, maps MMIO, validates child sensor count, enables the `enable` clock, writes monitor/detection periods, reads global calibration sign and ratio, iterates child sensor nodes, reads each `reg`, derives per-sensor calibration from `sen_delta_cal`, programs overheat/hot thresholds, registers a thermal zone for each sensor, sets controller ready/enabled state, waits for first temperature data, enables all zones, and stores driver data.

Temperature path: each `get_temp` reads a 10-bit raw value from `SPRD_THM_TEMP(id)`, clamps it, and applies `T = cal_slope * raw - cal_offset`. Inverse conversion programs OTP and hot thresholds. The only variant currently has ideal slope `262` and ideal offset `66400`.

State and persistence: persistent calibration is in NVMEM cells `thm_sign_cal`, `thm_ratio_cal`, and per-sensor `sen_delta_cal`. Runtime state includes sensor pointers indexed by ID, ratio sign/offset, clock, and MMIO registers for thresholds, monitor periods, sensor enables, and interrupt bits.

Dependencies and integration points: OF child sensor nodes, NVMEM cells, enabled clock, thermal OF zones, system sleep PM, and hardware PMIC shutdown interrupt path. The driver intentionally enables hardware interrupt bits without registering a Linux IRQ handler because hardware can notify PMIC automatically.

Risks: `sprd_thm_sensor_calibration()` comments mention default calibration but returns error if `sen_delta_cal` is missing; child sensor IDs are used as indexes and must be contiguous for later loops over `nr_sensors`; `sprd_thm_wait_temp_ready()` polls for `!(val & SPRD_THM_TEMPER_RDY)`, which depends on hardware's inverted-ready semantics; overheat IRQ is hardware-only from Linux's perspective.

Test signals: validate NVMEM cell presence and bad length handling; boot with multiple child sensors and non-contiguous IDs to catch indexing assumptions; compare raw/temp conversions; test suspend/resume reprograms enables and waits for data; verify hardware overheat thresholds are written.

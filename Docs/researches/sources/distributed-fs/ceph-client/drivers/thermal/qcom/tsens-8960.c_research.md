# sources/distributed-fs/ceph-client/drivers/thermal/qcom/tsens-8960.c

Purpose: Qualcomm TSENS backend for MSM8960/APQ8064-era hardware. It supplies version-specific register fields, calibration, enable/disable, and suspend/resume operations to the shared TSENS core.

Important APIs/functions: `tsens_msm8960_slope[]` provides per-sensor slopes. `calibrate_8960()` reads `calib` or `calib_backup` QFPROM data, copies one-point calibration values, assigns slopes, and calls `compute_intercept_slope()`. `enable_8960()` sets sensor enable bits, sleep clock, measurement period, reset, and main enable; for IDs above 5 it enables sensors 6..10 together due to a hardware bug. `disable_8960()` clears sensor enables and sleep clock. `suspend_8960()` saves threshold/control registers and disables measurement; `resume_8960()` resets, restores config/threshold/control. `tsens_8960_regfields[]` maps legacy registers into common field IDs.

Control flow: the TSENS core uses `data_8960` to initialize common regmaps, call calibration, enable sensors, read temperatures through `get_temp_common()`, and manage PM callbacks. Threshold fields are shared for all sensors on this hardware.

State/persistence: calibration intercept/slope is stored in core sensor structs; suspend context stores threshold/control registers. Hardware enable and threshold registers persist until suspend/disable. Dependencies: shared `tsens.h` core, regmap, QFPROM helpers.

Risks: only one-point calibration is available; 8660/8960 sensor-count comments differ from platform data, requiring care; sensors greater than 5 must be enabled as a group. Test signals include primary/backup calibration reads, grouped high-sensor enable, suspend/resume register restoration, threshold field mapping, and temperature reads through common core.

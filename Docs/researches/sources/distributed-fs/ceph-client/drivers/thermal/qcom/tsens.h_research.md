# sources/distributed-fs/ceph-client/drivers/thermal/qcom/tsens.h

Purpose: internal interface and data model for the Qualcomm TSENS driver family. It defines calibration modes, IP versions, register-field IDs, per-sensor and per-controller state, SoC operation callbacks, and exported platform data names used by `tsens.c` and version-specific implementation files.

Important APIs and types: `enum tsens_ver`, `enum tsens_irq_type`, `struct tsens_sensor`, `struct tsens_ops`, `enum regfield_ids`, `struct tsens_features`, `struct tsens_plat_data`, `struct tsens_context`, `struct tsens_priv`, `struct tsens_single_value`, and `struct tsens_legacy_calibration_format`. It declares shared helpers including `tsens_read_calibration_legacy()`, `tsens_read_calibration()`, `tsens_calibrate_nvmem()`, `compute_intercept_slope()`, `init_common()`, `get_temp_tsens_valid()`, and `get_temp_common()`.

Control flow role: version-specific files populate `struct tsens_plat_data` with sensor count, hardware IDs, feature flags, bitfield arrays, and `struct tsens_ops` callbacks. `tsens.c` consumes those declarations to run init, calibration, temperature reads, enable/disable, and PM callbacks without embedding per-SoC register layouts.

State model: `struct tsens_priv` owns register maps for TM and SROT spaces, `regmap_field *rf[MAX_REGFIELDS]`, SoC feature pointers, operations, debugfs dentries, a threshold lock, and a flexible array of `struct tsens_sensor`. Each sensor tracks its thermal zone, hardware ID, slope, offset, and optional calibration offsets.

Register dependencies: the macro families `REG_FIELD_FOR_EACH_SENSOR11`, `REG_FIELD_FOR_EACH_SENSOR16`, `REG_FIELD_SPLIT_BITS_0_15`, and `REG_FIELD_SPLIT_BITS_16_31` help SoC files build `struct reg_field` arrays indexed by `enum regfield_ids`. The header explicitly warns that reordering the enum affects allocation loops in `init_common()`.

Integration points: relies on Linux regmap, interrupt, thermal, and allocation headers. It exports platform data symbols such as `data_8960`, `data_8226`, `data_8916`, `data_tsens_v1`, `data_8996`, `data_ipq8074`, and newer IPQ entries, making this header the contract between common and SoC-specific TSENS code.

Risks: enum ordering and field array completeness are high-risk maintenance points. The `MAX_SENSORS` limit constrains flexible allocation and NVMEM parsing. `tsens_resume_common` becomes `NULL` without `CONFIG_SUSPEND`, so SoC ops must tolerate that. Calibration constants and threshold ADC limits are shared assumptions across IP versions.

Test signals: compile all TSENS SoC files together; add static coverage for every `regfield_ids` range used by `init_common()`; validate that every exported `tsens_plat_data` has non-NULL mandatory ops and enough fields for `max_sensors`; test one v0, v0.1, v1, and v2 compatible path.

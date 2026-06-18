# sources/distributed-fs/ceph-client/drivers/thermal/qcom/tsens-v0_1.c

Purpose: Qualcomm TSENS v0.1 backend for early SoCs such as 8226, 8909, 8916, 8939, 8974, and 9607. It defines legacy nvmem layouts, calibration fixups, init quirks, register fields, ops, and platform data.

Important APIs/functions: `tsens_8916_nvmem`, `tsens_8974_nvmem`, and backup layout structures describe bit-level QFPROM extraction. `calibrate_8916()` and `calibrate_8974()` read calibration points and compute slopes/intercepts; `fixup_8974_points()` corrects known calibration-point encodings. Init helpers such as `init_8226()`, `init_8909()`, `init_8939()`, and `init_9607()` set sensor counts or mode quirks before common init. `tsens_v0_1_regfields[]` maps SROT/TM fields for the common core. `data_*` structures bind ops/features/fields to SoCs.

Control flow: the TSENS core selects the `data_*` object from its compatible table, then calls the backend init and calibration hooks before registering sensors and using common get-temp/interrupt helpers. This file does not register a platform driver itself; it links into `qcom_tsens`.

State/persistence: extracted calibration data becomes per-sensor slope/intercept in common state. Register layout and feature structures are static. Dependencies: shared TSENS core, nvmem/QFPROM extraction helpers, regmap fields.

Risks: bitfield layouts are SoC-specific and easy to break; backup calibration selection for 8974 is subtle; init quirks must match compatible data. Test signals include nvmem extraction for each layout, invalid calibration handling, 8974 fixups, per-SoC sensor counts, and common-core temperature conversion.

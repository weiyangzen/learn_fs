# sources/distributed-fs/ceph-client/drivers/thermal/qcom/tsens-v2.c

Purpose: Qualcomm TSENS v2 backend for newer SoCs including generic v2, IPQ8074, IPQ5332/IPQ5424, and MSM8996. It defines feature variants, register fields, calibration from mode/p1/p2 data, no-RPM initialization, and platform data.

Important APIs/functions: `tsens_v2_feat`, `ipq8074_feat`, and `ipq5332_feat` describe capabilities. `tsens_v2_regfields[]` maps v2 SROT/TM fields. `tsens_v2_calibrate_sensor()` calculates per-sensor calibration from two-point or fallback data; `tsens_v2_calibration()` reads calibration mode and sensor points and computes conversion parameters. `init_tsens_v2_no_rpm()` enables/configures TSENS without RPM. Ops tables cover generic v2 and IPQ5332-specific behavior. `data_tsens_v2`, `data_ipq8074`, `data_ipq5332`, `data_ipq5424`, and `data_8996` bind counts/features/ops/fields to platforms.

Control flow: the TSENS core loads the selected platform data, allocates regfields, runs init/calibration hooks, then uses common get-temp and threshold code. Calibration mode determines whether one-point, two-point, or default handling is used.

State/persistence: static data describes hardware; computed calibration is stored in core sensor state. No-RPM init programs enable/configuration bits. Dependencies: shared TSENS core, nvmem/QFPROM helpers, regmap fields.

Risks: per-sensor p1/p2 extraction and mode interpretation are correctness-critical; IPQ feature differences affect interrupts and sensor counts; default calibration can hide bad efuse data. Test signals include two-point calibration math, missing/invalid nvmem fallback, no-RPM init, per-compatible sensor counts, threshold field access, and common get-temp validation.

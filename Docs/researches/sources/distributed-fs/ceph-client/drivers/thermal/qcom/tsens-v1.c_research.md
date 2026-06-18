# sources/distributed-fs/ceph-client/drivers/thermal/qcom/tsens-v1.c

Purpose: Qualcomm TSENS v1 backend for mid-generation SoCs including generic v1, 8937, 8956, 8976, QCS404-style nvmem, and IPQ5018. It provides calibration, register fields, optional no-RPM initialization, and platform data to the shared TSENS core.

Important APIs/functions: `tsens_qcs404_nvmem` describes legacy calibration format. `calibrate_v1()` delegates to common legacy calibration handling for v1 devices. `tsens_v1_feat` and `tsens_v1_no_rpm_feat` describe feature differences. `tsens_v1_regfields[]` defines common register fields. `init_8956()` and `init_tsens_v1_no_rpm()` handle platform-specific setup, including enabling sensors without RPM firmware involvement. Ops tables combine init/calibrate/get-temp behavior for generic, common, 8956, and IPQ5018 variants. `data_8937`, `data_8956`, `data_8976`, `data_ipq5018`, and generic `data_tsens_v1` expose those combinations.

Control flow: selected platform data drives core initialization; calibration populates sensor conversion state; no-RPM init writes enable/configuration fields where needed; temperature reads use common TSENS routines.

State/persistence: static feature/regfield data plus per-device calibration state owned by the core. Hardware enable bits may be programmed during init for no-RPM variants. Dependencies: shared `tsens.h`, regmap fields, nvmem calibration helpers.

Risks: no-RPM and RPM-managed variants must not share the wrong init path; feature flags determine interrupt and ADC behavior in the core; calibration format assumptions must match QFPROM cells. Test signals include each platform data object, no-RPM enable sequence, QCS404 calibration extraction, valid temperature reads, and suspend/resume behavior inherited from common ops.

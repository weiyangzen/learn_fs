# sources/distributed-fs/ceph-client/drivers/mfd/qcom-spmi-pmic.c

## Purpose
`qcom-spmi-pmic.c` is the common Qualcomm SPMI PMIC parent. It creates an SPMI regmap, loads or inherits PMIC revision identity across multi-USID PMICs, exports `qcom_pmic_get()` for child drivers, and populates PMIC child devices.

## Important APIs, Types, And Functions
`struct qcom_spmi_dev` stores USID count and `struct qcom_spmi_pmic` revision data. `qcom_pmic_get_base_usid()` locates the base SPMI device for a multi-USID PMIC. `pmic_spmi_load_revid()` reads type, subtype, revision, major/minor, optional FAB ID, and applies legacy revision quirks. `pmic_spmi_get_base_revid()` copies base revision data under `pmic_spmi_revid_lock`. `qcom_pmic_get()` is exported.

## Control Flow
Probe initializes an extended SPMI regmap and context. If the current USID is a base USID, it reads revision registers; otherwise it finds the sibling base USID and defers until that device is bound. It stores drvdata under a mutex, then calls `devm_of_platform_populate()`. Remove clears drvdata under the same mutex.

## State And Persistence
State is per-SPMI-device drvdata plus revision metadata copied from hardware. The mutex protects cross-device lookups during probe/remove. The driver does not alter persistent PMIC configuration.

## Dependencies And Integration Points
It depends on the SPMI core, `devm_regmap_init_spmi_ext()`, OF matching for many Qualcomm PMIC compatibles, `soc/qcom/qcom-spmi-pmic.h`, and child drivers that call `qcom_pmic_get()` for subtype/revision decisions.

## Risks
Sibling discovery supports only one- and two-USID PMICs. Probe ordering can defer non-base USIDs. `qcom_pmic_get()` assumes the parent matches and has valid drvdata; child drivers should handle error pointers or probe deferral. Type mismatch returns the read result, which may be zero, leaving unsupported hardware identification subtle.

## Test Signals
Exercise one-USID and two-USID PMIC DT layouts, non-base probing before base probing, revision quirks for PM8941/PM8226/PM8110, FAB ID reads for PMI8998/PM660, child `qcom_pmic_get()` calls, and remove while children are unbinding.

# sources/distributed-fs/ceph-client/drivers/regulator/qcom-refgen-regulator.c

Purpose: implements Qualcomm REFGEN MMIO-backed regulator support for SDM845 and SM8250-style reference generator blocks.

Important APIs/types/functions: SDM845 uses custom `qcom_sdm845_refgen_enable()`, `qcom_sdm845_refgen_disable()`, and `qcom_sdm845_refgen_is_enabled()` because enabling requires programming both bandgap control and bias-enable registers. SM8250 uses standard regmap enable/disable helpers on `REFGEN_REG_PWRDWN_CTRL5`. Two static `regulator_desc` instances are selected by OF match data. `qcom_refgen_probe()` maps MMIO, creates a 32-bit stride-4 regmap, gets regulator init data, and registers the regulator.

Control flow: probe retrieves the descriptor from the compatible, maps the platform resource, initializes an MMIO regmap, obtains DT regulator constraints, builds config, and registers one regulator. SDM845 enable writes BG control then bias enable; disable reverses the order. `is_enabled` checks both fields.

State and persistence: no software state is stored beyond devm-managed regmap and regulator device. Enable state lives in MMIO registers.

Dependencies and integration: depends on platform MMIO resources, regmap-mmio, OF regulator init data, and regulator core. Compatibles are `qcom,sdm845-refgen-regulator` and `qcom,sm8250-refgen-regulator`.

Risks and test signals: SDM845 helper functions ignore regmap return values and always report success for enable/disable; `is_enabled()` also ignores read errors. Test both compatibles, MMIO mapping failures, constraint absence, enable/disable/is_enabled register values, and injected regmap errors if test infrastructure supports them.

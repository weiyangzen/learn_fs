# sources/distributed-fs/ceph-client/drivers/thermal/qcom/Kconfig

Purpose: Kconfig entries for Qualcomm thermal drivers: TSENS, SPMI ADC thermal monitor, SPMI PMIC temperature alarm, and LMh.

Important entries: `QCOM_TSENS` depends on `NVMEM_QCOM_QFPROM` and `ARCH_QCOM || COMPILE_TEST`; it builds the multi-version TSENS thermal sysfs driver. `QCOM_SPMI_ADC_TM5` depends on `OF && SPMI && IIO`, selects `REGMAP_SPMI` and `QCOM_VADC_COMMON`, and enables ADC threshold monitor support. `QCOM_SPMI_TEMP_ALARM` has similar OF/SPMI/IIO dependencies and selects `REGMAP_SPMI`. `QCOM_LMH` depends on `ARCH_QCOM || COMPILE_TEST` and selects `QCOM_SCM`.

Control flow/integration: symbols are consumed by the adjacent Makefile. The dependencies align with each driver's required firmware, bus, IIO, regmap, or SCM interfaces.

State/persistence: build-time only. Risks: enabling TSENS requires QFPROM even for platforms whose calibration path may be different; LMh depends on secure monitor calls, so build coverage differs from runtime availability. Test signals include dependency resolution, module builds for each option, and compile-test coverage outside ARCH_QCOM.

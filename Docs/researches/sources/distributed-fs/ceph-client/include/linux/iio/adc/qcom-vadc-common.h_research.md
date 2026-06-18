# `sources/distributed-fs/ceph-client/include/linux/iio/adc/qcom-vadc-common.h`

Purpose: common Qualcomm VADC/ADC5 scaling constants, calibration structures, scale-function enum, data descriptors, and firmware-property conversion helpers.

Important APIs/types/functions: ADC code/range/decimation/settle/average constants, `enum vadc_calibration`, `struct vadc_linear_graph`, `enum vadc_scale_fn_type`, `struct adc5_data`, `qcom_vadc_scale`, `struct qcom_adc5_scale_type`, `qcom_adc5_hw_scale`, TM temperature/voltage conversion helpers, and DT parser helpers for prescale, settle time, average samples, and decimation.

Control flow and state: no persistent state in the header. Runtime code uses calibration graphs and ADC data descriptors to convert raw codes into microvolts or millidegrees and map firmware values into hardware selector indices.

Dependencies/integration: depends on math and types, IIO descriptors referenced indirectly, and Qualcomm ADC/TM drivers.

Risks: physical-unit conversions are sensitive to signed 32/64-bit arithmetic, prescale ratios, absolute vs ratiometric calibration, and lookup-table scale function selection; enum comments contain duplicated PMIC therm wording, so callers must use exact enum names.

Test signals: known-code-to-voltage/temperature vectors for every scale function, DT parser invalid values, min/max ADC codes, prescale ratio mapping, PMIC5/PMIC7 thermistor paths, and overflow checks.

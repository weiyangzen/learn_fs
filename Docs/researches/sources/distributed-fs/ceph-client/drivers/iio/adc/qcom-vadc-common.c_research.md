# sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-vadc-common.c

Shared Qualcomm VADC/ADC5 scaling and DT conversion helper library. It converts raw ADC codes into microvolts or millicelsius, maps temperatures to ADC codes for thermal-monitor thresholds, and validates DT prescale, settle, averaging, and decimation values used by multiple Qualcomm ADC drivers.

Internal `struct vadc_map_pt` tables encode thermistor and die-temperature curves. Exported APIs are `qcom_vadc_scale`, `qcom_adc_tm5_temp_volt_scale`, `qcom_adc_tm5_gen2_temp_res_scale`, `qcom_adc5_hw_scale`, `qcom_adc5_prescaling_from_dt`, `qcom_adc5_hw_settle_time_from_dt`, `qcom_adc5_avg_samples_from_dt`, `qcom_adc5_decimation_from_dt`, and `qcom_vadc_decimation_from_dt`. Internal helpers implement calibration graph scaling, thermistor lookup interpolation, hardware-calibrated ADC5 voltage/therm/die/SMB/charger calculations, and inverse threshold mappings.

Legacy VADC callers pass a scale type, measured calibration graph, prescale ratio, absolute/ratiometric flag, and raw code to `qcom_vadc_scale`. ADC5 callers pass a hardware-calibrated scale type and prescale index to `qcom_adc5_hw_scale`, which dispatches through `scale_adc5_fn`. DT helper functions scan fixed tables or validate powers of two. Thermal-monitor helpers invert thermistor maps to produce ADC threshold codes.

The file has no mutable device state: only static lookup tables and prescale arrays. It is used by `qcom-spmi-vadc.c`, `qcom-pm8xxx-xoadc.c`, `qcom-spmi-adc5.c`, Gen3 ADC/TM code, and likely ADC thermal-monitor drivers.

Risks include lookup table ordering assumptions, unchecked prescale index use in `qcom_adc5_hw_scale` relying on caller validation, low-voltage clamping of ADC5 codes above `VADC5_MAX_CODE`, and integer precision loss. Test interpolation boundaries, inverse conversions, invalid scale types, all DT helpers, full-scale variants, thermistor/die maps, and monotonicity.

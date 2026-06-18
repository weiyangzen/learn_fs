# sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-spmi-vadc.c

Qualcomm SPMI PMIC voltage ADC driver for older VADC peripherals. It parses DT channel children, validates mandatory reference channels, measures calibration graphs at probe, and exposes raw or processed IIO readings for voltage and temperature inputs.

`struct vadc_channel_prop` stores channel number, calibration type, decimation, prescale, settle time, averaging, scale function, and label. `struct vadc_priv` holds regmap/base, parsed channels, reference calibration graphs, completion, mutex, and polling flag. Main functions are `vadc_configure`, `vadc_do_conversion`, `vadc_measure_ref_points`, `vadc_get_fw_channel_data`, `vadc_get_fw_data`, `vadc_read_raw`, `vadc_check_revision`, and `vadc_probe`.

Probe reads parent regmap and base, checks peripheral type/subtype/revision, parses child channels, requests an EOC IRQ or enables polling, sets follow-warm-reset behavior, measures absolute and ratiometric reference points, then registers IIO. A read configures mode/channel/decimation/settle/averaging, enables ADC, requests conversion, waits by IRQ or polling and double-checks EOC, reads a clamped 16-bit result, disables ADC, then either returns raw code or calls `qcom_vadc_scale`.

Probe-time calibration graphs remain in memory and are reused for processed conversions. Per-channel properties are parsed once from DT. Dependencies are SPMI parent regmap, fwnode child channels, IIO labels and fwnode xlate, platform IRQs, and `qcom-vadc-common.c`. Mandatory reference channels are 1.25 V, 0.625 V, VDD, and GND references.

Risks include hard probe failures for absent/equal reference readings, timeout scaling with averaging, raw-only channel entries without scale functions, strict DT validation, and no runtime remeasurement of reference drift. Test revision checks, mandatory references, IRQ/polling, raw-only vs processed channels, fwnode xlate, invalid DT properties, ADC reset errors, and thermistor/die/charger/default scaling.

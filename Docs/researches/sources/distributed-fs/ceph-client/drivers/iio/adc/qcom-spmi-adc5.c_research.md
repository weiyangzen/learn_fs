# sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-spmi-adc5.c

Qualcomm PMIC ADC5/ADC7 IIO driver for SPMI ADC peripherals. It parses DT-defined channels, programs ADC5 or ADC7 conversion registers, waits by IRQ or polling fallback, and returns processed physical values using hardware-calibrated scaling tables from the common Qualcomm ADC code.

`struct adc5_channel_prop` stores channel number, calibration method/value, SID for ADC7, prescale, decimation, settle time, averaging, scale function, and label. `struct adc5_chip` stores regmap/base, IIO arrays, completion, mutex, polling flag, and `struct adc5_data`. Key functions are `adc5_configure`, `adc7_configure`, `adc5_do_conversion`, `adc7_do_conversion`, `adc_read_raw_common`, `adc5_get_fw_channel_data`, `adc5_get_fw_data`, and `adc5_probe`.

Probe obtains the parent regmap and base `reg`, initializes completion and mutex, matches ADC data for ADC5/ADC7/rev2, parses child channels, requests the EOC IRQ if present, otherwise enables polling for ADC5, and registers IIO. ADC5 conversion writes a block from digital parameter through conversion request and waits for IRQ or polls status. ADC7 writes application SID, channel/timing configuration, conversion request, waits briefly, checks conversion-fault status, and reads voltage data. Processed reads call `qcom_adc5_hw_scale`.

State is parsed DT properties plus selected static data tables. ADC register programming is per conversion, and calibration is hardware-provided rather than measured at probe. Dependencies are SPMI parent regmap, platform IRQs, fwnode child nodes, `dt-bindings/iio/qcom,spmi-vadc.h`, IIO direct mode, and common Qualcomm parsing/scaling helpers.

Risks: ADC7 has no polling support; missing/broken IRQ can cause bad read behavior. Channel validity and table support rely on static arrays and `info_mask`. Digital-version detection controls settle-time table selection. Test all compatibles, IRQ and polling paths, ADC7 virtual SID translation, invalid DT properties, conversion faults, invalid data sentinel, scaling, and concurrent read serialization.

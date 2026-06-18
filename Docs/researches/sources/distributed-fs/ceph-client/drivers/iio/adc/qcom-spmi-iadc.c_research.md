# sources/distributed-fs/ceph-client/drivers/iio/adc/qcom-spmi-iadc.c

Qualcomm SPMI PMIC current ADC driver exposing internal and external current-sense channels through IIO. It calibrates gain and offsets at probe, reads sense resistor values from hardware/DT, and converts ADC codes into current values.

`struct iadc_chip` holds regmap/base, sense resistor values, calibration offsets, gain code, completion, mutex, and polling flag. Important functions are `iadc_configure`, `iadc_do_conversion`, `iadc_read_raw`, `iadc_update_offset`, `iadc_rsense_read`, `iadc_version_check`, and `iadc_probe`. The IIO channel table exposes `INTERNAL_RSENSE` and `EXTERNAL_RSENSE` as `IIO_CURRENT`.

Probe allocates IIO state, gets the parent regmap and base, checks peripheral type/subtype/revision, reads external resistor DT value and internal nominal resistor trim, obtains EOC IRQ or enables polling, performs warm-reset follow configuration, requests IRQ/wakeup if available, measures gain and both offset channels, then registers IIO. A raw read locks the device, configures normal mode, channel, decimation, settle, averaging, enables ADC, requests conversion, waits by IRQ or polling, reads 16-bit data, disables ADC, subtracts channel offset, converts raw code to microvolts using gain, divides by sense resistance, and returns microamps.

Gain and offset calibration codes plus internal/external sense resistances are held in memory after probe. Hardware conversion state is transient. Dependencies include parent SPMI regmap, platform `reg`, optional `qcom,external-resistor-micro-ohms`, IRQ completion, IIO, and PMIC trim register `IADC_NOMINAL_RSENSE`.

Risks include wrong default external shunt value when DT omits the resistor, zero shunt rejection, gain equal to offset calibration failure, and possible unsigned wrap in `adc_raw - offset`. Test revision rejection, trim sign handling, IRQ/polling conversions, current math, timeout diagnostics, and scale output.

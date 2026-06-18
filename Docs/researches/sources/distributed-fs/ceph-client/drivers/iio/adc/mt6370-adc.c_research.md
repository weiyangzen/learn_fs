# sources/distributed-fs/ceph-client/drivers/iio/adc/mt6370-adc.c

Purpose: this platform driver exposes MT6370/RT5081-family charger ADC measurements through IIO. It supports charger voltage, bus/battery current, battery thermistor, and junction-temperature channels using synchronous one-shot conversions through the parent regmap.

Important APIs, types, and functions: `struct mt6370_adc_data` holds the regmap, device, ADC mutex, and vendor ID. `mt6370_adc_read_channel()` writes `MT6370_REG_CHG_ADC` with start and input-select bits, sleeps for conversion time, polls until the start bit clears, then reads the big-endian ADC result. `mt6370_get_vendor_info()` reads the vendor nibble and affects current scales. `mt6370_adc_read_scale()` adjusts IBUS and IBAT scales based on vendor and live AICR/ICHG register fields. `mt6370_adc_read_offset()` exposes the fixed temperature offset.

Control flow: probe gets the parent regmap, initializes state and mutex, reads vendor information, resets the ADC selector/start register to zero, then registers a direct-mode IIO device with fixed channel specs. All raw conversions take the ADC lock, so concurrent channel reads cannot interleave selector/start writes.

State and persistence: only the vendor ID is cached in software. Hardware state is the charger ADC control register and charger current-limit registers used for scale. There is no triggered buffer, interrupt handler, PM callback, or persistent storage.

Dependencies and integration points: it uses the MT6370 parent regmap, DT binding constants from `mediatek,mt6370_adc.h`, platform/OF binding `mediatek,mt6370-adc`, Linux bitfield helpers, and IIO direct mode.

Risks: conversion is delay/poll based; a stuck start bit returns an error after roughly three conversion windows. Scale values are coupled to charger current configuration and vendor ID, so wrong `DEV_INFO` decoding yields wrong current units. The offset helper returns `-20` for all channels even though only `TEMP_JC` advertises offset.

Test signals: validate vendor ID decoding for RT5081, RT5081A, MT6370, and fallback IDs; raw conversion success and timeout; scale changes across AICR/ICHG thresholds; label strings; temperature offset; and concurrent reads serialized by `adc_lock`.

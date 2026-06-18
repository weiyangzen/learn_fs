# sources/distributed-fs/ceph-client/drivers/iio/adc/mt6360-adc.c

Purpose: this platform driver exposes the MT6360 PMU/charger ADC as an IIO direct-mode and triggered-buffer device. It provides voltage, current, temperature, and thermistor-reference channels using the parent regmap.

Important APIs, types, and functions: `struct mt6360_adc_data` stores the regmap, mutex, and per-channel last-off timestamps used to avoid stale samples. `mt6360_adc_read_channel()` selects a preferred channel, enables the ADC, waits long enough based on the previous off time, polls the report channel until it matches, reads the big-endian report value, then disables all per-channel enables and restores `NO_PREFER`. `mt6360_adc_read_scale()` provides per-channel scale values, including IBUS dependence on the input-current-limit register. `mt6360_adc_trigger_handler()` reads active scan channels sequentially into a timestamped buffer. `mt6360_adc_reset()` initializes idle wait and ADC enable state.

Control flow: probe obtains the parent regmap, allocates IIO state, initializes the lock, resets the ADC block, sets channel metadata, installs a triggered buffer, and registers the device. Direct and buffered reads share `mt6360_adc_read_channel()`, so the single hardware control path is serialized by `adc_lock`.

State and persistence: hardware state includes ADC enable bits, preferred channel, idle wait, and report registers. Software persists last-off timestamps to choose 25 ms versus 75 ms pre-wait. No data survives device removal.

Dependencies and integration points: it depends on the MT6360 parent MFD regmap, platform/OF compatible `mediatek,mt6360-adc`, IIO buffers, trigger consumer support, and charger registers for current scaling.

Risks: background ADC users for VBAT and TS can collide with requested channels, making the report-channel polling logic critical. Cleanup writes in `out_adc_conv` ignore failures. Buffered scans can be slow because each active channel performs a complete serialized conversion. Scale for IBUS depends on live charger configuration, so users must not cache it blindly.

Test signals: probe/reset, raw reads for all channels, report-channel mismatch timeout, interrupted sleep returning `-ERESTARTSYS`, IBUS scale below and above 400 mA AICR, temperature offset, triggered-buffer scans, and concurrent direct reads returning serialized values.

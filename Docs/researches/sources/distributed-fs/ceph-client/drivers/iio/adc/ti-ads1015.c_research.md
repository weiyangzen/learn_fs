# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads1015.c

Purpose: I2C/regmap IIO driver for ADS1015, ADS1115, and TLA2024 ADCs. It exposes four single-ended and four differential voltage channels, per-channel gain and data-rate controls, one-shot buffered scans, runtime PM, and comparator threshold events for chips that support ALERT/RDY.

Important APIs/types/functions: `struct ads1015_data` stores regmap, mutex, per-channel PGA/data-rate settings, active event channel/mode, thresholds, chip data, and `conv_invalid`. Main functions are `ads1015_get_adc_result()`, trigger handler, scale/data-rate setters, raw read/write callbacks, event read/write/config callbacks, event IRQ handler, buffer setup ops, firmware channel config parsing, conversion-mode control, probe/remove, and runtime PM callbacks.

Control flow: probe selects chip data, initializes threshold defaults, reads optional child-node `ti,gain`/`ti,datarate`, creates an I2C regmap with threshold registers only for comparator chips, sets up a one-hot triggered buffer, optionally configures ALERT/RDY IRQ polarity and requests event IRQ, switches to continuous conversion, enables runtime PM autosuspend, and registers IIO. Raw reads claim direct mode, resume PM, program mux/PGA/data rate and comparator queue if needed, wait for stale conversion periods after config changes, read conversion register, sign-extend, then autosuspend. Events program low/high threshold registers, enable comparator queue/mode, force a first conversion, and push IIO events from the IRQ after reading conversion to clear latch.

State and persistence: persistent state includes per-channel PGA/data rate, thresholds, comparator queue, active event channel, conversion mode, and stale-conversion flag. Hardware state persists in config and threshold registers and is switched to single-shot on runtime suspend/remove.

Dependencies and integration: depends on I2C regmap, runtime PM, IRQ trigger type, IIO events/buffers, one-hot scan validation, firmware child-node properties compatible with the older hwmon ABI, and OF/I2C IDs.

Risks: buffer and event mode are mutually exclusive and enforced through direct-mode claims plus event state. Conversion validity requires sleeping for old plus new data-rate periods after config changes. TLA2024 lacks comparator registers, so event paths are removed through chip info. Firmware channel config fallback silently defaults when no valid children are parsed.

Test signals: ADS1015/ADS1115/TLA2024 variants, scale and sample-frequency available lists, per-channel write/readback, raw reads after data-rate/mux changes, one-hot triggered buffers, runtime suspend/resume stale conversion handling, comparator rising/window events, IRQ polarity validation, threshold/period configuration, and remove power-down.

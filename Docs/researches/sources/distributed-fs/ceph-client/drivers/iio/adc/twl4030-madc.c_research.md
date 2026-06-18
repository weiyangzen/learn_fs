# sources/distributed-fs/ceph-client/drivers/iio/adc/twl4030-madc.c

Purpose: platform IIO driver for the TWL4030 MADC in TWL PMICs, exposing 16 channels for battery, charger, USB, temperature, and general ADC readings, with raw, averaged raw, and processed conversions.

Important APIs/types/functions: `struct twl4030_madc_request` describes conversion method, channel bitmap, averaging, raw/processed mode, and result buffer. `struct twl4030_madc_data` holds device, mutex, bias regulator, method requests, IRQ selection, and ISR/IMR register addresses. `twl4030_madc_conversion()` is the serialized conversion engine. `twl4030_madc_read_channels()` reads and optionally converts values. `twl4030_madc_threaded_irq_handler()` services MADC interrupts, though IIO reads use wait/polling.

Control flow: probe powers MADC, enables battery-type current generator, sets battery measurement bits, ensures MADC high-frequency clock is enabled, selects first or second IRQ registers from platform data/firmware, requests threaded IRQ, configures USB analog routing for MADC[3:6], enables `vusb3v1`, and registers IIO. Reads build a wait-mode request for SW1 or SW2, select channel bitmap and averaging registers, start conversion, poll CTRL for not-busy and EOC, then read channel registers.

State and persistence: a global `twl4030_madc` pointer gates exported conversion use. Active request state is kept per conversion method under mutex. Hardware state includes MADC power, current generators, MADC clock, USB routing, and selected channels. No disk persistence.

Dependencies and integration: TWL MFD I2C helpers, platform data or firmware node, regulator `vusb3v1`, IRQ, IIO direct mode, charger/USB TWL modules.

Risks: global singleton limits multiple instances; error paths must unwind current generator and power; processed conversions contain channel-specific battery current/temperature math and divider ratios; IRQ code services active requests even on I2C error. Test signals include raw/average/processed reads, timeout at 5 ms, first vs second IRQ selection, USB routing/regulator enable, and conversion of channels 1 and 10.

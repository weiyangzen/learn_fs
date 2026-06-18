# sources/distributed-fs/ceph-client/drivers/iio/adc/ad7091r-base.c

## Purpose
`ad7091r-base.c` is the shared IIO core for the AD7091R family used by bus-specific front ends. It implements channel reads, scale reporting, threshold event ABI, IRQ event handling, reference selection, common probe/registration, and exported register access policy helpers.

## Important APIs, types, and functions
The file exports `ad7091r_events`, `ad7091r_probe()`, `ad7091r_writeable_reg()`, and `ad7091r_volatile_reg()` in namespace `IIO_AD7091R`. The base state and chip/init descriptions are declared in the companion header. `ad7091r_set_channel()` writes the conversion channel mask and performs the required dummy result read for the one-conversion sequencer latency. `ad7091r_read_one()` reads a result and checks that the result channel ID matches the requested channel. `ad7091r_read_raw()` implements raw and scale. Event functions read/write threshold high, low, and hysteresis registers and enable or suppress alert generation. `ad7091r_event_handler()` converts alert-status bits into rising/falling IIO threshold events.

## Control flow
Bus drivers call `ad7091r_probe()` with an `ad7091r_init_info` and IRQ. The common probe allocates the IIO device, lets the bus driver initialize `st->map`, installs IIO info and direct mode, runs optional bus setup, selects IRQ-aware or no-IRQ chip info, enables alert generation and requests a threaded IRQ when an IRQ is present, wires channel metadata, configures optional external `vref` or internal reference, switches the part into command mode, and registers the IIO device.

Raw reads are serialized by `st->lock`. Only command mode allows raw reads; otherwise `-EBUSY` is returned. Scale reads use the external regulator voltage when available, otherwise the chip's internal reference millivolt value. Event config reads infer enabled state by comparing threshold registers with sentinel disabled values. Disabling events does not clear global alert enable; it writes high threshold to full scale or low threshold to zero so future alerts for that direction are suppressed.

## State and persistence behavior
The base layer caches the selected mode, optional regulator pointer, chip info, regmap pointer, GPIOs supplied by bus code, and small TX/RX buffers in `ad7091r_state`. Hardware state persists in CONF, CHANNEL, limit, hysteresis, and alert registers. The optional external regulator is enabled during probe and disabled by a devm action. There is no filesystem persistence.

## Dependencies and integration points
This file depends on IIO core/events, interrupt handling, regmap, regulators, cleanup guards, and the bus-specific `set_mode()` / `init_adc_regmap()` callbacks. It is consumed by `ad7091r5.c` and `ad7091r8.c`. It assumes chip info supplies channel arrays, default vref, result-channel-ID extraction, and mode-setting behavior.

## Risks and edge cases
The read path relies on result channel ID validation; bus drivers must supply the correct extractor width. Raw reads fail unless the part is in command mode, so future buffered/autocycle support would need explicit mode transitions. Event disable uses threshold sentinels and leaves alert enable set, so threshold writes after disable can re-enable practical alert behavior. `ad7091r_probe()` assumes `info_irq` is valid when IRQ is nonzero; bus init tables must populate it for IRQ-capable devices. Optional `vref` errors other than defer are treated as absent external reference and cause internal reference enable.

## Test signals
Test probe with and without IRQ, optional setup failure, regmap initialization errors, external vref and internal vref paths, regulator cleanup, raw reads in command and non-command modes, channel-ID mismatch returning `-EIO`, threshold read/write/config for rising/falling/hysteresis, alert IRQ event generation bits, and exported volatile/writeable reg helpers for RESULT and ALERT.

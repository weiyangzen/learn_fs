# sources/distributed-fs/ceph-client/drivers/iio/dummy/iio_simple_dummy_events.c

Purpose: optional event support for the IIO simple dummy driver. It demonstrates event configuration/value sysfs callbacks and IRQ-driven event delivery through the companion fake event generator.

Important APIs/types/functions: `iio_simple_dummy_read_event_config()`, `write_event_config()`, `read_event_value()`, and `write_event_value()` expose event enable and threshold state. `iio_simple_dummy_get_timestamp()` captures timestamp in the hard IRQ handler. `iio_simple_dummy_event_handler()` maps fake register data to IIO event codes. Register/unregister functions allocate the fake IRQ, obtain fake regs, request a threaded IRQ, and release resources.

Control flow: event config validates channel type, event type, and direction before toggling `st->event_en`. The threaded handler inspects `st->regs->reg_data`: 0 emits voltage rising threshold, 1 emits running threshold if cached running exceeds threshold, 2 emits walking falling threshold if cached walking is below threshold, and 3 emits steps change. Timestamp is captured before threaded handling.

State/persistence: `event_en`, `event_val`, `event_irq`, `event_timestamp`, and fake register pointer are per-device volatile state. The event generator holds the simulated IRQ backing store.

Dependencies/integration: depends on IIO events, IRQ APIs, and `iio_dummy_evgen` exported helpers. The channel event specs are declared in `iio_simple_dummy.c`.

Risks: `event_en` is a single boolean shared across all event-capable channels, so enabling one event effectively caches one global enable state. Event handler does not check `event_en` before pushing events. Threshold storage is also global, not per event. Test signals include sysfs enable/value round-trips, fake `poke_ev*` delivery, timestamp ordering, event code selection, and unregister cleanup after failed `request_threaded_irq()`.

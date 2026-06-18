# sources/distributed-fs/ceph-client/drivers/counter/interrupt-cnt.c

Purpose: simple platform driver that counts rising-edge interrupts, optionally reads a GPIO level as the signal, and pushes Generic Counter change-of-state events.

Important APIs/types/functions: `struct interrupt_cnt_priv` stores `atomic_long_t count`, optional GPIO, IRQ number, enable flag, mutex, and per-instance signal/synapse/count descriptors. `interrupt_cnt_isr()` increments the count and calls `counter_push_event()`. Counter callbacks cover enable, action, count read/write, fixed increase function, optional signal level, and watch validation.

Control flow: probe obtains an optional IRQ and optional GPIO, derives an IRQ from GPIO if needed, builds per-instance Generic Counter descriptors, requests the IRQ with `IRQ_NOAUTOEN` and rising-edge trigger, initializes mutex, and registers with `devm_counter_add()`. Userspace enables counting through the `enable` extension, which calls `enable_irq()` or `disable_irq()`. Watch validation only accepts channel 0 `COUNTER_EVENT_CHANGE_OF_STATE`.

State and persistence: count is an atomic in memory and is reset on probe. Enable state is driver memory plus IRQ enabled state. GPIO is read live when requested. No persistent hardware configuration exists.

Dependencies and integration: uses platform/OF compatible `interrupt-counter`, GPIO consumer APIs, IRQ APIs, Generic Counter, and exported `counter_push_event()`.

Risks: `interrupt_cnt_write()` uses the atomic counter type for range validation, so portability depends on `atomic_long_t` width. Disabling an IRQ from sysfs can sleep/block depending on IRQ state. If only an IRQ is provided, signal level reads return `-EINVAL` because no GPIO exists.

Test signals: probe with IRQ-only, GPIO-only, and both sources; enable/disable toggles IRQ delivery; interrupt increments count and wakes cdev watch readers; count write range checks; signal read behavior with and without GPIO; invalid watch events rejected.

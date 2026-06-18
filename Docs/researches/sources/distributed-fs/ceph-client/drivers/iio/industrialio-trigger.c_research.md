# sources/distributed-fs/ceph-client/drivers/iio/industrialio-trigger.c

## Purpose
`industrialio-trigger.c` implements IIO trigger devices and trigger consumers. It registers triggers on the IIO bus, exposes trigger names and per-device `trigger/current_trigger`, allocates per-trigger synthetic IRQs for poll functions, dispatches trigger polls to consumers, handles trigger attachment/detachment, provides pollfunc allocation helpers, and supports immutable/own-device trigger validation.

## Important APIs, types, and functions
- `iio_trigger_ida`, `iio_trigger_list`, and `iio_trigger_list_lock` maintain registered trigger IDs and global name lookup.
- `iio_trigger_register()` and `iio_trigger_unregister()` add/remove trigger devices and global list entries.
- `iio_trigger_set_immutable()` assigns a read-only trigger to an IIO device.
- `iio_trigger_poll()` and `iio_trigger_poll_nested()` dispatch hard-IRQ or nested-thread trigger events to enabled synthetic sub-IRQs.
- `iio_trigger_notify_done()` and the atomic variant decrement `use_count` and reenable the trigger when all consumers finish.
- `iio_trigger_attach_poll_func()` allocates a sub-IRQ, requests a threaded IRQ for an `iio_poll_func`, enables the hardware trigger on first user, and records own-device attachment.
- `iio_trigger_detach_poll_func()` disables the trigger on last user, frees IRQ state, and drops the consumer module reference.
- `iio_alloc_pollfunc()`, `iio_dealloc_pollfunc()`, and `iio_pollfunc_store_time()` support triggered buffer/event handlers.
- `current_trigger_show/store()` implements trigger selection by name.
- `__iio_trigger_alloc()`, `__devm_iio_trigger_alloc()`, `iio_trigger_free()`, and `devm_iio_trigger_register()` manage trigger object lifetime.
- `iio_device_suspend_triggering()` and `_resume_triggering()` disable/enable an attached pollfunc IRQ.

## Control flow
Trigger allocation reserves `CONFIG_IIO_CONSUMERS_PER_TRIGGER` IRQ descriptors, initializes a simple irq_chip whose mask/unmask callbacks toggle per-subirq `enabled`, formats a trigger name, initializes the embedded device, and returns the trigger. Registration assigns an ID, names the device `triggerN`, adds it to the device model, rejects duplicate trigger names under the global list lock, and appends it to the available-trigger list.

Consumers get a `trigger/current_trigger` sysfs group when registered with triggered modes. A store refuses changes while the device is in triggered buffer mode or the trigger is immutable, resolves the trigger by name, validates it through both consumer and trigger callbacks, swaps `indio_dev->trig`, detaches event pollfuncs from the old trigger when needed, and attaches event pollfuncs to the new trigger when needed.

When a trigger fires, `iio_trigger_poll()` or `_nested()` sets `use_count` to the configured maximum and dispatches each enabled synthetic IRQ. Disabled sub-IRQs immediately notify done. Poll functions call `iio_trigger_notify_done()` when finished; when the count reaches zero, the trigger reenable callback runs directly or through work depending on context.

## State and persistence behavior
State is in-memory: trigger ID, device object, global list membership, trigger name, sub-IRQ descriptors, sub-IRQ enabled flags, IRQ pool bitmap, use count, attached own-device flag, consumer `indio_dev->trig` reference, and optional readonly flag in the consumer opaque state. There is no persistent configuration except userspace can reselect triggers at runtime through sysfs.

## Dependencies and integration points
The file integrates with the IIO core bus, Linux IRQ subsystem, device model, module reference counting, sysfs, IIO buffer enable paths, triggered event setup, and driver-provided trigger ops such as `set_trigger_state`, `reenable`, and `validate_device`.

## Risks
- `iio_trigger_poll()` sets `use_count` to `CONFIG_IIO_CONSUMERS_PER_TRIGGER`, not the actual number of active consumers; every disabled sub-IRQ must notify done to avoid stuck triggers.
- Reenable can race with removal or disabled hardware state; comments rely on drivers not blindly reenabling after state is off.
- `current_trigger_store()` checks current mode under `mlock` but performs lookup and assignment after the scoped lock block; concurrent mode changes need scrutiny.
- Attach/detach module references protect the consumer driver while attached, but errors in request/free IRQ paths can leak if ordering changes.
- Duplicate trigger names are detected after `device_add()`, requiring correct cleanup of both device and ID.

## Test signals
- Trigger registration tests should cover duplicate names, ID allocation/free, device release freeing IRQ descriptors, and devm register/unregister.
- Consumer tests should cover trigger selection, readonly triggers, validation callback failures, own-device validation, event pollfunc attach/detach, and busy rejection while triggered buffer mode is active.
- Polling tests should simulate enabled and disabled sub-IRQs, hard IRQ and nested paths, notify-done reenable behavior, and removal races.
- Suspend/resume tests should verify IRQ disable/enable only when a pollfunc IRQ is attached.

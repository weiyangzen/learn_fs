<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/trigger.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/trigger.h

Purpose: Declares the IIO trigger provider interface and trigger object lifecycle.

Important APIs/types/functions: `struct iio_subirq` tracks per-consumer interrupt state; `struct iio_trigger_ops` supplies owner, state, reenable, validate, and try_reenable hooks; `struct iio_trigger` embeds a device, ops, list, pool_lock, subirq base, pool bitmap, attached device list, use count, immutable flag, and driver data. APIs allocate/free, register/unregister, devm-register, poll, generic data-ready polling, validate own triggers, and set immutable triggers.

Control flow: Providers allocate/register triggers; consumers attach poll functions; provider IRQs call `iio_trigger_poll()` or nested variant; core fans out to subirqs and later receives notify-done.

State/persistence: Trigger state includes device lifetime, attached consumers, interrupt pool, use count, and private driver data.

Dependencies/integration: Depends on IRQ, module, atomic, device model, IIO devices, and optional `CONFIG_IIO_TRIGGER`.

Risks: Incorrect reenable/notify discipline can stall triggers; own-trigger validation prevents unsafe self-trigger loops.

Test signals: Trigger registration, consumer attach/detach, poll fanout, nested IRQ contexts, immutable trigger rejection, and disabled-Kconfig builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/trigger.h -->

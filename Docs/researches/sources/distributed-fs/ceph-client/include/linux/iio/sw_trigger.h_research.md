<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/sw_trigger.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/sw_trigger.h

Purpose: Exposes configfs-backed software IIO trigger type registration and lifecycle helpers.

Important APIs/types/functions: `module_iio_sw_trigger_driver()` creates module init/exit. `struct iio_sw_trigger_type`, `iio_sw_trigger`, and `iio_sw_trigger_ops` describe trigger type, instance, and `probe()`/`remove()` hooks. APIs register/unregister types and create/destroy named triggers.

Control flow: Type registration makes configfs trigger creation possible; instance creation calls probe to allocate an `iio_trigger`; destruction calls remove.

State/persistence: Instance state includes the trigger pointer and configfs group for the instance lifetime.

Dependencies/integration: Depends on module, device, IIO core, configfs, and IIO trigger internals.

Risks: Missing cleanup leaves configfs items or triggers registered; names must remain unique.

Test signals: Software trigger module lifecycle, configfs instance creation/removal, trigger visibility under IIO, and error unwind coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/sw_trigger.h -->

# sources/distributed-fs/ceph-client/drivers/iio/iio_core_trigger.h

Purpose: Private IIO core header for trigger consumer registration and poll-function attach/detach helpers.

Important APIs/types/functions: When `CONFIG_IIO_TRIGGER` is enabled, declares `iio_device_register_trigger_consumer()`, `iio_device_unregister_trigger_consumer()`, `iio_trigger_attach_poll_func()`, and `iio_trigger_detach_poll_func()`. When disabled, provides stubs that return success or do nothing.

Control flow: Compile-time configuration chooses real trigger consumer infrastructure or no-op stubs. Implementations live elsewhere in the IIO core.

State and persistence: No direct state. Real implementations manage trigger consumer state and poll-function attachment relationships.

Dependencies and integration points: Internal to IIO core and trigger support. It bridges IIO devices, triggers, and `struct iio_poll_func`.

Risks: Stubs return success when trigger support is disabled, so higher-level code must ensure trigger-specific paths are not exposed in configurations where they cannot operate. The closing comment names `CONFIG_TRIGGER_CONSUMER`, while the guard uses `CONFIG_IIO_TRIGGER`, a minor documentation mismatch.

Test signals: Build with `CONFIG_IIO_TRIGGER=y/m/n`, exercise triggered-buffer setup, attach/detach ordering, and no-trigger builds for drivers selecting triggered buffers conditionally.

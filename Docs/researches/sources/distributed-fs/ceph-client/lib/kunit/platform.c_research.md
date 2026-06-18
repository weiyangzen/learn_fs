# sources/distributed-fs/ceph-client/lib/kunit/platform.c

Purpose: implements KUnit-managed helpers for allocating/registering platform devices, waiting for probe, and registering platform drivers with automatic cleanup.

Important APIs/types/functions: `kunit_platform_device_alloc()`, `kunit_platform_device_add()`, `kunit_platform_device_prepare_wait_for_probe()`, `kunit_platform_driver_register()`, `kunit_platform_device_alloc_init/exit`, probe notifier `kunit_platform_device_probe_notify()`, and action wrappers for unregister functions.

Control flow: allocation creates a `platform_device` as a KUnit resource. Adding first calls `platform_device_add()`. If the device came from `kunit_platform_device_alloc()`, the existing resource free function is changed from `platform_device_put()` to `platform_device_unregister()` to transfer ownership safely; otherwise an unregister action is queued. Probe wait allocates a notifier, completes immediately if already bound, or registers a bus notifier and removes it via an action. Driver registration calls `platform_driver_register()` and queues unregister.

State/persistence: stores platform-device pointers in KUnit resources, temporary notifier blocks, and platform bus registrations. All persistent kernel registrations are tied to KUnit cleanup actions/resources.

Dependencies/integration: integrates `kunit/resource.h`, Linux platform bus APIs, completions, `bus_register_notifier()`, and device locking.

Risks: the refcount transfer in `kunit_platform_device_add()` is critical; failing it can double-put or leak devices. `bus_register_notifier()` return is not checked before adding cleanup. Probe wait relies on caller keeping the completion valid.

Test signals: covered by `platform-test.c`, especially duplicate add, cleanup removal, probe completion, and already-probed behavior.

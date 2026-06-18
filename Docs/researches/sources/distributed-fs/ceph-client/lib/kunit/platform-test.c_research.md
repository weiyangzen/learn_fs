# sources/distributed-fs/ceph-client/lib/kunit/platform-test.c

Purpose: KUnit tests for the KUnit platform-device and platform-driver helper APIs.

Important APIs/types/functions: `kunit_platform_device_alloc_test`, `kunit_platform_device_add_test`, `kunit_platform_device_add_twice_fails_test`, `kunit_platform_device_add_cleans_up`, `kunit_platform_driver_register_test`, `kunit_platform_device_prepare_wait_for_probe_completes_when_already_probed`, and `kunit_platform_driver_test_context`.

Control flow: device tests allocate a platform device, add it to the platform bus, validate name/id/type, test duplicate add failure, and use a fake KUnit context to force cleanup. Driver tests allocate a device, prepare a completion notifier, register a matching driver, wait for probe, and test the already-bound fast path.

State/persistence: temporarily registers platform devices and drivers in the kernel device model. A fake test object is cleaned to verify device removal and refcount migration.

Dependencies/integration: depends on `kunit/platform_device.h`, `linux/platform_device.h`, completions, `platform_bus_type`, `bus_find_device()`, and KUnit cleanup actions.

Risks: duplicate device names may collide if cleanup breaks. The test cannot directly assert refcount underflow, so it relies on absence of later refcount warnings and bus lookup failure.

Test signals: successful cases demonstrate test-managed platform devices unregister on KUnit cleanup, driver registration probes devices, and probe wait completions work both before and after binding.

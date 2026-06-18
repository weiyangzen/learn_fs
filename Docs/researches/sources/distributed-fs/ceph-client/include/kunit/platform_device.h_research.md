# sources/distributed-fs/ceph-client/include/kunit/platform_device.h

Source read summary: 22 lines, 607 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/kunit/platform_device.h` declares KUnit helpers for allocating/adding platform devices and registering platform drivers with optional probe-completion synchronization.

Important APIs, types, and functions: Important exported functions or hooks: `kunit_platform_device_alloc`, `kunit_platform_device_add`, `kunit_platform_device_prepare_wait_for_probe`, `kunit_platform_driver_register`. Important types: `completion`, `kunit`, `platform_device`, `platform_driver`. Important constants/macros: none.

Control flow: Platform-driver tests allocate a device, add it to the platform bus, optionally wait for probe completion, and register drivers under KUnit cleanup ownership.

State and persistence behavior: Platform devices and drivers persist only for the running test case and are unregistered by cleanup actions.

Dependencies and integration points: It is self-contained at include level. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Asynchronous probe ordering and cleanup after partial setup are the main edge cases.

Test signals: Test probe success/failure, deferred/asynchronous probe wait paths, driver registration cleanup, and device add failure cleanup.

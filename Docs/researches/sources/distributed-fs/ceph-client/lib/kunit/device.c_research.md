# sources/distributed-fs/ceph-client/lib/kunit/device.c

Purpose: implements KUnit-managed fake devices and drivers on a dedicated `kunit` bus so tests can exercise driver-model code with automatic cleanup.

Important APIs/types: internal `struct kunit_device`, `kunit_bus_init`, `kunit_bus_shutdown`, `kunit_driver_create`, `kunit_device_register_with_driver`, `kunit_device_register`, and `kunit_device_unregister`. Action wrappers unregister devices and drivers through KUnit cleanup actions.

Control flow: bus init registers a root device and bus type. Driver creation allocates a managed driver, sets name/bus/owner, registers it, and adds a cleanup action. Device registration allocates a `kunit_device`, names it as `<test>.<name>`, sets release/bus/parent, registers it, sets a 32-bit DMA mask, and schedules unregister cleanup. The convenience device path creates both a driver and device and releases the driver action if device registration fails.

State and persistence: persistent state includes global `kunit_bus_device`, registered bus, registered fake devices/drivers, and per-test KUnit actions that own cleanup.

Dependencies and integration: depends on Linux driver core, DMA masks, KUnit resource/action APIs, and device helper headers.

Risks: bus init failure must clean up root device; early unregister must release both device and auto-created driver; driver name memory allocated with KUnit const helpers must be released on manual unregister; device lifetime depends on driver-core release callback.

Test signals: KUnit device tests in core test infrastructure, driver probe/remove tests, leak checks, and module unload path calling bus shutdown.

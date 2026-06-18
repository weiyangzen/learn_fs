# sources/distributed-fs/ceph-client/lib/kunit/device-impl.h

Purpose: internal header for KUnit fake-device bus lifecycle helpers.

Important APIs: declares `kunit_bus_init()` and `kunit_bus_shutdown()` for internal registration/unregistration of the KUnit bus.

Control flow: no runtime logic in the header; it exposes functions implemented in `device.c`.

State and persistence: no direct state.

Dependencies and integration: used by KUnit core/device code to set up and tear down the fake bus for test-managed devices.

Risks: internal-only functions should not become general API; callers must pair init/shutdown around the lifetime of KUnit device helpers.

Test signals: KUnit device tests and build coverage when KUnit is modular or built-in.

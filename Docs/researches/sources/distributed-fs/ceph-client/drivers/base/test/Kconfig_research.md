# sources/distributed-fs/ceph-client/drivers/base/test/Kconfig

Purpose: this Kconfig file declares optional test modules for the Linux device model area in `drivers/base/test`.

Important APIs, types, and functions: it defines `TEST_ASYNC_DRIVER_PROBE`, `DM_KUNIT_TEST`, and `DRIVER_PE_KUNIT_TEST`. `TEST_ASYNC_DRIVER_PROBE` is a tristate module gated by module support (`depends on m`). The two KUnit options depend on `KUNIT` and default to `KUNIT_ALL_TESTS` while remaining individually selectable when not building all KUnit tests.

Control flow: the symbols here are consumed by the adjacent Makefile to include `test_async_driver_probe.o`, root/platform device-model KUnit tests, and property-entry KUnit tests. There is no runtime code in this file.

State and persistence: build configuration state determines which test objects are compiled. No kernel runtime state is stored here.

Dependencies and integration points: the file plugs into the kernel Kconfig tree and exposes test coverage for asynchronous driver probing, device-managed resource release on base devices, platform-device matching, and property-entry software-node APIs.

Risks: `TEST_ASYNC_DRIVER_PROBE` being module-only is intentional because it runs timing-sensitive setup at module load; changing the dependency can make it run too early or as built-in unexpectedly. Incorrect defaults could either hide tests from `KUNIT_ALL_TESTS` or force unwanted test modules into normal builds.

Test signals: selecting the symbols should produce the expected objects from `drivers/base/test/Makefile`. KUnit listings should show `root-device-devm`, `platform-device-devm`, `platform-device-match`, and `property-entry` when the corresponding options are enabled.

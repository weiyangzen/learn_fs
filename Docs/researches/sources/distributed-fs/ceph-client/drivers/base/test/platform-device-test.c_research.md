# sources/distributed-fs/ceph-client/drivers/base/test/platform-device-test.c

Purpose: this KUnit file tests platform-device behavior in two areas: device-managed resource release when platform devices are unregistered, and null firmware-node/device matching helpers.

Important APIs, types, and functions: `struct test_priv` tracks probe/release completion, waitqueues, and the target device. Test helpers include `platform_device_devm_init`, `devm_device_action`, `devm_put_device_action`, `fake_probe`, and `fake_driver`. Test cases cover unprobed and probed platform devices, with and without an extra device reference, plus `platform_device_find_by_null_test`.

Control flow: each devm test allocates or registers a platform driver/device, attaches a devm action, unregisters the platform device, and waits up to `RELEASE_TIMEOUT_MS` for the action to mark completion. The probed variants register `fake_driver`, set driver data before adding the device, wait for probe completion, then validate release. The null-match test creates a KUnit-managed platform device and asserts that `of_find_device_by_node(NULL)`, bus find-by-null helpers, and `device_match_*` predicates all fail cleanly.

State and persistence: all test state is KUnit-allocated or KUnit-managed. Waitqueues provide deterministic synchronization with probe/release callbacks. The fake driver is registered only within the relevant test cases and unregistered before exit.

Dependencies and integration points: it integrates with KUnit, KUnit platform-device helpers, devres, platform bus registration, OF/fwnode/ACPI match helpers, and waitqueue scheduling.

Risks: timing-based waits can fail on a broken release path or a severely stalled environment. The tests intentionally hold references in two cases; if devm release regresses to wait for final put rather than unregister, these tests catch it. Fake driver global state means tests must keep registration/unregistration balanced.

Test signals: KUnit suite names are `platform-device-devm` and `platform-device-match`. Passing tests signal that platform unregister releases devm actions for probed and unprobed devices and that null match inputs are handled as nonmatches rather than accidental matches or crashes.

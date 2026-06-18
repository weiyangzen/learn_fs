# sources/distributed-fs/ceph-client/drivers/base/test/root-device-test.c

Purpose: this KUnit file verifies that bus-less root devices run device-managed actions when unregistered, even when another reference to the device is held.

Important APIs, types, and functions: `struct test_priv` records release completion and the `struct device *`. Helpers include `root_device_devm_init`, `devm_device_action`, and `devm_put_device_action`. Test cases are `root_device_devm_register_unregister_test` and `root_device_devm_register_get_unregister_with_devm_test`.

Control flow: each test registers a root device with `root_device_register`, adds a devm action through `devm_add_action_or_reset`, unregisters the root device, and waits for `release_done` on a waitqueue. The reference-holding test calls `get_device()` and uses a devm action that performs the balancing `put_device()` before signaling completion.

State and persistence: test state is KUnit-allocated and short-lived. The root device exists only for each test case. Waitqueue synchronization prevents the test from relying only on immediate synchronous behavior.

Dependencies and integration points: this targets the base device core, root-device helpers, devres release semantics, reference counting, KUnit resource allocation, and waitqueues.

Risks: the test catches regressions where devm actions are incorrectly deferred until final reference drop rather than device unregister. A timeout indicates either broken release semantics or scheduling issues. The extra-reference test must not leak the reference if the devm action fails to run.

Test signals: the KUnit suite is `root-device-devm`. Passing tests confirm root-device unregister triggers devm actions in both normal and extra-reference cases.

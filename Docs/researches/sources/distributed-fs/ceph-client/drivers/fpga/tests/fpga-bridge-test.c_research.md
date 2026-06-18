<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/tests/fpga-bridge-test.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/tests/fpga-bridge-test.c

## Purpose
`fpga-bridge-test.c` is a KUnit suite for the FPGA bridge core. It creates fake bridge devices, tracks bridge enable state through a minimal `fpga_bridge_ops`, and validates acquisition, exclusive get semantics, direct enable/disable, and list-oriented bridge helper behavior.

## Important APIs, types, and functions
The local fixtures are `struct bridge_stats` and `struct bridge_ctx`. `register_test_bridge()` allocates a KUnit device and registers a fake `struct fpga_bridge` using `fpga_bridge_register()`. `op_enable_set()` backs `fake_bridge_ops` and records the last requested enable state. Test cases cover `fpga_bridge_get()`, `fpga_bridge_put()`, `fpga_bridge_disable()`, `fpga_bridge_enable()`, `fpga_bridge_get_to_list()`, `fpga_bridges_disable()`, `fpga_bridges_enable()`, and `fpga_bridges_put()`.

## Control flow
Suite initialization registers one fake bridge and stores it in `test->priv`. The get test retrieves that bridge by parent device, verifies the second get is rejected with `-EBUSY`, then releases it. The toggle test drives disable and enable calls and checks the private state flag. The list test registers a second fake bridge, pushes both bridges into a list, disables and enables the whole list, then releases all list entries and checks the list is empty.

## State and persistence behavior
State is entirely test-local. KUnit owns allocated contexts and test devices, while `kunit_add_action_or_reset()` guarantees bridge unregister on teardown. The only observed state is `bridge_stats.enable`; there is no persistence outside the test process.

## Dependencies and integration points
The file depends on KUnit device helpers and the public FPGA bridge API. It integrates with the bridge core through the real registration, reference, list, and operation dispatch paths rather than mocking the core internals.

## Risks and edge cases
The suite validates busy reference behavior and list cleanup, but it does not cover bridge operation failures, `enable_show`, multiple competing consumers beyond a duplicate get, or ordering semantics if bridge-list enable fails midway. Because the fake op always succeeds, rollback/error propagation is outside this test's signal.

## Test signals
Useful signals are KUnit pass/fail results for suite `fpga_bridge`, especially `-EBUSY` on a second get, correct `enable` transitions, and an empty bridge list after `fpga_bridges_put()`. Failures indicate regressions in bridge registration lifetime, exclusive access, list insertion order, or operation dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/tests/fpga-bridge-test.c -->

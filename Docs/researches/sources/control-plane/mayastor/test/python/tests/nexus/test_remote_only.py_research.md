# sources/control-plane/mayastor/test/python/tests/nexus/test_remote_only.py

## Purpose
Stress/regression test for nexuses whose children are all remote NVMf bdevs.

## Important APIs, Types, And Functions
Defines `ensure_zero_devices`, `create_publish`, `delete_all_bdevs`, and parametrized `test_remote_only` running ten iterations.

## Control Flow
For each iteration, the test ensures no bdevs exist, creates remote malloc bdevs and shares them, creates/publishes nexuses on a local node using remote children, destroys/publishes cleanup, deletes remote bdevs, waits briefly, and verifies all nodes return to zero bdevs.

## State And Persistence
State includes remote malloc bdevs, shared NVMf URIs, local nexus bdevs, and published resources. The test is designed to leave no bdevs behind.

## Dependencies And Integration Points
Depends on module-scoped Mayastor fixtures and remote NVMf bdev creation/sharing through `MayastorHandle`.

## Risks
Fixed sleeps and ten-iteration loops can be flaky or slow. `ensure_zero_devices` is strict and may fail due to unrelated leftovers from previous tests.

## Test Signals
Passing iterations indicate remote-only nexus creation and teardown do not leak local or remote bdevs.

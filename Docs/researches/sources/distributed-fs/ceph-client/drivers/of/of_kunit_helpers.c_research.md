# sources/distributed-fs/ceph-client/drivers/of/of_kunit_helpers.c

## Purpose
`of_kunit_helpers.c` provides test-managed helper APIs for OF KUnit tests. It centralizes common skip logic for systems without a populated DT root and wraps node/overlay cleanup in KUnit resource actions.

## Important APIs, types, and functions
Exports include `of_root_kunit_skip()`, `of_overlay_fdt_apply_kunit()` when overlays and early flattree are enabled, and `of_node_put_kunit()`. The file uses `KUNIT_DEFINE_ACTION_WRAPPER()` to bind `of_node_put()` as a KUnit cleanup action.

## Control flow and state
`of_root_kunit_skip()` skips on ARM64 or RISC-V ACPI boots where DT may not populate `of_root`. `of_overlay_fdt_apply_kunit()` applies an overlay, stores the overlay changeset ID in KUnit-managed memory, and registers an action that removes the overlay when the test ends or if action registration fails. `of_node_put_kunit()` registers a cleanup action to drop a node reference and fails the test if resource allocation fails.

## Dependencies and integration
This file integrates KUnit resource management, OF overlay APIs, early flattree availability, and the shared `of_root` global. It supports tests in `of_test.c` and other OF KUnit suites.

## Risks and test signals
Risks are mostly test-infrastructure risks: missing cleanup action registration, running DT tests on ACPI-only boots, overlay apply failure, and leaked node references. Signals are KUnit skip messages, overlay removal after tests, and absence of reference leak warnings.

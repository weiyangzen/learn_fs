# sources/distributed-fs/ceph-client/drivers/of/of_test.c

## Purpose
`of_test.c` contains KUnit tests for selected OF core behavior. In this subset it verifies a loaded root DTB and validates resource-bound calculations for OF address resources.

## Important APIs, types, and functions
The `of_dtb` suite includes `of_dtb_root_node_found_by_path()` and `of_dtb_root_node_populates_of_root()`, gated by `of_dtb_test_init()`. The `of_address` suite defines `struct of_address_resource_bounds_case`, parameter descriptions, `of_address_resource_bounds_cases`, and `of_address_resource_bounds()` to exercise `__of_address_resource_bounds()`.

## Control flow and state
The DTB suite skips when helper logic determines there is no populated DT root or when early flattree is not enabled. It then checks `of_find_node_by_path("/")` and `of_root`. The address suite skips without `CONFIG_OF_ADDRESS`, runs parameterized start/size pairs, expects either success with exact `resource` start/end/size values or `-EOVERFLOW` for ranges that cannot fit `resource_size_t`.

## Dependencies and integration
The tests depend on KUnit, `of_root_kunit_skip()` from `of_kunit_helpers.c`, OF path lookup from `base.c`, and an address helper exported under the KUnit namespace. They import `EXPORTED_FOR_KUNIT_TESTING`.

## Risks and test signals
Coverage is focused rather than broad. It catches regressions in root availability assumptions and resource overflow handling, especially on 32-bit `resource_size_t` builds. It does not cover the wider IRQ, dynamic, reserved-memory, or kexec paths in this subset.

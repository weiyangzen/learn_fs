<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/tests/fpga-region-test.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/tests/fpga-region-test.c

## Purpose
`fpga-region-test.c` is a KUnit suite for the FPGA region core. It verifies that a region can be found through class matching and that `fpga_region_program_fpga()` coordinates bridge acquisition/control with FPGA manager programming.

## Important APIs, types, and functions
The fixture combines fake manager, bridge, and region objects in `struct test_ctx`. `op_write()` increments manager programming count, `op_enable_set()` records bridge state and activation cycles, `fake_region_get_bridges()` populates `region->bridge_list`, and `fake_region_match()` supports class lookup. The tests cover `fpga_region_class_find()`, `fpga_region_register_full()`, `fpga_region_program_fpga()`, `devm_fpga_mgr_register()`, `fpga_bridge_register()`, and `fpga_bridges_put()`.

## Control flow
Suite init creates KUnit devices, registers a fake manager, a fake bridge, and a region whose `get_bridges` callback returns that bridge. The class-find test searches for a region with a parent-device predicate and releases the returned device reference. The programming test allocates an image, attaches it to the region, programs the FPGA, checks manager write count and bridge enable cycle count, releases the bridge list, and repeats the programming path to ensure the region can be reused.

## State and persistence behavior
State is test-local: `mgr_stats.write_count`, `bridge_stats.enable`, and `bridge_stats.cycles_count`. KUnit cleanup actions unregister image info, bridge, and region. No durable state is produced.

## Dependencies and integration points
The file depends on KUnit, FPGA manager, FPGA bridge, and FPGA region APIs. It integrates with the real region registration, class find, bridge list, and programming orchestration paths while using fake operations for the hardware-specific endpoints.

## Risks and edge cases
The test intentionally uses one bridge and a write-only fake manager, so it does not validate multiple-bridge rollback, bridge acquisition failure, manager load failures, overlay/DT-driven region behavior, or partial reconfiguration flags. Manual `fpga_bridges_put()` calls are needed after each program cycle because the region keeps the list populated.

## Test signals
Suite `fpga_region` should show successful class lookup, one manager write and one bridge activation per program call, and correct reuse after bridge-list release. Failures indicate regressions in region lookup, bridge orchestration, or manager handoff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/tests/fpga-region-test.c -->

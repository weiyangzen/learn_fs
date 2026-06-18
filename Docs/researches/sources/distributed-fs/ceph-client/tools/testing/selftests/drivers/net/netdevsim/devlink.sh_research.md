# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/devlink.sh

Purpose: Provides broad devlink API regression coverage using a controllable netdevsim device.

Important APIs/functions: Exercises `devlink dev flash`, parameters, default parameter values, regions/snapshots, reload, namespace reload, resources, resource dumps, `devlink dev info`, health reporters, port resources, eswitch/rate objects, and rate attributes including `tx_share`, `tx_max`, parent, and `tc-bw`. Helpers include `param_get`, `param_set`, `check_value`, `res_val_get`, `check_reporter_info`, rate accessors, and `devlink_wait`.

Control flow: `setup_prepare` loads netdevsim and creates `netdevsim10` with four ports. `tests_run` executes `ALL_TESTS`; each test mutates devlink state and verifies either devlink JSON output, debugfs mirrors, or expected command failure. Cleanup deletes the device and unloads the module.

State and persistence: Uses `/sys/bus/netdevsim/new_device`, debugfs knobs under `/sys/kernel/debug/netdevsim/netdevsim10`, devlink objects, network namespaces, SR-IOV VFs, and devlink resource sizes. All should be reverted by test-local cleanup or device deletion.

Dependencies and integration: Sources forwarding `lib.sh` for `check_err`, `check_fail`, `cmd_jq`, `busywait`, `tests_run`, and logging. Requires `devlink`, `jq`, namespace support, debugfs, firmware files for flash, and netdevsim devlink implementation.

Risks: It depends on exact devlink CLI JSON shape and feature availability; several subtests skip when CLI support is missing. Namespace reload and resource tests can leave namespaces if interrupted before cleanup. Health/rate checks rely on debugfs values matching devlink state.

Test signals: Expected passes include correct parameter commit-on-reload behavior, rejected invalid flashes/resources, snapshot read bounds, reporter state/recovery counters, resource visibility by scope, and rate object debugfs/API consistency.

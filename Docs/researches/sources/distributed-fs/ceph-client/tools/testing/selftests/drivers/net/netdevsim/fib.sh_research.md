# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/fib.sh

Purpose: Exercises netdevsim FIB offload/resource behavior for IPv4 and IPv6 routes, including replay, overflow, delete-failure, and flag-change notification paths.

Important APIs/functions: Uses `devlink resource set/show`, `devlink dev reload`, namespaced `ip route`, sysctls `fib_notify_on_flag_change`, and debugfs FIB failure controls. Local helpers check route flags, resource occupancy, route add/delete/replay outcomes, and notification settings.

Control flow: `setup_prepare` creates netdevsim, moves it into `testns1`, creates dummy interfaces, and sets command prefixes. Tests run with notification disabled and enabled, covering route additions, route replacements, route offload failure, IPv6 error replay, delete failure injection, and reload after resource resizing.

State and persistence: Mutates devlink FIB resource sizes, namespaced routes, dummy links, sysctls, and debugfs failure flags. Cleanup deletes namespace/device/module state.

Dependencies and integration: Requires netdevsim FIB offload support, devlink resources, `iproute2`, jq/cmd helpers from forwarding `lib.sh`, and namespace support.

Risks: FIB offload notifications are asynchronous, so sleeps and monitor timing are important. Resource limits and route counts must match netdevsim accounting. Failure injection must be reset or later tests can cascade fail.

Test signals: Expected outcomes include correct `trap`/`offload_failed` route flags, occupancy values, rejected routes over resource limits, clean replay after reload, and no stale state after failed delete/reload scenarios.

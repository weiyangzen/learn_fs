# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/fib_notifications.sh

Purpose: Verifies route netlink notification behavior when FIB offload flags change for IPv4 and IPv6 netdevsim routes.

Important APIs/functions: Helpers `route_addition_check`, `route_deletion_check`, and `route_replacement_check` run `ip monitor route` and inspect emitted lines. `route_notify_check` validates notification count and flag sequence via `check_rt_trap` or `check_rt_offload_failed`. Tests toggle `net.ipv4/ipv6.fib_notify_on_flag_change` and debugfs `fib/fail_route_offload`.

Control flow: Setup creates one netdevsim device, moves it into `testns1`, and adds `dummy1`. For each IP family, tests cover route add, delete, replace, and offload-failed addition under notify modes 0, 1, and 2. Monitors are started before the route mutation, killed after a short wait, and the temp output is checked.

State and persistence: Uses namespaced sysctls, temporary routes/devices, temp files, and netdevsim debugfs fault flags. Cleanup removes `dummy1`, namespace, device, and module.

Dependencies and integration: Relies on forwarding `lib.sh` process helpers, `ip monitor route` output strings, devlink namespace reload, and netdevsim FIB offload flags.

Risks: Monitor timing can be flaky on slow systems. Parsing text flags (`rt_trap`, `rt_offload_failed`) depends on iproute2 output. A killed monitor job must not leave background processes.

Test signals: Correct runs see one notification for normal add/delete/replace when flag-change notification is disabled, two notifications with flag-change enabled, and two failed-offload notifications when notify mode is failure-only.

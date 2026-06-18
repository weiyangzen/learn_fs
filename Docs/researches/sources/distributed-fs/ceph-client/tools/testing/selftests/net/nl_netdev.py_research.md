<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/nl_netdev.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/nl_netdev.py

## Purpose
This Python kselftest validates the `netdev` generic-netlink family for device queries, NAPI listing and threaded mode control, queue reset behavior, and page-pool reporting/orphaning.

## Important APIs, Types, And Functions
It uses `NetdevFamily`, `NetdevSimDev`, `NlError`, `ip()`, `ksft_run()`, `ksft_exit()`, `ksft_eq/ge/ne`, `ksft_raises`, and `ksft_busy_wait`. Test functions are `empty_check()`, `lo_check()`, `dev_dump_reject_attr()`, `napi_list_check()`, `napi_set_threaded()`, `dev_set_threaded()`, `nsim_rxq_reset_down()`, and `page_pool_check()`.

## Control Flow
The tests instantiate `NetdevFamily`, run a basic device dump, validate loopback XDP feature fields, assert that dump requests reject unexpected attributes with extack details, create netdevsim devices with controlled queue counts, inspect NAPI IDs, toggle threaded mode through both netdev-genl and sysfs, reset queues while up/down, and exercise page-pool visibility as a netdevsim device is brought up/down and holds/releases pages.

## State, Persistence, And Dependencies
State includes temporary netdevsim devices, sysfs threaded flags, netdev-genl NAPI state, page-pool references, and debugfs-like netdevsim controls (`queue_reset`, `pp_hold`). Context managers clean up devices. It depends on Python YNL/lib helpers and kernel support for netdev family operations.

## Integration Points
This test connects netdev generic-netlink reporting/control to netdevsim behavior, sysfs threaded NAPI controls, and page-pool lifetime accounting. It also validates strict policy/extack behavior for netdev dump commands.

## Risks
Threaded NAPI and page-pool fields are kernel-version sensitive. Page-pool freeing is asynchronous and uses a busy wait, so slow cleanup can be flaky. Tests rely on netdevsim debug controls and loopback ifindex 1.

## Test Signals
Signals are kselftest assertion results: device dump nonempty, expected loopback feature arrays empty, exact extack message/bad attribute, NAPI counts and threaded PID presence/absence, successful queue reset while down, and expected page-pool inflight/detach behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/nl_netdev.py -->

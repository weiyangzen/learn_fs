# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/fib.sh

## Purpose

Wraps shared FIB offload API tests for mlxsw and adds local-table replacement cases.

## Important APIs, Types, and Functions

Sources `fib_offload_lib.sh` and exposes many `ALL_TESTS` wrappers for IPv4/IPv6 add, metric, TOS, replace, delete, prefix length, replay, flush, multipath append/replace/delete, and local replacement. It adds `ipv4_local_replace`, `ipv6_local_replace`, and a `fib_notify_on_flag_change_set` setup path.

## Control Flow

With zero physical netifs, setup creates namespaces and enables FIB notification behavior through shared helpers. Most test functions delegate to generic library routines with namespace `testns1` and `$DEVLINK_DEV`. Local replacement tests create dummy interfaces, install local and main-table routes for the same host prefixes, and verify which routes carry offload/trap flags.

## State and Persistence Behavior

State is namespace-local routes, dummy interfaces, devlink reload/replay state, and kernel FIB offload flags. It does not change source files.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced. It specifically integrates with `fib_offload_lib.sh` for most assertions.

## Risks and Edge Cases

The suite is sensitive to route flag timing and route-table precedence. Local-table and main-table interactions are subtle; stale dummy routes can contaminate later checks. Replay tests depend on devlink reload preserving and reprogramming route offload state.

## Test Signals

Signals are `fib4_trap_check`/`fib6_trap_check` outcomes, shared FIB library assertions, and successful route replay after devlink operations.

# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/fib_offload_lib.sh

## Purpose
`fib_offload_lib.sh` is a shared library of FIB offload behavior tests. It verifies which IPv4/IPv6 routes should be programmed in hardware, represented in `ip route` JSON by the absence or presence of the `trap` flag, across route add/append/prepend/replace/delete/replay/flush scenarios.

## Important APIs, Functions, and Control Flow
The primitive `__fib_trap_check` runs `ip -n $ns -j -p -$family route show $route` and uses `jq` to test whether route flags contain `trap`. `fib_trap_check` wraps it in `busywait`; `fib4_trap_check` and `fib6_trap_check` specialize by address family. Test functions then create dummy devices in a supplied namespace, manipulate routes, call trap checks, log a subtest, and delete dummy devices.

IPv4 coverage includes identical routes with append/prepend ordering, TOS priority, metric priority, route replace, delete promotion to the next lowest metric, shared-leaf prefix-length routes, devlink reload replay for metric/TOS/prefix length, and flush-on-device-delete. IPv6 coverage includes single route add, metric priority, append without `nexthop`, replace single, multipath metric/append/replace, appending multipath to a non-multipath route, delete variants for single and multipath routes including replacement by next route type, and devlink reload replay for single and multipath routes.

## State, Dependencies, Integration Points, and Risks
State is isolated to the caller-provided namespace plus dummy devices, route entries, route flags, and devlink reload side effects. Dependencies include `ip`, `jq`, `busywait`, `check_err`, `log_test`, and a devlink device argument for replay tests. Consumers must create the namespace and arrange hardware/offload support before calling these functions. Risks include route string matching sensitivity, hardware drivers that use different offload/trap timing, and cleanup gaps if a function fails before deleting dummy devices.

## Test Signals
The signal is whether the expected route is offloaded (`trap` absent) or trapped/not offloaded (`trap` present) within the busywait window. Each scenario has explicit `check_err` messages indicating the violated route ordering or replay rule.

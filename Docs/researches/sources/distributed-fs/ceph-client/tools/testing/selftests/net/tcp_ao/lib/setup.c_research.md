# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/lib/setup.c

## Purpose
`setup.c` provides the TCP-AO selftest process, namespace, thread, output, and sysctl lifecycle used by the tests in `tcp_ao/`. It wraps kselftest result printing so multi-threaded server/client tests do not interleave output, creates isolated parent and child network namespaces connected by a veth, assigns the per-thread local and peer addresses, and centralizes skip/fail/exit handling.

## Important APIs, Types, And Functions
The file exports `__test_msg()`, `__test_ok()`, `__test_fail()`, `__test_xfail()`, `__test_error()`, and `__test_skip()` as mutex-protected kselftest print adapters. Test lifecycle functions include `test_failed()`, `test_add_destructor()`, `open_netns()`, `unshare_open_netns()`, `switch_ns()`, `switch_save_ns()`, `switch_close_ns()`, `synchronize_threads()`, and `__test_init()`. It also exports thread-local `this_ip_addr` and `this_ip_dest`, global `test_family`, and optmem helpers `test_get_optmem()` and `test_set_optmem()`.

## Control Flow
`__test_init()` installs a SIGINT handler, checks required kernel config features for network namespaces, veth, and TCP-AO, sets the kselftest plan, seeds `rand()`, initializes namespaces and ftrace, creates the cross-namespace veth, configures the child namespace, optionally starts the peer thread there, switches back to the parent namespace, configures its endpoint, and invokes the primary peer function. The thread entry stores its endpoint addresses in thread-local globals before running the supplied test function. `synchronize_threads()` implements a reusable two-slot barrier between the server and client sides.

## State, Persistence, And Dependencies
State is mostly process-local: namespace fds, destructor list, failure/skip flags, barrier counters, `nr_threads`, and thread-local endpoint addresses. It mutates system state by unsharing network namespaces, creating veth links through helpers from the TCP-AO library, and potentially writing `/proc/sys/net/core/optmem_max`. The optmem path handles both old global and newer per-namespace sysctl behavior and registers a destructor to restore the saved value.

## Integration Points
All TCP-AO C tests use this file through `aolib.h` and `test_init()` wrappers. It integrates kselftest, namespace helpers, ftrace setup, link/address/route helpers, and the socket helpers in `sock.c`.

## Risks
The barrier assumes every participating thread reaches every stage; early returns can deadlock. The optmem adjustment is explicitly not re-entrant and is unsafe for parallel tests that alter the same sysctl. Namespace switching errors abort the process. The temporary thread argument in `__test_init()` is stack-backed, but the code relies on the new thread copying it before the parent continues past the synchronization-heavy test setup.

## Test Signals
Useful signals are clean kselftest pass/skip/fail accounting, deterministic veth setup in two namespaces, successful barrier progress, and restoration of `optmem_max` when changed. Failures usually surface as `test_error()` exits, timeout deadlocks, or missing kernel config skips.

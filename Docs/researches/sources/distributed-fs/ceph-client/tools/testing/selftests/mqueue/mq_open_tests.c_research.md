<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mqueue/mq_open_tests.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mqueue/mq_open_tests.c

## Purpose
Correctness test for POSIX `mq_open()` behavior under different system defaults, maxima, resource limits, attributes, and effective user IDs.

## Important APIs, Types, and Functions
- Global sysctl paths cover `/proc/sys/fs/mqueue/msg_default`, `msgsize_default`, `msg_max`, and `msgsize_max`.
- `shutdown()` restores sysctls, closes/unlinks the queue, and exits.
- `get()`, `set()`, `getr()`, and `setr()` read/write sysctls and `RLIMIT_MSGQUEUE`.
- `validate_current_settings()` adjusts defaults/maxima if current limits are too low for testing.
- `test_queue()` creates a queue and treats failure as fatal.
- `test_queue_fail()` attempts queue creation where failure may be expected.

## Control Flow
`main()` normalizes the queue path, skips if not root, opens sysctl files, saves current sysctl and rlimit state, prints initial settings, validates/adjusts settings, then runs two broad series. Series 1 tests behavior when `mq_open()` is called without attributes, including default knobs and defaults greater than maxima/rlimit. Series 2 tests explicit attributes that exceed rlimit or maxima first as euid 0 and then after dropping to euid 99.

## State and Persistence Behavior
The program mutates mqueue sysctls and `RLIMIT_MSGQUEUE`, creates/unlinks a POSIX message queue, and temporarily changes effective uid. `shutdown()` restores saved sysctls and unlinks the queue on normal and error paths.

## Dependencies and Integration Points
Requires root, writable mqueue sysctls, POSIX mqueue support, `mq_open`, `mq_getattr`, `mq_unlink`, and kselftest skip support. Linked by the mqueue makefile with realtime/pthread/popt libraries, though this file mainly uses librt mqueue APIs.

## Risks and Edge Cases
The test prints PASS/FAIL text for subconditions but does not consistently increment kselftest counters. `shutdown()` must be reached to restore sysctls; abrupt termination may leave changed settings. Some kernels may not expose separate default sysctls, and the code handles both default-supported and legacy tied-to-max behavior.

## Test Signals
Root absence exits with kselftest skip. The test prints PASS/FAIL lines for each scenario and exits 0 through `shutdown(0, "", 0)` unless a fatal syscall/sysctl error occurs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mqueue/mq_open_tests.c -->

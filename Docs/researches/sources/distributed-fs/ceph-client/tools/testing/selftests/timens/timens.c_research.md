# sources/distributed-fs/ceph-client/tools/testing/selftests/timens/timens.c

## Purpose
Core time namespace gettime test. It verifies that namespace offsets affect supported clocks through both vDSO/libc and raw syscall paths while parent namespace time remains unchanged.

## Important APIs, Types, and Functions
Defines `struct test_clock` and `clocks[]` for boottime, boottime alarm, monotonic, monotonic coarse, and monotonic raw. Functions are `switch_ns`, `init_namespaces`, `test_gettime`, and `main`.

## Control Flow
`init_namespaces()` opens the parent `time_for_children` namespace, unshares a new time namespace, opens the child namespace, and verifies different inodes. `test_gettime()` switches to parent to capture a baseline, switches to child, reads the clock through vDSO/libc or raw syscall, and compares it to expected parent time plus offset. `main()` sets clock offsets and runs all clocks through both access paths.

## State and Persistence Behavior
State is held in namespace file descriptors and per-clock offsets written to `/proc/self/timens_offsets`. No external persistence is used.

## Dependencies and Integration Points
Depends on `setns`, `unshare(CLONE_NEWTIME)`, procfs time namespace files, POSIX clock APIs, raw `SYS_clock_gettime`, and kselftest output. Integrates with vDSO and syscall implementations of time namespace offsets.

## Risks and Edge Cases
Coarse/raw clocks share monotonic offsets, represented by `off_id`; mapping mistakes cause false failures. Precision tolerances differ for coarse/raw clocks. Requires root or equivalent namespace privileges.

## Test Signals
Signals are pass lines for each clock and access path, skip lines for unsupported alarm/POSIX timers, and failure if parent/child offsets are wrong.

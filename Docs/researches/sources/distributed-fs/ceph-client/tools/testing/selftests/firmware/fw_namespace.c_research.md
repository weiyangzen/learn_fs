<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_namespace.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_namespace.c

## Purpose
This helper tests that firmware requests use the mount namespace of PID 1 rather than the caller's private mount namespace.

## Important APIs, Types, And Functions
Important functions are `die()`, `trigger_fw()`, `setup_fw()`, `test_fw_in_ns()`, and `main()`. It manipulates `/lib/firmware`, a temporary `test-firmware.bin`, mount namespaces through `unshare(CLONE_NEWNS)`, and the sysfs trigger path supplied as argv[1].

## Control Flow
`main()` mounts tmpfs on `/lib/firmware`, writes firmware, then runs a positive case where the child hides firmware only in its own namespace and a negative case where the parent namespace blocks firmware while the child namespace exposes it. `test_fw_in_ns()` forks, adjusts mount propagation to slave in the child, mounts or unmounts tmpfs depending on the scenario, triggers firmware, and reports child exit status.

## State And Persistence
It temporarily mounts tmpfs over `/lib/firmware`, creates and unlinks a firmware file, and unmounts on exit/error. Failed cleanup can leave a test mount behind.

## Dependencies And Integration Points
It requires root, mount namespace support, writable mount operations on `/lib/firmware`, and the `test_firmware` sysfs trigger passed by `fw_run_tests.sh`.

## Risks
The test assumes the initial mount namespace is equivalent to PID 1 for firmware loading. `die()` unmounts `/lib/firmware` globally, so running on non-isolated systems is invasive. The negative case depends on firmware not being found through any other loader path.

## Test Signals
Pass signals are success when firmware exists in the parent/PID1 namespace and failure when firmware exists only in the child namespace, followed by clean unmount and unlink.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/firmware/fw_namespace.c -->

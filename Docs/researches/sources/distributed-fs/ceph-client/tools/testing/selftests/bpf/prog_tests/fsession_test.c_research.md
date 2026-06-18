
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fsession_test.c

## Purpose

`fsession_test.c` tests fentry/fexit session attachment behavior, including basic operation, detach/reattach, and session-cookie handling.

## Important APIs, Types, and Functions

The harness uses `fsession_test.skel.h`, skeleton `open/load/attach/detach/destroy`, and `bpf_prog_test_run_opts()` against `skel->progs.test1`. `check_result()` treats the BSS as an array of `__u64` result slots and requires every slot to be set to one.

## Control Flow and Data Flow

The basic subtest loads and attaches the skeleton, then runs `test1` to trigger function calls. The reattach subtest runs once, detaches, zeroes BSS, reattaches, and runs again. The cookie subtest disables `test6` autoload, compensates by setting its expected BSS fields, then verifies the remaining session-cookie paths.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is skeleton BSS result counters and link attachment state. Dependencies include kernel fprobe/session support; `-EOPNOTSUPP` causes skip. Integration is fentry/fexit session attachment, detachment, and cookie propagation. Risks are treating all BSS fields uniformly as `__u64` and feature availability on older kernels. Test signals are zero test-run error/retval and every expected result field equal to one across first attach, second attach, and cookie variant.

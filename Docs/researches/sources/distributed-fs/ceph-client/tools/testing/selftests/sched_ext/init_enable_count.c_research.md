<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/init_enable_count.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/init_enable_count.c

## Purpose

Userspace sched_ext selftest that counts init_task, exit_task, enable, disable, fork, and transition callback paths.

## Important APIs, Types, and Functions

Includes generated skeleton headers, libbpf bpf_map__attach_struct_ops/open/load/destroy APIs, scx_test.h registration/assertion helpers, and standard process/thread APIs as needed. Functions include run_test, run.

## Control Flow and Integration

host side runs global and partial-switch modes, forks many pre-existing and new children, changes some children to SCHED_EXT, and validates counter lower bounds/exact partial counts. The file registers a struct scx_test so runner.c can execute it serially.

## State and Persistence Behavior

State lives in the libbpf skeleton, bpf_link lifetime, child processes/threads, and counters read from BPF data/BSS maps. Cleanup destroys links/skeletons and joins or kills local workload where implemented.

## Dependencies and Integration Points

Depends on the matching .bpf.c skeleton, runner.c, scx_test.h, libbpf, sched_ext kernel support, and privileges to load BPF struct_ops schedulers.

## Risks and Edge Cases

Tests can be timing-sensitive and affect the host scheduler while attached. Expected-failure tests must not be treated as runner failures when the observed exit/load error matches the contract.

## Test Signals

Pass signal is SCX_TEST_PASS from run(), printed by runner as ok; failure macros emit file-specific diagnostics and return SCX_TEST_FAIL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/init_enable_count.c -->

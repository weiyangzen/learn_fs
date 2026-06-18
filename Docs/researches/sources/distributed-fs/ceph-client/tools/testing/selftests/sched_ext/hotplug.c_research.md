<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/hotplug.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/hotplug.c

## Purpose

Userspace sched_ext selftest that tests CPU hotplug callbacks and restart exit reasons.

## Important APIs, Types, and Functions

Includes generated skeleton headers, libbpf bpf_map__attach_struct_ops/open/load/destroy APIs, scx_test.h registration/assertion helpers, and standard process/thread APIs as needed. Functions include is_cpu_online, toggle_online_status, setup, test_hotplug, test_hotplug_attach, run, cleanup.

## Control Flow and Integration

host side toggles CPU online status, validates onlining/offlining exit flags when callbacks exist, validates attach behavior without callbacks, and restores CPU online state in cleanup. The file registers a struct scx_test so runner.c can execute it serially.

## State and Persistence Behavior

State lives in the libbpf skeleton, bpf_link lifetime, child processes/threads, and counters read from BPF data/BSS maps. Cleanup destroys links/skeletons and joins or kills local workload where implemented.

## Dependencies and Integration Points

Depends on the matching .bpf.c skeleton, runner.c, scx_test.h, libbpf, sched_ext kernel support, and privileges to load BPF struct_ops schedulers.

## Risks and Edge Cases

Tests can be timing-sensitive and affect the host scheduler while attached. Expected-failure tests must not be treated as runner failures when the observed exit/load error matches the contract.

## Test Signals

Pass signal is SCX_TEST_PASS from run(), printed by runner as ok; failure macros emit file-specific diagnostics and return SCX_TEST_FAIL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/hotplug.c -->

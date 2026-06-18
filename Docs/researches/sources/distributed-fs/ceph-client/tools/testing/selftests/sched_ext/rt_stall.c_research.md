<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/rt_stall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/rt_stall.c

## Purpose

Userspace sched_ext selftest that validates RT tasks cannot fully starve FAIR/SCHED_EXT tasks when the ext deadline server is available.

## Important APIs, Types, and Functions

Includes generated skeleton headers, libbpf bpf_map__attach_struct_ops/open/load/destroy APIs, scx_test.h registration/assertion helpers, and standard process/thread APIs as needed. Functions include signal_ready, wait_ready, process_func, set_affinity, set_sched, get_process_runtime, setup, sched_stress_test.

## Control Flow and Integration

host side checks ext_server field support, alternates runs with and without sched_ext attached, pins an EXT/FAIR busy task and an RT FIFO task to CPU0, measures /proc runtime for five seconds, and requires the non-RT task to receive at least 4 percent CPU. The file registers a struct scx_test so runner.c can execute it serially.

## State and Persistence Behavior

State lives in the libbpf skeleton, bpf_link lifetime, child processes/threads, and counters read from BPF data/BSS maps. Cleanup destroys links/skeletons and joins or kills local workload where implemented.

## Dependencies and Integration Points

Depends on the matching .bpf.c skeleton, runner.c, scx_test.h, libbpf, sched_ext kernel support, and privileges to load BPF struct_ops schedulers.

## Risks and Edge Cases

Tests can be timing-sensitive and affect the host scheduler while attached. Expected-failure tests must not be treated as runner failures when the observed exit/load error matches the contract.

## Test Signals

Pass signal is SCX_TEST_PASS from run(), printed by runner as ok; failure macros emit file-specific diagnostics and return SCX_TEST_FAIL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/rt_stall.c -->

# subset-b-006802 Research

This grouped report covers the requested BPF selftest `prog_tests` files. Each section is source-tree aligned and wrapped for reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/perf_buffer.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/perf_buffer.c

## Purpose
Validates libbpf perf-buffer delivery from a BPF program on every online CPU, including per-CPU buffer enumeration, epoll fd exposure, direct per-buffer consumption, and CPU/data identity checks. The source was read as a complete 148-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `on_sample()`, `trigger_on_cpu()`, `serial_test_perf_buffer()`.
- Includes and fixtures: `#include <pthread.h>`, `#include <sched.h>`, `#include <sys/socket.h>`, `#include <test_progs.h>`, `#include "test_perf_buffer.skel.h"`, `#include "bpf/libbpf_internal.h"`.
- Generated skeletons/objects referenced: `test_perf_buffer`.
- Primary APIs and types: `test_perf_buffer__open_and_load()`, `test_perf_buffer__attach()`, `bpf_map_update_elem()`, `perf_buffer__new()`, `perf_buffer__poll()`, `perf_buffer__buffer_cnt()`, `perf_buffer__buffer_fd()`, `perf_buffer__consume_buffer()`, `parse_cpu_mask_file()`, `pthread_setaffinity_np()`.

## Control Flow
`serial_test_perf_buffer()` reads the online CPU mask, loads the skeleton, stores the current PID in `my_pid_map`, attaches the probe, creates a perf buffer with `on_sample()`, triggers the probe once on each online CPU using `trigger_on_cpu()`, polls, then drains and re-triggers each per-CPU buffer to verify targeted consumption.

## State and Persistence Behavior
State is mostly transient: `cpu_seen` records callbacks, the BPF map stores one PID filter, perf-buffer mmap/fds are owned by libbpf, and thread CPU affinity is changed while triggering samples. Cleanup frees the perf buffer, skeleton, and parsed CPU mask.

## Dependencies and Integration Points
Depends on generated `test_perf_buffer.skel.h`, libbpf perf-buffer internals, `/sys/devices/system/cpu/online`, pthread affinity support, kprobe attachment in the skeleton, and selftests `CHECK`/`ASSERT` helpers.

## Risks and Edge Cases
CPU hotplug or affinity failures can make online CPU counts drift; ASAN needs the callback no-sanitize annotation for mmap data; skipped offline CPUs must remain aligned with `perf_buffer__buffer_cnt()` ordering; perf event permissions can block attachment.

## Test Signals
Assertions cover PID map update, epoll fd sanity, sample CPU equality, seen CPU count, per-buffer fd uniqueness, successful drain/consume, and callback re-delivery after each per-buffer trigger. Named assertion/check labels observed in the source include: `cpu_data %d != cpu %d\n`, `cpu #%d, err %d\n`, `err %d\n`, `skeleton open/load failed\n`, `my_pid_update`, `bad fd: %d\n`, `last fd %d == fd %d\n`, `cpu %d, err %d\n`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/perf_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/perf_event_stackmap.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/perf_event_stackmap.c

## Purpose
Checks stack map capture from a BPF program attached to a software perf event, using both user and kernel stack collection paths. The source was read as a complete 117-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_perf_event_stackmap()`.
- Includes and fixtures: `#include <pthread.h>`, `#include <sched.h>`, `#include <test_progs.h>`, `#include "perf_event_stackmap.skel.h"`.
- Generated skeletons/objects referenced: `bpf_program`, `perf_event_stackmap`.
- Primary APIs and types: `perf_event_open` through `bpf_program__attach_perf_event()`, `perf_event_stackmap__open_and_load()`, skeleton maps/programs, `pthread`/CPU helper paths, and selftests polling/wait macros.

## Control Flow
The test loads the `perf_event_stackmap` skeleton, creates a perf event, attaches the program, generates CPU activity, and inspects BPF-side counters/maps to confirm stack traces are collected and symbolized enough for the expected selftest conditions.

## State and Persistence Behavior
Persistent state is limited to perf-event fd/link lifetime and stack-map contents inside the loaded BPF object. Skeleton destruction closes links and maps.

## Dependencies and Integration Points
Depends on `perf_event_stackmap.skel.h`, perf event availability, stack-map verifier support, and kernel stack/user stack helper behavior.

## Risks and Edge Cases
Stack collection is sensitive to perf_event_paranoid, frame-pointer/unwind configuration, CPU scheduling, and unavailable PMU features; failures can be environmental rather than logic regressions.

## Test Signals
The key signal is successful perf-event attachment plus expected BPF map/counter updates after load and trigger activity. Named assertion/check labels observed in the source include: `skeleton open failed\n`, `skeleton load failed: %d\n`, `err %d, errno %d\n`, `attach_perf_event`, `failed\n`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/perf_event_stackmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/perf_link.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/perf_link.c

## Purpose
Validates BPF link metadata and detach semantics for perf-event-attached programs. The source was read as a complete 92-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `burn_cpu()`, `test_perf_link()`.
- Includes and fixtures: `#include <linux/compiler.h>`, `#include <test_progs.h>`, `#include "testing_helpers.h"`, `#include "test_perf_link.skel.h"`.
- Generated skeletons/objects referenced: `test_perf_link`.
- Primary APIs and types: `syscall(__NR_perf_event_open)`, `test_perf_link__open_and_load()`, `bpf_program__attach_perf_event()`, `bpf_link__fd()`, `bpf_link_get_info_by_fd()`, `bpf_link__destroy()`, and `burn_cpu()` workload generation.

## Control Flow
`test_perf_link()` opens a software perf event, loads the skeleton, attaches the program as a BPF link, queries link info for type/id/prog id, burns CPU until the program runs, destroys the link, then burns CPU again to confirm run count stops.

## State and Persistence Behavior
State includes the perf event fd, the BPF link fd, and skeleton BSS run counters. Once the link is destroyed, no persistent attachment should remain.

## Dependencies and Integration Points
Requires generated `test_perf_link.skel.h`, software perf events, link-info kernel support, and testing helper timeouts.

## Risks and Edge Cases
Timing-sensitive CPU burning can be flaky on constrained hosts; old kernels may lack link metadata fields; perf_event_open can fail due to policy.

## Test Signals
Assertions check perf fd, skeleton load, link fd/type/id/prog id, run-count timeout while attached, and unchanged run count after detach. Named assertion/check labels observed in the source include: `perf_fd`, `skel_load`, `link_fd`, `link_type`, `link_id`, `link_prog_id`, `run_cnt_timeout`, `run_cnt_before_after`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/perf_link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/perf_skip.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/perf_skip.c

## Purpose
Exercises perf event overflow skip behavior, signal delivery, and breakpoint interaction when a BPF perf-event program is attached. The source was read as a complete 138-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `handle_sigio()`, `handle_sigtrap()`, `serial_test_perf_skip()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include "test_perf_skip.skel.h"`, `#include <linux/compiler.h>`, `#include <linux/hw_breakpoint.h>`, `#include <sys/mman.h>`.
- Generated skeletons/objects referenced: `bpf_link`, `bpf_program`, `test_perf_skip`.
- Primary APIs and types: `sigaction()`, `fcntl(F_SETFL/F_SETOWN_EX)`, `ioctl(PERF_EVENT_IOC_REFRESH)`, `bpf_program__attach_perf_event()`, hardware breakpoint constants, `mmap()`, and generated `test_perf_skip` skeleton.

## Control Flow
The serial test installs SIGIO/SIGTRAP handlers, loads and attaches the BPF program to a perf event, arms async notification, refreshes the event, and verifies which signals are delivered as the perf event and breakpoint paths fire.

## State and Persistence Behavior
Global signal counters (`sigio_count`, `sigtrap_count`) are the observable state. The perf event fd, async owner, BPF link, and mapped breakpoint target are temporary and cleaned up before return.

## Dependencies and Integration Points
Depends on `test_perf_skip.skel.h`, Linux perf event and hardware breakpoint support, process-directed signals, and serial execution to avoid signal interference.

## Risks and Edge Cases
Signal timing and hardware breakpoint availability vary across architectures and virtualization; global handlers make concurrency unsafe, hence serial test naming.

## Test Signals
Assertions check signal codes, handler installation, async fcntl setup, perf refresh, attach success, and exact SIGIO/SIGTRAP count transitions. Named assertion/check labels observed in the source include: `si_code`, `sigaction`, `signal`, `skel_load`, `perf_event_open`, `fcntl(F_SETFL, O_ASYNC)`, `fcntl(F_SETOWN_EX)`, `ioctl(PERF_EVENT_IOC_REFRESH)`, `bpf_program__attach_perf_event`, `sigio_count`, `sigtrap_count`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/perf_skip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pinning.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pinning.c

## Purpose
Covers libbpf map pinning behavior: invalid pin metadata rejection, automatic pinning, reuse of pinned maps, custom pin roots, manual pin paths, parameter-mismatch rollback, and reuse-fd pinning. The source was read as a complete 281-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `get_map_id()`, `test_pinning()`.
- Includes and fixtures: `#include <sys/types.h>`, `#include <sys/stat.h>`, `#include <unistd.h>`, `#include <test_progs.h>`.
- Generated skeletons/objects referenced: `bpf_object`.
- Primary APIs and types: `bpf_object__open_file()`, `bpf_object__load()`, `bpf_object__pin_maps()`, `bpf_object__unpin_maps()`, `bpf_map__pin()`, `bpf_map__set_pin_path()`, `bpf_map__pin_path()`, `bpf_map__reuse_fd()`, `bpf_map_create()`, `bpf_map_get_info_by_fd()`, `stat()`, `unlink()`, `rmdir()`.

## Control Flow
`test_pinning()` first verifies invalid pinning definitions fail, then loads `test_pinning.bpf.o` and checks default auto-pinning. It reloads to verify the same pinned map id is reused, tests re-pin and different-location failures, manually assigns pin paths to non-pinned maps, verifies rollback on incompatible reuse, repeats with `pin_root_path`, then pins a reused manual map fd.

## State and Persistence Behavior
This test intentionally persists bpffs entries under `/sys/fs/bpf` during execution: `pinmap`, `nopinmap*`, and `/sys/fs/bpf/custom/pinmap`. It tracks map IDs across object close/reopen and removes all paths in `out:` cleanup.

## Dependencies and Integration Points
Depends on mounted bpffs, `test_pinning.bpf.o` and invalid fixture object, libbpf object/map APIs, and root/CAP_BPF-like permissions.

## Risks and Edge Cases
Failure cleanup can leave pinned maps that affect later runs; incompatible existing bpffs entries can cause false failures; custom root path needs directory creation/removal behavior from libbpf.

## Test Signals
Checks invalid `-EINVAL`, path existence/nonexistence, map-id reuse, no-op re-pin, different path rejection, path getter values, mismatch rollback, custom root pinning, and reuse-fd pinning. Named assertion/check labels observed in the source include: `NULL map`, `err %d errno %d`, `err %d errno %d\n`, `err %d errno %d id %d id2 %d\n`, `nopinmap`, `get pin path after set`, `fd %d\n`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pinning.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pinning_devmap_reuse.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pinning_devmap_reuse.c

## Purpose
Tests reuse of pinned devmap-style maps across skeleton instances and behavior when bpffs pins are swapped between loads. The source was read as a complete 51-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_pinning_devmap_reuse()`.
- Includes and fixtures: `#include <sys/types.h>`, `#include <sys/stat.h>`, `#include <unistd.h>`, `#include <test_progs.h>`, `#include "test_pinning_devmap.skel.h"`.
- Generated skeletons/objects referenced: `test_pinning_devmap`.
- Primary APIs and types: `test_pinning_devmap__open_and_load()`, skeleton map pin paths, map fd/pin operations, and bpffs rename/swap helpers in the test.

## Control Flow
The test loads two skeletons using devmap pinning, swaps pin paths to emulate reuse/change scenarios, then loads a third skeleton to verify libbpf handles existing pins correctly.

## State and Persistence Behavior
Persistent state is bpffs map pins for the devmap fixture. Skeleton objects own live fds; pins survive object destruction until explicit cleanup.

## Dependencies and Integration Points
Depends on generated `test_pinning_devmap.skel.h`, devmap support, bpffs, and stable pin names from the BPF object.

## Risks and Edge Cases
Stale pins or map attribute mismatches can invalidate reuse; devmap availability is kernel/config dependent.

## Test Signals
Assertions check first/second skeleton load, successful pin swap, and third skeleton load using the resulting pins. Named assertion/check labels observed in the source include: `skel_load1`, `skel_load2`, `swap pins`, `skel_load3`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pinning_devmap_reuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pinning_htab.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pinning_htab.c

## Purpose
Minimal hash-table pin/unpin smoke test through skeleton APIs. The source was read as a complete 37-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `unpin_map()`, `test_pinning_htab()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include "test_pinning_htab.skel.h"`.
- Generated skeletons/objects referenced: `test_pinning_htab`.
- Primary APIs and types: `test_pinning_htab__open_and_load()`, `bpf_object__find_map_by_name()`, `bpf_map__pin()`, `bpf_map__unpin()`.

## Control Flow
The test opens/loads the hash-table skeleton, finds the map by name, pins it, and unpins it through a helper.

## State and Persistence Behavior
Only the temporary bpffs pin for the hash map is persistent; it is removed by `bpf_map__unpin()`.

## Dependencies and Integration Points
Requires generated `test_pinning_htab.skel.h`, bpffs, and libbpf map pinning.

## Risks and Edge Cases
Existing pin path conflicts and missing bpffs permissions are the main environmental failures.

## Test Signals
Assertions cover skeleton load, map lookup, pin success, and unpin success. Named assertion/check labels observed in the source include: `skel open_and_load`, `bpf_object__find_map_by_name`, `bpf_map__pin`, `bpf_map__unpin`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pinning_htab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pkt_access.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pkt_access.c

## Purpose
Runs packet-access BPF programs with IPv4 and IPv6 packets to verify direct packet load/store bounds and return values. The source was read as a complete 33-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_pkt_access()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include <network_helpers.h>`.
- Generated skeletons/objects referenced: none in this C file; it uses raw object/helper loading or framework macros.
- Primary APIs and types: `bpf_prog_test_run_opts()`, `network_helpers` packet fixtures, `test__load_program()` style helpers, and selftests run option structs.

## Control Flow
`test_pkt_access()` loads the packet access object and runs it once with IPv4 and once with IPv6 input data, checking both test-run syscall success and returned verdict.

## State and Persistence Behavior
No persistent kernel state beyond the loaded program fd; packet buffers and run options are stack/local.

## Dependencies and Integration Points
Depends on `network_helpers.h`, BPF_PROG_TEST_RUN support for packet programs, and the compiled packet access BPF object.

## Risks and Edge Cases
Packet fixture size or expected return mismatches can hide verifier changes; run options must provide correct data pointers and sizes.

## Test Signals
Assertions check no test-run error and expected retval for IPv4 and IPv6. Named assertion/check labels observed in the source include: `ipv4 test_run_opts err`, `ipv4 test_run_opts retval`, `ipv6 test_run_opts err`, `ipv6 test_run_opts retval`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pkt_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pkt_md_access.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pkt_md_access.c

## Purpose
Verifies packet metadata access from a BPF test-run path. The source was read as a complete 26-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_pkt_md_access()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include <network_helpers.h>`.
- Generated skeletons/objects referenced: none in this C file; it uses raw object/helper loading or framework macros.
- Primary APIs and types: `bpf_prog_test_run_opts()`, `network_helpers`, and the packet metadata BPF object loaded by selftest helpers.

## Control Flow
The test loads the metadata-access program, runs it with a network packet fixture, and validates syscall result and program retval.

## State and Persistence Behavior
Only local packet buffers and run options are mutated; no bpffs or namespace state persists.

## Dependencies and Integration Points
Requires packet test-run support and metadata fields accepted by the kernel verifier for the program type.

## Risks and Edge Cases
Kernel changes to metadata availability or context layout can break the test; incorrect packet fixture lengths can cause false negatives.

## Test Signals
Assertions cover test-run syscall success and expected retval. Named assertion/check labels observed in the source include: `test_run_opts err`, `test_run_opts retval`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pkt_md_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/preempt_lock.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/preempt_lock.c

## Purpose
Loads and runs the preemption-lock BPF skeleton to validate helper/kfunc behavior that must execute under the expected preemption state. The source was read as a complete 10-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_preempt_lock()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include <network_helpers.h>`, `#include <preempt_lock.skel.h>`.
- Generated skeletons/objects referenced: none in this C file; it uses raw object/helper loading or framework macros.
- Primary APIs and types: `preempt_lock.skel.h` skeleton, `RUN_TESTS()` macro from selftests, and network/test helper includes.

## Control Flow
`test_preempt_lock()` delegates to the skeleton test macro, which opens, loads, attaches or test-runs all programs declared in the generated skeleton.

## State and Persistence Behavior
No explicit C-side state; BPF-side globals and map state live only for the skeleton test lifetime.

## Dependencies and Integration Points
Depends on `preempt_lock.skel.h`, generated skeleton metadata, and kernel support for the preempt-lock BPF feature under test.

## Risks and Edge Cases
Because the C harness is thin, failures need BPF-side log inspection; feature availability can be kernel-config dependent.

## Test Signals
The selftests `RUN_TESTS(preempt_lock)` wrapper reports load/run/attach failures for each skeleton program. Named assertion/check labels observed in the source include: framework macro results and source-specific checks rather than named assertion labels.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/preempt_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/preempted_bpf_ma_op.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/preempted_bpf_ma_op.c

## Purpose
Stress-tests BPF memory allocator operations while a BPF program is preempted, validating allocation failure and concurrency handling. The source was read as a complete 90-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_preempted_bpf_ma_op()`.
- Includes and fixtures: `#include <sched.h>`, `#include <pthread.h>`, `#include <stdbool.h>`, `#include <test_progs.h>`, `#include "preempted_bpf_ma_op.skel.h"`.
- Generated skeletons/objects referenced: `preempted_bpf_ma_op`.
- Primary APIs and types: `preempted_bpf_ma_op__open_and_load()`, `__attach()`, `bpf_prog_test_run_opts()`, `pthread_create()`, scheduler affinity/yield helpers, and BPF skeleton BSS flags.

## Control Flow
The test loads and attaches the skeleton, starts a worker thread to create preemption pressure, finds the test program, repeatedly runs it, and checks that allocator operations either succeed or fail with the expected `ENOMEM` condition.

## State and Persistence Behavior
Uses pthread-local execution plus shared skeleton BSS counters/flags. All state is process-local and destroyed with the skeleton/thread cleanup.

## Dependencies and Integration Points
Depends on `preempted_bpf_ma_op.skel.h`, pthreads, scheduler behavior, BPF allocator implementation, and test-run support.

## Risks and Edge Cases
Race/preemption tests are timing-sensitive; CPU count, scheduler policy, and memory pressure can change failure frequency.

## Test Signals
Assertions check open/load, attach, program lookup, pthread creation, program run status, and observed `ENOMEM` where expected. Named assertion/check labels observed in the source include: `open_and_load`, `attach`, `no test prog`, `pthread_create`, `run prog err`, `ENOMEM`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/preempted_bpf_ma_op.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/prepare.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/prepare.c

## Purpose
Validates libbpf object preparation before and after load, ensuring `bpf_object__prepare()` assigns expected internal map/program state without prematurely loading. The source was read as a complete 100-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `check_prepared()`, `test_prepare_no_load()`, `test_prepare_load()`, `test_prepare()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include <network_helpers.h>`, `#include "prepare.skel.h"`.
- Generated skeletons/objects referenced: `prepare`.
- Primary APIs and types: `prepare__open()`, `prepare__load()`, `bpf_object__prepare()`, `bpf_program__fd()`, `bpf_object` skeleton accessors, and `check_prepared()`.

## Control Flow
`test_prepare()` runs subtests for no-load and load paths. `check_prepared()` inspects object internals, while `test_prepare_no_load()` calls prepare before load and `test_prepare_load()` confirms preparation during/after load and program fd validity.

## State and Persistence Behavior
State is libbpf object-internal: prepared flags, allocated map/program descriptors, and loaded program fds. No bpffs state persists.

## Dependencies and Integration Points
Depends on generated `prepare.skel.h` and libbpf prepare semantics.

## Risks and Edge Cases
The test is coupled to libbpf object lifecycle details; changes in when fds are assigned or internal flags are set can require test updates.

## Test Signals
Assertions cover unprepared/prepared transitions, `bpf_object__prepare()` success, program fd availability after load, and test-run/load error status. Named assertion/check labels observed in the source include: `not check_prepared`, `bpf_object__prepare`, `check_prepared`, `prog_fd`, `err`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/prepare.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pro_epilogue.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pro_epilogue.c

## Purpose
Exercises BPF prologue/epilogue generation paths for struct_ops, tail calls, gotos to start, exits, and kfunc use. The source was read as a complete 63-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_tailcall()`, `test_pro_epilogue()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include "pro_epilogue.skel.h"`, `#include "epilogue_tailcall.skel.h"`, `#include "pro_epilogue_goto_start.skel.h"`, `#include "epilogue_exit.skel.h"`, `#include "pro_epilogue_with_kfunc.skel.h"`.
- Generated skeletons/objects referenced: `bpf_map`, `epilogue_exit`, `epilogue_tailcall`, `pro_epilogue`, `pro_epilogue_goto_start`, `pro_epilogue_with_kfunc`.
- Primary APIs and types: Skeletons `pro_epilogue`, `epilogue_tailcall`, `pro_epilogue_goto_start`, `epilogue_exit`, `pro_epilogue_with_kfunc`, `bpf_map_update_elem()`, `bpf_prog_test_run_opts()`, and struct_ops attach helpers.

## Control Flow
The tailcall subtest loads `epilogue_tailcall`, attaches struct_ops, updates a prog-array map, runs a program with test-run options, and checks argument/result mutations. Other subtests are selected through skeleton load/run macros for verifier/codegen coverage.

## State and Persistence Behavior
State includes prog-array entries, struct_ops links, and BPF-side argument/result globals. Cleanup is skeleton/link destruction.

## Dependencies and Integration Points
Requires generated skeletons, BPF struct_ops, tail-call map support, and kfunc availability for the relevant variant.

## Risks and Edge Cases
Feature-gated kernels may skip or fail kfunc/struct_ops pieces; tail-call map setup must match program fds exactly.

## Test Signals
Assertions check skeleton load, struct_ops attach, prog test run, argument value, and returned retval. Named assertion/check labels observed in the source include: `epilogue_tailcall__open_and_load`, `attach_struct_ops`, `bpf_prog_test_run_opts`, `args.a`, `topts.retval`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pro_epilogue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/probe_read_user_str.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/probe_read_user_str.c

## Purpose
Tests `bpf_probe_read_user_str()` behavior across user strings and expected copy lengths/results. The source was read as a complete 72-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_one_str()`, `test_probe_read_user_str()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include "test_probe_read_user_str.skel.h"`.
- Generated skeletons/objects referenced: `test_probe_read_user_str`.
- Primary APIs and types: `test_probe_read_user_str__open_and_load()`, skeleton BSS/rodata fields, attach helpers, and user string buffers passed to BPF.

## Control Flow
`test_one_str()` configures a source string case, triggers the BPF program, and compares copied data/length/error status. `test_probe_read_user_str()` iterates representative strings and edge cases.

## State and Persistence Behavior
User-space buffers and skeleton BSS fields hold the source pointer, destination bytes, and observed return values. No persistent state remains after skeleton destruction.

## Dependencies and Integration Points
Depends on generated `test_probe_read_user_str.skel.h`, probe-read helper support, and a trigger point provided by the skeleton.

## Risks and Edge Cases
String termination and maximum-length boundaries are subtle; invalid user pointers must fail without crashing the process.

## Test Signals
Test signals are copied bytes, returned length/error values, and BSS flags for each string case. Named assertion/check labels observed in the source include: `prog returned: %ld\n`, `prog copied wrong string`, `trailing bytes were not stripped`, `skeleton open and load failed\n`, `skeleton attach failed: %d\n`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/probe_read_user_str.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/probe_user.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/probe_user.c

## Purpose
Validates user-memory probing from BPF, including BSS initialization and kprobe attachment against user pointers. The source was read as a complete 111-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_probe_user()`.
- Includes and fixtures: `#include <test_progs.h>`.
- Generated skeletons/objects referenced: `bpf_link`, `bpf_object`, `bpf_program`.
- Primary APIs and types: `bpf_object__open_file()`, `bpf_object__find_map_by_name()`, BSS mmap/update logic, `bpf_program__attach_kprobe()`, `bpf_link`, and raw libbpf object/program APIs.

## Control Flow
The test opens the BPF object, locates/initializes BSS data, loads programs, attaches a kprobe, triggers user-memory reads, and checks BPF-observed values in BSS.

## State and Persistence Behavior
The BSS map is mutable shared state between user space and BPF. Link/object lifetime controls the attachment; no bpffs persistence is used.

## Dependencies and Integration Points
Depends on compiled BPF object, kprobe availability, libbpf BSS support, and selftest permissions.

## Risks and Edge Cases
Probe targets and user-memory access rules vary by architecture and kernel hardening; BSS layout mismatches can cause misleading failures.

## Test Signals
Assertions check object open, BSS size/initialization, kprobe attach, and expected BPF-written BSS values. Named assertion/check labels observed in the source include: `obj_open_file`, `prog '%s' not found\n`, `bss_size`, `set_bss_init`, `err %d\n`, `attach_kprobe`, `failed to get kprobe res: %d\n`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/probe_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/prog_array_init.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/prog_array_init.c

## Purpose
Tests initialization of `BPF_MAP_TYPE_PROG_ARRAY` entries from an object file and tail-call execution through pre-populated program slots. The source was read as a complete 33-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_prog_array_init()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include "test_prog_array_init.skel.h"`.
- Generated skeletons/objects referenced: `bpf_program`, `test_prog_array_init`.
- Primary APIs and types: `test_prog_array_init__open()`, `bpf_program__attach_tracepoint()`, skeleton maps/programs, and BSS/result inspection.

## Control Flow
The test opens the skeleton, attaches a sys_enter program, triggers the tracepoint, and checks that a tail call through the initialized prog array updates the expected value.

## State and Persistence Behavior
State is in the prog-array map and BPF-side global value. Attach link lifetime is temporary.

## Dependencies and Integration Points
Depends on `test_prog_array_init.skel.h`, tracepoint availability, and libbpf support for program-array initial values.

## Risks and Edge Cases
Program order and map initialization metadata must match the BPF object; tracepoint trigger reliability matters.

## Test Signals
Assertions check object open, sys_enter program lookup/attach, and expected value after trigger. Named assertion/check labels observed in the source include: `could not open BPF object`, `sys_enter`, `could not attach BPF program`, `unexpected value`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/prog_array_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/prog_run_opts.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/prog_run_opts.c

## Purpose
Covers `bpf_prog_test_run_opts()` option handling, output sizing, retval reporting, ignored size hints, and no-output operation. The source was read as a complete 78-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `check_run_cnt()`, `test_prog_run_opts()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include <network_helpers.h>`, `#include "test_pkt_access.skel.h"`.
- Generated skeletons/objects referenced: `test_pkt_access`.
- Primary APIs and types: `bpf_prog_test_run_opts()`, `bpf_enable_stats()`, `test_pkt_access__open_and_load()`, `LIBBPF_OPTS`, packet fixture buffers, and `check_run_cnt()`.

## Control Flow
The test enables stats, loads the packet-access skeleton, runs with normal options, deliberately overflows output sizing, tests ignored hints, and runs with no output buffer while validating run counters and return codes.

## State and Persistence Behavior
State is program run statistics, packet input/output buffers, and mutable `bpf_test_run_opts` fields such as `data_size_out` and `retval`.

## Dependencies and Integration Points
Depends on `test_pkt_access.skel.h`, packet test-run support, stats enabling support, and network helper packet data.

## Risks and Edge Cases
Option structure ABI changes can affect behavior; output buffer sizing must be exact to distinguish kernel regression from test bug.

## Test Signals
Assertions cover stats enablement, load success, test-run errno/result/retval/data_size_out, overflow handling, ignored size hint, and no-output retval. Named assertion/check labels observed in the source include: `failed to get bpf_prog_info for fd %d\n`, `incorrect number of repetitions, want %llu have %llu\n`, `enable_stats good fd`, `open_and_load`, `test_run errno`, `test_run`, `test_run retval`, `test_run data_size_out`, `overflow, BPF_PROG_TEST_RUN ignored size hint`, `run_no_output errno`, `run_no_output err`, `run_no_output retval`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/prog_run_opts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/prog_tests_framework.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/prog_tests_framework.c

## Purpose
Self-tests the `test_progs` framework itself: subtest counting, output capture, failure emission, and dummy test registration behavior. The source was read as a complete 182-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `clear_test_state()`, `test_prog_tests_framework()`, `dummy_emit()`.
- Includes and fixtures: `#include "test_progs.h"`, `#include "testing_helpers.h"`.
- Generated skeletons/objects referenced: none in this C file; it uses raw object/helper loading or framework macros.
- Primary APIs and types: `test__start_subtest()`, framework state globals, `open_memstream()`/capture helpers, `ASSERT_*` macros, and `dummy_emit()`.

## Control Flow
The test clears framework state, starts nested/numbered subtests, emits dummy pass/fail output, and compares captured output to expected framework formatting.

## State and Persistence Behavior
Mutates global test framework state, stdout/stderr capture buffers, and subtest counters. `clear_test_state()` resets these between checks.

## Dependencies and Integration Points
Depends on `test_progs.h` and `testing_helpers.h`; no BPF object is loaded.

## Risks and Edge Cases
Very sensitive to formatting changes in the framework; tests can fail due to expected text drift rather than kernel behavior.

## Test Signals
Assertions check subtest number accounting and captured expected output strings. Named assertion/check labels observed in the source include: `subtest_num_check`, `expected output`, `, `.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/prog_tests_framework.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ptr_untrusted.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ptr_untrusted.c

## Purpose
Verifies verifier and attach behavior for programs that handle untrusted pointers across LSM and raw tracepoint contexts. The source was read as a complete 37-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `serial_test_ptr_untrusted()`.
- Includes and fixtures: `#include <string.h>`, `#include <linux/bpf.h>`, `#include <test_progs.h>`, `#include "test_ptr_untrusted.skel.h"`.
- Generated skeletons/objects referenced: `bpf_program`, `test_ptr_untrusted`.
- Primary APIs and types: `test_ptr_untrusted__open()`, `bpf_program__attach_lsm()`, `bpf_program__attach_raw_tracepoint()`, program name comparison, and skeleton load.

## Control Flow
The serial test opens/loads the skeleton, attaches the LSM program, attaches a raw tracepoint program, and compares tracepoint naming/metadata expected by the test.

## State and Persistence Behavior
Only link lifetimes are persistent during the test. No maps or bpffs entries persist.

## Dependencies and Integration Points
Depends on `test_ptr_untrusted.skel.h`, LSM BPF support, raw tracepoint support, and serial execution for attach side effects.

## Risks and Edge Cases
Kernels without BPF LSM enabled will skip/fail; raw tracepoint names must match kernel tracepoint availability.

## Test Signals
Assertions check skeleton open, LSM attach, raw tracepoint attach, and tracepoint name comparison. Named assertion/check labels observed in the source include: `skel_open`, `lsm_attach`, `raw_tp_attach`, `cmp_tp_name`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ptr_untrusted.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/queue_stack_map.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/queue_stack_map.c

## Purpose
Exercises queue and stack map semantics through BPF program test runs and direct map syscalls. The source was read as a complete 109-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_queue_stack_map_by_type()`, `test_queue_stack_map()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include <network_helpers.h>`.
- Generated skeletons/objects referenced: none in this C file; it uses raw object/helper loading or framework macros.
- Primary APIs and types: `bpf_map_pop_elem()`, `bpf_map_lookup_and_delete_elem()`, `bpf_map_push_elem()`, `bpf_prog_test_run_opts()`, and network packet helpers.

## Control Flow
`test_queue_stack_map_by_type()` loads a program for either queue or stack map type, pushes/reads values, runs BPF to pop or observe map contents, verifies empty-map behavior, and repeats for both map classes via `test_queue_stack_map()`.

## State and Persistence Behavior
Map contents are the key mutable state. Packet output fields and `data_size_out` verify what the BPF program popped. State is discarded when fds close.

## Dependencies and Integration Points
Depends on queue/stack map kernel support, network helper fixtures, and BPF_PROG_TEST_RUN.

## Risks and Edge Cases
Queue FIFO vs stack LIFO expectations must be kept distinct; empty map error handling is part of the contract.

## Test Signals
Assertions check pop return values, test-run retval/data_size_out, packet destination address, empty-map handling, lookup-delete behavior, and push success. Named assertion/check labels observed in the source include: `bpf_map_pop_elem`, `bpf_map_pop_elem test retval`, `bpf_map_pop_elem data_size_out`, `bpf_map_pop_elem iph.daddr`, `check-queue-stack-map-empty`, `check-queue-stack-map-empty test retval`, `check-queue-stack-map-empty data_size_out`, `bpf_map_lookup_and_delete_elem`, `bpf_map_push_elem val`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/queue_stack_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/raw_tp_null.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/raw_tp_null.c

## Purpose
Checks raw tracepoint programs with nullable/null context handling and rejects invalid variants through a fail skeleton. The source was read as a complete 29-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_raw_tp_null()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include "raw_tp_null.skel.h"`, `#include "raw_tp_null_fail.skel.h"`.
- Generated skeletons/objects referenced: `raw_tp_null`, `raw_tp_null_fail`.
- Primary APIs and types: `raw_tp_null__open_and_load()`, `raw_tp_null_fail` skeleton load expectation, `trigger_module_test_read()`, and skeleton BSS invocation counters.

## Control Flow
The test loads the accepted skeleton, expects the fail skeleton to be rejected, triggers the test module read path, and checks invocation count from the raw tracepoint program.

## State and Persistence Behavior
BPF-side invocation counter is the observable state; module trigger and skeleton links are temporary.

## Dependencies and Integration Points
Depends on `raw_tp_null.skel.h`, `raw_tp_null_fail.skel.h`, selftests test module trigger, and raw tracepoint support.

## Risks and Edge Cases
Requires the bpf test module path used by `trigger_module_test_read`; fail-log expectations may change with verifier diagnostics.

## Test Signals
Assertions check successful load, trigger success, and expected invocation count. Named assertion/check labels observed in the source include: `raw_tp_null__open_and_load`, `trigger testmod read`, `invocations`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/raw_tp_null.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/raw_tp_test_run.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/raw_tp_test_run.c

## Purpose
Validates `BPF_PROG_TEST_RUN` for raw tracepoint programs, including context sizing, on-CPU selection, retval, and invalid option handling. The source was read as a complete 87-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_raw_tp_test_run()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include <linux/bpf.h>`, `#include "bpf/libbpf_internal.h"`, `#include "test_raw_tp_test_run.skel.h"`.
- Generated skeletons/objects referenced: `test_raw_tp_test_run`.
- Primary APIs and types: `test_raw_tp_test_run__open()`, `bpf_prog_test_run_opts()`, `parse_cpu_mask_file()`, `/proc/self/comm` writes, and libbpf internal helpers.

## Control Flow
The test reads the CPU mask, opens the skeleton, renames the task via `/proc/self/comm`, checks live tracepoint count/on-CPU behavior, then uses test-run options with valid and invalid contexts/CPU selectors to confirm retval and errors.

## State and Persistence Behavior
State includes task comm, skeleton BSS counters (`count`, on-CPU fields), raw tracepoint context arrays, and parsed online CPU mask. Task comm is restored by process lifetime/name rewrite behavior.

## Dependencies and Integration Points
Depends on `test_raw_tp_test_run.skel.h`, writable `/proc/self/comm`, raw tracepoint test-run kernel support, and CPU mask parsing.

## Risks and Edge Cases
CPU online changes and task naming permissions can introduce environmental failures; invalid CPU tests depend on exact errno contracts (`ENXIO`, `EINVAL`).

## Test Signals
Assertions cover CPU mask parsing, skeleton open, comm open/write, count/on-CPU checks, small-context failure, normal retval, and invalid option errno paths. Named assertion/check labels observed in the source include: `parse_cpu_mask_file`, `skel_open`, `/proc/self/comm`, `open /proc/self/comm`, `task rename`, `check_count`, `check_on_cpu`, `test_run should fail for too small ctx`, `test_run`, `check_retval`, `test_run_opts`, `test_run_opts should fail with ENXIO`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/raw_tp_test_run.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/raw_tp_writable_reject_nbd_invalid.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/raw_tp_writable_reject_nbd_invalid.c

## Purpose
Verifies that invalid writable raw tracepoint programs for NBD tracepoints are rejected by the verifier. The source was read as a complete 44-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_raw_tp_writable_reject_nbd_invalid()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include <linux/nbd.h>`, `#include "bpf_util.h"`.
- Generated skeletons/objects referenced: none in this C file; it uses raw object/helper loading or framework macros.
- Primary APIs and types: `bpf_prog_load()`/raw instruction loading via `bpf_util.h`, `linux/nbd.h` tracepoint context definitions, and selftest load-failure checks.

## Control Flow
The test builds or loads an intentionally invalid writable raw tracepoint program targeting NBD context and expects program load to fail.

## State and Persistence Behavior
No persistent state; failed load leaves no program/link. Any generated log is local.

## Dependencies and Integration Points
Depends on NBD tracepoint type definitions, writable raw tracepoint verifier paths, and `bpf_util.h` helpers.

## Risks and Edge Cases
Tracepoint context changes or missing NBD config can alter expected rejection; verifier message text may vary.

## Test Signals
Test passes when the invalid writable raw tracepoint load is rejected with the expected failure mode. Named assertion/check labels observed in the source include: `failed: %d errno %d\n`, `erroneously succeeded\n`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/raw_tp_writable_reject_nbd_invalid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/raw_tp_writable_test_run.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/raw_tp_writable_test_run.c

## Purpose
Tests writable raw tracepoint program execution through test-run APIs using an NBD request-like context. The source was read as a complete 84-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `serial_test_raw_tp_writable_test_run()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include <linux/nbd.h>`, `#include "bpf_util.h"`.
- Generated skeletons/objects referenced: none in this C file; it uses raw object/helper loading or framework macros.
- Primary APIs and types: `bpf_prog_load()` helpers from `bpf_util.h`, `bpf_prog_test_run_opts()`, `linux/nbd.h` structures, and raw tracepoint writable program type/attach type.

## Control Flow
The serial test loads a writable raw tracepoint program, prepares an NBD-style context, runs it via test-run, and verifies that permitted writable fields are modified while invalid fields remain protected.

## State and Persistence Behavior
State is entirely local: context buffer before/after, run options, and program fd. No link or bpffs state persists.

## Dependencies and Integration Points
Depends on writable raw tracepoint test-run support and NBD tracepoint layout headers.

## Risks and Edge Cases
Tightly coupled to NBD tracepoint ABI and verifier writable-field policy; kernel config can remove the relevant tracepoint types.

## Test Signals
Signals are successful load/test-run and expected context mutation or rejection results. Named assertion/check labels observed in the source include: `failed: %d errno %d\n`, `tracepoint did not modify return value\n`, `socket_filter did not return 0\n`, `test_run failed with %d errno %d\n`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/raw_tp_writable_test_run.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/rbtree.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/rbtree.c

## Purpose
Covers BPF rbtree kfunc API behavior, including add/remove/first/search, nested nodes, array-contained nodes, API aliasing, expected verifier failures, and BTF type mismatch failures. The source was read as a complete 202-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_rbtree_add_nodes()`, `test_rbtree_add_nodes_nested()`, `test_rbtree_add_and_remove()`, `test_rbtree_add_and_remove_array()`, `test_rbtree_first_and_remove()`, `test_rbtree_api_release_aliasing()`, `test_rbtree_success()`, `test_rbtree_btf_fail()`, `test_rbtree_fail()`, `test_rbtree_search()`, `test_rbtree_search_kptr()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include <network_helpers.h>`, `#include "rbtree.skel.h"`, `#include "rbtree_fail.skel.h"`, `#include "rbtree_btf_fail__wrong_node_type.skel.h"`, `#include "rbtree_btf_fail__add_wrong_type.skel.h"`, `#include "rbtree_search.skel.h"`, `#include "rbtree_search_kptr.skel.h"`.
- Generated skeletons/objects referenced: `rbtree`, `rbtree_btf_fail__add_wrong_type`, `rbtree_btf_fail__wrong_node_type`, `rbtree_fail`, `rbtree_search`, `rbtree_search_kptr`.
- Primary APIs and types: Skeletons `rbtree`, `rbtree_fail`, BTF fail skeletons, `rbtree_search`, `rbtree_search_kptr`, `bpf_prog_test_run_opts()`, and BPF-side rbtree kfuncs exercised by programs.

## Control Flow
Success helpers open/load the `rbtree` skeleton and run individual programs, checking return values and BSS result fields. Failure helpers attempt to load invalid skeletons. Search helpers validate lookup behavior for normal and kptr-backed nodes.

## State and Persistence Behavior
BPF maps/globals hold tree roots, removed keys, callback flags, and search results during each skeleton lifetime. No user-space persistence remains.

## Dependencies and Integration Points
Depends on generated skeletons, BPF rbtree kfunc support, BTF type checking, and network helper test-run scaffolding.

## Risks and Edge Cases
Verifier rules for ownership/release/aliasing are precise and can change; BTF fail tests are coupled to diagnostic/load-rejection semantics.

## Test Signals
Assertions cover program run success/retval, less-callback execution, first/removed key values, fail skeleton rejection, and search/kptr outcomes. Named assertion/check labels observed in the source include: `rbtree__open_and_load`, `rbtree_add_nodes run`, `rbtree_add_nodes retval`, `rbtree_add_nodes less_callback_ran`, `rbtree_add_nodes_nested run`, `rbtree_add_nodes_nested retval`, `rbtree_add_nodes_nested less_callback_ran`, `rbtree_add_and_remove`, `rbtree_add_and_remove retval`, `rbtree_add_and_remove first removed key`, `rbtree_add_and_remove_array`, `rbtree_add_and_remove_array retval`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/rbtree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/rcu_read_lock.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/rcu_read_lock.c

## Purpose
Validates BPF-side `bpf_rcu_read_lock()`/unlock regions, RCU pointer acquisition, misuse rejection, and integration with cgroup/task storage. The source was read as a complete 160-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_success()`, `test_rcuptr_acquire()`, `test_inproper_region()`, `test_rcuptr_misuse()`, `test_rcu_read_lock()`.
- Includes and fixtures: `#include <unistd.h>`, `#include <sys/syscall.h>`, `#include <sys/types.h>`, `#include <test_progs.h>`, `#include <bpf/btf.h>`, `#include "rcu_read_lock.skel.h"`, `#include "cgroup_helpers.h"`.
- Generated skeletons/objects referenced: `rcu_read_lock`.
- Primary APIs and types: `rcu_read_lock__open/load/attach()`, `bpf_object__find_program_by_name()`, `bpf_program__set_autoload()`, cgroup helper setup, BTF APIs, and skeleton BSS checks.

## Control Flow
Success subtests load and attach valid programs, trigger storage/cgroup paths, and verify BPF-observed values. Misuse subtests selectively autoload invalid programs and expect load failure. The top-level test prepares cgroup context and runs each subtest.

## State and Persistence Behavior
State includes cgroup hierarchy entries, task storage values, skeleton BSS fields, and program autoload flags. Cgroup cleanup is required to remove created directories.

## Dependencies and Integration Points
Depends on `rcu_read_lock.skel.h`, cgroup helpers, BTF, BPF task/cgroup storage, and RCU kfunc verifier support.

## Risks and Edge Cases
Cgroup setup permissions and kernel feature gates can cause skips/failures; typo-named `test_inproper_region` still represents invalid region checks.

## Test Signals
Assertions check skeleton open/load/attach, task storage value, cgroup id, selected invalid program load failures, and cgroup path setup. Named assertion/check labels observed in the source include: `skel_open`, `skel_load`, `skel_attach`, `task_storage_val`, `cgroup_id`, `bpf_object__find_program_by_name`, `/rcu_read_lock`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/rcu_read_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/rdonly_maps.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/rdonly_maps.c

## Purpose
Tests read-only map sections and mmap/BSS-style global data immutability from user and BPF perspectives. The source was read as a complete 90-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_rdonly_maps()`.
- Includes and fixtures: `#include <test_progs.h>`.
- Generated skeletons/objects referenced: `bpf_link`, `bpf_object`, `bpf_program`.
- Primary APIs and types: `bpf_object__open_file()`, map/program lookup, skeleton-less libbpf APIs, `bpf_program__attach_*`, and BPF link cleanup.

## Control Flow
The test opens the object, locates read-only map content, loads/attaches the program, triggers it, and checks that read-only data is visible but not unexpectedly mutated.

## State and Persistence Behavior
Read-only maps hold constants/global data for the object lifetime. Attach link and object close release all fds.

## Dependencies and Integration Points
Depends on the compiled read-only maps BPF object, libbpf global data handling, and the trigger hook used by the program.

## Risks and Edge Cases
Global data section layout and mmap permissions are ABI-sensitive; mutable-vs-read-only expectations may change with libbpf loader behavior.

## Test Signals
Assertions cover object open, program attach, and observed map/global values after trigger. Named assertion/check labels observed in the source include: `obj_open`, `err %d errno %d\n`, `failed\n`, `prog '%s' not found\n`, `failed to set bss data: %d\n`, `attach_prog`, `failed to get bss data: %d\n`, `prog '%s' didn't run?\n`, `prog '%s' iters: %d, expected: %d\n`, `prog '%s' sum: %d, expected: %d\n`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/rdonly_maps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/read_vsyscall.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/read_vsyscall.c

## Purpose
Verifies BPF probe-read behavior against the fixed vsyscall address range on x86-like systems. The source was read as a complete 60-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_read_vsyscall()`.
- Includes and fixtures: `#include "test_progs.h"`, `#include "read_vsyscall.skel.h"`, `#include <asm/vsyscall.h>`.
- Generated skeletons/objects referenced: `read_vsyscall`.
- Primary APIs and types: `read_vsyscall__open_and_load()`, `read_vsyscall__attach()`, `<asm/vsyscall.h>` constants, and skeleton BSS result fields.

## Control Flow
The test loads and attaches the skeleton, triggers the attached program, and checks whether reading vsyscall memory succeeds/fails according to kernel policy encoded in the BPF program.

## State and Persistence Behavior
Only BPF-side result fields are mutated; skeleton/link destruction cleans all state.

## Dependencies and Integration Points
Depends on generated `read_vsyscall.skel.h`, architecture header availability, vsyscall mapping behavior, and probe-read helper support.

## Risks and Edge Cases
Architecture-specific; kernels with different vsyscall emulation/mapping policy can skip or fail. The include ties the test to platforms exposing `<asm/vsyscall.h>`.

## Test Signals
Assertions check skeleton open/load and attach; BPF-side checks determine pass/fail for read behavior. Named assertion/check labels observed in the source include: `read_vsyscall open_load`, `read_vsyscall attach`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/read_vsyscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/recursion.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/recursion.c

## Purpose
Tests recursion prevention/accounting for BPF programs that can trigger nested execution paths. The source was read as a complete 42-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_recursion()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include "recursion.skel.h"`.
- Generated skeletons/objects referenced: `recursion`.
- Primary APIs and types: `recursion__open_and_load()`, skeleton attach/trigger helpers, BSS counters `pass1`, `pass2`, and `recursion_misses`.

## Control Flow
The test loads the skeleton, triggers recursive paths multiple times, and checks pass counters progress through expected values while recursion misses are accounted for.

## State and Persistence Behavior
BPF BSS counters persist for the skeleton lifetime and are inspected after each trigger. No external state persists.

## Dependencies and Integration Points
Depends on `recursion.skel.h`, the hook used to trigger recursive execution, and kernel recursion guard behavior.

## Risks and Edge Cases
Counters are sensitive to extra trigger events from the environment; recursion guard semantics can change with kernel internals.

## Test Signals
Assertions verify skeleton load, pass1/pass2 counter sequence, and recursion miss count. Named assertion/check labels observed in the source include: `skel_open_and_load`, `pass1 == 0`, `pass1 == 1`, `pass1 == 2`, `pass2 == 0`, `pass2 == 1`, `pass2 == 2`, `recursion_misses`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/recursion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/recursive_attach.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/recursive_attach.c

## Purpose
Covers fentry recursive attachment, attach-target setting, BTF-id presence, chain behavior, and stress attaching from multiple threads. The source was read as a complete 219-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_recursive_fentry_chain()`, `test_recursive_fentry()`, `test_fentry_attach_btf_presence()`, `test_fentry_attach_stress()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include "fentry_recursive.skel.h"`, `#include "fentry_recursive_target.skel.h"`, `#include <bpf/btf.h>`, `#include "bpf/libbpf_internal.h"`.
- Generated skeletons/objects referenced: `fentry_recursive`, `fentry_recursive_target`.
- Primary APIs and types: `fentry_recursive_target__open_and_load()`, `fentry_recursive__open/load/attach()`, `bpf_program__set_attach_target()`, `bpf_link__fd()`, `bpf_prog_test_run_opts()`, BTF APIs, and pthread joins.

## Control Flow
Chain tests load target and recursive fentry skeletons, set attach targets, attach links, and run target programs. BTF-presence tests validate attach target metadata. Stress tests create threads that attach repeatedly and join them.

## State and Persistence Behavior
State includes target program fds, fentry links, BSS counters, and thread-local attach attempts. All links/skeletons are destroyed at cleanup.

## Dependencies and Integration Points
Depends on generated fentry skeletons, BTF availability, fentry attach support, and pthreads.

## Risks and Edge Cases
Recursive attach and stress cases are timing-sensitive; BTF id lookup behavior can differ across kernels; improper cleanup can leave links until process exit.

## Test Signals
Assertions check target load, attach-target setting, load/attach success/failure, link fd, target test-run, and pthread joins. Named assertion/check labels observed in the source include: `fentry_recursive_target__open_and_load`, `fentry_recursive__open`, `bpf_program__set_attach_target`, `fentry_recursive__load`, `fentry_recursive__attach`, `link_fd`, `fentry_target test_run`, `fentry_target`, `pthread_join`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/recursive_attach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/refcounted_kptr.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/refcounted_kptr.c

## Purpose
Tests refcounted kptr ownership rules, wrong-owner rbtree removal failures, per-CPU hash refcount leak prevention, and expected verifier rejection cases. The source was read as a complete 103-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_refcounted_kptr()`, `test_refcounted_kptr_fail()`, `test_refcounted_kptr_wrong_owner()`, `test_percpu_hash_refcounted_kptr_refcount_leak()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include <network_helpers.h>`, `#include "refcounted_kptr.skel.h"`, `#include "refcounted_kptr_fail.skel.h"`.
- Generated skeletons/objects referenced: `refcounted_kptr`, `refcounted_kptr_fail`.
- Primary APIs and types: `refcounted_kptr__open_and_load()`, `refcounted_kptr_fail` skeleton, `bpf_prog_test_run_opts()`, `bpf_map__update_elem()`, `libbpf_num_possible_cpus()`, and per-CPU value allocation.

## Control Flow
Success tests run programs that manipulate refcounted kptrs and validate return values. Failure tests load invalid variants. The per-CPU hash test allocates per-CPU values, updates the map, runs programs, and confirms no leaked refcount remains.

## State and Persistence Behavior
State lives in BPF maps containing kptrs/rbtree nodes and per-CPU values. User allocates a per-CPU value array and frees it after map updates/runs.

## Dependencies and Integration Points
Depends on generated `refcounted_kptr*.skel.h`, refcounted kptr verifier/kfunc support, rbtree support, and CPU-count helper.

## Risks and Edge Cases
Ownership rules are verifier-sensitive; per-CPU allocation must match possible CPU count exactly; failure tests can break on verifier diagnostic-policy changes.

## Test Signals
Assertions cover skeleton loads/rejections, program run retval, per-CPU allocation/update, and expected failure for wrong-owner remove paths. Named assertion/check labels observed in the source include: `refcounted_kptr__open_and_load`, `rbtree_wrong_owner_remove_fail_a1`, `rbtree_wrong_owner_remove_fail_a1 retval`, `rbtree_wrong_owner_remove_fail_b`, `rbtree_wrong_owner_remove_fail_b retval`, `rbtree_wrong_owner_remove_fail_a2`, `rbtree_wrong_owner_remove_fail_a2 retval`, `libbpf_num_possible_cpus`, `calloc values`, `bpf_map__update_elem`, `opts.retval`, `bpf_prog_test_run_opts`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/refcounted_kptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/reference_tracking.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/reference_tracking.c

## Purpose
Runs verifier reference-tracking tests from object files and validates object naming/open behavior. The source was read as a complete 64-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_reference_tracking()`.
- Includes and fixtures: `#include <test_progs.h>`.
- Generated skeletons/objects referenced: `bpf_object`.
- Primary APIs and types: `bpf_object__open_file()`, `bpf_object__name()`, object load error handling, and selftests object iteration.

## Control Flow
`test_reference_tracking()` opens BPF object fixtures for reference acquisition/release scenarios, checks object name, and expects load success or verifier rejection according to each case.

## State and Persistence Behavior
Only object fds/logs are transient. Reference state is modeled inside verifier during program load.

## Dependencies and Integration Points
Depends on compiled reference-tracking BPF object files and verifier reference-lifetime rules.

## Risks and Edge Cases
Failure expectations are tightly coupled to verifier reference diagnostics and object naming conventions.

## Test Signals
Assertions check object name, object open, and success/failure of verifier load cases. Named assertion/check labels observed in the source include: `wrong obj name '%s', expected '%s'\n`, `obj_open_file`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/reference_tracking.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/reg_bounds.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/reg_bounds.c

## Purpose
Large verifier oracle for scalar register bounds. It generates BPF programs for combinations of signed/unsigned 64-bit and 32-bit ranges, simulates expected verifier refinement, parses verifier logs, and compares actual branch register states. The source was read as a complete 2253-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `num_is_small()`, `snprintf_num()`, `snprintf_range()`, `print_range()`, `range_eq()`, `is_valid_num()`, `is_valid_range()`, `range_canbe_op()`, `range_always_op()`, `range_never_op()`, `range_branch_taken_op()`, `range_cond()`, `print_reg_state()`, `print_refinement()`, `reg_state_refine()`, `reg_state_set_const()`, `reg_state_cond()`, `reg_state_branch_taken_op()`, `load_range_cmp_prog()`, `parse_reg_state()`, `parse_range_cmp_log()`, `assert_range_eq()`, `assert_reg_state_eq()`, `print_verifier_log()`, and 83 more.
- Includes and fixtures: `#include <limits.h>`, `#include <test_progs.h>`, `#include <linux/filter.h>`, `#include <linux/bpf.h>`.
- Generated skeletons/objects referenced: none in this C file; it uses raw object/helper loading or framework macros.
- Primary APIs and types: Raw `bpf_prog_load()` with generated `struct bpf_insn`, `BPF_JMP/JMP32` macros, verifier log options, `ASSERT_*`, environment variables `SLOW_TESTS`, `REG_BOUNDS_MAX_FAILURE_CNT`, `REG_BOUNDS_RAND_CASE_CNT`, `REG_BOUNDS_RAND_SEED`, and test_progs subtest registration.

## Control Flow
The file defines numeric domains, range cast/refinement operations, branch-condition simulation, generated BPF program loading, verifier-log parsing, and comparison helpers. Crafted cases run normally via `test_reg_bounds_crafted()`. Generated exhaustive cases require `SLOW_TESTS=1`; randomized cases use configurable seed/count and report reproducible progress.

## State and Persistence Behavior
State is in `struct ctx`: generated values/ranges, counters, failure limits, random seed, and progress timestamps. Verifier state is not persisted; it is parsed from each generated load log. Allocated range arrays are freed by `cleanup_ctx()`.

## Dependencies and Integration Points
Depends on verifier log text format, Linux BPF instruction macros, raw tracepoint program loading, selftests verbosity/progress plumbing, and enough log buffer for state extraction.

## Risks and Edge Cases
Extremely coupled to verifier output syntax and scalar-bound semantics; exhaustive cases are slow and gated; random tests must report seed for reproduction; parser defaults must mirror verifier defaults exactly.

## Test Signals
Signals include successful generated program loads, parsed false/true branch register states for R6/R7, exact range equality across U64/U32/S64/S32 domains, crafted edge cases, progress output, and bounded failure count behavior. Named assertion/check labels observed in the source include: `branch taken inconsistency!\n`, `load_range_cmp_prog`, `parse_range_cmp_log`, `uranges_calloc`, `sranges_calloc`, `usubranges_calloc`, `ssubranges_calloc`, `REG_BOUNDS_MAX_FAILURE_CNT`, `REG_BOUNDS_RAND_CASE_CNT`, `REG_BOUNDS_RAND_SEED`, `gen_ranges`, `parse_env_vars`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/reg_bounds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/res_spin_lock.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/res_spin_lock.c

## Purpose
Validates BPF resource spin-lock behavior, expected verifier failures, success paths, and stress behavior under concurrent test runs. The source was read as a complete 118-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_res_spin_lock_failure()`, `test_res_spin_lock_success()`, `serial_test_res_spin_lock_stress()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include <network_helpers.h>`, `#include <sys/sysinfo.h>`, `#include "res_spin_lock.skel.h"`, `#include "res_spin_lock_fail.skel.h"`.
- Generated skeletons/objects referenced: `res_spin_lock`, `res_spin_lock_fail`.
- Primary APIs and types: `res_spin_lock__open_and_load()`, `res_spin_lock_fail` skeleton, `bpf_prog_test_run_opts()`, `pthread_create()`, `sysinfo/get_nprocs` style CPU sizing, and network helpers.

## Control Flow
Failure subtests load invalid programs and expect rejection. Success subtests run valid programs and check retval. The serial stress test starts worker threads, repeatedly runs programs until timeout, and checks module/resource interactions.

## State and Persistence Behavior
State includes skeleton BSS retval/error fields, thread counters, timeout flags, and BPF map/resource lock state during runs. All state is cleaned when skeletons/threads exit.

## Dependencies and Integration Points
Depends on generated skeletons, resource spin-lock kernel support, pthreads, and the BPF test module for some paths.

## Risks and Edge Cases
Stress portion is timing and CPU-count sensitive; module availability can gate coverage; deadlocks/timeouts are the main failure mode.

## Test Signals
Assertions cover test-run success/retval, invalid-load errors, pthread creation, timeout status, and module load expectations. Named assertion/check labels observed in the source include: `test_run`, `test_run retval`, `res_spin_lock__open_and_load`, `error`, `retval`, `pthread_create`, `timeout err`, `err`, `timeout`, `load module AA`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/res_spin_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/resolve_btfids.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/resolve_btfids.c

## Purpose
Unit-tests userspace BTF ID symbol resolution logic used by kernel tooling, mapping symbol records to BTF type ids. The source was read as a complete 168-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `__resolve_symbol()`, `resolve_symbols()`, `test_resolve_btfids()`.
- Includes and fixtures: `#include <linux/err.h>`, `#include <string.h>`, `#include <bpf/btf.h>`, `#include <bpf/libbpf.h>`, `#include <linux/btf.h>`, `#include <linux/kernel.h>`, `#include <linux/btf_ids.h>`, `#include "test_progs.h"`.
- Generated skeletons/objects referenced: none in this C file; it uses raw object/helper loading or framework macros.
- Primary APIs and types: `btf__parse()`, `btf__find_by_name_kind()`, `__resolve_symbol()`, `resolve_symbols()`, `struct btf_id`, `ERR_PTR` helpers, and libbpf BTF APIs.

## Control Flow
The test constructs symbol requests, resolves each against BTF by name/kind, writes ids into result structures, and checks error behavior for missing or incompatible symbols.

## State and Persistence Behavior
State is local arrays of symbols/ids and a parsed BTF object. No kernel BPF program is loaded.

## Dependencies and Integration Points
Depends on libbpf BTF parser, kernel/user BTF data available to the fixture, and `linux/btf_ids.h` structure definitions.

## Risks and Edge Cases
BTF contents differ across kernels/configs; symbol-kind mismatches can be environment-specific; error-pointer handling must not be confused with raw ids.

## Test Signals
Pass/fail is determined by successful resolution of expected symbols and expected errors for unresolved entries. Named assertion/check labels observed in the source include: `id_check`, `ID %d not found in test_symbols\n`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/resolve_btfids.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ringbuf.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ringbuf.c

## Purpose
Comprehensive libbpf ring-buffer test covering mmap permissions, callback polling, per-ring inspection APIs, notification flags, consume_n batching, map-key use, write/discard behavior, and overwrite mode. The source was read as a complete 576-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `atomic_inc()`, `atomic_xchg()`, `process_sample()`, `trigger_samples()`, `ringbuf_write_subtest()`, `ringbuf_subtest()`, `process_n_sample()`, `ringbuf_n_subtest()`, `process_map_key_sample()`, `ringbuf_map_key_subtest()`, `ringbuf_overwrite_mode_subtest()`, `test_ringbuf()`.
- Includes and fixtures: `#include <linux/compiler.h>`, `#include <asm/barrier.h>`, `#include <test_progs.h>`, `#include <sys/mman.h>`, `#include <sys/epoll.h>`, `#include <time.h>`, `#include <sched.h>`, `#include <signal.h>`, `#include <pthread.h>`, `#include <sys/sysinfo.h>`, and 7 more.
- Generated skeletons/objects referenced: `test_ringbuf`, `test_ringbuf_lskel`, `test_ringbuf_map_key`, `test_ringbuf_map_key_lskel`, `test_ringbuf_n`, `test_ringbuf_n_lskel`, `test_ringbuf_overwrite`, `test_ringbuf_overwrite_lskel`, `test_ringbuf_write`, `test_ringbuf_write_lskel`.
- Primary APIs and types: `test_ringbuf*.lskel.h`, `ring_buffer__new/poll/consume/consume_n/ring`, `ring__map_fd/avail_data_size/size/consumer_pos/producer_pos/consume`, `mmap()`, `mprotect()`, `mremap()`, `pthread_create/tryjoin`, `BPF_RB_NO_WAKEUP`, `BPF_RB_FORCE_WAKEUP`, and ring-buffer header constants.

## Control Flow
`test_ringbuf()` runs five subtests. The main subtest validates mmap protections, triggers samples via `getpgid`, checks ring positions, polls until `-EDONE`, verifies adaptive/no/force wakeups with a background poll thread, and consumes pending samples. Additional subtests cover `consume_n`, map-key samples, user writes/discards, and overwrite accounting.

## State and Persistence Behavior
Global `sample_cnt`, `ringbuf`, and skeleton pointers coordinate callbacks. BPF BSS fields track pid, value, flags, dropped/total/discarded, positions, and overwrite counters. All ring buffers and skeletons are freed/detached.

## Dependencies and Integration Points
Depends on generated light skeletons, ring-buffer mmap ABI, pthreads, syscalls used as triggers, and libbpf ring APIs.

## Risks and Edge Cases
Mmap permission expectations are kernel ABI sensitive; wakeup tests have timing sleeps and background threads; global ringbuf state requires serial-like isolation.

## Test Signals
Assertions check mmap success/failure and errno, ring position/size values, callback sample values, poll return `-EDONE`, sample counts, wakeup blocking/unblocking, consume_n counts, map lookup by sample key, write/discard counters, and overwrite positions. Named assertion/check labels observed in the source include: `exp %ld, got %ld\n`, `skel_open`, `skel_load`, `unmap_rw`, `ringbuf_new`, `skel_attach`, `discarded`, `passed`, `skeleton open failed\n`, `skeleton load failed\n`, `rw_cons_pos`, `exec_cons_pos_protect`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ringbuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ringbuf_multi.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ringbuf_multi.c

## Purpose
Tests libbpf multi-ring manager behavior, ring indexes, dynamic resize/reset, and polling across multiple BPF ring buffers. The source was read as a complete 148-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `process_sample()`, `test_ringbuf_multi()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include <sys/epoll.h>`, `#include "test_ringbuf_multi.skel.h"`.
- Generated skeletons/objects referenced: `test_ringbuf_multi`.
- Primary APIs and types: `test_ringbuf_multi__open/load/attach()`, `ring_buffer__new()`, `ring_buffer__add()`, `ring_buffer__ring()`, `ring_buffer__poll()`, `ring__map_fd()`, resize/reset helpers, and `epoll` integration.

## Control Flow
The test adjusts ring sizes before load, verifies resize/reset behavior, loads/attaches the skeleton, creates a multi-ring buffer manager, triggers samples into multiple rings, checks ring index/map fd lookup, and validates polling again returns expected callback results.

## State and Persistence Behavior
BPF maps for two ring buffers persist during skeleton lifetime. User-space callback state records which samples arrived. Resize/reset changes map max_entries before load.

## Dependencies and Integration Points
Depends on `test_ringbuf_multi.skel.h`, libbpf multi-ring APIs, epoll, and ringbuf map resize support.

## Risks and Edge Cases
Resize after load should fail; ring index ordering matters; epoll readiness can be timing-sensitive.

## Test Signals
Assertions check size before/after resize/reset, rejected resize after load, ring index lookup, and expected repeated polling behavior. Named assertion/check labels observed in the source include: `exp %d, got %d\n`, `exp %ld, got %ld\n`, `unexpected sample seq %d, val %ld\n`, `skeleton open failed\n`, `rb1_size_before`, `rb1_resize`, `rb1_size_after`, `rb1_reset`, `rb1_size_final`, `bpf_map_create failed\n`, `bpf_map__set_inner_map_fd failed\n`, `skeleton load failed\n`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ringbuf_multi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/section_names.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/section_names.c

## Purpose
Verifies libbpf section-name parsing tables for program type and expected attach type inference. The source was read as a complete 261-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_prog_type_by_name()`, `test_attach_type_by_name()`, `test_section_names()`.
- Includes and fixtures: `#include <test_progs.h>`.
- Generated skeletons/objects referenced: none in this C file; it uses raw object/helper loading or framework macros.
- Primary APIs and types: `libbpf_prog_type_by_name()`, `libbpf_attach_type_by_name()`, local test case arrays, and selftests assertion macros.

## Control Flow
`test_section_names()` iterates known section-name patterns, checking program type resolution and attach type resolution separately for valid and invalid names.

## State and Persistence Behavior
No persistent state; all data is static/local test vectors.

## Dependencies and Integration Points
Depends on libbpf section parser behavior and the list of section patterns supported by this kernel/libbpf snapshot.

## Risks and Edge Cases
New section aliases or parser refactors require updating expected tables; tests can fail due to intentional libbpf API expansion.

## Test Signals
Failures identify section strings whose inferred program or attach type differs from expected. Named assertion/check labels observed in the source include: `prog: unexpected rc=%d for %s\n`, `prog: unexpected prog_type=%d for %s\n`, `prog: unexpected expected_attach_type=%d for %s\n`, `attach: unexpected rc=%d for %s\n`, `attach: unexpected attach_type=%d for %s\n`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/section_names.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/select_reuseport.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/select_reuseport.c

## Purpose
Large networking integration test for `BPF_PROG_TYPE_SK_REUSEPORT` selection across reuseport sockarray, sockmap, and sockhash inner maps, TCP/UDP, IPv4/IPv6, loopback/inany binds, syncookies, pass-on-error, and detach behavior. The source was read as a complete 861-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `create_maps()`, `prepare_bpf_obj()`, `ss_init_loopback()`, `ss_init_inany()`, `read_int_sysctl()`, `write_int_sysctl()`, `enable_fastopen()`, `enable_syncookie()`, `disable_syncookie()`, `get_linum()`, `check_data()`, `check_results()`, `send_data()`, `do_test()`, `test_err_inner_map()`, `test_err_skb_data()`, `test_err_sk_select_port()`, `test_pass()`, `test_syncookie()`, `test_pass_on_err()`, `test_detach_bpf()`, `prepare_sk_fds()`, `setup_per_test()`, `cleanup_per_test()`, and 5 more.
- Includes and fixtures: `#include <stdlib.h>`, `#include <unistd.h>`, `#include <stdbool.h>`, `#include <string.h>`, `#include <errno.h>`, `#include <assert.h>`, `#include <fcntl.h>`, `#include <linux/bpf.h>`, `#include <linux/err.h>`, `#include <linux/types.h>`, and 10 more.
- Generated skeletons/objects referenced: `bpf_object`.
- Primary APIs and types: `bpf_map_create()`, `BPF_MAP_TYPE_ARRAY_OF_MAPS`, `bpf_map__reuse_fd()`, `bpf_object__open/load()`, `SO_REUSEPORT`, `SO_ATTACH_REUSEPORT_EBPF`, `SO_DETACH_REUSEPORT_BPF`, `epoll`, `sendto(MSG_FASTOPEN)`, socket syscalls, netns helpers, and sysctl read/write for fastopen/syncookies.

## Control Flow
`serial_test_select_reuseport()` runs the full matrix for three map types. Each map type creates inner/outer maps, loads `test_select_reuseport_kern.bpf.o`, then for each socket/family/bind config creates a fresh netns, enables fastopen, disables syncookies, sets up 32 reuseport sockets, installs the inner map, runs error/pass/syncookie/detach subtests, checks result/data maps, and cleans sockets/maps.

## State and Persistence Behavior
Global fds hold maps, BPF object, socket array, epoll fd, server sockaddr, and expected result counters. It temporarily mutates TCP sysctls inside the test netns and BPF maps (`result_map`, `tmp_index_ovr_map`, `linum_map`, `data_check_map`). Cleanup closes fds and removes outer-map entries.

## Dependencies and Integration Points
Depends on network namespace creation, TCP fastopen/syncookie sysctls, BPF reuseport program support, map-in-map, sockmap/sockhash support, and the compiled kernel BPF object plus common header.

## Risks and Edge Cases
Complex environmental sensitivity: netns permissions, sysctl availability, TCP fastopen behavior, syncookie timing, socket ordering, and optional detach socket option. Global state makes serial execution necessary.

## Test Signals
Signals include result-map counters per enum result, data_check map fields for skb protocol/addresses/ports/hash, epoll selected socket index, received command payload, syncookie tmp-index reset, and no BPF runs after detach. Named assertion/check labels observed in the source include: `netns_new`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/select_reuseport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/send_signal.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/send_signal.c

## Purpose
Tests `bpf_send_signal()` and thread-targeted signal delivery from tracepoint, software perf, and hardware/NMI perf contexts, including remote process signaling. The source was read as a complete 293-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `sigusr1_handler()`, `sigusr1_siginfo_handler()`, `test_send_signal_common()`, `test_send_signal_tracepoint()`, `test_send_signal_perf()`, `test_send_signal_nmi()`, `test_send_signal()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include <sys/time.h>`, `#include <sys/resource.h>`, `#include "test_send_signal_kern.skel.h"`, `#include "io_helpers.h"`.
- Generated skeletons/objects referenced: `bpf_program`, `test_send_signal_kern`.
- Primary APIs and types: `test_send_signal_kern__open_and_load/attach()`, `bpf_program__attach_perf_event()`, `perf_event_open`, `fork()`, pipes, `sigaction()/signal()`, `setpriority()`, `read_with_timeout()`, and SIGUSR1 handlers.

## Control Flow
`test_send_signal_common()` forks a child, installs handlers, coordinates readiness over pipes, loads/attaches either tracepoint or perf program, sets BSS target fields, triggers the event locally or remotely, waits for the child result, then kills/waits for cleanup. `test_send_signal()` runs 12 subtests across context, thread flag, and remote flag.

## State and Persistence Behavior
Global `sigusr1_received` records signal receipt in child context. Skeleton BSS fields define signal number, target pid, current pid, and thread-vs-process mode. Pipes coordinate parent/child; priority is temporarily raised and restored.

## Dependencies and Integration Points
Depends on generated `test_send_signal_kern.skel.h`, perf software/hardware events, signal permissions, fork/pipe support, and `io_helpers.h` timeout reads.

## Risks and Edge Cases
Hardware PMU may be unavailable and is skipped for known errno; signal timing is inherently racy; priority changes can fail under policy; child cleanup uses SIGKILL on error paths.

## Test Signals
Assertions check pipe/fork/signal setup, priority operations, skeleton attach or perf attach, child signal value 8, timeout read, and result byte correctness. Named assertion/check labels observed in the source include: `pipe_p2c`, `fork`, `sigaction`, `signal`, `getpriority`, `setpriority`, `pipe_write`, `pipe_read`, `sigusr1_received`, `skel_open_and_load`, `skel_attach`, `perf_event_open`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/send_signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/send_signal_sched_switch.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/send_signal_sched_switch.c

## Purpose
Serial stress path for BPF signal sending from the scheduler switch tracepoint context. The source was read as a complete 62-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `sigusr1_handler()`, `serial_test_send_signal_sched_switch()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include <stdio.h>`, `#include <stdlib.h>`, `#include <sys/mman.h>`, `#include <pthread.h>`, `#include <sys/types.h>`, `#include <sys/stat.h>`, `#include <fcntl.h>`, `#include "test_send_signal_kern.skel.h"`.
- Generated skeletons/objects referenced: `test_send_signal_kern`.
- Primary APIs and types: `test_send_signal_kern.skel.h`, `pthread`, `mmap`, file/syscall helpers, SIGUSR1 handler, and scheduler-triggering loops.

## Control Flow
The test installs a signal handler, loads the signal skeleton variant for sched_switch, creates activity that causes context switches, and waits until the signal is delivered from BPF.

## State and Persistence Behavior
Global signal flag/counter records delivery. Skeleton BSS configures target pid/signal. Temporary threads and mappings are cleaned at end.

## Dependencies and Integration Points
Depends on sched_switch tracepoint availability, generated skeleton, signal delivery from BPF, and serial execution to avoid handler interference.

## Risks and Edge Cases
Scheduler timing and system load can make delivery latency variable; shared signal handler state is not parallel-safe.

## Test Signals
Pass condition is observed SIGUSR1 delivery while the sched_switch-attached BPF program is active. Named assertion/check labels observed in the source include: `skeleton open_and_load failed\n`, `skeleton attach failed\n`, `Error creating thread, %s\n`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/send_signal_sched_switch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/setget_sockopt.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/setget_sockopt.c

## Purpose
Tests BPF cgroup socket hooks that get/set socket options across TCP, UDP, kTLS, and nonstandard option paths. The source was read as a complete 246-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `create_netns()`, `test_tcp()`, `test_udp()`, `test_ktls()`, `test_nonstandard_opt()`, `test_setget_sockopt()`.
- Includes and fixtures: `#include <sched.h>`, `#include <linux/socket.h>`, `#include <linux/tls.h>`, `#include <net/if.h>`, `#include "test_progs.h"`, `#include "cgroup_helpers.h"`, `#include "network_helpers.h"`, `#include "setget_sockopt.skel.h"`.
- Generated skeletons/objects referenced: `bpf_link`, `bpf_program`, `setget_sockopt`.
- Primary APIs and types: `setget_sockopt__open/load/attach()`, cgroup helpers, `start_server()`, `connect_to_fd_server()`, `connect_to_fd()`, `accept()`, `setsockopt()/getsockopt()`, TLS socket options, netns/veth helpers, and skeleton BSS counters.

## Control Flow
`test_setget_sockopt()` creates a netns/cgroup environment, attaches cgroup programs, then runs TCP, UDP, kTLS, and nonstandard option subtests. Each creates sockets, triggers cgroup hooks, and validates BPF counters and socket option effects.

## State and Persistence Behavior
State includes cgroup attachments/links, netns/veth setup, server/client sockets, TLS state, and skeleton BSS counters for listen/connect/active/passive/post_create/bind hooks. Cleanup detaches links and tears down namespace/cgroup state.

## Dependencies and Integration Points
Depends on `setget_sockopt.skel.h`, cgroup v2 helpers, network helpers, kTLS support for TLS subtest, and socket hook program types.

## Risks and Edge Cases
kTLS and cgroup permissions may be unavailable; socket option semantics differ by protocol; leaked cgroup links can affect later tests.

## Test Signals
Assertions check veth setup, server/client connections, hook counters, TLS setsockopt/read behavior, and nonstandard option handling. Named assertion/check labels observed in the source include: `bring veth up`, `start_server`, `connect_to_fd_server`, `nr_listen`, `nr_connect`, `nr_active`, `nr_passive`, `nr_socket_post_create`, `nr_bind`, `connect_to_fd`, `accept`, `tls`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/setget_sockopt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sha256.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sha256.c

## Purpose
Unit-tests libbpf internal SHA-256 implementation against randomized data and a digest-of-digests accumulator. The source was read as a complete 53-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_sha256()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include "bpf/libbpf_internal.h"`.
- Generated skeletons/objects referenced: none in this C file; it uses raw object/helper loading or framework macros.
- Primary APIs and types: `libbpf_sha256_*` internal helpers from `bpf/libbpf_internal.h`, `malloc()`, `random()`, and selftests assertions.

## Control Flow
The test allocates buffers, generates random input of varying sizes, computes SHA-256 digests, feeds those digests into a final digest, and compares to the expected fixture value.

## State and Persistence Behavior
Only heap buffers and digest contexts are mutated. No kernel/BPF state is used.

## Dependencies and Integration Points
Depends on libbpf internal SHA-256 implementation and deterministic random seeding/sequence used by the test.

## Risks and Edge Cases
Because it uses internal APIs, refactors can require test adjustment; random sequence must remain deterministic for the expected digest.

## Test Signals
Assertions check allocation, random data generation path, and final digest-of-digests match. Named assertion/check labels observed in the source include: `malloc`, `random`, `digest_of_digests`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sha256.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/signal_pending.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/signal_pending.c

## Purpose
Verifies that pending Unix signals interrupt long-running `BPF_PROG_TEST_RUN` execution as expected. The source was read as a complete 51-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `sigalrm_handler()`, `test_signal_pending_by_type()`, `test_signal_pending()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include <network_helpers.h>`.
- Generated skeletons/objects referenced: none in this C file; it uses raw object/helper loading or framework macros.
- Primary APIs and types: `sigaction(SIGALRM)`, interval timers/alarms, `bpf_prog_test_run_opts()`, network helper object loading, and duration timing.

## Control Flow
`test_signal_pending_by_type()` loads a test program, arms SIGALRM, starts a long test-run, and verifies the run returns promptly when the signal is pending. Top-level runs applicable program types.

## State and Persistence Behavior
Global SIGALRM handler flag plus timer state; loaded program fd is transient.

## Dependencies and Integration Points
Depends on signal delivery, BPF test-run duration/loop behavior, and network helper loading for selected program types.

## Risks and Edge Cases
Timer granularity and scheduling can make duration assertions flaky; handler state requires isolation.

## Test Signals
Assertions cover program load, sigaction/timer setup, and bounded duration/interruption behavior. Named assertion/check labels observed in the source include: `test-run load`, `test-run-signal-sigaction`, `test-run-signal-timer`, `test-run-signal-duration`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/signal_pending.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sk_assign.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sk_assign.c

## Purpose
Integration test for `bpf_sk_assign()` in TC ingress, proving traffic can be redirected to a selected socket even when destination port/address differs. The source was read as a complete 300-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `configure_stack()`, `rcv_msg()`, `run_test()`, `prepare_addr()`, `test_sk_assign()`.
- Includes and fixtures: `#include <fcntl.h>`, `#include <signal.h>`, `#include <stdlib.h>`, `#include <unistd.h>`, `#include "test_progs.h"`, `#include "network_helpers.h"`.
- Generated skeletons/objects referenced: none in this C file; it uses raw object/helper loading or framework macros.
- Primary APIs and types: `tc` command invocation, `ip` route/link commands, `unshare(CLONE_NEWNET)`, `setns()`, `bpf_obj_get()` for `/sys/fs/bpf/tc/globals/server_map`, `bpf_map_update_elem()`, `start_server_addr()`, `connect_to_addr()`, socket read/write helpers, and IPv4/IPv6 address preparation.

## Control Flow
`test_sk_assign()` saves the original netns, configures a new netns and TC clsact program, opens the pinned server map, then runs eight TCP/UDP IPv4/IPv6 port/address rewrite subtests. Each starts a server on `BIND_PORT`, updates the BPF map with its fd, connects to `CONNECT_PORT` or rewritten address, sends data, and checks the receiving socket port.

## State and Persistence Behavior
Persistent during the test: a new netns, loopback routes, TC qdisc/filter, pinned TC globals map, and server socket fd stored in `server_map`. Cleanup unlinks the map path and returns to the original netns.

## Dependencies and Integration Points
Depends on external `tc` and `ip`, tc built with or without libbpf selecting different object files, CAP_NET_ADMIN, bpffs TC globals path, and network helpers.

## Risks and Edge Cases
External command availability/version matters; cleanup after netns/TC failure is delicate; fixed test ports can conflict inside namespace only if setup leaks.

## Test Signals
Subtests pass when data arrives and accepted TCP sockets report `CONNECT_PORT` while UDP server remains on `BIND_PORT`; setup failures print command-specific diagnostics. Named assertion/check labels observed in the source include: `%d\n`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sk_assign.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sk_bypass_prot_mem.c -->

# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sk_bypass_prot_mem.c

## Purpose
Tests socket protected-memory bypass accounting for TCP and UDP under BPF sk_msg/sk_skb style hooks and sysctl-controlled memory pressure. The source was read as a complete 298-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `tcp_create_sockets()`, `udp_create_sockets()`, `get_memory_allocated()`, `tcp_get_memory_allocated()`, `udp_get_memory_allocated()`, `check_bypass()`, `run_test()`, `serial_test_sk_bypass_prot_mem()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include "sk_bypass_prot_mem.skel.h"`, `#include "network_helpers.h"`, `#include <unistd.h>`.
- Generated skeletons/objects referenced: `bpf_program`, `sk_bypass_prot_mem`.
- Primary APIs and types: `sk_bypass_prot_mem__open_and_load/attach()`, `start_server()`, `connect_to_fd()`, `accept()`, `setsockopt(SO_RCVBUF)`, socket send/connect helpers, netns/sysctl helpers, and `/proc/net/sockstat`-style memory readers.

## Control Flow
The serial test opens a netns, toggles memory-protection sysctls, loads/attaches skeleton programs, creates TCP/UDP socket pairs, samples memory allocation before/after sends, and runs bypass/no-bypass checks.

## State and Persistence Behavior
State includes netns sysctls, server/client sockets, socket receive buffer sizes, BPF links, and observed protocol memory counters. Cleanup restores sysctls/netns and closes sockets.

## Dependencies and Integration Points
Depends on `sk_bypass_prot_mem.skel.h`, network helpers, socket memory accounting files/sysctls, and BPF socket program support.

## Risks and Edge Cases
Memory accounting is noisy and kernel-version dependent; sysctl write permissions and namespace isolation are required; protocol differences make thresholds subtle.

## Test Signals
Assertions check socket creation/connect/accept, rcvbuf setsockopt, memory reads, send success, and expected bypass versus no-bypass counter movement. Named assertion/check labels observed in the source include: `start_server_str`, `connect_to_fd`, `accept`, `start_server`, `connect_fd_to_fd`, `setsockopt(SO_RCVBUF)`, `get_memory_allocated`, `send`, `bypass`, `no bypass`, `open_and_load`, `/sk_bypass_prot_mem`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sk_bypass_prot_mem.c -->

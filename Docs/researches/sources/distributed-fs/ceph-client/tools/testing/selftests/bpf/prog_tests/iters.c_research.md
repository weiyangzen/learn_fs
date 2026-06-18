
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/iters.c

## Purpose

`iters.c` validates numeric, task, VMA, cgroup, css, testmod, and state-safety iterator behavior, including both attached iterators and open-coded iterator programs.

## Important APIs, Types, and Functions

The harness uses many skeletons: `iters`, `iters_state_safety`, `iters_looping`, `iters_num`, `iters_testmod`, `iters_testmod_seq`, `iters_task_vma`, `iters_task`, `iters_css_task`, `iters_css`, and `iters_task_failure`. It uses `bpf_iter_create()`, direct `bpf_prog_test_run_opts()`, `/proc/self/maps`, cgroup helpers, pthreads, `mmap`-related triggers, and `RUN_TESTS` for verifier cases.

## Control Flow and Data Flow

Numeric iterator subtests attach, briefly run, detach, and compare many BSS results to rodata expected values. Testmod seq iterators run only when `env.has_testmod`. Task VMA tests compare BPF-seen ranges to `/proc/self/maps`. Task iterator tests create blocked threads and verify process/thread counts. CSS/cgroup tests create and join cgroups before triggering. Additional subtests cover looping/state safety and expected failures.

## State, Dependencies, Integration Points, Risks, and Test Signals

State includes iterator links/FDs, BSS result arrays, cgroups, temporary threads, and process VMA snapshots. Dependencies are BPF iterator kernel support, cgroupfs setup, testmod for module iterators, pthreads, and procfs. Integration is iterator next/destroy semantics, open-coded iterators, task/mm/css references, and verifier state safety. Risks are environmental cgroup setup failure, thread-count races, `/proc/self/maps` special entries, and skipped module coverage. Test signals are BSS result equals rodata expected values, VMA ranges match procfs, process/thread counts match, cgroup/css counts are correct, and verifier-case skeletons pass.

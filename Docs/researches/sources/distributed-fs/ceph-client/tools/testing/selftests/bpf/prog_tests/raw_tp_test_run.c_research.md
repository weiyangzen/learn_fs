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

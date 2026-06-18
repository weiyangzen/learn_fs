# sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/amd-ibs-period.c

## Purpose
This file implements an x86 perf test suite for AMD IBS sample-period behavior. It exercises both `ibs_fetch` and `ibs_op` PMUs through direct `perf_event_open`, mmap ring-buffer sample collection, period/frequency constraints, `PERF_EVENT_IOC_PERIOD`, invalid configuration rejection, and L3MissOnly filtering. The test is AMD-only, IBS-PMU-only, and intentionally skipped on kernels older than v6.15 because it verifies fixes expected in that kernel generation.

## Important APIs, Types, and Data
The central exported entry point is `test__amd_ibs_period(struct test_suite *, int)`. Global state includes `page_size`, `fetch_pmu`, `op_pmu`, and `perf_event_max_sample_rate`. Local helpers build `struct perf_event_attr` instances with `fetch_prepare_attr()` and `op_prepare_attr()`, using PMU type IDs found through `perf_pmus__find("ibs_fetch")` and `perf_pmus__find("ibs_op")`.

The data tables drive most behavior: `fetch_configs[]` and `op_configs[]` validate IBS-specific `MaxCnt` configuration encoding; `fetch_period[]` and `op_period[]` validate kernel normalization of period/frequency requests; `fetch_ioctl[]` and `op_ioctl[]` validate dynamic period updates; and `fetch_l3missonly`/`op_l3missonly` validate filtered IBS events where hardware discards tagged operations before software sees a sample.

Ring-buffer helpers `copy_sample_data()`, `rb_read()`, `rb_skip()`, and `rb_drain_samples()` read `PERF_RECORD_SAMPLE` records from an mmaped perf buffer. The sample contract is narrow: `sample_type = PERF_SAMPLE_PERIOD`, so sample records are expected to contain only the header and sampled period payload.

## Control Flow
`test__amd_ibs_period()` initializes page size, reads `/proc/sys/kernel/perf_event_max_sample_rate`, locates IBS PMUs, skips non-AMD/non-IBS/old-kernel systems, resolves the current perf executable path, pins the process to CPU 0, then runs five checks in order: config encoding, period/frequency constraints, ioctl period updates, negative high-frequency config admission, and L3MissOnly filtering. `dummy_workload_1()` uses executable anonymous memory and tiny return-value instruction sequences to create IBS activity. `dummy_workload_2()` invokes `taskset -c 0 <perf> bench sched messaging -g 10 -l 5000` to produce memory behavior for L3-miss filtering.

## State and Persistence
No durable repository state is written. Runtime state is kernel and process state: perf event file descriptors, mmaped ring buffers, process CPU affinity, executable memory from `mprotect(PROT_EXEC)`, and a shell command spawned via `system()`. `rb_read()` advances `data_tail` after copying records. The test mutates selected expected-result table rows when requested frequency exceeds the runtime `perf_event_max_sample_rate`.

## Dependencies and Integration Points
The file depends on Linux perf UAPI, syscalls, `sched_setaffinity`, `mprotect`, `uname`, and `/proc/sys/kernel/perf_event_max_sample_rate`. It integrates with perf tooling through `arch-tests.h`, `tests/tests.h`, PMU discovery, `perf_exe()`, `x86__is_amd_cpu()`, `ARRAY_SIZE`, `strbuf`, and debug logging. `arch-tests.c` registers it with `DEFINE_SUITE_EXCLUSIVE("AMD IBS sample period", amd_ibs_period)`.

## Risks and Edge Cases
The test is hardware-, kernel-, privilege-, and system-load-sensitive. It opens CPU-wide events on CPU 0, so perf paranoid settings, missing IBS support, lack of PMU formats, or container restrictions can cause skips or failures. Zero-sample paths are logged but not always cascaded as failures because the test cannot distinguish lack of activity from an IBS failure in every case. Executable anonymous memory and `system()` execution increase environmental sensitivity. The kernel-version parser assumes `major.minor` at the start of `utsname.release`.

## Test Signals
Strong positive signals are `TEST_OK` with debug output showing accepted/rejected config values, nonzero samples where available, and period equality or minimum-period compliance. Expected skip signals are non-AMD CPU, missing IBS PMUs, or kernel older than v6.15. Failures indicate regressions in IBS period validation, config-to-period conversion, ioctl validation, perf sample-rate enforcement, or L3MissOnly period clamping.

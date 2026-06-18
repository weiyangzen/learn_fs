# sources/distributed-fs/ceph-client/tools/testing/selftests/turbostat/smi_aperf_mperf.py

## Purpose
This test validates turbostat columns that depend on SMI, APERF, and MPERF data across MSR-backed and perf-backed counter sources.

## Important APIs, Types, and Functions
`check_perf_access()` probes `msr/mperf/`, `msr/aperf/`, and `msr/smi/` with `perf stat`. `check_msr_access()` opens `/dev/cpu/<BASE_CPU>/msr` and uses `pread()` on IA32_MPERF and IA32_APERF MSRs. The script optionally uses `ctypes.CDLL(None).sched_getcpu()` to choose a base CPU. It runs turbostat with `--show` on `SMI`, `Avg_MHz`, `Busy%`, `Bzy_MHz`, and `IPC` when perf is available.

## Control Flow
The script discovers MSR and perf access, builds counter source options `--no-perf` and/or `--no-msr`, skips entirely if neither is available, locates turbostat and timeout, then for each dependent column and source option runs turbostat normally and with `--debug`, comparing exact headers.

## State and Persistence
No persistent state is written. It reads MSR device files and launches external processes.

## Dependencies and Integration Points
It depends on x86 MSR devices, perf event access, turbostat, timeout, and optional ctypes access to `sched_getcpu()`.

## Risks
Hardware and permission sensitivity is high. Missing MSR or perf access prunes parts of coverage. Exact header matching is brittle. `IPC` is skipped for `--no-perf` because it requires perf.

## Test Signals
Pass means each selected counter source reports the requested dependent column alone in normal mode and with default debug columns in debug mode. Skip text indicates unavailable counter sources.

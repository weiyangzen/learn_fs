<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/config

## Purpose
This file lists kernel configuration options needed for broad ftrace selftest coverage.

## Important APIs, Types, And Functions
It requires ftrace, kprobe/uprobe, eprobe/fprobe, BTF, histogram triggers, syscall tracing, function graph return values, IRQ/preempt tracers, stack/snapshot/profiler support, modules, samples, and delay-test modules.

## Control Flow
kselftest uses this as prerequisite documentation/config checking data; individual `ftracetest` cases still evaluate runtime files and README strings.

## State And Persistence
No state is mutated.

## Dependencies And Integration Points
It maps to ftrace features under tracefs and module-based samples used by `test.d`.

## Risks
Config options may be necessary but not sufficient; tracefs permissions, module availability, and architecture support can still skip or fail tests.

## Test Signals
Kernels satisfying this config should expose the required tracefs files, tracers, and README feature strings for most ftrace `.tc` cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ftrace/config -->

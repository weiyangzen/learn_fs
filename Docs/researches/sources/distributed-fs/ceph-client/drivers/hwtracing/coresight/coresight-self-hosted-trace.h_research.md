# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-self-hosted-trace.h

## Purpose
This small arm64 helper header wraps access to the self-hosted trace filter control register `TRFCR_EL1`. It is used by trace source code that needs to enable or restore architectural tracing controls outside CoreSight MMIO blocks.

## Important APIs, Types, And Functions
`read_trfcr()` returns `read_sysreg_s(SYS_TRFCR_EL1)`. `write_trfcr(u64 val)` writes `SYS_TRFCR_EL1` and immediately executes `isb()` so subsequent execution observes the new trace filter state.

## Control Flow And State
The header owns no storage. It provides ordered register access for callers that store desired TRFCR values in their own driver state, such as ETM/ETE code maintaining per-CPU trace enable state.

## Dependencies And Integration Points
The only direct dependency is `asm/sysreg.h`. Integration is architecture-specific: this helper is meaningful on arm64 CPUs implementing self-hosted trace controls and is expected to be included only in code paths where `SYS_TRFCR_EL1` is valid.

## Risks And Test Signals
The main risk is calling it on unsupported architecture/configuration paths or forgetting the synchronization requirement after writes. The `isb()` in `write_trfcr()` is the critical ordering behavior. Test signals are compile coverage for arm64 trace builds and runtime ETM/ETE sessions that require TRFCR programming across enable, disable, CPU hotplug, and power transitions.

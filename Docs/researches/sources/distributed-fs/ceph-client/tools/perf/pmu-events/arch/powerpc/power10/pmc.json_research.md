# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/pmc.json

## Purpose

This file defines 42 POWER10 raw events for baseline PMU accounting, privilege-mode cycles and completions, PMC overflow/rewind/saved behavior, threshold exceptions, run latch accounting, interrupts, and marked probe/time-out events. It supplies many denominator and context counters used by POWER10 metrics.

## APIs, types, and schema

Entries use `EventCode`, `EventName`, and `BriefDescription`. Important names include `PM_INST_CMPL`, `PM_CYC`, `PM_RUN_CYC`, `PM_RUN_INST_CMPL`, `PM_INST_FIN`, `PM_HYPERVISOR_CYC`, `PM_PRIVILEGED_CYC`, `PM_ULTRAVISOR_CYC`, `PM_RUN_CYC_SMT2_MODE`, `PM_RUN_CYC_SMT4_MODE`, `PM_PMC*_OVERFLOW`, `PM_PMC*_REWIND`, and `PM_THRESH_EXC_*`.

## Control flow and integration

Perf generation treats these as raw events. Runtime metrics use them as bases for CPI, IPC, run-cycle rate, completed instruction set size, privilege accounting, threshold behavior, and operation-per-instruction ratios. The file is central to metric evaluation because `PM_CYC`, `PM_INST_CMPL`, `PM_RUN_CYC`, and `PM_RUN_INST_CMPL` are common denominators.

## State and persistence

The file is static metadata, but its generated event names are persistent user-facing identifiers. Counters such as PMC overflow and rewind describe hardware PMU state transitions, but the JSON itself does not persist runtime counter state.

## Dependencies

Dependencies include POWER10 PMU hardware semantics and perf's event parser. `metrics.json` depends heavily on the baseline counters in this file. Integration points include perf list output, metric evaluation, Python perf bindings, and tests that compare generated PMU event tables against JSON.

## Risks

Baseline counter mistakes have high impact because they skew many derived ratios. Privilege and ultravisor/hypervisor counters can be sensitive to execution context and availability. PMC overflow/rewind/saved events are low-level and can be confused with perf's own sampling overflow behavior. The lack of `PublicDescription` reduces detail for users diagnosing mode-specific measurements.

## Test signals

Use `jq`, uniqueness checks, perf PMU generation, and runtime direct event opens. Integration tests should evaluate `IPC`, `RUN_CPI`, `RUN_IPC`, `RUN_CYCLES_RATE`, and stall metrics that rely on `PM_RUN_INST_CMPL`. Mode-specific counters should be checked only on environments where privilege and ultravisor semantics are meaningful.

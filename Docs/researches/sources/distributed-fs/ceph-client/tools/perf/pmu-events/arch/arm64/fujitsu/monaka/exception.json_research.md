<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/exception.json

## Purpose
Monaka exception topic file that selects standard ARM64 exception events for the model. It covers exception entry, return, undefined instruction, SVC, instruction/data aborts, IRQ/FIQ, SMC, and HVC.

## APIs, Types, and Functions
The file contains `ArchStdEvent` entries with Monaka descriptions. Aliases include `EXC_TAKEN`, `EXC_RETURN`, `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, `EXC_DABORT`, `EXC_IRQ`, `EXC_FIQ`, `EXC_SMC`, and `EXC_HVC`.

## Control Flow, State, and Persistence
During build, standard ARM64 event metadata is resolved and emitted into the Monaka PMU table. Runtime perf sessions program counters by alias after CPU matching. No configuration or persistence exists beyond the JSON table.

## Dependencies and Integration
Depends on ARM64 standard event definitions and the Monaka mapfile entry. It integrates with kernel, virtualization, interrupt, and fault-analysis workflows that need exception counts alongside instruction retirement and branch speculation data.

## Risks and Test Signals
Risks are architecture-version differences in exception attribution, virtualization traps being counted differently than expected, and alias resolution failures if standard names change. Test signals include generated table success, controlled syscall and interrupt workloads increasing `EXC_SVC` and `EXC_IRQ`, fault injection increasing abort counters, and consistency between `EXC_TAKEN` and subtype totals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/exception.json -->

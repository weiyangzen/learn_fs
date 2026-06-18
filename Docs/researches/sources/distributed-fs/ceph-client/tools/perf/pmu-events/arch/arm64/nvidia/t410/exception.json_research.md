<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/exception.json

## Purpose
NVIDIA T410 exception topic table. It selects standard exception entry/return/subtype events plus trapped exception classes for aborts, other traps, IRQ, and FIQ.

## APIs, Types, and Functions
All records are `ArchStdEvent` aliases with public descriptions. Names include `EXC_TAKEN`, `EXC_RETURN`, `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, `EXC_DABORT`, `EXC_IRQ`, `EXC_FIQ`, `EXC_SMC`, `EXC_HVC`, `EXC_TRAP_PABORT`, `EXC_TRAP_DABORT`, `EXC_TRAP_OTHER`, `EXC_TRAP_IRQ`, and `EXC_TRAP_FIQ`.

## Control Flow, State, and Persistence
The perf build resolves these standard aliases into the generated T410 PMU table. Runtime counter state is owned by PMU hardware and perf sessions; the JSON has no persistence beyond source metadata.

## Dependencies and Integration
Depends on ARM64 standard exception events and the T410 mapfile row. It integrates with virtualization, kernel fault, and interrupt diagnostics on NVIDIA ARM64 systems.

## Risks and Test Signals
Risks include traps being counted differently across exception levels, virtualized environments masking hardware events, and subtype totals not matching aggregate `EXC_TAKEN` exactly. Test signals are successful generation, syscall and interrupt workloads, fault injection for aborts, hypervisor trap tests where available, and consistency with kernel tracepoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/exception.json -->

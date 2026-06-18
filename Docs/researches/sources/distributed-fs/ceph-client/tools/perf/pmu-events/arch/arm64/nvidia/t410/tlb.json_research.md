# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/tlb.json

## Purpose
This 38-entry T410 Arm64 file enumerates instruction/data TLB access, refill, walk, hardware update, step, page-size, read/write, and prefetch-related translation events. It covers L1I, L1D, L2D, DTLB, ITLB, and software-prefetch cases.

## Important Data Fields
Rows use `ArchStdEvent` for common Arm events and `EventCode`/`EventName` for T410-specific extensions such as `L1I_TLB_REFILL_PRFM` at `0x0224`. `PublicDescription` distinguishes demand, prefetch, refill, walk, and fault-exclusion semantics.

## Control Flow And Integration
`jevents.py` turns the table into generated T410 PMU aliases. Runtime consumers include direct perf commands, memory-system investigation workflows, and metrics that compare translation stalls with cache and memory activity.

## State, Dependencies, Risks, And Tests
The JSON is static state. It depends on standard Arm definitions for common TLB events and correct local codes for the implementation-defined set. Risks include duplicate-looking event families with subtly different units, fault-exclusion semantics, and metrics that combine walk-per-cycle with raw event counts. Test signals include JSON validation, generated alias presence, and hardware checks under TLB-pressure workloads.

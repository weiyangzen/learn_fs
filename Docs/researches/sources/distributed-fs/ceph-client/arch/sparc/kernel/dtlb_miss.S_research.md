# sources/distributed-fs/ceph-client/arch/sparc/kernel/dtlb_miss.S

## Purpose
`dtlb_miss.S` is an inline trap-table fragment for sparc64 data TLB misses. It performs the fastest possible TSB lookup for non-context-zero misses and loads the DTLB directly when the TSB tag matches.

## Important APIs, Types, and Functions
There are no callable C-style functions. The fragment uses privileged ASIs `ASI_DMMU_TSB_8KB_PTR`, `ASI_DMMU`, and `ASI_DTLB_DATA_IN`, the `TSB_LOAD_QUAD()` macro, and external trap labels `kvmap_dtlb` and `tsb_miss_dtlb`.

## Control Flow and State
The handler reads the current DMMU TSB pointer and tag target, extracts the context, and branches to `kvmap_dtlb` for context zero. Otherwise it masks the context out of the tag, loads the candidate TSB entry, compares tags, branches to the full miss path with `FAULT_CODE_DTLB` on mismatch, or writes the TTE into `ASI_DTLB_DATA_IN` and `retry`s.

## Persistence and Dependencies
The only state mutated is the hardware DTLB. Correctness depends on TSB entry format, register conventions in the trap table, and the miss/fault handlers included by `head_64.S`.

## Integration Points, Risks, and Test Signals
This code integrates with `ktlb.S`, `tsb.S`, and the sparc64 trap table. It is latency-sensitive and line-padded for trap-table/icache layout. Risks include register convention drift, incorrect context masking, and TSB/TTE format changes. Test signals are successful user/kernel data accesses after TLB eviction, no unexpected `tsb_miss_dtlb` floods, and boot stability under memory pressure.

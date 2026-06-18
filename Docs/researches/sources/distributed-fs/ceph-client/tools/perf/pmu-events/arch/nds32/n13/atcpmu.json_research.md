# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/nds32/n13/atcpmu.json

## Purpose
This 48-entry NDS32 N13 ATCPMU file defines core event aliases for branch behavior, instruction classes, interrupts/exceptions, loads/stores, TLB access/miss, stalls, BIU cycles/requests, cache/DLM/ILM access, DMA, external events, and compact instruction forms such as `push25_inst` and `pop25_inst`.

## Important Data Fields
Rows use `PublicDescription`, `EventCode`, `EventName`, and `BriefDescription`. Encodings are hex strings such as `0x102` for `cond_br` and `0x21e` for `pop25_inst`. There are no standard-event references; this is a concrete N13 model table.

## Control Flow And Integration
The NDS32 `mapfile.csv` maps CPUID `0x0` version `v3` to the `n13` directory. `jevents.py` generates the event table from this file, and perf exposes the aliases for the matching N13 PMU.

## State, Dependencies, Risks, And Tests
The file is static input. Dependencies are NDS32 support in perf, the mapfile entry, kernel PMU exposure, and hardware-correct event codes. Risks include architecture bitrot, event-code transcription errors, and ambiguous brief descriptions for events whose precise semantics matter to performance diagnosis. Test signals include JSON validity, NDS32 `jevents.py` generation, generated C table inspection, and hardware or emulator `perf list` validation when available.

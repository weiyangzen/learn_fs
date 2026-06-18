# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/datasource.json

## Purpose
This 367-entry POWER10 datasource file is the largest table in this work item. It enumerates where instruction and data cache reloads came from: L1/L2/L3, local and remote memory, on-chip/off-chip cache, local/remote/distant regions, regent/non-regent sources, conflict/no-conflict/MEPF cases, and marked-instruction variants. Prefix analysis shows 129 `PM_DATA_FROM...`, 126 `PM_MRK_DATA...`, 53 `PM_INST_FROM...`, and 52 `PM_MRK_INST...` events.

## Important Data Fields
Rows use `EventCode`, `EventName`, and `BriefDescription`. Encodings range from compact values such as `0x1505E` for `PM_LD_HIT_L1` to wide POWER10 selector encodings such as `0x095840000020C142` for `PM_MRK_DATA_FROM_ANY_MEMORY_ALL`.

## Control Flow And Integration
The PowerPC mapfile selects this file through the POWER10 directory. `jevents.py` parses the long hex event-code strings and emits generated C rows. Runtime perf users can count source-attribution events directly or use them as building blocks for memory hierarchy and marked-instruction analysis.

## State, Dependencies, Risks, And Tests
The file is static but high-risk due to size and encoding complexity. Dependencies are POWER10 PMU selector semantics, generated-code handling for wide hex values, and consistency between marked and unmarked event families. Risks include copy/paste mistakes, inconsistent `_ALL` variants, near-duplicate descriptions masking different encodings, and generated output size. Test signals include JSON validity, full PowerPC `jevents.py` generation, generated table spot checks for first/last and marked/unmarked pairs, and hardware sanity checks under local/remote memory pressure.

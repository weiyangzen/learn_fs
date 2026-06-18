# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/marked.json

## Purpose
This 54-entry POWER10 marked-instruction file defines events for PMU-marked instruction issue, decode, dispatch, completion, flush, transfer-source PMC events, marked branch/cache/TLB/load/store behavior, marked STCX/LARX/TLBIE, and marked data-source misses.

## Important Data Fields
Rows use `EventCode`, `EventName`, and `BriefDescription`. Event names are consistently prefixed with `PM_MRK_`, making the table a focused bridge between ordinary counting and sampled/marked instruction analysis. The first row is `PM_MRK_INST_ISSUED`; the last is `PM_MRK_DATA_FROM_L2MISS`.

## Control Flow And Integration
`jevents.py` emits the table into POWER10 generated events. Runtime integration is through perf's marked-event support and workflows that correlate marked instruction samples with memory hierarchy, branch, and synchronization behavior.

## State, Dependencies, Risks, And Tests
The file is static. Dependencies include POWER10 marked-instruction PMU semantics and consistency with `datasource.json`, where many marked source-attribution variants also exist. Risks include duplication or semantic drift between marked tables, event-code transcription errors, and misleading analysis if marked sampling configuration is not active. Test signals include generated alias checks, sampling/counting comparisons, and POWER10 marked-instruction workload tests.

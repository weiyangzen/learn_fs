# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/clearwaterforest/pipeline.json

Purpose: Defines 15 Clearwater Forest pipeline and topdown PMU aliases for perf. The file covers retired branches, mispredicted retired branches, core and reference cycles, instructions retired, and topdown slot categories for bad speculation, backend bound, frontend bound, and retiring.

Important APIs/types/functions: The schema fields are `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Fixed-counter aliases include `INST_RETIRED.ANY` on fixed counter 0, `CPU_CLK_UNHALTED.CORE`/`THREAD` on fixed counter 1, and `CPU_CLK_UNHALTED.REF_TSC` on fixed counter 2. Programmable aliases include `BR_INST_RETIRED.ALL_BRANCHES` (`0xc4`), `BR_MISP_RETIRED.ALL_BRANCHES` (`0xc5`), `CPU_CLK_UNHALTED.*_P` (`0x3c`), `INST_RETIRED.ANY_P` (`0xc0`), and `TOPDOWN_BE_BOUND.ALL(_P)` (`0xa4/0x2`). Topdown fixed slots use counters 36, 37, and 38 for bad speculation, frontend bound, and retiring.

Control flow: `jevents.py` generates the Clearwater Forest pipeline aliases and preserves fixed-counter names as aliases without ordinary event codes where applicable. At runtime, perf resolves the `_P` forms to programmable counters and the non-`_P` fixed forms to fixed or topdown counters. Alias descriptions document equivalences such as `CPU_CLK_UNHALTED.CORE_P` being an alias of `THREAD_P` and `TOPDOWN_BE_BOUND.ALL` being an alias of `ALL_P`.

State and persistence behavior: The file is static metadata. Hardware state is per-core counting of retired branches/instructions, unhalted cycles, and topdown slot categories. Fixed counters have dedicated hardware resources, while programmable versions compete for the general counter pool declared in `counter.json`.

Dependencies: Depends on Clearwater Forest PMU support for fixed counters, topdown counters, and programmable event encodings. The topdown rows must stay consistent with `counter.json` because counters 36 through 38 are outside the classic fixed-counter 0 through 2 range. Perf's generated alias layer must preserve rows without `EventCode` for fixed counters.

Integration points: Integrates with every other Clearwater Forest topic as the high-level performance context. Cache, memory, virtual-memory, and frontend events can explain whether backend, frontend, speculation, or retiring topdown slots dominate. Branch retired and mispredict retired events provide branch-mispredict rates and help interpret bad-speculation slots.

Risks: Alias duplication can confuse users: core/thread cycle aliases and topdown backend-bound aliases map to equivalent hardware events. Fixed topdown counter numbering is unusual and must match kernel PMU exposure. Rows without `EventCode` rely on perf's fixed-counter handling; generic validators may flag them incorrectly. Branch descriptions include a typo in "resteered" but the semantics are clear.

Test signals: JSON parsing and `jevents.py` generation must keep both fixed and programmable aliases. `perf list` should show fixed cycle/instruction/topdown names and programmable `_P` variants. On hardware, sanity checks should confirm IPC from instructions/cycles, branch miss ratio from branch rows, and topdown categories responding to frontend-bound, backend-bound, and branch-mispredict workloads.

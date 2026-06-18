# subset-b-006617 research

Grouped research report for perf PMU event JSON files. Each section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/pmc.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/pmc.json

## Purpose
This JSON file is a PMU event table for `power9` under the `powerpc` perf PMU event tree. It provides topic-scoped raw event aliases for powerpc power9 `pmc` counters. It contains 23 entries and belongs to the `pmc` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x10026..0x4f148.
- Representative names: PM_BR_2PATH, PM_MEM_LOC_THRESH_LSU_HIGH, PM_MRK_DCACHE_RELOAD_INTV, PM_MRK_DPTEG_FROM_DL2L3_MOD, PM_THRESH_EXC_64, PM_DPTEG_FROM_L3MISS, PM_SYS_PUMP_MPRED_RTY, PM_MRK_DPTEG_FROM_L2MISS, PM_CMPLU_STALL_BRU, PM_4FLOP_CMPL.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- Power9 `pmc` contributes IBM PMU event mnemonics such as PM_BR_2PATH, PM_MEM_LOC_THRESH_LSU_HIGH, PM_MRK_DCACHE_RELOAD_INTV, PM_MRK_DPTEG_FROM_DL2L3_MOD, PM_THRESH_EXC_64, PM_DPTEG_FROM_L3MISS, PM_SYS_PUMP_MPRED_RTY, PM_MRK_DPTEG_FROM_L2MISS.
- The file focuses on PMC-threshold and marked-event samples, including pump retry and memory locality threshold signals.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/powerpc/mapfile.csv maps PVR 0x004e... to the power9 directory as core PMU events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.
- Power event names are uppercase IBM PMU mnemonics; tests should preserve case and hex strings because user-facing perf aliases are generated from them.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/pmc.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/translation.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/translation.json

## Purpose
This JSON file is a PMU event table for `power9` under the `powerpc` perf PMU event tree. It provides topic-scoped raw event aliases for powerpc power9 `translation` counters. It contains 45 entries and belongs to the `translation` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x1e..0x4e05c.
- Representative names: PM_CYC, PM_PMC2_OVERFLOW, PM_DATA_FROM_L21_SHR, PM_DP_QP_FLOP_CMPL, PM_DPTEG_FROM_DMEM, PM_ST_FIN, PM_IPTEG_FROM_RL2L3_SHR, PM_MRK_LSU_FIN, PM_CMPLU_STALL_VFXU, PM_LSU_FIN.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- Power9 `translation` contributes IBM PMU event mnemonics such as PM_CYC, PM_PMC2_OVERFLOW, PM_DATA_FROM_L21_SHR, PM_DP_QP_FLOP_CMPL, PM_DPTEG_FROM_DMEM, PM_ST_FIN, PM_IPTEG_FROM_RL2L3_SHR, PM_MRK_LSU_FIN.
- The file emphasizes translation/data-source aliases, including PM_CYC and LSU/IPTEG/DPTEG source events used for memory hierarchy attribution.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/powerpc/mapfile.csv maps PVR 0x004e... to the power9 directory as core PMU events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.
- Power event names are uppercase IBM PMU mnemonics; tests should preserve case and hex strings because user-facing perf aliases are generated from them.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/translation.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/andes/ax45/firmware.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/andes/ax45/firmware.json

## Purpose
This JSON file is a architecture-standard alias table for `andes/ax45` under the `riscv` perf PMU event tree. It provides model-local references to RISC-V architecture standard firmware events declared in the architecture root. It contains 22 entries and belongs to the `firmware` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `ArchStdEvent`.
- Encoding summary: No local numeric event code field; entries dereference or compute from other event definitions..
- Representative names: FW_MISALIGNED_LOAD, FW_MISALIGNED_STORE, FW_ACCESS_LOAD, FW_ACCESS_STORE, FW_ILLEGAL_INSN, FW_SET_TIMER, FW_IPI_SENT, FW_IPI_RECEIVED, FW_FENCE_I_SENT, FW_FENCE_I_RECEIVED.
- `ArchStdEvent` is a dereference key, not a standalone event definition; generation resolves it against architecture standard events by `EventName`.

## Content Notes
- The file contains 22 bare `ArchStdEvent` references; descriptions and config codes are inherited from the RISC-V root standard firmware table.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

For this file the main control-flow branch is architecture-standard resolution: the local entry names a firmware standard event, and the generator copies the canonical root definition into the model table.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.
- `jevents.py` resolves each `ArchStdEvent` through architecture-root standard events by matching `EventName`

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Every reference must match an architecture-root standard event; a typo fails at generation or silently drops expected firmware aliases depending on validation path.
- These model files intentionally duplicate the same SBI firmware reference list; consistency with `riscv-sbi-firmware.json` matters more than local descriptions.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Check every `ArchStdEvent` resolves to a root RISC-V standard event by `EventName`.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/andes/ax45/firmware.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/andes/ax45/instructions.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/andes/ax45/instructions.json

## Purpose
This JSON file is a PMU event table for `andes/ax45` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv andes/ax45 `instructions` counters. It contains 25 entries and belongs to the `instructions` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x10..0x190.
- Representative names: cycle_count, inst_count, int_load_inst, int_store_inst, atomic_inst, sys_inst, int_compute_inst, condition_br, taken_condition_br, jal_inst.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The andes/ax45 `instructions` table defines model-specific aliases such as cycle_count, inst_count, int_load_inst, int_store_inst, atomic_inst, sys_inst, int_compute_inst, condition_br.
- Andes AX45 events use lower-case event aliases and encode cache, TLB, bus, unaligned-access, branch, and retire class counters.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/andes/ax45/instructions.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/andes/ax45/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/andes/ax45/memory.json

## Purpose
This JSON file is a PMU event table for `andes/ax45` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv andes/ax45 `memory` counters. It contains 11 entries and belongs to the `memory` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x1..0xa1.
- Representative names: ilm_access, dlm_access, icache_access, icache_miss, dcache_access, dcache_miss, dcache_load_access, dcache_load_miss, dcache_store_access, dcache_store_miss.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The andes/ax45 `memory` table defines model-specific aliases such as ilm_access, dlm_access, icache_access, icache_miss, dcache_access, dcache_miss, dcache_load_access, dcache_load_miss.
- Andes AX45 events use lower-case event aliases and encode cache, TLB, bus, unaligned-access, branch, and retire class counters.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/andes/ax45/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/andes/ax45/microarch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/andes/ax45/microarch.json

## Purpose
This JSON file is a PMU event table for `andes/ax45` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv andes/ax45 `microarch` counters. It contains 15 entries and belongs to the `microarch` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x2..0x161.
- Representative names: cycle_wait_icache_fill, cycle_wait_dcache_fill, uncached_ifetch_from_bus, uncached_load_from_bus, cycle_wait_uncached_ifetch, cycle_wait_uncached_load, main_itlb_access, main_itlb_miss, main_dtlb_access, main_dtlb_miss.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The andes/ax45 `microarch` table defines model-specific aliases such as cycle_wait_icache_fill, cycle_wait_dcache_fill, uncached_ifetch_from_bus, uncached_load_from_bus, cycle_wait_uncached_ifetch, cycle_wait_uncached_load, main_itlb_access, main_itlb_miss.
- Andes AX45 events use lower-case event aliases and encode cache, TLB, bus, unaligned-access, branch, and retire class counters.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/andes/ax45/microarch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/openhwgroup/cva6/firmware.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/openhwgroup/cva6/firmware.json

## Purpose
This JSON file is a architecture-standard alias table for `openhwgroup/cva6` under the `riscv` perf PMU event tree. It provides model-local references to RISC-V architecture standard firmware events declared in the architecture root. It contains 22 entries and belongs to the `firmware` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `ArchStdEvent`.
- Encoding summary: No local numeric event code field; entries dereference or compute from other event definitions..
- Representative names: FW_MISALIGNED_LOAD, FW_MISALIGNED_STORE, FW_ACCESS_LOAD, FW_ACCESS_STORE, FW_ILLEGAL_INSN, FW_SET_TIMER, FW_IPI_SENT, FW_IPI_RECEIVED, FW_FENCE_I_SENT, FW_FENCE_I_RECEIVED.
- `ArchStdEvent` is a dereference key, not a standalone event definition; generation resolves it against architecture standard events by `EventName`.

## Content Notes
- The file contains 22 bare `ArchStdEvent` references; descriptions and config codes are inherited from the RISC-V root standard firmware table.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

For this file the main control-flow branch is architecture-standard resolution: the local entry names a firmware standard event, and the generator copies the canonical root definition into the model table.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.
- `jevents.py` resolves each `ArchStdEvent` through architecture-root standard events by matching `EventName`

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Every reference must match an architecture-root standard event; a typo fails at generation or silently drops expected firmware aliases depending on validation path.
- These model files intentionally duplicate the same SBI firmware reference list; consistency with `riscv-sbi-firmware.json` matters more than local descriptions.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Check every `ArchStdEvent` resolves to a root RISC-V standard event by `EventName`.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/openhwgroup/cva6/firmware.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/openhwgroup/cva6/instructions.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/openhwgroup/cva6/instructions.json

## Purpose
This JSON file is a PMU event table for `openhwgroup/cva6` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv openhwgroup/cva6 `instructions` counters. It contains 9 entries and belongs to the `instructions` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x5..0x15.
- Representative names: LOAD_INSTRUCTIONS_RETIRED, STORE_INSTRUCTIONS_RETIRED, EXCEPTIONS, EXCEPTION_HANDLER_RETURNS, BRANCH_INSTRUCTIONS_RETIRED, CALL_INSTRUCTIONS_RETIRED, RETURN_INSTRUCTIONS_RETIRED, INTEGER_INSTRUCTIONS_RETIRED, FLOATING_POINT_INSTRUCTIONS_RETIRED.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The openhwgroup/cva6 `instructions` table defines model-specific aliases such as LOAD_INSTRUCTIONS_RETIRED, STORE_INSTRUCTIONS_RETIRED, EXCEPTIONS, EXCEPTION_HANDLER_RETURNS, BRANCH_INSTRUCTIONS_RETIRED, CALL_INSTRUCTIONS_RETIRED, RETURN_INSTRUCTIONS_RETIRED, INTEGER_INSTRUCTIONS_RETIRED.
- CVA6 events are compact uppercase aliases for retired instruction classes, L1/TLB counters, and core pipeline conditions.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/openhwgroup/cva6/instructions.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/openhwgroup/cva6/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/openhwgroup/cva6/memory.json

## Purpose
This JSON file is a PMU event table for `openhwgroup/cva6` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv openhwgroup/cva6 `memory` counters. It contains 8 entries and belongs to the `memory` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x1..0x13.
- Representative names: L1_I_CACHE_MISSES, L1_D_CACHE_MISSES, ITLB_MISSES, DTLB_MISSES, L1_I_CACHE_ACCESSES, L1_D_CACHE_ACCESSES, L1_CACHE_LINE_EVICTION, ITLB_FLUSH.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The openhwgroup/cva6 `memory` table defines model-specific aliases such as L1_I_CACHE_MISSES, L1_D_CACHE_MISSES, ITLB_MISSES, DTLB_MISSES, L1_I_CACHE_ACCESSES, L1_D_CACHE_ACCESSES, L1_CACHE_LINE_EVICTION, ITLB_FLUSH.
- CVA6 events are compact uppercase aliases for retired instruction classes, L1/TLB counters, and core pipeline conditions.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/openhwgroup/cva6/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/openhwgroup/cva6/microarch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/openhwgroup/cva6/microarch.json

## Purpose
This JSON file is a PMU event table for `openhwgroup/cva6` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv openhwgroup/cva6 `microarch` counters. It contains 5 entries and belongs to the `microarch` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0xa..0x16.
- Representative names: BRANCH_MISPREDICTS, BRANCH_EXCEPTIONS, MSB_FULL, INSTRUCTION_FETCH_EMPTY, PIPELINE_STALL.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The openhwgroup/cva6 `microarch` table defines model-specific aliases such as BRANCH_MISPREDICTS, BRANCH_EXCEPTIONS, MSB_FULL, INSTRUCTION_FETCH_EMPTY, PIPELINE_STALL.
- CVA6 events are compact uppercase aliases for retired instruction classes, L1/TLB counters, and core pipeline conditions.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/openhwgroup/cva6/microarch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/riscv-sbi-firmware.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/riscv-sbi-firmware.json

## Purpose
This JSON file is a architecture-standard firmware event table for `` under the `riscv` perf PMU event tree. It provides RISC-V SBI firmware event definitions with 64-bit config encodings. It contains 22 entries and belongs to the `riscv-sbi-firmware` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, ConfigCode, EventName, PublicDescription`.
- Encoding summary: ConfigCode range 0x8000000000000000..0x8000000000000015.
- Representative names: FW_MISALIGNED_LOAD, FW_MISALIGNED_STORE, FW_ACCESS_LOAD, FW_ACCESS_STORE, FW_ILLEGAL_INSN, FW_SET_TIMER, FW_IPI_SENT, FW_IPI_RECEIVED, FW_FENCE_I_SENT, FW_FENCE_I_RECEIVED.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `PublicDescription` supplies longer help text when available; `jevents.py` normalizes it into the generated long description field.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `ConfigCode` is the RISC-V firmware event selector; these values have ABI significance for SBI firmware counters.

## Content Notes
- The root standard table assigns SBI firmware events to high-bit config values 0x8000000000000000 through 0x8000000000000015.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/riscv-sbi-firmware.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-07/cycle-and-instruction-count.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-07/cycle-and-instruction-count.json

## Purpose
This JSON file is a PMU event table for `sifive/bullet-07` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv sifive/bullet-07 `cycle-and-instruction-count` counters. It contains 2 entries and belongs to the `cycle-and-instruction-count` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x165..0x265.
- Representative names: CORE_CLOCK_CYCLES, INSTRUCTIONS_RETIRED.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The sifive/bullet-07 `cycle-and-instruction-count` table defines model-specific aliases such as CORE_CLOCK_CYCLES, INSTRUCTIONS_RETIRED.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-07/cycle-and-instruction-count.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-07/firmware.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-07/firmware.json

## Purpose
This JSON file is a architecture-standard alias table for `sifive/bullet-07` under the `riscv` perf PMU event tree. It provides model-local references to RISC-V architecture standard firmware events declared in the architecture root. It contains 22 entries and belongs to the `firmware` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `ArchStdEvent`.
- Encoding summary: No local numeric event code field; entries dereference or compute from other event definitions..
- Representative names: FW_MISALIGNED_LOAD, FW_MISALIGNED_STORE, FW_ACCESS_LOAD, FW_ACCESS_STORE, FW_ILLEGAL_INSN, FW_SET_TIMER, FW_IPI_SENT, FW_IPI_RECEIVED, FW_FENCE_I_SENT, FW_FENCE_I_RECEIVED.
- `ArchStdEvent` is a dereference key, not a standalone event definition; generation resolves it against architecture standard events by `EventName`.

## Content Notes
- The file contains 22 bare `ArchStdEvent` references; descriptions and config codes are inherited from the RISC-V root standard firmware table.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

For this file the main control-flow branch is architecture-standard resolution: the local entry names a firmware standard event, and the generator copies the canonical root definition into the model table.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.
- `jevents.py` resolves each `ArchStdEvent` through architecture-root standard events by matching `EventName`

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Every reference must match an architecture-root standard event; a typo fails at generation or silently drops expected firmware aliases depending on validation path.
- These model files intentionally duplicate the same SBI firmware reference list; consistency with `riscv-sbi-firmware.json` matters more than local descriptions.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Check every `ArchStdEvent` resolves to a root RISC-V standard event by `EventName`.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-07/firmware.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-07/instruction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-07/instruction.json

## Purpose
This JSON file is a PMU event table for `sifive/bullet-07` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv sifive/bullet-07 `instruction` counters. It contains 18 entries and belongs to the `instruction` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x100..0x2000000.
- Representative names: EXCEPTION_TAKEN, INTEGER_LOAD_RETIRED, INTEGER_STORE_RETIRED, ATOMIC_MEMORY_RETIRED, SYSTEM_INSTRUCTION_RETIRED, INTEGER_ARITHMETIC_RETIRED, CONDITIONAL_BRANCH_RETIRED, JAL_INSTRUCTION_RETIRED, JALR_INSTRUCTION_RETIRED, INTEGER_MULTIPLICATION_RETIRED.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The sifive/bullet-07 `instruction` table defines model-specific aliases such as EXCEPTION_TAKEN, INTEGER_LOAD_RETIRED, INTEGER_STORE_RETIRED, ATOMIC_MEMORY_RETIRED, SYSTEM_INSTRUCTION_RETIRED, INTEGER_ARITHMETIC_RETIRED, CONDITIONAL_BRANCH_RETIRED, JAL_INSTRUCTION_RETIRED.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-07/instruction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-07/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-07/memory.json

## Purpose
This JSON file is a PMU event table for `sifive/bullet-07` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv sifive/bullet-07 `memory` counters. It contains 6 entries and belongs to the `memory` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x102..0x2002.
- Representative names: ICACHE_MISS, DCACHE_MISS, DCACHE_RELEASE, ITLB_MISS, DTLB_MISS, UTLB_MISS.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The sifive/bullet-07 `memory` table defines model-specific aliases such as ICACHE_MISS, DCACHE_MISS, DCACHE_RELEASE, ITLB_MISS, DTLB_MISS, UTLB_MISS.
- SiFive memory tables share core I-cache, D-cache, TLB, and UTLB names; P550/P650 add PTE cache and multi-hit counters compared with smaller Bullet variants.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-07/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-07/microarch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-07/microarch.json

## Purpose
This JSON file is a PMU event table for `sifive/bullet-07` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv sifive/bullet-07 `microarch` counters. It contains 12 entries and belongs to the `microarch` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x101..0x80001.
- Representative names: ADDRESSGEN_INTERLOCK, LONGLATENCY_INTERLOCK, CSR_INTERLOCK, ICACHE_BLOCKED, DCACHE_BLOCKED, BRANCH_DIRECTION_MISPREDICTION, BRANCH_TARGET_MISPREDICTION, PIPELINE_FLUSH, REPLAY, INTEGER_MUL_DIV_INTERLOCK.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The sifive/bullet-07 `microarch` table defines model-specific aliases such as ADDRESSGEN_INTERLOCK, LONGLATENCY_INTERLOCK, CSR_INTERLOCK, ICACHE_BLOCKED, DCACHE_BLOCKED, BRANCH_DIRECTION_MISPREDICTION, BRANCH_TARGET_MISPREDICTION, PIPELINE_FLUSH.
- SiFive microarchitecture tables encode interlock, blocked-cache, branch-prediction, flush, replay, and release-event conditions with model-specific additions.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-07/microarch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-07/watchpoint.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-07/watchpoint.json

## Purpose
This JSON file is a PMU event table for `sifive/bullet-07` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv sifive/bullet-07 `watchpoint` counters. It contains 8 entries and belongs to the `watchpoint` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x164..0x8064.
- Representative names: WATCHPOINT_0, WATCHPOINT_1, WATCHPOINT_2, WATCHPOINT_3, WATCHPOINT_4, WATCHPOINT_5, WATCHPOINT_6, WATCHPOINT_7.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The sifive/bullet-07 `watchpoint` table defines model-specific aliases such as WATCHPOINT_0, WATCHPOINT_1, WATCHPOINT_2, WATCHPOINT_3, WATCHPOINT_4, WATCHPOINT_5, WATCHPOINT_6, WATCHPOINT_7.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-07/watchpoint.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-0d/cycle-and-instruction-count.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-0d/cycle-and-instruction-count.json

## Purpose
This JSON file is a PMU event table for `sifive/bullet-0d` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv sifive/bullet-0d `cycle-and-instruction-count` counters. It contains 2 entries and belongs to the `cycle-and-instruction-count` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x165..0x265.
- Representative names: CORE_CLOCK_CYCLES, INSTRUCTIONS_RETIRED.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The sifive/bullet-0d `cycle-and-instruction-count` table defines model-specific aliases such as CORE_CLOCK_CYCLES, INSTRUCTIONS_RETIRED.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-0d/cycle-and-instruction-count.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-0d/firmware.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-0d/firmware.json

## Purpose
This JSON file is a architecture-standard alias table for `sifive/bullet-0d` under the `riscv` perf PMU event tree. It provides model-local references to RISC-V architecture standard firmware events declared in the architecture root. It contains 22 entries and belongs to the `firmware` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `ArchStdEvent`.
- Encoding summary: No local numeric event code field; entries dereference or compute from other event definitions..
- Representative names: FW_MISALIGNED_LOAD, FW_MISALIGNED_STORE, FW_ACCESS_LOAD, FW_ACCESS_STORE, FW_ILLEGAL_INSN, FW_SET_TIMER, FW_IPI_SENT, FW_IPI_RECEIVED, FW_FENCE_I_SENT, FW_FENCE_I_RECEIVED.
- `ArchStdEvent` is a dereference key, not a standalone event definition; generation resolves it against architecture standard events by `EventName`.

## Content Notes
- The file contains 22 bare `ArchStdEvent` references; descriptions and config codes are inherited from the RISC-V root standard firmware table.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

For this file the main control-flow branch is architecture-standard resolution: the local entry names a firmware standard event, and the generator copies the canonical root definition into the model table.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.
- `jevents.py` resolves each `ArchStdEvent` through architecture-root standard events by matching `EventName`

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Every reference must match an architecture-root standard event; a typo fails at generation or silently drops expected firmware aliases depending on validation path.
- These model files intentionally duplicate the same SBI firmware reference list; consistency with `riscv-sbi-firmware.json` matters more than local descriptions.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Check every `ArchStdEvent` resolves to a root RISC-V standard event by `EventName`.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-0d/firmware.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-0d/instruction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-0d/instruction.json

## Purpose
This JSON file is a PMU event table for `sifive/bullet-0d` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv sifive/bullet-0d `instruction` counters. It contains 18 entries and belongs to the `instruction` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x100..0x2000000.
- Representative names: EXCEPTION_TAKEN, INTEGER_LOAD_RETIRED, INTEGER_STORE_RETIRED, ATOMIC_MEMORY_RETIRED, SYSTEM_INSTRUCTION_RETIRED, INTEGER_ARITHMETIC_RETIRED, CONDITIONAL_BRANCH_RETIRED, JAL_INSTRUCTION_RETIRED, JALR_INSTRUCTION_RETIRED, INTEGER_MULTIPLICATION_RETIRED.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The sifive/bullet-0d `instruction` table defines model-specific aliases such as EXCEPTION_TAKEN, INTEGER_LOAD_RETIRED, INTEGER_STORE_RETIRED, ATOMIC_MEMORY_RETIRED, SYSTEM_INSTRUCTION_RETIRED, INTEGER_ARITHMETIC_RETIRED, CONDITIONAL_BRANCH_RETIRED, JAL_INSTRUCTION_RETIRED.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-0d/instruction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-0d/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-0d/memory.json

## Purpose
This JSON file is a PMU event table for `sifive/bullet-0d` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv sifive/bullet-0d `memory` counters. It contains 6 entries and belongs to the `memory` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x102..0x2002.
- Representative names: ICACHE_MISS, DCACHE_MISS, DCACHE_RELEASE, ITLB_MISS, DTLB_MISS, UTLB_MISS.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The sifive/bullet-0d `memory` table defines model-specific aliases such as ICACHE_MISS, DCACHE_MISS, DCACHE_RELEASE, ITLB_MISS, DTLB_MISS, UTLB_MISS.
- SiFive memory tables share core I-cache, D-cache, TLB, and UTLB names; P550/P650 add PTE cache and multi-hit counters compared with smaller Bullet variants.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-0d/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-0d/microarch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-0d/microarch.json

## Purpose
This JSON file is a PMU event table for `sifive/bullet-0d` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv sifive/bullet-0d `microarch` counters. It contains 14 entries and belongs to the `microarch` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x101..0x200001.
- Representative names: ADDRESSGEN_INTERLOCK, LONGLATENCY_INTERLOCK, CSR_INTERLOCK, ICACHE_BLOCKED, DCACHE_BLOCKED, BRANCH_DIRECTION_MISPREDICTION, BRANCH_TARGET_MISPREDICTION, PIPELINE_FLUSH, REPLAY, INTEGER_MUL_DIV_INTERLOCK.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The sifive/bullet-0d `microarch` table defines model-specific aliases such as ADDRESSGEN_INTERLOCK, LONGLATENCY_INTERLOCK, CSR_INTERLOCK, ICACHE_BLOCKED, DCACHE_BLOCKED, BRANCH_DIRECTION_MISPREDICTION, BRANCH_TARGET_MISPREDICTION, PIPELINE_FLUSH.
- SiFive microarchitecture tables encode interlock, blocked-cache, branch-prediction, flush, replay, and release-event conditions with model-specific additions.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-0d/microarch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-0d/watchpoint.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-0d/watchpoint.json

## Purpose
This JSON file is a PMU event table for `sifive/bullet-0d` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv sifive/bullet-0d `watchpoint` counters. It contains 8 entries and belongs to the `watchpoint` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x164..0x8064.
- Representative names: WATCHPOINT_0, WATCHPOINT_1, WATCHPOINT_2, WATCHPOINT_3, WATCHPOINT_4, WATCHPOINT_5, WATCHPOINT_6, WATCHPOINT_7.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The sifive/bullet-0d `watchpoint` table defines model-specific aliases such as WATCHPOINT_0, WATCHPOINT_1, WATCHPOINT_2, WATCHPOINT_3, WATCHPOINT_4, WATCHPOINT_5, WATCHPOINT_6, WATCHPOINT_7.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet-0d/watchpoint.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet/firmware.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet/firmware.json

## Purpose
This JSON file is a architecture-standard alias table for `sifive/bullet` under the `riscv` perf PMU event tree. It provides model-local references to RISC-V architecture standard firmware events declared in the architecture root. It contains 22 entries and belongs to the `firmware` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `ArchStdEvent`.
- Encoding summary: No local numeric event code field; entries dereference or compute from other event definitions..
- Representative names: FW_MISALIGNED_LOAD, FW_MISALIGNED_STORE, FW_ACCESS_LOAD, FW_ACCESS_STORE, FW_ILLEGAL_INSN, FW_SET_TIMER, FW_IPI_SENT, FW_IPI_RECEIVED, FW_FENCE_I_SENT, FW_FENCE_I_RECEIVED.
- `ArchStdEvent` is a dereference key, not a standalone event definition; generation resolves it against architecture standard events by `EventName`.

## Content Notes
- The file contains 22 bare `ArchStdEvent` references; descriptions and config codes are inherited from the RISC-V root standard firmware table.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

For this file the main control-flow branch is architecture-standard resolution: the local entry names a firmware standard event, and the generator copies the canonical root definition into the model table.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.
- `jevents.py` resolves each `ArchStdEvent` through architecture-root standard events by matching `EventName`

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Every reference must match an architecture-root standard event; a typo fails at generation or silently drops expected firmware aliases depending on validation path.
- These model files intentionally duplicate the same SBI firmware reference list; consistency with `riscv-sbi-firmware.json` matters more than local descriptions.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Check every `ArchStdEvent` resolves to a root RISC-V standard event by `EventName`.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet/firmware.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet/instruction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet/instruction.json

## Purpose
This JSON file is a PMU event table for `sifive/bullet` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv sifive/bullet `instruction` counters. It contains 18 entries and belongs to the `instruction` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x100..0x2000000.
- Representative names: EXCEPTION_TAKEN, INTEGER_LOAD_RETIRED, INTEGER_STORE_RETIRED, ATOMIC_MEMORY_RETIRED, SYSTEM_INSTRUCTION_RETIRED, INTEGER_ARITHMETIC_RETIRED, CONDITIONAL_BRANCH_RETIRED, JAL_INSTRUCTION_RETIRED, JALR_INSTRUCTION_RETIRED, INTEGER_MULTIPLICATION_RETIRED.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The sifive/bullet `instruction` table defines model-specific aliases such as EXCEPTION_TAKEN, INTEGER_LOAD_RETIRED, INTEGER_STORE_RETIRED, ATOMIC_MEMORY_RETIRED, SYSTEM_INSTRUCTION_RETIRED, INTEGER_ARITHMETIC_RETIRED, CONDITIONAL_BRANCH_RETIRED, JAL_INSTRUCTION_RETIRED.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet/instruction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet/memory.json

## Purpose
This JSON file is a PMU event table for `sifive/bullet` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv sifive/bullet `memory` counters. It contains 6 entries and belongs to the `memory` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x102..0x2002.
- Representative names: ICACHE_MISS, DCACHE_MISS, DCACHE_RELEASE, ITLB_MISS, DTLB_MISS, UTLB_MISS.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The sifive/bullet `memory` table defines model-specific aliases such as ICACHE_MISS, DCACHE_MISS, DCACHE_RELEASE, ITLB_MISS, DTLB_MISS, UTLB_MISS.
- SiFive memory tables share core I-cache, D-cache, TLB, and UTLB names; P550/P650 add PTE cache and multi-hit counters compared with smaller Bullet variants.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet/microarch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet/microarch.json

## Purpose
This JSON file is a PMU event table for `sifive/bullet` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv sifive/bullet `microarch` counters. It contains 11 entries and belongs to the `microarch` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x101..0x40001.
- Representative names: ADDRESSGEN_INTERLOCK, LONGLATENCY_INTERLOCK, CSR_INTERLOCK, ICACHE_BLOCKED, DCACHE_BLOCKED, BRANCH_DIRECTION_MISPREDICTION, BRANCH_TARGET_MISPREDICTION, PIPELINE_FLUSH, REPLAY, INTEGER_MUL_DIV_INTERLOCK.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The sifive/bullet `microarch` table defines model-specific aliases such as ADDRESSGEN_INTERLOCK, LONGLATENCY_INTERLOCK, CSR_INTERLOCK, ICACHE_BLOCKED, DCACHE_BLOCKED, BRANCH_DIRECTION_MISPREDICTION, BRANCH_TARGET_MISPREDICTION, PIPELINE_FLUSH.
- SiFive microarchitecture tables encode interlock, blocked-cache, branch-prediction, flush, replay, and release-event conditions with model-specific additions.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/bullet/microarch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p550/firmware.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p550/firmware.json

## Purpose
This JSON file is a architecture-standard alias table for `sifive/p550` under the `riscv` perf PMU event tree. It provides model-local references to RISC-V architecture standard firmware events declared in the architecture root. It contains 22 entries and belongs to the `firmware` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `ArchStdEvent`.
- Encoding summary: No local numeric event code field; entries dereference or compute from other event definitions..
- Representative names: FW_MISALIGNED_LOAD, FW_MISALIGNED_STORE, FW_ACCESS_LOAD, FW_ACCESS_STORE, FW_ILLEGAL_INSN, FW_SET_TIMER, FW_IPI_SENT, FW_IPI_RECEIVED, FW_FENCE_I_SENT, FW_FENCE_I_RECEIVED.
- `ArchStdEvent` is a dereference key, not a standalone event definition; generation resolves it against architecture standard events by `EventName`.

## Content Notes
- The file contains 22 bare `ArchStdEvent` references; descriptions and config codes are inherited from the RISC-V root standard firmware table.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

For this file the main control-flow branch is architecture-standard resolution: the local entry names a firmware standard event, and the generator copies the canonical root definition into the model table.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.
- `jevents.py` resolves each `ArchStdEvent` through architecture-root standard events by matching `EventName`

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Every reference must match an architecture-root standard event; a typo fails at generation or silently drops expected firmware aliases depending on validation path.
- These model files intentionally duplicate the same SBI firmware reference list; consistency with `riscv-sbi-firmware.json` matters more than local descriptions.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Check every `ArchStdEvent` resolves to a root RISC-V standard event by `EventName`.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p550/firmware.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p550/instruction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p550/instruction.json

## Purpose
This JSON file is a PMU event table for `sifive/p550` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv sifive/p550 `instruction` counters. It contains 18 entries and belongs to the `instruction` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x100..0x2000000.
- Representative names: EXCEPTION_TAKEN, INTEGER_LOAD_RETIRED, INTEGER_STORE_RETIRED, ATOMIC_MEMORY_RETIRED, SYSTEM_INSTRUCTION_RETIRED, INTEGER_ARITHMETIC_RETIRED, CONDITIONAL_BRANCH_RETIRED, JAL_INSTRUCTION_RETIRED, JALR_INSTRUCTION_RETIRED, INTEGER_MULTIPLICATION_RETIRED.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The sifive/p550 `instruction` table defines model-specific aliases such as EXCEPTION_TAKEN, INTEGER_LOAD_RETIRED, INTEGER_STORE_RETIRED, ATOMIC_MEMORY_RETIRED, SYSTEM_INSTRUCTION_RETIRED, INTEGER_ARITHMETIC_RETIRED, CONDITIONAL_BRANCH_RETIRED, JAL_INSTRUCTION_RETIRED.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p550/instruction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p550/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p550/memory.json

## Purpose
This JSON file is a PMU event table for `sifive/p550` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv sifive/p550 `memory` counters. It contains 9 entries and belongs to the `memory` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x102..0x10002.
- Representative names: ICACHE_MISS, DCACHE_MISS, DCACHE_RELEASE, ITLB_MISS, DTLB_MISS, UTLB_MISS, UTLB_HIT, PTE_CACHE_MISS, PTE_CACHE_HIT.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The sifive/p550 `memory` table defines model-specific aliases such as ICACHE_MISS, DCACHE_MISS, DCACHE_RELEASE, ITLB_MISS, DTLB_MISS, UTLB_MISS, UTLB_HIT, PTE_CACHE_MISS.
- SiFive memory tables share core I-cache, D-cache, TLB, and UTLB names; P550/P650 add PTE cache and multi-hit counters compared with smaller Bullet variants.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p550/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p550/microarch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p550/microarch.json

## Purpose
This JSON file is a PMU event table for `sifive/p550` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv sifive/p550 `microarch` counters. It contains 11 entries and belongs to the `microarch` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x101..0x40001.
- Representative names: ADDRESSGEN_INTERLOCK, LONGLATENCY_INTERLOCK, CSR_INTERLOCK, ICACHE_BLOCKED, DCACHE_BLOCKED, BRANCH_DIRECTION_MISPREDICTION, BRANCH_TARGET_MISPREDICTION, PIPELINE_FLUSH, REPLAY, INTEGER_MUL_DIV_INTERLOCK.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The sifive/p550 `microarch` table defines model-specific aliases such as ADDRESSGEN_INTERLOCK, LONGLATENCY_INTERLOCK, CSR_INTERLOCK, ICACHE_BLOCKED, DCACHE_BLOCKED, BRANCH_DIRECTION_MISPREDICTION, BRANCH_TARGET_MISPREDICTION, PIPELINE_FLUSH.
- SiFive microarchitecture tables encode interlock, blocked-cache, branch-prediction, flush, replay, and release-event conditions with model-specific additions.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p550/microarch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p650/cycle-and-instruction-count.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p650/cycle-and-instruction-count.json

## Purpose
This JSON file is a PMU event table for `sifive/p650` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv sifive/p650 `cycle-and-instruction-count` counters. It contains 2 entries and belongs to the `cycle-and-instruction-count` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x165..0x265.
- Representative names: CORE_CLOCK_CYCLES, INSTRUCTIONS_RETIRED.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The sifive/p650 `cycle-and-instruction-count` table defines model-specific aliases such as CORE_CLOCK_CYCLES, INSTRUCTIONS_RETIRED.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p650/cycle-and-instruction-count.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p650/firmware.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p650/firmware.json

## Purpose
This JSON file is a architecture-standard alias table for `sifive/p650` under the `riscv` perf PMU event tree. It provides model-local references to RISC-V architecture standard firmware events declared in the architecture root. It contains 22 entries and belongs to the `firmware` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `ArchStdEvent`.
- Encoding summary: No local numeric event code field; entries dereference or compute from other event definitions..
- Representative names: FW_MISALIGNED_LOAD, FW_MISALIGNED_STORE, FW_ACCESS_LOAD, FW_ACCESS_STORE, FW_ILLEGAL_INSN, FW_SET_TIMER, FW_IPI_SENT, FW_IPI_RECEIVED, FW_FENCE_I_SENT, FW_FENCE_I_RECEIVED.
- `ArchStdEvent` is a dereference key, not a standalone event definition; generation resolves it against architecture standard events by `EventName`.

## Content Notes
- The file contains 22 bare `ArchStdEvent` references; descriptions and config codes are inherited from the RISC-V root standard firmware table.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

For this file the main control-flow branch is architecture-standard resolution: the local entry names a firmware standard event, and the generator copies the canonical root definition into the model table.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.
- `jevents.py` resolves each `ArchStdEvent` through architecture-root standard events by matching `EventName`

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Every reference must match an architecture-root standard event; a typo fails at generation or silently drops expected firmware aliases depending on validation path.
- These model files intentionally duplicate the same SBI firmware reference list; consistency with `riscv-sbi-firmware.json` matters more than local descriptions.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Check every `ArchStdEvent` resolves to a root RISC-V standard event by `EventName`.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p650/firmware.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p650/instruction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p650/instruction.json

## Purpose
This JSON file is a PMU event table for `sifive/p650` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv sifive/p650 `instruction` counters. It contains 18 entries and belongs to the `instruction` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x100..0x2000000.
- Representative names: EXCEPTION_TAKEN, INTEGER_LOAD_RETIRED, INTEGER_STORE_RETIRED, ATOMIC_MEMORY_RETIRED, SYSTEM_INSTRUCTION_RETIRED, INTEGER_ARITHMETIC_RETIRED, CONDITIONAL_BRANCH_RETIRED, JAL_INSTRUCTION_RETIRED, JALR_INSTRUCTION_RETIRED, INTEGER_MULTIPLICATION_RETIRED.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The sifive/p650 `instruction` table defines model-specific aliases such as EXCEPTION_TAKEN, INTEGER_LOAD_RETIRED, INTEGER_STORE_RETIRED, ATOMIC_MEMORY_RETIRED, SYSTEM_INSTRUCTION_RETIRED, INTEGER_ARITHMETIC_RETIRED, CONDITIONAL_BRANCH_RETIRED, JAL_INSTRUCTION_RETIRED.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p650/instruction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p650/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p650/memory.json

## Purpose
This JSON file is a PMU event table for `sifive/p650` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv sifive/p650 `memory` counters. It contains 11 entries and belongs to the `memory` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x102..0x40002.
- Representative names: ICACHE_MISS, DCACHE_MISS, DCACHE_RELEASE, ITLB_MISS, DTLB_MISS, UTLB_MISS, UTLB_HIT, PTE_CACHE_MISS, PTE_CACHE_HIT, ITLB_MULTI_HIT.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The sifive/p650 `memory` table defines model-specific aliases such as ICACHE_MISS, DCACHE_MISS, DCACHE_RELEASE, ITLB_MISS, DTLB_MISS, UTLB_MISS, UTLB_HIT, PTE_CACHE_MISS.
- SiFive memory tables share core I-cache, D-cache, TLB, and UTLB names; P550/P650 add PTE cache and multi-hit counters compared with smaller Bullet variants.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p650/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p650/microarch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p650/microarch.json

## Purpose
This JSON file is a PMU event table for `sifive/p650` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv sifive/p650 `microarch` counters. It contains 12 entries and belongs to the `microarch` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x101..0x80001.
- Representative names: ADDRESSGEN_INTERLOCK, LONGLATENCY_INTERLOCK, CSR_INTERLOCK, ICACHE_BLOCKED, DCACHE_BLOCKED, BRANCH_DIRECTION_MISPREDICTION, BRANCH_TARGET_MISPREDICTION, PIPELINE_FLUSH, REPLAY, INTEGER_MUL_DIV_INTERLOCK.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The sifive/p650 `microarch` table defines model-specific aliases such as ADDRESSGEN_INTERLOCK, LONGLATENCY_INTERLOCK, CSR_INTERLOCK, ICACHE_BLOCKED, DCACHE_BLOCKED, BRANCH_DIRECTION_MISPREDICTION, BRANCH_TARGET_MISPREDICTION, PIPELINE_FLUSH.
- SiFive microarchitecture tables encode interlock, blocked-cache, branch-prediction, flush, replay, and release-event conditions with model-specific additions.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p650/microarch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p650/watchpoint.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p650/watchpoint.json

## Purpose
This JSON file is a PMU event table for `sifive/p650` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv sifive/p650 `watchpoint` counters. It contains 8 entries and belongs to the `watchpoint` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x164..0x8064.
- Representative names: WATCHPOINT_0, WATCHPOINT_1, WATCHPOINT_2, WATCHPOINT_3, WATCHPOINT_4, WATCHPOINT_5, WATCHPOINT_6, WATCHPOINT_7.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The sifive/p650 `watchpoint` table defines model-specific aliases such as WATCHPOINT_0, WATCHPOINT_1, WATCHPOINT_2, WATCHPOINT_3, WATCHPOINT_4, WATCHPOINT_5, WATCHPOINT_6, WATCHPOINT_7.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/sifive/p650/watchpoint.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/starfive/dubhe-80/common.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/starfive/dubhe-80/common.json

## Purpose
This JSON file is a PMU event table for `starfive/dubhe-80` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv starfive/dubhe-80 `common` counters. It contains 34 entries and belongs to the `common` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x1..0x22.
- Representative names: ACCESS_MMU_STLB, MISS_MMU_STLB, ACCESS_MMU_PTE_C, MISS_MMU_PTE_C, ROB_FLUSH, BTB_PREDICTION_MISS, ITLB_MISS, SYNC_DEL_FETCH_G, ICACHE_MISS, BPU_BR_RETIRE.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The starfive/dubhe-80 `common` table defines model-specific aliases such as ACCESS_MMU_STLB, MISS_MMU_STLB, ACCESS_MMU_PTE_C, MISS_MMU_PTE_C, ROB_FLUSH, BTB_PREDICTION_MISS, ITLB_MISS, SYNC_DEL_FETCH_G.
- StarFive Dubhe common events span several conventional topics in one file instead of splitting instruction, cache, and microarchitecture files.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/starfive/dubhe-80/common.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/starfive/dubhe-80/firmware.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/starfive/dubhe-80/firmware.json

## Purpose
This JSON file is a architecture-standard alias table for `starfive/dubhe-80` under the `riscv` perf PMU event tree. It provides model-local references to RISC-V architecture standard firmware events declared in the architecture root. It contains 22 entries and belongs to the `firmware` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `ArchStdEvent`.
- Encoding summary: No local numeric event code field; entries dereference or compute from other event definitions..
- Representative names: FW_MISALIGNED_LOAD, FW_MISALIGNED_STORE, FW_ACCESS_LOAD, FW_ACCESS_STORE, FW_ILLEGAL_INSN, FW_SET_TIMER, FW_IPI_SENT, FW_IPI_RECEIVED, FW_FENCE_I_SENT, FW_FENCE_I_RECEIVED.
- `ArchStdEvent` is a dereference key, not a standalone event definition; generation resolves it against architecture standard events by `EventName`.

## Content Notes
- The file contains 22 bare `ArchStdEvent` references; descriptions and config codes are inherited from the RISC-V root standard firmware table.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

For this file the main control-flow branch is architecture-standard resolution: the local entry names a firmware standard event, and the generator copies the canonical root definition into the model table.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.
- `jevents.py` resolves each `ArchStdEvent` through architecture-root standard events by matching `EventName`

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Every reference must match an architecture-root standard event; a typo fails at generation or silently drops expected firmware aliases depending on validation path.
- These model files intentionally duplicate the same SBI firmware reference list; consistency with `riscv-sbi-firmware.json` matters more than local descriptions.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Check every `ArchStdEvent` resolves to a root RISC-V standard event by `EventName`.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/starfive/dubhe-80/firmware.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/thead/c900-legacy/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/thead/c900-legacy/cache.json

## Purpose
This JSON file is a PMU event table for `thead/c900-legacy` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv thead/c900-legacy `cache` counters. It contains 13 entries and belongs to the `cache` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x1..0x13.
- Representative names: L1_ICACHE_ACCESS, L1_ICACHE_MISS, ITLB_MISS, DTLB_MISS, JTLB_MISS, L1_DCACHE_READ_ACCESS, L1_DCACHE_READ_MISS, L1_DCACHE_WRITE_ACCESS, L1_DCACHE_WRITE_MISS, LL_CACHE_READ_ACCESS.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The thead/c900-legacy `cache` table defines model-specific aliases such as L1_ICACHE_ACCESS, L1_ICACHE_MISS, ITLB_MISS, DTLB_MISS, JTLB_MISS, L1_DCACHE_READ_ACCESS, L1_DCACHE_READ_MISS, L1_DCACHE_WRITE_ACCESS.
- The T-Head legacy tables use vendor-specific instruction/cache/microarchitecture names and include a PublicDescription only for microarchitecture events.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/thead/c900-legacy/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/thead/c900-legacy/firmware.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/thead/c900-legacy/firmware.json

## Purpose
This JSON file is a architecture-standard alias table for `thead/c900-legacy` under the `riscv` perf PMU event tree. It provides model-local references to RISC-V architecture standard firmware events declared in the architecture root. It contains 22 entries and belongs to the `firmware` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `ArchStdEvent`.
- Encoding summary: No local numeric event code field; entries dereference or compute from other event definitions..
- Representative names: FW_MISALIGNED_LOAD, FW_MISALIGNED_STORE, FW_ACCESS_LOAD, FW_ACCESS_STORE, FW_ILLEGAL_INSN, FW_SET_TIMER, FW_IPI_SENT, FW_IPI_RECEIVED, FW_FENCE_I_SENT, FW_FENCE_I_RECEIVED.
- `ArchStdEvent` is a dereference key, not a standalone event definition; generation resolves it against architecture standard events by `EventName`.

## Content Notes
- The file contains 22 bare `ArchStdEvent` references; descriptions and config codes are inherited from the RISC-V root standard firmware table.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

For this file the main control-flow branch is architecture-standard resolution: the local entry names a firmware standard event, and the generator copies the canonical root definition into the model table.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.
- `jevents.py` resolves each `ArchStdEvent` through architecture-root standard events by matching `EventName`

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Every reference must match an architecture-root standard event; a typo fails at generation or silently drops expected firmware aliases depending on validation path.
- These model files intentionally duplicate the same SBI firmware reference list; consistency with `riscv-sbi-firmware.json` matters more than local descriptions.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Check every `ArchStdEvent` resolves to a root RISC-V standard event by `EventName`.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/thead/c900-legacy/firmware.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/thead/c900-legacy/instruction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/thead/c900-legacy/instruction.json

## Purpose
This JSON file is a PMU event table for `thead/c900-legacy` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv thead/c900-legacy `instruction` counters. It contains 14 entries and belongs to the `instruction` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName`.
- Encoding summary: EventCode range 0x6..0x2a.
- Representative names: INST_BRANCH_MISPREDICT, INST_BRANCH, INST_JMP_MISPREDICT, INST_JMP, INST_STORE, INST_ALU, INST_LDST, INST_VECTOR, INST_CSR, INST_SYNC.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The thead/c900-legacy `instruction` table defines model-specific aliases such as INST_BRANCH_MISPREDICT, INST_BRANCH, INST_JMP_MISPREDICT, INST_JMP, INST_STORE, INST_ALU, INST_LDST, INST_VECTOR.
- The T-Head legacy tables use vendor-specific instruction/cache/microarchitecture names and include a PublicDescription only for microarchitecture events.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/thead/c900-legacy/instruction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/thead/c900-legacy/microarch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/thead/c900-legacy/microarch.json

## Purpose
This JSON file is a PMU event table for `thead/c900-legacy` under the `riscv` perf PMU event tree. It provides topic-scoped raw event aliases for riscv thead/c900-legacy `microarch` counters. It contains 15 entries and belongs to the `microarch` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName, PublicDescription`.
- Encoding summary: EventCode range 0xa..0x29.
- Representative names: LSU_SPEC_FAIL, IDU_RF_PIPE_FAIL, IDU_RF_REG_FAIL, IDU_RF_INSTRUCTION, LSU_4K_STALL, LSU_OTHER_STALL, LSU_SQ_OTHER_DIS, LSU_SQ_DATA_DISCARD, BRANCH_DIRECTION_MISPREDICTION, BRANCH_DIRECTION_PREDICTION.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `PublicDescription` supplies longer help text when available; `jevents.py` normalizes it into the generated long description field.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.

## Content Notes
- The thead/c900-legacy `microarch` table defines model-specific aliases such as LSU_SPEC_FAIL, IDU_RF_PIPE_FAIL, IDU_RF_REG_FAIL, IDU_RF_INSTRUCTION, LSU_4K_STALL, LSU_OTHER_STALL, LSU_SQ_OTHER_DIS, LSU_SQ_DATA_DISCARD.
- The T-Head legacy tables use vendor-specific instruction/cache/microarchitecture names and include a PublicDescription only for microarchitecture events.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/riscv/mapfile.csv maps MVENDORID-MARCHID-MIMPID patterns to vendor/model directories as core events.

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/riscv/thead/c900-legacy/microarch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z10/basic.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z10/basic.json

## Purpose
This JSON file is a PMU event table for `cf_z10` under the `s390` perf PMU event tree. It provides topic-scoped raw event aliases for s390 cf_z10 `basic` counters. It contains 12 entries and belongs to the `basic` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName, PublicDescription, Unit`.
- Encoding summary: EventCode range 0x0..0x25; Units: CPU-M-CF.
- Representative names: CPU_CYCLES, INSTRUCTIONS, L1I_DIR_WRITES, L1I_PENALTY_CYCLES, L1D_DIR_WRITES, L1D_PENALTY_CYCLES, PROBLEM_STATE_CPU_CYCLES, PROBLEM_STATE_INSTRUCTIONS, PROBLEM_STATE_L1I_DIR_WRITES, PROBLEM_STATE_L1I_PENALTY_CYCLES.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `PublicDescription` supplies longer help text when available; `jevents.py` normalizes it into the generated long description field.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.
- `Unit` binds events to a PMU namespace such as `CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`.

## Content Notes
- The cf_z10 `basic` table exposes s390 counter facility aliases such as CPU_CYCLES, INSTRUCTIONS, L1I_DIR_WRITES, L1I_PENALTY_CYCLES, L1D_DIR_WRITES, L1D_PENALTY_CYCLES, PROBLEM_STATE_CPU_CYCLES, PROBLEM_STATE_INSTRUCTIONS.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/s390/mapfile.csv maps IBM family/model regular expressions to cf_z* directories as core events.
- `Unit` selects the Linux PMU namespace through `jevents.py` unit-to-PMU normalization instead of default core PMU handling

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.
- Incorrect `Unit` mapping can place aliases on the wrong PMU (`CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`) and make user event selection fail.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Confirm generated PMU unit strings match kernel PMU names for the target s390 facility.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z10/basic.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z10/crypto.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z10/crypto.json

## Purpose
This JSON file is a PMU event table for `cf_z10` under the `s390` perf PMU event tree. It provides topic-scoped raw event aliases for s390 cf_z10 `crypto` counters. It contains 16 entries and belongs to the `crypto` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName, PublicDescription, Unit`.
- Encoding summary: EventCode range 0x40..0x4f; Units: CPU-M-CF.
- Representative names: PRNG_FUNCTIONS, PRNG_CYCLES, PRNG_BLOCKED_FUNCTIONS, PRNG_BLOCKED_CYCLES, SHA_FUNCTIONS, SHA_CYCLES, SHA_BLOCKED_FUNCTIONS, SHA_BLOCKED_CYCLES, DEA_FUNCTIONS, DEA_CYCLES.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `PublicDescription` supplies longer help text when available; `jevents.py` normalizes it into the generated long description field.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.
- `Unit` binds events to a PMU namespace such as `CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`.

## Content Notes
- The cf_z10 `crypto` table exposes s390 counter facility aliases such as PRNG_FUNCTIONS, PRNG_CYCLES, PRNG_BLOCKED_FUNCTIONS, PRNG_BLOCKED_CYCLES, SHA_FUNCTIONS, SHA_CYCLES, SHA_BLOCKED_FUNCTIONS, SHA_BLOCKED_CYCLES.
- Crypto tables track function counts, cycles, and blocked activity; `crypto6` adds newer z15/z16-era crypto counter groups.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/s390/mapfile.csv maps IBM family/model regular expressions to cf_z* directories as core events.
- `Unit` selects the Linux PMU namespace through `jevents.py` unit-to-PMU normalization instead of default core PMU handling

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.
- Incorrect `Unit` mapping can place aliases on the wrong PMU (`CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`) and make user event selection fail.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Confirm generated PMU unit strings match kernel PMU names for the target s390 facility.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z10/crypto.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z10/extended.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z10/extended.json

## Purpose
This JSON file is a PMU event table for `cf_z10` under the `s390` perf PMU event tree. It provides topic-scoped raw event aliases for s390 cf_z10 `extended` counters. It contains 18 entries and belongs to the `extended` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName, PublicDescription, Unit`.
- Encoding summary: EventCode range 0x80..0x93; Units: CPU-M-CF.
- Representative names: L1I_L2_SOURCED_WRITES, L1D_L2_SOURCED_WRITES, L1I_L3_LOCAL_WRITES, L1D_L3_LOCAL_WRITES, L1I_L3_REMOTE_WRITES, L1D_L3_REMOTE_WRITES, L1D_LMEM_SOURCED_WRITES, L1I_LMEM_SOURCED_WRITES, L1D_RO_EXCL_WRITES, L1I_CACHELINE_INVALIDATES.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `PublicDescription` supplies longer help text when available; `jevents.py` normalizes it into the generated long description field.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.
- `Unit` binds events to a PMU namespace such as `CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`.

## Content Notes
- The cf_z10 `extended` table exposes s390 counter facility aliases such as L1I_L2_SOURCED_WRITES, L1D_L2_SOURCED_WRITES, L1I_L3_LOCAL_WRITES, L1D_L3_LOCAL_WRITES, L1I_L3_REMOTE_WRITES, L1D_L3_REMOTE_WRITES, L1D_LMEM_SOURCED_WRITES, L1I_LMEM_SOURCED_WRITES.
- Extended tables grow substantially across generations as cache/TLB/memory-source detail becomes available.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/s390/mapfile.csv maps IBM family/model regular expressions to cf_z* directories as core events.
- `Unit` selects the Linux PMU namespace through `jevents.py` unit-to-PMU normalization instead of default core PMU handling

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.
- Incorrect `Unit` mapping can place aliases on the wrong PMU (`CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`) and make user event selection fail.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Confirm generated PMU unit strings match kernel PMU names for the target s390 facility.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z10/extended.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z13/basic.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z13/basic.json

## Purpose
This JSON file is a PMU event table for `cf_z13` under the `s390` perf PMU event tree. It provides topic-scoped raw event aliases for s390 cf_z13 `basic` counters. It contains 12 entries and belongs to the `basic` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName, PublicDescription, Unit`.
- Encoding summary: EventCode range 0x0..0x25; Units: CPU-M-CF.
- Representative names: CPU_CYCLES, INSTRUCTIONS, L1I_DIR_WRITES, L1I_PENALTY_CYCLES, L1D_DIR_WRITES, L1D_PENALTY_CYCLES, PROBLEM_STATE_CPU_CYCLES, PROBLEM_STATE_INSTRUCTIONS, PROBLEM_STATE_L1I_DIR_WRITES, PROBLEM_STATE_L1I_PENALTY_CYCLES.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `PublicDescription` supplies longer help text when available; `jevents.py` normalizes it into the generated long description field.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.
- `Unit` binds events to a PMU namespace such as `CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`.

## Content Notes
- The cf_z13 `basic` table exposes s390 counter facility aliases such as CPU_CYCLES, INSTRUCTIONS, L1I_DIR_WRITES, L1I_PENALTY_CYCLES, L1D_DIR_WRITES, L1D_PENALTY_CYCLES, PROBLEM_STATE_CPU_CYCLES, PROBLEM_STATE_INSTRUCTIONS.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/s390/mapfile.csv maps IBM family/model regular expressions to cf_z* directories as core events.
- `Unit` selects the Linux PMU namespace through `jevents.py` unit-to-PMU normalization instead of default core PMU handling

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.
- Incorrect `Unit` mapping can place aliases on the wrong PMU (`CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`) and make user event selection fail.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Confirm generated PMU unit strings match kernel PMU names for the target s390 facility.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z13/basic.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z13/crypto.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z13/crypto.json

## Purpose
This JSON file is a PMU event table for `cf_z13` under the `s390` perf PMU event tree. It provides topic-scoped raw event aliases for s390 cf_z13 `crypto` counters. It contains 16 entries and belongs to the `crypto` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName, PublicDescription, Unit`.
- Encoding summary: EventCode range 0x40..0x4f; Units: CPU-M-CF.
- Representative names: PRNG_FUNCTIONS, PRNG_CYCLES, PRNG_BLOCKED_FUNCTIONS, PRNG_BLOCKED_CYCLES, SHA_FUNCTIONS, SHA_CYCLES, SHA_BLOCKED_FUNCTIONS, SHA_BLOCKED_CYCLES, DEA_FUNCTIONS, DEA_CYCLES.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `PublicDescription` supplies longer help text when available; `jevents.py` normalizes it into the generated long description field.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.
- `Unit` binds events to a PMU namespace such as `CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`.

## Content Notes
- The cf_z13 `crypto` table exposes s390 counter facility aliases such as PRNG_FUNCTIONS, PRNG_CYCLES, PRNG_BLOCKED_FUNCTIONS, PRNG_BLOCKED_CYCLES, SHA_FUNCTIONS, SHA_CYCLES, SHA_BLOCKED_FUNCTIONS, SHA_BLOCKED_CYCLES.
- Crypto tables track function counts, cycles, and blocked activity; `crypto6` adds newer z15/z16-era crypto counter groups.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/s390/mapfile.csv maps IBM family/model regular expressions to cf_z* directories as core events.
- `Unit` selects the Linux PMU namespace through `jevents.py` unit-to-PMU normalization instead of default core PMU handling

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.
- Incorrect `Unit` mapping can place aliases on the wrong PMU (`CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`) and make user event selection fail.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Confirm generated PMU unit strings match kernel PMU names for the target s390 facility.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z13/crypto.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z13/extended.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z13/extended.json

## Purpose
This JSON file is a PMU event table for `cf_z13` under the `s390` perf PMU event tree. It provides topic-scoped raw event aliases for s390 cf_z13 `extended` counters. It contains 56 entries and belongs to the `extended` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName, PublicDescription, Unit`.
- Encoding summary: EventCode range 0x80..0x1c1; Units: CPU-M-CF.
- Representative names: L1D_RO_EXCL_WRITES, DTLB1_WRITES, DTLB1_MISSES, DTLB1_HPAGE_WRITES, DTLB1_GPAGE_WRITES, L1D_L2D_SOURCED_WRITES, ITLB1_WRITES, ITLB1_MISSES, L1I_L2I_SOURCED_WRITES, TLB2_PTE_WRITES.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `PublicDescription` supplies longer help text when available; `jevents.py` normalizes it into the generated long description field.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.
- `Unit` binds events to a PMU namespace such as `CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`.

## Content Notes
- The cf_z13 `extended` table exposes s390 counter facility aliases such as L1D_RO_EXCL_WRITES, DTLB1_WRITES, DTLB1_MISSES, DTLB1_HPAGE_WRITES, DTLB1_GPAGE_WRITES, L1D_L2D_SOURCED_WRITES, ITLB1_WRITES, ITLB1_MISSES.
- Extended tables grow substantially across generations as cache/TLB/memory-source detail becomes available.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/s390/mapfile.csv maps IBM family/model regular expressions to cf_z* directories as core events.
- `Unit` selects the Linux PMU namespace through `jevents.py` unit-to-PMU normalization instead of default core PMU handling

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.
- Incorrect `Unit` mapping can place aliases on the wrong PMU (`CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`) and make user event selection fail.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Confirm generated PMU unit strings match kernel PMU names for the target s390 facility.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z13/extended.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z13/transaction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z13/transaction.json

## Purpose
This JSON file is a metric table for `cf_z13` under the `s390` perf PMU event tree. It provides derived perf metrics for s390 cf_z13; formulas reference event names and use `has_event(...)` guards. It contains 15 entries and belongs to the `transaction` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, MetricExpr, MetricName`.
- Encoding summary: No local numeric event code field; entries dereference or compute from other event definitions..
- Representative names: transaction, cpi, prbstate, l1mp, l2p, l3p, l4lp, l4rp, memp, finite_cpi.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `MetricExpr` is parsed by `metric.py` and may reference raw event names plus helper predicates such as `has_event(...)`.

## Content Notes
- The transaction file contains derived metrics such as transaction, cpi, prbstate, l1mp, l2p, l3p, l4lp, l4rp, each represented by `MetricName` plus `MetricExpr` rather than raw `EventCode`.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

For this file the main control-flow branch is metric parsing: expressions are simplified during generation and evaluated later against runtime counter values only when their dependency events exist.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/s390/mapfile.csv maps IBM family/model regular expressions to cf_z* directories as core events.
- `tools/perf/pmu-events/metric.py` parses `MetricExpr`; formulas depend on referenced event aliases being present in the same CPU table

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Metric expressions are brittle against event renames; `has_event(...)` guards avoid lookup failures but can yield zero-valued metrics when dependency events are absent.
- Several formulas divide by instruction or miss counters; perf metric evaluation must handle zero denominators as defined by the metric parser/runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Run `tools/perf/tests/parse-metric` or metric parser coverage for each `MetricExpr`, including `has_event(...)` fallback behavior.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z13/transaction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z14/basic.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z14/basic.json

## Purpose
This JSON file is a PMU event table for `cf_z14` under the `s390` perf PMU event tree. It provides topic-scoped raw event aliases for s390 cf_z14 `basic` counters. It contains 8 entries and belongs to the `basic` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName, PublicDescription, Unit`.
- Encoding summary: EventCode range 0x0..0x21; Units: CPU-M-CF.
- Representative names: CPU_CYCLES, INSTRUCTIONS, L1I_DIR_WRITES, L1I_PENALTY_CYCLES, L1D_DIR_WRITES, L1D_PENALTY_CYCLES, PROBLEM_STATE_CPU_CYCLES, PROBLEM_STATE_INSTRUCTIONS.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `PublicDescription` supplies longer help text when available; `jevents.py` normalizes it into the generated long description field.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.
- `Unit` binds events to a PMU namespace such as `CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`.

## Content Notes
- The cf_z14 `basic` table exposes s390 counter facility aliases such as CPU_CYCLES, INSTRUCTIONS, L1I_DIR_WRITES, L1I_PENALTY_CYCLES, L1D_DIR_WRITES, L1D_PENALTY_CYCLES, PROBLEM_STATE_CPU_CYCLES, PROBLEM_STATE_INSTRUCTIONS.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/s390/mapfile.csv maps IBM family/model regular expressions to cf_z* directories as core events.
- `Unit` selects the Linux PMU namespace through `jevents.py` unit-to-PMU normalization instead of default core PMU handling

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.
- Incorrect `Unit` mapping can place aliases on the wrong PMU (`CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`) and make user event selection fail.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Confirm generated PMU unit strings match kernel PMU names for the target s390 facility.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z14/basic.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z14/crypto.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z14/crypto.json

## Purpose
This JSON file is a PMU event table for `cf_z14` under the `s390` perf PMU event tree. It provides topic-scoped raw event aliases for s390 cf_z14 `crypto` counters. It contains 16 entries and belongs to the `crypto` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName, PublicDescription, Unit`.
- Encoding summary: EventCode range 0x40..0x4f; Units: CPU-M-CF.
- Representative names: PRNG_FUNCTIONS, PRNG_CYCLES, PRNG_BLOCKED_FUNCTIONS, PRNG_BLOCKED_CYCLES, SHA_FUNCTIONS, SHA_CYCLES, SHA_BLOCKED_FUNCTIONS, SHA_BLOCKED_CYCLES, DEA_FUNCTIONS, DEA_CYCLES.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `PublicDescription` supplies longer help text when available; `jevents.py` normalizes it into the generated long description field.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.
- `Unit` binds events to a PMU namespace such as `CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`.

## Content Notes
- The cf_z14 `crypto` table exposes s390 counter facility aliases such as PRNG_FUNCTIONS, PRNG_CYCLES, PRNG_BLOCKED_FUNCTIONS, PRNG_BLOCKED_CYCLES, SHA_FUNCTIONS, SHA_CYCLES, SHA_BLOCKED_FUNCTIONS, SHA_BLOCKED_CYCLES.
- Crypto tables track function counts, cycles, and blocked activity; `crypto6` adds newer z15/z16-era crypto counter groups.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/s390/mapfile.csv maps IBM family/model regular expressions to cf_z* directories as core events.
- `Unit` selects the Linux PMU namespace through `jevents.py` unit-to-PMU normalization instead of default core PMU handling

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.
- Incorrect `Unit` mapping can place aliases on the wrong PMU (`CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`) and make user event selection fail.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Confirm generated PMU unit strings match kernel PMU names for the target s390 facility.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z14/crypto.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z14/extended.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z14/extended.json

## Purpose
This JSON file is a PMU event table for `cf_z14` under the `s390` perf PMU event tree. It provides topic-scoped raw event aliases for s390 cf_z14 `extended` counters. It contains 53 entries and belongs to the `extended` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName, PublicDescription, Unit`.
- Encoding summary: EventCode range 0x80..0x1c1; Units: CPU-M-CF.
- Representative names: L1D_RO_EXCL_WRITES, DTLB2_WRITES, DTLB2_MISSES, DTLB2_HPAGE_WRITES, DTLB2_GPAGE_WRITES, L1D_L2D_SOURCED_WRITES, ITLB2_WRITES, ITLB2_MISSES, L1I_L2I_SOURCED_WRITES, TLB2_PTE_WRITES.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `PublicDescription` supplies longer help text when available; `jevents.py` normalizes it into the generated long description field.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.
- `Unit` binds events to a PMU namespace such as `CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`.

## Content Notes
- The cf_z14 `extended` table exposes s390 counter facility aliases such as L1D_RO_EXCL_WRITES, DTLB2_WRITES, DTLB2_MISSES, DTLB2_HPAGE_WRITES, DTLB2_GPAGE_WRITES, L1D_L2D_SOURCED_WRITES, ITLB2_WRITES, ITLB2_MISSES.
- Extended tables grow substantially across generations as cache/TLB/memory-source detail becomes available.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/s390/mapfile.csv maps IBM family/model regular expressions to cf_z* directories as core events.
- `Unit` selects the Linux PMU namespace through `jevents.py` unit-to-PMU normalization instead of default core PMU handling

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.
- Incorrect `Unit` mapping can place aliases on the wrong PMU (`CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`) and make user event selection fail.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Confirm generated PMU unit strings match kernel PMU names for the target s390 facility.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z14/extended.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z14/transaction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z14/transaction.json

## Purpose
This JSON file is a metric table for `cf_z14` under the `s390` perf PMU event tree. It provides derived perf metrics for s390 cf_z14; formulas reference event names and use `has_event(...)` guards. It contains 14 entries and belongs to the `transaction` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, MetricExpr, MetricName`.
- Encoding summary: No local numeric event code field; entries dereference or compute from other event definitions..
- Representative names: transaction, cpi, prbstate, l1mp, l2p, l3p, l4lp, l4rp, memp, finite_cpi.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `MetricExpr` is parsed by `metric.py` and may reference raw event names plus helper predicates such as `has_event(...)`.

## Content Notes
- The transaction file contains derived metrics such as transaction, cpi, prbstate, l1mp, l2p, l3p, l4lp, l4rp, each represented by `MetricName` plus `MetricExpr` rather than raw `EventCode`.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

For this file the main control-flow branch is metric parsing: expressions are simplified during generation and evaluated later against runtime counter values only when their dependency events exist.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/s390/mapfile.csv maps IBM family/model regular expressions to cf_z* directories as core events.
- `tools/perf/pmu-events/metric.py` parses `MetricExpr`; formulas depend on referenced event aliases being present in the same CPU table

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Metric expressions are brittle against event renames; `has_event(...)` guards avoid lookup failures but can yield zero-valued metrics when dependency events are absent.
- Several formulas divide by instruction or miss counters; perf metric evaluation must handle zero denominators as defined by the metric parser/runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Run `tools/perf/tests/parse-metric` or metric parser coverage for each `MetricExpr`, including `has_event(...)` fallback behavior.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z14/transaction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z15/basic.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z15/basic.json

## Purpose
This JSON file is a PMU event table for `cf_z15` under the `s390` perf PMU event tree. It provides topic-scoped raw event aliases for s390 cf_z15 `basic` counters. It contains 8 entries and belongs to the `basic` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName, PublicDescription, Unit`.
- Encoding summary: EventCode range 0x0..0x21; Units: CPU-M-CF.
- Representative names: CPU_CYCLES, INSTRUCTIONS, L1I_DIR_WRITES, L1I_PENALTY_CYCLES, L1D_DIR_WRITES, L1D_PENALTY_CYCLES, PROBLEM_STATE_CPU_CYCLES, PROBLEM_STATE_INSTRUCTIONS.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `PublicDescription` supplies longer help text when available; `jevents.py` normalizes it into the generated long description field.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.
- `Unit` binds events to a PMU namespace such as `CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`.

## Content Notes
- The cf_z15 `basic` table exposes s390 counter facility aliases such as CPU_CYCLES, INSTRUCTIONS, L1I_DIR_WRITES, L1I_PENALTY_CYCLES, L1D_DIR_WRITES, L1D_PENALTY_CYCLES, PROBLEM_STATE_CPU_CYCLES, PROBLEM_STATE_INSTRUCTIONS.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/s390/mapfile.csv maps IBM family/model regular expressions to cf_z* directories as core events.
- `Unit` selects the Linux PMU namespace through `jevents.py` unit-to-PMU normalization instead of default core PMU handling

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.
- Incorrect `Unit` mapping can place aliases on the wrong PMU (`CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`) and make user event selection fail.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Confirm generated PMU unit strings match kernel PMU names for the target s390 facility.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z15/basic.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z15/crypto6.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z15/crypto6.json

## Purpose
This JSON file is a PMU event table for `cf_z15` under the `s390` perf PMU event tree. It provides topic-scoped raw event aliases for s390 cf_z15 `crypto6` counters. It contains 20 entries and belongs to the `crypto6` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName, PublicDescription, Unit`.
- Encoding summary: EventCode range 0x40..0x53; Units: CPU-M-CF.
- Representative names: PRNG_FUNCTIONS, PRNG_CYCLES, PRNG_BLOCKED_FUNCTIONS, PRNG_BLOCKED_CYCLES, SHA_FUNCTIONS, SHA_CYCLES, SHA_BLOCKED_FUNCTIONS, SHA_BLOCKED_CYCLES, DEA_FUNCTIONS, DEA_CYCLES.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `PublicDescription` supplies longer help text when available; `jevents.py` normalizes it into the generated long description field.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.
- `Unit` binds events to a PMU namespace such as `CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`.

## Content Notes
- The cf_z15 `crypto6` table exposes s390 counter facility aliases such as PRNG_FUNCTIONS, PRNG_CYCLES, PRNG_BLOCKED_FUNCTIONS, PRNG_BLOCKED_CYCLES, SHA_FUNCTIONS, SHA_CYCLES, SHA_BLOCKED_FUNCTIONS, SHA_BLOCKED_CYCLES.
- Crypto tables track function counts, cycles, and blocked activity; `crypto6` adds newer z15/z16-era crypto counter groups.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/s390/mapfile.csv maps IBM family/model regular expressions to cf_z* directories as core events.
- `Unit` selects the Linux PMU namespace through `jevents.py` unit-to-PMU normalization instead of default core PMU handling

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.
- Incorrect `Unit` mapping can place aliases on the wrong PMU (`CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`) and make user event selection fail.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Confirm generated PMU unit strings match kernel PMU names for the target s390 facility.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z15/crypto6.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z15/extended.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z15/extended.json

## Purpose
This JSON file is a PMU event table for `cf_z15` under the `s390` perf PMU event tree. It provides topic-scoped raw event aliases for s390 cf_z15 `extended` counters. It contains 57 entries and belongs to the `extended` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName, PublicDescription, Unit`.
- Encoding summary: EventCode range 0x80..0x1c1; Units: CPU-M-CF.
- Representative names: L1D_RO_EXCL_WRITES, DTLB2_WRITES, DTLB2_MISSES, DTLB2_HPAGE_WRITES, DTLB2_GPAGE_WRITES, L1D_L2D_SOURCED_WRITES, ITLB2_WRITES, ITLB2_MISSES, L1I_L2I_SOURCED_WRITES, TLB2_PTE_WRITES.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `PublicDescription` supplies longer help text when available; `jevents.py` normalizes it into the generated long description field.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.
- `Unit` binds events to a PMU namespace such as `CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`.

## Content Notes
- The cf_z15 `extended` table exposes s390 counter facility aliases such as L1D_RO_EXCL_WRITES, DTLB2_WRITES, DTLB2_MISSES, DTLB2_HPAGE_WRITES, DTLB2_GPAGE_WRITES, L1D_L2D_SOURCED_WRITES, ITLB2_WRITES, ITLB2_MISSES.
- Extended tables grow substantially across generations as cache/TLB/memory-source detail becomes available.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/s390/mapfile.csv maps IBM family/model regular expressions to cf_z* directories as core events.
- `Unit` selects the Linux PMU namespace through `jevents.py` unit-to-PMU normalization instead of default core PMU handling

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.
- Incorrect `Unit` mapping can place aliases on the wrong PMU (`CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`) and make user event selection fail.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Confirm generated PMU unit strings match kernel PMU names for the target s390 facility.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z15/extended.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z15/transaction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z15/transaction.json

## Purpose
This JSON file is a metric table for `cf_z15` under the `s390` perf PMU event tree. It provides derived perf metrics for s390 cf_z15; formulas reference event names and use `has_event(...)` guards. It contains 14 entries and belongs to the `transaction` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, MetricExpr, MetricName`.
- Encoding summary: No local numeric event code field; entries dereference or compute from other event definitions..
- Representative names: transaction, cpi, prbstate, l1mp, l2p, l3p, l4lp, l4rp, memp, finite_cpi.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `MetricExpr` is parsed by `metric.py` and may reference raw event names plus helper predicates such as `has_event(...)`.

## Content Notes
- The transaction file contains derived metrics such as transaction, cpi, prbstate, l1mp, l2p, l3p, l4lp, l4rp, each represented by `MetricName` plus `MetricExpr` rather than raw `EventCode`.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

For this file the main control-flow branch is metric parsing: expressions are simplified during generation and evaluated later against runtime counter values only when their dependency events exist.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/s390/mapfile.csv maps IBM family/model regular expressions to cf_z* directories as core events.
- `tools/perf/pmu-events/metric.py` parses `MetricExpr`; formulas depend on referenced event aliases being present in the same CPU table

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Metric expressions are brittle against event renames; `has_event(...)` guards avoid lookup failures but can yield zero-valued metrics when dependency events are absent.
- Several formulas divide by instruction or miss counters; perf metric evaluation must handle zero denominators as defined by the metric parser/runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Run `tools/perf/tests/parse-metric` or metric parser coverage for each `MetricExpr`, including `has_event(...)` fallback behavior.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z15/transaction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z16/basic.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z16/basic.json

## Purpose
This JSON file is a PMU event table for `cf_z16` under the `s390` perf PMU event tree. It provides topic-scoped raw event aliases for s390 cf_z16 `basic` counters. It contains 8 entries and belongs to the `basic` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName, PublicDescription, Unit`.
- Encoding summary: EventCode range 0x0..0x21; Units: CPU-M-CF.
- Representative names: CPU_CYCLES, INSTRUCTIONS, L1I_DIR_WRITES, L1I_PENALTY_CYCLES, L1D_DIR_WRITES, L1D_PENALTY_CYCLES, PROBLEM_STATE_CPU_CYCLES, PROBLEM_STATE_INSTRUCTIONS.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `PublicDescription` supplies longer help text when available; `jevents.py` normalizes it into the generated long description field.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.
- `Unit` binds events to a PMU namespace such as `CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`.

## Content Notes
- The cf_z16 `basic` table exposes s390 counter facility aliases such as CPU_CYCLES, INSTRUCTIONS, L1I_DIR_WRITES, L1I_PENALTY_CYCLES, L1D_DIR_WRITES, L1D_PENALTY_CYCLES, PROBLEM_STATE_CPU_CYCLES, PROBLEM_STATE_INSTRUCTIONS.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/s390/mapfile.csv maps IBM family/model regular expressions to cf_z* directories as core events.
- `Unit` selects the Linux PMU namespace through `jevents.py` unit-to-PMU normalization instead of default core PMU handling

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.
- Incorrect `Unit` mapping can place aliases on the wrong PMU (`CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`) and make user event selection fail.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Confirm generated PMU unit strings match kernel PMU names for the target s390 facility.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z16/basic.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z16/crypto6.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z16/crypto6.json

## Purpose
This JSON file is a PMU event table for `cf_z16` under the `s390` perf PMU event tree. It provides topic-scoped raw event aliases for s390 cf_z16 `crypto6` counters. It contains 20 entries and belongs to the `crypto6` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName, PublicDescription, Unit`.
- Encoding summary: EventCode range 0x40..0x53; Units: CPU-M-CF.
- Representative names: PRNG_FUNCTIONS, PRNG_CYCLES, PRNG_BLOCKED_FUNCTIONS, PRNG_BLOCKED_CYCLES, SHA_FUNCTIONS, SHA_CYCLES, SHA_BLOCKED_FUNCTIONS, SHA_BLOCKED_CYCLES, DEA_FUNCTIONS, DEA_CYCLES.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `PublicDescription` supplies longer help text when available; `jevents.py` normalizes it into the generated long description field.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.
- `Unit` binds events to a PMU namespace such as `CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`.

## Content Notes
- The cf_z16 `crypto6` table exposes s390 counter facility aliases such as PRNG_FUNCTIONS, PRNG_CYCLES, PRNG_BLOCKED_FUNCTIONS, PRNG_BLOCKED_CYCLES, SHA_FUNCTIONS, SHA_CYCLES, SHA_BLOCKED_FUNCTIONS, SHA_BLOCKED_CYCLES.
- Crypto tables track function counts, cycles, and blocked activity; `crypto6` adds newer z15/z16-era crypto counter groups.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/s390/mapfile.csv maps IBM family/model regular expressions to cf_z* directories as core events.
- `Unit` selects the Linux PMU namespace through `jevents.py` unit-to-PMU normalization instead of default core PMU handling

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.
- Incorrect `Unit` mapping can place aliases on the wrong PMU (`CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`) and make user event selection fail.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Confirm generated PMU unit strings match kernel PMU names for the target s390 facility.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z16/crypto6.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z16/extended.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z16/extended.json

## Purpose
This JSON file is a PMU event table for `cf_z16` under the `s390` perf PMU event tree. It provides topic-scoped raw event aliases for s390 cf_z16 `extended` counters. It contains 70 entries and belongs to the `extended` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName, PublicDescription, Unit`.
- Encoding summary: EventCode range 0x80..0x1c1; Units: CPU-M-CF.
- Representative names: L1D_RO_EXCL_WRITES, DTLB2_WRITES, DTLB2_MISSES, CRSTE_1MB_WRITES, DTLB2_GPAGE_WRITES, ITLB2_WRITES, ITLB2_MISSES, TLB2_PTE_WRITES, TLB2_CRSTE_WRITES, TLB2_ENGINES_BUSY.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `PublicDescription` supplies longer help text when available; `jevents.py` normalizes it into the generated long description field.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.
- `Unit` binds events to a PMU namespace such as `CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`.

## Content Notes
- The cf_z16 `extended` table exposes s390 counter facility aliases such as L1D_RO_EXCL_WRITES, DTLB2_WRITES, DTLB2_MISSES, CRSTE_1MB_WRITES, DTLB2_GPAGE_WRITES, ITLB2_WRITES, ITLB2_MISSES, TLB2_PTE_WRITES.
- Extended tables grow substantially across generations as cache/TLB/memory-source detail becomes available.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/s390/mapfile.csv maps IBM family/model regular expressions to cf_z* directories as core events.
- `Unit` selects the Linux PMU namespace through `jevents.py` unit-to-PMU normalization instead of default core PMU handling

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.
- Incorrect `Unit` mapping can place aliases on the wrong PMU (`CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`) and make user event selection fail.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Confirm generated PMU unit strings match kernel PMU names for the target s390 facility.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z16/extended.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z16/pai_crypto.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z16/pai_crypto.json

## Purpose
This JSON file is a PAI event table for `cf_z16` under the `s390` perf PMU event tree. It provides s390 processor activity instrumentation table for pai-crypto unit counters. It contains 157 entries and belongs to the `pai_crypto` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName, PublicDescription, Unit`.
- Encoding summary: EventCode range 0x1000..0x109c; Units: PAI-CRYPTO.
- Representative names: CRYPTO_ALL, KM_DEA, KM_TDEA_128, KM_TDEA_192, KM_ENCRYPTED_DEA, KM_ENCRYPTED_TDEA_128, KM_ENCRYPTED_TDEA_192, KM_AES_128, KM_AES_192, KM_AES_256.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `PublicDescription` supplies longer help text when available; `jevents.py` normalizes it into the generated long description field.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.
- `Unit` binds events to a PMU namespace such as `CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`.

## Content Notes
- The cf_z16 `pai_crypto` table exposes s390 counter facility aliases such as CRYPTO_ALL, KM_DEA, KM_TDEA_128, KM_TDEA_192, KM_ENCRYPTED_DEA, KM_ENCRYPTED_TDEA_128, KM_ENCRYPTED_TDEA_192, KM_AES_128.
- PAI tables are tied to processor activity instrumentation units rather than the normal CPU-M-CF unit.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/s390/mapfile.csv maps IBM family/model regular expressions to cf_z* directories as core events.
- `Unit` selects the Linux PMU namespace through `jevents.py` unit-to-PMU normalization instead of default core PMU handling

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.
- Incorrect `Unit` mapping can place aliases on the wrong PMU (`CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`) and make user event selection fail.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Confirm generated PMU unit strings match kernel PMU names for the target s390 facility.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z16/pai_crypto.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z16/pai_ext.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z16/pai_ext.json

## Purpose
This JSON file is a PAI event table for `cf_z16` under the `s390` perf PMU event tree. It provides s390 processor activity instrumentation table for pai-ext unit counters. It contains 28 entries and belongs to the `pai_ext` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName, PublicDescription, Unit`.
- Encoding summary: EventCode range 0x1800..0x181b; Units: PAI-EXT.
- Representative names: NNPA_ALL, NNPA_ADD, NNPA_SUB, NNPA_MUL, NNPA_DIV, NNPA_MIN, NNPA_MAX, NNPA_LOG, NNPA_EXP, NNPA_IBM_RESERVED_9.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `PublicDescription` supplies longer help text when available; `jevents.py` normalizes it into the generated long description field.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.
- `Unit` binds events to a PMU namespace such as `CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`.

## Content Notes
- The cf_z16 `pai_ext` table exposes s390 counter facility aliases such as NNPA_ALL, NNPA_ADD, NNPA_SUB, NNPA_MUL, NNPA_DIV, NNPA_MIN, NNPA_MAX, NNPA_LOG.
- PAI tables are tied to processor activity instrumentation units rather than the normal CPU-M-CF unit.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/s390/mapfile.csv maps IBM family/model regular expressions to cf_z* directories as core events.
- `Unit` selects the Linux PMU namespace through `jevents.py` unit-to-PMU normalization instead of default core PMU handling

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.
- Incorrect `Unit` mapping can place aliases on the wrong PMU (`CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`) and make user event selection fail.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Confirm generated PMU unit strings match kernel PMU names for the target s390 facility.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z16/pai_ext.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z16/transaction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z16/transaction.json

## Purpose
This JSON file is a metric table for `cf_z16` under the `s390` perf PMU event tree. It provides derived perf metrics for s390 cf_z16; formulas reference event names and use `has_event(...)` guards. It contains 14 entries and belongs to the `transaction` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, MetricExpr, MetricName`.
- Encoding summary: No local numeric event code field; entries dereference or compute from other event definitions..
- Representative names: transaction, cpi, prbstate, l1mp, l2p, l3p, l4lp, l4rp, memp, finite_cpi.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `MetricExpr` is parsed by `metric.py` and may reference raw event names plus helper predicates such as `has_event(...)`.

## Content Notes
- The transaction file contains derived metrics such as transaction, cpi, prbstate, l1mp, l2p, l3p, l4lp, l4rp, each represented by `MetricName` plus `MetricExpr` rather than raw `EventCode`.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

For this file the main control-flow branch is metric parsing: expressions are simplified during generation and evaluated later against runtime counter values only when their dependency events exist.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/s390/mapfile.csv maps IBM family/model regular expressions to cf_z* directories as core events.
- `tools/perf/pmu-events/metric.py` parses `MetricExpr`; formulas depend on referenced event aliases being present in the same CPU table

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Metric expressions are brittle against event renames; `has_event(...)` guards avoid lookup failures but can yield zero-valued metrics when dependency events are absent.
- Several formulas divide by instruction or miss counters; perf metric evaluation must handle zero denominators as defined by the metric parser/runtime.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Run `tools/perf/tests/parse-metric` or metric parser coverage for each `MetricExpr`, including `has_event(...)` fallback behavior.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z16/transaction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z17/basic.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z17/basic.json

## Purpose
This JSON file is a PMU event table for `cf_z17` under the `s390` perf PMU event tree. It provides topic-scoped raw event aliases for s390 cf_z17 `basic` counters. It contains 8 entries and belongs to the `basic` topic.

## Data Contract and Important Fields
- Root shape: JSON array; each element is an event, metric, or architecture-standard reference dictionary.
- Fields present: `BriefDescription, EventCode, EventName, PublicDescription, Unit`.
- Encoding summary: EventCode range 0x0..0x21; Units: CPU-M-CF.
- Representative names: CPU_CYCLES, INSTRUCTIONS, L1I_DIR_WRITES, L1I_PENALTY_CYCLES, L1D_DIR_WRITES, L1D_PENALTY_CYCLES, PROBLEM_STATE_CPU_CYCLES, PROBLEM_STATE_INSTRUCTIONS.
- `BriefDescription` supplies the short user-facing text used in generated perf alias tables.
- `PublicDescription` supplies longer help text when available; `jevents.py` normalizes it into the generated long description field.
- `EventName` is the stable symbolic alias users type in perf commands after generation.
- `EventCode` is parsed as an integer by `jevents.py` and converted into perf event configuration strings.
- `Unit` binds events to a PMU namespace such as `CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`.

## Content Notes
- The cf_z17 `basic` table exposes s390 counter facility aliases such as CPU_CYCLES, INSTRUCTIONS, L1I_DIR_WRITES, L1I_PENALTY_CYCLES, L1D_DIR_WRITES, L1D_PENALTY_CYCLES, PROBLEM_STATE_CPU_CYCLES, PROBLEM_STATE_INSTRUCTIONS.
## Control Flow
At build time, perf traverses `tools/perf/pmu-events/arch`, reads this file because of its `.json` suffix, and feeds each dictionary into `JsonEvent` in `jevents.py`. The generator normalizes names, descriptions, units, numeric event/config fields, architecture-standard references, and metric expressions into generated `pmu-events.c` tables. At runtime, perf chooses a CPU table through the architecture mapfile, then exposes these entries as event aliases or metrics for `perf list`, `perf stat`, and related commands.

## State and Persistence
The file has no runtime state, mutation, or persistence logic of its own. Its persistent effect is generated build output: `pmu-events.c` embeds the normalized strings and numeric encodings into libperf/perf binaries until the JSON changes and the generator is rerun.

## Dependencies and Integration Points
- `tools/perf/pmu-events/jevents.py` parses this JSON and emits generated `pmu-events.c` tables
- `tools/perf/pmu-events/README` defines the JSON/mapfile contract
- perf runtime lookup uses generated `pmu_events_map` entries to expose symbolic event aliases
- arch/s390/mapfile.csv maps IBM family/model regular expressions to cf_z* directories as core events.
- `Unit` selects the Linux PMU namespace through `jevents.py` unit-to-PMU normalization instead of default core PMU handling

## Risks and Edge Cases
- Event and metric names are unique within this file; cross-file duplicates still depend on perf table merge semantics.
- Counter encodings are hardware ABI data; a wrong code builds cleanly but reports misleading measurements at runtime.
- Incorrect `Unit` mapping can place aliases on the wrong PMU (`CPU-M-CF`, `PAI-CRYPTO`, or `PAI-EXT`) and make user event selection fail.

## Test Signals
- Validate JSON syntax and that the root is an array of event dictionaries.
- Build or run the perf PMU generation path (`tools/perf/pmu-events/Build` invoking `jevents.py`) to catch malformed fields and expression parse errors.
- Use `perf list`/alias lookup on matching hardware or a generated-table unit test to confirm symbolic names appear with expected descriptions.
- Confirm generated PMU unit strings match kernel PMU names for the target s390 facility.

## Research Notes
This file was read as structured JSON and summarized from all entries, not sampled. The most important maintenance behavior is preserving the exact event names, hardware codes, unit strings, and metric dependencies expected by perf's generated-table pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z17/basic.json -->

# subset-b-006610 Research

Grouped research for `subset-b-006610`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/pipeline.json

Purpose: Declares frontend/backend stall and slot-accounting PMU aliases for pipeline pressure analysis.

Important data contract: JSON array with 8 entries for the `cortex-a75` `pipeline` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 6 entries carry local descriptions. Representative names: `STALL_FRONTEND`, `STALL_BACKEND`, `LF_STALL`, `PTW_STALL`, `D_LSU_SLOT_FULL`, `LS_IQ_FULL`, `DP_IQ_FULL`, `DE_IQ_FULL`.

Control flow: These events feed direct stall counters and topdown-style metrics; slot events are especially sensitive to the CPU's issue width and `#slots` substitution.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-a75` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, BriefDescription, EventCode, EventName, PublicDescription`. Sibling metrics may consume these stall names together with cycle counters and issue-slot constants.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `STALL_FRONTEND`, `STALL_BACKEND`, `LF_STALL`, `PTW_STALL`, `D_LSU_SLOT_FULL`, and 3 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a75/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a76/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a76/branch.json

Purpose: Declares branch prediction and branch-speculation PMU aliases for perf on this Arm core.

Important data contract: JSON array with 2 entries for the `cortex-a76` `branch` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 2 entries carry local descriptions. Representative names: `BR_MIS_PRED`, `BR_PRED`.

Control flow: The table is consumed as named raw PMU events; branch metrics and `perf stat -e` aliases depend on these names resolving to the CPU's PMU encoding.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-a76` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `BR_MIS_PRED`, `BR_PRED`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a76/branch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a76/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a76/bus.json

Purpose: Declares bus, counter-cycle, and bus read/write access PMU aliases for perf.

Important data contract: JSON array with 5 entries for the `cortex-a76` `bus` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 3 entries carry local descriptions. Representative names: `CPU_CYCLES`, `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`.

Control flow: Perf exposes these as CPU-specific event names used for bandwidth and platform-interconnect accounting; metrics may divide them by cycle events.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-a76` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, BriefDescription, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `CPU_CYCLES`, `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a76/bus.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a76/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a76/cache.json

Purpose: Declares cache hierarchy PMU aliases, including access, refill, writeback, invalidation, read/write, and miss-level events where the CPU supports them.

Important data contract: JSON array with 47 entries for the `cortex-a76` `cache` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 20 entries carry local descriptions. Representative names: `L1I_CACHE_REFILL`, `L1I_TLB_REFILL`, `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_TLB_REFILL`, `L1I_CACHE`, `L1D_CACHE_WB`, `L2D_CACHE`, plus 39 more.

Control flow: Perf maps each `ArchStdEvent` into the generated event table; cache MPKI and miss-ratio metrics rely on these names matching the Arm PMU definitions.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-a76` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, BriefDescription, PublicDescription`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Cache/TLB aliases often differ by generation; copying entries across CPUs without checking support can expose unusable events.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `L1I_CACHE_REFILL`, `L1I_TLB_REFILL`, `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_TLB_REFILL`, and 42 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a76/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a76/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a76/exception.json

Purpose: Declares exception, trap, abort, IRQ/FIQ, and exception-return PMU aliases.

Important data contract: JSON array with 15 entries for the `cortex-a76` `exception` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 1 entries carry local descriptions. Representative names: `EXC_TAKEN`, `MEMORY_ERROR`, `EXC_DABORT`, `EXC_FIQ`, `EXC_HVC`, `EXC_IRQ`, `EXC_PABORT`, `EXC_SMC`, plus 7 more.

Control flow: These aliases let perf count architectural exception activity; consumers use them directly rather than through executable control flow in this file.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-a76` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `EXC_TAKEN`, `MEMORY_ERROR`, `EXC_DABORT`, `EXC_FIQ`, `EXC_HVC`, and 10 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a76/exception.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a76/instruction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a76/instruction.json

Purpose: Declares instruction, retired-operation, speculative-operation, floating-point, and vector-operation PMU aliases for operation-mix analysis.

Important data contract: JSON array with 28 entries for the `cortex-a76` `instruction` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 5 entries carry local descriptions. Representative names: `SW_INCR`, `INST_RETIRED`, `EXC_RETURN`, `CID_WRITE_RETIRED`, `INST_SPEC`, `TTBR_WRITE_RETIRED`, `BR_RETIRED`, `BR_MIS_PRED_RETIRED`, plus 20 more.

Control flow: The generated perf table exposes these names for direct counting and for metrics that calculate IPC, branch rates, scalar/vector mix, and SVE/FP percentages.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-a76` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `SW_INCR`, `INST_RETIRED`, `EXC_RETURN`, `CID_WRITE_RETIRED`, `INST_SPEC`, and 23 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a76/instruction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a76/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a76/memory.json

Purpose: Declares memory-access PMU aliases, including load/store, remote, alignment, checked-access, and memory-error events depending on CPU generation.

Important data contract: JSON array with 7 entries for the `cortex-a76` `memory` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 1 entries carry local descriptions. Representative names: `MEM_ACCESS`, `REMOTE_ACCESS`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `UNALIGNED_LD_SPEC`, `UNALIGNED_ST_SPEC`, `UNALIGNED_LDST_SPEC`.

Control flow: Perf uses these aliases for memory behavior counters and for metric expressions that calculate data-side effectiveness or per-cycle access rates.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-a76` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `MEM_ACCESS`, `REMOTE_ACCESS`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `UNALIGNED_LD_SPEC`, and 2 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a76/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a76/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a76/pipeline.json

Purpose: Declares frontend/backend stall and slot-accounting PMU aliases for pipeline pressure analysis.

Important data contract: JSON array with 2 entries for the `cortex-a76` `pipeline` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 2 entries carry local descriptions. Representative names: `STALL_FRONTEND`, `STALL_BACKEND`.

Control flow: These events feed direct stall counters and topdown-style metrics; slot events are especially sensitive to the CPU's issue width and `#slots` substitution.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-a76` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics may consume these stall names together with cycle counters and issue-slot constants.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `STALL_FRONTEND`, `STALL_BACKEND`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a76/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a77/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a77/branch.json

Purpose: Declares branch prediction and branch-speculation PMU aliases for perf on this Arm core.

Important data contract: JSON array with 5 entries for the `cortex-a77` `branch` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `BR_MIS_PRED`, `BR_PRED`, `BR_IMMED_SPEC`, `BR_RETURN_SPEC`, `BR_INDIRECT_SPEC`.

Control flow: The table is consumed as named raw PMU events; branch metrics and `perf stat -e` aliases depend on these names resolving to the CPU's PMU encoding. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-a77` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `BR_MIS_PRED`, `BR_PRED`, `BR_IMMED_SPEC`, `BR_RETURN_SPEC`, `BR_INDIRECT_SPEC`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a77/branch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a77/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a77/bus.json

Purpose: Declares bus, counter-cycle, and bus read/write access PMU aliases for perf.

Important data contract: JSON array with 5 entries for the `cortex-a77` `bus` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `CPU_CYCLES`, `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`.

Control flow: Perf exposes these as CPU-specific event names used for bandwidth and platform-interconnect accounting; metrics may divide them by cycle events. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-a77` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `CPU_CYCLES`, `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a77/bus.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a77/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a77/cache.json

Purpose: Declares cache hierarchy PMU aliases, including access, refill, writeback, invalidation, read/write, and miss-level events where the CPU supports them.

Important data contract: JSON array with 47 entries for the `cortex-a77` `cache` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `L1I_CACHE_REFILL`, `L1I_TLB_REFILL`, `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_TLB_REFILL`, `L1I_CACHE`, `L1D_CACHE_WB`, `L2D_CACHE`, plus 39 more.

Control flow: Perf maps each `ArchStdEvent` into the generated event table; cache MPKI and miss-ratio metrics rely on these names matching the Arm PMU definitions. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-a77` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Cache/TLB aliases often differ by generation; copying entries across CPUs without checking support can expose unusable events. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `L1I_CACHE_REFILL`, `L1I_TLB_REFILL`, `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_TLB_REFILL`, and 42 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a77/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a77/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a77/exception.json

Purpose: Declares exception, trap, abort, IRQ/FIQ, and exception-return PMU aliases.

Important data contract: JSON array with 15 entries for the `cortex-a77` `exception` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `EXC_TAKEN`, `MEMORY_ERROR`, `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, `EXC_DABORT`, `EXC_IRQ`, `EXC_FIQ`, plus 7 more.

Control flow: These aliases let perf count architectural exception activity; consumers use them directly rather than through executable control flow in this file. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-a77` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `EXC_TAKEN`, `MEMORY_ERROR`, `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, and 10 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a77/exception.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a77/instruction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a77/instruction.json

Purpose: Declares instruction, retired-operation, speculative-operation, floating-point, and vector-operation PMU aliases for operation-mix analysis.

Important data contract: JSON array with 25 entries for the `cortex-a77` `instruction` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `SW_INCR`, `INST_RETIRED`, `EXC_RETURN`, `CID_WRITE_RETIRED`, `INST_SPEC`, `TTBR_WRITE_RETIRED`, `BR_RETIRED`, `BR_MIS_PRED_RETIRED`, plus 17 more.

Control flow: The generated perf table exposes these names for direct counting and for metrics that calculate IPC, branch rates, scalar/vector mix, and SVE/FP percentages. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-a77` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `SW_INCR`, `INST_RETIRED`, `EXC_RETURN`, `CID_WRITE_RETIRED`, `INST_SPEC`, and 20 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a77/instruction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a77/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a77/memory.json

Purpose: Declares memory-access PMU aliases, including load/store, remote, alignment, checked-access, and memory-error events depending on CPU generation.

Important data contract: JSON array with 7 entries for the `cortex-a77` `memory` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `MEM_ACCESS`, `REMOTE_ACCESS`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `UNALIGNED_LD_SPEC`, `UNALIGNED_ST_SPEC`, `UNALIGNED_LDST_SPEC`.

Control flow: Perf uses these aliases for memory behavior counters and for metric expressions that calculate data-side effectiveness or per-cycle access rates. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-a77` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `MEM_ACCESS`, `REMOTE_ACCESS`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `UNALIGNED_LD_SPEC`, and 2 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a77/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a77/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a77/pipeline.json

Purpose: Declares frontend/backend stall and slot-accounting PMU aliases for pipeline pressure analysis.

Important data contract: JSON array with 2 entries for the `cortex-a77` `pipeline` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `STALL_FRONTEND`, `STALL_BACKEND`.

Control flow: These events feed direct stall counters and topdown-style metrics; slot events are especially sensitive to the CPU's issue width and `#slots` substitution. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-a77` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`. Sibling metrics may consume these stall names together with cycle counters and issue-slot constants.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `STALL_FRONTEND`, `STALL_BACKEND`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a77/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a78/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a78/branch.json

Purpose: Declares branch prediction and branch-speculation PMU aliases for perf on this Arm core.

Important data contract: JSON array with 5 entries for the `cortex-a78` `branch` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `BR_MIS_PRED`, `BR_PRED`, `BR_IMMED_SPEC`, `BR_RETURN_SPEC`, `BR_INDIRECT_SPEC`.

Control flow: The table is consumed as named raw PMU events; branch metrics and `perf stat -e` aliases depend on these names resolving to the CPU's PMU encoding. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-a78` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `BR_MIS_PRED`, `BR_PRED`, `BR_IMMED_SPEC`, `BR_RETURN_SPEC`, `BR_INDIRECT_SPEC`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a78/branch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a78/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a78/bus.json

Purpose: Declares bus, counter-cycle, and bus read/write access PMU aliases for perf.

Important data contract: JSON array with 6 entries for the `cortex-a78` `bus` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `CPU_CYCLES`, `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`, `CNT_CYCLES`.

Control flow: Perf exposes these as CPU-specific event names used for bandwidth and platform-interconnect accounting; metrics may divide them by cycle events. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-a78` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `CPU_CYCLES`, `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`, and 1 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a78/bus.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a78/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a78/cache.json

Purpose: Declares cache hierarchy PMU aliases, including access, refill, writeback, invalidation, read/write, and miss-level events where the CPU supports them.

Important data contract: JSON array with 51 entries for the `cortex-a78` `cache` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `L1I_CACHE_REFILL`, `L1I_TLB_REFILL`, `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_TLB_REFILL`, `L1I_CACHE`, `L1D_CACHE_WB`, `L2D_CACHE`, plus 43 more.

Control flow: Perf maps each `ArchStdEvent` into the generated event table; cache MPKI and miss-ratio metrics rely on these names matching the Arm PMU definitions. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-a78` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Cache/TLB aliases often differ by generation; copying entries across CPUs without checking support can expose unusable events. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `L1I_CACHE_REFILL`, `L1I_TLB_REFILL`, `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_TLB_REFILL`, and 46 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a78/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a78/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a78/exception.json

Purpose: Declares exception, trap, abort, IRQ/FIQ, and exception-return PMU aliases.

Important data contract: JSON array with 15 entries for the `cortex-a78` `exception` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `EXC_TAKEN`, `MEMORY_ERROR`, `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, `EXC_DABORT`, `EXC_IRQ`, `EXC_FIQ`, plus 7 more.

Control flow: These aliases let perf count architectural exception activity; consumers use them directly rather than through executable control flow in this file. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-a78` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `EXC_TAKEN`, `MEMORY_ERROR`, `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, and 10 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a78/exception.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a78/instruction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a78/instruction.json

Purpose: Declares instruction, retired-operation, speculative-operation, floating-point, and vector-operation PMU aliases for operation-mix analysis.

Important data contract: JSON array with 26 entries for the `cortex-a78` `instruction` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `SW_INCR`, `INST_RETIRED`, `EXC_RETURN`, `CID_WRITE_RETIRED`, `INST_SPEC`, `TTBR_WRITE_RETIRED`, `BR_RETIRED`, `BR_MIS_PRED_RETIRED`, plus 18 more.

Control flow: The generated perf table exposes these names for direct counting and for metrics that calculate IPC, branch rates, scalar/vector mix, and SVE/FP percentages. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-a78` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `SW_INCR`, `INST_RETIRED`, `EXC_RETURN`, `CID_WRITE_RETIRED`, `INST_SPEC`, and 21 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a78/instruction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a78/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a78/memory.json

Purpose: Declares memory-access PMU aliases, including load/store, remote, alignment, checked-access, and memory-error events depending on CPU generation.

Important data contract: JSON array with 7 entries for the `cortex-a78` `memory` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `MEM_ACCESS`, `REMOTE_ACCESS`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `UNALIGNED_LD_SPEC`, `UNALIGNED_ST_SPEC`, `UNALIGNED_LDST_SPEC`.

Control flow: Perf uses these aliases for memory behavior counters and for metric expressions that calculate data-side effectiveness or per-cycle access rates. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-a78` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `MEM_ACCESS`, `REMOTE_ACCESS`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `UNALIGNED_LD_SPEC`, and 2 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a78/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a78/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a78/pipeline.json

Purpose: Declares frontend/backend stall and slot-accounting PMU aliases for pipeline pressure analysis.

Important data contract: JSON array with 7 entries for the `cortex-a78` `pipeline` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `STALL_FRONTEND`, `STALL_BACKEND`, `STALL`, `STALL_SLOT_BACKEND`, `STALL_SLOT_FRONTEND`, `STALL_SLOT`, `STALL_BACKEND_MEM`.

Control flow: These events feed direct stall counters and topdown-style metrics; slot events are especially sensitive to the CPU's issue width and `#slots` substitution. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-a78` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`. Sibling metrics may consume these stall names together with cycle counters and issue-slot constants.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `STALL_FRONTEND`, `STALL_BACKEND`, `STALL`, `STALL_SLOT_BACKEND`, `STALL_SLOT_FRONTEND`, and 2 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-a78/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x1/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x1/branch.json

Purpose: Declares branch prediction and branch-speculation PMU aliases for perf on this Arm core.

Important data contract: JSON array with 5 entries for the `cortex-x1` `branch` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `BR_MIS_PRED`, `BR_PRED`, `BR_IMMED_SPEC`, `BR_RETURN_SPEC`, `BR_INDIRECT_SPEC`.

Control flow: The table is consumed as named raw PMU events; branch metrics and `perf stat -e` aliases depend on these names resolving to the CPU's PMU encoding. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-x1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `BR_MIS_PRED`, `BR_PRED`, `BR_IMMED_SPEC`, `BR_RETURN_SPEC`, `BR_INDIRECT_SPEC`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x1/branch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x1/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x1/bus.json

Purpose: Declares bus, counter-cycle, and bus read/write access PMU aliases for perf.

Important data contract: JSON array with 6 entries for the `cortex-x1` `bus` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `CPU_CYCLES`, `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`, `CNT_CYCLES`.

Control flow: Perf exposes these as CPU-specific event names used for bandwidth and platform-interconnect accounting; metrics may divide them by cycle events. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-x1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `CPU_CYCLES`, `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`, and 1 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x1/bus.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x1/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x1/cache.json

Purpose: Declares cache hierarchy PMU aliases, including access, refill, writeback, invalidation, read/write, and miss-level events where the CPU supports them.

Important data contract: JSON array with 51 entries for the `cortex-x1` `cache` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `L1I_CACHE_REFILL`, `L1I_TLB_REFILL`, `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_TLB_REFILL`, `L1I_CACHE`, `L1D_CACHE_WB`, `L2D_CACHE`, plus 43 more.

Control flow: Perf maps each `ArchStdEvent` into the generated event table; cache MPKI and miss-ratio metrics rely on these names matching the Arm PMU definitions. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-x1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Cache/TLB aliases often differ by generation; copying entries across CPUs without checking support can expose unusable events. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `L1I_CACHE_REFILL`, `L1I_TLB_REFILL`, `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_TLB_REFILL`, and 46 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x1/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x1/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x1/exception.json

Purpose: Declares exception, trap, abort, IRQ/FIQ, and exception-return PMU aliases.

Important data contract: JSON array with 15 entries for the `cortex-x1` `exception` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `EXC_TAKEN`, `MEMORY_ERROR`, `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, `EXC_DABORT`, `EXC_IRQ`, `EXC_FIQ`, plus 7 more.

Control flow: These aliases let perf count architectural exception activity; consumers use them directly rather than through executable control flow in this file. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-x1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `EXC_TAKEN`, `MEMORY_ERROR`, `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, and 10 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x1/exception.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x1/instruction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x1/instruction.json

Purpose: Declares instruction, retired-operation, speculative-operation, floating-point, and vector-operation PMU aliases for operation-mix analysis.

Important data contract: JSON array with 26 entries for the `cortex-x1` `instruction` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `SW_INCR`, `INST_RETIRED`, `EXC_RETURN`, `CID_WRITE_RETIRED`, `INST_SPEC`, `TTBR_WRITE_RETIRED`, `BR_RETIRED`, `BR_MIS_PRED_RETIRED`, plus 18 more.

Control flow: The generated perf table exposes these names for direct counting and for metrics that calculate IPC, branch rates, scalar/vector mix, and SVE/FP percentages. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-x1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `SW_INCR`, `INST_RETIRED`, `EXC_RETURN`, `CID_WRITE_RETIRED`, `INST_SPEC`, and 21 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x1/instruction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x1/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x1/memory.json

Purpose: Declares memory-access PMU aliases, including load/store, remote, alignment, checked-access, and memory-error events depending on CPU generation.

Important data contract: JSON array with 7 entries for the `cortex-x1` `memory` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `MEM_ACCESS`, `REMOTE_ACCESS`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `UNALIGNED_LD_SPEC`, `UNALIGNED_ST_SPEC`, `UNALIGNED_LDST_SPEC`.

Control flow: Perf uses these aliases for memory behavior counters and for metric expressions that calculate data-side effectiveness or per-cycle access rates. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-x1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `MEM_ACCESS`, `REMOTE_ACCESS`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `UNALIGNED_LD_SPEC`, and 2 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x1/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x1/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x1/pipeline.json

Purpose: Declares frontend/backend stall and slot-accounting PMU aliases for pipeline pressure analysis.

Important data contract: JSON array with 7 entries for the `cortex-x1` `pipeline` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `STALL_FRONTEND`, `STALL_BACKEND`, `STALL`, `STALL_SLOT_BACKEND`, `STALL_SLOT_FRONTEND`, `STALL_SLOT`, `STALL_BACKEND_MEM`.

Control flow: These events feed direct stall counters and topdown-style metrics; slot events are especially sensitive to the CPU's issue width and `#slots` substitution. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-x1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`. Sibling metrics may consume these stall names together with cycle counters and issue-slot constants.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `STALL_FRONTEND`, `STALL_BACKEND`, `STALL`, `STALL_SLOT_BACKEND`, `STALL_SLOT_FRONTEND`, and 2 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x1/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/branch.json

Purpose: Declares branch prediction and branch-speculation PMU aliases for perf on this Arm core.

Important data contract: JSON array with 5 entries for the `cortex-x2` `branch` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `BR_MIS_PRED`, `BR_PRED`, `BR_IMMED_SPEC`, `BR_RETURN_SPEC`, `BR_INDIRECT_SPEC`.

Control flow: The table is consumed as named raw PMU events; branch metrics and `perf stat -e` aliases depend on these names resolving to the CPU's PMU encoding. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-x2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `BR_MIS_PRED`, `BR_PRED`, `BR_IMMED_SPEC`, `BR_RETURN_SPEC`, `BR_INDIRECT_SPEC`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/branch.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/bus.json

Purpose: Declares bus, counter-cycle, and bus read/write access PMU aliases for perf.

Important data contract: JSON array with 6 entries for the `cortex-x2` `bus` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `CPU_CYCLES`, `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`, `CNT_CYCLES`.

Control flow: Perf exposes these as CPU-specific event names used for bandwidth and platform-interconnect accounting; metrics may divide them by cycle events. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-x2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `CPU_CYCLES`, `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`, and 1 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/bus.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/cache.json

Purpose: Declares cache hierarchy PMU aliases, including access, refill, writeback, invalidation, read/write, and miss-level events where the CPU supports them.

Important data contract: JSON array with 51 entries for the `cortex-x2` `cache` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `L1I_CACHE_REFILL`, `L1I_TLB_REFILL`, `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_TLB_REFILL`, `L1I_CACHE`, `L1D_CACHE_WB`, `L2D_CACHE`, plus 43 more.

Control flow: Perf maps each `ArchStdEvent` into the generated event table; cache MPKI and miss-ratio metrics rely on these names matching the Arm PMU definitions. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-x2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Cache/TLB aliases often differ by generation; copying entries across CPUs without checking support can expose unusable events. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `L1I_CACHE_REFILL`, `L1I_TLB_REFILL`, `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_TLB_REFILL`, and 46 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/exception.json

Purpose: Declares exception, trap, abort, IRQ/FIQ, and exception-return PMU aliases.

Important data contract: JSON array with 15 entries for the `cortex-x2` `exception` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `EXC_TAKEN`, `MEMORY_ERROR`, `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, `EXC_DABORT`, `EXC_IRQ`, `EXC_FIQ`, plus 7 more.

Control flow: These aliases let perf count architectural exception activity; consumers use them directly rather than through executable control flow in this file. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-x2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `EXC_TAKEN`, `MEMORY_ERROR`, `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, and 10 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/exception.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/instruction.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/instruction.json

Purpose: Declares instruction, retired-operation, speculative-operation, floating-point, and vector-operation PMU aliases for operation-mix analysis.

Important data contract: JSON array with 44 entries for the `cortex-x2` `instruction` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `SW_INCR`, `INST_RETIRED`, `EXC_RETURN`, `CID_WRITE_RETIRED`, `INST_SPEC`, `TTBR_WRITE_RETIRED`, `BR_RETIRED`, `BR_MIS_PRED_RETIRED`, plus 36 more.

Control flow: The generated perf table exposes these names for direct counting and for metrics that calculate IPC, branch rates, scalar/vector mix, and SVE/FP percentages. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-x2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `SW_INCR`, `INST_RETIRED`, `EXC_RETURN`, `CID_WRITE_RETIRED`, `INST_SPEC`, and 39 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/instruction.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/memory.json

Purpose: Declares memory-access PMU aliases, including load/store, remote, alignment, checked-access, and memory-error events depending on CPU generation.

Important data contract: JSON array with 13 entries for the `cortex-x2` `memory` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `MEM_ACCESS`, `REMOTE_ACCESS`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `UNALIGNED_LD_SPEC`, `UNALIGNED_ST_SPEC`, `UNALIGNED_LDST_SPEC`, `LDST_ALIGN_LAT`, plus 5 more.

Control flow: Perf uses these aliases for memory behavior counters and for metric expressions that calculate data-side effectiveness or per-cycle access rates. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-x2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `MEM_ACCESS`, `REMOTE_ACCESS`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `UNALIGNED_LD_SPEC`, and 8 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/pipeline.json

Purpose: Declares frontend/backend stall and slot-accounting PMU aliases for pipeline pressure analysis.

Important data contract: JSON array with 7 entries for the `cortex-x2` `pipeline` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `STALL_FRONTEND`, `STALL_BACKEND`, `STALL`, `STALL_SLOT_BACKEND`, `STALL_SLOT_FRONTEND`, `STALL_SLOT`, `STALL_BACKEND_MEM`.

Control flow: These events feed direct stall counters and topdown-style metrics; slot events are especially sensitive to the CPU's issue width and `#slots` substitution. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-x2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`. Sibling metrics may consume these stall names together with cycle counters and issue-slot constants.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `STALL_FRONTEND`, `STALL_BACKEND`, `STALL`, `STALL_SLOT_BACKEND`, `STALL_SLOT_FRONTEND`, and 2 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/trace.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/trace.json

Purpose: Declares trace buffer, trace external output, and CTI trigger PMU aliases.

Important data contract: JSON array with 9 entries for the `cortex-x2` `trace` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 0 entries carry local descriptions. Representative names: `TRB_WRAP`, `TRCEXTOUT0`, `TRCEXTOUT1`, `TRCEXTOUT2`, `TRCEXTOUT3`, `CTI_TRIGOUT4`, `CTI_TRIGOUT5`, `CTI_TRIGOUT6`, plus 1 more.

Control flow: Perf exposes the trace/CTI event names when the CPU PMU advertises them, allowing low-level trace integration counters to be selected by name. This file intentionally carries only event identifiers, so public descriptions are inherited from shared Arm event metadata or omitted in generated help.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `cortex-x2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Because descriptions are absent, `perf list` help text may be sparse and reviewers must verify meanings from shared metadata or vendor docs.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `TRB_WRAP`, `TRCEXTOUT0`, `TRCEXTOUT1`, `TRCEXTOUT2`, `TRCEXTOUT3`, and 4 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/cortex-x2/trace.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/bus.json

Purpose: Declares bus, counter-cycle, and bus read/write access PMU aliases for perf.

Important data contract: JSON array with 4 entries for the `neoverse-n1` `bus` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 4 entries carry local descriptions. Representative names: `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`.

Control flow: Perf exposes these as CPU-specific event names used for bandwidth and platform-interconnect accounting; metrics may divide them by cycle events.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/bus.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/exception.json

Purpose: Declares exception, trap, abort, IRQ/FIQ, and exception-return PMU aliases.

Important data contract: JSON array with 15 entries for the `neoverse-n1` `exception` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 15 entries carry local descriptions. Representative names: `EXC_TAKEN`, `EXC_RETURN`, `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, `EXC_DABORT`, `EXC_IRQ`, `EXC_FIQ`, plus 7 more.

Control flow: These aliases let perf count architectural exception activity; consumers use them directly rather than through executable control flow in this file.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `EXC_TAKEN`, `EXC_RETURN`, `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, and 10 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/exception.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/general.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/general.json

Purpose: Declares general cycle-counting PMU aliases for this Neoverse CPU.

Important data contract: JSON array with 1 entries for the `neoverse-n1` `general` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 1 entries carry local descriptions. Representative names: `CPU_CYCLES`.

Control flow: These cycle aliases are foundational dependencies for IPC, stall, topdown, and percentage metrics in sibling metric tables.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `CPU_CYCLES`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/general.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/l1d_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/l1d_cache.json

Purpose: Declares cache hierarchy PMU aliases, including access, refill, writeback, invalidation, read/write, and miss-level events where the CPU supports them.

Important data contract: JSON array with 12 entries for the `neoverse-n1` `l1d cache` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 12 entries carry local descriptions. Representative names: `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_CACHE_WB`, `L1D_CACHE_RD`, `L1D_CACHE_WR`, `L1D_CACHE_REFILL_RD`, `L1D_CACHE_REFILL_WR`, `L1D_CACHE_REFILL_INNER`, plus 4 more.

Control flow: Perf maps each `ArchStdEvent` into the generated event table; cache MPKI and miss-ratio metrics rely on these names matching the Arm PMU definitions.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Cache/TLB aliases often differ by generation; copying entries across CPUs without checking support can expose unusable events.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_CACHE_WB`, `L1D_CACHE_RD`, `L1D_CACHE_WR`, and 7 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/l1d_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/l1i_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/l1i_cache.json

Purpose: Declares cache hierarchy PMU aliases, including access, refill, writeback, invalidation, read/write, and miss-level events where the CPU supports them.

Important data contract: JSON array with 2 entries for the `neoverse-n1` `l1i cache` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 2 entries carry local descriptions. Representative names: `L1I_CACHE_REFILL`, `L1I_CACHE`.

Control flow: Perf maps each `ArchStdEvent` into the generated event table; cache MPKI and miss-ratio metrics rely on these names matching the Arm PMU definitions.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `L1I_CACHE_REFILL`, `L1I_CACHE`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/l1i_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/l2_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/l2_cache.json

Purpose: Declares cache hierarchy PMU aliases, including access, refill, writeback, invalidation, read/write, and miss-level events where the CPU supports them.

Important data contract: JSON array with 11 entries for the `neoverse-n1` `l2 cache` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 11 entries carry local descriptions. Representative names: `L2D_CACHE`, `L2D_CACHE_REFILL`, `L2D_CACHE_WB`, `L2D_CACHE_ALLOCATE`, `L2D_CACHE_RD`, `L2D_CACHE_WR`, `L2D_CACHE_REFILL_RD`, `L2D_CACHE_REFILL_WR`, plus 3 more.

Control flow: Perf maps each `ArchStdEvent` into the generated event table; cache MPKI and miss-ratio metrics rely on these names matching the Arm PMU definitions.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Cache/TLB aliases often differ by generation; copying entries across CPUs without checking support can expose unusable events.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `L2D_CACHE`, `L2D_CACHE_REFILL`, `L2D_CACHE_WB`, `L2D_CACHE_ALLOCATE`, `L2D_CACHE_RD`, and 6 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/l2_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/l3_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/l3_cache.json

Purpose: Declares cache hierarchy PMU aliases, including access, refill, writeback, invalidation, read/write, and miss-level events where the CPU supports them.

Important data contract: JSON array with 4 entries for the `neoverse-n1` `l3 cache` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 4 entries carry local descriptions. Representative names: `L3D_CACHE_ALLOCATE`, `L3D_CACHE_REFILL`, `L3D_CACHE`, `L3D_CACHE_RD`.

Control flow: Perf maps each `ArchStdEvent` into the generated event table; cache MPKI and miss-ratio metrics rely on these names matching the Arm PMU definitions.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Cache/TLB aliases often differ by generation; copying entries across CPUs without checking support can expose unusable events.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `L3D_CACHE_ALLOCATE`, `L3D_CACHE_REFILL`, `L3D_CACHE`, `L3D_CACHE_RD`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/l3_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/ll_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/ll_cache.json

Purpose: Declares cache hierarchy PMU aliases, including access, refill, writeback, invalidation, read/write, and miss-level events where the CPU supports them.

Important data contract: JSON array with 2 entries for the `neoverse-n1` `ll cache` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 2 entries carry local descriptions. Representative names: `LL_CACHE_RD`, `LL_CACHE_MISS_RD`.

Control flow: Perf maps each `ArchStdEvent` into the generated event table; cache MPKI and miss-ratio metrics rely on these names matching the Arm PMU definitions.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `LL_CACHE_RD`, `LL_CACHE_MISS_RD`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/ll_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/memory.json

Purpose: Declares memory-access PMU aliases, including load/store, remote, alignment, checked-access, and memory-error events depending on CPU generation.

Important data contract: JSON array with 5 entries for the `neoverse-n1` `memory` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 5 entries carry local descriptions. Representative names: `MEM_ACCESS`, `MEMORY_ERROR`, `REMOTE_ACCESS`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`.

Control flow: Perf uses these aliases for memory behavior counters and for metric expressions that calculate data-side effectiveness or per-cycle access rates.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `MEM_ACCESS`, `MEMORY_ERROR`, `REMOTE_ACCESS`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/metrics.json

Purpose: Defines derived perf metrics rather than raw programmable events. The entries combine architected PMU event names into ratios, MPKI values, operation-mix percentages, and cycle/topdown-style accounting formulas for this CPU.

Important data contract: JSON array with 31 entries for the `neoverse-n1` `metrics` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 31 entries carry local descriptions and 31 entries carry `MetricExpr` formulas. Representative names: `backend_stalled_cycles`, `branch_misprediction_ratio`, `branch_mpki`, `branch_percentage`, `crypto_percentage`, `dtlb_mpki`, `dtlb_walk_ratio`, `frontend_stalled_cycles`, plus 23 more.

Control flow: Perf's pmu-events generator preserves each `MetricName`, parses `MetricExpr`, and resolves referenced event tokens against sibling event JSON tables for the same CPU map. Runtime selection evaluates the expression over counters collected in the same stat session. Metric groups represented include Cycle_Accounting, General, LL_Cache_Effectiveness, MPKI;Branch_Effectiveness, MPKI;DTLB_Effectiveness, MPKI;ITLB_Effectiveness, plus 14 more.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n1` directory for matching MIDR/CPUID values. Schema fields present here are `BriefDescription, MetricExpr, MetricGroup, MetricName, ScaleUnit`. Metric expressions reference sibling raw events such as ASE_SPEC, BR_IMMED_SPEC, BR_INDIRECT_SPEC, BR_MIS_PRED_RETIRED, BR_RETIRED, CPU_CYCLES, CRYPTO_SPEC, DP_SPEC, DTLB_WALK, INST_RETIRED, plus 21 more tokens.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Metric expressions can silently become misleading if referenced raw events are renamed, unavailable for a CPU revision, or have divide-by-zero behavior on short runs. Expressions using `#slots` or `strcmp_cpuid_str` are tightly coupled to perf's metric parser and CPU identification helpers.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `backend_stalled_cycles`, `branch_misprediction_ratio`, `branch_mpki`, `branch_percentage`, `crypto_percentage`, and 26 more. Run `perf stat -M` for representative metrics and check expression parsing, event grouping, and zero-denominator handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/retired.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/retired.json

Purpose: Declares instruction, retired-operation, speculative-operation, floating-point, and vector-operation PMU aliases for operation-mix analysis.

Important data contract: JSON array with 6 entries for the `neoverse-n1` `retired` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 6 entries carry local descriptions. Representative names: `SW_INCR`, `INST_RETIRED`, `CID_WRITE_RETIRED`, `TTBR_WRITE_RETIRED`, `BR_RETIRED`, `BR_MIS_PRED_RETIRED`.

Control flow: The generated perf table exposes these names for direct counting and for metrics that calculate IPC, branch rates, scalar/vector mix, and SVE/FP percentages.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `SW_INCR`, `INST_RETIRED`, `CID_WRITE_RETIRED`, `TTBR_WRITE_RETIRED`, `BR_RETIRED`, and 1 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/retired.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/spe.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/spe.json

Purpose: Declares Statistical Profiling Extension sampling pipeline PMU aliases.

Important data contract: JSON array with 4 entries for the `neoverse-n1` `spe` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 4 entries carry local descriptions. Representative names: `SAMPLE_POP`, `SAMPLE_FEED`, `SAMPLE_FILTRATE`, `SAMPLE_COLLISION`.

Control flow: Perf exposes these names for SPE feed/pop/filter/collision accounting; they complement, but do not configure, SPE sampling itself.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `SAMPLE_POP`, `SAMPLE_FEED`, `SAMPLE_FILTRATE`, `SAMPLE_COLLISION`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/spe.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/spec_operation.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/spec_operation.json

Purpose: Declares instruction, retired-operation, speculative-operation, floating-point, and vector-operation PMU aliases for operation-mix analysis.

Important data contract: JSON array with 25 entries for the `neoverse-n1` `spec operation` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 25 entries carry local descriptions. Representative names: `BR_MIS_PRED`, `BR_PRED`, `INST_SPEC`, `UNALIGNED_LD_SPEC`, `UNALIGNED_ST_SPEC`, `UNALIGNED_LDST_SPEC`, `LDREX_SPEC`, `STREX_PASS_SPEC`, plus 17 more.

Control flow: The generated perf table exposes these names for direct counting and for metrics that calculate IPC, branch rates, scalar/vector mix, and SVE/FP percentages.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `BR_MIS_PRED`, `BR_PRED`, `INST_SPEC`, `UNALIGNED_LD_SPEC`, `UNALIGNED_ST_SPEC`, and 20 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/spec_operation.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/stall.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/stall.json

Purpose: Declares frontend/backend stall and slot-accounting PMU aliases for pipeline pressure analysis.

Important data contract: JSON array with 2 entries for the `neoverse-n1` `stall` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 2 entries carry local descriptions. Representative names: `STALL_FRONTEND`, `STALL_BACKEND`.

Control flow: These events feed direct stall counters and topdown-style metrics; slot events are especially sensitive to the CPU's issue width and `#slots` substitution.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics may consume these stall names together with cycle counters and issue-slot constants.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `STALL_FRONTEND`, `STALL_BACKEND`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/stall.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/tlb.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/tlb.json

Purpose: Declares instruction/data TLB access, refill, read/write, and walk PMU aliases.

Important data contract: JSON array with 16 entries for the `neoverse-n1` `tlb` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 16 entries carry local descriptions. Representative names: `L1I_TLB_REFILL`, `L1D_TLB_REFILL`, `L1D_TLB`, `L1I_TLB`, `L2D_TLB_REFILL`, `L2D_TLB`, `DTLB_WALK`, `ITLB_WALK`, plus 8 more.

Control flow: Perf maps these aliases into generated event tables used for TLB miss ratios, MPKI metrics, and direct page-walk counters.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Cache/TLB aliases often differ by generation; copying entries across CPUs without checking support can expose unusable events.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `L1I_TLB_REFILL`, `L1D_TLB_REFILL`, `L1D_TLB`, `L1I_TLB`, `L2D_TLB_REFILL`, and 11 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n1/tlb.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/bus.json

Purpose: Declares bus, counter-cycle, and bus read/write access PMU aliases for perf.

Important data contract: JSON array with 4 entries for the `neoverse-n2-v2` `bus` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 4 entries carry local descriptions. Representative names: `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`.

Control flow: Perf exposes these as CPU-specific event names used for bandwidth and platform-interconnect accounting; metrics may divide them by cycle events.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n2-v2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/bus.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/exception.json

Purpose: Declares exception, trap, abort, IRQ/FIQ, and exception-return PMU aliases.

Important data contract: JSON array with 15 entries for the `neoverse-n2-v2` `exception` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 15 entries carry local descriptions. Representative names: `EXC_TAKEN`, `EXC_RETURN`, `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, `EXC_DABORT`, `EXC_IRQ`, `EXC_FIQ`, plus 7 more.

Control flow: These aliases let perf count architectural exception activity; consumers use them directly rather than through executable control flow in this file.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n2-v2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `EXC_TAKEN`, `EXC_RETURN`, `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, and 10 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/exception.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/fp_operation.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/fp_operation.json

Purpose: Declares instruction, retired-operation, speculative-operation, floating-point, and vector-operation PMU aliases for operation-mix analysis.

Important data contract: JSON array with 5 entries for the `neoverse-n2-v2` `fp operation` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 5 entries carry local descriptions. Representative names: `FP_HP_SPEC`, `FP_SP_SPEC`, `FP_DP_SPEC`, `FP_SCALE_OPS_SPEC`, `FP_FIXED_OPS_SPEC`.

Control flow: The generated perf table exposes these names for direct counting and for metrics that calculate IPC, branch rates, scalar/vector mix, and SVE/FP percentages.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n2-v2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `FP_HP_SPEC`, `FP_SP_SPEC`, `FP_DP_SPEC`, `FP_SCALE_OPS_SPEC`, `FP_FIXED_OPS_SPEC`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/fp_operation.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/general.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/general.json

Purpose: Declares general cycle-counting PMU aliases for this Neoverse CPU.

Important data contract: JSON array with 2 entries for the `neoverse-n2-v2` `general` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 2 entries carry local descriptions. Representative names: `CPU_CYCLES`, `CNT_CYCLES`.

Control flow: These cycle aliases are foundational dependencies for IPC, stall, topdown, and percentage metrics in sibling metric tables.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n2-v2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `CPU_CYCLES`, `CNT_CYCLES`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/general.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/l1d_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/l1d_cache.json

Purpose: Declares cache hierarchy PMU aliases, including access, refill, writeback, invalidation, read/write, and miss-level events where the CPU supports them.

Important data contract: JSON array with 13 entries for the `neoverse-n2-v2` `l1d cache` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 13 entries carry local descriptions. Representative names: `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_CACHE_WB`, `L1D_CACHE_LMISS_RD`, `L1D_CACHE_RD`, `L1D_CACHE_WR`, `L1D_CACHE_REFILL_RD`, `L1D_CACHE_REFILL_WR`, plus 5 more.

Control flow: Perf maps each `ArchStdEvent` into the generated event table; cache MPKI and miss-ratio metrics rely on these names matching the Arm PMU definitions.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n2-v2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Cache/TLB aliases often differ by generation; copying entries across CPUs without checking support can expose unusable events.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_CACHE_WB`, `L1D_CACHE_LMISS_RD`, `L1D_CACHE_RD`, and 8 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/l1d_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/l1i_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/l1i_cache.json

Purpose: Declares cache hierarchy PMU aliases, including access, refill, writeback, invalidation, read/write, and miss-level events where the CPU supports them.

Important data contract: JSON array with 3 entries for the `neoverse-n2-v2` `l1i cache` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 3 entries carry local descriptions. Representative names: `L1I_CACHE_REFILL`, `L1I_CACHE`, `L1I_CACHE_LMISS`.

Control flow: Perf maps each `ArchStdEvent` into the generated event table; cache MPKI and miss-ratio metrics rely on these names matching the Arm PMU definitions.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n2-v2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `L1I_CACHE_REFILL`, `L1I_CACHE`, `L1I_CACHE_LMISS`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/l1i_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/l2_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/l2_cache.json

Purpose: Declares cache hierarchy PMU aliases, including access, refill, writeback, invalidation, read/write, and miss-level events where the CPU supports them.

Important data contract: JSON array with 12 entries for the `neoverse-n2-v2` `l2 cache` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 12 entries carry local descriptions. Representative names: `L2D_CACHE`, `L2D_CACHE_REFILL`, `L2D_CACHE_WB`, `L2D_CACHE_ALLOCATE`, `L2D_CACHE_RD`, `L2D_CACHE_WR`, `L2D_CACHE_REFILL_RD`, `L2D_CACHE_REFILL_WR`, plus 4 more.

Control flow: Perf maps each `ArchStdEvent` into the generated event table; cache MPKI and miss-ratio metrics rely on these names matching the Arm PMU definitions.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n2-v2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Cache/TLB aliases often differ by generation; copying entries across CPUs without checking support can expose unusable events.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `L2D_CACHE`, `L2D_CACHE_REFILL`, `L2D_CACHE_WB`, `L2D_CACHE_ALLOCATE`, `L2D_CACHE_RD`, and 7 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/l2_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/l3_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/l3_cache.json

Purpose: Declares cache hierarchy PMU aliases, including access, refill, writeback, invalidation, read/write, and miss-level events where the CPU supports them.

Important data contract: JSON array with 5 entries for the `neoverse-n2-v2` `l3 cache` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 5 entries carry local descriptions. Representative names: `L3D_CACHE_ALLOCATE`, `L3D_CACHE_REFILL`, `L3D_CACHE`, `L3D_CACHE_RD`, `L3D_CACHE_LMISS_RD`.

Control flow: Perf maps each `ArchStdEvent` into the generated event table; cache MPKI and miss-ratio metrics rely on these names matching the Arm PMU definitions.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n2-v2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Cache/TLB aliases often differ by generation; copying entries across CPUs without checking support can expose unusable events.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `L3D_CACHE_ALLOCATE`, `L3D_CACHE_REFILL`, `L3D_CACHE`, `L3D_CACHE_RD`, `L3D_CACHE_LMISS_RD`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/l3_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/ll_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/ll_cache.json

Purpose: Declares cache hierarchy PMU aliases, including access, refill, writeback, invalidation, read/write, and miss-level events where the CPU supports them.

Important data contract: JSON array with 2 entries for the `neoverse-n2-v2` `ll cache` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 2 entries carry local descriptions. Representative names: `LL_CACHE_RD`, `LL_CACHE_MISS_RD`.

Control flow: Perf maps each `ArchStdEvent` into the generated event table; cache MPKI and miss-ratio metrics rely on these names matching the Arm PMU definitions.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n2-v2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `LL_CACHE_RD`, `LL_CACHE_MISS_RD`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/ll_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/memory.json

Purpose: Declares memory-access PMU aliases, including load/store, remote, alignment, checked-access, and memory-error events depending on CPU generation.

Important data contract: JSON array with 11 entries for the `neoverse-n2-v2` `memory` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 11 entries carry local descriptions. Representative names: `MEM_ACCESS`, `MEMORY_ERROR`, `REMOTE_ACCESS`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `LDST_ALIGN_LAT`, `LD_ALIGN_LAT`, `ST_ALIGN_LAT`, plus 3 more.

Control flow: Perf uses these aliases for memory behavior counters and for metric expressions that calculate data-side effectiveness or per-cycle access rates.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n2-v2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `MEM_ACCESS`, `MEMORY_ERROR`, `REMOTE_ACCESS`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, and 6 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/metrics.json

Purpose: Defines derived perf metrics rather than raw programmable events. The entries combine architected PMU event names into ratios, MPKI values, operation-mix percentages, and cycle/topdown-style accounting formulas for this CPU.

Important data contract: JSON array with 46 entries for the `neoverse-n2-v2` `metrics` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 42 entries carry local descriptions and 46 entries carry `MetricExpr` formulas. Representative names: `backend_bound`, `backend_stalled_cycles`, `bad_speculation`, `branch_misprediction_ratio`, `branch_mpki`, `branch_percentage`, `crypto_percentage`, `dtlb_mpki`, plus 38 more.

Control flow: Perf's pmu-events generator preserves each `MetricName`, parses `MetricExpr`, and resolves referenced event tokens against sibling event JSON tables for the same CPU map. Runtime selection evaluates the expression over counters collected in the same stat session. Metric groups represented include Cycle_Accounting, General, LL_Cache_Effectiveness, MPKI;Branch_Effectiveness, MPKI;DTLB_Effectiveness, MPKI;ITLB_Effectiveness, plus 16 more.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n2-v2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, BriefDescription, MetricExpr, MetricGroup, MetricName, ScaleUnit`. Metric expressions reference sibling raw events such as #slots, ASE_SPEC, BR_IMMED_SPEC, BR_INDIRECT_SPEC, BR_MIS_PRED, BR_MIS_PRED_RETIRED, BR_RETIRED, BR_RETURN_SPEC, CPU_CYCLES, CRYPTO_SPEC, plus 32 more tokens.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Metric expressions can silently become misleading if referenced raw events are renamed, unavailable for a CPU revision, or have divide-by-zero behavior on short runs. Expressions using `#slots` or `strcmp_cpuid_str` are tightly coupled to perf's metric parser and CPU identification helpers.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `backend_bound`, `backend_stalled_cycles`, `bad_speculation`, `branch_misprediction_ratio`, `branch_mpki`, and 41 more. Run `perf stat -M` for representative metrics and check expression parsing, event grouping, and zero-denominator handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/retired.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/retired.json

Purpose: Declares instruction, retired-operation, speculative-operation, floating-point, and vector-operation PMU aliases for operation-mix analysis.

Important data contract: JSON array with 7 entries for the `neoverse-n2-v2` `retired` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 7 entries carry local descriptions. Representative names: `SW_INCR`, `INST_RETIRED`, `CID_WRITE_RETIRED`, `TTBR_WRITE_RETIRED`, `BR_RETIRED`, `BR_MIS_PRED_RETIRED`, `OP_RETIRED`.

Control flow: The generated perf table exposes these names for direct counting and for metrics that calculate IPC, branch rates, scalar/vector mix, and SVE/FP percentages.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n2-v2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `SW_INCR`, `INST_RETIRED`, `CID_WRITE_RETIRED`, `TTBR_WRITE_RETIRED`, `BR_RETIRED`, and 2 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/retired.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/spe.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/spe.json

Purpose: Declares Statistical Profiling Extension sampling pipeline PMU aliases.

Important data contract: JSON array with 4 entries for the `neoverse-n2-v2` `spe` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 4 entries carry local descriptions. Representative names: `SAMPLE_POP`, `SAMPLE_FEED`, `SAMPLE_FILTRATE`, `SAMPLE_COLLISION`.

Control flow: Perf exposes these names for SPE feed/pop/filter/collision accounting; they complement, but do not configure, SPE sampling itself.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n2-v2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `SAMPLE_POP`, `SAMPLE_FEED`, `SAMPLE_FILTRATE`, `SAMPLE_COLLISION`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/spe.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/spec_operation.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/spec_operation.json

Purpose: Declares instruction, retired-operation, speculative-operation, floating-point, and vector-operation PMU aliases for operation-mix analysis.

Important data contract: JSON array with 27 entries for the `neoverse-n2-v2` `spec operation` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 27 entries carry local descriptions. Representative names: `BR_MIS_PRED`, `BR_PRED`, `INST_SPEC`, `OP_SPEC`, `UNALIGNED_LD_SPEC`, `UNALIGNED_ST_SPEC`, `UNALIGNED_LDST_SPEC`, `LDREX_SPEC`, plus 19 more.

Control flow: The generated perf table exposes these names for direct counting and for metrics that calculate IPC, branch rates, scalar/vector mix, and SVE/FP percentages.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n2-v2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `BR_MIS_PRED`, `BR_PRED`, `INST_SPEC`, `OP_SPEC`, `UNALIGNED_LD_SPEC`, and 22 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/spec_operation.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/stall.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/stall.json

Purpose: Declares frontend/backend stall and slot-accounting PMU aliases for pipeline pressure analysis.

Important data contract: JSON array with 7 entries for the `neoverse-n2-v2` `stall` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 7 entries carry local descriptions. Representative names: `STALL_FRONTEND`, `STALL_BACKEND`, `STALL`, `STALL_SLOT_BACKEND`, `STALL_SLOT_FRONTEND`, `STALL_SLOT`, `STALL_BACKEND_MEM`.

Control flow: These events feed direct stall counters and topdown-style metrics; slot events are especially sensitive to the CPU's issue width and `#slots` substitution.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n2-v2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics may consume these stall names together with cycle counters and issue-slot constants.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `STALL_FRONTEND`, `STALL_BACKEND`, `STALL`, `STALL_SLOT_BACKEND`, `STALL_SLOT_FRONTEND`, and 2 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/stall.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/sve.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/sve.json

Purpose: Declares instruction, retired-operation, speculative-operation, floating-point, and vector-operation PMU aliases for operation-mix analysis.

Important data contract: JSON array with 12 entries for the `neoverse-n2-v2` `sve` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 12 entries carry local descriptions. Representative names: `SVE_INST_SPEC`, `SVE_PRED_SPEC`, `SVE_PRED_EMPTY_SPEC`, `SVE_PRED_FULL_SPEC`, `SVE_PRED_PARTIAL_SPEC`, `SVE_PRED_NOT_FULL_SPEC`, `SVE_LDFF_SPEC`, `SVE_LDFF_FAULT_SPEC`, plus 4 more.

Control flow: The generated perf table exposes these names for direct counting and for metrics that calculate IPC, branch rates, scalar/vector mix, and SVE/FP percentages.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n2-v2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `SVE_INST_SPEC`, `SVE_PRED_SPEC`, `SVE_PRED_EMPTY_SPEC`, `SVE_PRED_FULL_SPEC`, `SVE_PRED_PARTIAL_SPEC`, and 7 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/sve.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/tlb.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/tlb.json

Purpose: Declares instruction/data TLB access, refill, read/write, and walk PMU aliases.

Important data contract: JSON array with 16 entries for the `neoverse-n2-v2` `tlb` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 16 entries carry local descriptions. Representative names: `L1I_TLB_REFILL`, `L1D_TLB_REFILL`, `L1D_TLB`, `L1I_TLB`, `L2D_TLB_REFILL`, `L2D_TLB`, `DTLB_WALK`, `ITLB_WALK`, plus 8 more.

Control flow: Perf maps these aliases into generated event tables used for TLB miss ratios, MPKI metrics, and direct page-walk counters.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n2-v2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Cache/TLB aliases often differ by generation; copying entries across CPUs without checking support can expose unusable events.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `L1I_TLB_REFILL`, `L1D_TLB_REFILL`, `L1D_TLB`, `L1I_TLB`, `L2D_TLB_REFILL`, and 11 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/tlb.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/trace.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/trace.json

Purpose: Declares trace buffer, trace external output, and CTI trigger PMU aliases.

Important data contract: JSON array with 9 entries for the `neoverse-n2-v2` `trace` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 9 entries carry local descriptions. Representative names: `TRB_WRAP`, `TRCEXTOUT0`, `TRCEXTOUT1`, `TRCEXTOUT2`, `TRCEXTOUT3`, `CTI_TRIGOUT4`, `CTI_TRIGOUT5`, `CTI_TRIGOUT6`, plus 1 more.

Control flow: Perf exposes the trace/CTI event names when the CPU PMU advertises them, allowing low-level trace integration counters to be selected by name.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n2-v2` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `TRB_WRAP`, `TRCEXTOUT0`, `TRCEXTOUT1`, `TRCEXTOUT2`, `TRCEXTOUT3`, and 4 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n2-v2/trace.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/bus.json

Purpose: Declares bus, counter-cycle, and bus read/write access PMU aliases for perf.

Important data contract: JSON array with 4 entries for the `neoverse-n3` `bus` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 4 entries carry local descriptions. Representative names: `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`.

Control flow: Perf exposes these as CPU-specific event names used for bandwidth and platform-interconnect accounting; metrics may divide them by cycle events.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n3` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/bus.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/exception.json

Purpose: Declares exception, trap, abort, IRQ/FIQ, and exception-return PMU aliases.

Important data contract: JSON array with 15 entries for the `neoverse-n3` `exception` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 15 entries carry local descriptions. Representative names: `EXC_TAKEN`, `EXC_RETURN`, `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, `EXC_DABORT`, `EXC_IRQ`, `EXC_FIQ`, plus 7 more.

Control flow: These aliases let perf count architectural exception activity; consumers use them directly rather than through executable control flow in this file.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n3` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `EXC_TAKEN`, `EXC_RETURN`, `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, and 10 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/exception.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/fp_operation.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/fp_operation.json

Purpose: Declares instruction, retired-operation, speculative-operation, floating-point, and vector-operation PMU aliases for operation-mix analysis.

Important data contract: JSON array with 5 entries for the `neoverse-n3` `fp operation` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 5 entries carry local descriptions. Representative names: `FP_HP_SPEC`, `FP_SP_SPEC`, `FP_DP_SPEC`, `FP_SCALE_OPS_SPEC`, `FP_FIXED_OPS_SPEC`.

Control flow: The generated perf table exposes these names for direct counting and for metrics that calculate IPC, branch rates, scalar/vector mix, and SVE/FP percentages.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n3` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `FP_HP_SPEC`, `FP_SP_SPEC`, `FP_DP_SPEC`, `FP_SCALE_OPS_SPEC`, `FP_FIXED_OPS_SPEC`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/fp_operation.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/general.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/general.json

Purpose: Declares general cycle-counting PMU aliases for this Neoverse CPU.

Important data contract: JSON array with 2 entries for the `neoverse-n3` `general` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 2 entries carry local descriptions. Representative names: `CPU_CYCLES`, `CNT_CYCLES`.

Control flow: These cycle aliases are foundational dependencies for IPC, stall, topdown, and percentage metrics in sibling metric tables.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n3` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `CPU_CYCLES`, `CNT_CYCLES`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/general.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/l1d_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/l1d_cache.json

Purpose: Declares cache hierarchy PMU aliases, including access, refill, writeback, invalidation, read/write, and miss-level events where the CPU supports them.

Important data contract: JSON array with 12 entries for the `neoverse-n3` `l1d cache` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 12 entries carry local descriptions. Representative names: `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_CACHE_WB`, `L1D_CACHE_LMISS_RD`, `L1D_CACHE_RD`, `L1D_CACHE_WR`, `L1D_CACHE_REFILL_INNER`, `L1D_CACHE_REFILL_OUTER`, plus 4 more.

Control flow: Perf maps each `ArchStdEvent` into the generated event table; cache MPKI and miss-ratio metrics rely on these names matching the Arm PMU definitions.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n3` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Cache/TLB aliases often differ by generation; copying entries across CPUs without checking support can expose unusable events.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_CACHE_WB`, `L1D_CACHE_LMISS_RD`, `L1D_CACHE_RD`, and 7 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/l1d_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/l1i_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/l1i_cache.json

Purpose: Declares cache hierarchy PMU aliases, including access, refill, writeback, invalidation, read/write, and miss-level events where the CPU supports them.

Important data contract: JSON array with 3 entries for the `neoverse-n3` `l1i cache` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 3 entries carry local descriptions. Representative names: `L1I_CACHE_REFILL`, `L1I_CACHE`, `L1I_CACHE_LMISS`.

Control flow: Perf maps each `ArchStdEvent` into the generated event table; cache MPKI and miss-ratio metrics rely on these names matching the Arm PMU definitions.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n3` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `L1I_CACHE_REFILL`, `L1I_CACHE`, `L1I_CACHE_LMISS`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/l1i_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/l2_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/l2_cache.json

Purpose: Declares cache hierarchy PMU aliases, including access, refill, writeback, invalidation, read/write, and miss-level events where the CPU supports them.

Important data contract: JSON array with 19 entries for the `neoverse-n3` `l2 cache` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 19 entries carry local descriptions. Representative names: `L2D_CACHE`, `L2D_CACHE_REFILL`, `L2D_CACHE_WB`, `L2D_CACHE_ALLOCATE`, `L2I_CACHE`, `L2I_CACHE_REFILL`, `L2D_CACHE_RD`, `L2D_CACHE_WR`, plus 11 more.

Control flow: Perf maps each `ArchStdEvent` into the generated event table; cache MPKI and miss-ratio metrics rely on these names matching the Arm PMU definitions.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n3` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Cache/TLB aliases often differ by generation; copying entries across CPUs without checking support can expose unusable events.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `L2D_CACHE`, `L2D_CACHE_REFILL`, `L2D_CACHE_WB`, `L2D_CACHE_ALLOCATE`, `L2I_CACHE`, and 14 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/l2_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/l3_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/l3_cache.json

Purpose: Declares cache hierarchy PMU aliases, including access, refill, writeback, invalidation, read/write, and miss-level events where the CPU supports them.

Important data contract: JSON array with 6 entries for the `neoverse-n3` `l3 cache` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 6 entries carry local descriptions. Representative names: `L3D_CACHE_ALLOCATE`, `L3D_CACHE_REFILL`, `L3D_CACHE`, `L3D_CACHE_RD`, `L3D_CACHE_LMISS_RD`, `L3D_CACHE_MISS`.

Control flow: Perf maps each `ArchStdEvent` into the generated event table; cache MPKI and miss-ratio metrics rely on these names matching the Arm PMU definitions.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n3` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Cache/TLB aliases often differ by generation; copying entries across CPUs without checking support can expose unusable events.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `L3D_CACHE_ALLOCATE`, `L3D_CACHE_REFILL`, `L3D_CACHE`, `L3D_CACHE_RD`, `L3D_CACHE_LMISS_RD`, and 1 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/l3_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/ll_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/ll_cache.json

Purpose: Declares cache hierarchy PMU aliases, including access, refill, writeback, invalidation, read/write, and miss-level events where the CPU supports them.

Important data contract: JSON array with 5 entries for the `neoverse-n3` `ll cache` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 5 entries carry local descriptions. Representative names: `LL_CACHE`, `LL_CACHE_MISS`, `LL_CACHE_RD`, `LL_CACHE_MISS_RD`, `LL_CACHE_REFILL`.

Control flow: Perf maps each `ArchStdEvent` into the generated event table; cache MPKI and miss-ratio metrics rely on these names matching the Arm PMU definitions.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n3` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `LL_CACHE`, `LL_CACHE_MISS`, `LL_CACHE_RD`, `LL_CACHE_MISS_RD`, `LL_CACHE_REFILL`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/ll_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/memory.json

Purpose: Declares memory-access PMU aliases, including load/store, remote, alignment, checked-access, and memory-error events depending on CPU generation.

Important data contract: JSON array with 13 entries for the `neoverse-n3` `memory` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 13 entries carry local descriptions. Representative names: `MEM_ACCESS`, `REMOTE_ACCESS`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `LDST_ALIGN_LAT`, `LD_ALIGN_LAT`, `ST_ALIGN_LAT`, `MEM_ACCESS_CHECKED`, plus 5 more.

Control flow: Perf uses these aliases for memory behavior counters and for metric expressions that calculate data-side effectiveness or per-cycle access rates.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n3` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `MEM_ACCESS`, `REMOTE_ACCESS`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`, `LDST_ALIGN_LAT`, and 8 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/metrics.json

Purpose: Defines derived perf metrics rather than raw programmable events. The entries combine architected PMU event names into ratios, MPKI values, operation-mix percentages, and cycle/topdown-style accounting formulas for this CPU.

Important data contract: JSON array with 67 entries for the `neoverse-n3` `metrics` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 63 entries carry local descriptions and 65 entries carry `MetricExpr` formulas. Representative names: `backend_bound`, `backend_busy_bound`, `backend_cache_l1d_bound`, `backend_cache_l2d_bound`, `backend_core_bound`, `backend_core_rename_bound`, `backend_mem_bound`, `backend_mem_cache_bound`, plus 59 more.

Control flow: Perf's pmu-events generator preserves each `MetricName`, parses `MetricExpr`, and resolves referenced event tokens against sibling event JSON tables for the same CPU map. Runtime selection evaluates the expression over counters collected in the same stat session. Metric groups represented include Branch_Effectiveness, Cycle_Accounting, FP_Arithmetic_Intensity, FP_Precision_Mix, General, LL_Cache_Effectiveness, plus 20 more.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n3` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, BriefDescription, MetricExpr, MetricGroup, MetricName, ScaleUnit`. Metric expressions reference sibling raw events such as ASE_SPEC, BR_IMMED_RETIRED, BR_IND_RETIRED, BR_MIS_PRED_RETIRED, BR_RETIRED, BR_RETURN_RETIRED, CPU_CYCLES, CRYPTO_SPEC, DMB_SPEC, DP_SPEC, plus 55 more tokens.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Metric expressions can silently become misleading if referenced raw events are renamed, unavailable for a CPU revision, or have divide-by-zero behavior on short runs. Expressions using `#slots` or `strcmp_cpuid_str` are tightly coupled to perf's metric parser and CPU identification helpers.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `backend_bound`, `backend_busy_bound`, `backend_cache_l1d_bound`, `backend_cache_l2d_bound`, `backend_core_bound`, and 62 more. Run `perf stat -M` for representative metrics and check expression parsing, event grouping, and zero-denominator handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/retired.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/retired.json

Purpose: Declares instruction, retired-operation, speculative-operation, floating-point, and vector-operation PMU aliases for operation-mix analysis.

Important data contract: JSON array with 22 entries for the `neoverse-n3` `retired` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 22 entries carry local descriptions. Representative names: `SW_INCR`, `INST_RETIRED`, `CID_WRITE_RETIRED`, `PC_WRITE_RETIRED`, `BR_IMMED_RETIRED`, `BR_RETURN_RETIRED`, `TTBR_WRITE_RETIRED`, `BR_RETIRED`, plus 14 more.

Control flow: The generated perf table exposes these names for direct counting and for metrics that calculate IPC, branch rates, scalar/vector mix, and SVE/FP percentages.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n3` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `SW_INCR`, `INST_RETIRED`, `CID_WRITE_RETIRED`, `PC_WRITE_RETIRED`, `BR_IMMED_RETIRED`, and 17 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/retired.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/spe.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/spe.json

Purpose: Declares Statistical Profiling Extension sampling pipeline PMU aliases.

Important data contract: JSON array with 10 entries for the `neoverse-n3` `spe` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 10 entries carry local descriptions. Representative names: `SAMPLE_POP`, `SAMPLE_FEED`, `SAMPLE_FILTRATE`, `SAMPLE_COLLISION`, `SAMPLE_FEED_BR`, `SAMPLE_FEED_LD`, `SAMPLE_FEED_ST`, `SAMPLE_FEED_OP`, plus 2 more.

Control flow: Perf exposes these names for SPE feed/pop/filter/collision accounting; they complement, but do not configure, SPE sampling itself.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n3` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `SAMPLE_POP`, `SAMPLE_FEED`, `SAMPLE_FILTRATE`, `SAMPLE_COLLISION`, `SAMPLE_FEED_BR`, and 5 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/spe.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/spec_operation.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/spec_operation.json

Purpose: Declares instruction, retired-operation, speculative-operation, floating-point, and vector-operation PMU aliases for operation-mix analysis.

Important data contract: JSON array with 22 entries for the `neoverse-n3` `spec operation` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 22 entries carry local descriptions. Representative names: `BR_MIS_PRED`, `BR_PRED`, `INST_SPEC`, `OP_SPEC`, `STREX_FAIL_SPEC`, `STREX_SPEC`, `LD_SPEC`, `ST_SPEC`, plus 14 more.

Control flow: The generated perf table exposes these names for direct counting and for metrics that calculate IPC, branch rates, scalar/vector mix, and SVE/FP percentages.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n3` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `BR_MIS_PRED`, `BR_PRED`, `INST_SPEC`, `OP_SPEC`, `STREX_FAIL_SPEC`, and 17 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/spec_operation.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/stall.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/stall.json

Purpose: Declares frontend/backend stall and slot-accounting PMU aliases for pipeline pressure analysis.

Important data contract: JSON array with 21 entries for the `neoverse-n3` `stall` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 21 entries carry local descriptions. Representative names: `STALL_FRONTEND`, `STALL_BACKEND`, `STALL`, `STALL_SLOT_BACKEND`, `STALL_SLOT_FRONTEND`, `STALL_SLOT`, `STALL_BACKEND_MEM`, `STALL_FRONTEND_MEMBOUND`, plus 13 more.

Control flow: These events feed direct stall counters and topdown-style metrics; slot events are especially sensitive to the CPU's issue width and `#slots` substitution.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n3` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics may consume these stall names together with cycle counters and issue-slot constants.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `STALL_FRONTEND`, `STALL_BACKEND`, `STALL`, `STALL_SLOT_BACKEND`, `STALL_SLOT_FRONTEND`, and 16 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/stall.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/sve.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/sve.json

Purpose: Declares instruction, retired-operation, speculative-operation, floating-point, and vector-operation PMU aliases for operation-mix analysis.

Important data contract: JSON array with 12 entries for the `neoverse-n3` `sve` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 12 entries carry local descriptions. Representative names: `SVE_INST_SPEC`, `SVE_PRED_SPEC`, `SVE_PRED_EMPTY_SPEC`, `SVE_PRED_FULL_SPEC`, `SVE_PRED_PARTIAL_SPEC`, `SVE_PRED_NOT_FULL_SPEC`, `SVE_LDFF_SPEC`, `SVE_LDFF_FAULT_SPEC`, plus 4 more.

Control flow: The generated perf table exposes these names for direct counting and for metrics that calculate IPC, branch rates, scalar/vector mix, and SVE/FP percentages.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n3` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `SVE_INST_SPEC`, `SVE_PRED_SPEC`, `SVE_PRED_EMPTY_SPEC`, `SVE_PRED_FULL_SPEC`, `SVE_PRED_PARTIAL_SPEC`, and 7 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/sve.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/tlb.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/tlb.json

Purpose: Declares instruction/data TLB access, refill, read/write, and walk PMU aliases.

Important data contract: JSON array with 18 entries for the `neoverse-n3` `tlb` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 18 entries carry local descriptions. Representative names: `L1I_TLB_REFILL`, `L1D_TLB_REFILL`, `L1D_TLB`, `L1I_TLB`, `L2D_TLB_REFILL`, `L2D_TLB`, `DTLB_WALK`, `ITLB_WALK`, plus 10 more.

Control flow: Perf maps these aliases into generated event tables used for TLB miss ratios, MPKI metrics, and direct page-walk counters.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n3` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Cache/TLB aliases often differ by generation; copying entries across CPUs without checking support can expose unusable events.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `L1I_TLB_REFILL`, `L1D_TLB_REFILL`, `L1D_TLB`, `L1I_TLB`, `L2D_TLB_REFILL`, and 13 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/tlb.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/trace.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/trace.json

Purpose: Declares trace buffer, trace external output, and CTI trigger PMU aliases.

Important data contract: JSON array with 10 entries for the `neoverse-n3` `trace` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 10 entries carry local descriptions. Representative names: `TRB_WRAP`, `TRB_TRIG`, `TRCEXTOUT0`, `TRCEXTOUT1`, `TRCEXTOUT2`, `TRCEXTOUT3`, `CTI_TRIGOUT4`, `CTI_TRIGOUT5`, plus 2 more.

Control flow: Perf exposes the trace/CTI event names when the CPU PMU advertises them, allowing low-level trace integration counters to be selected by name.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-n3` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `TRB_WRAP`, `TRB_TRIG`, `TRCEXTOUT0`, `TRCEXTOUT1`, `TRCEXTOUT2`, and 5 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-n3/trace.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/bus.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/bus.json

Purpose: Declares bus, counter-cycle, and bus read/write access PMU aliases for perf.

Important data contract: JSON array with 4 entries for the `neoverse-v1` `bus` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 4 entries carry local descriptions. Representative names: `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`.

Control flow: Perf exposes these as CPU-specific event names used for bandwidth and platform-interconnect accounting; metrics may divide them by cycle events.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-v1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `BUS_ACCESS`, `BUS_CYCLES`, `BUS_ACCESS_RD`, `BUS_ACCESS_WR`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/bus.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/exception.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/exception.json

Purpose: Declares exception, trap, abort, IRQ/FIQ, and exception-return PMU aliases.

Important data contract: JSON array with 15 entries for the `neoverse-v1` `exception` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 15 entries carry local descriptions. Representative names: `EXC_TAKEN`, `EXC_RETURN`, `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, `EXC_DABORT`, `EXC_IRQ`, `EXC_FIQ`, plus 7 more.

Control flow: These aliases let perf count architectural exception activity; consumers use them directly rather than through executable control flow in this file.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-v1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `EXC_TAKEN`, `EXC_RETURN`, `EXC_UNDEF`, `EXC_SVC`, `EXC_PABORT`, and 10 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/exception.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/fp_operation.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/fp_operation.json

Purpose: Declares instruction, retired-operation, speculative-operation, floating-point, and vector-operation PMU aliases for operation-mix analysis.

Important data contract: JSON array with 2 entries for the `neoverse-v1` `fp operation` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 2 entries carry local descriptions. Representative names: `FP_SCALE_OPS_SPEC`, `FP_FIXED_OPS_SPEC`.

Control flow: The generated perf table exposes these names for direct counting and for metrics that calculate IPC, branch rates, scalar/vector mix, and SVE/FP percentages.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-v1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `FP_SCALE_OPS_SPEC`, `FP_FIXED_OPS_SPEC`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/fp_operation.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/general.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/general.json

Purpose: Declares general cycle-counting PMU aliases for this Neoverse CPU.

Important data contract: JSON array with 2 entries for the `neoverse-v1` `general` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 2 entries carry local descriptions. Representative names: `CPU_CYCLES`, `CNT_CYCLES`.

Control flow: These cycle aliases are foundational dependencies for IPC, stall, topdown, and percentage metrics in sibling metric tables.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-v1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `CPU_CYCLES`, `CNT_CYCLES`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/general.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/l1d_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/l1d_cache.json

Purpose: Declares cache hierarchy PMU aliases, including access, refill, writeback, invalidation, read/write, and miss-level events where the CPU supports them.

Important data contract: JSON array with 13 entries for the `neoverse-v1` `l1d cache` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 13 entries carry local descriptions. Representative names: `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_CACHE_WB`, `L1D_CACHE_LMISS_RD`, `L1D_CACHE_RD`, `L1D_CACHE_WR`, `L1D_CACHE_REFILL_RD`, `L1D_CACHE_REFILL_WR`, plus 5 more.

Control flow: Perf maps each `ArchStdEvent` into the generated event table; cache MPKI and miss-ratio metrics rely on these names matching the Arm PMU definitions.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-v1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Cache/TLB aliases often differ by generation; copying entries across CPUs without checking support can expose unusable events.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `L1D_CACHE_REFILL`, `L1D_CACHE`, `L1D_CACHE_WB`, `L1D_CACHE_LMISS_RD`, `L1D_CACHE_RD`, and 8 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/l1d_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/l1i_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/l1i_cache.json

Purpose: Declares cache hierarchy PMU aliases, including access, refill, writeback, invalidation, read/write, and miss-level events where the CPU supports them.

Important data contract: JSON array with 3 entries for the `neoverse-v1` `l1i cache` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 3 entries carry local descriptions. Representative names: `L1I_CACHE_REFILL`, `L1I_CACHE`, `L1I_CACHE_LMISS`.

Control flow: Perf maps each `ArchStdEvent` into the generated event table; cache MPKI and miss-ratio metrics rely on these names matching the Arm PMU definitions.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-v1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `L1I_CACHE_REFILL`, `L1I_CACHE`, `L1I_CACHE_LMISS`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/l1i_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/l2_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/l2_cache.json

Purpose: Declares cache hierarchy PMU aliases, including access, refill, writeback, invalidation, read/write, and miss-level events where the CPU supports them.

Important data contract: JSON array with 12 entries for the `neoverse-v1` `l2 cache` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 12 entries carry local descriptions. Representative names: `L2D_CACHE`, `L2D_CACHE_REFILL`, `L2D_CACHE_WB`, `L2D_CACHE_ALLOCATE`, `L2D_CACHE_RD`, `L2D_CACHE_WR`, `L2D_CACHE_REFILL_RD`, `L2D_CACHE_REFILL_WR`, plus 4 more.

Control flow: Perf maps each `ArchStdEvent` into the generated event table; cache MPKI and miss-ratio metrics rely on these names matching the Arm PMU definitions.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-v1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Cache/TLB aliases often differ by generation; copying entries across CPUs without checking support can expose unusable events.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `L2D_CACHE`, `L2D_CACHE_REFILL`, `L2D_CACHE_WB`, `L2D_CACHE_ALLOCATE`, `L2D_CACHE_RD`, and 7 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/l2_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/l3_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/l3_cache.json

Purpose: Declares cache hierarchy PMU aliases, including access, refill, writeback, invalidation, read/write, and miss-level events where the CPU supports them.

Important data contract: JSON array with 5 entries for the `neoverse-v1` `l3 cache` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 5 entries carry local descriptions. Representative names: `L3D_CACHE_ALLOCATE`, `L3D_CACHE_REFILL`, `L3D_CACHE`, `L3D_CACHE_RD`, `L3D_CACHE_LMISS_RD`.

Control flow: Perf maps each `ArchStdEvent` into the generated event table; cache MPKI and miss-ratio metrics rely on these names matching the Arm PMU definitions.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-v1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Cache/TLB aliases often differ by generation; copying entries across CPUs without checking support can expose unusable events.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `L3D_CACHE_ALLOCATE`, `L3D_CACHE_REFILL`, `L3D_CACHE`, `L3D_CACHE_RD`, `L3D_CACHE_LMISS_RD`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/l3_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/ll_cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/ll_cache.json

Purpose: Declares cache hierarchy PMU aliases, including access, refill, writeback, invalidation, read/write, and miss-level events where the CPU supports them.

Important data contract: JSON array with 2 entries for the `neoverse-v1` `ll cache` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 2 entries carry local descriptions. Representative names: `LL_CACHE_RD`, `LL_CACHE_MISS_RD`.

Control flow: Perf maps each `ArchStdEvent` into the generated event table; cache MPKI and miss-ratio metrics rely on these names matching the Arm PMU definitions.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-v1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics consume these names for miss ratios and MPKI calculations.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `LL_CACHE_RD`, `LL_CACHE_MISS_RD`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/ll_cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/memory.json

Purpose: Declares memory-access PMU aliases, including load/store, remote, alignment, checked-access, and memory-error events depending on CPU generation.

Important data contract: JSON array with 5 entries for the `neoverse-v1` `memory` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 5 entries carry local descriptions. Representative names: `MEM_ACCESS`, `MEMORY_ERROR`, `REMOTE_ACCESS`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`.

Control flow: Perf uses these aliases for memory behavior counters and for metric expressions that calculate data-side effectiveness or per-cycle access rates.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-v1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `MEM_ACCESS`, `MEMORY_ERROR`, `REMOTE_ACCESS`, `MEM_ACCESS_RD`, `MEM_ACCESS_WR`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/metrics.json

Purpose: Defines derived perf metrics rather than raw programmable events. The entries combine architected PMU event names into ratios, MPKI values, operation-mix percentages, and cycle/topdown-style accounting formulas for this CPU.

Important data contract: JSON array with 35 entries for the `neoverse-v1` `metrics` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 31 entries carry local descriptions and 33 entries carry `MetricExpr` formulas. Representative names: `backend_bound`, `backend_stalled_cycles`, `bad_speculation`, `branch_misprediction_ratio`, `branch_mpki`, `branch_percentage`, `crypto_percentage`, `dtlb_mpki`, plus 27 more.

Control flow: Perf's pmu-events generator preserves each `MetricName`, parses `MetricExpr`, and resolves referenced event tokens against sibling event JSON tables for the same CPU map. Runtime selection evaluates the expression over counters collected in the same stat session. Metric groups represented include Cycle_Accounting, General, LL_Cache_Effectiveness, MPKI;Branch_Effectiveness, MPKI;DTLB_Effectiveness, MPKI;ITLB_Effectiveness, plus 14 more.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-v1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, BriefDescription, MetricExpr, MetricGroup, MetricName, ScaleUnit`. Metric expressions reference sibling raw events such as ASE_SPEC, BR_IMMED_SPEC, BR_INDIRECT_SPEC, BR_MIS_PRED, BR_MIS_PRED_RETIRED, BR_RETIRED, CPU_CYCLES, CRYPTO_SPEC, DP_SPEC, DTLB_WALK, plus 26 more tokens.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions. Metric expressions can silently become misleading if referenced raw events are renamed, unavailable for a CPU revision, or have divide-by-zero behavior on short runs. Expressions using `#slots` or `strcmp_cpuid_str` are tightly coupled to perf's metric parser and CPU identification helpers.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `backend_bound`, `backend_stalled_cycles`, `bad_speculation`, `branch_misprediction_ratio`, `branch_mpki`, and 30 more. Run `perf stat -M` for representative metrics and check expression parsing, event grouping, and zero-denominator handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/retired.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/retired.json

Purpose: Declares instruction, retired-operation, speculative-operation, floating-point, and vector-operation PMU aliases for operation-mix analysis.

Important data contract: JSON array with 7 entries for the `neoverse-v1` `retired` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 7 entries carry local descriptions. Representative names: `SW_INCR`, `INST_RETIRED`, `CID_WRITE_RETIRED`, `TTBR_WRITE_RETIRED`, `BR_RETIRED`, `BR_MIS_PRED_RETIRED`, `OP_RETIRED`.

Control flow: The generated perf table exposes these names for direct counting and for metrics that calculate IPC, branch rates, scalar/vector mix, and SVE/FP percentages.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-v1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `SW_INCR`, `INST_RETIRED`, `CID_WRITE_RETIRED`, `TTBR_WRITE_RETIRED`, `BR_RETIRED`, and 2 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/retired.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/spe.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/spe.json

Purpose: Declares Statistical Profiling Extension sampling pipeline PMU aliases.

Important data contract: JSON array with 4 entries for the `neoverse-v1` `spe` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 4 entries carry local descriptions. Representative names: `SAMPLE_POP`, `SAMPLE_FEED`, `SAMPLE_FILTRATE`, `SAMPLE_COLLISION`.

Control flow: Perf exposes these names for SPE feed/pop/filter/collision accounting; they complement, but do not configure, SPE sampling itself.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-v1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `SAMPLE_POP`, `SAMPLE_FEED`, `SAMPLE_FILTRATE`, `SAMPLE_COLLISION`. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/spe.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/spec_operation.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/spec_operation.json

Purpose: Declares instruction, retired-operation, speculative-operation, floating-point, and vector-operation PMU aliases for operation-mix analysis.

Important data contract: JSON array with 27 entries for the `neoverse-v1` `spec operation` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 27 entries carry local descriptions. Representative names: `BR_MIS_PRED`, `BR_PRED`, `INST_SPEC`, `OP_SPEC`, `UNALIGNED_LD_SPEC`, `UNALIGNED_ST_SPEC`, `UNALIGNED_LDST_SPEC`, `LDREX_SPEC`, plus 19 more.

Control flow: The generated perf table exposes these names for direct counting and for metrics that calculate IPC, branch rates, scalar/vector mix, and SVE/FP percentages.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-v1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `BR_MIS_PRED`, `BR_PRED`, `INST_SPEC`, `OP_SPEC`, `UNALIGNED_LD_SPEC`, and 22 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/spec_operation.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/stall.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/stall.json

Purpose: Declares frontend/backend stall and slot-accounting PMU aliases for pipeline pressure analysis.

Important data contract: JSON array with 7 entries for the `neoverse-v1` `stall` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 7 entries carry local descriptions. Representative names: `STALL_FRONTEND`, `STALL_BACKEND`, `STALL`, `STALL_SLOT_BACKEND`, `STALL_SLOT_FRONTEND`, `STALL_SLOT`, `STALL_BACKEND_MEM`.

Control flow: These events feed direct stall counters and topdown-style metrics; slot events are especially sensitive to the CPU's issue width and `#slots` substitution.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-v1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`. Sibling metrics may consume these stall names together with cycle counters and issue-slot constants.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `STALL_FRONTEND`, `STALL_BACKEND`, `STALL`, `STALL_SLOT_BACKEND`, `STALL_SLOT_FRONTEND`, and 2 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/stall.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/sve.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/sve.json

Purpose: Declares instruction, retired-operation, speculative-operation, floating-point, and vector-operation PMU aliases for operation-mix analysis.

Important data contract: JSON array with 7 entries for the `neoverse-v1` `sve` category. Entries are selected by `ArchStdEvent`, `EventName`, or `MetricName`; 7 entries carry local descriptions. Representative names: `SVE_INST_SPEC`, `SVE_PRED_SPEC`, `SVE_PRED_EMPTY_SPEC`, `SVE_PRED_FULL_SPEC`, `SVE_PRED_PARTIAL_SPEC`, `SVE_LDFF_SPEC`, `SVE_LDFF_FAULT_SPEC`.

Control flow: The generated perf table exposes these names for direct counting and for metrics that calculate IPC, branch rates, scalar/vector mix, and SVE/FP percentages.

State and persistence: This file has no runtime mutable state. Its persistent effect is build-time data: perf's pmu-events tooling compiles the JSON records into generated event/metric tables installed with perf, and runtime behavior depends on CPU-map selection rather than code in this file.

Dependencies and integration: Depends on the Linux perf pmu-events JSON schema and the Arm64 mapfile entry that selects the `neoverse-v1` directory for matching MIDR/CPUID values. Schema fields present here are `ArchStdEvent, PublicDescription`.

Risks: The main risk is semantic drift between these aliases and the CPU technical reference manual or Arm architectural PMU event definitions.

Test signals: Run the perf pmu-events JSON validator/generator over this tree and confirm no schema errors. On matching hardware or with generated-table inspection, confirm `perf list` exposes `SVE_INST_SPEC`, `SVE_PRED_SPEC`, `SVE_PRED_EMPTY_SPEC`, `SVE_PRED_FULL_SPEC`, `SVE_PRED_PARTIAL_SPEC`, and 2 more. Run `perf stat -e` for representative aliases and verify counts are accepted by the kernel PMU driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/arm/neoverse-v1/sve.json -->

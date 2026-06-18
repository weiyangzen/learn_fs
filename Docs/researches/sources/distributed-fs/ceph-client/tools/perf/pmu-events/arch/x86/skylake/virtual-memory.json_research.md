
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/virtual-memory.json

## Purpose

This file defines 28 Skylake client virtual-memory/TLB events. It covers data-TLB load misses, data-TLB store misses, instruction-TLB misses, EPT walk pending, ITLB flushes, and TLB flush events. The events distinguish STLB hits, page-walk starts/completions, walk-active cycles, walk-pending counts, and page sizes such as 4K, 2M/4M, and 1G.

The event names include `DTLB_LOAD_MISSES.*`, `DTLB_STORE_MISSES.*`, `ITLB_MISSES.*`, `EPT.WALK_PENDING`, `ITLB.ITLB_FLUSH`, and `TLB_FLUSH.*`. They provide the raw event layer used for memory-translation analysis and for topdown metrics involving TLB pressure.

## Important Schema Fields and APIs

Each row exposes a core PMU event alias:

- `EventName`: symbolic perf event.
- `EventCode` and `UMask`: raw event selector and subevent mask.
- `Counter`: allowed programmable counters.
- `CounterMask`: present on cycle-thresholded rows such as active/pending walk conditions.
- `SampleAfterValue`: default sampling period for `perf record` style use.
- `BriefDescription` and `PublicDescription`: short and detailed descriptions surfaced to users.

Unlike uncore files, there is no `Unit` field here; these are core PMU events. The `CounterMask` field maps to `cmask=...` in perf event encoding. `SampleAfterValue` affects default sampling behavior but not `perf stat` counting semantics.

## Control Flow and Data Flow

At build time, `jevents.py` converts each descriptor into generated C metadata. At runtime, perf maps symbolic event names to event selectors when the CPU matches the Skylake model. Users can count the events directly or use them through `skl-metrics.json` formulas such as TLB miss ratios, STLB MPKI metrics, and topdown memory-TLB bottleneck nodes.

The data flow is raw PMU increments from TLB hardware -> perf event counts/samples -> direct output or metric-expression inputs. There is no internal control flow within the JSON file.

## State and Persistence

The JSON is source-time static metadata. Generated aliases persist in the perf binary. Runtime state is limited to PMU counters, perf buffers, and sampled records if a user runs a sampling command; no state is persisted by this descriptor file.

## Dependencies and Integration Points

The file integrates with Skylake core PMU support in the kernel, `jevents.py`, the x86 mapfile, generated `pmu-events.c`, and perf metric evaluation. It is tightly coupled to TLB metrics in `skl-metrics.json`, especially metrics involving code STLB misses, load/store STLB misses, page-walk utilization, and memory-data-TLB bottlenecks.

## Risks

TLB event semantics are sensitive to page size, virtualization, EPT usage, and kernel/hypervisor behavior. Some rows count walks completed by page size while others count miss causes, active cycles, or pending cycles; mixing them incorrectly can produce invalid ratios. `CounterMask` and `SampleAfterValue` mistakes may create scheduling or sampling artifacts. Hardware errata or kernel event alias changes could make formulas in the metric file stale.

## Test Signals

Validation should include JSON syntax, generated alias output, `perf list` visibility for `DTLB_*`, `ITLB_*`, `EPT.*`, and `TLB_FLUSH.*`, and runtime tests using workloads with known TLB stress. Metric-level tests should run representative `tma_*tlb*` and `tma_info_memory_tlb_*` metrics to ensure referenced aliases resolve.

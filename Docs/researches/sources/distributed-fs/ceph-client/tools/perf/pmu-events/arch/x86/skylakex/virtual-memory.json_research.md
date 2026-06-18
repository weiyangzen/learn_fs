# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/virtual-memory.json

## Purpose

`virtual-memory.json` is the Skylake-X core PMU catalog for TLB, page-walk, EPT-walk, and TLB flush events in perf. It contains 28 events covering data-load DTLB misses, store DTLB misses, instruction TLB misses, second-level TLB hits, page-walk completion by page size, page-walk active and pending cycles, EPT walk pending cycles, ITLB flushes, and DTLB/STLB flush attempts.

## Important APIs, Types, and Data Fields

The file is a JSON array using the core event schema: `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, and optional `Counter`, `CounterMask`, and `SampleAfterValue`. Unlike uncore files, these records do not set a `Unit`; they are core PMU events. Major families are `DTLB_LOAD_MISSES.*` with `EventCode: "0x08"`, `DTLB_STORE_MISSES.*` with `EventCode: "0x49"`, `ITLB_MISSES.*` with `EventCode: "0x85"`, `EPT.WALK_PENDING` with `EventCode: "0x4f"`, `ITLB.ITLB_FLUSH` with `EventCode: "0xAE"`, and `TLB_FLUSH.*` with `EventCode: "0xBD"`.

The page-walk completion masks distinguish all page sizes from 4K, 2M/4M, and 1G completions. `STLB_HIT` rows count L1 TLB misses that were satisfied by the second-level TLB. `WALK_ACTIVE` and `WALK_PENDING` rows use the same event and mask within each family but describe related cycle/accounting views of page miss handler activity.

## Control Flow and Data Flow

There is no code-level control flow. Perf parses the records into generated event tables, exposes aliases, and programs core PMU counters when users request them. Data flow starts at per-core hardware counters, then perf aggregates per CPU, per thread, or system-wide according to the chosen command. The events form a diagnostic pipeline: first identify DTLB/ITLB miss-caused page walks, then separate STLB hits from full walks, then split completed walks by page size, and finally correlate active/pending cycles with workload stalls.

## State and Persistence Behavior

Persistent state is limited to the static event metadata. Runtime page-table behavior, TLB contents, EPT walk state, and flush activity live in hardware and kernel execution, not in this file. Counts are core-scoped and depend on perf's sampling or counting mode. The descriptions explicitly note that EPT page-walk duration is excluded from the Skylake `WALK_ACTIVE`/`WALK_PENDING` DTLB and ITLB rows, while `EPT.WALK_PENDING` covers EPT walks separately.

## Dependencies and Integration Points

This file depends on Skylake-X core PMU support and perf's pmu-events schema. It integrates with cache, frontend, backend, and uncore memory files by explaining whether observed stalls or memory traffic are related to address translation. It is relevant to huge-page tuning, virtualization overhead analysis, page-table locality studies, TLB shootdown diagnostics, and instruction-fetch bottleneck analysis.

## Risks and Edge Cases

Rows with the same event code and mask but different names can be misinterpreted if tooling treats aliases as independent signals rather than alternate semantic views. Page-walk completion counts by page size require workloads that actually use those page sizes; otherwise the counters may stay at zero. EPT walk accounting is separated from ordinary page-walk duration on Skylake-X, so virtualization analysis must include `EPT.WALK_PENDING`. TLB flush events count attempts or flushes, not necessarily resulting misses. Core aggregation can hide per-core skew in NUMA, virtualization, or mixed workload cases.

## Test Signals

Static validation should parse the JSON and generate perf event tables. Runtime tests should confirm `perf list` exposes `DTLB_LOAD_MISSES.*`, `DTLB_STORE_MISSES.*`, `ITLB_MISSES.*`, `EPT.WALK_PENDING`, and `TLB_FLUSH.*` aliases on Skylake-X. Pointer-chasing or large working-set tests should increase DTLB walk events; code-footprint stress should affect ITLB rows; huge-page workloads should move 2M/4M or 1G completion rows; virtualized workloads should exercise EPT walk pending; TLB shootdown or mapping churn tests should affect flush rows.

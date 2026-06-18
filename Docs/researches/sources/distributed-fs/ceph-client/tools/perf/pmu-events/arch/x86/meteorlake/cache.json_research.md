# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/cache.json

## Purpose

`cache.json` is the Meteor Lake cache and memory-access event catalog for perf. It contains 162 events covering L1D replacements and pending misses, L2 line fills/evictions/requests, longest-latency-cache references and misses, instruction-fetch and demand-load memory-bound stalls, retired memory instructions, load data-source breakdowns, memory scheduler blocks, offcore requests and outstanding cycles, OCR snoop/data-source filters, software prefetches, bus locks, and an atom frontend icache top-down event.

## Important APIs, Types, And Data Shape

The array uses standard perf PMU event fields: `EventName`, `Unit`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, `MSRIndex`, `MSRValue`, `Data_LA`, and `EdgeDetect`. It has both `cpu_core` and `cpu_atom` events, often with the same alias name but different encodings. Core PEBS/load-address related retired memory events use `Data_LA: "1"`. OCR and some load-latency events program MSR filters such as `0x1a6,0x1a7` or `0x3F6`.

## Control Flow

`jevents.py` reads the file as topic `cache`, builds generated aliases, and emits unit-specific event records. At runtime, perf resolves names such as `l2_rqsts.references`, `mem_load_retired.l3_miss`, `ocr.demand_data_rd.l3_hit.snoop_hitm`, or `offcore_requests_outstanding.demand_data_rd` against the PMU unit. Higher-level memory metrics use these aliases to attribute stalls and bandwidth pressure.

## State And Persistence

The source is static metadata. Generated event tables persist encodings, descriptions, data-address capability annotations, and MSR filter values. Runtime state consists of PMU counter programming, PEBS configuration where required, and any offcore response MSR settings applied by perf during collection.

## Dependencies And Integration Points

Dependencies include Meteor Lake hybrid PMU event encodings, Intel offcore response filters, PEBS load-address support, and perf's generated PMU alias system. Integration points include `perf list cache`, `perf mem`, `perf stat` memory metrics, `util/pmu.c` alias matching, generated `pmu-events.c`, and tests that compare expected generated event fields. It also feeds metric groups such as cache hits/misses, memory bandwidth, memory latency, data sharing, snoop, and load/store bound groups.

## Risks

The file is dense and has several risk classes. Duplicate aliases must remain separated by `Unit`. OCR filters rely on exact `MSRValue` bitmasks; mistakes produce plausible but wrong data-source counts. PEBS/Data_LA events require hardware and kernel support, and should not be treated as generic counting events on unsupported systems. Some aliases are compatibility aliases, for example `L2_REQUEST.*` and `L2_RQSTS.*`, so removing one spelling can break users. Events that count cycles, requests, retired instructions, and latency-threshold samples should not be mixed without normalization.

## Test Signals

Validation should confirm array length 162, expected `cpu_atom` and `cpu_core` coverage, JSON generation success, and no accidental loss of MSR-backed OCR entries. Runtime checks include `perf list cache`, collecting L1/L2 aliases under cache-stressing workloads, PEBS availability checks for `mem_inst_retired.*`, and offcore-request smoke tests. Regression tests should compare generated event strings for representative aliases with `MSRIndex`, `MSRValue`, `CounterMask`, and `Data_LA`.

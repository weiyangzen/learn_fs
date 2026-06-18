# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/other.json

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/other.json` defines Cascade Lake X core PMU events that do not fit the cache, frontend, memory, pipeline, virtual-memory, or uncore topic files. The file is dominated by offcore response (`OCR.*`) events for demand reads, prefetch reads, RFOs, PMM local hits, and supplier/snoop response classes, plus a small set of core power-license and hardware-interrupt events. The source was read as a complete 1,257-line JSON array with 126 event objects.

## Important APIs, Types, and Data Fields

This file uses perf's standard PMU event JSON schema. Every event has `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`. Five non-OCR rows also carry `PublicDescription`. The 121 `OCR.*` rows additionally use `MSRIndex` and `MSRValue`, which cause `jevents.py` to generate offcore-response MSR programming fields for the event alias.

Event families are:

- `CORE_POWER.LVL0_TURBO_LICENSE`, `CORE_POWER.LVL1_TURBO_LICENSE`, `CORE_POWER.LVL2_TURBO_LICENSE`, and `CORE_POWER.THROTTLE`, all using event code `0x28` with distinct umasks for AVX/turbo license and throttle-cycle accounting.
- `HW_INTERRUPTS.RECEIVED`, using event code `0xCB` and umask `0x1`.
- `OCR.*`, using event codes `0xB7, 0xBB`, umask `0x1`, counters `0,1,2,3`, MSR indices `0x1a6,0x1a7`, and different `MSRValue` encodings.

The OCR rows cover request classes including `ALL_DATA_RD`, `ALL_PF_DATA_RD`, `ALL_PF_RFO`, `ALL_READS`, `ALL_RFO`, `OTHER`, `PF_L1D_AND_SW`, `PF_L2_DATA_RD`, `PF_L2_RFO`, `PF_L3_DATA_RD`, and `PF_L3_RFO`. For those classes, response filters include `ANY_RESPONSE`, `PMM_HIT_LOCAL_PMM` variants (`ANY_SNOOP`, `SNOOP_NONE`, `SNOOP_NOT_NEEDED`), and `SUPPLIER_NONE` variants (`ANY_SNOOP`, `HITM_OTHER_CORE`, `HIT_OTHER_CORE_FWD`, `HIT_OTHER_CORE_NO_FWD`, `NO_SNOOP_NEEDED`, `SNOOP_MISS`, `SNOOP_NONE`).

## Control Flow and Data Flow

There is no executable control flow in the file. Build-time flow is handled by `tools/perf/pmu-events/jevents.py`: each object is parsed into generated PMU event metadata, `EventCode` contributes the base `event=` selector, `UMask` contributes `umask=`, `SampleAfterValue` contributes the default `period=`, and `MSRIndex`/`MSRValue` are converted into the appropriate offcore-response MSR field. The code path takes the first event code before the comma when building the alias, while the MSR index/value data supplies the extra offcore filter.

At runtime, a user can select symbolic names such as `OCR.ALL_READS.ANY_RESPONSE` or `CORE_POWER.LVL2_TURBO_LICENSE` with `perf stat` or `perf record`. Perf resolves the alias from the generated Cascade Lake X table, asks the kernel x86 PMU driver to program the programmable counter and any required MSR filter, and reports counts or samples. The OCR rows are designed for memory-origin and snoop-response analysis; the power rows expose cycles spent in each turbo license level or throttled while a power-level request is pending.

## State and Persistence Behavior

The JSON is static metadata. It does not store live offcore transactions, interrupt counts, power state, or throttle state. `SampleAfterValue` values persist as default sampling periods in generated metadata, but actual counter values are owned by hardware and perf event file descriptors during a profiling run. Offcore response configuration is transiently programmed into model-specific registers by the kernel for active events and is not persisted by this file.

## Dependencies and Integration Points

The file depends on Cascade Lake X core PMU semantics, including the availability of programmable counters `0,1,2,3`, the `CORE_POWER`, `HW_INTERRUPTS`, and offcore response events, and MSR filter encodings for `0x1a6`/`0x1a7`. It integrates with `jevents.py` for JSON conversion, `pmu-events.h`/generated `pmu-events.c` for event lookup, the x86 mapfile entry `GenuineIntel-6-55-[56789ABCDEF],v1.25,cascadelakex,core`, and perf runtime commands that consume event aliases.

The file also integrates analytically with Cascade Lake X memory and PMM metrics: the `PMM_HIT_LOCAL_PMM` rows distinguish persistent-memory local hits, while `SUPPLIER_NONE` and snoop variants help explain offcore read responses, cache-to-cache transfers, and requests that did not require snooping.

## Risks and Edge Cases

The biggest correctness risk is the pairing of event selector, offcore MSR index, and `MSRValue`. A wrong `MSRValue` can produce a valid event that counts the wrong response class. The comma-separated `EventCode` values are parsed by the generator with the first code as the alias event selector, so any expectation that both selectors are programmed from the string itself must be verified against the x86 PMU driver path. OCR events compete for limited programmable counters and offcore response MSR resources, so some combinations may fail to schedule together.

Several descriptions are mechanically generated and repetitive, sometimes duplicating the event name in prose; this can make documentation less clear without changing encoding. Power-license events count cycles in license categories, not necessarily direct wall-clock residency or frequency, and turbo throttling interpretation depends on package power/thermal policy. Hardware interrupt counts can be affected by interrupt routing, affinity, virtualization, and privilege restrictions.

## Test Signals

Static test signals include JSON parse success, every row having `EventName`/`EventCode`/`UMask`/`Counter`/`SampleAfterValue`, all OCR rows having both `MSRIndex` and `MSRValue`, and generated `pmu-events.c` build success. Runtime smoke tests should verify `perf list` shows representative names from each family and `perf stat -e CORE_POWER.LVL0_TURBO_LICENSE,HW_INTERRUPTS.RECEIVED sleep 0.1` is accepted on matching hardware.

For OCR rows, useful tests are `perf stat` runs for a small subset such as `OCR.ALL_READS.ANY_RESPONSE`, `OCR.ALL_RFO.ANY_RESPONSE`, and one PMM-local row on a Cascade Lake X system. Workload signals should show all-read counters moving under memory-heavy loads, RFO counters moving under write-heavy workloads, and PMM-local counters only becoming meaningful on systems with configured persistent memory. Scheduling tests should intentionally combine multiple OCR events to catch offcore MSR constraint failures.

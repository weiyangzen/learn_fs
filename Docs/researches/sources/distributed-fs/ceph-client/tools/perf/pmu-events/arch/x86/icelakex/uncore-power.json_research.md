# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-power.json

## Purpose

`uncore-power.json` defines 26 Ice Lake Xeon PCU uncore events for package power, residency, frequency clipping, voltage regulator, thermal, demotion, and transition behavior. It gives perf symbolic access to power-control-unit conditions such as AVX frequency clipping, thermal max-frequency limits, package C-state residency, PROCHOT assertion, and VR hot cycles.

## Schema And API Surface

Every entry is an event object with `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, and `Unit: "PCU"`. Several entries also carry `Counter` and `Experimental`. Representative names are `UNC_P_CLOCKTICKS`, `UNC_P_FREQ_CLIP_AVX256`, `UNC_P_FREQ_CLIP_AVX512`, `UNC_P_FREQ_MAX_LIMIT_THERMAL_CYCLES`, `UNC_P_PKG_RESIDENCY_C6_CYCLES`, `UNC_P_POWER_STATE_OCCUPANCY.CORES_C0`, `UNC_P_PROCHOT_INTERNAL_CYCLES`, and `UNC_P_VR_HOT_CYCLES`.

## Control Flow And Integration

The file is parsed by `jevents.py` with the rest of the Ice Lake X PMU files. Generated aliases are exposed through the uncore PCU PMU. The runtime flow is: CPU model match, alias table lookup, PCU event encoding, then perf opens the corresponding uncore PMU event. These aliases are especially relevant to `perf stat` investigations that correlate core throughput changes with package-level power or frequency constraints.

## State And Persistence

The JSON is static metadata. The measured state is package-level PCU hardware counter state. Many events count cycles spent in a condition, so interpretation usually requires normalization against `UNC_P_CLOCKTICKS`, TSC, or elapsed time. The `Unit` field is the key persistence boundary because it links the event definitions to the PCU PMU instead of core PMUs.

## Dependencies

The file depends on Ice Lake Xeon PCU event encodings and perf's uncore PMU alias support. It integrates with topdown or system summary metrics that may use power, frequency, or residency signals, and with perf display code that prints metric groups and event descriptions.

## Risks

Power events are easy to misuse if interpreted as rates without a denominator. An incorrect unit or umask can be hard to catch at build time because JSON remains valid. Experimental markings should be preserved because hardware support and counter behavior may vary by stepping or platform firmware. Residency and throttling aliases may require package scope; using them as per-core evidence can produce misleading analysis.

## Test Signals

Validation should include JSON parsing, successful `jevents.py` generation, `perf list` visibility under PCU uncore PMUs, and `perf stat` checks while running AVX, idle, and thermally constrained workloads. Expected signals include nonzero C-state residency while idle and frequency clip counters changing under appropriate stress conditions.

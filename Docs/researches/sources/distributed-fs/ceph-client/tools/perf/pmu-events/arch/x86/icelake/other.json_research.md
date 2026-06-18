# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/other.json

## Purpose

This small file defines five Ice Lake miscellaneous core PMU events that do not fit the frontend, memory, or pipeline catalogs. It covers turbo-license residency levels and two offcore response classes for "other" and streaming-write request types with any response.

## Important APIs, Types, And Data

The entries use the standard event JSON fields `EventName`, `EventCode`, `UMask`, `Counter`, `MSRIndex`, `MSRValue`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. `CORE_POWER.LVL0_TURBO_LICENSE`, `CORE_POWER.LVL1_TURBO_LICENSE`, and `CORE_POWER.LVL2_TURBO_LICENSE` share selector `0x28` with umasks `0x7`, `0x18`, and `0x20`. `OCR.OTHER.ANY_RESPONSE` and `OCR.STREAMING_WR.ANY_RESPONSE` use offcore selectors `0xB7, 0xBB`, umask `0x1`, MSRs `0x1a6,0x1a7`, and response masks `0x18000` and `0x10800`.

## Control Flow

Build-time handling is the normal `jevents.py` event path: parse the array, normalize each object, convert selector/mask/MSR fields into generated perf aliases, and emit them into the Ice Lake table. Runtime perf resolves the generated aliases and programs either normal core power-license events or offcore-response-filtered events.

## State And Persistence Behavior

The file persists static alias definitions and descriptions. Turbo-license residency and offcore response counts are hardware state sampled during a perf run. No runtime values are persisted in the source tree. Default sample periods become generated alias metadata.

## Dependencies And Integration Points

The turbo-license entries integrate with power and frequency analysis workflows and may complement `icl-metrics.json` power/system metrics, though cstate residency metrics mostly use MSR/cstate aliases. The OCR entries integrate with offcore and memory bottleneck analysis. All entries depend on Ice Lake model selection, `jevents.py`, generated event tables, and kernel support for the relevant core PMU/offcore MSR programming.

## Risks And Edge Cases

The file is small but semantically mixed. Power-license events count cycles under turbo-license constraints, which users may confuse with frequency or package residency metrics. The OCR entries share offcore programming behavior with `memory.json`, so wrong MSR masks can silently change request categorization. Because this file is often treated as a catch-all, future edits risk duplicating events already present in more specific catalogs.

## Test Signals

Validate with `jq empty other.json`, run x86 PMU event generation, and inspect `perf list` for `core_power.lvl*_turbo_license` and `ocr.*.any_response`. Runtime tests should compare turbo-license counts under frequency-sensitive workloads and ensure offcore entries program response MSRs without conflicting with `memory.json` OCR aliases.

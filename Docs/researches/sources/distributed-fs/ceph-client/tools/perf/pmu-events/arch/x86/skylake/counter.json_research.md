# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/counter.json

## Purpose

`counter.json` describes the basic Skylake PMU counter inventory rather than individual events. It contains four records that declare available counter resources for the `core`, `CBOX`, `ARB`, and `cbox_0` PMU units. The core PMU row advertises 3 fixed counters and 4 generic programmable counters; the uncore-style `CBOX` and `ARB` rows advertise 2 generic counters each; `cbox_0` advertises 1 fixed counter and 0 generic counters.

This file helps perf and related tooling understand counter capacity and unit naming for the Skylake PMU map. It is a small but central companion to the event files because event constraints such as `Counter: 0,1,2,3` only make sense when the architecture's generic/fixed counter counts are known.

## Important schema/API surface

The API is a compact JSON array with fields different from normal event descriptors:

- `Unit`: PMU unit name, specifically `core`, `CBOX`, `ARB`, and `cbox_0`.
- `CountersNumFixed`: fixed-function counter count, with values `3`, `0`, `0`, and numeric `1`.
- `CountersNumGeneric`: programmable generic counter count, with values `4`, `2`, `2`, and `0`.

No `EventCode`, `UMask`, or `EventName` fields are present because this file does not program a specific event.

## Control flow and integration

Perf's PMU event metadata loader treats this file as architecture capacity metadata. The data is integrated with the same Skylake map as event categories such as `cache.json`, `frontend.json`, and `pipeline.json`. Scheduling and display paths can use it to explain that Skylake exposes four generic core counters and three fixed counters, while specific event descriptors name the counters they can use.

The uncore-style `CBOX`, `ARB`, and `cbox_0` rows are integration signals that consumers must not assume every row describes the core programmable PMU. Tools should key counter capacity by `Unit`.

## State and persistence behavior

The file is persistent static metadata. It has no runtime mutation and no per-host state. At runtime the real counter availability can still be affected by kernel PMU support, privilege settings, NMI watchdog usage, pinned events, virtualization, and already scheduled perf sessions.

## Dependencies

The file depends on perf's PMU event JSON parser recognizing counter inventory fields and on the Skylake PMU implementation having 3 fixed counters and 4 generic counters. It also depends on downstream tools handling `Unit` rows without event encodings.

## Risks and maintenance notes

The main risk is confusing this schema with event-list schema. Generic validators that require `EventName` or `EventCode` would incorrectly reject this file. Conversely, event loaders that iterate every JSON file as an event array without checking row shape could try to expose bogus aliases.

Counter counts are simple values but high impact. If `CountersNumGeneric` or `CountersNumFixed` is wrong, scheduling diagnostics and event multiplexing expectations become misleading. The mixed string and numeric representation of counts (`"3"` versus `1`) is also worth preserving or normalizing deliberately in consumers.

## Test signals

Validation should check that the file is valid JSON, has four rows, includes `CountersNumFixed: "3"` and `CountersNumGeneric: "4"` for `core`, includes the `CBOX`, `ARB`, and `cbox_0` rows, and does not require event-specific fields. Integration tests should run perf's PMU event table generation and confirm no bogus event aliases are emitted from this file.

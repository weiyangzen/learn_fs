# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/counter.json

## Purpose

`icelake/counter.json` defines PMU counter inventory metadata for the Ice Lake model. Unlike event files, it contains no `EventName` records. Instead it declares the number of fixed and generic counters available for three PMU units: `core`, `ARB`, and `CLOCK`. This metadata helps perf describe or constrain the hardware counter resources for the model.

## Important APIs, types, and schema

The schema is a short JSON array of objects with `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. The records are `core` with 4 fixed and 8 generic counters, `ARB` with 0 fixed and 2 generic counters, and `CLOCK` with 1 fixed and 0 generic counters. Most numeric values are strings, while `CLOCK.CountersNumFixed` is the JSON number `1`; consumers therefore need to tolerate both string and numeric representations, as neighboring x86 model counter files do.

## Control flow and integration

The file has no executable control flow and is not parsed as ordinary event aliases because it lacks `EventName`. It lives in the same model directory selected by `arch/x86/mapfile.csv` for Ice Lake, so any counter metadata consumer in the perf PMU event tooling can associate these limits with the generated Ice Lake PMU tables. It complements event files such as `cache.json` and `floating-point.json` by documenting how many counters can schedule the aliases.

## State and persistence behavior

The persistent behavior is the Ice Lake counter inventory. Changing these counts changes perf's understanding of available model resources and can affect validation, display, or scheduling assumptions. There is no runtime mutable state or generated alias state inside this file.

## Dependencies

Dependencies include Intel Ice Lake PMU counter topology and any perf tooling that reads `counter.json` files alongside model event catalogs. It also depends on the x86 model directory contract and the repository-wide convention for `CountersNumFixed` and `CountersNumGeneric` fields.

## Risks

The largest risk is resource misdescription. Overstating generic counters could make validation or documentation imply that event groups can be scheduled when hardware cannot support them; understating counts hides legitimate concurrency. Mixed numeric/string value types are a compatibility risk for strict parsers. The `ARB` and `CLOCK` units should not be confused with standard core event aliases, since they are resource declarations rather than programmable event records.

## Test signals

Validation should include JSON syntax, schema checks that accept both numeric and string count values, and comparison against adjacent Ice Lake-family counter files such as `rocketlake/counter.json` or `icelakex/counter.json` where appropriate. Runtime-facing confidence comes from perf scheduling behavior and `perf list` or debug output matching the expected 8 generic core counters and 4 fixed counters on Ice Lake client hardware.

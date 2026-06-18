# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivybridge/counter.json

## Purpose

`counter.json` is a compact Ivy Bridge PMU topology descriptor rather than a list of individual events. It declares the number of generic and fixed counters for specific units so the perf PMU event generator and users have model-level counter-capacity metadata.

## Schema And API Surface

The file contains 3 objects with `Unit`, `CountersNumGeneric`, and `CountersNumFixed`. Units include `core`, `CBOX`, and `ARB`. For `core`, the file records both generic and fixed counter counts; for uncore boxes it records generic counter counts. These keys are schema-level inputs rather than runtime event aliases, so there are no `EventName` or `MetricName` entries.

## Control Flow And Integration

During PMU event generation, the JSON is parsed with the rest of the Ivy Bridge directory. The data informs generated PMU metadata rather than generating user-facing event aliases. It integrates with perf's model table and can affect how perf understands available counters and uncore boxes for the Ivy Bridge event set.

## State And Persistence

The persisted state is static counter capacity by PMU unit. It does not mutate and does not represent measured counter values. Runtime availability still depends on kernel PMU registration and actual hardware.

## Dependencies

The values depend on Ivy Bridge hardware topology and perf's support for interpreting counter metadata JSON. It sits beside event files that define what the counters can count.

## Risks

Wrong counts can cause confusing scheduling assumptions, especially for multiplexing or grouping. Because this file has a different shape from the event arrays, generic tooling that assumes every JSON entry has `EventName` can misclassify it. Validators should explicitly allow this metadata schema.

## Test Signals

Structural tests should confirm valid JSON and expected keys. Build tests should confirm `jevents.py` accepts the file. Runtime validation is indirect: perf should build and list Ivy Bridge events without counter-topology warnings, and grouped perf stat runs should behave consistently with hardware counter availability.

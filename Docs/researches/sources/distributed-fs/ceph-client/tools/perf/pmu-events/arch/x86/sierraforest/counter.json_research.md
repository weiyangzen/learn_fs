# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/counter.json

## Purpose

This 15-entry file declares the number of fixed and generic counters available for Sierra Forest core and uncore PMU units. It gives perf the resource model needed to schedule events on `core`, `B2CMI`, `CHA`, `IMC`, `CXLCM`, `CXLDP`, `B2HOT`, `IIO`, `IRP`, `UPI`, `B2UPI`, `B2CXL`, `PCU`, `CHACMS`, and `MDF` units.

## Important APIs, Types, and Data

Each object contains `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. The `core` unit declares 3 fixed counters and 8 generic counters. Every listed uncore unit declares 0 fixed counters. Most uncore units have 4 generic counters, while `CXLCM` declares 8. Values are inconsistently typed as strings and JSON numbers, so consumers must tolerate both.

## Control Flow

Perf's pmu-events tooling reads this table as PMU capability metadata. Event scheduling uses the counter counts to decide whether a requested event group can fit without multiplexing and how many generic slots are available per PMU unit. This file does not name events; it constrains the events declared in adjacent Sierra Forest files and uncore catalogs.

## State and Persistence Behavior

The persistent state is the counter-capacity contract for the model. Runtime state is perf's scheduling decision and PMU counter allocation during a measurement session. Because the file describes hardware resources, changing a count changes whether event groups are accepted, rejected, or multiplexed.

## Dependencies and Integration Points

This file integrates with perf event scheduling, generated PMU tables, uncore PMU discovery, and metric groups that may request several events at once. It is especially relevant for large topdown or uncore metric sets, where exceeding the declared counter count can force multiplexing. It also documents the presence of CXL- and UPI-related uncore units used by adjacent event catalogs.

## Risks

The main risk is incorrect scheduling from a wrong counter count. Overstating counters can make perf attempt impossible event groups; understating them can unnecessarily multiplex or reject valid groups. Mixed numeric/string typing can break strict validators. Hardware SKUs may not expose every uncore unit even though the model table lists it, so runtime code still needs PMU discovery and graceful fallback.

## Test Signals

Validation should include JSON parsing that accepts mixed value types, generated table inspection, and `perf stat` group scheduling tests around 4-event, 8-event, and fixed-counter boundaries. Runtime tests should compare listed units against `/sys/bus/event_source/devices` on Sierra Forest systems and verify absent uncore units do not break perf list or metrics.

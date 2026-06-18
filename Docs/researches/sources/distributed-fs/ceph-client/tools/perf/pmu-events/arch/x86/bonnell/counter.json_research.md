# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/bonnell/counter.json

## Purpose

This metadata file declares Bonnell counter topology rather than a normal event alias. It states that the `core` unit has `CountersNumGeneric` set to 2 and `CountersNumFixed` set to 3.

## Important APIs, Types, And Data

The single object uses `Unit`, `CountersNumGeneric`, and `CountersNumFixed`. It intentionally lacks `EventName`, `EventCode`, and descriptions, so it is not an event users select by alias. The values describe the hardware counter resources available to perf and generated PMU metadata consumers.

## Control Flow

When `jevents.py` reads this file, the object has no `EventName`, so it does not become a normal pending event. Its fields are still part of the PMU event metadata corpus and can inform generated tables or tooling paths that inspect counter resources.

## State And Persistence Behavior

The file persistently documents Bonnell core counter counts. It does not track allocation state. Runtime allocation and scheduling of two generic counters and three fixed counters is managed by perf and the kernel PMU driver.

## Dependencies And Integration Points

The metadata integrates with the Bonnell model directory and perf PMU event generation. It is relevant to event scheduling, group feasibility, and user expectations when too many events are requested for simultaneous counting.

## Risks And Edge Cases

Because the object is structurally different from event records, schema consumers must tolerate records without `EventName`. Treating this as a malformed event would break generation. Incorrect counter counts can mislead scheduling diagnostics and event-group expectations.

## Test Signals

Validation should confirm the JSON parses and `jevents.py` generation does not emit an empty bogus alias. Perf event scheduling tests on Bonnell-like fixtures should respect two programmable and three fixed counters.

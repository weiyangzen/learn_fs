# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/counter.json

## Purpose

`counter.json` records Goldmont PMU counter topology. It declares that the `core` PMU has 3 fixed counters and 4 generic programmable counters.

## Important APIs, Types, and Data Fields

The file is a one-object JSON array with `Unit: core`, `CountersNumFixed: 3`, and `CountersNumGeneric: 4`. Unlike event catalogs, it has no `EventName`, `EventCode`, `UMask`, or descriptions.

## Control Flow and Data Flow

There is no control flow. Perf metadata generation reads this file as capability data for the Goldmont core PMU. The values inform scheduling, grouping, multiplexing decisions, and validation of event counter availability.

## State and Persistence Behavior

The file persists static PMU topology only. It does not track active counters, current values, or runtime scheduling state. Runtime perf sessions use the values as constraints but store measurements elsewhere.

## Dependencies and Integration Points

This metadata depends on the Goldmont PMU architecture and integrates with the rest of the Goldmont event files in this directory. It is relevant to perf event scheduling and to tests that assert how many events can be measured concurrently without multiplexing.

## Risks and Edge Cases

The absence of event rows is intentional; tools must not require `EventName` for counter-topology files. If the fixed/generic counts are wrong, perf may overpromise grouping or unnecessarily multiplex events. Consumers should parse the numeric strings as counts and associate them with `Unit: core`.

## Test Signals

Validation should include JSON parsing, schema compatibility for counter files, and perf scheduling tests that can place up to four generic core events plus fixed-counter events according to Goldmont capabilities. Regression tests should ensure event-list generators do not try to display this object as a normal PMU event.

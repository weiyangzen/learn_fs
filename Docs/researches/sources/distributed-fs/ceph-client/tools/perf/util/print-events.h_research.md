# sources/distributed-fs/ceph-client/tools/perf/util/print-events.h

## Purpose
This header defines the callback interface for printing event and metric catalogs independent of the final output format.

## Important APIs, Types, and Functions
`struct print_callbacks` contains lifecycle callbacks, `print_event`, `print_metric`, and `skip_duplicate_pmus`. It declares `print_events`, `print_sdt_events`, `metricgroup__print`, and `is_event_supported`.

## Control Flow
The header is declarative. Implementations call callbacks in a producer-defined order, allowing text, JSON, or other output formats to share event discovery logic.

## State and Persistence
No state is stored here. The caller supplies a `print_state` pointer passed back to every callback.

## Dependencies and Integration Points
It depends on Linux perf event and type definitions and is consumed by PMU printing, libpfm printing, and command output code.

## Risks
The callback contract assumes `skip_duplicate_pmus` is non-null where used. Field order and nullable string behavior must remain consistent across producers and output backends.

## Test Signals
Mock callback tests can validate all producers pass expected nullability, PMU metadata, descriptions, encodings, and duplicate-skipping decisions.

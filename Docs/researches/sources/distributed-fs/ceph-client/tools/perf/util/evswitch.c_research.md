# sources/distributed-fs/ceph-client/tools/perf/util/evswitch.c

## Purpose

`evswitch.c` implements event-driven filtering windows for perf output. It lets a tool discard samples until a named switch-on event appears and resume discarding when a named switch-off event appears.

## Important APIs, Types, and Functions

`evswitch__init` resolves `on_name` and `off_name` into `struct evsel *` objects from an evlist and initializes starting discard state. `evswitch__discard` decides whether a sample/event for a given evsel should be suppressed and toggles state when on/off events are seen. `evswitch__fprintf_enoent` prints missing-event diagnostics.

## Control Flow

Initialization first resolves the on event; if present, the switch starts in discarding mode. It then resolves the off event. Runtime filtering has two phases: while discarding, all events are dropped until the on event appears; while accepting, events pass until the off event appears. The switch marker event itself is dropped unless `show_on_off_events` is set.

## State and Persistence Behavior

The mutable state is `evswitch->discarding` plus resolved `on`/`off` pointers. Names are borrowed option strings. No state is persisted to disk.

## Dependencies and Integration Points

It depends on evlists and evsels, especially `evlist__find_evsel_by_str`. The option surface is declared in the header and is intended for perf commands that support `--switch-on`, `--switch-off`, and `--show-on-off-events`.

## Risks and Edge Cases

Missing names fail initialization with `-ENOENT`. Duplicate event names depend on evlist lookup semantics. If only `off` is configured, collection starts enabled and turns off at the first off event. Marker visibility can surprise tests because switching events are suppressed by default.

## Test Signals

Tests should cover on-only, off-only, on/off pairs, missing event names, duplicate names, marker visibility, and streams where on/off events occur multiple times.

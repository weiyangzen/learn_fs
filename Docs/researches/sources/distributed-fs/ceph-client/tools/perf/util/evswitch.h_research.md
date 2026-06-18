# sources/distributed-fs/ceph-client/tools/perf/util/evswitch.h

## Purpose

`evswitch.h` declares the small state machine used to gate perf event output between named on/off events.

## Important APIs, Types, and Functions

`struct evswitch` stores resolved `on` and `off` evsels, option-provided names, current `discarding` state, and `show_on_off_events`. `evswitch__init` resolves names against an evlist. `evswitch__discard` evaluates and updates the filter state. `OPTS_EVSWITCH` expands to command-line options for `--switch-on`, `--switch-off`, and `--show-on-off-events`.

## Control Flow

Perf commands embed an `evswitch`, include `OPTS_EVSWITCH` in option parsing, call `evswitch__init` after evlist construction, and then call `evswitch__discard` for each event to decide whether to display/process it.

## State and Persistence Behavior

All state is in memory for one command invocation. The header does not define ownership transfer for the name strings; they are typical option-parser storage.

## Dependencies and Integration Points

It forward-declares `evsel` and `evlist`, includes boolean and stdio types, and relies on the perf option macro API being available where `OPTS_EVSWITCH` is used.

## Risks and Edge Cases

The option macro assumes `OPT_STRING` and `OPT_BOOLEAN` are visible at expansion sites. Tools must initialize the struct to zero before option parsing or stale pointers/state can affect filtering.

## Test Signals

Compile tests for option users and runtime switch filtering tests provide coverage. Zero-initialization tests are useful because the state machine has no separate constructor beyond `evswitch__init`.

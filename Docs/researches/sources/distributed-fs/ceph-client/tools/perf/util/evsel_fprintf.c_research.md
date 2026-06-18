# sources/distributed-fs/ceph-client/tools/perf/util/evsel_fprintf.c

## Purpose

`evsel_fprintf.c` formats event selectors and sample symbol/callchain data for text output. It supports compact event printing, verbose attribute dumps, grouped-event rendering, tracepoint field listing, and symbolized sample/callchain lines.

## Important APIs, Types, and Functions

`evsel__fprintf` prints either a single event or a full group depending on `struct perf_attr_details`. It can append verbose `perf_event_attr` fields or sample frequency/period. `sample__fprintf_callchain` walks a committed `callchain_cursor` and prints IPs, symbols, DSO names/offsets, source lines, arrows, inline markers, and stop-list behavior. `sample__fprintf_sym` delegates to callchain printing when a cursor is present or prints one resolved address location.

## Control Flow

Formatting starts with `comma_fprintf`, which inserts the initial colon and later commas for attribute-like suffixes. Group mode prints only from leaders and iterates members. Trace-field mode validates the event is a tracepoint and walks libtraceevent format fields. Callchain output commits the cursor, loops nodes, skips ignored symbols if requested, maps IPs through maps, resolves symbols/source lines, stops on configured backtrace stop symbols, and advances the cursor.

## State and Persistence Behavior

The file does not own long-lived state. It reads `evsel`, `perf_sample`, callchain cursor, map, symbol, DSO, and strlist state owned elsewhere. Output persistence is only the bytes written to the caller-provided `FILE *`.

## Dependencies and Integration Points

It integrates with event naming, perf-event attribute formatting, traceevent formats, callchain cursors, maps, symbols, DSOs, source-line lookup, address locations, and strlists. It is a presentation layer used by tools such as `perf evlist`, `perf script`, and report-like flows.

## Risks and Edge Cases

Null cursors print an explicit memory warning. Symbol/map pointers may be absent, so unknown-address formatting flags matter. Trace-field printing depends on tracepoint format availability. Callchain cursor state must be prepared by callers; otherwise no frames are printed. Oneline mode changes separators and newline behavior.

## Test Signals

Tests should compare output for grouped and ungrouped events, verbose/frequency modes, tracepoint field mode, callchains with and without symbols/maps/source lines, ignored-symbol skip lists, deferred-callchain cookies, and oneline versus multiline formatting.

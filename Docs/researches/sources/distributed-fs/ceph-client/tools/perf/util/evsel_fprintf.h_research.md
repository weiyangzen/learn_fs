# sources/distributed-fs/ceph-client/tools/perf/util/evsel_fprintf.h

## Purpose

`evsel_fprintf.h` declares the text-formatting contract for event selectors and sample symbol/callchain output.

## Important APIs, Types, and Functions

`struct perf_attr_details` selects frequency, verbose, event group, forced, and trace-field output modes. `EVSEL__PRINT_*` bit flags control IP, symbol, DSO, symbol offset, DSO offset, one-line output, source lines, unknown-address handling, callchain arrows, and ignored-frame skipping. The header declares `evsel__fprintf`, `sample__fprintf_callchain`, `sample__fprintf_sym`, the attribute callback type, and `perf_event_attr__fprintf`.

## Control Flow

Callers construct `perf_attr_details` or print-option bitmasks and pass the relevant `evsel`, `perf_sample`, `addr_location`, callchain cursor, stop list, and output stream. The implementation performs all formatting and returns the printed character count.

## State and Persistence Behavior

No state is stored in the header. The option structs and bit flags define transient formatting policy; output is persisted only through the supplied `FILE *`.

## Dependencies and Integration Points

It forward-declares perf sampling, address-location, callchain, and strlist types so reporting and script code can include the API without pulling full implementations. It also exposes the generic perf-event-attribute formatter callback contract used by verbose event output.

## Risks and Edge Cases

The print flags are bit positions, so new flags must avoid collisions. `perf_attr_details.force` is declared here but not used by the inspected implementation, so consumers should verify intended semantics before relying on it.

## Test Signals

Compile coverage across report/script/evlist users, golden-output tests for each flag combination, and ABI checks for new print flags are the main signals.

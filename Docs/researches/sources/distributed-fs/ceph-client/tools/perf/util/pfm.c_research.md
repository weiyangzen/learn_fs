# sources/distributed-fs/ceph-client/tools/perf/util/pfm.c

## Purpose
This file integrates libpfm4 event encoding into perf. It parses `--pfm-events` style event strings into perf evsels and lists host-supported libpfm events through perf's generic print callback interface.

## Important APIs, Types, and Functions
Exports are `parse_libpfm_events_option` and `print_libpfm_events`. Internal helpers include `libpfm_initialize`, `is_libpfm_event_supported`, `print_attr_flags`, and `print_libpfm_event`. It uses libpfm APIs such as `pfm_initialize`, `pfm_get_perf_event_encoding`, `pfm_get_pmu_info`, `pfm_get_event_info`, and `pfm_get_event_attr_info`.

## Control Flow
`parse_libpfm_events_option` duplicates the user string, tokenizes it on commas and braces, rejects nested groups, encodes each libpfm event into `perf_event_attr`, creates an evsel, marks it as a libpfm event, and applies group leadership. `print_libpfm_events` initializes libpfm, iterates present non-perf-event PMUs, fetches each event, builds an encoding description, checks support by attempting to open the event, and emits event or umask rows through callbacks.

## State and Persistence
There is no durable state in this file. It mutates the caller's `evlist` during parsing and creates transient CPU/thread maps while checking support.

## Dependencies and Integration Points
This file is compiled only when libpfm support is enabled. It integrates with perf parse-options, evlist/evsel creation, PMU lookup, thread and CPU maps, and print-events output.

## Risks
Group parsing is simple and does not support nesting. Support checks open real perf events and can vary by privileges, paranoid settings, CPU availability, and PMU driver behavior. Event listing can be expensive because every candidate may be probed.

## Test Signals
Tests should cover single events, grouped events, bad group syntax, unsupported libpfm names, and print output on hosts with and without libpfm PMUs. Permission-sensitive tests should validate the exclude-kernel retry path.

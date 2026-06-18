# sources/distributed-fs/ceph-client/tools/perf/util/evsel_config.h

## Purpose

`evsel_config.h` defines per-event configuration terms parsed from event modifiers and later applied by `evsel__config`. It is the data contract between parse-events code and the event-selector configuration path.

## Important APIs, Types, and Functions

`enum evsel_term_type` enumerates supported modifiers: period, frequency, time, callgraph, stack size, inherit, max stack/events, overwrite, driver config, branch stack, percore, AUX output/action/sample size, user-changed `config` through `config4`, and `ratio-to-prev`. `struct evsel_config_term` stores the term type, whether a string must be freed, a union value, a `weak` override flag, and list linkage. `evsel__get_config_term` wraps `__evsel__get_config_term` with enum-token construction.

## Control Flow

Parser code allocates these terms and appends them to `evsel::config_terms`. `evsel__apply_config_terms` walks the list, mutates `perf_event_attr`, configures callgraphs and branch stacks, applies weak override semantics, and records user-changed PMU config bits so later defaults do not overwrite explicit user settings.

## State and Persistence Behavior

Each term persists until `free_config_terms` or `evsel__exit`. String-valued terms use `free_str` to distinguish owned strings from borrowed values. The `weak` flag lets defaults be superseded by global user options without losing the parsed term object.

## Dependencies and Integration Points

The header depends on list heads, Linux integer types, and booleans. It integrates directly with parse-events, PMU format packing, callchain parsing, AUX trace configuration, and `evsel.c` clone/free logic.

## Risks and Edge Cases

Adding a term requires updates in parsers, clone/free paths, and `evsel__apply_config_terms`; otherwise modifiers may parse but never take effect or may leak. The union requires the selected member to match `type`. Incorrect `free_str` handling causes leaks or invalid frees.

## Test Signals

Tests should parse events with every modifier, clone selectors before opening, then verify resulting `perf_event_attr` fields, config-term lifetime under failure paths, and weak override behavior for global period/frequency options.

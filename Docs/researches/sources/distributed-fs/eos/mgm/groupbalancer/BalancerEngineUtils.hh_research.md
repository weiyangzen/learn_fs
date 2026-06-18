# sources/distributed-fs/eos/mgm/groupbalancer/BalancerEngineUtils.hh

## Purpose
Provides small header-only helpers shared by the group balancer engines for average calculation, typed configuration extraction, percent parsing, comma-list parsing, and threshold validation.

## Important APIs, types, and functions
`calculateAvg()` averages `GroupSizeInfo::filled()` over a `group_size_map`. `extract_value()` is a generic map lookup plus extractor wrapper that invokes the extractor on an empty string when a key is missing. `extract_double_value()` uses `common::StringToNumeric()` with a default and optional error string. `extract_percent_value()` converts configured percent values to fractions. `extract_commalist_value()` returns an unordered set from a comma/space-delimited string. `is_valid_threshold()` validates one or more positive numeric strings.

## Control flow
Engines call these helpers during `configure()` and `recalculate()`. Missing config keys flow through defaults, while invalid numeric strings are reported through the shared error string and logged by callers.

## State and persistence
This file stores no state and performs no persistence. Its outputs become in-memory engine thresholds and blocklists.

## Dependencies and integration points
Depends on `common/StringUtils.hh`, `common/StringSplit.hh`, and `BalancerEngine.hh` types. It is used by `MinMaxBalancerEngine`, `StdDevBalancerEngine`, `StdDrainerEngine`, and `FreeSpaceBalancerEngine`.

## Risks and test signals
`std::stod()` accepts partial numeric strings, so threshold validation may allow values with suffixes. Default values passed to `extract_percent_value()` are treated as percent values, which makes callers sensitive to whether they pass `2` or `0.02`. Tests should cover missing keys, malformed strings, zero/negative thresholds, comma-list whitespace, and multi-threshold validation.

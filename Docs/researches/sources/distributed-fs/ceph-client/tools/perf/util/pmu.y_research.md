# sources/distributed-fs/ceph-client/tools/perf/util/pmu.y

## Purpose
This bison grammar parses PMU format files into sparse bitmaps describing which bits of `perf_event_attr.config`, `config1`, `config2`, `config3`, or `config4` a named format term controls.

## Important APIs, Types, and Functions
The grammar accepts `PP_CONFIG ':' bits` and `PP_CONFIG PP_VALUE ':' bits`. `perf_pmu__set_format` builds a bitmap for single bits or ranges. Reductions call `perf_pmu_format__set_value(format, config_index, bits)`.

## Control Flow
The parser recognizes one or more format terms. `bits` is a comma-joined union of `bit_term` values, and `bit_term` is either a single number or a closed numeric range. Empty `to` values in `perf_pmu__set_format` mean a single bit.

## State and Persistence
The parser mutates the `struct perf_pmu_format` supplied through `%parse-param {void *format}`. It has no global state and uses a pure parser with reentrant lexer state.

## Dependencies and Integration Points
It depends on Linux bitmap helpers and `PERF_PMU_FORMAT_BITS` from `pmu.h`. `pmu.c` invokes it when a PMU format file is loaded.

## Risks
There is no explicit range validation in the grammar body before setting bits, so invalid large values depend on bitmap helper behavior and parser input constraints. Error reporting is intentionally silent through `perf_pmu_error`, making diagnostics depend on higher layers.

## Test Signals
Tests should validate config target selection, bit unions, ranges, single-bit terms, multiple format terms, and parse failures. Fuzzing malformed sysfs format text can catch grammar acceptance issues.

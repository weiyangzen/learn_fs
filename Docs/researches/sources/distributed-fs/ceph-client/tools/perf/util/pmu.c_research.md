# sources/distributed-fs/ceph-client/tools/perf/util/pmu.c

## Purpose
This file implements individual PMU discovery, metadata loading, event alias handling, event-term to `perf_event_attr` encoding, PMU matching, sysfs path helpers, capabilities parsing, and cleanup. It is the core implementation behind `struct perf_pmu`.

## Important APIs, Types, and Functions
Key public APIs include `perf_pmu__init`, `perf_pmu__lookup`, `perf_pmu__config`, `perf_pmu__config_terms`, `perf_pmu__check_alias`, `perf_pmu__for_each_event`, `perf_pmu__num_events`, `perf_pmu__for_each_format`, `perf_pmu__format_pack`, `perf_pmu__format_unpack`, `perf_pmu__caps_parse`, `perf_pmu__warn_invalid_config`, `perf_pmu__pathname_*`, and `perf_pmu__delete`. Internal `struct perf_pmu_alias` stores sysfs and JSON event alias metadata.

## Control Flow
PMU creation reads type, format file names, CPU masks, uncore identifiers, alias names, max precision, event tables, and architecture defaults. Format files are often registered first and parsed lazily through flex/bison when needed. Alias lookup first checks the case-insensitive hashmap, optionally probes sysfs for a matching event file, then loads sysfs aliases or JSON events. Configuration parses terms, resolves aliases into weak terms, validates format names and maximum values, and packs sparse bitfields into `config` through `config4`.

## State and Persistence
State lives in the caller-owned `struct perf_pmu`: format lists, alias hashmap, sysfs/json alias counters, caps list, CPU maps, identifier strings, config masks, and lazy-loaded flags. Persistent external state is read from sysfs under `/bus/event_source/devices/<pmu>/` and built-in pmu-events tables.

## Dependencies and Integration Points
The file integrates with `pmus.c` for global registry scans, parse-events term structures, hwmon and DRM PMU specializations, tool and tracepoint PMUs, PMU JSON event tables, sysfs helpers, locale-safe scale parsing, and architecture hooks through weak `perf_pmu__arch_init`.

## Risks
Lazy loading makes ordering subtle: callers must tolerate aliases, formats, and caps becoming available on demand. Incorrect format masks can silently truncate config values when no parse error object is supplied. Sysfs and JSON aliases can overlap, with sysfs metadata being enriched or overridden by JSON. Regex matching for uncore identifiers and wildcard suffix stripping are compatibility-sensitive.

## Test Signals
Tests should use synthetic sysfs directories for format parsing, alias parsing, unit/scale/per-pkg/snapshot files, caps, invalid terms, value overflow, JSON/sysfs overlap, uncore name matching, and fake PMUs. Integration tests should verify that parsed event strings produce expected `perf_event_attr` fields.

# sources/distributed-fs/ceph-client/tools/perf/util/amd-sample-raw.c

## Purpose

`amd-sample-raw.c` decodes AMD IBS raw sample MSR payloads for `perf report/script -D` style dumps. It turns fetch and op raw data into readable fields, with CPU-family erratum handling and PMU capability-dependent output.

## Important APIs, Types, and Functions

Public APIs are `evlist__amd_sample_raw` and `evlist__has_amd_ibs`. Helpers print IBS fetch control, extended fetch control, op control/data/data2/data3, fetch/op addresses, and branch targets. Static state caches CPU family/model, PMU type numbers for `ibs_fetch` and `ibs_op`, and capabilities `zen4_ibs_extensions`, `ldlat_cap`, and `dtlb_pgsize_cap`.

## Control Flow and State

`evlist__has_amd_ibs` parses PMU mappings and capabilities from `perf_env`, then parses CPUID if IBS PMUs exist. During event dumping, `evlist__amd_sample_raw` checks event type and raw size, maps the sample to an evsel, validates enable/valid bits, and dispatches to fetch or op decoders. Decoders cast raw MSR order into IBS union types and print fields conditionally.

## Dependencies and Integration Points

It depends on AMD IBS union definitions, perf env/session/evlist/sample APIs, and debug output. It integrates with generic sample raw dumping through `sample-raw.h`.

## Risks and Test Signals

Risks include raw-size assumptions, PMU type zero ambiguity, CPU errata conditions, reserved data-source values, and stale static capability state across sessions. Tests need AMD IBS fetch/op samples from Zen generations, invalid raw samples, Zen4 capability fields, erratum-affected family 0x19 models, and sessions without IBS mappings.

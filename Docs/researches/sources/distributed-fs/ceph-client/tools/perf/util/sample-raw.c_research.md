# sources/distributed-fs/ceph-client/tools/perf/util/sample-raw.c

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/sample-raw.c` selects architecture/vendor-specific raw sample interpreters for a perf evlist based on perf.data environment metadata.

## Important APIs, Types, and Functions

The public function is `evlist__init_trace_event_sample_raw`.

## Control Flow

The function reads architecture and CPUID strings from `perf_env`. If the architecture is `s390`, it installs `evlist__s390_sample_raw`. If the architecture is `x86`, CPUID starts with `AuthenticAMD`, and the evlist has AMD IBS events, it installs `evlist__amd_sample_raw`. Otherwise no callback is set.

## State and Persistence Behavior

It mutates the caller-owned `evlist->trace_event_sample_raw` function pointer. No persistent state is written.

## Dependencies and Integration Points

It depends on perf env metadata, evlist helpers, AMD IBS detection, and s390 raw-sample support declared in `sample-raw.h`. It is part of perf report/script raw sample display setup.

## Risks and Edge Cases

Selection depends on recorded environment strings; missing or unexpected arch/CPUID values leave raw samples uninterpreted. AMD detection is both vendor and event-list dependent. Only one callback is selected.

## Test Signals

Tests should cover s390 selection, AMD x86 IBS selection, x86 non-AMD no-op, AMD without IBS no-op, missing env fields, and callback pointer preservation/overwrite expectations.

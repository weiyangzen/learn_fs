<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/pfm.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/pfm.c

## Purpose

This selftest validates perf's optional libpfm4 event parser for plain event lists and grouped event expressions.

## Research

When `HAVE_LIBPFM` is enabled, `count_pfm_events` walks a `perf_evlist`. `test__pfm_events` feeds strings such as empty input, `instructions`, repeated events, unknown `stereolab`, and mixed known/unknown entries to `parse_libpfm_events_option`, then checks event count and zero groups. `test__pfm_group` covers `{}` groups, repeated groups, mixed invalid groups, unmatched braces, and nested braces, verifying both evsel count and group count. Without libpfm support both tests skip. State is per-case newly allocated evlists. Dependencies are libpfm integration in `util/pfm.h`, the option callback ABI, and perf grouping semantics. Integration catches regressions in command-line `--pfm-events` parsing. Risks are libpfm event availability differences and permissive parser behavior that intentionally accepts some malformed tails. Test signals are exact expected event and group counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/pfm.c -->

# sources/distributed-fs/ceph-client/tools/perf/tests/hists_link.c

## Purpose
Tests matching and linking histograms from two evsels, including common entries, distinct entries, dummy paired entries, and collapsed duplicates.

## Important APIs, Types, and Functions
- `fake_common_samples[]` defines five entries expected to pair between the two hists.
- `fake_samples[2][5]` defines evsel-specific entries; the second evsel has a duplicate `bash/libc/malloc` that collapses.
- `add_hist_entries()` adds common and distinct samples to each evsel via `hists__add_entry()`.
- `find_sample()` matches a hist entry against known sample arrays by thread, map, and symbol.
- `validate_match()` checks `hists__match()` pairs only common entries.
- `validate_link()` checks `hists__link()` creates expected pair/dummy relationships.

## Control Flow
The suite creates an evlist with `cpu-clock` and `task-clock`, builds the fake machine, sets sorting, adds sample entries, and collapse-resorts each hists object. It then selects first and last evsel hists. First it calls `hists__match()` and validates only common samples have pairs. Next it calls `hists__link()` and validates the leader has dummy entries for other-only samples while the other hists entries all have pairs and no dummy entries.

## State and Persistence
All state is in-memory inside evlist/hists and static sample reference fields. Static map references are released at cleanup. The test mutates hist entry pair lists and may create dummy entries during linking.

## Dependencies and Integration Points
Integrates shared fake machine setup, sort setup/reset, evlist parsing, hist entry insertion, and hists match/link APIs. Registered as `DEFINE_SUITE("Match and link multiple hists", hists_link)`.

## Risks and Edge Cases
- Expected dummy count accounts for the collapsed duplicate in the second hists (`ARRAY_SIZE(fake_samples[1]) - 1`); changes in collapse semantics affect the test.
- Validation is based on thread/map/symbol identity, so reference-counting correctness in fixture setup matters.
- Only two hists are linked; multi-way linking behavior is not covered here.

## Test Signals
Passing confirms common entries are matched and distinct entries are linked through dummy pairs with expected counts. Failures print missing matched entries or invalid pair/dummy totals.

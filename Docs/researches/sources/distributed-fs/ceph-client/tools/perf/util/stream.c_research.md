# sources/distributed-fs/ceph-client/tools/perf/util/stream.c

## Purpose

`stream.c` compares hot callchain streams between evsels, typically for perf diff-style analysis. It selects the top N hottest callchain nodes per event, matches callchains across two evsels, and prints matched and unmatched hot streams.

## Important APIs, Types, and Functions

Public functions are `evlist__create_streams()`, `evlist_streams__delete()`, `evsel_streams__entry()`, `evsel_streams__match()`, and `evsel_streams__report()`. Private helpers allocate per-evsel stream arrays, select hot callchain nodes, initialize from hists, match callchains, link pairs, and print reports.

## Control Flow and Data Flow

Creation allocates an `evlist_streams` sized to the evlist and a fixed-size `stream` array for each evsel. It resorts hists output, walks each hist entry's sorted callchain tree, and keeps the highest-hit callchain nodes using a simple replacement of the current smallest hit. Matching iterates base streams, finds the first pair stream whose callchain node matches via `callchain_cnode_matched()`, and stores reciprocal `pair_cnode` pointers. Reporting prints matched pairs, old-only streams, and new-only streams with hit percentages and average cycles.

## State and Persistence Behavior

Stream structures borrow callchain node pointers from hists; they do not own callchain data. Pairing state is stored in `pair_cnode` fields until the stream object is deleted. Output goes directly to stdout.

## Dependencies and Integration Points

It depends on hists, sort resorting, evlist/evsel iteration, callchain node/list helpers, debug support, and zalloc. It integrates with analysis that compares old and new perf data callchains.

## Risks and Edge Cases

The hot-stream selection is O(N * max_streams) and intentionally simple for small N. Equal hit counts do not replace existing streams. Borrowed callchain pointers require the underlying hists to outlive the stream object. Reporting assumes pair callchains have compatible list traversal. `printf()` to stdout bypasses configurable perf output streams.

## Test Signals

Tests should cover creation/deletion, top-N replacement, no callchains, matching and unmatched streams, hit percentage calculation, average cycle display, multiple evsels, and lifetime ordering with hists.

# sources/distributed-fs/ceph-client/tools/perf/util/stream.h

## Purpose

`stream.h` declares the hot-callchain stream comparison data structures and API.

## Important APIs, Types, and Functions

`struct stream` stores a selected callchain node and its matched pair node. `struct evsel_streams` stores one evsel's stream array, capacity, count, total hits, and evsel pointer. `struct evlist_streams` stores all evsel stream sets. The API creates, deletes, finds, matches, and reports streams.

## Control Flow and Data Flow

Consumers create streams from an evlist, fetch entries for particular evsels, match two `evsel_streams`, report results, and delete the container.

## State and Persistence Behavior

The structures own only their arrays, not callchain nodes. Pair state is mutable and process-local.

## Dependencies and Integration Points

The header forward-declares callchain, evlist, and evsel types and is implemented by `stream.c`.

## Risks and Edge Cases

Callchain owners must outlive stream structures. Callers should not reuse pair state across unrelated comparisons without rebuilding or clearing it.

## Test Signals

Build coverage plus stream comparison tests against synthetic hists validate the contract.

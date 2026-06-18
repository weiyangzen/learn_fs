<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/gc/gc_test.go -->
# sources/distributed-fs/ipfs-kubo/gc/gc_test.go

## Purpose

This test validates the mark-and-sweep behavior of `GC` against direct pins, recursive pins, best-effort roots, and unpinned DAGs.

## Important APIs, Types, and Functions

`TestGC` constructs an in-memory datastore, GC blockstore, DAG service, datastore-backed pinner, and DAG generator. It pins direct and recursive DAGs, adds unpinned DAGs, adds best-effort root DAGs, runs `GC`, and compares removed/kept multihashes. `toMHs` maps CIDs to multihashes for codec-insensitive comparison.

## Control Flow, State, and Integration

The test creates known DAG sets, tracks expected kept and discarded hashes, drains the GC result channel while requiring no errors, then enumerates remaining blockstore keys.

## Dependencies, Risks, and Test Signals

Dependencies include boxo blockstore, merkledag test utilities, dspinner pinner, and testify. The test does not cover delete failure, traversal failure, context cancellation, or datastore compaction errors, but it strongly signals the main mark/sweep contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/gc/gc_test.go -->

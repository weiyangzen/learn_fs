<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/gc/gc.go -->
# sources/distributed-fs/ipfs-kubo/gc/gc.go

## Purpose

`gc.go` implements Kubo block garbage collection. It computes a colored set of blocks reachable from pins and best-effort roots, then sweeps unmarked blocks from the GC blockstore and optionally asks the datastore to collect its own garbage.

## Important APIs, Types, and Functions

`Result` carries either a removed CID or an error. `toRawCids` normalizes marked CIDs to raw CIDv1 by multihash. `GC` locks the blockstore, builds a DAG service, calls `ColoredSet`, iterates `AllKeysChan`, deletes unmarked blocks, emits incremental results, and invokes `dstore.GCDatastore.CollectGarbage` when available. `Descendants` validates CIDs and walks DAGs from streamed pins. `ColoredSet` marks recursive pins, best-effort roots, direct pins, and internal pins. Error types include `CannotFetchLinksError` and `CannotDeleteBlockError`.

## Control Flow, State, and Integration

GC runs asynchronously and returns a channel. It uses context cancellation to stop work and unlocks the blockstore in a deferred cleanup. Missing best-effort root links are tolerated only when they are not found; other traversal errors abort marking. Delete errors are non-fatal per block but cause a final `ErrCannotDeleteSomeBlocks`. Persistent state changes are block deletions and optional datastore compaction.

## Dependencies, Risks, and Test Signals

Dependencies are boxo blockstore/blockservice/offline exchange/merkledag/pinner, datastore GC, cid sets, verifcid, and IPLD traversal. Risks include high memory use for the colored set, CID codec normalization assumptions, aborting on insecure hash validation, partial delete failures, and best-effort root semantics. `gc_test.go` verifies pinned and best-effort DAGs are kept while unpinned DAGs are removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/gc/gc.go -->

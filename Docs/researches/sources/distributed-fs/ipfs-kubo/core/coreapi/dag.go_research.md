# sources/distributed-fs/ipfs-kubo/core/coreapi/dag.go

Purpose: wraps the node DAG service for CoreAPI and provides DAG adders that also pin.

Important APIs/types/functions: `dagAPI` embeds `ipld.DAGService`; `pinningAdder` implements `ipld.NodeAdder`; methods `Add`, `AddMany`, `Pinning`, and `Session`.

Control flow: `pinningAdder.Add` locks the blockstore pin lock, adds a node to DAG, pins it recursively, and flushes. `AddMany` adds all nodes first, deduplicates CIDs with a CID set, pins each unique CID recursively, and flushes. `Pinning` returns a node adder backed by the CoreAPI. `Session` returns a merkledag session getter.

State and persistence behavior: writes DAG blocks and pin state, flushing pins for durability. Uses pin lock to coordinate with garbage collection.

Dependencies and integration points: used by CoreAPI `Dag()`. Depends on boxo merkledag/session, pinning pinner, blockstore pin locking, and tracing.

Risks: `AddMany` adds DAG nodes before pinning; partial failure after add but before all pins can leave unpinned blocks. Recursive pinning every unique node may be expensive for large batches.

Test signals: interface-level DAG behavior is exercised by `coreapi/test/api_test.go`.

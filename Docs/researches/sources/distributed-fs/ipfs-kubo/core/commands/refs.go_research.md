# sources/distributed-fs/ipfs-kubo/core/commands/refs.go

## Purpose

`refs.go` implements `ipfs refs` and `ipfs refs local`, listing linked CIDs from DAG objects or all local blockstore keys. It supports recursive traversal, unique output, max-depth pruning, edge formatting, and custom format tokens.

## Important APIs, Types, and Functions

`RefsCmd` emits `RefWrapper` and uses `RefWriter`. `RefsLocalCmd` emits all local blockstore keys. Helper `objectsForPaths` resolves input paths to root CIDs. `RefWriter` stores the response emitter, DAG getter/session, context, uniqueness flag, max depth, print format, and a seen-depth map. Methods are `WriteRefs`, `writeRefsRecursive`, `visit`, and `WriteEdge`.

## Control Flow

The command parses body args, obtains CoreAPI and CID encoder, resolves options, converts non-recursive mode to `maxDepth=1`, and maps `--edges` to format `<src> -> <dst>` while rejecting simultaneous custom format. It resolves all input paths to CIDs, creates a merkledag session, then writes refs for each root. Traversal iterates linked child nodes via `ipld.GetDAG`; `visit` decides whether to print and/or recurse based on depth limits and uniqueness. If a child must be printed or recursed into, the lazy getter is fetched, the edge is emitted, and recursion continues as allowed. `refs local` streams `n.Blockstore.AllKeysChan`.

## State and Persistence Behavior

The command is read-only. It may fetch DAG blocks during path resolution and traversal. Unique recursive traversals hold a map of seen CIDs and depths; local refs streams all blockstore keys.

## Dependencies and Integration Points

Dependencies include Kubo CoreAPI DAG/path resolution, Boxo merkledag sessions, go-ipld-format lazy traversal, CID encoding utilities, blockstore access through node, and command encoders. It integrates with repo listing as `ipfs repo ls`.

## Risks and Test Signals

Risks include memory growth for `--unique` on large DAGs, expensive recursive fetches, max-depth edge cases such as zero, custom format token replacement ambiguity, and emitting traversal errors as response objects that text encoding converts to errors. Tests should cover direct versus recursive refs, unique branch pruning at different depths, max-depth values, edges/custom format conflict, link names, traversal errors, context cancellation, local key streaming, CID base selection, and multiple roots.

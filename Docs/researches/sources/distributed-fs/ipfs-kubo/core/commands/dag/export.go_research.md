<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/export.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/dag/export.go

## Purpose

Implements `ipfs dag export`, streaming a selected DAG as CARv1, with optional best-effort local-only export and CLI progress.

## Important APIs, Types, and Functions

`dagExport` is the command handler. `exportPartialCAR` writes a partial CAR from the raw local blockstore. `finishCLIExport` handles CLI stream/progress output. `dagStore` adapts CoreAPI DAG reads to go-car storage, and `cidFromBinString` decodes CAR storage keys.

## Control Flow

The handler parses a CID/path, validates `--local-only` versus explicit `--offline=false`, obtains API, forces offline API for local-only, stats the root block, and starts a goroutine that writes CAR data to an `io.Pipe`. Normal export uses `gocar.TraverseV1` over a link system backed by `dagStore`. Local-only export uses `exportPartialCAR`, which writes the root header and walks links from the raw blockstore, skipping missing/unreadable subtrees. The response emits the pipe as `application/vnd.ipld.car` and waits for the writer error.

## State and Persistence Behavior

Read-only. Normal export may fetch missing blocks through DAG API when online. Local-only export is structurally limited to local blockstore reads and does not fetch.

## Dependencies and Integration Points

Uses CoreAPI, boxo blockstore/walker, go-car v2, IPLD link systems, selector traversal, `cmdenv`, `cmdutils`, and progress helpers.

## Risks and Edge Cases

Pipe error handling must avoid losing writer-side failures after client emit. Local-only silently skips unavailable subtrees by design, producing incomplete CARs. Normal export decorates offline not-found errors for user clarity. CLI post-run rejects unexpected multipart responses.

## Test Signals

No local tests in this subset. Useful tests include local-only skip semantics, `--offline=false` conflict, missing root failure, writer error propagation, and CAR content-type behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/export.go -->

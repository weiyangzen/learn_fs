<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/resolve.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/dag/resolve.go

## Purpose

Implements the core handler for `ipfs dag resolve`, resolving a path to the deepest resolved root CID plus unresolved remainder.

## Important APIs, Types, and Functions

`dagResolve(req, res, env)` gets CoreAPI, parses the path through `cmdutils.PathOrCidPath`, calls `api.ResolvePath`, and emits `ResolveOutput`.

## Control Flow

The handler resolves the path under the request context and converts the remainder segments into a path string with `path.SegmentsToString`.

## State and Persistence Behavior

Read-only. It may fetch path-resolution data depending on CoreAPI online/offline mode.

## Dependencies and Integration Points

Depends on boxo path utilities, `cmdenv`, `cmdutils`, and the `ResolveOutput` encoder defined in `dag.go`.

## Risks and Edge Cases

Invalid paths fail before API resolution. Remainders are returned rather than traversed further, so callers must distinguish fully resolved CIDs from partial paths.

## Test Signals

No direct tests. Useful coverage includes CID-only paths, paths with remainders, invalid path errors, and CID-base formatting through the encoder in `dag.go`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dag/resolve.go -->

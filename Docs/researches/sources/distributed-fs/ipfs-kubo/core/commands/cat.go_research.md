<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cat.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cat.go

## Purpose

Implements `ipfs cat`, which streams UnixFS file data for one or more IPFS/IPNS paths to stdout or RPC clients, with byte offset, length, and terminal progress support.

## Important APIs, Types, and Functions

`CatCmd` defines `ipfs-path` variadic arguments and `--offset`, `--length`, `--progress` options. The helper `cat(ctx, api, paths, offset, max)` resolves each path through `cmdutils.PathOrCidPath`, fetches UnixFS nodes, verifies they are files, seeks, applies aggregate length limits, and returns readers plus total length.

## Control Flow

The run handler validates non-negative offsets and lengths, parses stdin/body args, calls `cat`, sets response length, wraps all returned readers in `io.MultiReader`, and emits the stream. The CLI post-run skips progress for known short outputs, otherwise wraps emitted readers with `progressBarForReader` when `cmdenv.ShouldShowProgress` returns true.

## State and Persistence Behavior

The command is read-only. It can trigger path resolution and UnixFS block retrieval through CoreAPI unless the request is offline. No local config or repo state is mutated.

## Dependencies and Integration Points

Uses CoreAPI `Unixfs().Get`, boxo `files.File`, shared progress helpers from `get.go`, `cmdenv.ShouldShowProgress`, and command response length/streaming support. Directory inputs map to `iface.ErrIsDir`.

## Risks and Edge Cases

Offsets are consumed across multiple input paths, so a large offset can skip whole files. A file must implement `io.Seeker`; unsupported file implementations error. Stream read errors are returned through `res.Emit`, which is intentional so missing blocks surface to clients.

## Test Signals

No local tests in this subset. Regression coverage should include multi-path offset and length slicing, directory rejection, zero length, seek failures, short-output progress suppression, and missing-block propagation during `io.Copy`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cat.go -->

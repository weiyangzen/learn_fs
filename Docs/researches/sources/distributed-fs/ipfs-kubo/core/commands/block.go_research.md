<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/block.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/block.go

## Purpose

Defines the `ipfs block` plumbing command family for direct raw block access: stat, get, put, and rm. It is the command-layer bridge between CLI/RPC requests and the CoreAPI `Block()` service, with CID output honoring the shared `--cid-base` encoder.

## Important APIs, Types, and Functions

`BlockCmd` registers subcommands. `BlockStat` is the common stat/put response. `blockStatCmd` resolves a CID/path and returns CID plus size. `blockGetCmd` emits a raw block as `application/vnd.ipld.raw`. `blockPutCmd` imports streamed file arguments with `--cid-codec`, deprecated `--format`, `--mhtype`, `--mhlen`, `--pin`, and `--allow-big-block`. `blockRmCmd` resolves each argument and removes blocks with `--force` and quiet output.

## Control Flow

Handlers acquire CoreAPI with `cmdenv.GetApi`, parse paths through `cmdutils.PathOrCidPath`, and stream or emit typed results. `blockPutCmd` reads each multipart/stdin file, applies hash/codec options, stores through `api.Block().Put`, checks the 2 MiB soft size limit, and emits one result per input. `blockRmCmd` resolves immutable paths before removal and uses a CLI post-run loop to distinguish per-block failures from total aborts.

## State and Persistence Behavior

`put` writes blocks to the node blockstore and may pin recursively. `rm` deletes local blockstore entries; `force` affects nonexistent-block handling but not higher-level pin safety. `get` and `stat` are read-only except for possible network fetches when the request is not offline.

## Dependencies and Integration Points

Depends on `cmdenv`, `cmdutils`, CoreAPI block options, Kubo import config defaults, boxo files, `go-ipfs-cmds`, and multihash names. Integrates with global CID encoding flags and command response content-type metadata.

## Risks and Edge Cases

The deprecated `--format` path suppresses `--cid-codec` and can conflict with custom codec selection. Big blocks can be created only when explicitly allowed, and those may not transfer over standard Bitswap. `rm` emits per-block errors but returns a final error if any removal failed, which clients must handle as partial success.

## Test Signals

No file-local tests in this subset, but command tree coverage in `commands_test.go` includes all block subcommands. Good regression targets are CID codec/hash option combinations, stdin/multipart multiple puts, big-block rejection, raw content-type behavior, and partial `block rm` failure reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/block.go -->

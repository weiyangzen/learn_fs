<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdutils/utils.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cmdutils/utils.go

## Purpose

Holds reusable command utility functions for block-size safety, pin-name validation, CID/path parsing, and safe peer address copying.

## Important APIs, Types, and Functions

`AllowBigBlockOptionName`, `SoftBlockLimit`, and `AllowBigBlockOption` define the shared big-block override. `CheckCIDSize` loads a DAG node and delegates to `CheckBlockSize`. `ValidatePinName` enforces `MaxPinNameBytes`. `PathOrCidPath` accepts full paths or bare CID-like inputs. `CloneAddrInfo` clones peer address slices.

## Control Flow

`CheckBlockSize` allows any size only when `--allow-big-block` is true, otherwise rejects blocks over 2 MiB. `PathOrCidPath` first calls `path.NewPath(str)` and falls back to `/ipfs/` plus the string, returning the original error if both fail.

## State and Persistence Behavior

Utility functions are read-only except for DAG reads in `CheckCIDSize`. No persistent state is mutated.

## Dependencies and Integration Points

Uses boxo path, CoreAPI DAG service, go-cid, libp2p peer AddrInfo, and `go-ipfs-cmds`. Used by block put, DAG put/import, cat/get/files path parsing, and pin-related commands.

## Risks and Edge Cases

`PathOrCidPath` intentionally preserves original errors to avoid confusing fallback paths. Big-block override can create content that standard Bitswap peers cannot exchange. Pin-name length is by bytes, not runes.

## Test Signals

`utils_test.go` covers path fallback, original-error behavior, CID-with-path conversion, valid and invalid pin-name lengths, and Unicode byte counting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdutils/utils.go -->

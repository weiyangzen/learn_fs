<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/cidbase.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/cidbase.go

## Purpose

Provides shared command-environment helpers for CID output encoding, including the global `--cid-base` and deprecated `--upgrade-cidv0-in-output` options.

## Important APIs, Types, and Functions

`OptionCidBase` and `OptionUpgradeCidV0InOutput` are reusable command options. `GetCidEncoder` returns a `cidenc.Encoder`. `CidBaseDefined` checks whether `--cid-base` is set. `CidEncoderFromPath` infers output base from a CID embedded in a path.

## Control Flow

`GetCidEncoder` starts from `cidenc.Default`, applies a requested multibase encoder, and automatically enables CIDv0 upgrade for any base other than base58btc. If the deprecated upgrade flag is present, it overrides automatic behavior. `CidEncoderFromPath` extracts a likely CID from `CID`, `CID/...`, or `/namespace/CID/...`, decodes it, returns default encoding for CIDv0, and returns the CIDv1 multibase with upgrade enabled for CIDv1+.

## State and Persistence Behavior

No persistent state is changed. The functions only inspect request option maps or path strings.

## Dependencies and Integration Points

Uses `go-cid`, `go-cidutil/cidenc`, `go-ipfs-cmds`, and multibase. It is used by block, files, dag, filestore, and other commands that print CIDs.

## Risks and Edge Cases

Deprecated upgrade override can intentionally defeat automatic CIDv0 upgrade, producing output that may not match the requested base. `CidEncoderFromPath` is intentionally fuzzy and returns an error for non-CID paths, so callers must choose sensible fallback behavior.

## Test Signals

`cidbase_test.go` covers default encoding, base32 auto-upgrade, base58btc non-upgrade, deprecated overrides, CIDv0 path extraction, and CIDv1 base inference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/cidbase.go -->

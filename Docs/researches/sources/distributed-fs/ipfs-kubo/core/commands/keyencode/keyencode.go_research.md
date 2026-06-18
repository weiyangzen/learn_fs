<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/keyencode/keyencode.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/keyencode/keyencode.go

## Purpose

Provides peer/IPNS key encoding helpers for command output, supporting legacy base58 multihash and multibase CID forms.

## Important APIs, Types, and Functions

`OptionIPNSBase` defines the `--ipns-base` option defaulting to base36. `KeyEncoder` wraps an optional multibase encoder. `KeyEncoderFromString` parses labels, and `FormatID` formats a `peer.ID`.

## Control Flow

`KeyEncoderFromString` returns a zero encoder for `b58mh` and `v0`, preserving legacy `peer.ID.String()` output. For any other label it looks up a multibase encoder and stores it. `FormatID` either returns the legacy peer ID string or converts the peer ID to a CID and renders it in the requested base.

## State and Persistence Behavior

Pure formatting helper. No repo or network state.

## Dependencies and Integration Points

Uses `go-ipfs-cmds`, libp2p peer IDs, and multibase. `id.go` uses equivalent logic for `--peerid-base`; IPNS/name commands use `OptionIPNSBase`.

## Risks and Edge Cases

`FormatID` panics if `StringOfBase` fails, relying on prior encoder validation and valid peer IDs. Legacy labels are special-cased and do not use multibase.

## Test Signals

No direct tests in this subset. Useful tests include legacy labels, invalid base labels, base36/base32 output, and panic-free formatting for generated peer IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/keyencode/keyencode.go -->

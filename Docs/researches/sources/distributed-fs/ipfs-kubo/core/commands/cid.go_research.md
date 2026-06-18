<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cid.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cid.go

## Purpose

Defines repo-independent `ipfs cid` utilities for formatting, converting, inspecting, and listing multibase, multicodec, and multihash metadata.

## Important APIs, Types, and Functions

`CidCmd` registers `inspect`, `format`, `base32`, `bases`, `codecs`, and `hashes`. `cidFmtCmd` uses `cidFormatOpts`, `emitCids`, `toCidV0`, and `toCidV1`. `argumentIterator` merges positional and stdin arguments. `CidFormatRes`, `CodeAndName`, and `CidInspectRes` shape command output. Sorter types provide stable listings.

## Control Flow

`format` validates a printf-style CID format, optional version conversion, optional multicodec replacement, and optional output multibase. Requesting a non-base58btc base implicitly upgrades CIDv0 to CIDv1 unless `-v 0` is explicitly requested, where CIDv0 constraints are enforced. `emitCids` decodes each CID independently and emits non-fatal per-entry errors. `inspect` decodes one CID, derives base, codec, hash digest, CIDv0 feasibility, and CIDv1 canonical representation, with a PeerID fallback note.

## State and Persistence Behavior

All commands set `SetDoesNotUseRepo(true)` and are pure transformations over input strings and built-in multiformats tables. They do not read or write repo state.

## Dependencies and Integration Points

Uses `go-cid`, `go-cidutil`, multibase, multicodec, multihash, verifcid allowlist, IPLD multicodec registries, and libp2p peer ID conversion. `streamResult` from `commands.go` handles CLI non-fatal output errors.

## Risks and Edge Cases

CIDv0 conversion is valid only for dag-pb plus compatible sha2-256 hash. `emitCids` continues after per-CID decode/format errors, which can surprise clients expecting fail-fast behavior. `inspect` returns invalid-CID information as a typed result but its text encoder converts that into an error.

## Test Signals

`cid_test.go` covers CIDv0 with custom bases and implicit CIDv1 upgrade when a custom base is requested. Additional useful tests include unsupported multicodec conversion to CIDv0, stdin argument iteration errors, PeerID inspect hints, and sorted list stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cid.go -->

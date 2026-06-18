<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/cidbase_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/cidbase_test.go

## Purpose

Validates the shared CID encoder selection rules used across command output.

## Important APIs, Types, and Functions

`TestGetCidEncoder` uses synthetic `cmds.Request` instances to exercise `GetCidEncoder`. `TestEncoderFromPath` checks `CidEncoderFromPath` for CIDv0, CIDv1 base58btc, CIDv1 base32, namespaced paths, and malformed paths.

## Control Flow

Tests construct option maps and compare encoder fields directly. Path tests run a helper over multiple path shapes, then iterate bad inputs and assert extraction errors.

## State and Persistence Behavior

Pure unit tests. No repo, node, or filesystem state is used.

## Dependencies and Integration Points

Depends on `cidenc.Default`, multibase encoders, `cmds.Request`, and exact CID literals that encode representative version/base combinations.

## Risks and Edge Cases

Direct struct equality for encoders assumes stable comparable fields. The test intentionally treats IPNS and unknown namespaces as possible CID carriers, mirroring production fuzziness.

## Test Signals

Good coverage for automatic CIDv0 upgrade behavior and path-derived encoding. Remaining gaps include invalid multibase option errors and caller fallback behavior when no CID is found in a path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/cidbase_test.go -->

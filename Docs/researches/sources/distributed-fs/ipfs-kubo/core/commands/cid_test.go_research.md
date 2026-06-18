<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cid_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cid_test.go

## Purpose

Tests selected `ipfs cid format` option interactions, especially CIDv0 base restrictions and automatic CIDv1 upgrades when a non-default multibase is requested.

## Important APIs, Types, and Functions

`TestCidFmtCmd` contains parallel subtests that directly invoke `cidFmtCmd.Run` with synthetic `cmds.Request` option maps. It iterates over `multibase.EncodingToStr` and checks expected errors for `-v 0` plus custom bases.

## Control Flow

The first subtest creates requests with `cidToVersionOptionName: "0"` and each multibase name, expecting no error only for `base58btc`. The second subtest builds requests with no explicit version and custom base options to assert the run path accepts implicit CIDv1 upgrade cases.

## State and Persistence Behavior

The test is pure and does not construct a repo, node, or filesystem. It exercises repo-independent command behavior.

## Dependencies and Integration Points

Depends on the `go-ipfs-cmds` request type and multibase table. It is tightly coupled to option names in `cid.go` and to `cidFmtCmd.Run` validation order.

## Risks and Edge Cases

The test uses a nil response emitter in cases where it expects validation to happen before emission. That is suitable for option validation but does not prove emitted formatted strings. The second subtest checks only absence of error, not exact output.

## Test Signals

Strong signal for custom-base validation and compatibility behavior. Missing signal remains actual response content, stdin argument handling, per-CID non-fatal errors, and inspect/list subcommands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cid_test.go -->

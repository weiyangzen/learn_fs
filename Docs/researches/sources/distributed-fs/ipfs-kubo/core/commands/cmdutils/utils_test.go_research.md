<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdutils/utils_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cmdutils/utils_test.go

## Purpose

Tests shared path/CID parsing and pin-name byte-length validation.

## Important APIs, Types, and Functions

`TestPathOrCidPath` exercises `PathOrCidPath` for full IPFS paths, bare CIDs, IPNS paths, invalid inputs, empty strings, and bare CID-with-path values. `TestValidatePinName` checks `ValidatePinName`.

## Control Flow

Subtests assert exact path strings on success and inspect error messages on failure. Pin-name tests check empty, valid, max-length, too-long, and multi-byte Unicode names.

## State and Persistence Behavior

Pure unit tests.

## Dependencies and Integration Points

Uses `testify/assert` and `require`, plus the utility constants from `utils.go`.

## Risks and Edge Cases

The invalid-character test allows either original input or generic "invalid" text, which is flexible but less exact. Unicode pin-name test assumes emoji byte length.

## Test Signals

Strong signal for user-facing parse errors and byte-length enforcement. Missing coverage includes `CheckBlockSize`, `CheckCIDSize`, and `CloneAddrInfo`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdutils/utils_test.go -->

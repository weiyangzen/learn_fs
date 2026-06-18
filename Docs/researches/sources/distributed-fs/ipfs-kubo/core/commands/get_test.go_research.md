<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/get_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/get_test.go

## Purpose

Tests default and explicit local output path selection for `ipfs get`.

## Important APIs, Types, and Functions

`TestGetOutputPath` constructs command requests for `GetCmd` and calls `getOutPath`.

## Control Flow

Table cases cover explicit `--output`, trailing slashes, nested path final components, and extra ignored arguments. Each case builds a request with `cmds.NewRequest` and compares the computed path.

## State and Persistence Behavior

Pure unit test. It does not fetch or write files.

## Dependencies and Integration Points

Depends on `GetCmd` option parsing and command request construction.

## Risks and Edge Cases

The test covers path naming only, not path traversal, filesystem errors, or archive/compression suffix behavior.

## Test Signals

Good signal for user-visible default output naming. Limited signal for the main data transfer path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/get_test.go -->

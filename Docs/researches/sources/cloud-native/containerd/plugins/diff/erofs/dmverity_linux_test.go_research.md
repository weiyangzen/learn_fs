# sources/cloud-native/containerd/plugins/diff/erofs/dmverity_linux_test.go

## Purpose
Tests Linux dm-verity configuration and formatting behavior for EROFS differ layers.

## Important APIs, Types, And Functions
`TestGetDmverityOptions` checks 512-byte blocks for tar-index mode and 4096-byte blocks for regular mode. `TestFormatDmverityLayer` covers metadata creation, idempotency, regular/tar-index offsets, missing files, and non-aligned file-size rounding.

## Control Flow
The formatting test skips when dm-verity is unsupported, writes temporary layer files, calls `formatDmverityLayer`, reads sidecar metadata via `dmverity.ReadMetadata`, and asserts root hash and hash offset expectations.

## State And Persistence
Uses temporary files and real dm-verity formatting support. The tests create sidecar metadata and mutate layer files in temp directories.

## Dependencies And Integration Points
Depends on `internal/dmverity`, `logtest`, `testify`, Linux dm-verity availability, and `formatDmverityLayer`.

## Risks
The tests are environment-sensitive and skip without kernel/module support, so CI can miss formatting regressions on unsupported hosts.

## Test Signals
Strong targeted coverage for block-size selection, idempotency, metadata sidecar creation, and hash-offset alignment.

# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/handlers_test.go

## Purpose
Tests generic remotes handler helpers for ref-key prefixing and non-distributable blob filtering.

## Important APIs, Types, And Functions
`TestContextCustomKeyPrefix`, `TestSkipNonDistributableBlobs`, and `memoryLabelStore`.

## Control Flow
The ref-key test sets context prefixes for a built-in media type and a custom media type, then verifies built-in fallback, unknown fallback, override, and custom prefix behavior. The non-distributable test first filters a synthetic child list, then writes a manifest/config to a local labeled store and filters children returned by `images.ChildrenHandler`.

## State And Persistence
Uses temporary local content-store state and an in-memory label store. No persistent files beyond test temp directories.

## Dependencies And Integration Points
Targets `MakeRefKey`, `SkipNonDistributableBlobs`, containerd local content store, OCI descriptors, and image media-type classification.

## Risks And Edge Cases
The tests do not cover `PushContent` ordering or platform filtering, but they protect two commonly reused helper paths.

## Test Signals
Direct unit coverage for ref-key context customization and for filtering Windows/foreign/non-distributable layer media types while preserving config and distributable layers.

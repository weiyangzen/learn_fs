<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/handlers_test.go -->
# sources/cloud-native/containerd/core/remotes/handlers_test.go

## Purpose
Tests generic remotes handler helpers for ref-key prefix customization and non-distributable layer filtering.

## Important APIs, Types, And Functions
- `TestContextCustomKeyPrefix` validates built-in, unknown, overridden, and custom media-type prefixes in `MakeRefKey`.
- `TestSkipNonDistributableBlobs` validates descriptor filtering from a handler and from `images.ChildrenHandler` over a local content store.
- `memoryLabelStore` implements the local content store label interface for tests.

## Control Flow
The ref-key test builds contexts with prefix overrides and checks returned string prefixes. The non-distributable test first wraps a synthetic handler returning several layer media types, then creates a local labeled store, writes config and manifest content, and verifies child traversal excludes foreign/non-distributable layers while keeping config and normal layer.

## State And Persistence
Uses a temporary local content store and in-memory label store. Test artifacts are confined to `t.TempDir`.

## Dependencies And Integration Points
Exercises `content/local`, OCI manifests/configs, media-type classifiers from `images`, and the handler wrappers in `handlers.go`.

## Risks And Edge Cases
Protects compatibility for custom ingest refs and legal distribution filtering. It does not directly test `PushContent` ordering or distribution-source annotation copying.

## Test Signals
Good unit and small integration coverage for handler composition behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/handlers_test.go -->

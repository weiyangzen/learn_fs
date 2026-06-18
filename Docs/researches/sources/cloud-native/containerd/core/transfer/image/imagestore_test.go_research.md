# sources/cloud-native/containerd/core/transfer/image/imagestore_test.go

## Purpose
This file unit-tests `transfer/image.Store` reference resolution, GC labeling, and lookup behavior with an in-memory image store.

## Important APIs, Types, and Functions
`TestStore` drives a large table of reference scenarios. `TestLookup` validates direct lookup cases. `simpleImageStore` implements `images.Store` with a mutex-protected map and basic create/update/delete/get/list behavior.

## Control Flow
For each case, the test builds descriptors with containerd, OCI, generic import annotation, or no annotation. It calls `Store`, checks expected image names and digest targets, and verifies GC labels for primary versus extra references. Lookup tests prepopulate the simple store and compare sorted image names.

## State and Persistence
All persistence is in memory. The tests specifically validate labels that influence real GC persistence semantics in production stores.

## Dependencies and Integration Points
Uses `errdefs`, OCI descriptors, `go-digest`, and `core/images` annotations. It mirrors behavior relied on by archive imports and transfer local import/store paths.

## Risks
The in-memory store ignores filters and field paths, so it verifies reference logic rather than backend-specific store semantics. Time-sensitive GC expire labels are only checked for RFC3339 parsing, not exact value.

## Test Signals
Strong coverage exists for `WithNamedPrefix`, `WithDigestRef`, `SkipNamedDigest`, explicit extra references, missing references returning `ErrNotFound`, unsupported prefix export lookup returning `ErrNotImplemented`, and extra-reference GC label attachment.

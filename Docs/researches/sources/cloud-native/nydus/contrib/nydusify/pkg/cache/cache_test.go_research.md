# sources/cloud-native/nydus/contrib/nydusify/pkg/cache/cache_test.go

## Purpose
This file provides extensive unit coverage for Nydus cache record parsing, export/import behavior, bounded queue ordering, and remote interaction error handling.

## Important APIs, Types, and Functions
It defines helpers `makeRecord`, `makeBootstrapLayer`, `makeBlobLayer`, `testWithBackend`, mock content writer/fetcher/pusher/resolver types, and tests for `GetReferenceBlobs`, `layerToRecord`, `recordToLayer`, `SetReference`, `mergeRecord`, `Record`, `Export`, `Import`, `Check`, `Push`, and `PullBootstrap`.

## Control Flow
Tests create synthetic descriptors and records, compare exported layers for registry and object backends, simulate remote resolve/fetch/push through mocks, and assert expected errors for version mismatch, fs version mismatch, pull errors, push errors, and absent records.

## State, Persistence, and Dependencies
The tests use in-memory buffers and mock remotes, not real registries. Some temporary target paths are used for pull bootstrap error cases. Dependencies include containerd content/remotes, errdefs, OCI specs, digest, backend, remote, utils, and testify.

## Integration Points
These tests are the main safety net for cache manifest format compatibility and backend-specific layer encoding.

## Risks and Test Signals
Coverage is strong for pure cache logic but not for real registry auth, network retries, Docker pull compatibility, or backend object existence beyond mocks. Some tests use generated digests from strings rather than real SHA-256 encodings, which is fine for logic but less representative of production descriptors.

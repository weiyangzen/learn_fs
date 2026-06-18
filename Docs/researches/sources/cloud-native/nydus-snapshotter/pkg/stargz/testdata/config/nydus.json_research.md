# sources/cloud-native/nydus-snapshotter/pkg/stargz/testdata/config/nydus.json

## Purpose
Provides test configuration for Nydus in direct registry-backed mode with blob cache, digest validation, xattrs, IO stats, amplified IO, and filesystem prefetch settings.

## Important APIs, Types, And Functions
This is JSON data, not code. Key fields are `device.backend.type=registry`, backend timeouts/retry limit, `device.cache.type=blobcache`, `mode=direct`, `digest_validate`, `iostats_files`, `enable_xattr`, `amplify_io`, and `fs_prefetch`.

## Control Flow
Consumers load this fixture as Nydus configuration. It describes runtime behavior rather than executing logic itself.

## State And Persistence
The cache work directory is an empty string, implying tests or callers fill or default it. Other fields configure runtime IO/cache behavior.

## Dependencies And Integration Points
Used by stargz/Nydus integration tests or fixtures that need a registry backend and blob cache configuration.

## Risks And Edge Cases
`auth` and `work_dir` are blank fixture values and should not be used as production defaults without caller substitution. Retry limit is zero, so tests using it may exercise no retry behavior.

## Test Signals
Acts as fixture data; no assertions live in this file.

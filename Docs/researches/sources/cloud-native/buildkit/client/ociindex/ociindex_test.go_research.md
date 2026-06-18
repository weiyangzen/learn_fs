# sources/cloud-native/buildkit/client/ociindex/ociindex_test.go

## Purpose
This unit-test source verifies the behavior of the local OCI index helper used by BuildKit client cache and image-store export flows. It focuses on index creation, descriptor insertion, tag/name annotation behavior, lookup semantics, and replacement behavior.

## Important APIs, Types, and Functions
- `TestEmptyDir` asserts `Read` on a store without `index.json` returns `os.ErrNotExist`.
- `TestReadIndex` validates unmarshalling of an existing index.
- `TestReadByTag` checks lookup by OCI ref-name annotation.
- `TestWriteSingleDescriptor` validates `Put` followed by `GetSingle`.
- `TestAddDescriptor` verifies append behavior and default `schemaVersion`/media type population.
- `TestAddDescriptorWithTag` verifies tag annotation and lookup.
- `TestAddMultipleNames` verifies multiple descriptor entries are emitted for one input descriptor with different image names.
- `TestReplaceByImageName` verifies replacing an existing named descriptor preserves unrelated descriptors.
- `randDescriptor` creates deterministic descriptors from digest seeds.

## Control Flow
The tests create temporary directories, optionally seed `index.json`, call `NewStoreIndex`, then exercise `Read`, `Put`, `Get`, or `GetSingle`. Assertions inspect both the API return values and the raw JSON persisted in the temporary index file.

## State and Persistence Behavior
Each test uses a fresh temporary store path and writes actual `index.json` data. The tests confirm `Put` persists index defaults and descriptor annotations, not just in-memory return values. There is no shared state between cases.

## Dependencies and Integration Points
The tests depend on OCI descriptor/index types, OpenContainers digests, local filesystem IO, and testify assertions. They are direct coverage for `ociindex.go`; higher-level integration occurs through `solve.go` cache/output-store index updates.

## Risks and Edge Cases
The suite does not simulate lock contention, corrupt JSON, short writes, read-only stores, or crash consistency. It does protect the core compatibility rules: tag resolution, image-name resolution, descriptor append order, and replacement without mutating unrelated index entries.

## Test Signals
Passing tests indicate stable local OCI index semantics. Failures are likely to break local cache import/export by tag or local OCI/Docker output directories whose `index.json` must point at the latest exported descriptor.

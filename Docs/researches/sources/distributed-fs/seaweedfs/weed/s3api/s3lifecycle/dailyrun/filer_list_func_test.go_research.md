# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/filer_list_func_test.go

Purpose: comprehensive unit tests for the filer-to-bootstrap listing adapter.

Important APIs/types: `fakeFilerStream`, `fakeFiler`, helpers `file`, `dir`, `fileWithExt`, `versionsDir`, and tests around `FilerListFunc`.

Control flow: fake filer implements sorted, exclusive, limited `ListEntries` and `LookupDirectoryEntry`. Tests build in-memory directory trees and collect emitted `bootstrap.Entry` values.

State and persistence behavior: fake tree models persisted filer entries, extended metadata, version folders, and bare null versions. Tests validate how that persistent shape becomes walker entry state.

Dependencies and integration points: uses filer protobufs, S3 metadata constants, bootstrap entries, grpc stream interfaces, and testify.

Risks: the fake models only ListEntries and LookupDirectoryEntry, not all filer edge cases. Pagination behavior is represented, but this subset of displayed tests does not explicitly shrink `listPageSize`; if present elsewhere, it would cover truncation. Tests use `time.Now` in several places but do not rely on exact due calculations.

Test signals: strong regression coverage for versioned listing semantics, MPU cleanup discovery, tag extraction, resume filtering, and nil-client guard.

# sources/distributed-fs/eos/unit_tests/mgm/bulk-request/BulkRequestPrepareManagerTest.cc

## sources/distributed-fs/eos/unit_tests/mgm/bulk-request/BulkRequestPrepareManagerTest.cc

Purpose: tests `BulkRequestPrepareManager` as the bulk-aware variant of prepare handling. It checks request construction, stage/cancel/evict workflows, per-file error recording, idempotent behavior for empty or missing paths, and CTA report emission.

Important APIs and types: `BulkRequestPrepareManager`, `BulkRequestFactory`, `StageBulkRequest`, `BulkRequest`, `File`, `PrepareArgumentsWrapper`, `MockPrepareMgmFSInterface`, `ClientWrapper`, `ErrorWrapper`, XRootD prepare flags `Prep_STAGE`, `Prep_CANCEL`, and `Prep_EVICT`. It also uses `eos::common::VirtualIdentity::Root()` for request factory coverage.

Control flow: each workflow constructs prepare arguments, installs GoogleMock expectations on the mock MGM filesystem, invokes `pm.prepare(...)`, then inspects return codes and `pm.getBulkRequest()`. Stage success calls existence checks, workflow xattr lookup, access checks, `FSctl`, and EOS-CTA report methods per file. Empty-path stage returns `SFS_DATA` with a zero-file bulk request. All-missing stage still returns `SFS_DATA` and stores errors for each file. Cancel with partially missing files remains successful in the bulk manager. Evict success performs filesystem actions but does not retain a bulk request.

State and persistence: state is in-memory inside the manager-owned `BulkRequest`. The test verifies files and file errors are retained in request order. No disk persistence is used.

Dependencies and integration: integrated with common test fixtures in `PrepareManagerTest.hh` and reusable behavior lambdas from `MockPrepareMgmFSInterface`. The test codifies interaction contracts with `IMgmFileSystemInterface`, xattrs such as prepare workflow markers, and EOS report records.

Risks and test signals: it asserts precise call counts, making it sensitive to internal refactors. The most important signal is semantic divergence from plain `PrepareManager`: bulk operations should preserve idempotent, per-file status behavior and should not fail the whole request when errors can be represented in the bulk request.

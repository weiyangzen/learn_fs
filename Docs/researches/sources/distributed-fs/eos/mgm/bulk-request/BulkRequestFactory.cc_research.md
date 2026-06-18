## sources/distributed-fs/eos/mgm/bulk-request/BulkRequestFactory.cc

Purpose: implements convenience constructors for supported bulk-request types. Stage creation either generates a time-based UUID via `BulkRequestHelper` or uses a supplied request ID and optional creation time. Cancel creation wraps the supplied ID in `CancellationBulkRequest`.

Important APIs: `createStageBulkRequest(issuerVid)`, `createStageBulkRequest(requestId, issuerVid)`, `createStageBulkRequest(requestId, issuerVid, creationTime)`, and `createCancelBulkRequest(id)`.

State and dependencies: no persistent state; depends on `StageBulkRequest`, `CancellationBulkRequest`, and `BulkRequestHelper`. Integration points include `BulkRequestPrepareManager` for new stage/cancel requests and `ProcDirectoryBulkRequestDAO` for reconstructing persisted stage requests. Risks are no factory path for `EvictBulkRequest` despite the enum/class existing, and generated IDs relying on `StringConversion::timebased_uuidstring()`. Tests should validate ID propagation, creation-time preservation, issuer identity preservation, and cancel ID matching.

## sources/distributed-fs/eos/mgm/bulk-request/prepare/manager/BulkRequestPrepareManager.cc

Purpose: implements the bulk-aware subclass of `PrepareManager`. It injects domain request creation and persistence into the base prepare algorithm.

Important flow: stage initialization creates a `StageBulkRequest` with a generated ID and overwrites `reqid`; cancel initialization creates a `CancellationBulkRequest` using the incoming `reqid`; `addFileToBulkRequest()` appends validated/error files when a request exists; `saveBulkRequest()` delegates to `BulkRequestBusiness` and rethrows `PersistencyException`; `ignorePrepareFailures()` returns true so persisted bulk requests can report per-file failures without failing the whole prepare call.

State/dependencies: stores `shared_ptr<BulkRequestBusiness>` and `unique_ptr<BulkRequest>`. Risks include `getBulkRequest()` moving state out, null business silently skipping persistence, and all prepare failures ignored for this subclass. Tests should cover generated ID return, cancel ID preservation, file additions, persistence exception conversion in base class, and behavior with no business configured.

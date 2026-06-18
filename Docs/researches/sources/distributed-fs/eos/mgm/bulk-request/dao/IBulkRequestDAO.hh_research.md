## sources/distributed-fs/eos/mgm/bulk-request/dao/IBulkRequestDAO.hh

Purpose: defines the persistence contract for bulk requests. Implementations must save stage and cancellation requests, fetch by ID/type, expire inactive requests, check existence, and delete a request.

Important APIs: overloaded `saveBulkRequest()` for `CancellationBulkRequest` and `StageBulkRequest`, `getBulkRequest(id,type)`, `deleteBulkRequestNotQueriedFor(type, seconds)`, `exists(id,type)`, `deleteBulkRequest(req)`, and virtual destructor.

State/integration: no state; consumed by `BulkRequestBusiness`, `BulkRequestProcCleaner`, and DAO factories. The type-specific save overloads encode current persistence support and exclude evict saves. Risks include new request types requiring interface changes, cancellation semantics being implementation-defined, and no explicit transaction/atomicity contract. Tests should validate each implementation against empty requests, missing IDs, expiry age, and deletion idempotency.

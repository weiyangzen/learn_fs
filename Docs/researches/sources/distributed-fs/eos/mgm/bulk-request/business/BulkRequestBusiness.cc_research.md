## sources/distributed-fs/eos/mgm/bulk-request/business/BulkRequestBusiness.cc

Purpose: implements the business facade over bulk-request persistence. It logs/times operations and delegates to DAO instances produced by an injected `AbstractDAOFactory`.

Important flow: `saveBulkRequest()` switches on `req->getType()`: stage requests are cast to `StageBulkRequest`, cancellation requests to `CancellationBulkRequest`, and other types throw `PersistencyException`. `getBulkRequest()` retrieves by ID/type and logs hit/miss. `getStageBulkRequest()` retrieves `PREPARE_STAGE`, then releases and static-casts the base pointer to `StageBulkRequest`. `exists()` and `deleteBulkRequest()` pass through.

State/dependencies: owns `mDaoFactory`; each method calls `getBulkRequestDAO()`, potentially creating fresh DAO objects. Depends on logging/stat timing and `PersistencyException`. Risks include unchecked `static_cast`, unsupported evict persistence, repeated DAO construction, and exception behavior in logging paths if type strings are incomplete. Tests should mock the factory/DAO to verify dispatch, exception propagation, null retrieval, and stage downcast assumptions.

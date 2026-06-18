## sources/distributed-fs/eos/mgm/bulk-request/business/BulkRequestBusiness.hh

Purpose: declares the storage-agnostic business layer for bulk requests. It receives an `AbstractDAOFactory` and exposes save, fetch, exists, and delete operations to callers such as prepare managers or REST business code.

Important APIs: constructor taking `unique_ptr<AbstractDAOFactory>`, `saveBulkRequest(const BulkRequest*)`, `getBulkRequest(id,type)`, `getStageBulkRequest(id)`, `exists(id,type)`, and `deleteBulkRequest(req)`.

State/integration: owns the factory exclusively and returns `unique_ptr` request objects. It is the integration boundary between domain objects and DAO implementations. Risks include limited type support delegated to the `.cc`, no null request guard in the interface, and tight ownership of factory preventing copy/reuse. Tests should use a fake DAO factory to assert calls and errors without touching proc directories.

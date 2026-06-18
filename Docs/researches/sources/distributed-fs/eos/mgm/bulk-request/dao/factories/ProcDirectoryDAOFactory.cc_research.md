## sources/distributed-fs/eos/mgm/bulk-request/dao/factories/ProcDirectoryDAOFactory.cc

Purpose: implements the proc-directory DAO factory. The constructor stores an `XrdMgmOfs*` and a reference to `ProcDirectoryBulkRequestLocations`; `getBulkRequestDAO()` returns a new `ProcDirectoryBulkRequestDAO` using those dependencies.

State/dependencies: factory does not own the filesystem or locations; both must outlive the factory and produced DAO. Integration appears in cleaner setup and business-layer construction.

Risks: lifetime is by raw pointer/reference, no null checks, and every call creates a new DAO. Tests should verify construction with fake/non-null dependencies and that returned DAO paths derive from the provided locations.

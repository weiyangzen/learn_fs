## sources/distributed-fs/eos/mgm/bulk-request/dao/factories/ProcDirectoryDAOFactory.hh

Purpose: declares `ProcDirectoryDAOFactory`, the concrete `AbstractDAOFactory` for storing bulk requests in EOS proc directories.

Important API/state: constructor accepts `XrdMgmOfs* fileSystem` and `const ProcDirectoryBulkRequestLocations&`; `getBulkRequestDAO()` returns `unique_ptr<IBulkRequestDAO>`. Members are `mFileSystem` and `mBulkReqLocations`.

Integration: used wherever proc-directory persistence is selected, notably cleaner and MGM configuration paths. Risks include non-owning dependencies and no factory-level validation. Test signals should focus on dependency propagation and behavior when the proc location schema changes.

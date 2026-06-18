## sources/distributed-fs/eos/mgm/bulk-request/dao/proc/ProcDirectoryBulkRequestLocations.hh

Purpose: declares the path-schema holder used by proc DAO factories and cleaners. It centralizes where request directories live for each bulk-request type.

Important APIs/state: constructor from `procDirectoryPath`, `getAllBulkRequestDirectoriesPath()`, `getBulkRequestDirectory()`, and `getDirectoryPathWhereBulkRequestCouldBeSaved()`. Private state is `mBulkRequestTypeToPath` and `mBulkRequestDirectory`.

Integration: stored on `XrdMgmOfs` and shared with DAOs/cleaners. Risks include non-normalized paths and map lookup exceptions for future types. Test signals should assert schema stability because persisted request locations depend on these strings.

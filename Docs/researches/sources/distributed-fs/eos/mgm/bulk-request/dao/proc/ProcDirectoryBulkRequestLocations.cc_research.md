## sources/distributed-fs/eos/mgm/bulk-request/dao/proc/ProcDirectoryBulkRequestLocations.cc

Purpose: builds and serves the proc-directory path schema for bulk-request persistence. Given a base proc path, it derives `<base>/bulkrequests/`, `stage/`, and `evict/` subdirectories; cancel requests map to the stage directory because cancellation mutates stage requests.

Important APIs: constructor, `getAllBulkRequestDirectoriesPath()`, `getBulkRequestDirectory()`, and `getDirectoryPathWhereBulkRequestCouldBeSaved(type)`.

State/dependencies: stores a map from `BulkRequest::Type` to path plus root bulk-request directory. Risks include string concatenation assumptions about base paths, `at(type)` throwing for unsupported enum values, and duplicate stage/cancel paths being collapsed by `set` output. Tests should verify exact path generation, cancel-to-stage mapping, and behavior for all enum types.

## sources/distributed-fs/eos/mgm/bulk-request/exception/PersistencyException.hh

Purpose: declares the exception used for persistence failures in bulk-request business and DAO layers. It derives from `common::Exception`, preserving EOS error-info integration.

Important API: constructor from string forwards to `common::Exception`. This allows callers such as `PrepareManager` to call `fillXrdErrInfo(error, EIO)`.

Integration: thrown by `BulkRequestBusiness` and `ProcDirectoryBulkRequestDAO`, caught by prepare manager and cleaner. Risks include broad use for both user errors and infrastructure errors; tests should assert message propagation and XRootD error conversion through `common::Exception`.

## sources/distributed-fs/eos/mgm/bulk-request/dao/proc/ProcDirBulkRequestFile.hh

Purpose: declares a lightweight wrapper for file entries persisted in proc-directory xattrs. It abstracts whether an entry names a real file by file ID or a missing file by encoded path.

Important APIs: `setFileId()`, `getFileId()`, `setError()`, `getError()`, `setName()`, `getName()`, `operator<`, and `operator==`.

Integration: private helper type for `ProcDirectoryBulkRequestDAO`; depends on `common::FileId` and `std::optional`. Risks include optional file ID access requiring callers to check/value only after successful parse, and comparison not including file ID/error. Tests should verify optional state and ordering before using it in async future maps.

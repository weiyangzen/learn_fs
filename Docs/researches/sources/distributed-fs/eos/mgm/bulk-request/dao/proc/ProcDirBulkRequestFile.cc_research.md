## sources/distributed-fs/eos/mgm/bulk-request/dao/proc/ProcDirBulkRequestFile.cc

Purpose: implements the proc-persistence representation of a bulk-request file. It stores the persisted xattr suffix/name, optional file ID, and optional error text.

Important APIs: constructor from name, setters/getters for file ID, error, and name, plus comparison/equality by name. `operator<` enables use as a key in maps of metadata futures.

State/integration: used by `ProcDirectoryBulkRequestDAO::fillBulkRequestFromXattrs()` to distinguish numeric file IDs from encoded missing-file paths, carry error text, and resolve metadata asynchronously. Risks include name-only equality ignoring file ID and error, and `setError()` accepting empty strings. Tests should cover numeric and encoded names, map ordering, and error propagation into reconstructed `File` objects.

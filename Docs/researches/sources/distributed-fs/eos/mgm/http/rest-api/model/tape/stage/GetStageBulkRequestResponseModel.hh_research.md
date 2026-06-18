## sources/distributed-fs/eos/mgm/http/rest-api/model/tape/stage/GetStageBulkRequestResponseModel.hh

Purpose: holds the status response for a previously submitted stage bulk request.

Important APIs/types/functions: nested `File` contains `mPath`, `mError`, and `mOnDisk`; model has `addFile`, `getFiles`, `getCreationTime`, `getId`, `setCreationTime`, and `setId`.

Control flow: `TapeRestApiBusiness::getStageBulkRequest` fills request metadata and one `File` entry per query response matching persisted request files.

State and persistence: in-memory response only; it reflects persisted bulk request plus live query-prepare state at response time.

Dependencies and integration points: jsonified by `GetStageBulkRequestJsonifier`; uses bulk request/query response types.

Risks and test signals: `mCreationTime` and `mOnDisk` are uninitialized until explicitly set. Tests should verify no default model is serialized and that query responses for unknown files are ignored.

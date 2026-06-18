## sources/distributed-fs/eos/mgm/bulk-request/BulkRequest.hh

Purpose: declares the abstract bulk-request domain object. `BulkRequest` holds a unique request ID and a `FileCollection` of paths/errors; subclasses implement `getType()`.

Important APIs/types: `enum Type { PREPARE_STAGE, PREPARE_EVICT, PREPARE_CANCEL }`, `getId()`, pure virtual `getType()`, `getFiles()`, `getFilesMap()`, virtual `addFile(unique_ptr<File>&&)`, `bulkRequestTypeToString()`, and `getAllFilesInError()`. It exposes collection snapshots as shared pointers to containers of raw `File*` or the underlying multimap.

State and integration: owns `mId` and `mFileCollection`; used by factories, prepare manager, business layer, and DAO implementations. Risks include shallow-copy behavior inherited from `FileCollection`, raw pointers in returned vectors that depend on collection lifetime, and `bulkRequestTypeToString()` throwing if the enum map is incomplete. Test signals should verify insertion order, duplicate path handling, file-error filtering, subclass type dispatch, and lifetime assumptions around `getFiles()`.

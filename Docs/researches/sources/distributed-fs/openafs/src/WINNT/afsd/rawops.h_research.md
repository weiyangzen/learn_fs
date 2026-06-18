# sources/distributed-fs/openafs/src/WINNT/afsd/rawops.h

Purpose: declares the raw scache read/write entry points implemented by `rawops.c`.

Important APIs/types/functions: `raw_ReadData(cm_scache_t *scp, osi_hyper_t *offsetp, afs_uint32 length, char *bufferp, afs_uint32 *readp, cm_user_t *userp, cm_req_t *reqp)` and `raw_WriteData(cm_scache_t *scp, osi_hyper_t *offsetp, afs_uint32 length, char *bufferp, cm_user_t *userp, cm_req_t *reqp, afs_uint32 *writtenp)`.

Control flow: callers pass an scache, mutable offset, byte count, caller buffer, user, and request context. The implementation advances the offset and reports bytes transferred.

State/persistence: no state in the header. The contract implies the implementation mutates scache/cache state and requires lock discipline, but the header does not document that requirement.

Dependencies/integration: relies on OpenAFS cache-manager types being declared before inclusion. Used by low-level raw file I/O code.

Risks: missing include guards and missing lock/ownership comments can lead to duplicate declarations or misuse. Return type differs between read (`afs_int32`) and write (`afs_uint32`) despite both returning error codes.

Test signals: compile all includers, verify prototypes match implementation, and add caller-side tests that enforce write-lock preconditions.

# sources/distributed-fs/openafs/src/WINNT/afsd/rawops.c

Purpose: implements raw cache-manager read and write operations over `cm_scache_t` objects, copying data between caller buffers and OpenAFS cache buffers while coordinating callbacks, buffer fetches, dirty marking, and asynchronous store-back.

Important APIs/types/functions: `raw_ReadData` reads from an scache at an `osi_hyper_t` offset into a caller buffer and returns the number of bytes read. `raw_WriteData` writes caller data into cache buffers, extends file length when necessary, marks dirty ranges, and queues `cm_BkgStore` work. Both are documented as requiring the scache write lock on entry.

Control flow: read first synchronizes callback/status, clamps requested length to EOF, then loops block-by-block. For each cache block, it releases the scache write lock around `buf_Get`, reacquires it, synchronizes for read, fetches missing cache data with `cm_GetBuffer`, copies bytes, advances the offset, and releases the final buffer. Write synchronizes for callback/status/setstatus, updates `scp->length` and mask if extending EOF, loops over buffers, obtains and locks each buffer, skips server fetch when overwriting full or past-EOF data, writes bytes into `bufp->datap`, marks dirty ranges, and on success queues an async background store for the written range.

State/persistence: modifies in-memory scache length/mask and cache buffer data/dirty metadata. Actual persistence to AFS servers is delegated to background store. It holds/releases scache and buffer locks according to cache-manager conventions.

Dependencies/integration: depends on `cm_SyncOp`, `cm_SyncOpDone`, `buf_Get`, `buf_Release`, `cm_HaveBuffer`, `cm_GetBuffer`, `buf_SetDirty`, `cm_QueueBKGRequest`, `cm_BkgStore`, `rock_BkgStore_t`, `cm_data.blockSize`, and large-integer helpers. Integrated into raw SMB/redirector file I/O paths.

Risks: callers must hold the scache write lock exactly as expected; misuse can deadlock or corrupt buffers. `raw_ReadData` defines `sequential` but never sets it, so prefetch is never considered. Write returns without calling `cm_SyncOpDone` for `CM_SCACHESYNC_ASYNCSTORE`; the comment relies on `cm_BkgStore` completion, so failed queueing/sync paths need careful audit. Background-store allocation failure silently leaves dirty data for later normal flushing but does not surface pressure. Partial writes before an error leave `writtenp` updated and dirty buffers present.

Test signals: read at EOF/past EOF, multi-block reads/writes, writes extending file length, full-block overwrite avoiding fetch, partial past-EOF zeroing, simulated `buf_Get`/`cm_GetBuffer` failures, async store queue failure, lock-order stress, and dirty range correctness.

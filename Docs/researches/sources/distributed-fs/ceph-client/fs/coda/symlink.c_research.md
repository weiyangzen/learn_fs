# sources/distributed-fs/ceph-client/fs/coda/symlink.c

Purpose: implements Coda symlink page-cache population. Symlink contents live in Venus, and this file supplies the address-space operation that fetches them on demand.

Important APIs/functions: `coda_symlink_filler()` is the `.read_folio` callback for `coda_symlink_aops`. It obtains the inode from `folio->mapping->host`, extracts the `CodaFid` via `ITOC()`, uses a page-sized buffer at `folio_address(folio)`, and calls `venus_readlink()`.

Control flow: VFS follows or reads a symlink, the page-cache symlink machinery asks for a folio, `coda_symlink_filler()` sends a `CODA_READLINK` upcall, Venus copies the symlink target into the page, and `folio_end_read()` marks the folio success or failure.

State and persistence: no local persistent state. The folio becomes cached symlink data until invalidated by normal inode/cache behavior or Coda downcalls.

Dependencies/integration: depends on page-cache symlink support, Coda inode-private fids, and `venus_readlink()` in `upcall.c`. It is selected by inode construction for symlink cnodes elsewhere in the Coda client.

Risks: the buffer length is initialized to `PAGE_SIZE`; Venus results are truncated to leave a NUL terminator in `venus_readlink()`. Errors must call `folio_end_read()` with failure or consumers can observe stale/incomplete data. Cache invalidation from Venus must cover symlink target changes.

Test signals: readlink on valid symlinks, target length near `PAGE_SIZE`, Venus error propagation, folio uptodate state after failure, and cache invalidation after symlink update.

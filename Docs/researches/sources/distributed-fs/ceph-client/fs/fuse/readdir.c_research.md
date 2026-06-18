# sources/distributed-fs/ceph-client/fs/fuse/readdir.c

## Purpose
Implements FUSE directory iteration with optional READDIRPLUS lookup/linking and an inode page-cache-backed directory-entry cache for `FOPEN_CACHE_DIR`.

## Important APIs, Types, And Functions
`fuse_readdir()` selects cached or uncached paths. `fuse_readdir_uncached()` sends `FUSE_READDIR` or `FUSE_READDIRPLUS` and parses returned buffers. `fuse_use_readdirplus()` decides plus mode from connection flags, auto mode, and inode advisory bits. `parse_dirfile()` validates and emits plain dirents. `parse_dirplusfile()` emits entries and links returned attributes into the dcache/inode cache. `fuse_direntplus_link()` handles inode lookup, alias splicing, attr refresh, ACL invalidation, lookup refcounts, and entry timeouts. `fuse_readdir_cached()`, `fuse_add_dirent_to_cache()`, `fuse_readdir_cache_end()`, `fuse_parse_cache()`, and `fuse_rdc_reset()` maintain the page-backed readdir cache.

## Control Flow
Uncached reads allocate a bounded buffer, choose plus or plain opcode, lock the inode around the request, parse replies, mark cache complete on EOF, and invalidate atime. Plus parsing continues linking entries even after the caller buffer is full to avoid leaking lookup counts; failed links trigger forced `FORGET`. Cached reads verify seek position, refresh mtime at directory start when auto invalidation is enabled, validate cache version/mtime/iversion, map cached pages, parse dirents, and fall back to uncached if the requested position is not represented.

## State And Persistence
`fi->rdc` stores directory-cache lock, `cached` completion flag, version, size, stream position, mtime, and inode version. `ff->readdir` stores each open file's cache offset, directory position, and observed cache version. READDIRPLUS mutates dcache/inode state, `nlookup`, entry timeout, attr versioning, and ACL cache.

## Dependencies And Integration Points
Depends on FUSE read request builders, inode attr/version helpers, dcache APIs, ACL cache invalidation, page-cache APIs, and FUSE forget semantics. Integrates with directory file operations and lookup coherency.

## Risks
Directory entry parsing is corruption-sensitive: invalid lengths, slash-containing names, zero names, and oversized names return `EIO`. READDIRPLUS lookup reference accounting must send `FORGET` on failed linkage. Cache invalidation relies on mtime and i_version; stale or racing cache pages reset the cache. Auto READDIRPLUS policy changes latency and lookup behavior.

## Test Signals
Cover plain readdir, readdirplus, auto-plus first read and advisory bit behavior, invalid dirent buffers, cache fill/EOF, seek and rewind, mtime/i_version invalidation, dcache alias replacement, forced forget on link failure, and caller buffer overflow behavior.

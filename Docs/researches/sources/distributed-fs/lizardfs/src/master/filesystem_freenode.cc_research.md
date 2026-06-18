# sources/distributed-fs/lizardfs/src/master/filesystem_freenode.cc

## Purpose
`filesystem_freenode.cc` allocates inode numbers from `gMetadata->inode_pool` and preserves compatibility with old changelog free-inode entries.

## Important APIs and control flow
`fsnodes_get_next_id(uint32_t ts, uint32_t req_inode)` first attempts to mark a requested inode as acquired when a nonzero requested id is supplied. If no request is provided or the requested id is unavailable, it acquires the next free id from the pool. A zero result aborts the process with `mabort("Out of free inode numbers")`. Successful allocation updates `gMetadata->maxnodeid` if the id is the largest seen. `fs_apply_freeinodes` ignores old free-inode changelog payloads and increments `metaversion` for compatibility.

## State and persistence behavior
Allocation mutates the inode pool and the max inode counter. Inode release happens elsewhere during node removal. Requested inode handling is important during changelog replay because shadow/metarestore must recreate specific ids.

## Dependencies and integration points
The code depends on `FilesystemMetadata`, `IdPoolDetainer`, checksum updater includes, and filesystem operation status conventions. `fsnodes_create_node` is the main caller.

## Risks and test signals
The fatal behavior on exhausted inode pool is intentional but high impact. Tests should cover requested id success, requested id collision fallback, monotonic `maxnodeid`, release-and-reacquire delay semantics through the pool, replay creation with exact inode ids, and compatibility replay of old `FREEINODES` entries.

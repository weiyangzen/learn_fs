# sources/distributed-fs/ceph-client/fs/coda/coda_fs_i.h

## Purpose
`coda_fs_i.h` defines Coda per-inode and per-file private structures and declares inode/fid helper functions.

## Important APIs, Types, And Functions
It defines `struct coda_inode_info` with fid, flags, mmap count, permission-cache fields, lock, and embedded VFS inode. It defines `struct coda_file_info` with magic, container file, mmap count, and access-intent support. It declares `coda_cnode_make()`, `coda_iget()`, `coda_cnode_makectl()`, `coda_fid_to_inode()`, `coda_ftoc()`, and `coda_replace_fid()`.

## Control Flow
The header is declarative. Runtime code allocates Coda inodes from the inode cache, uses `c_fid` as identity, stores container-file state in `file->private_data`, and tracks flags such as `C_VATTR`, `C_FLUSH`, `C_DYING`, and `C_PURGE`.

## State, Persistence, And Dependencies
State is volatile kernel-side representation of Venus/server identities and open files. It depends on Linux inode/list/spinlock types and UAPI Coda fid/attribute definitions.

## Integration Points
`cnode.c`, `file.c`, `dir.c`, inode cache code, and psdev/upcall paths all rely on these structures to bridge VFS objects to Coda identities and Venus-opened container files.

## Risks
The comment says `c_fid` should be immutable, with only special replacement support elsewhere. Lock coverage for `c_flags`, `c_mapcount`, and permission fields must be preserved to avoid stale cache or mmap mapping races.

## Test Signals
Compile layout users, exercise file open/release/mmap, permission caching, invalidation flags, fid lookup/replacement, and KASAN checks for `coda_file_info` lifetime.

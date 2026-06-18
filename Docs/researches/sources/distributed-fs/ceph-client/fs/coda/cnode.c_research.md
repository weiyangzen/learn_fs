# sources/distributed-fs/ceph-client/fs/coda/cnode.c

## Purpose
`cnode.c` maps Coda file identifiers to VFS inodes, fills inode operations based on Venus attributes, handles special control inode creation, and supports fid replacement for disconnected-create collision repair.

## Important APIs, Types, And Functions
Important functions are `coda_iget()`, `coda_cnode_make()`, `coda_replace_fid()`, `coda_fid_to_inode()`, `coda_ftoc()`, and `coda_cnode_makectl()`. Internal helpers include `coda_fideq()`, `coda_fill_inode()`, `coda_test_inode()`, and `coda_set_inode()`.

## Control Flow
`coda_cnode_make()` asks Venus for attributes, then calls `coda_iget()` using `iget5_locked()` keyed by `coda_f2i(fid)`. New inodes get `i_ino`, cnode state, and mode-specific inode/file operations. Existing inodes with changed type are removed from the hash, flagged for purge, dropped, and retried. The control inode is created locally without Venus attributes.

## State, Persistence, And Dependencies
Per-inode Coda state is `struct coda_inode_info`, especially immutable `c_fid`, flags, mapcount, and permission cache fields. Persistent identity belongs to Venus/Coda servers. Dependencies include VFS inode hash APIs, page symlink ops, Coda attribute conversion, and Venus getattr.

## Integration Points
Directory lookup/create paths call into this file to materialize inodes. File operations use `coda_ftoc()` to validate private data. Pioctl/control operations use the synthetic control inode.

## Risks
`coda_replace_fid()` explicitly notes missing locking around rehashing. Fid hash collisions, type changes, disconnected local fid replacement, and stale inode flags are core risk areas.

## Test Signals
Test lookup/create for regular files, directories, symlinks, special files, type-change replacement, fid-to-inode lookup, control inode lookup, disconnected fid replacement, and inode hash race detection.

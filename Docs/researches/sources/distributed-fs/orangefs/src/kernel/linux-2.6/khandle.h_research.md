# sources/distributed-fs/orangefs/src/kernel/linux-2.6/khandle.h

Purpose: Declares and implements small helpers for comparing, copying, formatting, and hashing OrangeFS/PVFS kernel handles used as VFS inode identifiers and debug values.

Important APIs and functions: Declares `k2s(PVFS_khandle *, char *)` and `HANDLESTRINGSIZE`. `PVFS_khandle_cmp` lexicographically compares 16 handle bytes from high index to low. `PVFS_khandle_to` copies a handle into an arbitrary-size destination buffer after zeroing it. `PVFS_khandle_from` copies an arbitrary-size source buffer into a zeroed 16-byte `PVFS_khandle`. `pvfs2_khandle_to_ino` maps a 16-byte handle to an `ino_t` by combining bytes 0-3 and 12-15 through `struct ihash`.

Control flow: All helper logic is local and synchronous. Copy helpers zero the target and copy up to the smaller of 16 bytes and the supplied size. The inode-hash helper deliberately discards the middle eight bytes, matching the comment that the kernel module always uses first four and last four bytes as the scalar inode number.

State and persistence: No persistent state. The helpers influence persistent-looking VFS behavior because the generated inode number/hash is exposed through stat output and used as the hash key for inode-cache lookup before full handle comparison.

Dependencies and integration points: Depends on `PVFS_khandle`, `struct ihash`, `ino_t`, and C library/kernel primitives such as `memset`. Used by inode-cache code in `inode.c`, directory entry inode-number generation in `dir.c`, name lookup fallback paths in `namei.c`, and debug logging via `k2s`.

Risks: The comparison comment says it assumes little endian, and the inode hash intentionally collapses 128-bit handles to 64 bits, so collisions are possible and must be resolved by full handle+fsid checks where available. Some legacy fallback code elsewhere calls `pvfs2_khandle_to_ino` as if it accepted a value rather than a pointer, indicating stale compatibility branches. `PVFS_khandle_to/from` accept arbitrary sizes and raw `void *` pointers without NULL validation. Exposing the hash as `i_ino` can confuse tools if many 128-bit handles share first/last bytes.

Test signals: Test compare ordering, equality, copy-to/from with sizes 0, 8, 16, and larger than 16, inode-hash stability across 64-bit and 128-bit handles, and collision handling in `iget5_locked`/`iget4_locked` paths. Compile all legacy fallback branches that call the helper to catch signature drift.

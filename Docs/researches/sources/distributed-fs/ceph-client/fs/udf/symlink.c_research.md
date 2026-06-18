# sources/distributed-fs/ceph-client/fs/udf/symlink.c

## Purpose
`symlink.c` decodes UDF symbolic-link path component records into normal path strings for VFS readlink and attributes. It provides symlink address-space and inode operations.

## Important APIs, types, and functions
The exported tables are `udf_symlink_aops` and `udf_symlink_inode_operations`. Internal helpers are `udf_pc_to_char`, `udf_symlink_filler`, and `udf_symlink_getattr`. It consumes `struct pathComponent` streams and `udf_get_filename`.

## Control flow
Readlink goes through `page_get_link`, which triggers `udf_symlink_filler`. The filler rejects encoded symlinks longer than one block, chooses inline `i_data + i_lenEAttr` or reads block zero via `udf_bread`, decodes components into the folio, and completes the folio read. Component decoding maps root/absolute markers, parent, current directory, and named components, appending `/` separators and converting CS0 names through `udf_get_filename`. `getattr` reads the decoded first folio and reports decoded string length as `st_size`, not the encoded byte count.

## State and persistence
The file does not mutate disk. It interprets persisted symlink payloads stored either in the file entry or external data blocks and exposes decoded runtime folio contents.

## Dependencies and integration points
It depends on UDF inode allocation type, `udf_bread`, filename conversion, pagecache folio helpers, VFS symlink helpers, and `inode_nohighmem` setup from creation/read paths.

## Risks and test signals
Risks include malformed component lengths overrunning the encoded payload, decoded path truncation, root component semantics, pagecache errors affecting `getattr`, and mismatch between encoded `i_size` and decoded size. Test signals include inline and block-backed symlinks, absolute paths, repeated slashes, `.` and `..`, long component names, malformed component lengths, and `lstat` size consistency with `readlink`.

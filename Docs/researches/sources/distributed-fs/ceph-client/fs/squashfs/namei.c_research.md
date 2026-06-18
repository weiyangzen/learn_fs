# sources/distributed-fs/ceph-client/fs/squashfs/namei.c

## Purpose

`namei.c` implements filename lookup in SquashFS directories. It uses sorted directory metadata and optional directory indexes to locate a named child and instantiate its inode.

## Important APIs, Types, and Functions

The exported object is `squashfs_dir_inode_ops`. Internal functions are `get_dir_index_using_name()` and `squashfs_lookup()`. It uses `struct squashfs_dir_index`, `struct squashfs_dir_header`, `struct squashfs_dir_entry`, and `squashfs_iget()`.

## Control Flow

Lookup validates name length, uses the directory index to jump near the name, then scans directory headers and entries. Because entries are sorted, if the first character has advanced beyond the target name it exits early. On exact length/name match it constructs the packed inode value from header start block and entry offset, computes the visible inode number, and calls `squashfs_iget()`.

## State and Persistence Behavior

No directory state is mutated. Negative or positive dentries are returned through `d_splice_alias()`. Directory index metadata remains read-only.

## Dependencies and Integration Points

`inode.c` assigns these operations to directory inodes. It depends on metadata reading, directory private inode fields, xattr list support, and VFS dcache lookup semantics.

## Risks and Edge Cases

Oversized names return `-ENAMETOOLONG`. Corrupt directory counts/sizes produce `-EIO`. The early exit assumes sorted directory order. Index read errors degrade to partial index use rather than immediate failure.

## Test Signals

Lookup existing/missing names in small and large indexed directories, names near `SQUASHFS_NAME_LEN`, corrupt directory metadata, and dcache alias cases.

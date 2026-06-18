# sources/distributed-fs/ceph-client/fs/squashfs/fragment.c

## Purpose

`fragment.c` handles SquashFS fragments, which are tail-end file data packed into shared compressed blocks. It maps fragment numbers from inodes to on-disk block addresses and compressed sizes.

## Important APIs, Types, and Functions

Public functions are `squashfs_frag_lookup()` and `squashfs_read_fragment_index_table()`. It uses `struct squashfs_fragment_entry` and fragment table macros from `squashfs_fs.h`.

## Control Flow

At mount, `squashfs_read_fragment_index_table()` validates and reads the uncompressed fragment index table. At inode load time, `squashfs_frag_lookup()` validates the fragment number, finds the metadata block through `msblk->fragment_index`, reads the fragment entry, returns its start block through an output parameter, and returns the decoded compressed size.

## State and Persistence Behavior

The fragment index is persisted in memory as `msblk->fragment_index`; fragment data itself is read on demand through the fragment cache.

## Dependencies and Integration Points

Used by `inode.c` when regular inodes reference fragments and by `file.c` when reading fragment-backed tail pages. It depends on metadata reading and table read helpers.

## Risks and Edge Cases

Invalid fragment numbers and corrupt fragment sizes must fail reads or mount. Table validation only checks index bounds/order; individual entries are validated when used.

## Test Signals

Small-file and tail-fragment reads, images with no fragments, maximum fragment counts, and corrupt fragment table or entry sizes.

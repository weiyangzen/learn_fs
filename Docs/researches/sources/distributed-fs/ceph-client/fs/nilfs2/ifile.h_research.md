# sources/distributed-fs/ceph-client/fs/nilfs2/ifile.h

## Purpose
`ifile.h` declares inode-file operations and provides inline helpers to map/unmap raw inode entries inside ifile metadata buffers.

## Important APIs
- `nilfs_ifile_map_inode()` computes the palloc entry offset for an inode number and maps that location in the containing folio.
- `nilfs_ifile_unmap_inode()` releases the local kmap.
- `nilfs_ifile_create_inode()`, `nilfs_ifile_delete_inode()`, `nilfs_ifile_get_inode_block()`, `nilfs_ifile_count_free_inodes()`, and `nilfs_ifile_read()` expose the ifile implementation.

## Control flow and state behavior
The inline map helper assumes the caller already holds a valid buffer head for the inode entry. It returns a direct pointer to the raw `struct nilfs_inode` record; callers must unmap promptly after reading or writing. The declared functions manage palloc-backed inode entry lifecycle and checkpoint-root loading.

## Dependencies and integration points
The header includes `mdt.h` and `alloc.h`, so users share metadata-file and persistent-allocator conventions. It is used by inode read/write paths, cpfile checkpoint import, and ifile implementation.

## Risks and test signals
Incorrect buffer/inode pairing can map the wrong raw inode. Tests should cover map/unmap under highmem/local-kmap conditions, invalid inode numbers, and raw inode update persistence through checkpoint finalization.

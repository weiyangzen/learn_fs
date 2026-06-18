# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/ifile.h

Public inode-file interface. It provides inline helpers to map and unmap raw `struct nilfs_inode` records inside ifile entry buffers, plus declarations for inode create/delete/get, free inode counting, and ifile read/init.

The map helper uses `nilfs_palloc_entry_offset` and `kmap_local_folio`; callers must unmap with `nilfs_ifile_unmap_inode`.

Integration: used by inode lifecycle code, checkpoint/root loading, and any code that needs direct access to raw on-disk inode records.

Risk/notes: mapped raw inode pointers are local kmap addresses and must not outlive the calling context.

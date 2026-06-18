<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/file.c -->
# sources/distributed-fs/ceph-client/fs/vboxsf/file.c

Purpose: Implements vboxsf regular file operations, address-space operations, mmap behavior, host handle lifetime, pagecache read/writeback, and symlink target reads.

Important APIs, types, and functions: Defines `struct vboxsf_handle`, `vboxsf_create_sf_handle()`, `vboxsf_release_sf_handle()`, `vboxsf_reg_fops`, `vboxsf_reg_iops`, `vboxsf_reg_aops`, and `vboxsf_lnk_iops`. Internal paths include `vboxsf_file_open()`, `vboxsf_file_release()`, `vboxsf_file_mmap_prepare()`, `vboxsf_read_folio()`, `vboxsf_get_write_handle()`, `vboxsf_writepages()`, `vboxsf_write_end()`, and `vboxsf_get_link()`.

Control flow: Open maps Linux open flags to `SHFL_CF_*` create and access flags, calls host create/open, wraps the returned handle, and attaches it to `file->private_data`. Handles are refcounted and also listed per inode so writeback can find a writable host handle independent of the initiating file. Reads fill folios through `vboxsf_read()`, zero the tail, and mark completion. Writes go through generic buffered write paths, with `write_end()` immediately writing copied bytes to the host and writeback flushing dirty folios through an available writable handle. mmap installs filemap fault operations and flushes writes on VMA close.

State and persistence: Persistent data lives on the host filesystem. Guest state includes open host handles, the inode handle list, pagecache contents, and `force_restat` markers after writes or opens. Cache coherency is intentionally limited: host-side changes are detected primarily on open/revalidation by mtime comparison.

Dependencies and integration points: Depends on VFS generic file helpers, pagecache/folio APIs, writeback, mmap, krefs, and vboxsf host wrappers. Symlink reads use path conversion and `SHFL_FN_READLINK`.

Risks and test signals: Risks include host handle leaks, writeback without a writable handle, stale cached data after host-side writes, short host reads/writes, page tail zeroing mistakes, mmap write visibility, and symlink buffer truncation. Test read/write/truncate/append modes, buffered writeback after closing writers, mmap dirty close, host-side modification before and after open, unlink while open, and symlink target reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/file.c -->

# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsFile.h

**Purpose:** Declares the public VFS file/directory/address-space operation tables and function entry points implemented in `FhgfsOpsFile.c`, plus small inline accessors for `file->private_data`, lock-owner identity, and page-versus-folio write_begin compatibility.

**Important APIs/types/functions:** Exports operation tables for buffered/pagecache file ops, directory ops, and buffered/pagecache address-space ops. Declares llseek, open/release, directory open/read/release, fsync, flush helper, flock/range lock, readlink, read/write iterators, mmap, direct I/O, close-time lock cancellation, and sparse-read helper. Inline helpers cast `file->private_data` to `FsObjectInfo`, `FsDirInfo`, or `FsFileInfo`; set those pointers; return current lock PID as `current->tgid`; return virtual lock FD as the `struct file*` address; and adapt `struct page*` to `beegfs_pgfol_t` for folio-aware kernels.

**Control flow:** Other modules include this header to invoke shared file-operation helpers or install operation tables. `__FhgfsOps_getObjectInfo` is used when code needs to distinguish file and directory private data polymorphically. The folio/page helpers are used by write_begin/write_end implementations so the same source can compile across kernels that expect either `struct page*` or `struct folio*`, and across kernels whose `grab_cache_page_write_begin` accepts flags or not.

**State and persistence behavior:** The header itself owns no durable state. Its private-data helpers define how per-open `FsFileInfo` and `FsDirInfo` are stored in Linux `struct file`. Lock identity helpers define the remote owner identifiers used for BeeGFS entry/range locks.

**Dependencies and integration points:** Depends on BeeGFS app/config/threading/remoting, `FsDirInfo`, `FsFileInfo`, `FhgfsOps_versions`, `FhgfsOpsInode`, and Linux fs/vfs/pagemap/uio APIs. It is included by native file ops, export code, inode helpers, and compatibility wrappers.

**Risks:** `file->private_data` is untyped, so using a file helper on a directory or vice versa can corrupt assumptions. Remote lock FD uses pointer identity rather than user-space fd by design; that must match server-side unlock expectations. Kernel compatibility macros must be accurate for folio and write_begin signatures or builds will fail.

**Test signals:** Compile across old/new kernels, verify file and directory private-data setup/destruction, exercise lock cleanup using TGID and file pointer identities, and test page/folio write_begin wrappers on kernels with and without flags.

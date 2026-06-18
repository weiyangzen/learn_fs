# sources/distributed-fs/ceph-client/fs/readdir.c

Purpose: Implements VFS directory iteration and the `old_readdir`, `getdents`, and `getdents64` syscall ABIs, including compat variants.

Important APIs, types, and functions: Exports `wrap_directory_iterator()` and `iterate_dir()`. Defines directory entry callback state for old, getdents, getdents64, and compat ABIs plus fill functions `fillonedir()`, `filldir()`, `filldir64()`, `compat_fillonedir()`, and `compat_filldir()`.

Control flow: `iterate_dir()` checks `iterate_shared`, read permissions, fsnotify permission, takes shared inode lock, copies `file->f_pos` into `ctx->pos`, calls the filesystem iterator, writes back the new position, and records access. Legacy filesystem iterators can call `wrap_directory_iterator()` to downgrade from shared to exclusive locking. Fill callbacks validate names, compute ABI record lengths, check inode-number overflow, copy entries to user memory with unsafe user-access blocks, defer final `d_off` update until the next entry or syscall completion, and return false on full buffers or errors.

State and persistence: Mutates directory file position and user-provided dirent buffers. No directory contents are persisted here; filesystem iterators provide entries.

Dependencies and integration points: Depends on filesystem `iterate_shared`, VFS inode locks, security and fsnotify hooks, `dir_context`, user-copy primitives, compat ABI structures, and dirent layout definitions.

Risks and test signals: Risks include user-buffer overflow, wrong record alignment, inode-number overflow on 32-bit ABIs, corrupted names with slash or invalid length, signal interruption behavior, and stale position updates. Test small buffers, exact-fit buffers, invalid names from test filesystems, 64-bit inode values on 32-bit getdents, compat syscalls, concurrent directory mutation, and legacy wrapper locking.

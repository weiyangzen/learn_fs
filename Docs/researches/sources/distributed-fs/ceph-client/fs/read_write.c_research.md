# sources/distributed-fs/ceph-client/fs/read_write.c

Purpose: Implements core VFS read, write, seek, vector I/O, sendfile, copy-file-range, and generic write/copy validation helpers used by syscalls and in-kernel callers.

Important APIs, types, and functions: Exports `generic_ro_fops`, `vfs_setpos()`, `generic_file_llseek_size()`, `generic_llseek_cookie()`, `generic_file_llseek()`, fixed/noop/default llseek helpers, `vfs_llseek()`, `rw_verify_area()`, `kernel_read()`, `__kernel_write()`, `kernel_write()`, `vfs_iocb_iter_read()`, `vfs_iter_read()`, `vfs_iocb_iter_write()`, `vfs_iter_write()`, `vfs_copy_file_range()`, `generic_write_check_limits()`, `generic_write_checks_count()`, `generic_write_checks()`, `generic_file_rw_checks()`, and `generic_atomic_write_valid()`. Syscalls include read/write, pread/pwrite, readv/writev, preadv/pwritev variants, sendfile, copy_file_range, lseek, and llseek.

Control flow: Descriptor syscalls acquire fd references, snapshot or pass file positions, validate modes and user buffers, call `rw_verify_area()` for offset, LSM, and fsnotify permission checks, then dispatch to legacy `read`/`write` or iter operations. Iter-vector paths import iovecs and either call `read_iter`/`write_iter` or loop over legacy operations. Write paths bracket filesystem mutation with write-start/end helpers. `sendfile` and `copy_file_range` validate both files, clamp counts, prefer filesystem copy/remap support, and fall back to splice where allowed.

State and persistence: Mutates `file->f_pos`, file contents through filesystem operations, per-task I/O accounting counters, fsnotify state, and writeback/freeze state via write-start helpers. It stores no long-lived private state.

Dependencies and integration points: Central integration layer for syscall ABI, fd management, file operations, security hooks, fsnotify, splice, page cache, mount/freeze write protection, rlimits, compat syscalls, and filesystem-specific copy/remap implementations.

Risks and test signals: Risks include f_pos races, signed offset overflow, compat return truncation, missed permission checks, incorrect short-copy semantics, write freeze deadlocks, splice fallback inconsistencies, and append/nowait/direct-I/O validation errors. Test concurrent read/write/lseek, stream files, compat syscalls, RLIMIT_FSIZE, O_APPEND pwritev, copy_file_range across same and different superblocks, sendfile to files and pipes, and invalid user iovecs.

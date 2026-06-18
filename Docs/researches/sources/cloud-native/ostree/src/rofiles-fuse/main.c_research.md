# sources/cloud-native/ostree/src/rofiles-fuse/main.c

Purpose: implements `rofiles-fuse`, a FUSE filesystem that exposes a base directory with writable directories but protects OSTree hardlinked regular files/symlinks from mutation unless `--copyup` is enabled.

Important APIs/functions: FUSE callbacks cover getattr, readlink, readdir, mkdir/unlink/rmdir/symlink/rename/link, chmod/chown/truncate/utimens, create/open, read/write buffer paths, statfs, release/fsync/access, and xattrs. `ENSURE_RELPATH()` normalizes absolute FUSE paths. `can_write_stbuf()` rejects writes to hardlinked regular files/symlinks and fsverity files. `verify_write_or_copyup()` enforces that rule or invokes `copyup()`. `copyup()` uses `glnx_file_copy_at()` for regular files and `ostree_break_hardlink()` for symlinks. `rofs_parse_opt()` parses basepath and `--copyup`; `main()` calls `fuse_main()`.

Control flow: startup parses FUSE options and opens the first non-option as `basefd`. Read-only operations directly proxy to `*at` syscalls under `basefd`. Mutating operations normalize path then run `verify_write_or_copyup()` when they can alter file contents/metadata. Open/create distinguishes read-only from write access. The callback table supplies the operations to FUSE.

State/persistence: global `basefd` points to the exposed tree. With default mode, writes to hardlinked content fail with `EROFS`; directory changes and non-hardlinked file mutations persist in the base tree. With `--copyup`, protected hardlinks are broken before mutation, persistently creating independent file/symlink objects.

Dependencies/integration: depends on libfuse version conditionals, Linux `statx`, `renameat2`, xattr syscalls, libglnx copy helpers, and libostree hardlink-breaking. It is built by the sibling automake fragment.

Risks: global `basefd`/`opt_copyup` assume one mounted filesystem per process. `renameat2` assumes Linux 3.15+. Xattr operations build `/proc/self/fd/%d/%s` paths and need procfs. `access(W_OK)` intentionally lies by delegating to underlying access, so callers may still receive later `EROFS`. `can_write_stbuf()` depends on link count and fsverity attributes being accurate from `statx`.

Test signals: no file in this subset directly tests rofiles-fuse. Meaningful tests should mount FUSE, verify hardlinked file writes fail, `--copyup` breaks hardlinks, directory mutations persist, xattrs work, and fsverity files stay immutable.

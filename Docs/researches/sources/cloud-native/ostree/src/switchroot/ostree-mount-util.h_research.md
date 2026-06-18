# sources/cloud-native/ostree/src/switchroot/ostree-mount-util.h

Purpose: shared small C utility header for switchroot/remount binaries that must run early in boot with minimal dependencies.

Important APIs/macros: defines `INITRAMFS_MOUNT_VAR`, `_OSTREE_SYSROOT_READONLY_STAMP`, `_OSTREE_COMPOSEFS_ROOT_STAMP`, and an `autofree` cleanup attribute. `path_is_on_readonly_fs()` checks `statvfs()` for `ST_RDONLY`. `read_proc_cmdline()` reads `/proc/cmdline`. `find_proc_cmdline_key()` extracts `key=value` tokens. `touch_run_ostree()` creates `/run/ostree-booted` best-effort.

Control flow: helpers either return allocated strings/bools or terminate through `err()` on critical filesystem query failure.

State/persistence: `touch_run_ostree()` creates a stamp file; other helpers are read-only. `read_proc_cmdline()` allocates caller-owned memory.

Dependencies/integration: used by prepare-root static/nonstatic and remount code. It deliberately uses libc/POSIX APIs suitable for initramfs/static contexts.

Risks: `read_proc_cmdline()` assumes nonempty content before checking `cmdline[len - 1]`. `find_proc_cmdline_key()` does simple space tokenization and does not handle quoting. `path_is_on_readonly_fs()` exits process on stat failure.

Test signals: `tests-unit-container/test-prepare-root.sh` indirectly exercises cmdline reading and read-only filesystem detection through `ostree-prepare-root`.

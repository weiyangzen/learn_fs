# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/compat.h

## Purpose
Provides platform compatibility glue for GlusterFS builds across Linux, BSD, Darwin, and Solaris. It normalizes missing constants, filesystem flags, xattr APIs, timestamp accessors, path limits, endian helpers, and selected libc functions so the rest of libglusterfs can compile against a mostly uniform interface.

## APIs, Types, and Functions
Important definitions include `UNIX_PATH_MAX`, `GF_XATTR_NAME_MAX`, `FALLOC_FL_*`, `F_GETLK64/F_SETLK64/F_SETLKW64`, `_PATH_UMOUNT`, `NAME_MAX`, `EUCLEAN`, and `ST_ATIM_*`/`ST_MTIM_*`/`ST_CTIM_*` accessor macros. Old libc wrappers map `l* xattr` calls to non-link-aware calls when unavailable. BSD and Darwin sections define `off64_t`, `ino64_t`, `sighandler_t`, IPv6 address aliases, and endian conversion macros. Solaris declares compatibility functions such as `asprintf()`, `strsep()`, Solaris xattr wrappers, rename/unlink wrappers, and `solaris_xattr_resolve_path()`. The exported `gf_umount_lazy()` abstracts lazy unmount plus optional directory removal.

## Control Flow, State, and Persistence
This header is compile-time control flow: preprocessor branches select OS-specific shims. It keeps no runtime state, but its macro choices determine how all callers interpret timestamps, xattr names, fallocate flags, and device/path limits. GCC poisoning of `system`, `mkostemp`, and `popen` enforces safer internal run APIs unless `RELAX_POISONING` is set.

## Dependencies and Integration
Depends on OS headers such as `sys/un.h`, `sys/xattr.h`, `linux/falloc.h`, `sys/extattr.h`, `machine/endian.h`, `libgen.h`, and `argp`. It is included by core headers including `iatt.h` and `glusterfs-fops.h`, so incompatibilities propagate widely.

## Risks and Test Signals
Risks are stale OS assumptions, silent behavior changes when link-aware xattr calls are unavailable, Darwin hard failure without 64-bit inode support, Solaris xattr emulation divergence, and timestamp precision loss when only zero-nsec fallbacks exist. Test signals include multi-OS compile coverage, xattr round trips on symlinks, stat timestamp conversion tests, fallocate flag availability checks, and builds that verify poisoned APIs are not used.

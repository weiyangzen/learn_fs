<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/errno-mapping.c -->
# sources/distributed-fs/orangefs/src/common/misc/errno-mapping.c

Purpose: maps OrangeFS/PVFS error codes to human-readable strings and output helpers. It wraps platform `strerror_r` behavior and handles PVFS-specific non-errno error classes.

Important functions: `PVFS_strerror_r()` maps an input error through `PVFS_get_errno_mapping()`, then either copies a PVFS non-errno string from `PINT_non_errno_strerror_mapping` or calls platform `strerror_r`/`strerror_s`. `PVFS_perror()` writes formatted error information to stderr. `PVFS_perror_gossip_silent()` and `PVFS_perror_gossip_verbose()` toggle a static suppression flag. `PVFS_perror_gossip()` emits the same error information through `gossip_err()` unless silenced.

Control flow includes preprocessor manipulation of `_XOPEN_SOURCE`, `_GNU_SOURCE`, and `__USE_GNU` to force POSIX `strerror_r` declaration, then restore previous macro state. Windows defines missing errno constants and uses `strerror_s`.

State: only `pvfs_perror_gossip_silent` persists in process memory. There is no external persistence. Dependencies include `pvfs2-internal.h`, `pvfs2-util.h`, generated errno mapping macros from `pvfs2-types.h`, and gossip.

Risks: macro manipulation around libc feature macros is fragile and compile-environment sensitive. The POSIX `strerror_r` return value is passed through; callers should not assume GNU semantics. `limit = min(n, 256)` does not guard negative `n` robustly if callers misuse the API. Tests should cover PVFS errno errors, PVFS non-errno errors, plain errno values, non-PVFS warning formatting, silent/verbose toggles, and Windows/POSIX builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/errno-mapping.c -->

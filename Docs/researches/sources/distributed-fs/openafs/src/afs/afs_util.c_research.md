# sources/distributed-fs/openafs/src/afs/afs_util.c

## Purpose

`afs_util.c` provides miscellaneous Cache Manager utility routines for numeric/string conversion, portable string helpers, warning output for server addresses, vnode noop/bad operations, pointer-to-int truncation, and AFS inode-number calculation. These helpers are small, but several are widely used by vnode operations, server logging, cache identity generation, and portability layers.

## Important APIs, Types, and Functions

Exports include `afs_cv2string`, `afs_strtoi_r`, `afs_strcasecmp`, `afs_strcat`, `afs_strcpy` on selected OpenBSD builds, `afs_strchr`, `afs_strrchr`, `afs_strdup`, `print_internet_address`, `afs_noop`, `afs_badop`, `afs_data_pointer_to_int32`, and `afs_calc_inum`. Internal helper `afs_calc_inum_md5` optionally generates inode numbers from an MD5 digest when `afs_md5inum` is nonzero. Global `afs_md5inum` controls whether MD5-based inode calculation is attempted.

## Control Flow and State

`afs_cv2string` writes an unsigned decimal string backwards into a caller-provided buffer and returns the start pointer. `afs_strtoi_r` parses only unsigned decimal digits into an `afs_uint32`, stops at the first nondigit, reports overflow-like conditions, and updates `endptr`; it is documented as a portable parser for volume/vnode/uniq values, not a general `strtoul`. The string helper fallbacks are compiled only when platform macros do not provide equivalents.

`print_internet_address` formats a `srvAddr` IPv4 address, server cell, postamble, and error code through `afs_warnall`; for multihomed servers it adds context describing whether all addresses are down or only one interface changed. When logging a down event with an Rx connection, it asks Rx for network error origin/type/code/message and emits a second diagnostic if available. `afs_noop` returns `EINVAL`; `afs_badop` panics for invalid vnode operations.

`afs_data_pointer_to_int32` uses a union and runtime endian check to return the least significant `afs_int32` portion of a pointer without triggering truncation warnings. `afs_calc_inum` first asks `afs_calc_inum_md5` for a nonzero/non-one positive 31-bit inode derived from cell, volume, and vnode; if unavailable, it falls back to `(volume << 16) + vnode` and masks to 31 bits.

## Dependencies and Integration Points

The file depends on AFS kernel includes, `afs_stats.h` counters, Rx network-error reporting, `struct srvAddr`/`struct server`, warning output (`afs_warnall`), and `hcrypto/md5.h`. `print_internet_address` is called by server liveness code in `afs_server.c`. Inode calculation is used by vnode/cache identity code to produce stable-ish inode values for AFS objects exposed to the OS.

## Persistence and Side Effects

Most helpers are stateless. `afs_md5inum` is a runtime knob affecting inode-number generation. `print_internet_address` emits user-visible/kernel-visible warnings. `afs_badop` intentionally terminates via panic. `afs_strdup` allocates memory that callers must free with AFS allocation routines.

## Risks and Test Signals

Risks include buffer misuse by callers of `afs_cv2string`/`afs_strcat`, `afs_strtoi_r` accepting empty strings as zero with `endptr` unchanged, IPv4-only logging assumptions, inode-number collisions in both MD5 and fallback modes, and pointer truncation being intentionally lossy. Test signals include parsing boundary values around `4294967295`, server-down logging with and without Rx network errors, MD5 inode generation avoiding 0 and 1, fallback inode stability, and platform builds where fallback string functions are compiled.

# Group Research: group_1191_netbsd_src_sources_os_bsd_netbsd_src_lib_libc_compat_include_unistd_a9f53522b113

Scope checked against `Docs/research_subset_a.md`; all listed files are under `sources/os/bsd/netbsd-src`, which is included in subset A. Every source file listed for this group was read completely and summarized separately below.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/unistd.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/unistd.h

Read completely: 75 lines.

This compatibility header declares old and compatibility-visible process/file-descriptor interfaces: `vfork`, `__vfork14`, `dup3`, and `__dup3100`. It wraps declarations in `__BEGIN_DECLS`/`__END_DECLS` and marks the vfork variants `__returns_twice`.

Important interactions: consumed by compatibility implementations such as `compat_dup3.c`, and by legacy code that intentionally binds to older libc symbol versions.

Security/reliability notes: declaration-only; the main risk is ABI confusion if included instead of the current public `<unistd.h>`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/unistd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/utime.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/utime.h

Read completely: 51 lines.

This header defines legacy `struct utimbuf50` with 32-bit access and modification times and declares the old `utime` entry point plus newer `__utime50`. It includes machine ANSI definitions and cdefs for ABI-compatible prototypes.

Important interactions: bridges old callers using 32-bit `time_t` to the current `struct utimbuf` implementation.

Security/reliability notes: no executable logic. Time truncation is inherent when converting current time values into `int32_t`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/utime.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/utmp.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/utmp.h

Read completely: 68 lines.

This header defines `struct utmp50`, the old utmp record format with `int32_t ut_time`, and inline converters between `struct utmp` and `struct utmp50`. It declares compatibility `getutent` and current `__getutent50` symbols.

Important interactions: conversion is mostly raw `memcpy` with only the time field adjusted. It depends on the beginning layout of current `struct utmp` remaining compatible with the old fixed-size fields.

Security/reliability notes: no direct runtime logic beyond inline conversion. The 32-bit timestamp conversion can truncate modern timestamps.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/utmp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/utmpx.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/utmpx.h

Read completely: 101 lines.

This header defines legacy `utmpx50` and `lastlogx50` records using `timeval50`, plus inline conversion between current `utmpx` and old `utmpx50`. It declares compatibility wrappers for utmpx iteration, lookup, update, lastlog, and utmp/utmpx conversion functions.

Important interactions: relies on `compat/sys/time.h` conversion helpers and current utmpx layouts. Most fields are copied wholesale, with only embedded time values converted.

Security/reliability notes: ABI-only surface. Timestamp narrowing to 32-bit seconds is the primary correctness limit.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/utmpx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/vis.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/vis.h

Read completely: 43 lines.

This compatibility header declares old `unvis` entry points: `unvis`, `__unvis13`, and `__unvis50`. It exists so legacy code can bind to historical unvis symbol versions.

Security/reliability notes: declaration-only; runtime behavior is in the corresponding libc implementations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/vis.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/locale/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/locale/Makefile.inc

Read completely: 6 lines.

This makefile fragment adds compatibility locale sources to libc: `compat_setlocale1.c` and `compat_setlocale32.c`. It extends `.PATH` to machine-specific and generic compat locale directories and adds the current locale include path.

Security/reliability notes: build orchestration only.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/locale/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/locale/compat_setlocale1.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/locale/compat_setlocale1.c

Read completely: 55 lines.

This implements `compat_setlocale`, an old `setlocale` ABI wrapper. It warns on compatibility references, sets `__mb_len_max_runtime` to `1`, then calls the shared `__setlocale(category, locale)` implementation.

Important interactions: used for binaries built against an ABI where `MB_LEN_MAX` behavior was fixed to one byte.

Security/reliability notes: no allocation or parsing here. Correctness depends on callers expecting the historical single-byte runtime maximum.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/locale/compat_setlocale1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/locale/compat_setlocale32.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/locale/compat_setlocale32.c

Read completely: 61 lines.

This implements `__setlocale_mb_len_max_32`, the compatibility locale wrapper for old platforms where `MB_LEN_MAX` was effectively 32. It sets `__mb_len_max_runtime` to `32` and delegates to `__setlocale`.

Important interactions: hppa is explicitly excluded because it used a different historical maximum and has an architecture-specific file.

Security/reliability notes: no direct input handling beyond forwarding the locale string. ABI correctness depends on selecting the right per-architecture variant.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/locale/compat_setlocale32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/net/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/net/Makefile.inc

Read completely: 15 lines.

This makefile fragment adds `__cmsg_alignbytes.c`, `compat_ns_addr.c`, and `compat_ns_ntoa.c` to the compat network build. It also suppresses one lint warning in `compat_ns_ntoa.c` caused by lowercase-to-uppercase character arithmetic on unsigned character data.

Security/reliability notes: build-only; the lint suppression is narrowly targeted.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/net/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/net/__cmsg_alignbytes.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/net/__cmsg_alignbytes.c

Read completely: 68 lines.

This implements `__cmsg_alignbytes`, returning the alignment mask used for old control-message layout. It caches the value in a static local, tries to query `HW_ALIGNBYTES` via `sysctl` when available, and falls back to compile-time `ALIGNBYTES`.

Important interactions: consumed by compatibility socket ancillary-data macros/functions that must reproduce older alignment rules.

Security/reliability notes: the static cache is simple and unsynchronized, but races only compute the same small integer. Sysctl failure falls back safely.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/net/__cmsg_alignbytes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/net/compat_ns_addr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/net/compat_ns_addr.c

Read completely: 244 lines.

This implements legacy Xerox NS address parsing in `ns_addr`. It accepts multiple historical syntaxes using `.`, `:`, or `#` separators, parses network/host/port fields in decimal, octal, hexadecimal, dash-separated decimal chunks, dotted/colon hex bytes, and comma-separated shorts, then converts arbitrary-base chunks into byte arrays.

Important interactions: fills a static `struct ns_addr`, so callers receive a pointer-stable but non-thread-local global result pattern. It depends on compatibility `ns.h` and endian helpers for socket/port layout.

Security/reliability notes: input is copied into a fixed 50-byte buffer with `strlcpy`, so long strings are truncated before parsing. Numeric parsing with `sscanf` is permissive and legacy-oriented; malformed suffixes often just terminate parsing rather than fail explicitly.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/net/compat_ns_addr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/net/compat_ns_ntoa.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/net/compat_ns_ntoa.c

Read completely: 110 lines.

This implements legacy `ns_ntoa`, formatting an NS address into a static buffer. It prints the network in hex, appends host bytes with leading zero compression, appends a port if present, and uses `spectHex` to uppercase hex letters and append `H` when needed to disambiguate numeric-looking hex strings.

Important interactions: returns a pointer to a static 40-byte buffer, matching old libc behavior but not thread-safe.

Security/reliability notes: uses `sprintf` into fixed buffers, but field sizes are bounded by NS address widths. Static result storage means concurrent calls can overwrite previous results.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/net/compat_ns_ntoa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/rpc/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/rpc/Makefile.inc

Read completely: 5 lines.

This makefile fragment adds RPC compatibility sources `compat_pmap_rmtcall.c` and `compat_rpcb.c` from `${COMPATDIR}/rpc`.

Security/reliability notes: build orchestration only.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/rpc/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/rpc/compat_pmap_rmtcall.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/rpc/compat_pmap_rmtcall.c

Read completely: 69 lines.

This implements old `pmap_rmtcall` taking `struct timeval50`. It converts the timeout to current `struct timeval` and forwards all arguments to `__pmap_rmtcall50`.

Important interactions: exposes a weak alias for legacy symbol binding and warns callers to include the current RPC header for the correct reference.

Security/reliability notes: straightforward time conversion wrapper; timeout truncation or widening semantics are delegated to `timeval50_to_timeval`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/rpc/compat_pmap_rmtcall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/rpc/compat_rpcb.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/rpc/compat_rpcb.c

Read completely: 83 lines.

This implements compatibility `rpcb_rmtcall` and `rpcb_gettime`. `rpcb_rmtcall` converts a `timeval50` timeout and delegates to `__rpcb_rmtcall50`; `rpcb_gettime` calls `__rpcb_gettime50` and narrows the returned `time_t` to `int32_t`.

Important interactions: provides weak aliases and reference warnings for legacy RPC binder APIs.

Security/reliability notes: `rpcb_gettime` has inherent year-2038 style truncation because the legacy output pointer is `int32_t *`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/rpc/compat_rpcb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/stdio/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/stdio/Makefile.inc

Read completely: 23 lines.

This makefile fragment adds compatibility stdio sources `compat_fgetpos.c` and `compat_fsetpos.c`, including machine-architecture-specific paths. It adds stdio include flags and includes optional local make configuration when present.

Security/reliability notes: build-only; local configuration inclusion can affect build reproducibility by design.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/stdio/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/stdio/compat_fgetpos.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/stdio/compat_fgetpos.c

Read completely: 64 lines.

This implements old `fgetpos` using `off_t *` instead of current `fpos_t`. It asserts non-null arguments, stores `ftello(fp)` into `*pos`, and returns nonzero if `ftello` returned `(off_t)-1`.

Important interactions: binds legacy `fgetpos` to current offset-based stream positioning.

Security/reliability notes: simple wrapper. The return expression both assigns and checks for failure, relying on `ftello` to set errno.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/stdio/compat_fgetpos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/stdio/compat_fsetpos.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/stdio/compat_fsetpos.c

Read completely: 68 lines.

This implements old `fsetpos` with an `off_t *` position. It asserts non-null arguments and calls `fseeko(iop, *pos, SEEK_SET)`.

Important interactions: provides compatibility for binaries expecting the older position type.

Security/reliability notes: the wrapper compares the `fseeko` return value to `(off_t)-1` even though `fseeko` returns `int`; this works for failure detection but mirrors historical style rather than modern type clarity.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/stdio/compat_fsetpos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/stdlib/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/stdlib/Makefile.inc

Read completely: 5 lines.

This makefile fragment adds compatibility stdlib sources `compat_putenv.c`, `compat_random.c`, and `compat_unsetenv.c`, and includes compat/current stdlib headers.

Security/reliability notes: build orchestration only.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/stdlib/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/stdlib/compat_putenv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/stdlib/compat_putenv.c

Read completely: 83 lines.

This implements legacy `putenv` behavior that copies the supplied string instead of adopting caller-owned storage. It validates the environment variable name with `__envvarnamelen`, duplicates the string, replaces `=` with NUL, calls `setenv(copy, copy + name_len + 1, 1)`, then frees the temporary copy.

Important interactions: uses current environment helpers and `setenv` while preserving older ownership semantics.

Security/reliability notes: rejects empty/invalid variable names with `EINVAL`. Since it copies before calling `setenv`, caller mutation after return does not affect the environment.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/stdlib/compat_putenv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/stdlib/compat_random.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/stdlib/compat_random.c

Read completely: 66 lines.

This provides compatibility `initstate` and `srandom` wrappers whose seed type is `unsigned long`. Both cast the seed down to `unsigned int` and delegate to `__initstate60`/`__srandom60`.

Important interactions: preserves old symbol names via weak aliases and warnings.

Security/reliability notes: seed narrowing is intentional ABI compatibility. There is no cryptographic security claim for these PRNG APIs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/stdlib/compat_random.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/stdlib/compat_unsetenv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/stdlib/compat_unsetenv.c

Read completely: 86 lines.

This implements old `unsetenv` returning `void`. It locks the environment, repeatedly finds matching slots with `__getenvslot`, shifts `environ` entries left to delete every match, then unlocks.

Important interactions: uses current libc environment lock helpers and global `environ`.

Security/reliability notes: no error is returned to legacy callers. The environment lock protects concurrent libc environment access; callers still must avoid racing direct writes to `environ`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/stdlib/compat_unsetenv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/Lint_Ovfork.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/Lint_Ovfork.c

Read completely: 14 lines.

This is a lint stub for `vfork`, returning `0`. It exists only when lint sources are included.

Security/reliability notes: not a runtime implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/Lint_Ovfork.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/Makefile.inc

Read completely: 23 lines.

This makefile fragment lists the syscall compatibility source files built into libc, covering directory entries, time32/time50 wrappers, stat/statfs/statvfs transitions, file handles, sockets, SysV IPC, timers, scheduling, `dup3`, kqueue, message queues, and signal trampolines. It also adds the `getdirentries.3` man page and lint stub.

Security/reliability notes: build orchestration only, but it defines which old ABI symbols are actually present.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___fhstat30.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___fhstat30.c

Read completely: 57 lines.

This implements old `__fhstat30` by aliasing it to `__compat___fhstat30`. It converts the old fixed-size file-handle API by calling `__compat___fhstat40(fhp, FHANDLE30_SIZE, sb)`.

Important interactions: bridges old `compat_30_fhandle` callers to the newer length-explicit file-handle stat wrapper.

Security/reliability notes: no local validation beyond forcing `FHANDLE30_SIZE`; errors come from the downstream call.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___fhstat30.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___fhstatvfs140.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___fhstatvfs140.c

Read completely: 59 lines.

This implements `__fhstatvfs140`, forwarding a file handle and explicit length to `__fhstatvfs190`, then converting current `struct statvfs` to legacy `statvfs90` on success.

Important interactions: compatibility wrapper for the statvfs ABI version that still carried a flags argument but old output layout.

Security/reliability notes: allocation-free; correctness depends on `statvfs_to_statvfs90` handling field narrowing.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___fhstatvfs140.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___fhstatvfs40.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___fhstatvfs40.c

Read completely: 58 lines.

This implements `__fhstatvfs40`, forwarding to `__fhstatvfs190` with flags `0` and converting current `statvfs` to `statvfs90`.

Important interactions: old ABI for file-handle statvfs without a flags parameter.

Security/reliability notes: direct conversion wrapper; downstream syscall reports errors.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___fhstatvfs40.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___lwp_park50.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___lwp_park50.c

Read completely: 63 lines.

This implements `___lwp_park50`, adapting the old `__lwp_park` calling convention to `___lwp_park60`. It copies an optional relative-looking `timespec` pointer into a local and calls the newer API with `CLOCK_REALTIME` and `TIMER_ABSTIME`.

Important interactions: chained with `compat__lwp_park.c`, which converts `timespec50` to current `timespec` before reaching this layer.

Security/reliability notes: no heap allocation; timeout semantics are fixed by the chosen clock/flags.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___lwp_park50.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___msgctl13.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___msgctl13.c

Read completely: 68 lines.

This implements old `__msgctl13` for SysV message queues. For `IPC_SET`, it converts `msqid_ds13` to native, calls `__msgctl50`, and for `IPC_STAT` converts native results back to `msqid_ds13`.

Important interactions: relies on conversion helpers from `compat/sys/msg.h`.

Security/reliability notes: `ds13` must be valid for commands that need it. Field truncation is part of old ABI conversion.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___msgctl13.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___ntp_gettime30.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___ntp_gettime30.c

Read completely: 30 lines.

This implements `__ntp_gettime30`, calling `__ntp_gettime50` and converting the returned `ntptimeval` to `ntptimeval50` with 32-bit seconds and nanoseconds.

Security/reliability notes: no local validation; output timestamp seconds are narrowed to `int32_t`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___ntp_gettime30.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___semctl13.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___semctl13.c

Read completely: 108 lines.

This implements old varargs `__semctl13`. It extracts `union __semun` for commands that require an argument, converts `semid_ds13` to native for `IPC_SET`, points the union at a native temporary, calls `____semctl50`, and converts native output back for `IPC_STAT`.

Important interactions: handles the awkward SysV `semctl` varargs ABI and old structure layout.

Security/reliability notes: correctness depends on callers passing the expected vararg for commands that require it. The lint-only path uses `memcpy` to quiet varargs diagnostics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___semctl13.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___shmctl13.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___shmctl13.c

Read completely: 68 lines.

This implements old `__shmctl13` for SysV shared memory. It converts `shmid_ds13` to native for `IPC_SET`, calls `__shmctl50`, and converts native output to `shmid_ds13` for `IPC_STAT`.

Security/reliability notes: direct ABI conversion wrapper; old timestamp and size fields can be narrower than current native fields.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___shmctl13.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___sigaction14_sigtramp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___sigaction14_sigtramp.c

Read completely: 82 lines.

This implements `__libc_sigaction14`, weak-aliased as `__sigaction14`. It calls `__sigaction_sigtramp`, choosing no trampoline when `act == NULL`, a legacy sigcontext trampoline when available and `SA_SIGINFO` is not set, otherwise the siginfo trampoline.

Important interactions: preserves historical signal trampoline selection while using the modern trampoline registration backend.

Security/reliability notes: it preserves `errno` when the sigcontext trampoline probe fails with `EINVAL` and retries with siginfo. This is delicate ABI logic around signal delivery.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___sigaction14_sigtramp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___stat13.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___stat13.c

Read completely: 140 lines.

This implements `__stat13`, `__fstat13`, `__lstat13`, and old `fhstat` aliases. Each calls the corresponding `*50` current stat wrapper, then converts native `struct stat` to `struct stat13` by narrowing device, inode, rdev, and timestamp seconds to older fields.

Important interactions: `fhstat` passes a hard-coded old file-handle size of 28 bytes to `__fhstat50`.

Security/reliability notes: field narrowing can truncate inode/device/time values. The conversion is deterministic and allocation-free.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___stat13.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___stat30.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___stat30.c

Read completely: 137 lines.

This implements `__stat30`, `__fstat30`, `__lstat30`, and `__fhstat40`. It calls the current `*50` stat APIs and converts native `struct stat` to `struct stat30`, using `timespec50` conversion for timestamps and preserving wider inode fields than `stat13`.

Important interactions: `__fhstat40` accepts an explicit file-handle size and delegates to `__fhstat50`.

Security/reliability notes: device fields still narrow to 32-bit compatibility layout. Timestamp handling follows the `time50` conversion helpers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___stat30.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat__lwp_park.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat__lwp_park.c

Read completely: 66 lines.

This implements old `_lwp_park` taking `timespec50`. It converts an optional timeout to current `timespec` and calls `___lwp_park50`.

Security/reliability notes: direct stack-only conversion wrapper. Timeout pointer may be null and is handled.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat__lwp_park.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_adjtime.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_adjtime.c

Read completely: 77 lines.

This implements old `adjtime` using `timeval50` inputs and outputs. It converts optional delta and old-delta pointers to native `timeval`, calls `__adjtime50`, and converts the remainder back on success.

Security/reliability notes: null input/output pointers are handled. Timestamp narrowing happens only for the returned compatibility structure.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_adjtime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_aio_suspend.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_aio_suspend.c

Read completely: 70 lines.

This implements old `aio_suspend` with a `timespec50` timeout. It converts the optional timeout and delegates to `__aio_suspend50`.

Important interactions: leaves the aiocb list unchanged; only the timeout ABI differs.

Security/reliability notes: no heap allocation; timeout null is supported.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_aio_suspend.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_clock.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_clock.c

Read completely: 98 lines.

This implements compatibility `clock_settime`, `clock_gettime`, and `clock_getres` using `timespec50`. Set converts input to native and calls `__clock_settime50`; get/res call current wrappers and convert results back to `timespec50`.

Security/reliability notes: get/res handle null result pointers by passing null downstream. Set accepts null and forwards null, matching the wrapper style.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_dup3.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_dup3.c

Read completely: 76 lines.

This implements compatibility `dup3`. For distinct descriptors it delegates to `__dup3100`; for `oldfd == newfd`, it emulates allowed flag effects by updating file status flags with `F_GETFL`/`F_SETFL` and descriptor flags with `F_SETFD`.

Important interactions: supports compatibility behavior for same-fd `dup3`, including `O_NONBLOCK`, `O_NOSIGPIPE`, `O_CLOEXEC`, and `O_CLOFORK`.

Security/reliability notes: only the listed flags are handled in the same-fd path; unsupported bits are effectively ignored except through the masked cases. Errors from `fcntl` propagate.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_dup3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_fhopen.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_fhopen.c

Read completely: 56 lines.

This implements old `fhopen` by passing the legacy `compat_30_fhandle` and fixed `FHANDLE30_SIZE` to `__fhopen40`.

Security/reliability notes: direct wrapper; downstream file-handle validation controls errors and permissions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_fhopen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_fhstatvfs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_fhstatvfs.c

Read completely: 59 lines.

This implements old `fhstatvfs`, calling `__fhstatvfs190` with legacy handle size and flags `0`, then converting native `statvfs` to `statvfs90`.

Security/reliability notes: direct conversion wrapper; field narrowing is delegated to the statvfs converter.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_fhstatvfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_fhstatvfs1.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_fhstatvfs1.c

Read completely: 60 lines.

This implements old `fhstatvfs1`, like `fhstatvfs` but preserving the caller-supplied flags argument. It converts the returned native `statvfs` to `statvfs90`.

Security/reliability notes: no local allocation; depends on the newer syscall wrapper for validation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_fhstatvfs1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_getdents.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_getdents.c

Read completely: 92 lines.

This implements libc12-compatible `getdents`. It calls `__getdents30` to fill the user buffer with current `dirent` records, then converts them in place to smaller `dirent12` records, narrowing inode numbers to 32-bit and truncating names to the old fixed name buffer if needed.

Important interactions: in-place conversion relies on `dirent12` being smaller than current `dirent`.

Security/reliability notes: the code avoids unaligned 64-bit inode access with `memcpy`. Inode and long-name truncation are compatibility behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_getdents.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_getdirentries.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_getdirentries.c

Read completely: 51 lines.

This implements compatibility-only `getdirentries`. It stores the current directory offset from `lseek(fd, 0, SEEK_CUR)` into `*basep`, then calls the compatibility `getdents`.

Security/reliability notes: dereferences `basep` unconditionally. The warning notes this interface is compatibility-only and callers should prefer `getdents` or `readdir`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_getdirentries.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_getfh.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_getfh.c

Read completely: 69 lines.

This implements old `getfh`. It calls `__getfh30` with a `compat_30_fhandle` buffer and size pointer, then verifies the returned size equals `FHANDLE30_SIZE`; otherwise it returns `EINVAL`.

Security/reliability notes: explicit size verification prevents accepting a mismatched file-handle layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_getfh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_getrusage.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_getrusage.c

Read completely: 63 lines.

This implements old `getrusage` returning `struct rusage50`. It calls `__getrusage50` into native `struct rusage`, then converts to the compatibility layout.

Security/reliability notes: direct wrapper; time and resource fields may narrow according to `rusage_to_rusage50`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_getrusage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_gettimeofday.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_gettimeofday.c

Read completely: 62 lines.

This implements old `gettimeofday` with `timeval50`. It calls `__gettimeofday50` into native `timeval` and converts to `timeval50`.

Security/reliability notes: the code converts into `tv50` unconditionally after success, so callers must provide a valid output pointer for this ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_gettimeofday.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_itimer.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_itimer.c

Read completely: 82 lines.

This implements old `setitimer` and `getitimer` using `itimerval50`. Set converts optional new and old timer values around `__setitimer50`; get calls `__getitimer50` and converts the result back.

Security/reliability notes: null timer pointers are handled as optional where supported by the underlying API.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_itimer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_kevent.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_kevent.c

Read completely: 103 lines.

This implements compatibility `kevent` and `__kevent50`. `kevent` converts an optional `timespec50` timeout and calls `__kevent50`; `__kevent50` allocates native `struct kevent` arrays, converts input `kevent100` changes, calls `__kevent100`, then converts returned events back to `kevent100`.

Important interactions: bridges old kqueue event layout to the current one.

Security/reliability notes: allocation sizes are `sizeof(*event) * count` without an explicit overflow check. A zero-count `malloc(0)` returning NULL would be treated as failure on platforms with that behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_kevent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_lfs_segwait.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_lfs_segwait.c

Read completely: 64 lines.

This implements old `lfs_segwait`, converting an optional `timeval50` timeout to native `timeval` and calling `__lfs_segwait50`.

Security/reliability notes: direct timeout conversion wrapper for LFS segment wait.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_lfs_segwait.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_mknod.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_mknod.c

Read completely: 59 lines.

This implements old `mknod` with a 32-bit device argument. It aliases `mknod` to `__compat_mknod` and forwards to `__mknod50`.

Security/reliability notes: device number width is constrained by the old ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_mknod.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_mount.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_mount.c

Read completely: 27 lines.

This implements old `mount`, forwarding to `__mount50(type, dir, flags, data, 0)`. It discards positive return values, returning `0` for all non-`-1` results.

Important interactions: length `0` tells the kernel to use the default filesystem argument size.

Security/reliability notes: intentionally erases positive `MNT_GETARGS`-style responses for old ABI behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_mount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_mqueue.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_mqueue.c

Read completely: 86 lines.

This implements old `mq_timedreceive` and `mq_timedsend` with `timespec50` timeouts. Both convert optional timeout pointers to native `timespec` and call the `*50` message-queue wrappers.

Security/reliability notes: no local allocation. The message buffer and priority arguments are forwarded unchanged.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_mqueue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_msync.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_msync.c

Read completely: 48 lines.

This implements old two-argument `msync`. It calls `__msync13(addr, size, MS_SYNC | MS_INVALIDATE)`.

Security/reliability notes: hard-codes historical sync/invalidate behavior; no local validation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_msync.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_nanosleep.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_nanosleep.c

Read completely: 77 lines.

This implements old `nanosleep` using `timespec50`. It converts optional requested and remaining time pointers around `__nanosleep50`.

Security/reliability notes: null pointers are handled. Remaining time is converted back only on successful wrapper return.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_nanosleep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_ntp_gettime.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_ntp_gettime.c

Read completely: 30 lines.

This implements old `ntp_gettime`, calling `__ntp_gettime50` and converting native nanoseconds to old microseconds in `ntptimeval30`.

Security/reliability notes: seconds narrow to `int32_t`, and nanosecond precision is reduced to microseconds.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_ntp_gettime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_sched.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_sched.c

Read completely: 56 lines.

This implements old `sched_rr_get_interval`. It ignores the PID, sets seconds to zero, and sets nanoseconds from `sysconf(_SC_SCHED_RT_TS) * 1000`.

Security/reliability notes: no syscall is used. If `sysconf` fails or returns an unexpected value, the result is passed through arithmetically without local error handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_sched.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_select.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_select.c

Read completely: 102 lines.

This implements old `pollts`, `select`, and `pselect` with `timespec50`/`timeval50` timeout layouts. Each converts the optional timeout to native form and delegates to the corresponding `*50` wrapper.

Security/reliability notes: fd sets, pollfd arrays, and signal masks are forwarded unchanged. Null timeout pointers are supported.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_select.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_semctl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_semctl.c

Read completely: 100 lines.

This implements old public `semctl` for `semid_ds14`. It extracts varargs for commands that use `union __semun`, converts old structures to native for `IPC_SET`, calls `__semctl50`, and converts back for `IPC_STAT`.

Security/reliability notes: varargs ABI misuse by callers is not locally detectable. Structure conversion carries historical field-width limits.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_semctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_settimeofday.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_settimeofday.c

Read completely: 65 lines.

This implements old `settimeofday` with a `timeval50` pointer. It converts the supplied time to native `timeval` and calls `__settimeofday50`.

Security/reliability notes: unlike several other time wrappers, it dereferences/converts `tv50` unconditionally, so this compatibility ABI expects a non-null time pointer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_settimeofday.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_sigaltstack.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_sigaltstack.c

Read completely: 68 lines.

This implements old `sigaltstack` using `struct sigaltstack13`. It maps old stack fields into native `stack_t`, calls `__sigaltstack14`, then maps the old stack result back, clamping `ss_size` to `INT_MAX`.

Security/reliability notes: `onss` is dereferenced unconditionally, so it does not support a null new-stack pointer despite modern `sigaltstack` allowing query-only calls. Output size clamping avoids overflowing old `int` size.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_sigaltstack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_sigtimedwait.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_sigtimedwait.c

Read completely: 75 lines.

This implements old `sigtimedwait` and `__sigtimedwait` with `timespec50` timeout. It converts a non-null timeout to native `timespec` and calls `____sigtimedwait50`; null timeout is passed through.

Security/reliability notes: direct wrapper; signal set and siginfo pointers are forwarded unchanged.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_sigtimedwait.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_socket.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_socket.c

Read completely: 27 lines.

This implements compatibility `socket` by calling `__socket30`. If `errno` is `EAFNOSUPPORT`, it remaps it to `EPROTONOSUPPORT`.

Security/reliability notes: the errno remap is unconditional after the call rather than guarded by failure, which relies on normal libc convention that callers inspect errno only when the return value indicates error.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_socket.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_stat.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_stat.c

Read completely: 122 lines.

This implements old `stat`, `fstat`, and `lstat` returning `struct stat12`. Each calls the corresponding `*50` wrapper and converts native `stat` fields into the old layout, including 32-bit device/inode/rdev and 32-bit timestamp seconds.

Important interactions: `st_nlink` is saturated at `32767` if the native link count exceeds the old signed 15-bit range.

Security/reliability notes: field truncation/saturation are intentional compatibility behavior and can hide large native values from old callers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_stat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_statfs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_statfs.c

Read completely: 124 lines.

This implements obsolete `statfs`, `fstatfs`, `fhstatfs`, and `getfsstat` by using current statvfs APIs and converting to `statfs12`. `getfsstat` allocates a temporary native statvfs array sized from the old buffer length, calls `__getvfsstat90`, and converts each returned entry.

Important interactions: warns callers to use statvfs/getvfsstat instead.

Security/reliability notes: `getfsstat` computes allocation size from caller-provided byte size; very large sizes could request large allocations. Conversion may narrow filesystem counters and flags to the old layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_statfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_statvfs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_statvfs.c

Read completely: 121 lines.

This implements compatibility `statvfs`, `statvfs1`, `fstatvfs`, `fstatvfs1`, and `getvfsstat` returning `statvfs90`. Single-object calls use `*190` current APIs and convert the result; `getvfsstat` allocates a native array, calls `__getvfsstat90`, converts each slot, and frees the array.

Security/reliability notes: `getvfsstat` calls `calloc(count, sizeof(*sb))` even when `buf` could conceptually be null; allocation size is derived from caller-provided `size`. Field narrowing is handled by `statvfs_to_statvfs90`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_statvfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_timer.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_timer.c

Read completely: 83 lines.

This implements old `timer_settime` and `timer_gettime` using `itimerspec50`. Set converts optional new and old timer specs around `__timer_settime50`; get calls `__timer_gettime50` and converts the result back.

Security/reliability notes: direct wrapper; null optional pointers are handled.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_timer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_utimes.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_utimes.c

Read completely: 88 lines.

This implements old `utimes`, `lutimes`, and `futimes` using arrays of two `timeval50` values. If the array is non-null, it converts both access and modification times, then calls the corresponding `*50` wrapper; otherwise it forwards null.

Security/reliability notes: array callers must provide two valid entries. Null means “use current time” behavior is preserved.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_utimes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_wait4.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_wait4.c

Read completely: 84 lines.

This implements old `wait3` and `wait4` returning `rusage50`. Both call current `__wait350`/`__wait450` with a native `rusage` temporary when requested, then convert resource usage back on success.

Security/reliability notes: direct process wait wrapper; rusage field narrowing follows the conversion helper.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_wait4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/time/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/time/Makefile.inc

Read completely: 4 lines.

This makefile fragment adds time compatibility sources `compat_asctime.c`, `compat_localtime.c`, and `compat_difftime.c`.

Security/reliability notes: build orchestration only.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/time/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/time/compat_asctime.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/time/compat_asctime.c

Read completely: 33 lines.

This builds compatibility `ctime_r` and `ctime_rz` by redefining `timeval`, `timespec`, and `time_t` to the 50/32-bit compatibility types, then including the shared `time/asctime.c` implementation.

Important interactions: source inclusion reuses the real implementation while compiling it for the old ABI type universe.

Security/reliability notes: inherits behavior from `asctime.c`; timestamp range is limited by `int32_t time_t`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/time/compat_asctime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/time/compat_difftime.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/time/compat_difftime.c

Read completely: 54 lines.

This builds compatibility `difftime` by redefining time-related types to compatibility layouts and including the shared `time/difftime.c`.

Security/reliability notes: the function operates over `int32_t time_t` in this build, so range is the historical ABI range.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/time/compat_difftime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/time/compat_localtime.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/time/compat_localtime.c

Read completely: 91 lines.

This builds many old time APIs, including `gmtime_r`, `localtime_r`, `mktime_z`, `timegm`, `timelocal`, `tzset`, and related conversion helpers, by redefining time types to compatibility layouts and including `time/localtime.c`. Because it must include `<sys/stat.h>` under `__LIBC12_SOURCE__`, it manually declares current `stat`/`fstat` as `__stat50`/`__fstat50` so included timezone code can use current file metadata.

Important interactions: this is a source-level ABI specialization of the shared timezone implementation.

Security/reliability notes: inherits the complexity of `localtime.c`; old callers see 32-bit `time_t` limits even though the included code uses current stat calls internally.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/time/compat_localtime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compiler_rt/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compiler_rt/Makefile.inc

Read completely: 443 lines.

This makefile fragment integrates LLVM compiler-rt builtins and profiling runtime sources into NetBSD libc. It selects CPU/architecture-specific source directories, conditionally adds integer arithmetic, overflow-checking, soft/hard floating-point, complex, quad-precision, cache flush, ARM AEABI, PowerPC, aarch64, and profiling sources, then chooses assembly overrides when present.

Important interactions: adapts upstream compiler-rt source selection to NetBSD libc architecture policy and build flags. It adds many per-source lint suppressions and includes `${COMPILER_RT_DIR}/abi.mk`.

Security/reliability notes: build-only but critical for low-level compiler helper availability. Incorrect architecture conditions can cause missing builtins or ABI-incompatible helper implementations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compiler_rt/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/Makefile.inc

Read completely: 11 lines.

This makefile fragment enables private DB interfaces with `-D__DBINTERFACE_PRIVATE` and includes btree, db, hash, man, mpool, and recno subdirectory makefiles.

Security/reliability notes: build orchestration only; the private-interface define affects which DB internals are exposed during libc build.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/Makefile.inc

Read completely: 8 lines.

This makefile fragment adds Berkeley DB btree source files to libc, including close, conversion, debug, delete, get, open, overflow, page, put, search, sequential, split, and utility modules.

Security/reliability notes: build orchestration only.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_close.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_close.c

Read completely: 181 lines.

This implements btree close and sync. `__bt_close` unpins any cached page, syncs, closes the mpool, frees cursor/result buffers and tree/DB structures, then closes the file descriptor. `__bt_sync` writes metadata if dirty, syncs mpool pages, and clears `B_MODIFIED`; `bt_meta` writes the metadata page fields.

Important interactions: uses mpool for page caching and the `B_MODIFIED`/`B_METADIRTY` flags to decide what must reach disk.

Security/reliability notes: close returns early on sync/mpool errors and may leave ownership with the caller. Metadata writes are raw structure copies into page zero.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_close.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_conv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_conv.c

Read completely: 219 lines.

This implements btree page byte-order conversion for disk I/O. `__bt_pgin` and `__bt_pgout` swap page headers, line pointers, internal/leaf item sizes, child page numbers, and overflow references when `B_NEEDSWAP` is set; `mswap` handles the metadata page.

Important interactions: registered as mpool filters by `bt_open.c` for disk-backed trees with non-native byte order.

Security/reliability notes: conversion walks page internals based on on-page flags and offsets. Corrupt database pages could drive invalid offset interpretation unless higher layers reject them.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_conv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_debug.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_debug.c

Read completely: 379 lines.

This file provides debug and statistics support under `DEBUG` and `STATISTICS`. It initializes a trace file, dumps tree metadata and pages, prints page entries for btree/recno internal and leaf pages, follows overflow references for display, and computes tree statistics such as levels, page counts, free space, cache hits/misses, and split counts.

Important interactions: compiled only for debug/stat builds and uses mpool page access with `MPOOL_IGNOREPIN`.

Security/reliability notes: debug output prints key/data bytes as strings in some paths, so it is not suitable for untrusted binary data diagnostics without care. Not part of normal runtime builds unless enabled.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_delete.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_delete.c

Read completely: 641 lines.

This implements btree deletion. `__bt_delete` handles key deletion and cursor deletion, rejects writes to read-only trees, and marks the tree modified. The helpers delete all duplicates for a key, delete individual leaf items, free overflow chains, relink and free empty pages, collapse root pages back to empty leaves, and adjust cursor state around deleted records.

Important interactions: relies on `__bt_search` to build the parent stack, `__bt_dleaf` for leaf compaction, `__ovfl_delete` for large key/data storage, and mpool for page pinning. Cursor deletion may need `__bt_stkacq` to rebuild the stack when deleting an item from a page found by sequential scan.

Security/reliability notes: mutation is intricate and assumes page metadata and parent stack consistency. A noted edge is old-style page compaction and index adjustment; corrupt page offsets would be dangerous if not filtered earlier.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_delete.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_get.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_get.c

Read completely: 104 lines.

This implements btree lookup `__bt_get`. It unpins any previous page, rejects nonzero flags, searches for the key, returns `RET_SPECIAL` if not exact, and uses `__bt_ret` to return the data.

Important interactions: if `B_DB_LOCK` is set, returned key/data are copied and the page is unpinned; otherwise the found page remains pinned across calls via `bt_pinned`.

Security/reliability notes: page pin lifetime is part of the DB API contract. Callers must not assume returned data outlives the next DB operation unless copied.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_get.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_open.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_open.c

Read completely: 429 lines.

This implements btree open/initialization. It validates `BTREEINFO`, allocates `BTREE` and `DB`, opens a disk or temporary backing file, reads and validates existing metadata or creates new metadata, chooses page/cache sizes, computes overflow thresholds, opens mpool, registers byte-swap filters, creates the root page if needed, and installs DB method pointers.

Important interactions: central setup for all btree operations. It controls byte order, duplicate policy, in-memory mode, read-only mode, mpool cache sizing, and the DB_LOCK/DB_SHMEM/DB_TXN flags.

Security/reliability notes: rejects invalid metadata magic/version/page size/flags with `EFTYPE`. Cache-size rounding and overflow-threshold calculation are guarded with `_DBFIT`, but database file corruption remains a key risk boundary.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_open.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_overflow.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_overflow.c

Read completely: 233 lines.

This implements overflow storage for large btree keys/data. `__ovfl_put` stores a DBT across a linked chain of overflow pages; `__ovfl_get` reads the chain into a reusable buffer; `__ovfl_delete` frees the chain unless the first page is marked `P_PRESERVE`.

Important interactions: leaf/internal items store overflow references as `{pgno_t, uint32_t size}` byte strings. Delete and put paths use these helpers for records larger than the page threshold.

Security/reliability notes: comments note wasted space on the final overflow page and that failed later inserts may leak newly allocated overflow pages. Corrupt overflow chains could cause bad page traversal.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_overflow.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_page.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_page.c

Read completely: 99 lines.

This file manages btree page allocation and freeing. `__bt_free` links a page onto the tree freelist and marks metadata dirty; `__bt_new` prefers reusing the freelist head and falls back to `mpool_new`.

Important interactions: used by delete and overflow code to recycle pages, and by split/insert code to allocate new tree pages.

Security/reliability notes: freelist integrity depends on trusted page `nextpg` links. Freed pages are marked dirty so freelist state persists.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_page.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_put.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_put.c

Read completely: 319 lines.

This implements btree insertion/replacement `__bt_put`. It validates flags/read-only state, stores oversized key/data values on overflow pages, handles cursor replacement, searches for the insertion point with a sorted-input fast path, enforces `R_NOOVERWRITE` and duplicate policy, deletes replaced leaf entries, splits full pages, inserts the new leaf item, updates cursor indexes, and marks the tree modified.

Important interactions: uses `__ovfl_put`, `__bt_search`, `__bt_dleaf`, `__bt_split`, and `bt_fast`. The sorted insertion cache tracks forward/backward append patterns through `bt_order` and `bt_last`.

Security/reliability notes: the source notes that if an insert fails after overflow pages are allocated, those overflow pages are not recovered. Page free-space calculations and split correctness are central to avoiding on-page corruption.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_put.c -->
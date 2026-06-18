# Group Research: group_449_freebsd_src_sources_os_bsd_freebsd_src_sys_sys_soundcard_h_sources_o_7cd59115db7a

Scope: `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/soundcard.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/soundcard.h

## Purpose
`soundcard.h` defines FreeBSD's OSS/VoxWare-compatible public sound device ABI: audio formats, mixer controls, DSP ioctls, MIDI/sequencer events, patch loading structures, and OSSv4 information/control structures.

## Main Interfaces
- FreeBSD-specific audio ioctls include `AIONWRITE`, `AIOGSIZE`, `AIOSSIZE`, `AIOGFMT`, `AIOSFMT`, `AIOGMIX`, `AIOSMIX`, `AIOSTOP`, `AIOSYNC`, and `AIOGCAP`.
- Audio format masks cover mu-law, A-law, IMA ADPCM, signed/unsigned 8/16/24/32-bit PCM, MPEG, AC3, float, native/opposite endian aliases, stereo, full-duplex, and hardware format constraints.
- Classic OSS/VoxWare ioctls cover `/dev/sequencer`, timer control, MIDI, `/dev/dsp`, coprocessor loading/debug messaging, and `/dev/mixer`.
- Defines ABI structs such as `snd_chan_param`, `snd_mix_param`, `snd_capabilities`, `patch_info`, `sysex_info`, `patmgr_info`, `synth_info`, `midi_info`, `audio_buf_info`, `count_info`, `copr_buffer`, `mixer_info`, `oss_sysinfo`, `oss_audioinfo`, `oss_mixerinfo`, `oss_midi_info`, and `oss_card_info`.
- Provides userland sequencer convenience macros for buffering and emitting MIDI voice, channel, sysex, timer, local, and patch events.

## Implementation Notes
The header explicitly warns that ioctl command numbers and types must preserve OSS compatibility. Many definitions are historical aliases or obsolete compatibility names, but remain part of the ABI. Mixer devices use numeric channel IDs and bitmasks, with read/write ioctl constructors. OSSv4 additions extend device discovery, mixer extension metadata, sync groups, cooked mode, peak meters, channel ordering, and global song/name/label controls.

## Dependencies and Constraints
Includes `sys/types.h`, `machine/endian.h`, and `sys/ioccom.h` when ioctl macros are not already present. Consumers depend on exact struct layout, ioctl numbers, endian aliases, and legacy macro names.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/soundcard.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/specialfd.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/specialfd.h

## Purpose
`specialfd.h` defines the small argument ABI for the `__specialfd` syscall.

## Main Interfaces
- `enum specialfd_type` currently identifies `SPECIALFD_EVENTFD` and `SPECIALFD_INOTIFY`.
- `struct specialfd_eventfd` carries an initial counter value and flags.
- `struct specialfd_inotify` carries creation flags.

## Implementation Notes
This is only a public data-contract header; creation and validation happen in syscall implementation code.

## Dependencies and Constraints
No includes. Values are ABI-visible and must remain stable for userland callers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/specialfd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/spigenio.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/spigenio.h

## Purpose
`spigenio.h` defines ioctl structures and commands for the generic SPI device interface.

## Main Interfaces
- `struct spigen_transfer` describes command and data buffers using `struct iovec`.
- `struct spigen_transfer_mmapped` describes command and data lengths in an mmap-backed transfer area.
- Ioctls support normal and mmap transfers plus get/set operations for SPI clock speed and SPI mode.

## Implementation Notes
The command buffer is master-to-slave. The data buffer can be slave-to-master and/or master-to-slave. The mmap form places command data at offset 0 and transfer data immediately after it.

## Dependencies and Constraints
Includes `sys/_iovec.h`. The ioctl namespace uses base character `'S'`; consumers need ioctl macro definitions from their include context.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/spigenio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/splash.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/splash.h

## Purpose
`splash.h` defines a minimal splash image information structure.

## Main Interfaces
- `struct splash_info` exposes width, height, and depth as 32-bit unsigned integers.

## Implementation Notes
This is a compact shared ABI/header for code that needs splash geometry without depending on larger graphics structures.

## Dependencies and Constraints
Includes `sys/types.h` for `uint32_t`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/splash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/stack.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/stack.h

## Purpose
`stack.h` declares kernel stack capture, storage, printing, and tracing interfaces.

## Main Interfaces
- Exposes `struct stack` operations: create, destroy, put, copy, zero, print, compact/long sbuf formatting, and DDB-specific printing.
- `enum stack_sbuf_fmt` selects no formatting, long formatting, or compact formatting.
- `stack_save()` and `stack_save_td()` capture machine-dependent stack traces for the current or specified thread.
- `CTRSTACK()` logs captured stacks to KTR when KTR support is enabled.

## Implementation Notes
The header separates machine-independent stack manipulation from machine-dependent capture routines. If `sys/malloc.h` was included first, it declares `M_STACK`.

## Dependencies and Constraints
Includes `sys/_stack.h`. Forward-declares `struct sbuf` and `struct thread`. KTR support depends on `KTR` build configuration.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/stack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/stat.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/stat.h

## Purpose
`stat.h` defines the FreeBSD file status ABI, file mode/type macros, file flags, timestamp aliases, and userland stat/chmod/mkdir-style function prototypes.

## Main Interfaces
- Declares standard typedefs including `blksize_t`, `blkcnt_t`, `dev_t`, `fflags_t`, `gid_t`, `ino_t`, `mode_t`, `nlink_t`, `off_t`, and `uid_t`.
- Defines current `struct stat` with device, inode, link count, mode, BSD flags, owner IDs, rdev, access/modify/change/birth times, size, blocks, block size, file flags, generation, revision, and spare fields.
- Kernel compatibility structs include `ostat`, `freebsd11_stat`, and `nstat`.
- Defines permission bits, file type bits, `S_IS*()` tests, BSD file flags (`UF_*`, `SF_*`), and timestamp compatibility aliases.
- Declares userland APIs including `stat`, `fstat`, `lstat`, `fstatat`, `chmod`, `fchmodat`, `mkdir`, `mkfifo`, `mknod`, `utimensat`, and flags variants.

## Implementation Notes
The i386 ABI has extra time extension fields. Compatibility structs preserve old layout for legacy syscalls. BSD-visible sections expose file flags, whiteout type checks, and compatibility names such as `st_birthtime`.

## Dependencies and Constraints
Includes `sys/cdefs.h`, `sys/_timespec.h`, and `sys/_types.h`. Non-kernel BSD-visible builds include `sys/time.h`, with a comment noting namespace pollution.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/stat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/stats.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/stats.h

## Purpose
`stats.h` defines FreeBSD's kernel/user statistics blob API: templates, value-of-interest stat specifications, typed storage, histogram and t-digest helpers, serialization, sampling controls, and inline update/fetch wrappers.

## Main Interfaces
- Stat types include VOI state, sum, max, min, histogram, and t-digest.
- Data types cover signed/unsigned 32/64-bit integers, long/unsigned long, fixed-point q32/q64 values, continuous/discrete histogram variants, and clustering t-digest variants.
- Defines typed storage structs for numeric values, histograms, t-digest centroids, t-digest trees, `voistatdata`, `voistatspec`, `statsblob`, `metablob`, and `statsblob_tpl`.
- Constructor macros create common stat specs such as `STATS_VSS_SUM`, `STATS_VSS_MAX`, `STATS_VSS_MIN`, histogram specs, t-digest specs, and user bucket arrays.
- ABI v1 functions allocate templates, add VOI stats, initialize/clone/snapshot/destroy blobs, render blobs to strings, visit blob entries, update VOIs, and fetch stat data pointers.
- Inline ABI-agnostic wrappers expose typed fetch and absolute/relative update helpers for integer, long, and fixed-point values.

## Implementation Notes
The blob ABI records version, endianness, flags, max size, current size, and opaque payload. Iteration uses `sb_visit` flags for first/last callback, VOI, and voistat boundaries. Histogram helpers support linear, exponential, linear-exponential, and user-defined buckets. T-digest helpers use array-based red-black trees, with diagnostic RB trees optionally present.

## Dependencies and Constraints
Includes `sys/limits.h` and conditionally `sys/tree.h` under `DIAGNOSTIC`. Non-kernel builds define `VNET` shims so template code can be shared with userland. Callers must match VOI dtype and stat dtype; typed fetch helpers return `EFTYPE` on mismatches.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/stats.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/statvfs.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/statvfs.h

## Purpose
`statvfs.h` defines the POSIX `statvfs` filesystem capacity/status interface.

## Main Interfaces
- Defines `fsblkcnt_t` and `fsfilcnt_t`.
- `struct statvfs` exposes block counts, file counts, block size, flags, fragment size, filesystem ID placeholder, and maximum name length.
- Defines `ST_RDONLY` and `ST_NOSUID`.
- Declares `statvfs()` and `fstatvfs()`.

## Implementation Notes
The comments distinguish `f_bavail` from `f_bfree`: available space for unprivileged callers versus all free space, including privileged reserves.

## Dependencies and Constraints
Includes `sys/cdefs.h` and `sys/_types.h`. The interface maps filesystem data into POSIX unsigned count types.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/statvfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/stdarg.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/stdarg.h

## Purpose
`stdarg.h` is a minimal wrapper exposing FreeBSD's internal standard-argument definitions.

## Main Interfaces
- Includes `sys/_stdarg.h`.

## Implementation Notes
No types or macros are defined directly here; the header only provides the public include guard and delegates.

## Dependencies and Constraints
Depends entirely on `sys/_stdarg.h`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/stdarg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/stdatomic.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/stdatomic.h

## Purpose
`stdatomic.h` implements the C11 atomic API for FreeBSD across Clang C11 atomics, GCC `__atomic` builtins, and older GCC `__sync` builtins.

## Main Interfaces
- Defines lock-free macros when compiler-provided values exist.
- Defines `memory_order` values, `atomic_thread_fence()`, and `atomic_signal_fence()`.
- Declares atomic integer typedefs for bool, char, short, int, long, long long, C23 char8, char16, char32, wchar, least/fast widths, intptr, uintptr, size, ptrdiff, intmax, and uintmax.
- Provides explicit atomic operations for compare-exchange, exchange, fetch add/sub/and/or/xor, load, and store.
- Provides non-kernel default seq-cst convenience macros and `atomic_flag` operations.

## Implementation Notes
Kernel builds treat atomics as always lock-free and intentionally omit the non-explicit convenience operations to encourage explicit memory ordering. The fallback `__sync` path wraps values in `.__val` and uses full-barrier or compatibility primitives.

## Dependencies and Constraints
Includes `sys/cdefs.h` and `sys/_types.h`. Unsupported compilers fail with a preprocessor error. C++ builds temporarily map `_Bool` to `bool` if needed.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/stdatomic.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/stddef.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/stddef.h

## Purpose
`stddef.h` provides minimal FreeBSD standard definitions around null, offsetof, and pointer difference/address types.

## Main Interfaces
- Includes `NULL` and `offsetof` providers.
- Defines `ptraddr_t` when BSD-visible.
- Defines `ptrdiff_t`.

## Implementation Notes
The header avoids redefining typedefs by using `_PTRADDR_T_DECLARED` and `_PTRDIFF_T_DECLARED` guards.

## Dependencies and Constraints
Includes `sys/cdefs.h`, `sys/_null.h`, `sys/_offsetof.h`, `sys/_types.h`, and `sys/_visible.h`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/stddef.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/stdint.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/stdint.h

## Purpose
`stdint.h` defines FreeBSD's standard integer least/fast typedefs and related portability macros.

## Main Interfaces
- Imports machine and generic fixed-width integer definitions.
- Defines `int_least*`, `uint_least*`, `int_fast*`, and `uint_fast*` typedefs.
- Defines GNU/Darwin-compatible `__WORDSIZE`.
- Defines `WCHAR_MIN`, `WCHAR_MAX`, optional C11 Annex K `RSIZE_MAX`, and C23 integer width macros.

## Implementation Notes
The width macros are exposed only when `__ISO_C_VISIBLE >= 2023`. `RSIZE_MAX` is exposed under `__EXT1_VISIBLE`.

## Dependencies and Constraints
Includes `sys/cdefs.h`, `sys/_types.h`, `machine/_stdint.h`, and `sys/_stdint.h`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/stdint.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sx.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/sx.h

## Purpose
`sx.h` defines the kernel sleepable shared/exclusive lock API and lock-word encoding.

## Main Interfaces
- Lock state flags include shared/exclusive state, shared waiters, exclusive waiters, write spinner, recursion, waiter mask, owner extraction, and shared-holder count encoding.
- Declares initialization, destruction, try-lock, lock, unlock, upgrade, downgrade, assertion, and DDB owner-chain routines.
- `SX_SYSINIT` and `SX_SYSINIT_FLAGS` register static sx locks with SYSINIT/SYSUNINIT.
- Public macros expose `sx_xlock`, `sx_xlock_sig`, `sx_xunlock`, `sx_slock`, `sx_slock_sig`, `sx_sunlock`, `sx_try_*`, `sx_downgrade`, `sx_unlock`, `sx_sleep`, and `sx_assert`.

## Implementation Notes
The comments compare sx locks with rwlocks: sx uses sleep queues and lacks priority propagation, while rwlocks use turnstiles. Non-debug kernels inline exclusive lock/unlock fast paths with atomic compare-and-set and defer contention to hard routines. `_STANDALONE` builds provide no-op boot-loader versions.

## Dependencies and Constraints
Includes `sys/_lock.h` and `sys/_sx.h`; kernel builds also include pcpu, lock profiling/stat, and machine atomics. Kernel use requires `LOCK_DEBUG` from `sys/lock.h`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/syscall.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/syscall.h

## Purpose
`syscall.h` is the generated FreeBSD system call number table.

## Main Interfaces
- Maps syscall names to numeric IDs from `SYS_syscall` 0 through `SYS_renameat2` 602.
- Defines `SYS_exit` as `SYS__exit`.
- Includes active, compatibility, obsolete-commented, and FreeBSD-versioned syscall names.
- Filesystem/VFS-relevant entries include `mount`, `unmount`, `stat`, `fstat`, `statfs`, `getfsstat`, `fhopen`, `fhstat`, `openat`, `linkat`, `renameat`, `unlinkat`, `copy_file_range`, `fspacectl`, `getfhat`, `fhlink`, `funlinkat`, and many compatibility forms.
- Defines `SYS_MAXSYSCALL` as 603.

## Implementation Notes
The file is marked automatically generated and should not be edited directly. Commented holes preserve historical syscall number positions.

## Dependencies and Constraints
No includes. ABI stability depends on syscall numbers remaining consistent with the generated syscall switch, libc stubs, and syscall object list.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/syscall.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/syscall.mk -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/syscall.mk

## Purpose
`syscall.mk` is the generated makefile fragment listing machine-independent syscall stub object files.

## Main Interfaces
- Defines `MIASM` as a backslash-continued list of syscall `.o` files.
- Covers ordinary syscalls, compatibility syscall objects, capability mode calls, VFS/filesystem operations, IPC, networking, threading, jail, audit, POSIX AIO, timerfd, inotify, and recent process-descriptor calls.

## Implementation Notes
The order and names mirror generated syscall definitions. Obsolete or unimplemented syscall numbers do not appear as build objects.

## Dependencies and Constraints
Marked automatically generated and not intended for manual edits. Build correctness depends on consistency with the syscall master source and generated headers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/syscall.mk -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/syscallsubr.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/syscallsubr.h

## Purpose
`syscallsubr.h` declares kernel-internal syscall helper routines used by syscall entry points and compatibility wrappers.

## Main Interfaces
- Declares `struct mmap_req` for normalized `mmap` requests and optional file-permission checking callback.
- Provides prototypes for process, signal, scheduler, socket, IPC, jail, capability, kqueue, AIO, timer, VM, and file-descriptor operations.
- VFS/filesystem-facing helpers include `kern_openat`, `kern_openatfp`, `kern_statat`, `kern_statfs`, `kern_fstatfs`, `kern_getfsstat`, `kern_getdirentries`, `kern_getfhat`, `kern_fhopen`, `kern_fhstat`, `kern_fhstatfs`, `kern_linkat`, `kern_renameat`, `kern_symlinkat`, `kern_readlinkat`, `kern_mkdirat`, `kern_mkfifoat`, `kern_mknodat`, `kern_funlinkat`, `kern_frmdirat`, `kern_ftruncate`, `kern_truncate`, `kern_fspacectl`, `kern_copy_file_range`, `kern_posix_fadvise`, and `kern_posix_fallocate`.
- Declares user cpuset copy helpers and legacy `freebsd11_kern_getdirentries`.

## Implementation Notes
The header centralizes normalized kernel entry points so syscall wrappers can handle ABI/user-copy details while shared logic lives in `kern_*` routines. Many parameters carry `enum uio_seg` to distinguish user and kernel address spaces.

## Dependencies and Constraints
Includes `sys/types.h`, cpuset/domainset/uio internals, MAC, mount, signal, and socket headers. Forward declarations keep the header broad but avoid pulling every subsystem definition.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/syscallsubr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sysctl.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/sysctl.h

## Purpose
`sysctl.h` defines the FreeBSD sysctl MIB ABI and kernel registration framework for hierarchical tunables, statistics, and information nodes.

## Main Interfaces
- Defines sysctl type bits, access flags, security flags, tunable/statistics flags, capability-mode flags, and `OID_AUTO`.
- Kernel structures include `sysctl_req`, `sysctl_oid`, RB-tree `sysctl_oid_list`, and dynamic context tracking via `sysctl_ctx_list`.
- Declares generic handlers for bool, integer widths, long, string, opaque data, counters, UMA zone values, time conversions, and per-CPU values.
- Static and dynamic registration macros create root nodes, nodes, strings, const strings, bools, signed/unsigned integer widths, long/ulong, quad/uquad, counters, counter arrays, opaque data, structs, procedures, UMA zone controls, time conversions, feature flags, and `debug.sizeof` entries.
- Top-level numeric identifiers cover `CTL_SYSCTL`, `CTL_KERN`, `CTL_VM`, `CTL_VFS`, `CTL_NET`, `CTL_DEBUG`, `CTL_HW`, `CTL_MACHDEP`, `CTL_USER`, and `CTL_P1003_1B`.
- Userland declares `sysctl()`, `sysctlbyname()`, and `sysctlnametomib()`.

## Implementation Notes
Kernel OIDs are stored in linker sets for static registration and in RB trees for sibling lookup. Macros use compile-time assertions to check declared type, pointee size, and writeability constraints. `CTLFLAG_MPSAFE` versus `CTLFLAG_NEEDGIANT` enforcement is present but disabled behind `notyet`.

## Dependencies and Constraints
Kernel builds include queue/tree/linker-set and assert infrastructure; userland builds include `sys/cdefs.h` and `sys/_types.h`. Dynamic OIDs can be tracked in contexts for cleanup. The `CTL_VFS` top-level ID is the namespace root for filesystem sysctls.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/sysctl.h -->
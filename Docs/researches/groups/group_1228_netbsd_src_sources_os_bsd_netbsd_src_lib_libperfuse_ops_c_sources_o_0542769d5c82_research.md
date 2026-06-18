# Group Research: group_1228_netbsd_src_sources_os_bsd_netbsd_src_lib_libperfuse_ops_c_sources_o_0542769d5c82

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/netbsd-src`, so every file below is in-scope. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libperfuse/ops.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libperfuse/ops.c

## Purpose
Implements the PUFFS vnode/filesystem operation layer for `libperfuse`, translating NetBSD PUFFS callbacks into FUSE protocol requests and replies.

## Main Responsibilities
- Filesystem operations: init, unmount, statvfs, sync, pathconf, suspend, unimplemented fh conversions.
- Node operations: lookup, create, mknod, open/close, access, getattr/setattr, poll, fsync, remove/link/rename, mkdir/rmdir/symlink, readdir, readlink, reclaim/inactive, read/write, advlock, extattr, fallocate.
- Converts FUSE attributes and directory entries to NetBSD `vattr` and `dirent`.
- Tracks FUSE node ids, lookup counts, file handles, dirty state, removed/reclaimed state, and per-node request queues.
- Serializes sensitive operations with `requeue_request` / `dequeue_requests`: open, resize/getattr/setattr/write size updates, readdir buffering, after-write, after-FUSE-exchange, and reclaim references.

## Key Implementation Notes
- `xchg_msg()` is the central FUSE exchange wrapper. It increments global/per-node in-flight counters, optionally traces calls, destroys failed messages, and wakes operations waiting for `PCQ_AFTERXCHG`.
- `node_lookup_common()` sends `FUSE_LOOKUP`, reuses cached nodes by FUSE nodeid, handles ABI 7.4 negative lookup `ino == 0`, fills PUFFS newinfo, and increments FUSE/PUFFS lookup counters.
- `perfuse_node_create()` prefers `FUSE_CREATE`, caches `ENOSYS` as `PS_NO_CREAT`, then falls back to `mknod + open`.
- `perfuse_node_access()` normally uses local `puffs_access` emulation because `PS_NO_ACCESS` is set by default elsewhere; it can probe `FUSE_ACCESS` when enabled.
- `perfuse_node_setattr_ttl()` has detailed permission checks and special handling for resize plus chmod on open handles to avoid remote filesystem ordering failures.
- `perfuse_node_readdir()` reads all FUSE directory entries into a FUSE buffer, converts to native `dirent`, buffers output on the node, and serializes concurrent readdir on a node.
- `perfuse_node_reclaim2()` manages FUSE `FORGET`, lookup counters, cache removal, queued-operation drainage, and final `perfuse_destroy_pn`.
- Read/write split large transfers by `ps_max_readahead` / `ps_max_write`; write updates cached size, dirty flags, and sync statistics.
- Extended attributes map NetBSD user/system namespaces to Linux/FUSE xattr names via helpers in `subr.c`.

## Dependencies
- Internal: `perfuse_priv.h`, `fuse.h`, node/cache/file-handle helpers from `subr.c`, callbacks registered in `perfuse.c`.
- External: PUFFS, FUSE protocol structs, NetBSD vnode-style access helpers and extattr definitions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libperfuse/ops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libperfuse/perfuse.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libperfuse/perfuse.c

## Purpose
Provides the public `libperfuse` mount/open shim and initializes a PUFFS usermount backed by FUSE protocol callbacks.

## Main Responsibilities
- Wraps `open("/dev/fuse")` through `perfuse_open()`, connecting to a running `perfused` daemon or spawning `/usr/sbin/perfused`.
- Wraps `mount()` through `perfuse_mount()`, sending a `perfuse_mount_out` frame over the FUSE/perfused communication fd.
- Initializes `struct perfuse_state`, nodeid hash tables, defaults, environment options, and resource limits.
- Registers all `ops.c` filesystem and node operations with PUFFS.
- Creates and caches the root PUFFS node with FUSE root nodeid.
- Provides mainloop, private data accessors, nodeid accessor, forced unmount, unique id allocation, and async filesystem reply handling.

## Key Implementation Notes
- `init_state()` defaults `PS_NO_ACCESS` because some FUSE filesystems perform `access()` checks with incorrect credentials; `PERFUSE_OPTIONS` can enable/disable access and create behavior.
- `perfuse_open()` uses local sockets, preferring `SOCK_SEQPACKET` and falling back to datagrams with a warning.
- `perfuse_init()` sets `MNT_NOSUID|MNT_NODEV` for non-root owners and chooses PUFFS name cache behavior based on TTL support.
- `perfuse_fsreq()` handles fire-and-forget replies, ignoring success and `ENOENT`, warning on connection/transient errors, and warning on unexpected frames.

## Dependencies
- Public API from `perfuse.h` / `perfuse_if.h`.
- Private structures and node helpers from `perfuse_priv.h`.
- PUFFS operation registration macros and mount/mainloop APIs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libperfuse/perfuse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libperfuse/perfuse.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libperfuse/perfuse.h

## Purpose
Public wrapper header for applications using `libperfuse` as a FUSE compatibility layer.

## Main Responsibilities
- Declares `perfuse_open()` and `perfuse_mount()`.
- When `LIBPERFUSE` is not defined, macro-replaces `mount()` and `open()` with perfuse wrappers.
- Keeps the wrapper small and independent of private perfuse internals.

## Dependencies
- Includes `sys/cdefs.h` and `sys/types.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libperfuse/perfuse.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libperfuse/perfuse_if.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libperfuse/perfuse_if.h

## Purpose
Defines the public/internal callback interface between perfuse core code and a FUSE frame transport implementation.

## Main Responsibilities
- Defines paths and protocol constants such as `_PATH_FUSE`, `_PATH_PERFUSED`, `PERFUSE_MOUNT_MAGIC`, unknown inode/nodeid sentinels.
- Defines diagnostic flags and logging/error macros.
- Defines `perfuse_msg_t`, exchange reply modes, callback function pointer types, and `struct perfuse_callbacks`.
- Defines mount request metadata in `struct perfuse_mount_out` and `struct perfuse_mount_info`.
- Duplicates minimal FUSE input/output header definitions to avoid exposing full private `fuse.h`.
- Declares public perfuse lifecycle and helper APIs.

## Key Implementation Notes
- Diagnostics can print foreground, syslog, FUSE/PUFFS frames, file handles, readdir, sync, resize, trace, and queue events.
- `DERR`/`DERRX` abort in foreground mode but use `err`/`errx` otherwise.

## Dependencies
- PUFFS types and minimal FUSE header layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libperfuse/perfuse_if.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libperfuse/perfuse_priv.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libperfuse/perfuse_priv.h

## Purpose
Private `libperfuse` state, node metadata, queue types, macros, and operation prototypes.

## Main Responsibilities
- Defines `struct perfuse_state`, including mount metadata, counters, feature flags, callback table, trace queue, nodeid hash table, and PUFFS root.
- Defines `struct perfuse_node_data`, including read/write FUSE file handles, FUSE nodeid, parent nodeid, lookup counters, lock owner, readdir buffers, queued continuations, flags, cached name, and in-flight counters.
- Defines per-node queue types for readdir, read/write, open, resize, ref, and post-exchange waits.
- Provides payload/header accessor macros around callback methods.
- Declares all private helpers and operation entry points implemented in `ops.c` and `subr.c`.

## Key Flags
- State: `PS_NO_ACCESS`, `PS_NO_CREAT`, `PS_INLOOP`, `PS_NO_FALLOCATE`.
- Node: `PND_RECLAIMED`, `PND_INREADDIR`, `PND_DIRTY`, `PND_RFH`, `PND_WFH`, `PND_REMOVED`, `PND_INWRITE`, `PND_INOPEN`, `PND_INVALID`, `PND_INRESIZE`.

## Dependencies
- `perfuse_if.h`, private FUSE protocol definitions, PUFFS.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libperfuse/perfuse_priv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libperfuse/subr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libperfuse/subr.c

## Purpose
Utility implementation for perfuse node lifecycle, file-handle management, nodeid cache, and xattr namespace translation.

## Main Responsibilities
- Allocates and initializes PUFFS nodes plus `perfuse_node_data`.
- Destroys nodes, freeing readdir buffers and private data.
- Creates, destroys, and resolves read/write FUSE file handles on nodes.
- Provides a simple node path/name helper.
- Maps NetBSD extattr namespaces to Linux/FUSE xattr prefixes and filters listed xattrs.
- Maintains a hash table from FUSE nodeid to `perfuse_node_data`.

## Key Implementation Notes
- New nodes default file handles to `FUSE_UNKNOWN_FH` and parent nodeid to the parent’s FUSE nodeid or root.
- `perfuse_get_fh()` can use a write handle for reads when no read handle exists.
- `perfuse_node_cache()` inserts node data into the nodeid hash; `perfuse_cache_flush()` removes it.
- Xattr translation preserves matching reserved prefixes, prepends `user.` for user access to reserved-looking names, and prepends `system.` for system namespace names without a reserved prefix.

## Dependencies
- PUFFS node allocation APIs.
- `sys/hash.h` for nodeid hashing.
- `perfuse_priv.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libperfuse/subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libposix/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libposix/Makefile

## Purpose
Builds the NetBSD `libposix` library, which supplies POSIX-specific replacement routines over libc behavior.

## Main Responsibilities
- Sets `LIB=posix`.
- Adds `_REENTRANT`, libc include, and kernel syscall include paths.
- Includes libc include setup and `sys/Makefile.inc`.
- Adds `_errno.c` from libc for `powerpc64`.
- Builds with standard `bsd.lib.mk`.

## Dependencies
- `bsd.own.mk`, libc include makefile fragments, `libposix/sys/Makefile.inc`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libposix/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libposix/sys/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libposix/sys/Makefile.inc

## Purpose
Generates syscall wrapper stubs for `libposix`.

## Main Responsibilities
- Adds `.PATH` entries for generic and architecture syscall sources.
- Generates pseudo assembly stubs for `chown`, `fchown`, `lchown`, and `rename`, each calling the corresponding `__posix_*` symbol.
- Builds `cerror.S` with `__cerror` remapped to `__posix_cerror`.
- Defines dependencies on `SYS.h` and generated syscall headers.
- Generates lint stubs when lint is enabled.

## Dependencies
- libc object directory, architecture `SYS.h`, `sys/syscall.h`, libc `makelintstub`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libposix/sys/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libppath/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libppath/Makefile

## Purpose
Builds the `libppath` property-path helper library.

## Main Responsibilities
- Includes common library sources from `common/lib/libppath/Makefile.inc`.
- Adds local allocator adapter `ppath_malloc.c`.
- Links against `libprop`.
- Installs `ppath` manual pages and extensive MLINK aliases for component, path, bool, number, and object operations.
- Uses shared library directory and warning level 5.

## Dependencies
- Common `libppath` source makefile.
- `libprop`.
- `bsd.lib.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libppath/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libppath/ppath_malloc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libppath/ppath_malloc.c

## Purpose
Provides allocation hooks for `libppath`.

## Main Responsibilities
- Implements `ppath_alloc(size_t)` as zero-initializing `calloc(1, size)`.
- Implements `ppath_free(void *, size_t)` as `free(p)`, ignoring size.

## Dependencies
- `stdlib.h`.
- Internal `ppath/ppath_impl.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libppath/ppath_malloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libprop/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libprop/Makefile

## Purpose
Builds NetBSD `libprop`, the property container/object library.

## Main Responsibilities
- Includes shared source definitions from `common/lib/libprop/Makefile.inc`.
- Builds with `_LIBPROP`, `_REENTRANT`, libc-private includes, hidden symbol visibility, and shared library installation.
- Defines `LIB=prop`.
- Installs manuals and many MLINK aliases for arrays, dictionaries, bools, data, numbers, strings, object iteration, externalization/internalization, utility getters/setters, ioctl/syscall send/recv helpers, and ingest APIs.

## Dependencies
- Common `libprop` source tree.
- `bsd.lib.mk`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libprop/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/Makefile

## Purpose
Builds NetBSD `libpthread`, including machine-dependent thread support and ISO C11 threads wrappers.

## Main Responsibilities
- Selects architecture subdirectory from `PTHREAD_MACHINE_ARCH`, `PTHREAD_MACHINE_CPU`, `MACHINE_ARCH`, or `MACHINE_CPU`.
- Builds export symbol list from MI and MD symbol files.
- Sets libc/threading CPP flags and includes libc internals.
- Prevents libpthread unloading with linker `-z nodelete`.
- Builds core pthread source files, scheduler/cancel/mutex/cond/rwlock/spin/barrier/TSD code, semaphore code from librt, and optional MD assembly.
- Supports `PTHREAD__COMPAT` for NetBSD 2/3/4 chroots on newer kernels.
- Adds C11 thread sources: `call_once.c`, `cnd.c`, `mtx.c`, `thrd.c`, `tss.c`.
- Creates static `libpthread.a` as a single large relocatable object so linking any pthread symbol pulls in all pthread functionality.
- Installs pthread and C11 thread headers and extensive manpage MLINKs.

## Key Implementation Notes
- The file emphasizes that new libpthread source files must be referenced from `pthread.c` to avoid static archive discard.
- Alpha and hppa use MD RAS assembly exports; other architectures export MI RAS symbols.

## Dependencies
- Architecture-specific `arch/*/pthread_md.*`.
- `pthread_int.h`, pthread source modules, libc internals, librt `sem.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/aarch64/pthread_md.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/aarch64/pthread_md.h

## Purpose
AArch64 machine-dependent pthread helpers.

## Main Responsibilities
- Defines `pthread__sp()` using inline assembly `mov ..., sp`.
- Defines SMT wait/wake with `wfe` and `sev`.
- Defines ucontext stack pointer access via `_REG_SP`.
- Initializes user context SPSR to zero.

## Dependencies
- AArch64 register names in NetBSD ucontext/mcontext headers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/aarch64/pthread_md.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/alpha/pthread_md.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/alpha/pthread_md.S

## Purpose
Alpha assembly implementation of restartable-atomic-sequence simple lock operations for libpthread.

## Main Responsibilities
- Implements `pthread__ras_simple_lock_init`.
- Implements `pthread__ras_simple_lock_try` with exported `pthread__lock_ras_start` and `pthread__lock_ras_end` labels.
- Implements `pthread__ras_simple_unlock`.

## Key Implementation Notes
- Lock state is stored as integer zero/nonzero.
- The RAS labels allow the kernel/runtime to recognize and restart the critical sequence.

## Dependencies
- Alpha assembler conventions via `machine/asm.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/alpha/pthread_md.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/alpha/pthread_md.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/alpha/pthread_md.h

## Purpose
Alpha machine-dependent pthread helpers.

## Main Responsibilities
- Enables `PTHREAD__ASM_RASOPS`.
- Defines `pthread__sp()` from register `$30`.
- Defines ucontext stack pointer access via `_REG_SP`.
- Initializes processor status register to Alpha user value `0x0008`.

## Dependencies
- Alpha mcontext register layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/alpha/pthread_md.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/arm/pthread_md.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/arm/pthread_md.h

## Purpose
ARM machine-dependent pthread helpers.

## Main Responsibilities
- Defines `pthread__sp()` using `sp`.
- Defines SMT wait/wake as WFE/SEV encodings for ARM/Thumb where available, otherwise no-op.
- Defines ucontext stack pointer access via `_REG_SP`.
- Initializes CPSR to user 32-bit mode `0x10`.

## Dependencies
- ARM register layout and compiler mode macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/arm/pthread_md.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/hppa/pthread_md.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/hppa/pthread_md.S

## Purpose
HPPA assembly implementation of libpthread RAS simple lock operations.

## Main Responsibilities
- Initializes a 16-byte lock area as unlocked.
- Implements aligned RAS lock try using `RAS_START_ASM_HIDDEN` / `RAS_END_ASM_HIDDEN`.
- Implements unlock by storing unlocked state.

## Key Implementation Notes
- Uses HPPA register and branch-delay conventions.
- Lock is aligned to a 16-byte boundary before operating.

## Dependencies
- `sys/ras.h`, `machine/asm.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/hppa/pthread_md.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/hppa/pthread_md.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/hppa/pthread_md.h

## Purpose
HPPA machine-dependent pthread helpers.

## Main Responsibilities
- Enables `PTHREAD__ASM_RASOPS`.
- Defines `pthread__sp()` from register `r30`.
- Defines ucontext stack pointer access via `_REG_SP`.
- Initializes PSW to `0x4000f`.
- Defines `STACKSPACE` as `HPPA_FRAME_SIZE`.
- Marks pthread atomics as already memory-barrier-safe.

## Dependencies
- `machine/frame.h` and HPPA mcontext layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/hppa/pthread_md.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/i386/pthread_md.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/i386/pthread_md.h

## Purpose
i386 machine-dependent pthread helpers.

## Main Responsibilities
- Defines `pthread__sp()` from `%esp`.
- Defines ucontext stack pointer access via `_REG_UESP`.
- Initializes user context flags and segment registers from current CPU state.
- Defines SMT pause/wait as `rep; nop`.
- Marks atomics as memory-barrier-safe.
- Provides inline pointer compare-and-swap with locked and non-interlocked variants.

## Dependencies
- i386 ucontext register layout and inline x86 assembly.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/i386/pthread_md.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/ia64/pthread_md.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/ia64/pthread_md.h

## Purpose
IA-64 machine-dependent pthread helper stub.

## Main Responsibilities
- Provides placeholder `pthread__sp()` returning zero.
- Defines ucontext stack pointer access via `_REG_SP`.
- Leaves `PTHREAD__ASM_RASOPS` commented out.

## Dependencies
- IA-64 mcontext register layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/ia64/pthread_md.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/m68k/pthread_md.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/m68k/pthread_md.h

## Purpose
m68k machine-dependent pthread helpers.

## Main Responsibilities
- Defines `pthread__sp()` from `%sp`.
- Defines ucontext stack pointer access via `_REG_A7`.
- Marks atomics as memory-barrier-safe because m68k is not expected to be SMP.

## Dependencies
- m68k mcontext register layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/m68k/pthread_md.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/mips/pthread_md.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/mips/pthread_md.h

## Purpose
MIPS machine-dependent pthread helpers.

## Main Responsibilities
- Defines `pthread__sp()` from `$sp`.
- Defines ucontext stack pointer access via `_REG_SP`.

## Dependencies
- MIPS mcontext register layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/mips/pthread_md.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/or1k/pthread_md.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/or1k/pthread_md.h

## Purpose
OpenRISC/or1k machine-dependent pthread helpers.

## Main Responsibilities
- Defines `pthread__sp()` with inline assembly currently loading zero via `l.ori`.
- Defines ucontext stack pointer access as general register index `1`.

## Dependencies
- or1k mcontext layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/or1k/pthread_md.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/powerpc/pthread_md.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/powerpc/pthread_md.h

## Purpose
PowerPC machine-dependent pthread helpers.

## Main Responsibilities
- Defines `pthread__sp()` from register `r1`.
- Defines ucontext stack pointer access as general register index `1`.
- Initializes MSR to user value `0xd032`.

## Dependencies
- PowerPC mcontext register layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/powerpc/pthread_md.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/riscv/pthread_md.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/riscv/pthread_md.h

## Purpose
RISC-V machine-dependent pthread helpers.

## Main Responsibilities
- Defines `pthread__sp()` from `sp`.
- Defines ucontext stack pointer access via `_REG_SP`.

## Dependencies
- RISC-V mcontext register layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/riscv/pthread_md.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/sh3/pthread_md.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/sh3/pthread_md.h

## Purpose
SH3 machine-dependent pthread helpers.

## Main Responsibilities
- Defines `pthread__sp()` from `r15`.
- Defines ucontext stack pointer access via `_REG_R15`.
- Initializes status register to zero.
- Marks atomics as memory-barrier-safe because SH3 is not expected to be SMP.

## Dependencies
- SH3 mcontext register layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/sh3/pthread_md.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/sparc/pthread_md.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/sparc/pthread_md.h

## Purpose
SPARC machine-dependent pthread helpers.

## Main Responsibilities
- Defines `pthread__sp()` from `%sp`.
- Defines ucontext stack pointer access via `_REG_O6`.
- Marks atomics as memory-barrier-safe.

## Dependencies
- SPARC mcontext register layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/sparc/pthread_md.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/sparc64/pthread_md.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/sparc64/pthread_md.h

## Purpose
SPARC64 machine-dependent pthread helpers.

## Main Responsibilities
- Defines `pthread__sp()` from `%sp`.
- Defines ucontext stack pointer access via `_REG_O6`.

## Dependencies
- SPARC64 mcontext register layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/sparc64/pthread_md.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/vax/pthread_md.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/vax/pthread_md.h

## Purpose
VAX machine-dependent pthread helpers.

## Main Responsibilities
- Defines `pthread__sp()` from `%sp`.
- Defines ucontext stack pointer access via `_REG_SP`.
- Initializes PSL to user value `0x03c00000`.
- Marks atomics as memory-barrier-safe.

## Dependencies
- VAX mcontext register layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/vax/pthread_md.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/x86_64/pthread_md.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/arch/x86_64/pthread_md.h

## Purpose
x86_64 machine-dependent pthread helpers.

## Main Responsibilities
- Defines `pthread__sp()` from `%rsp`.
- Defines ucontext stack pointer access via `_REG_URSP`.
- Initializes user context segment registers and flags.
- Defines SMT pause/wait as `rep; nop`.
- Marks atomics as memory-barrier-safe.
- Provides inline pointer compare-and-swap with locked and non-interlocked variants.

## Dependencies
- x86_64 ucontext register layout and inline assembly.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/arch/x86_64/pthread_md.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/call_once.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/call_once.c

## Purpose
Implements the C11 `call_once()` API on top of POSIX pthread once control.

## Main Responsibilities
- Validates non-null arguments with `_DIAGASSERT`.
- Calls `pthread_once(flag, func)`.
- Ignores the pthread return value because C11 `call_once` returns `void`.

## Dependencies
- `pthread.h`, `threads.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/call_once.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/cnd.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/cnd.c

## Purpose
Implements C11 condition variable APIs over pthread condition variables.

## Main Responsibilities
- Maps `cnd_broadcast`, `cnd_signal`, `cnd_wait`, and `cnd_timedwait` to pthread condition APIs.
- Maps `cnd_init` and `cnd_destroy` to pthread condition init/destroy.
- Converts pthread return codes to C11 `thrd_success`, `thrd_error`, or `thrd_timedout`.

## Dependencies
- `pthread.h`, `threads.h`, `errno.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/cnd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/compat/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/compat/Makefile.inc

## Purpose
Adds libpthread compatibility sources to the build.

## Main Responsibilities
- Sets `COMPAT` to the parsed directory.
- Adds compatibility directory to `.PATH.c`.
- Adds `compat_pthread_setname_np.c` to sources.
- Adds include path and suppresses nonliteral format warnings for that compatibility source.

## Dependencies
- Included by the broader libpthread build when compatibility support is desired.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/compat/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/compat/compat_pthread_setname_np.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/compat/compat_pthread_setname_np.c

## Purpose
Provides ABI compatibility for older `pthread_setname_np` references.

## Main Responsibilities
- Includes compatibility pthread declarations under `__LIBC12_SOURCE__`.
- Emits a warning reference advising inclusion of `<pthread.h>` for the correct reference.
- Defines `pthread_setname_np` as a strong alias of `__compat_pthread_setname_np`.
- Implements `__compat_pthread_setname_np()` by forwarding to `__pthread_setname_np120(thread, name, arg)`.

## Dependencies
- Local `compat/pthread.h`.
- NetBSD symbol alias and warning-reference macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/compat/compat_pthread_setname_np.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/compat/pthread.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/compat/pthread.h

## Purpose
Minimal compatibility header for the old `pthread_setname_np` ABI wrapper.

## Main Responsibilities
- Includes `sys/mutex.h` and `pthread_types.h`.
- Declares hidden `__compat_pthread_setname_np`.
- Declares variadic `__pthread_setname_np120`.

## Dependencies
- NetBSD pthread type definitions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/compat/pthread.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/mtx.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/mtx.c

## Purpose
Implements C11 mutex APIs over pthread mutexes.

## Main Responsibilities
- Maps destroy, lock, timedlock, trylock, and unlock to pthread mutex APIs.
- Implements plain/timed mutex init with default pthread mutex attributes.
- Implements recursive mutex init with `PTHREAD_MUTEX_RECURSIVE`.
- Converts pthread return codes to C11 `thrd_success`, `thrd_error`, `thrd_timedout`, or `thrd_busy`.

## Key Implementation Notes
- `mtx_destroy()` ignores pthread destroy return because C11 destroy returns `void`.
- `mtx_init()` accepts `mtx_plain`, `mtx_timed`, and each combined with `mtx_recursive`.

## Dependencies
- `pthread.h`, `threads.h`, `errno.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/mtx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread.c

## Purpose
Core NetBSD pthread runtime implementation: initialization, thread creation/exit/join, cancellation, thread identity, diagnostics, park/unpark, fork handling, stack setup, and global thread tracking.

## Main Responsibilities
- Initializes libpthread state in `pthread__init()`: TSD storage, libc threading switch, page/CPU/guard sizes, locks, queues, all-thread tree, main thread, LWP control, MD init, diagnostic options, and atfork handlers.
- Implements `pthread_create()` using stack allocation/reuse, TLS allocation, thread struct initialization, and `pthread__makelwp()`.
- Implements `pthread_exit()`, cleanup handler execution, C++ thread atexit execution, TSD destruction, malloc cleanup, zombie/dead state transitions, and LWP exit.
- Implements `pthread_join()`, `pthread_detach()`, `pthread_equal()`, `pthread_self()`, `pthread_main_np()`.
- Implements thread naming via `pthread_getname_np()` and `pthread_setname_np()`.
- Implements cancellation: `pthread_cancel`, cancel state/type setters, `pthread_testcancel`, and internal cancellation transition helpers.
- Maintains global all-thread rb-tree for validation/search and dead-thread queue for reuse.
- Provides internal assertion/error reporting avoiding lock-taking stdio paths.
- Implements `_lwp_park` / `_lwp_unpark` wrappers for pthread blocking queues.
- Initializes main thread stack from auxinfo and stack resource limits.
- Provides lock hash selection and scheduling priority validation.

## Key Implementation Notes
- Strong aliases connect libc thread stubs to real pthread functions once libpthread is linked.
- Static library binder references force inclusion of key pthread object files.
- `pthread_create()` primes `_lwp_park` before first created thread to avoid lazy rtld symbol-resolution consuming a wakeup intended for libpthread.
- Dead thread structures may be reused only after `_lwp_kill(lid, 0)` confirms the LWP no longer exists.
- Cancellation state is maintained with atomics and release/acquire barriers: `pthread_cancel()` publishes cancellation, cancellation tests acquire only on the slow path.
- `pthread__find()` uses the all-thread rb-tree to validate pthread handles and avoid accepting dead thread ids.
- `pthread__getenv()` scans `environ` directly to avoid calling lock-using `getenv()` during early pthread initialization.

## Dependencies
- NetBSD LWP syscalls and LWP control.
- TLS/rtld hooks, libc private threading stubs, atomic namespace headers.
- `pthread_int.h`, `pthread_makelwp.h`, `reentrant.h`, machine-dependent pthread macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpthread/pthread.c -->
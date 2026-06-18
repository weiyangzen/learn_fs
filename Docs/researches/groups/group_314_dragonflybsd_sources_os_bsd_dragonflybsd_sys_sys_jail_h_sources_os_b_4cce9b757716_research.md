# Group Research: group_314_dragonflybsd_sources_os_bsd_dragonflybsd_sys_sys_jail_h_sources_os_b_4cce9b757716

Scope verified against `Docs/research_subset_a.md`: `sources/os/bsd/dragonflybsd` is included. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/jail.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/jail.h

Defines DragonFly BSD jail user/kernel ABI and kernel prison structures. Userland gets `struct jail`, legacy `struct jail_v0`, and `jail()` / `jail_attach()` declarations. Kernel sections define `struct prison`, per-jail IP storage, jail capability bit numbers, and helpers for IP validation, local/nonlocal address selection, wildcard replacement, privilege checks, refcounting, and sysctl lifecycle.

Filesystem relevance: jail capabilities include VFS permissions such as `PRISON_CAP_VFS_CHFLAGS` and mount permissions for nullfs, devfs, tmpfs, procfs, and fusefs. `struct prison` also stores the jailed root `nchandle`, tying jail isolation directly to namecache/VFS root lookup.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/jail.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/journal.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/journal.h

Defines the on-disk/on-wire binary record format for DragonFly’s VFS journaling stream. The file documents raw record alignment, forward/backward scanning, stream IDs, endian detection, transaction begin/end/abort bits, and nested subrecord semantics.

Key types are `journal_rawrecbeg`, `journal_rawrecend`, `journal_ackrecord`, `journal_subrecord`, and low-level leaf structures such as `jleaf_path`, `jleaf_vattr`, `jleaf_cred`, and `jleaf_ioinfo`. Constants define stream control bits, special stream IDs, max record sizes, nested record masks, VFS operation record types (`JTYPE_CREATE`, `JTYPE_RENAME`, `JTYPE_WRITE`, etc.), and leaf payload IDs. This is the protocol contract used by mount journaling and recovery/audit tools.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/journal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/joystick.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/joystick.h

Small user ABI header for joystick state and ioctls. Defines `struct joystick` with `x`, `y`, `b1`, and `b2` fields, plus timeout and X/Y offset ioctl commands.

No filesystem behavior; included in this group as a public DragonFly system header.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/joystick.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/kbio.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/kbio.h

Defines keyboard ioctl ABI, keyboard modes, LED/lock state constants, keyboard metadata, repeat settings, keymap structures, accent/dead-key maps, function-key tables, and key return flags. It exposes user/kernel shared structures such as `keyboard_info_t`, `keyboard_repeat_t`, `keymap_t`, `accentmap_t`, `keyarg_t`, and `fkeyarg_t`.

Kernel-only compatibility structures support old keymaps. No direct VFS role, but it is a stable ioctl-facing system interface.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/kbio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/kcollect.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/kcollect.h

Defines the fixed-format kernel statistics collection record `kcollect_t` and the 29-entry metric namespace. Metrics cover load, CPU percentages, swap, VM faults, memory states, syscall counts, path lookups, interrupts, IPIs, timers, and dynamic slots.

Kernel APIs allow registration/unregistration of callbacks and direct value/scale updates. Filesystem relevance is through `KCOLLECT_NLOOKUP`, which tracks path lookup activity, and VM/memory counters useful for filesystem workload diagnosis.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/kcollect.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/kcore.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/kcore.h

Declares `kcore_make_file()`, which fills a `kinfo_file` record from a kernel `file` object, process id, uid, and descriptor number. It bridges kernel file structures to exported kernel-core/introspection data.

Relevant to filesystem research because it exposes open-file metadata for core/kernel inspection paths.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/kcore.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/kenv.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/kenv.h

Defines constants for the `kenv(2)` syscall: get, set, unset, and dump operations, plus maximum name/value lengths of 128 bytes. This is a compact user/kernel ABI header for kernel environment variables.

No direct VFS logic, but boot/kernel environment values often feed mount/root/device configuration.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/kenv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/kern_syscall.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/kern_syscall.h

Kernel-only header collecting internal syscall helper prototypes. It groups descriptors, exec, wait, signals, generic I/O, limits, sockets, pipes, VFS syscalls, time, cwd, and mmap helpers.

Filesystem-relevant helpers include `kern_access`, `kern_chdir`, `kern_chmod`, `kern_chown`, `kern_chroot`, `kern_fstatfs`, `kern_fstatvfs`, `kern_ftruncate`, `kern_getdirentries`, `kern_link`, `kern_mountctl`, `kern_mkdir`, `kern_mknod`, `kern_open`, `kern_readlink`, `kern_rename`, `kern_stat`, `kern_statfs`, `kern_statvfs`, `kern_symlink`, `kern_truncate`, `kern_unlink`, `kern_fsync`, and `kern_mmap`. These are the reusable kernel-side entry points behind system call wrappers.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/kern_syscall.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/kernel.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/kernel.h

Kernel-only header for global kernel variables, boot/sysinit ordering, tunables, pseudo-device module registration, and interrupt configuration hooks. It declares host/time/tick globals and the `vmm_guest_type` enum.

The `sysinit_sub_id` enum defines boot ordering, including allocator, KLD, VFS, root configuration, dump configuration, mount-root, and kernel-thread phases. `SYSINIT` / `SYSUNINIT` register ordered init/uninit entries via linker sets. `TUNABLE_INT/LONG/ULONG/QUAD/STR` bind loader/kernel environment tunables into sysinit. Filesystem relevance is high because VFS modules use this ordering and `VFS_SET` ultimately relies on module/sysinit machinery.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/kernel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/kerneldump.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/kerneldump.h

Defines kernel dump header format and dump I/O interface. `kerneldumpheader` stores magic, architecture, dump version, length, time, block size, hostname, version string, panic string, and parity. Endian conversion macros encode dump byte order.

Kernel APIs include `mkdumpheader`, dumper callback type `dumper_t`, `struct dumperinfo`, `set_dumper`, `dump_write`, `dumpsys`, `md_dumpsys`, and CPU reactivation. Relevant to storage because dump devices implement the low-level writer described by `dumperinfo`.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/kerneldump.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/kinfo.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/kinfo.h

Defines public/kernel information structures for files, CPU time, PC tracking, clock info, LWPs, processes, and signal trampoline ranges. Major structures are `kinfo_file`, `kinfo_cputime`, `kinfo_pcheader`, `kinfo_pctrack`, `kinfo_clockinfo`, `kinfo_lwp`, `kinfo_proc`, and `kinfo_sigtramp`.

Filesystem relevance: `kinfo_file` reports file descriptor state including fd number, file pointer, type, offset, flags, and backing data pointer. `kinfo_proc` includes jail id, process credentials, VM size, and embedded LWP state. Kernel fill helpers populate these exported snapshots.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/kinfo.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/kobj.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/kobj.h

Kernel object dispatch framework adapted from FreeBSD. It defines `kobj_t`, `kobj_class_t`, method descriptors, method tables, class fields, compiled operation caches, and macros for declaring and defining classes with zero to three base classes.

Kernel APIs instantiate/uninstantiate classes, create/init/delete objects, lookup methods with cache support, and provide default error methods. This underpins driver and bus object method dispatch rather than VFS directly, but it is part of DragonFly’s kernel module architecture.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/kobj.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/kthread.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/kthread.h

Kernel-only process/thread daemon interface. Defines `struct kproc_desc` for starting internal daemons and declares kproc/kthread lifecycle helpers: start, suspend, resume, suspend loop, shutdown, allocation, CPU-specific creation, and exit.

Filesystem relevance: background filesystem, syncer, journal, buffer, VM, and helper threads use this style of kernel thread lifecycle.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/kthread.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ktr.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/ktr.h

Defines generic kernel trace-ring support. Core structures are `ktr_info`, `ktr_entry`, per-core `ktr_cpu_core`, and cache-aligned `ktr_cpu`. `KTR_INFO_MASTER`, `KTR_INFO`, `KTR_LOG`, and `KTR_COND_LOG` create typed, compile-time-checkable trace sites with sysctl-controlled masks.

Relevant to filesystem debugging because any subsystem can define trace classes and log compact event payloads into per-CPU buffers without full printf overhead.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ktr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ktrace.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/ktrace.h

Defines process syscall tracing ABI and kernel helpers. Includes trace operations, trace flags, `ktrace_node`, `ktr_header`, and records for syscall entry/return, generic I/O, signals, and context switches.

Filesystem relevance: `KTR_NAMEI` records pathnames and `KTR_GENIO` records file descriptor read/write data; userland APIs `ktrace()` and `utrace()` expose tracing control. Kernel helpers emit namei, genio, syscall, sysret, sysctl, signal, and context-switch records.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ktrace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/libkern.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/libkern.h

Kernel-only libc-like utility declarations and inline helpers. Provides BCD/hex conversion tables, min/max/abs variants for several integer types, random APIs, compare/search/sort/string routines, fnmatch, mem helpers, and compatibility aliases such as `strchr` to `index`.

Filesystem code commonly depends on these primitives for path/string handling, sorting, matching, randomization, checks, and safe kernel-side utility operations.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/libkern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/limits.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/limits.h

Thin wrapper that includes `<machine/limits.h>`. It provides machine-specific limit constants through the standard system header path.

No local logic.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/limits.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/link_elf.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/link_elf.h

Defines ELF runtime linker/debugger public structures and helpers. Includes SunOS-compatible search path flags, `Link_map`, `r_debug`, `dl_phdr_info`, callback type for `dl_iterate_phdr`, and rtld helper declarations.

Mostly user/runtime-linker ABI. Indirectly relevant to kernel/module research through ELF format conventions, but kernel KLD details are in `linker.h`.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/link_elf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/linker.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/linker.h

Defines kernel linker/KLD interfaces and userland kld syscall ABI. Kernel sections define `linker_file`, `linker_file_ops`, `linker_class`, symbol lookup types, dependency tracking, preload metadata search, ELF relocation helpers, and linker debug macros.

User ABI includes module metadata constants, `kld_file_stat`, `kld_sym_lookup`, and functions `kldload`, `kldunload`, `kldfind`, `kldnext`, `kldstat`, `kldfirstmod`, and `kldsym`. Filesystem relevance is high because VFS implementations are commonly loadable kernel modules registered through this linker/module path.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/linker.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/linker_set.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/linker_set.h

Defines ELF linker set macros. `__MAKE_SET` places pointers into named `set_*` sections and declares start/stop symbols. Public macros include `TEXT_SET`, `DATA_SET`, `BSS_SET`, `ABS_SET`, `SET_ENTRY`, `SET_DECLARE`, `SET_BEGIN`, `SET_LIMIT`, `SET_FOREACH`, `SET_ITEM`, and `SET_COUNT`.

This is core infrastructure for `SYSINIT`, module metadata, and other registry-style kernel tables, including VFS/module registration.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/linker_set.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/lock.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/lock.h

Defines DragonFly’s general sleepable lock manager API. `struct lock` stores flags, timeout, shared/exclusive count bits, wait message, and exclusive holder. The header defines lock request types, count bit layout, external/control flags, return semantics, initializer macros, sysinit helpers, and inline dispatch through `lockmgr()`.

Filesystem relevance is central: mount locks, vnode locks, rename locks, and many VFS paths use lockmgr semantics for shared/exclusive locking, upgrades, downgrades, cancellation, retries, and reclaim-aware behavior.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/lock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/lockf.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/lockf.h

Kernel-only byte-range locking structures. `lockf_range` records lock type, flags, start/end offsets, owner process, and list linkage. `struct lockf` keeps active and blocked range queues plus initialization state.

Kernel APIs include `lf_advlock`, `lf_count_adjust`, and `maxposixlocksperuid`. This is the VFS advisory locking support embedded by filesystem inode/vnode implementations.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/lockf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/lwp.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/lwp.h

Defines user ABI for lightweight process creation and control. `lwp_params` supplies entry function, argument, stack, and two tid copyout addresses. User-visible APIs include `lwp_create`, `lwp_create2`, `lwp_gettid`, name get/set, realtime priority, affinity get/set, and `lwp_kill`.

No direct VFS implementation, but LWP ids appear in tracing and kinfo records.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/lwp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/machintr.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/machintr.h

Kernel-only machine-independent interrupt ABI. Defines `machintr_type`, vector setup/teardown constants, and `struct machintr_abi` containing callbacks for interrupt enable/disable/setup/teardown, legacy interrupt routing, MSI/MSI-X allocation/release/map, finalization, stabilization, IRQ map initialization, and resource manager setup.

Storage and filesystem code do not call this directly, but block/network drivers depend on this interrupt abstraction underneath I/O completion.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/machintr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/malloc.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/malloc.h

Defines DragonFly kernel malloc flags, malloc type declaration/definition macros, common malloc types, slab/contiguous allocation APIs, kmalloc object-zone helpers, debug and non-debug allocation wrappers, zeroing optimizations, realloc/string duplication helpers, free helpers, usable-size/limit APIs, and slab cleanup.

Filesystem relevance is broad: VFS, vnode, mount, journal, namecache, and filesystem implementations allocate typed kernel memory through this interface. Notable semantics: `M_NOWAIT` can fail often on DragonFly; `M_SYSALLOC`/reserve flags exist for critical kernel infrastructure; object allocations use separate `_obj` malloc types.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/malloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mapped_ioctl.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/mapped_ioctl.h

Defines an ioctl translation/mapping framework. It declares wrapper and command mapping callback types, `ioctl_map_range`, range construction macros, `ioctl_map`, and `ioctl_map_handler`.

Kernel APIs register/unregister handlers and route `mapped_ioctl()` calls. Useful for compatibility layers where ioctl command numbers or payload layouts must be translated before dispatching to underlying file/device handlers.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mapped_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mbuf.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/mbuf.h

Defines DragonFly mbuf packet buffer layout, flags, allocation macros, packet headers, external storage descriptors, packet tags, checksum flags, firewall/PF metadata, allocator statistics, manipulation routines, and mbuf queue helpers.

Core structures include `m_hdr`, `pkthdr_pf`, `m_tag`, `pkthdr`, `m_ext`, `mbuf`, `mbstat`, and `mbufq`. Kernel APIs cover allocation, free, append, copy, pullup/pulldown, split, defrag, external buffer attach, packet header movement, tag management, and queue operations. Filesystem relevance is indirect through network filesystems, sockets, sendfile, and kernel I/O paths that pass data through mbufs.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mbuf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mchain.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/mchain.h

Kernel-only helper API for encoding and decoding typed values into/from mbuf chains. Defines copy modes, custom copy callback type, `mbchain` write builder, and `mdchain` read cursor.

APIs initialize, finalize, detach, reserve, fix headers, append integers in big/little endian, append memory/mbufs/uio, and extract typed values/memory/mbufs/uio. Relevant to network filesystems and protocols that serialize filesystem messages over mbufs.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mchain.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/md4.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/md4.h

Kernel-only MD4 interface. Userland is explicitly directed to OpenSSL’s MD4 header. Defines `MD4_CTX` with state, count, and input buffer, plus `MD4Init`, `MD4Update`, and `MD4Final`.

Likely used by legacy protocols or compatibility code needing MD4 in kernel context.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/md4.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/md5.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/md5.h

Kernel-only MD5 interface and libmd/OpenSSL compatibility shim. Defines MD5 block/digest constants, `MD5_CTX`, and `MD5Init`, `MD5Update`, `MD5Final`.

Potential filesystem relevance through checksumming, protocol authentication, or compatibility code, though this header itself only declares the digest API.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/md5.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/memrange.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/memrange.h

Defines `/dev/mem` memory range attribute ABI. User structures `mem_range_desc` and `mem_range_op` describe base, length, cache/write attributes, owner, and set/remove operations. Ioctls are `MEMRANGE_GET` and `MEMRANGE_SET`.

Kernel section declares `mem_range_ops`, `mem_range_softc`, global softc, get/set helpers, AP init, and I/O privilege helpers. Relevant to low-level storage/device mappings where cache attributes matter.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/memrange.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/microtime_pcpu.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/microtime_pcpu.h

Defines a per-CPU monotonic microtime helper. `union microtime_pcpu` stores either a `timeval` or TSC value. `microtime_pcpu_get()` uses invariant TSC when available, otherwise `microuptime`; `microtime_pcpu_diff()` returns elapsed microseconds.

Useful for low-overhead timing in kernel subsystems, with the caveat that monotonicity is only guaranteed on the same CPU.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/microtime_pcpu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mman.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/mman.h

Defines memory mapping and memory advice user ABI. Includes `mode_t`, `off_t`, and `size_t` fallbacks; protection flags; mapping flags including DragonFly/BSD extensions such as `MAP_VPAGETABLE`, `MAP_TRYFIXED`, `MAP_NOCORE`, `MAP_SIZEALIGN`, and `MAP_32BIT`; mlock flags; msync flags; madvise/posix_madvise constants; mincore bits; and mmap-family function declarations.

Filesystem relevance is high because file-backed mappings, msync, mmap, mincore, and vnode-backed VM behavior are part of the VFS/VM boundary.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mman.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/module.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/module.h

Defines kernel module metadata and module event ABI. Includes metadata types, module event types, `module_t`, event handler type, `moduledata_t`, module-specific stat union, dependency/version/metadata structures, and kernel macros `MODULE_METADATA`, `MODULE_DEPEND`, `DECLARE_MODULE`, and `MODULE_VERSION`.

Kernel APIs register, lookup, reference, release, unload, enumerate, and set module-specific data. User ABI exposes `module_stat`, `modnext`, `modfnext`, `modstat`, and `modfind`. VFS modules use this infrastructure for load/unload and dependency/version metadata.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/module.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mount.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/mount.h

Primary DragonFly VFS mount interface. Defines file system ids, file handles, `statfs`, BIO dependency callbacks, quota accounting trees, the central `struct mount`, mount/user/kernel flags, mount-list scan flags, VFS sysctl IDs, MP-lock helper macros, sync flags, export/public NFS structures, `vfsconf`, VFS implementation flags, vfsquery flags, VFS operation typedefs, `struct vfsops`, dispatch macros, `VFS_SET`, export structures, and kernel/user VFS APIs.

Important filesystem details: `struct mount` stores VFS ops, vfsconf, namecache generation, syncer vnode/context, vnode lists, mount lock/token, stat/statvfs caches, mountpoint handles, VOP operation stacks for coherency/journaling/normal/spec/fifo, active journal list and stream id bitmap, BIO ops, rename lock, and VFS accounting. This is the core contract every filesystem implementation must satisfy.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mountctl.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/mountctl.h

Defines mount control operations, especially journaling control. Public operation constants cover installing/removing/resyncing/status/restarting VFS journals, block journals, export setting, statvfs, and mount flag extraction.

Structures include journal install/restart/remove/status requests, returned journal status, in-kernel `journal_memfifo`, `journal`, `jrecord`, and `jrecord_list`. Kernel APIs create/destroy journal threads and build journal records with nested/leaf data, uio/xio/page/vnode/path/credential helpers. Userland gets `mountctl()`. This header ties `journal.h` protocol records to live mount-level journal management.

<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mountctl.h -->
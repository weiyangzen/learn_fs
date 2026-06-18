# Group Research: group_445_freebsd_src_sources_os_bsd_freebsd_src_sys_sys_linker_h_sources_os_b_fd4c97ad4b8e

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/freebsd-src`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/linker.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/linker.h

Defines FreeBSD kernel linker and KLD user/kernel ABI interfaces.

Key content:
- Kernel-only `struct linker_file`, `struct linker_class`, symbol typedefs, and callbacks for loaded ELF objects.
- Tracks module reference counts, pathname, load address/size, constructors/destructors, dependency files, common symbols, contained modules, preload dependency state, and tracing metadata.
- Declares kernel linker APIs: module reference/release, loaded-file iteration, symbol lookup, linker set lookup, function enumeration, file unload, dependency loading, DDB symbol helpers, HWPMC object listing, and kldload busy/unbusy coordination.
- Defines boot/preload metadata constants such as `MODINFO_*` and `MODINFOMD_*`, plus preload search/fetch APIs.
- Declares ELF relocation and CTF support hooks used by linker backends.
- Exposes user-visible KLD syscall structures: `struct kld_file_stat`, `struct kld_sym_lookup`, unload flags, and libc prototypes for `kldload`, `kldunload`, `kldfind`, `kldstat`, `kldsym`, etc.

Research relevance:
- This is the central interface between boot-loaded modules, runtime-loaded KLDs, module metadata, and kernel symbol/relocation services.
- It is tightly coupled with `module.h` and `linker_set.h`: module metadata is collected through linker sets and interpreted by the runtime linker/module subsystem.
- Filesystem and storage modules depend on this ABI for load/unload, version/dependency checks, exported symbol resolution, and static constructor/destructor handling.

Cautions:
- Several definitions are kernel-only, while KLD syscall ABI structs are shared with userland.
- `MODINFOMD_*` values have machine-dependent caveats, especially PowerPC.
- `struct kld_file_stat_1` is legacy and versioned by struct size.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/linker.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/linker_set.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/linker_set.h

Defines FreeBSD linker set declaration, population, iteration, and counting macros.

Key content:
- `__MAKE_SET_QV` emits weak `__start_set_<set>` and `__stop_set_<set>` symbols and places a pointer to a target symbol in an ELF section named `set_<set>`.
- Public macros include `TEXT_SET`, `DATA_SET`, `DATA_WSET`, `BSS_SET`, `ABS_SET`, and `SET_ENTRY`.
- `SET_DECLARE`, `SET_BEGIN`, `SET_LIMIT`, `SET_FOREACH`, `SET_ITEM`, and `SET_COUNT` provide typed access to collected entries.
- Userspace AddressSanitizer redzones are avoided with `__nosanitizeaddress`; kernel builds use an empty `__NOASAN`.
- PowerPC64 ELFv1 has a special `__MAKE_SET_CONST` rule because function pointers point to descriptors.

Research relevance:
- Linker sets are the compile/link-time registry mechanism used throughout the kernel for module metadata, sysinit records, device methods, and other extensible registries.
- `module.h` uses `DATA_SET(modmetadata_set, ...)` to collect dependency/version/PNP/module declarations.
- Filesystem modules declared via `VFS_SET` ultimately rely on module metadata and linker set collection.

Cautions:
- Sets contain addresses of objects, so iterator variables must be pointer-to-pointer style.
- Section packing assumptions are important; sanitizer redzones can break those assumptions without the no-ASAN annotation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/linker_set.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/lock.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/lock.h

Defines the generic lock-class framework, lock object flags, WITNESS hooks, KTR lock tracing helpers, and adaptive spin delay support.

Key content:
- `struct lock_class` abstracts common operations for lock types: assert, DDB show, lock/unlock around sleep queues, owner query, and trylock.
- Class flags distinguish sleep locks, spin locks, sleepability, recursion, and upgradability.
- Lock object flags cover initialization, WITNESS monitoring, quiet mode, recursion, sleepability, vnode-lock hints, profiling disable, and class index encoding.
- Lock operation flags include trylock, exclusive, duplicate-ok, no-sleep, new-order, and quiet behavior.
- Assertion flags define unlocked, locked, shared, exclusive, recursed, and non-recursed states.
- Kernel-only tracing macros emit KTR lock events when `LOCK_DEBUG > 0`.
- Declares global lock classes for mutex, sx, rw, rm, and lockmgr.
- Provides `lock_delay_*` adaptive spin delay structs and helpers.
- Declares the WITNESS API and maps it to no-op macros when `WITNESS` is disabled.

Research relevance:
- This is the common lock instrumentation layer used by VFS, mount, vnode, mbuf, allocator, and module subsystems.
- `lockmgr.h`, `mount.h`, and `msgbuf.h` depend on lock object/class semantics from this header.
- WITNESS and KTR are essential for diagnosing filesystem locking order and sleep-with-lock bugs.

Cautions:
- Lock class indices are encoded into `lo_flags`, so class mask/shift values are ABI-sensitive inside the kernel.
- Many macros depend on `_KERNEL` and debug config options.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/lock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/lock_profile.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/lock_profile.h

Defines lock profiling declarations and no-op fallbacks.

Key content:
- Declares `struct lock_profile_object` and `LIST_HEAD(lpohead, lock_profile_object)`.
- Under `_KERNEL && LOCK_PROFILING`, includes CPU timing and lock definitions.
- Declares `lock_prof_enable` and profiling hooks for successful lock obtain, release, and thread exit.
- Inline `lock_profile_obtain_lock_failed()` records wait start time with `nanoseconds()` when profiling is enabled, the lock is profileable, and contention has not already been recorded.
- Without `LOCK_PROFILING`, all profiling macros compile to no-ops.

Research relevance:
- Used with `lockstat.h` and lock implementations to record contention timing and hold behavior.
- Important for diagnosing filesystem/VFS lock contention under load.
- `LO_NOPROFILE` from `lock.h` suppresses profiling for specific locks.

Cautions:
- Profiling code exists only in kernel builds with `LOCK_PROFILING`.
- The failed-obtain helper only records first contention per attempt through the caller-provided `contested` flag.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/lock_profile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/lockf.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/lockf.h

Defines kernel byte-range file lock state for POSIX/flock-style advisory locking.

Key content:
- `struct lockf_entry` represents one byte-range lock request or active lock, including semantics flags, lock type, range, owner, vnode, async callback, graph edges, and references.
- `struct lockf_edge` links blocked pending locks to active or older pending locks, forming a dependency graph.
- `struct lockf` tracks lock state for a vnode/file: active lock list, pending lock list, sx lock, and thread count.
- Lists are ordered by lock start for active locks; pending locks are newer-first and include edges for blocking/fairness.
- Extra implementation flag `F_INTR` marks locks interrupted by purge.
- Declares APIs: `lf_advlock`, `lf_advlockasync`, `lf_purgelocks`, lock iteration by sysid/vnode, lock counting, and remote system clearing.

Research relevance:
- This is the kernel structure behind VFS advisory record locks.
- Filesystems embed or reference `struct lockf *` in private vnode/node state to support `VOP_ADVLOCK`.
- The graph model is relevant to deadlock/fairness analysis for NFS and local filesystems.

Cautions:
- Field comments specify distinct locks: vnode interlock, per-state sx lock, global lock-state lock, and constant-after-allocation fields.
- Correct lifecycle depends on `ls_threads` deferring free while users may sleep.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/lockf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/lockmgr.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/lockmgr.h

Defines the lockmgr lock API, state encoding, operations, attributes, and assertions.

Key content:
- Low bits in `lk_lock` encode shared/exclusive waiters, spinners, share mode, and writer recursion.
- Macros decode holder, sharer count, unlocked state, and disowned kernel ownership.
- Kernel API includes `__lockmgr_args`, direct shared/exclusive/unlock helpers, init/destroy, recursion/share toggles, disown, status, debug chain, and printinfo.
- Inline wrappers accept mutex or rwlock interlocks and pass their embedded `lock_object`.
- Public macros include `lockmgr`, `lockmgr_args`, `lockmgr_args_rw`, `lockmgr_disown`, `lockmgr_recursed`, and `lockmgr_assert`.
- `lockinit()` flags define recursion, no-duplicate, no-profile, no-share, no-witness, quiet, vnode, and new behavior.
- Operation flags define shared/exclusive/release/upgrade/downgrade/drain/try-upgrade.
- Assertion flags map to generic lock assertions.

Research relevance:
- Lockmgr is heavily used by vnode and filesystem code, including mount locks in `mount.h`.
- Its state encoding matters when researching vnode lock behavior, shared/exclusive transitions, and recursion.
- Requires `LOCK_FILE` and `LOCK_LINE`, so callers must include `sys/lock.h` first.

Cautions:
- Some flags are operation attributes, some init-only, and some operation types; `LK_TOTAL_MASK` separates these classes.
- Comment has legacy spelling but API names are authoritative.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/lockmgr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/lockstat.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/lockstat.h

Defines DTrace lockstat provider probes and lock profiling integration macros.

Key content:
- Declares `lockstat` SDT provider and probes for adaptive mutexes, spin locks, rw locks, sx locks, lockmgr locks, and thread spin events.
- Probe categories include acquire, release, spin, block, upgrade, downgrade, and disown.
- Defines `LOCKSTAT_WRITER` and `LOCKSTAT_READER`.
- Exposes `volatile bool lockstat_enabled`.
- With `KDTRACE_HOOKS`, `LOCKSTAT_RECORD*` macros emit SDT probes and profiling macros call lock-profile hooks plus emit the matching probe.
- Without `KDTRACE_HOOKS`, probe macros are empty while profiling hooks still call lock profiling where applicable.
- Provides `LOCKSTAT_PROFILE_ENABLED()` as runtime gating and declares `lockstat_nsecs()` with KDTrace hooks.

Research relevance:
- Bridges lock implementations with observability. Useful for tracing VFS and network-buffer lock contention without changing lock code.
- Works alongside `lock_profile.h`; DTrace and lock profiling can be independently relevant.

Cautions:
- Only active in kernel builds.
- Probe macros compile away when KDTrace hooks are absent, so instrumentation availability is build-dependent.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/lockstat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/loginclass.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/loginclass.h

Defines per-login-class resource-accounting state.

Key content:
- `struct loginclass` contains list linkage, login class name, reference count, and pointer to resource accounting object `struct racct`.
- Declares `loginclass_hold`, `loginclass_free`, `loginclass_find`, and `loginclass_racct_foreach`.
- `loginclass_racct_foreach` supports callbacks over login-class resource accounting objects with optional pre/post hooks and two generic callback arguments.

Research relevance:
- Provides the kernel representation for login classes used in resource accounting and limits.
- Relevant to filesystem work where credentials, jails, or resource accounting intersect with mount/file operations indirectly.

Cautions:
- Depends on `MAXLOGNAME` and `LIST_ENTRY` being available from including context.
- This header only exposes the structure and lifecycle API; policy and locking live elsewhere.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/loginclass.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/mac.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/mac.h

Defines the user/kernel ABI for Mandatory Access Control labels.

Key content:
- Establishes POSIX MAC visibility and label size constants:
  - `MAC_MAX_POLICY_NAME`
  - `MAC_MAX_LABEL_ELEMENT_NAME`
  - `MAC_MAX_LABEL_ELEMENT_DATA`
  - `MAC_MAX_LABEL_BUF_LEN`
- `struct mac` carries label text buffers across syscalls/ioctls with `m_buflen` and `m_string`.
- `mac_t` is a pointer to `struct mac`.
- Userland-only APIs include label allocation/free, text conversion, get/set label on fd/file/link/process/peer/pid, policy presence checks, type-specific prepare helpers, `mac_execve`, and `mac_syscall`.
- Defines userland config path `/etc/mac.conf`.

Research relevance:
- VFS, mount, mbuf packet tags, SysV IPC, shared memory, and filesystems can carry MAC labels.
- This file is the public ABI for MAC-aware tools and the structure used at syscall boundaries.

Cautions:
- Kernel policy hooks and internal label structures are not defined here.
- Userland declarations are hidden under `!_KERNEL`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/mac.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/malloc.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/malloc.h

Defines FreeBSD kernel malloc type accounting, allocation flags, allocator APIs, and standalone fallback allocation macros.

Key content:
- Allocation flags include `M_NOWAIT`, `M_WAITOK`, `M_NORECLAIM`, `M_ZERO`, `M_NOVM`, `M_USE_RESERVE`, `M_NODUMP`, fit strategies, executable allocation, never-freed, and unprotected allocation.
- `M_VERSION` guards malloc type structure versioning.
- `struct malloc_type_stats` stores per-CPU allocation/free counters and size bitmask; asserted to be 64 bytes.
- `struct malloc_type_internal` stores DTrace probes, UMA zone id, per-CPU stats, and spare ABI fields.
- `struct malloc_type` is the public type descriptor with global-chain link, version, short description, and internal data.
- Stream structures expose `kern.malloc` statistics to userland.
- Kernel macros `MALLOC_DEFINE` and `MALLOC_DECLARE` define/register malloc types via SYSINIT/SYSUNINIT.
- Declares common malloc types such as `M_CACHE`, `M_DEVBUF`, `M_TEMP`, and `M_IOV`.
- Declares allocation APIs including `malloc`, `free`, `zfree`, `realloc`, `reallocf`, `mallocarray`, domainset variants, executable variants, aligned variants, and contiguous allocation.
- The `malloc` macro optimizes compile-time-known `M_ZERO` allocations by clearing at the call site.
- `WOULD_OVERFLOW()` supports multiplication overflow detection for array allocation.
- `_STANDALONE` maps allocation to boot/stand `Malloc`/`Free`.

Research relevance:
- This is the core allocator contract for kernel subsystems, including VFS, modules, mbuf tags, mount state, and device ioctls.
- Malloc type accounting is important when tracing memory use by filesystem components.

Cautions:
- Kernel `malloc` is macro-wrapped, so call-site behavior may differ from a plain function call.
- Struct layout is ABI-sensitive for monitoring tools.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/malloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/mbuf.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/mbuf.h

Defines FreeBSD mbuf packet-buffer structures, flags, external storage model, packet tags, allocation/free APIs, queue helpers, and mchain helpers.

Key content:
- Defines mbuf sizing macros `MHSIZE`, `MPKTHSIZE`, `MLEN`, `MHLEN`, `MINCLSIZE`, and `M_NODOM`.
- Kernel SDT probes cover mbuf init, allocation, cluster attachment, free, and chain free.
- `struct m_tag` represents packet annotations with cookie/id/length/free callback.
- `struct m_snd_tag` tracks interface send tags with refcount and operations table.
- `struct pkthdr` stores per-packet metadata: receive/send interface union, leaf receive interface, tags, total length, flow id, checksum/offload flags, FIB, NUMA domain, RSS hash type, timestamps/header lengths, persistent and local scratch storage.
- `struct m_ext` describes external storage or multi-page unmapped storage, including embedded or external refcounts, storage size/type/flags, buffer/page vectors, TLS header/trailer space, free callback, and args.
- `struct mbuf` combines chain pointers, data pointer, length, type/flags, optional packet header, external storage, multi-page TLS metadata, and inline data.
- Defines extensive mbuf flags: external storage, packet header, end-of-record, readonly, broadcast/multicast/promisc, VLAN tag, unmapped ext pages, timestamps, and protocol-specific flags.
- Defines RSS hash types, external storage types, external flags, checksum/offload flags, compatibility aliases, and mbuf content types.
- Declares UMA zones and large API surface for mbuf manipulation: adjust, append, copy, collapse, defrag, demote, external add, fragment, free, get variants, length, pullup/pulldown, split, uiomove, unshare, send tag, rcvif serialization, and unmapped conversions.
- Inline helpers handle page length sanity, type/zone selection, raw/initialized allocation, cluster setting, protocol-flag clearing, last mbuf lookup, refcount lookup, writability checks, assertions, start/size/leading/trailing space, prepend, receive interface access, packet tag operations, send tag ref/release, and single-mbuf free.
- Packet tag IDs include IPsec, bridge, gif/gre, checksum, encapsulation, IPv6, dummynet, divert, MAC label, PF, CARP, NAT-T, ND, OpenVPN, and more.
- `struct mbufq` implements packet queues with max length and inline enqueue/dequeue/flush/drain/concat helpers.
- `struct mchain` tracks chains by `m_stailq`, with logical data length and memory-consumption accounting plus get/split/uiomove APIs.
- Timestamp helpers convert packet timestamps to `timespec` or `timeval`.
- Debugnet and TLS-session helper declarations are present.

Research relevance:
- This is the core network I/O buffer ABI. It intersects with filesystem/storage through sendfile, unmapped pages, UIO conversion, KTLS, mbuf-backed memory descriptors, MAC labels, and kernel I/O paths.
- `memdesc.h` can construct mbuf chains from abstract memory descriptors and uses `M_EXT`/`M_EXTPG` semantics.
- `mchain.h` provides protocol serialization/deserialization helpers on top of mbufs.

Cautions:
- Many structure sizes and offsets are asserted in implementation files; layout changes are dangerous.
- `M_WRITABLE()` is conservative and responsibility still rests with callers.
- `m_cljset()` is explicitly described as dangerous because it cannot prove the cluster is new/unreferenced.
- `m_free()` may release packet tags, send tags, external storage, ext pages, or the UMA mbuf depending on flags.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/mbuf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/mchain.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/mchain.h

Defines mbuf-chain marshal/unmarshal helper structures and APIs for kernel protocol code.

Key content:
- Kernel-only header.
- Copy modes for `mb_put_mem`/`md_get_mem`: system bcopy, user copyin/copyout, inline copy loop, zero fill, and custom callback.
- `struct mbchain` tracks output chain state: top mbuf, current mbuf, remaining space, byte count, optional custom copy function, and user data.
- `struct mdchain` tracks input parsing state: top mbuf, current mbuf, and current data position.
- Declares builders for padding, integer writes in big/little endian, memory writes, mbuf writes, and UIO writes.
- Declares readers for integer values in native/big/little endian, memory extraction, mbuf extraction, UIO extraction, and record traversal.

Research relevance:
- Common in network filesystem/protocol implementations that serialize request/response fields into mbuf chains.
- Complements `mbuf.h` with a cursor-style API for structured binary protocols.

Cautions:
- Endianness-specific helpers are explicit; callers must choose correctly for protocol wire format.
- Only declarations are here; allocation/failure semantics are implemented elsewhere.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/mchain.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/md4.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/md4.h

Defines MD4 context and function prototypes.

Key content:
- `MD4_CTX` contains four-word state, two-word bit count, and 64-byte input buffer.
- Userland symbol names are remapped to `_libmd_*` names unless already defined, avoiding clashes with libcrypto.
- Declares `MD4Init`, `MD4Update`, `MD4Pad`, and `MD4Final`.
- Userland-only convenience APIs: `MD4End`, `MD4Fd`, `MD4FdChunk`, `MD4File`, `MD4FileChunk`, and `MD4Data`.
- Uses RSA-MD license.

Research relevance:
- Provides legacy digest API used by compatibility code and protocols that still require MD4.
- Kernel exposure is limited to core transform/update/final API; file/fd helpers are userland-only.

Cautions:
- MD4 is cryptographically broken; presence here is compatibility, not modern security guidance.
- Include context must provide integer types such as `u_int32_t`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/md4.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/md5.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/md5.h

Defines MD5 context, digest constants, and function prototypes.

Key content:
- Constants:
  - `MD5_BLOCK_LENGTH` = 64
  - `MD5_DIGEST_LENGTH` = 16
  - `MD5_DIGEST_STRING_LENGTH` = 33
- `MD5_CTX` contains four-word state, two-word bit count, and 64-byte input buffer.
- Userland symbol names are remapped to `_libmd_*` to avoid libcrypto collisions.
- Declares `MD5Init`, `MD5Update`, and `MD5Final`.
- Userland-only helpers include `MD5End`, `MD5Fd`, `MD5FdChunk`, `MD5File`, `MD5FileChunk`, and `MD5Data`.
- Uses RSA-MD license.

Research relevance:
- Legacy checksum/digest API used in compatibility and non-cryptographic contexts.
- Some filesystems/tools historically use MD5 for identifiers or integrity checks, so this ABI may appear in related code.

Cautions:
- MD5 is not suitable for collision-resistant security.
- Kernel API omits userland file/fd convenience wrappers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/md5.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/mdioctl.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/mdioctl.h

Defines ioctl ABI for the FreeBSD memory disk pseudo-device.

Key content:
- `enum md_types` covers memory-disk backing types: malloc, preload, vnode, swap, and null.
- `struct md_ioctl` carries version, unit number, type, backing file path, media size, sector size, options, base address, firmware geometry, label, and padding.
- Device names: `MD_NAME` = `md`, `MDCTL_NAME` = `mdctl`.
- `MDIOVERSION` is 0.
- Ioctls:
  - `MDIOCATTACH`
  - `MDIOCDETACH`
  - `MDIOCQUERY`
  - `MDIOCRESIZE`
- Options include clustering behavior, swap reservation, auto unit, readonly, compression, force, async, vnode verify, cache vnode data, and BIO_DELETE deallocation requirement.

Research relevance:
- Directly relevant to block-storage and filesystem test setups: md devices provide in-memory, file-backed, swap-backed, preload-backed, or null block devices.
- Vnode-backed options intersect with VFS caching, verification, and BIO_DELETE behavior.

Cautions:
- Comment notes configuration persists across opens/closes until cleared/detached.
- `MD_CLUSTER` comment says "Don't cluster", so the flag name is historically counterintuitive.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/mdioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/membarrier.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/membarrier.h

Defines FreeBSD membarrier command ABI.

Key content:
- `enum membarrier_cmd` values are bit flags; `MEMBARRIER_CMD_QUERY` returns supported commands as a bitset and itself has value zero.
- Commands include global/shared barrier, global expedited, registration for global expedited, private expedited, private expedited sync-core, registration variants, RSEQ compatibility constants, and current-registration query.
- RSEQ command constants are defined for source compatibility but explicitly not supported by query.
- `enum membarrier_cmd_flag` defines `MEMBARRIER_CMD_FLAG_CPU`.
- Userland prototype: `int membarrier(int, unsigned, int);`

Research relevance:
- Provides userspace-visible memory ordering and synchronization ABI.
- Relevant to runtime libraries and lock-free algorithms rather than filesystem code directly, but can affect kernel/user synchronization assumptions in tests.

Cautions:
- Query support mask is authoritative; defined constants are not necessarily implemented.
- Header is small and ABI-focused, with kernel implementation elsewhere.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/membarrier.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/memdesc.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/memdesc.h

Defines an abstract memory descriptor used to represent different backing layouts for I/O buffers.

Key content:
- `struct memdesc` stores one of: virtual address, physical address, bus DMA segment list, UIO, mbuf, VM page array, plus length/segment count/offset and type.
- Types include contiguous virtual, contiguous physical, virtual scatter/gather list, physical scatter/gather list, UIO, mbuf, and VM pages.
- Inline constructors: `memdesc_vaddr`, `memdesc_paddr`, `memdesc_vlist`, `memdesc_plist`, `memdesc_uio`, `memdesc_mbuf`, `memdesc_vmpages`.
- Conversion constructors declared for `bio` and CAM `ccb`.
- Declares copy helpers `memdesc_copyback` and `memdesc_copydata`.
- Defines callback types for allocating external-buffer mbufs and ext-page mbufs.
- `memdesc_alloc_ext_mbufs()` constructs an mbuf chain backed by the described memory, using `M_EXT` for mapped storage and `M_EXTPG` for unmapped/page storage; supports offset, length, actual length, wait flag, and truncation.

Research relevance:
- Bridges storage I/O (`bio`, CAM CCB), VM pages, UIO, and network mbufs.
- Important for zero-copy or low-copy paths, sendfile-like logic, and storage/network integration.
- Tightly related to `mbuf.h` external storage and unmapped page semantics.

Cautions:
- A memdesc is only a description; caller-supplied callbacks manage actual mbuf allocation and references.
- Partial allocation failure frees already-built chains.
- Truncation can intentionally return a shorter chain to avoid splitting pages.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/memdesc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/memrange.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/memrange.h

Defines memory range attribute ioctls and kernel hooks for `/dev/mem`.

Key content:
- Memory attribute flags represent uncacheable, write-combine, write-through, write-back, write-protect, unknown, and attribute mask.
- Control flags identify fixed base/length, firmware-provided, active, bogus, fixed active, busy, and force.
- `struct mem_range_desc` describes base, length, flags, and owner string.
- `struct mem_range_op` carries descriptor pointer and operation args for update/remove.
- Ioctls: `MEMRANGE_GET`, `MEMRANGE_SET`.
- `struct mem_extract` supports virtual-to-physical extraction with domain and state; ioctl `MEM_EXTRACT_PADDR`.
- `struct mem_livedump_arg` supports live kernel dump request; ioctl `MEM_KERNELDUMP`.
- Kernel-only declarations include `M_MEMDESC`, `struct mem_range_ops`, `struct mem_range_softc`, global `mem_range_softc`, init/destroy, and get/set attribute APIs.

Research relevance:
- Relevant to low-level memory mapping, caching behavior, kernel dumps, and physical address inspection.
- Storage and filesystem crash/debug workflows may use live dump and memory extraction paths.

Cautions:
- Attribute modifications can be risky; `MDF_FORCE` exists for risky changes.
- Machine-dependent implementation is abstracted behind `mem_range_ops`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/memrange.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/mman.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/mman.h

Defines memory mapping, protection, advisory, locking, shared memory, memfd, and kernel `shmfd` ABI/state.

Key content:
- Defines inheritance constants for `minherit`.
- Protection flags: none/read/write/exec plus CHERI bits and max-protection encoding helpers under BSD visibility.
- Mapping flags include shared/private, fixed, semaphore, stack, nosync, anon, guard, excl, nocore, prefault read, low 32-bit, and alignment/superpage alignment.
- Shared memory rename flags support no-replace and exchange.
- Memory locking flags: `MCL_CURRENT`, `MCL_FUTURE`.
- `MAP_FAILED`, `msync` flags, and `madvise`/POSIX madvise constants.
- `mincore` result bits include incore, referenced/modified by self/others, and superpage page-size index.
- Defines `SHM_ANON`, `shm_open2` flags, largepage allocation policies, `struct shm_largepage_conf`.
- Defines `memfd_create` flags and hugepage size encodings.
- Declares `mode_t`, `off_t`, and `size_t` when needed.
- Kernel or `_WANT_FILE` exposes `struct shmfd`: size, VM object, pages, refs, uid/gid/mode, kmapping count, timestamps, inode, MAC label, path, range lock, mutex, flags, seals, and largepage config.
- Kernel declares shm map/unmap/access/alloc/hold/drop/truncate/largepage/remove-prison/path APIs and `shm_ops`.
- Userland declares mmap-family, mlock-family, shm, memfd, and largepage shm APIs.

Research relevance:
- Filesystems and VFS interact with memory mapping through file ops, vnode-backed mappings, shared memory fileops, and `mmap` flags.
- `struct shmfd` is a kernel file-like object with stat-compatible metadata and MAC labeling.
- Largepage and memfd behavior can affect VM/filesystem tests.

Cautions:
- Many constants are gated by feature visibility macros.
- Some POSIX typed memory APIs are explicitly noted as missing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/mman.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/module.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/module.h

Defines kernel module metadata, declaration macros, dependency/version records, PNP info export, module locking, and userland module stat calls.

Key content:
- Metadata types: dependency, module declaration, version, PNP info.
- Defines module event types: load, unload, shutdown, quiesce.
- `moduledata_t` stores module name, event handler, and private data.
- `modspecific_t` union lets modules report custom scalar data through `kldstat`.
- `struct mod_depend`, `struct mod_version`, `struct mod_metadata`, and `struct mod_pnp_match_info` describe embedded metadata.
- Kernel macros:
  - `MODULE_METADATA` emits metadata into `modmetadata_set`.
  - `MODULE_DEPEND` records versioned dependencies.
  - `DECLARE_MODULE`, `DECLARE_MODULE_TIED`, and `DECLARE_MODULE_WITH_MAXVER` register modules through SYSINIT and attach kernel-version dependency metadata.
  - `MODULE_VERSION` records module version.
  - `MODULE_PNP_INFO` exports parseable driver match tables.
- PNP descriptor grammar is documented for matching fields such as U8/V16/U32/string/EISA/table keys.
- Declares global module sx lock and lock macros.
- Kernel module APIs include register, lookup by name/id, quiesce, reference/release, unload, id/name/specific/file accessors.
- Userland ABI includes `struct module_stat` and calls `modnext`, `modfnext`, `modstat`, and `modfind`.

Research relevance:
- Central to loadable filesystem, storage, and driver modules.
- Works directly with `linker.h` and `linker_set.h`.
- `mount.h` uses module declarations for `VFS_SET`.

Cautions:
- `DECLARE_MODULE_TIED` enforces exact `__FreeBSD_version`; regular module max version rounds to branch end unless `KLD_TIED`.
- Module metadata is embedded via linker sets, so linker behavior is part of the ABI.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/module.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/module_khelp.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/module_khelp.h

Defines kernel helper module declaration structures and macros.

Key content:
- Helper flag `HELPER_NEEDS_OSD`.
- `struct helper` contains init/destroy callbacks, fixed-size name, UMA zone, hook info pointer/count, classes, id, refcount, flags, and list linkage.
- `struct khelp_modevent_data` carries helper module declaration data: name, helper object, hooks, hook count, UMA zone size, constructor, and destructor.
- `KHELP_DECLARE_MOD_UMA` builds modevent data, moduledata, declares the module at `SI_SUB_KHELP`, and records module version.
- `KHELP_DECLARE_MOD` is the no-UMA convenience wrapper.
- Declares `khelp_modevent`.

Research relevance:
- Provides module scaffolding for kernel helper frameworks with hooks and optional UMA per-object storage.
- Depends on `module.h` module declaration/version mechanisms and UMA types.

Cautions:
- Helper names are limited to 16 bytes including terminator constraints in fixed buffers.
- Hook structures are referenced but not defined here.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/module_khelp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/mount.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/mount.h

Defines FreeBSD filesystem mount ABI, VFS mount structures, statfs layouts, mount flags, export structures, VFS operation vectors, VFS registration macros, and mount lifecycle APIs.

Key content:
- Defines `fsid_t`, `fsidcmp`, `struct fid`, `fhandle_t`, and current/legacy `statfs` layouts.
- `struct statfs` contains version, filesystem type, exported flags, block/file counters, read/write counters, vnode list size, name length, owner, fsid, type name, mounted-from name, and mount-on name.
- `_WANT_MOUNT`/kernel section defines mount option lists and `struct vfsopt`.
- `struct mount_pcpu` tracks per-CPU thread-in-op, references, lock references, and write operation counts.
- `struct mount_upper_node` tracks stacked filesystems mounted above a lower filesystem.
- `struct mount` is the core per-mounted-filesystem object: operation counters, flags, pcpu state, root/covered vnodes, vfsops/vfsconf, interlock, vnode lists, write counts, mount options, statfs cache, credentials, private data, export data, MAC label, hash seed, suspension state, rename/export locks, upper/notification lists, deferred-unmount fields, etc.
- Provides vnode iteration macros for all vnodes and lazy vnodes on a mount.
- Provides mount interlock/reference macros.
- Defines mount option name mappings when requested.
- User-visible `MNT_*` flags cover read-only, sync/async, noexec/nosuid, ACL/NFSv4 ACL, union, noatime, clustering, soft updates/SUJ, gjournal, MAC multilabel, automounted, verified, untrusted, named attributes, NFS export/TLS flags, local/quota/root/user/ignore, and command flags.
- Internal `MNTK_*` flags describe unmount, suspend, async filtering, softdep interactions, shared write/lock behavior, I/O page-fault policy, nullfs cache behavior, fast path lookup, buffer cache use, and more.
- Defines VFS sysctl identifiers, sync wait modes, export argument structures, public NFS export state, `struct vfsconf`, userland `xvfsconf`, implementation flags `VFCF_*`, VFS control structures, and `vfsquery`.
- Kernel VFS op typedefs include mount, cmount, unmount, root, quotactl, statfs, sync, vget, fhtovp, checkexp, init/uninit, extattrctl, sysctl, suspension cleanup, lower-vnode notifications, purge, and lockf reporting.
- `struct vfsops` contains the filesystem operation vector plus ABI spares.
- Inline wrappers dispatch `VFS_*` operations and optionally trace mount.
- `VFS_SET` declares a filesystem module using `module.h`.
- Declares large VFS API surface for mount argument building, option parsing, exporting, busy/unbusy, root mount, notification, refs, mount allocation/destruction, syncer vnodes, VFS registration, default ops, suspend/resume all filesystems, operation barriers, and per-CPU operation counters.
- Userland declarations include file-handle APIs, `statfs`/`fstatfs`/`getfsstat`/`getmntinfo`, `mount`, `nmount`, `unmount`, and `getvfsbyname`.

Research relevance:
- This is the primary VFS mount contract for FreeBSD. It defines how filesystem modules register, mount, export, report stats, synchronize, and interact with vnodes.
- It is central to local filesystems, network filesystems, stacked filesystems, jail-aware exports, lock reporting, and mount lifecycle.
- Integrates with `module.h`, `lockmgr.h`, `lock.h`, vnode code, MAC labels, NFS export structures, and per-CPU operation accounting.

Cautions:
- Comments explicitly warn that changing `statfs`, `mount`, `MNT_*`, or `MNTK_*` requires updating DDB mount display code.
- User-visible flags, command flags, and internal flags share names/prefixes but have distinct semantics.
- Some old flags intentionally collide in different syscall contexts.
- Per-CPU VFS op enter/exit relies on critical sections and atomic fences; misuse can break unmount/drain invariants.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/mount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/mouse.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/mouse.h

Defines mouse device ioctl ABI, status/mode/hardware structures, protocol identifiers, model identifiers, and packet-format constants.

Key content:
- Ioctls for status, hardware info, mode get/set, protocol level get/set, raw state/data reads, and Synaptics hardware info.
- `mousestatus_t` tracks state-change flags, current/previous buttons, and dx/dy/dz movement.
- Button masks support up to 31 buttons, with standard and extended button masks.
- `mousehw_t` reports button count, interface type, device type, model, and hardware id.
- `synapticshw_t` exposes many Synaptics capability and geometry fields.
- Defines interface types: unknown, serial, PS/2, sysmouse, USB.
- Defines device types: mouse, trackball, stick, pad.
- Defines models including generic, GlidePoint, IntelliMouse, Think, VersaPad, Explorer, Synaptics, TrackPoint, Elantech.
- `mousemode_t` stores protocol, rate, resolution, acceleration, level, packet size, and sync mask.
- Protocol constants cover serial, PS/2, sysmouse, remote, VersaPad, jogdial, GTCO, and legacy bus/inport.
- Extensive packet constants document packet sizes, sync masks, button bits, sign/overflow bits, wheel bits, and sysmouse extended packet layout.
- Defines `_PATH_MOUSEREMOTE`.

Research relevance:
- Peripheral/device ABI rather than filesystem-specific, but part of the FreeBSD sys header group.
- Useful for understanding userland ioctl compatibility and input-device packet decoding.

Cautions:
- Several bus protocols are marked obsolete in comments.
- Packet bit definitions vary by protocol and sometimes reuse bits, e.g. PS/2 GlidePoint tap uses the sync bit.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/mouse.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/mpt_ioctl.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/mpt_ioctl.h

Defines ioctl ABI for LSI MPT-Fusion host adapter configuration and RAID actions.

Key content:
- Includes MPI type/config headers from `dev/mpt/mpilib`.
- `struct mpt_cfg_page_req` carries a config page header, page address, buffer pointer, length, and IOC status.
- `struct mpt_ext_cfg_page_req` is the extended-page variant.
- `struct mpt_raid_action` carries RAID action, volume bus/id, physical disk number, action data word, buffer, length, volume status, action data array, action status, IOC status, and write flag.
- Ioctls:
  - `MPTIO_READ_CFG_HEADER`
  - `MPTIO_READ_CFG_PAGE`
  - `MPTIO_READ_EXT_CFG_HEADER`
  - `MPTIO_READ_EXT_CFG_PAGE`
  - `MPTIO_WRITE_CFG_PAGE`
  - `MPTIO_RAID_ACTION`
- On amd64, 32-bit compatibility structs/ioctls replace pointers with uint32_t buffer fields.

Research relevance:
- Storage-controller management ABI for configuration pages and RAID actions.
- Relevant to block-storage research where device ioctls expose hardware configuration and status.

Cautions:
- Callers must include correct page type/extended type, page number, version, and page address.
- 32-bit compatibility ABI is explicitly separate on amd64.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/mpt_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/mqueue.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/mqueue.h

Defines POSIX message queue attribute structure.

Key content:
- `struct mq_attr` includes:
  - `mq_flags`
  - `mq_maxmsg`
  - `mq_msgsize`
  - `mq_curmsgs`
  - four reserved longs, ignored on input and zeroed on output.

Research relevance:
- Minimal user/kernel ABI for POSIX message queues.
- Included in this group as a small IPC header, not directly VFS-specific.

Cautions:
- Only attributes are defined here; queue operations and implementation live elsewhere.
- Reserved fields are part of ABI padding/forward compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/mqueue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/msan.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/msan.h

Defines Kernel Memory Sanitizer interface hooks and no-op fallbacks.

Key content:
- Active only under `KMSAN`; otherwise every hook macro compiles to no-op.
- KMSAN state constants distinguish uninitialized and initialized shadow bytes.
- KMSAN type constants classify stack, kmem, malloc, and UMA origins.
- `KMSAN_RET_ADDR` captures caller return address.
- Declares init and shadow mapping hooks.
- Declares thread allocation/free hooks.
- Declares DMA map sync hook through `struct memdesc` and `bus_dmasync_op_t`.
- Declares origin, mark, and check functions for raw buffers, bios, mbufs, CAM CCBs, and UIOs.

Research relevance:
- Important for detecting use of uninitialized memory across storage, network, UIO, and mbuf paths.
- Interacts with `memdesc.h`, `mbuf.h`, and block I/O structures.

Cautions:
- Function names in no-op section include legacy DMA macro names as well as `kmsan_bus_dmamap_sync`.
- Requires `KMSAN` build to have any runtime effect.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/msan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/msg.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/msg.h

Defines System V message queue ABI and kernel-private queue structures.

Key content:
- Defines `MSG_NOERROR`.
- Typedefs `msglen_t` and `msgqnum_t`.
- Declares standard scalar types if not already declared.
- Legacy `struct msqid_ds_old` is available under old FreeBSD compatibility options.
- `struct msqid_ds` exposes queue permissions, first/last message pointers, byte count, message count, byte limit, last send/receive pids, and send/receive/change times.
- Kernel-only `struct msg` stores next pointer, message type, message size, buffer segment location, and MAC label.
- Internal `struct msginfo` stores SysV tunables: max chars/message, queue identifiers, queue bytes, total messages, segment size, segment count.
- `struct msqid_kernel` wraps user-visible `msqid_ds` plus kernel-private MAC label and creator credentials.
- Kernel declares global `msginfo` and `kern_get_msqids`.
- Userland declares `msgctl`, `msgget`, `msgrcv`, and `msgsnd`.

Research relevance:
- IPC ABI with MAC integration and credential ownership.
- Relevant to kernel object accounting/security and compatibility, though not filesystem-specific.

Cautions:
- Header comments call out namespace pollution around `struct msg` and nonstandard members.
- Segment size constraints are documented but enforced in implementation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/msg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/msgbuf.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/msgbuf.h

Defines kernel circular message buffer state and APIs.

Key content:
- `struct msgbuf` stores buffer pointer, magic value, size, write/read sequence numbers, checksum, sequence modulus, last priority, flags, and mutex.
- Magic constant `MSG_MAGIC`.
- Flags:
  - `MSGBUF_NEEDNL`
  - `MSGBUF_WRAP`
- Sequence macros normalize sequence values, convert sequence to buffer position, and add/subtract normalized sequence numbers.
- Kernel declarations include global msgbuf size/trigger/pointer and global lock.
- Kernel APIs initialize, reinitialize, duplicate, clear, copy, add char/string, get bytes, peek bytes, get count, and get one character.
- Default `MSGBUF_SIZE` is `32768 * 3` unless overridden.

Research relevance:
- Kernel log/message ring used for boot/runtime diagnostics.
- Relevant to filesystem research for crash/debug output and persistent diagnostic paths.

Cautions:
- Sequence arithmetic uses `msg_seqmod`, not raw buffer size, to handle wrap behavior.
- Includes lock/mutex headers and embeds a mutex in the message buffer.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/msgbuf.h -->
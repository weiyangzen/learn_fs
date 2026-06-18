# Group Research: group_553_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_m_91281d5c643a

Scope verified against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All four listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/mmapobj.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/mmapobj.c

## Purpose

Implements `mmapobj()`, the kernel object mapper used to map files either as flat private mappings or as interpreted executable objects. It understands ELF `ET_EXEC`, `ET_DYN`, `ET_REL`, and `ET_CORE` behavior; unsupported or small/non-ELF interpreted files fail with `ENOTSUP`. The file also implements a `lib_va` cache for ET_DYN objects so repeatedly mapped shared libraries can prefer stable virtual addresses when ASLR and padding do not disable the optimization.

## Main Entry Points

- `mmapobj()` dispatches flat vs interpreted mapping, validates padding and flags, handles `E2BIG` sizing for caller-provided `mmapobj_result_t` arrays.
- `mmapobj_unmap()` tears down partial or complete mappings, including ET_EXEC `/dev/null` reservation restoration and ET_DYN reservation-hole cleanup.
- `check_exec_addrs()` reserves fixed ET_EXEC address ranges or reuses prior `/dev/null` reservations.
- `mmapobj_map_interpret()` reads the initial header and routes ELF work through `doelfwork()`.
- `doelfwork()` validates ELF class/model/type, reads program headers with sleep/nosleep allocation policy, and calls `process_phdrs()`.
- `process_phdrs()` computes loadable spans, allocates/reserves start addresses, fills result descriptors, manages padding, updates the `lib_va` cache, and invokes `mmapobj_map_elf()`.
- `mmapobj_map_flat()`, `mmapobj_map_elf()`, and `mmapobj_map_ptload()` perform the actual vnode/address-space mapping and BSS zero-fill handling.

## Key Data and Algorithms

`struct lib_va` caches per-vnode identity, timestamps, preferred base VA, span, alignment, and up to `LIBVA_CACHED_SEGS` cached result descriptors. Cache lookup keys use fsid/nodeid plus ctime/mtime. Stale entries are removed immediately or marked `LV_DEL` until reference count reaches zero.

Address placement uses `map_addr()`, `as_gap()`, `valid_usr_range()`, `as_map()`, and per-model `lib_va_32_arena` / `lib_va_64_arena` vmem arenas. ASLR or requested padding disables the cache. 32-bit library VA reservation is limited by `lib_threshold`.

ELF segment processing recognizes `PT_LOAD` and `PT_SUNWBSS`, rejects overlapping mappings, handles non-power-of-two alignment by rounding, maps executable text with `MAP_TEXT`, maps data with `MAP_INITDATA`, and falls back to anonymous mapping plus `vn_rdwr()` when file offset and virtual address page offsets do not permit direct `VOP_MAP()`.

## Dependencies

This file sits directly on VM, VFS, ELF, process, and vnode interfaces: `as_*`, `segvn`, `segdev`, `VOP_MAP`, `VOP_GETATTR`, `vn_rdwr`, `valid_usr_range`, `map_addr`, process security flags, and filesystem `VFS_NOEXEC`.

## Correctness Notes

Important edge cases include noexec filesystems, ET_EXEC address collisions, partial failure cleanup after some segments are mapped, non-page-aligned ELF segments, BSS tail zeroing without permanent write permission, program-header allocation failure for very large tables, and avoiding reserved stack ranges. The cache uses mutexes and memory barriers so `lv_mps` is visible before `lv_num_segs` advertises valid cached descriptors.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/mmapobj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/modconf.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/modconf.c

## Purpose

Defines the `mod_ops` implementations used by illumos loadable modules. Despite the filename, this file is not the driver.conf parser; it is the install/remove/info dispatch layer for module linkage types.

## Main Entry Points

- `mod_install()`, `mod_remove()`, and `mod_info()` walk a module’s `modlinkage` array and call type-specific install/remove/info methods, with rollback/reinstall behavior on partial failure.
- `mod_modname()` returns the module name from the owning `modctl`.
- `mod_driverops`, `mod_fsops`, `mod_syscallops`, `mod_strmodops`, `mod_sockmodops`, `mod_schedops`, `mod_execops`, `mod_dacfops`, `mod_ippops`, `mod_pcbeops`, `mod_brandops`, and `mod_kiconvops` bind linkage classes to concrete operations.

## Subsystem Behavior

Driver modules are installed by validating module linkage, resolving major number, rejecting MT-unsafe non-nexus drivers, checking bus ops revision, populating `devopsp[major]`, and setting STREAMS implementation fields when needed. Removal refuses active/unload-disabled drivers and restores `mod_nodev_ops`.

Filesystem modules validate `vfsdef`, allocate or find `vfssw` slots, merge mount option prototypes, call filesystem init, and optionally initialize VOP stats. Removal checks `vsw_count` and `vfs_opsinuse()` before clearing the slot.

System call modules patch `sysent` and, when enabled, `sysent32`; removal requires loadable/non-`SE_NOUNLOAD` state and a try-write lock. Scheduling class, exec format, STREAMS, socket, DACF, IPP, brand, PCBE, and kiconv modules each register/unregister with their respective global subsystem tables.

## Dependencies

Key dependencies include `modctl` ownership lookup, `devnamesp`, `devopsp`, STREAMS `fmodsw`, `vfssw`, `sysent`, `execsw`, scheduling class state, DACF, IPP, BrandZ, kiconv, CPC/PCBE, and socket module registration.

## Correctness Notes

The file is mostly state-table mutation code. Locking discipline matters around `devnames` locks, `vfssw` read/write locks, syscall `sy_lock`, scheduler class locks, and exec locks. Several module classes intentionally refuse unload under debug/autounload controls or by design, especially PCBE modules.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/modconf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/modctl.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/modctl.c

## Purpose

Implements the `modctl(2)` system call and the kernel module loading/unloading framework. It owns global module records, module setup at boot, dynamic loading through `kobj`, installation via `_init`, removal via `_fini`, dependency tracking, autounload, driver major bindings, minor permissions, device policy helpers, device retirement, devfs helpers, and DDI module-open APIs.

## Main Entry Points

- `mod_setup()` initializes major/syscall bindings, `devopsp`, `devnamesp`, module hash support, DACF, IPP, syscall locks, exec locks, classes, and autounload thread-specific state.
- `modctl()` dispatches privileged user commands such as `MODLOAD`, `MODUNLOAD`, `MODINFO`, driver alias binding, driver.conf load/unload, device path/devid queries, sysevents, minor permissions, devfs queries, device retirement, hotplug, and devname operations.
- `modload()`, `modload_qualified()`, `modloadonly()`, `modunload()`, `mod_remove_by_name()`, `modreap()`, and `mod_uninstall_daemon()` provide kernel module lifecycle APIs.
- `mod_hold_stub()` / `mod_release_stub()` support loadable stubs.
- `ddi_modopen()`, `ddi_modsym()`, and `ddi_modclose()` implement dynamic module/library reference loading for DDI clients.

## Module Lifecycle

Module records are `struct modctl` entries linked on the global `modules` list. `mod_hold_by_name_common()`, `mod_hold_by_id()`, and `mod_hold_by_modctl()` serialize access with `mod_lock`, `mod_busy`, `mod_want`, and `mod_cv`. Circular dependency detection uses `mod_inprogress_thread` and `mod_requisite_loading`.

`mod_load()` checks exclusion policy, loads object code through `kobj_load_module()` in a helper thread when possible, records linkage via `_info`, installs stubs, runs hotinlines, and notifies DTrace. `modinstall()` installs requisites then invokes `_init`. `moduninstall()` refuses primary/referenced/enabled modules, detaches drivers before `_fini`, then clears installed stubs on success. `mod_unload()` resets stubs, unloads kobj memory, releases requisites, and notifies DTrace.

## Device and Filesystem-Relevant Control

This file manages driver major aliases and binding state through `modctl_update_driver_aliases()`, `modctl_rem_major()`, `modctl_load_drvconf()`, and `modctl_unload_drvconf()`. It integrates with device tree binding/unbinding, driver.conf reloads, devfs cache invalidation, `/devices` attribute cleanup, `/dev` non-reconfiguring queries, device retirement persistence, devid-to-path lookup, minor-name/path lookup, framebuffer path query, and hotplug operations.

Minor permissions are loaded from nvlist payloads and stored per driver in `devnamesp[major]`. `dev_minorperm()` resolves defaults using exact/pattern matching, wildcard entries, clone-driver special handling, and alias fallback.

## Dependencies

Major dependencies include `kobj`, DDI/NDI, devfs/sdev, devpolicy, sysevents, DACF, IPP, DTrace callbacks, module stubs, instance database, binding-file hash tables, `devnamesp`, `devopsp`, syscall tables, exec tables, class setup, and power-management lock borrowing during module load.

## Correctness Notes

The highest-risk areas are lifecycle races and lock ordering. The code carefully avoids holding `mod_lock` across blocking operations, releases module holds before driver detach to avoid devinfo/module deadlocks, uses autounload disable counters to serialize cleanup windows, and preserves dependency reference counts through requisite lists. User-facing commands rely heavily on careful `copyin`/`copyout`, native vs 32-bit model conversion, length validation, and double-NUL path-list sizing.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/modctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/modhash.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/modhash.c

## Purpose

Provides a small, flexible, chained hash table implementation for kernel subsystems. It supports pluggable key destructors, value destructors, hash functions, comparator functions, allocation policy, reserved-entry insertion, lookup callbacks, walking, replacement, removal, and clearing.

## Main Entry Points

- Constructors: `mod_hash_create_extended()`, `mod_hash_create_strhash()`, `mod_hash_create_ptrhash()`, `mod_hash_create_idhash()`.
- Destructors: `mod_hash_destroy_hash()`, plus string/pointer/id wrapper destroy functions.
- Mutation: `mod_hash_insert()`, `mod_hash_insert_reserve()`, `mod_hash_replace()`, `mod_hash_remove()`, `mod_hash_destroy()`, `mod_hash_clear()`.
- Lookup/walk: `mod_hash_find()`, `mod_hash_find_cb()`, `mod_hash_find_cb_rval()`, `mod_hash_walk()`.
- Allocation helpers: `mod_hash_reserve()`, `mod_hash_reserve_nosleep()`, `mod_hash_cancel()`.
- Internal nosync helpers are exported in this file for callers that already hold appropriate synchronization.

## Hash Variants

String hashes use the classic Dragon Book string hash and string key comparison/destruction. Pointer hashes shift out low alignment bits based on pointed-to element size. ID hashes multiply by the next prime larger than the chain count, generated by `mod_hash_iddata_gen()`.

## Data and Locking

Entries come from the global `mh_e_cache` kmem cache initialized by `mod_hash_init()`. Each hash has an `rwlock` protecting contents; public insert/remove/replace/clear paths take writer locks, find/walk paths take reader locks. All created hashes are linked on the global `mh_head` list under `mh_head_lock`.

## Correctness Notes

Duplicate inserts are rejected. Removal destroys stored keys but returns values to the caller; destroy paths destroy both key and value. Callback lookup executes the callback while the hash reader lock is held, so callbacks must avoid updates to the same hash. The implementation does not resize, and `nchains` choice directly affects lookup cost.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/modhash.c -->
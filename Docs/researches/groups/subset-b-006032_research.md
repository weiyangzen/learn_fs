# subset-b-006032 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/gcov/clang.c -->
# sources/distributed-fs/ceph-client/kernel/gcov/clang.c

## Purpose
`clang.c` adapts LLVM/Clang's `llvm_gcov_init()`/`llvm_gcda_*()` callback model to the kernel gcov debugfs infrastructure. LLVM does not expose a GCC-style stable `gcov_info` object, so this file builds a kernel-local `gcov_info` list while compiler-rt calls back through start-file, function, and arc emission hooks.

## Important APIs, types, and functions
The file defines private `struct gcov_info` and `struct gcov_fn_info` layouts for Clang coverage, stores registered objects in `clang_gcov_list`, and uses `current_info` as transient callback context. Exported compiler hooks are `llvm_gcov_init()`, `llvm_gcda_start_file()`, `llvm_gcda_emit_function()`, `llvm_gcda_emit_arcs()`, `llvm_gcda_summary_info()`, and `llvm_gcda_end_file()`. Generic gcov integration is provided through `gcov_info_filename()`, `gcov_info_version()`, `gcov_info_next()`, `gcov_info_link()`, `gcov_info_unlink()`, `gcov_info_within_module()`, `gcov_info_reset()`, compatibility/add/dup/free helpers, and `convert_to_gcda()`.

## Control flow
`llvm_gcov_init()` allocates a new info object, links it under `gcov_lock`, sets `current_info`, calls LLVM's writeout callback, then emits a `GCOV_ADD` event if debugfs event replay is enabled. The callback sequence populates filename/version/checksum, appends one function record per `llvm_gcda_emit_function()`, and attaches counter arrays through `llvm_gcda_emit_arcs()`. Reads from debugfs later call `convert_to_gcda()`, which serializes the stored records into a `.gcda` stream: header, function tags, counter tag, and 64-bit counter values.

## State and persistence
Registered Clang coverage objects persist in `clang_gcov_list` for the lifetime of the module/object that registered them. Function counter pointers normally reference compiler-generated storage, while duplicated info objects deep-copy filenames and counter arrays for unloaded-module persistence in `fs.c`. `current_info` is valid only during the writeout callback. There is no disk persistence here; debugfs readers synthesize gcda bytes on demand.

## Dependencies and integration points
This file depends on `gcov.h`, the shared `gcov_lock` and event mechanism from `base.c`/`fs.c`, Linux list and allocation helpers, module address range checks via `within_module()`, and the compiler-rt LLVM gcov callback ABI. It intentionally exposes the same generic gcov helper API as the GCC backend so `fs.c` can operate without knowing the compiler-specific layout.

## Risks and test signals
Risks include callback ordering assumptions, silent loss of function records on allocation failure, `llvm_gcda_emit_arcs()` assuming a function was just appended, compatibility checks that compare checksums but not counter counts before addition, and lifetime hazards because live counter arrays are not owned by this file. Test signals include boot/module coverage with Clang, unload persistence with `gcov_persist=1`, reset clearing live counters, debugfs gcda streams accepted by `gcov`, incompatible reload warnings, and failure injection around function/counter duplication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/gcov/clang.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/gcov/fs.c -->
# sources/distributed-fs/ceph-client/kernel/gcov/fs.c

## Purpose
`fs.c` exposes kernel gcov coverage data under debugfs as a directory tree rooted at `/sys/kernel/debug/gcov`. It creates one data file per instrumented object, provides symlinks needed by gcov tooling, supports per-file and global counter resets, and optionally preserves accumulated coverage for unloaded modules.

## Important APIs, types, and functions
The central type is `struct gcov_node`, which models debugfs directories and data files, tracks loaded `gcov_info` pointers, an `unloaded_info` copy, child lists, symlink dentries, and names. `struct gcov_iterator` holds a synthesized gcda buffer for seq-file reading. Key functions are `gcov_event()`, `add_node()`, `add_info()`, `remove_info()`, `save_info()`, `get_accumulated_info()`, `gcov_seq_open()`, `gcov_seq_write()`, `reset_write()`, `add_links()`, and `gcov_fs_init()`.

## Control flow
Initialization creates the `gcov` debugfs directory and `reset` control file, then enables event replay so already registered coverage objects appear. `gcov_event(GCOV_ADD)` locates an existing node by filename or creates path directories and a data file; duplicate object names are checked for compatibility and accumulated at read time. Opening a data file copies and sums the relevant `gcov_info` objects under `node_lock`, serializes them to a fixed gcda buffer, and hands that buffer to seq-file callbacks in page-sized strides. Writing to a data file resets that object or removes an unloaded-only node; writing to `reset` resets all live nodes and prunes unload-only leaves.

## State and persistence
All state is in memory: `root_node`, `all_head`, child lists, debugfs dentries, live `loaded_info` arrays, and optional `unloaded_info` snapshots. `gcov_persist`, controlled by the `gcov_persist=` boot parameter, determines whether unload data is deep-copied and accumulated or removed when the last live object disappears. Open readers use independent deep-copy buffers, so concurrent counter updates do not mutate the active seq read.

## Dependencies and integration points
The file depends on debugfs, seq_file, module gcov events, compiler-specific helpers declared in `gcov.h`, `OBJTREE`/`SRCTREE` path definitions, and Linux allocation/list/mutex primitives. It integrates with both GCC and Clang backends through the common `gcov_info_*()` API and creates `.gcno` symlinks through `gcov_link[]` so external gcov tools can pair runtime data with build artifacts.

## Risks and test signals
Risks include path traversal behavior from `.` and `..` components, stale node lookup by filename when two objects share a name, incomplete symlink cleanup on partial failure, large coverage buffers stressing `kvmalloc`, compatibility decisions losing saved unload data, and reset/remove races around open files. Test signals include recursive copy of debugfs gcov, per-file reset and global reset, module unload/reload with compatible and incompatible code, object paths under objtree and external builds, `.tmp_` deskewed module filenames, and concurrent reads during add/remove events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/gcov/fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/gcov/gcc_4_7.c -->
# sources/distributed-fs/ceph-client/kernel/gcov/gcc_4_7.c

## Purpose
`gcc_4_7.c` implements the compiler-specific gcov backend for GCC 4.7 and newer profiling layouts. It understands GCC-generated `gcov_info`, function metadata, active counter arrays, GCC-version-dependent counter counts and record-size units, and converts live profiling data into gcda format for the generic debugfs exporter.

## Important APIs, types, and functions
Private types are `struct gcov_ctr_info`, `struct gcov_fn_info`, and `struct gcov_info`, matching GCC's generated layout for the compiler version in use. The global list head is `gcov_info_head`. Public helpers include `gcov_info_filename()`, `gcov_info_version()`, `gcov_info_next()`, `gcov_info_link()`, `gcov_info_unlink()`, `gcov_info_within_module()`, `gcov_info_reset()`, `gcov_info_is_compatible()`, `gcov_info_add()`, `gcov_info_dup()`, `gcov_info_free()`, and `convert_to_gcda()`.

## Control flow
Compiler constructor code registers `gcov_info` through the base file, which links objects into the singly linked list here. Reset walks every instrumented function and active counter type, zeroing counter arrays. Duplication deep-copies the object filename, function pointer array, per-function metadata, and active counter value arrays. Addition walks matching functions and active counter types to accumulate counts. `convert_to_gcda()` serializes file header, optional GCC 12+ checksum field, function records, and all active counter records with proper GCC unit sizing.

## State and persistence
Live `gcov_info` objects are compiler-generated static data; only their `next` pointer and counter values change at runtime. Deep copies created for debugfs readers or unload persistence own duplicated filenames, function info, and counter arrays. Compatibility is based on `stamp`, so saved data persists only across reloads with the same compile stamp. No persistent storage is written by this file.

## Dependencies and integration points
This backend is selected by build configuration for GCC coverage and is consumed by `gcc_base.c` and `fs.c` through `gcov.h`. It depends on exact GCC layout compatibility, compiler version macros, kernel allocation helpers, and gcov record constants. `gcov_link[]` provides `.gcno` symlink metadata for the debugfs layer.

## Risks and test signals
Risks include GCC layout drift, incorrect `GCOV_COUNTERS` values for a new compiler, GCC 12 byte-versus-word record-size handling, compatibility based only on `stamp`, active-counter traversal mismatches between source and destination, and large allocations during duplication. Test signals include coverage builds across supported GCC versions, gcda parsing by matching `gcov`, unload/reload accumulation, reset of all active counter kinds, GCC 12+ output checksum field handling, and failure injection in `gcov_info_dup()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/gcov/gcc_4_7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/gcov/gcc_base.c -->
# sources/distributed-fs/ceph-client/kernel/gcov/gcc_base.c

## Purpose
`gcc_base.c` provides the exported symbols that GCC-generated profiling code expects in the kernel. It registers each object file's `gcov_info` and stubs out libgcov merge/flush/exit helpers that are referenced by instrumented code but not used by the kernel runtime.

## Important APIs, types, and functions
The central entry point is `__gcov_init(struct gcov_info *info)`. Exported no-op helpers are `__gcov_flush()`, `__gcov_merge_add()`, `__gcov_merge_single()`, `__gcov_merge_delta()`, `__gcov_merge_ior()`, `__gcov_merge_time_profile()`, `__gcov_merge_icall_topn()`, and `__gcov_exit()`. The file uses shared `gcov_lock`, `gcov_info_link()`, `gcov_info_version()`, `gcov_events_enabled`, and `gcov_event()`.

## Control flow
When GCC constructor code calls `__gcov_init()`, the function takes `gcov_lock`, records and logs the first observed GCC version magic, links the object into the compiler-specific gcov list, and notifies the debugfs event consumer if events are enabled. The merge and flush symbols return immediately because kernel gcov does not rely on libgcov process-exit merge logic.

## State and persistence
The only local state is a static `gcov_version` used for one-time logging. Persistent runtime state is owned by the compiler-specific backend list and debugfs node tree. There is no on-disk persistence and no ownership transfer of the compiler-generated `gcov_info` object.

## Dependencies and integration points
This file is the GCC-specific registration bridge between instrumented object constructors and the generic kernel gcov stack. It depends on `gcov.h`, exported kernel symbols for modules, and the debugfs event path in `fs.c`. Instrumented modules link against these symbols when built with coverage enabled.

## Risks and test signals
Risks include missing newly introduced GCC merge symbols, event ordering before debugfs initialization, version-magic mismatches hidden by one-time logging only, and module unload requiring other code to unlink/remove data correctly. Test signals include module load registering coverage, first-version printk, debugfs event replay after late gcov fs init, and successful linking of coverage-instrumented objects across GCC versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/gcov/gcc_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/gcov/gcov.h -->
# sources/distributed-fs/ceph-client/kernel/gcov/gcov.h

## Purpose
`gcov.h` defines the shared internal contract between compiler-specific gcov backends, registration code, and the debugfs exporter. It hides compiler-private `struct gcov_info` layouts while exposing uniform operations to enumerate, serialize, copy, reset, and combine coverage data.

## Important APIs, types, and functions
The header defines gcda constants `GCOV_DATA_MAGIC`, `GCOV_TAG_FUNCTION`, `GCOV_TAG_COUNTER_BASE`, and `GCOV_TAG_FOR_COUNTER()`, plus `gcov_type` sized by native word width. It forward-declares `struct gcov_info`, declares all `gcov_info_*()` operations, `convert_to_gcda()`, `gcov_event()`, `gcov_enable_events()`, `store_gcov_u32()`, `store_gcov_u64()`, and the `struct gcov_link` array used for companion file symlinks.

## Control flow
There is no runtime control flow in the header, but it defines the call graph contract: compiler constructors register `gcov_info`; generic code enumerates with `gcov_info_next()`, builds debugfs nodes through `gcov_event()`, converts objects through `convert_to_gcda()`, and duplicates/adds/resets through the compiler backend functions.

## State and persistence
The header declares shared global state `gcov_events_enabled` and `gcov_lock`, while actual state lives in backend lists and debugfs nodes. `struct gcov_link` instances identify build-tree/source-tree link targets but do not persist data.

## Dependencies and integration points
`gcov.h` includes module and type definitions and is included by GCC, Clang, base registration, and filesystem exporter code. Its opaque layout boundary is the key integration point that allows GCC and Clang to provide different in-memory metadata while sharing the same debugfs frontend.

## Risks and test signals
Risks include stale prototypes when backend APIs change, incorrect gcov constants breaking userspace parsing, and ABI drift where generic code accidentally assumes a concrete `gcov_info` layout. Test signals include building both GCC and Clang coverage configurations, sparse/compiler warnings on prototypes, and userspace gcov successfully reading generated `.gcda` files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/gcov/gcov.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/gen_kheaders.sh -->
# sources/distributed-fs/ceph-client/kernel/gen_kheaders.sh

## Purpose
`gen_kheaders.sh` builds the compressed kernel header archive used by `CONFIG_IKHEADERS`. It copies selected source-tree and object-tree headers into a temporary directory, strips non-SPDX block comments, emits make dependencies, and produces a reproducible tar.xz archive.

## Important APIs, types, and functions
The script inputs are `tarfile`, `srclist`, `objlist`, and `timestamp`; environment dependencies include `srctree`, `TAR`, and `XZ`. It creates a dependency file named after the tarball, uses `sed` to normalize source paths and dependency lines, pipes file lists through tar extraction into `tmpdir`, uses `find -print0` plus parallel `xargs perl -pi` for comment stripping, and invokes tar with owner/group/sort/mode/mtime normalization.

## Control flow
The script writes the make dependency fragment first, recreates a `.tmp_dir` beside the output archive, copies source-list files relative to `srctree`, copies object-list files from the current object tree, strips C block comments except SPDX text, then creates the final xz-compressed archive with deterministic metadata. Temporary content is removed at the end.

## State and persistence
Persistent outputs are the requested tarball and its sidecar dependency file. Temporary state is confined to `${dir}/.tmp_dir` and `${tmpdir}.contents.txt`, both removed on the normal path. Because `set -e` is active, failures may leave partial temporary directories for inspection or cleanup by the build.

## Dependencies and integration points
This script is invoked by the kernel build for in-kernel headers. It depends on GNU-ish tar features, xz integration through tar `-I`, Perl, xargs with null-delimited input, and build-system-provided file lists. The dependency file integrates the archive into make's incremental rebuild logic while intentionally excluding `include/generated/autoconf.h` from the object dependency list.

## Risks and test signals
Risks include unescaped paths in dependency output, comment stripping changing headers unexpectedly, non-GNU tar incompatibility, stale temp directories after interrupted builds, and dependence on `srctree` being set. Test signals include reproducible archive hashes with a fixed timestamp, successful extraction of source and generated headers, dependency rebuilds when listed headers change, SPDX comments preserved, and builds with paths containing unusual characters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/gen_kheaders.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/groups.c -->
# sources/distributed-fs/ceph-client/kernel/groups.c

## Purpose
`groups.c` implements supplementary group ID storage and system call support. It allocates/refcounts `struct group_info`, copies group IDs between userspace and kernel credentials with namespace mapping, sorts and searches group arrays, and applies group changes through the credential and LSM frameworks.

## Important APIs, types, and functions
Exported helpers include `groups_alloc()`, `groups_free()`, `groups_sort()`, `groups_search()`, `set_groups()`, `set_current_groups()`, `in_group_p()`, and `in_egroup_p()`. Syscalls are `getgroups` and `setgroups`. Internal helpers include `groups_to_user()`, `groups_from_user()`, `gid_cmp()`, and `may_setgroups()`.

## Control flow
`setgroups()` checks namespace capability and `NGROUPS_MAX`, allocates a flexible `group_info`, copies and validates user GIDs as `kgid_t` values in the current user namespace, sorts them, then installs them through `set_current_groups()`. `set_current_groups()` prepares copy-on-write credentials, replaces the group pointer with proper refcounting, runs `security_task_fix_setgroups()`, and commits or aborts. `getgroups()` reports the current group count or copies mapped GIDs to userspace. Membership checks compare fsgid/egid first and fall back to binary search.

## State and persistence
Group membership is runtime credential state attached to `struct cred`; updates use copy-on-write credential replacement, not in-place mutation. `group_info` is refcounted elsewhere and freed with `kvfree()`. User namespace mapping affects the userspace representation, but group arrays store kernel IDs. There is no disk persistence.

## Dependencies and integration points
This file integrates with credentials, user namespaces, LSM hooks, syscall argument copying, kernel sorting, capability checks, and exported group helpers used by permission checks across filesystems and kernel subsystems. It relies on callers maintaining sorted supplementary groups for `groups_search()`.

## Risks and test signals
Risks include invalid namespace ID translation, unsorted group arrays causing false negatives, refcount leaks on credential errors, capability semantics around `userns_may_setgroups()`, and large allocations near `NGROUPS_MAX`. Test signals include `getgroups` size-probe behavior, `setgroups` permission denial in user namespaces, invalid GID rejection, sorted membership checks, LSM denial path cleanup, and fsgid/egid fast-path membership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/groups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/hung_task.c -->
# sources/distributed-fs/ceph-client/kernel/hung_task.c

## Purpose
`hung_task.c` implements `khungtaskd`, the kernel watchdog that detects tasks stuck in uninterruptible sleep for too long. It emits diagnostics, optional all-CPU backtraces/system information, blocker ownership hints, counters visible through sysctl, and can panic when configured.

## Important APIs, types, and functions
Key globals are `sysctl_hung_task_timeout_secs`, `sysctl_hung_task_check_interval_secs`, `sysctl_hung_task_check_count`, `sysctl_hung_task_warnings`, `sysctl_hung_task_detect_count`, `sysctl_hung_task_panic`, `hung_task_si_mask`, `watchdog_task`, and suspend/panic flags. Important functions are `task_is_hung()`, `debug_show_blocker()`, `hung_task_info()`, `check_hung_uninterruptible_tasks()`, `proc_dohung_task_detect_count()`, `proc_dohung_task_timeout_secs()`, `reset_hung_task_detector()`, `hungtask_pm_notify()`, `watchdog()`, and `hung_task_init()`.

## Control flow
`khungtaskd` sleeps for the configured interval, then scans process threads under RCU unless reset or suspended. `task_is_hung()` filters for `TASK_UNINTERRUPTIBLE` tasks that are not killable, idle, or frozen and whose context switch count has not changed since the last check. Detected tasks increment the global counter, trigger tracepoints, print task and blocker diagnostics while warnings remain or panic is pending, update sys-info mask selection, and eventually call `panic()` if the per-round panic threshold is reached. The scan periodically breaks and reacquires RCU to avoid excessive grace-period and preemption latency.

## State and persistence
State is runtime-only: per-task `last_switch_count` and `last_switch_time`, global sysctl tunables, an atomic detection counter, warning budget, reset flag, suspend flag, and panic notification flag. Sysctl writes can reset the detect counter only by writing zero and wake the watchdog after timeout changes. No state persists beyond boot.

## Dependencies and integration points
The file integrates with scheduler task state, tracepoints, sysctl, panic notifiers, PM notifiers, freezer/suspend lifecycle, RCU task iteration, lock/blocker owner helpers for mutex/semaphore/rwsem, `sys_info()`, and NMI watchdog touch points. It exports `reset_hung_task_detector()` for subsystems that need to suppress false positives after long stalls.

## Risks and test signals
Risks include false positives during heavy stalls or suspend transitions, races while reading task state and blocker owners, warning suppression hiding later hangs, panic threshold semantics changing operator expectations, and scan count limits missing tasks. Test signals include sysctl interval and timeout updates, reset behavior, D-state task detection, TASK_KILLABLE/TASK_IDLE/TASK_FROZEN exclusion, blocker owner printing, suspend/resume suppression, all-CPU backtrace option, and panic-on-hung-task boot/sysctl settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/hung_task.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/iomem.c -->
# sources/distributed-fs/ceph-client/kernel/iomem.c

## Purpose
`iomem.c` implements `memremap()` and managed wrappers for mapping physical memory resources as normal kernel pointers when `__iomem` accessors are not appropriate. It chooses direct-map access for suitable system RAM and falls back to cacheable/write-through/write-combine ioremap modes for non-RAM resources.

## Important APIs, types, and functions
Public APIs are `memremap()`, `memunmap()`, `devm_memremap()`, and `devm_memunmap()`. Internal helpers include weak/default `arch_memremap_wb()`, `arch_memremap_can_ram_remap()`, `try_ram_remap()`, `devm_memremap_release()`, and `devm_memremap_match()`.

## Control flow
`memremap()` first rejects empty flags and mixed RAM/non-RAM ranges. For `MEMREMAP_WB`, RAM ranges may return the linear direct-map address if the PFN is valid, not highmem, and the architecture permits it; otherwise it uses the architecture write-back remap. If a mapping is still absent and the target is system RAM with non-WB flags, it warns and fails to avoid cache aliasing. Non-RAM WT and WC requests then use `ioremap_wt()` or `ioremap_wc()`. `memunmap()` only calls `iounmap()` for addresses recognized as ioremap mappings. Devres wrappers allocate a resource record, map, register release, and later release by matching the returned pointer.

## State and persistence
Mappings persist until `memunmap()` or device-managed release. Direct-map WB mappings do not allocate a new virtual mapping and therefore are not unmapped. Device-managed mappings are tied to the `struct device` devres lifecycle. There is no disk persistence.

## Dependencies and integration points
The file depends on the resource tree via `region_intersects()`, architecture overrides for cacheable remap behavior, PFN/page/highmem helpers, ioremap variants, devres, and exported symbols used by drivers and persistent memory subsystems. It bridges resource metadata and virtual address mapping policy.

## Risks and test signals
Risks include aliasing system RAM with non-WB attributes, direct-map assumptions on architecture-specific memory encryption/decryption flags, mixed resource detection failures, highmem handling, and devres double-release warnings. Test signals include mapping RAM with WB, rejecting RAM WT/WC, mapping device memory with WC/WT/WB fallback, `memunmap()` on direct-map versus ioremap addresses, and devm cleanup on probe failure/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/iomem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/irq/Kconfig

## Purpose
`irq/Kconfig` defines feature switches for the generic IRQ subsystem. It lets architecture and subsystem code select generic probing, sparse descriptors, IRQ domains, generic chips, simulated IRQs, IPI support, MSI hierarchy, debugfs, migration, statistics snapshots, forced threading, and KUnit tests.

## Important APIs, types, and functions
This is declarative Kconfig, not C code. Important symbols include `MAY_HAVE_SPARSE_IRQ`, `GENERIC_IRQ_PROBE`, `GENERIC_IRQ_SHOW`, `GENERIC_IRQ_EFFECTIVE_AFF_MASK`, `GENERIC_PENDING_IRQ`, `GENERIC_IRQ_MIGRATION`, `GENERIC_IRQ_CHIP`, `IRQ_DOMAIN`, `IRQ_SIM`, `IRQ_DOMAIN_HIERARCHY`, `GENERIC_IRQ_IPI`, `GENERIC_IRQ_IPI_MUX`, `GENERIC_MSI_IRQ`, `GENERIC_IRQ_STAT_SNAPSHOT`, `IRQ_FORCED_THREADING`, `SPARSE_IRQ`, `GENERIC_IRQ_DEBUGFS`, `GENERIC_IRQ_KEXEC_CLEAR_VM_FORWARD`, `IRQ_KUNIT_TEST`, `GENERIC_IRQ_MULTI_HANDLER`, and `DEPRECATED_IRQ_CPU_ONOFFLINE`.

## Control flow
Kconfig selection controls which files are built and which conditional paths compile in the IRQ core. For example `GENERIC_IRQ_CHIP` selects `IRQ_DOMAIN`, `IRQ_SIM` selects `IRQ_WORK` and `IRQ_DOMAIN`, `GENERIC_IRQ_IPI` depends on SMP and selects hierarchy domains, and `IRQ_KUNIT_TEST` depends on built-in KUnit and sparse IRQ support.

## State and persistence
The file contributes build-time configuration only. Its choices become persistent for a built kernel through `.config`, generated headers, and compiled code paths, but it maintains no runtime state itself.

## Dependencies and integration points
This file drives `irq/Makefile` object inclusion and preprocessor paths in the IRQ implementation. It is selected by architecture Kconfig files, irqchip drivers, MSI/IOMMU code, debugfs, procfs, PM, SMP, and KUnit.

## Risks and test signals
Risks include missing `select` dependencies causing link errors, enabling options on unsupported architectures, stale deprecated options, and test configs that cannot satisfy CPU/hotplug assumptions. Test signals include allmodconfig/allyesconfig builds, architecture defconfigs with sparse and non-sparse IRQs, debugfs and simulated IRQ configs, IPI hierarchy builds, and KUnit `irq_test_cases`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/Makefile -->
# sources/distributed-fs/ceph-client/kernel/irq/Makefile

## Purpose
`irq/Makefile` maps IRQ subsystem configuration symbols to object files. It always builds the generic descriptor, handler, management, spurious, resend, chip, dummy-chip, devres, and kexec code, then conditionally includes domain, simulation, proc, migration, PM, MSI, IPI, debugfs, matrix allocator, and KUnit test objects.

## Important APIs, types, and functions
Always-built objects are `irqdesc.o`, `handle.o`, `manage.o`, `spurious.o`, `resend.o`, `chip.o`, `dummychip.o`, `devres.o`, and `kexec.o`. Conditional objects include `generic-chip.o`, `autoprobe.o`, `irqdomain.o`, `irq_sim.o`, `proc.o`, `migration.o`, `cpuhotplug.o`, `pm.o`, `msi.o`, `ipi.o`, `ipi-mux.o`, `affinity.o`, `debugfs.o`, `matrix.o`, and `irq_test.o`.

## Control flow
The build system appends objects to `obj-y` according to configuration. This determines which APIs are compiled and whether internal fallback stubs in headers are used.

## State and persistence
The file is build metadata only. Its effects persist in the final kernel image or modules but it owns no runtime data.

## Dependencies and integration points
It integrates directly with `irq/Kconfig` symbols and the top-level kernel build. Object ordering matters for built-in linkage only insofar as all generic core pieces must be present before conditional extension code references them.

## Risks and test signals
Risks include missing an object for a selected symbol, compiling tests without required helpers, and stale object names after file moves. Test signals include configuration matrix builds for `GENERIC_IRQ_CHIP`, `IRQ_DOMAIN`, `IRQ_SIM`, `GENERIC_IRQ_IPI`, `GENERIC_IRQ_DEBUGFS`, and `IRQ_KUNIT_TEST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/affinity.c -->
# sources/distributed-fs/ceph-client/kernel/irq/affinity.c

## Purpose
`affinity.c` computes default interrupt affinity masks for multiqueue devices and determines a suitable vector count from driver affinity requirements. It spreads managed vectors over present CPUs while preserving pre/post vectors that should use default affinity.

## Important APIs, types, and functions
Public functions are `irq_create_affinity_masks()` and `irq_calc_affinity_vectors()`. The helper `default_calc_sets()` fills a single affinity set. The code operates on `struct irq_affinity`, `struct irq_affinity_desc`, `irq_default_affinity`, CPU masks, and `group_cpus_evenly()`.

## Control flow
`irq_create_affinity_masks()` subtracts pre/post vectors from total vectors, installs a default set calculator when the caller did not provide one, asks the callback to partition affinity vectors into sets, allocates one descriptor per vector, fills pre vectors with default affinity, spreads each set with `group_cpus_evenly()`, fills any trailing or excess vectors with default affinity, and marks the actual affinity range as managed. `irq_calc_affinity_vectors()` rejects configurations where reserved vectors exceed the minimum and otherwise returns reserved vectors plus either callback-limited or CPU-count-limited affinity vectors.

## State and persistence
The only persisted state is the caller-owned returned `irq_affinity_desc` array. The function may mutate `affd->calc_sets`, `affd->nr_sets`, and `affd->set_size[]` via the callback. No global state is modified.

## Dependencies and integration points
This file is used by PCI/MSI and other multiqueue interrupt allocation paths before descriptors are allocated. It depends on SMP CPU masks, `irq_default_affinity`, allocation helpers, and `group_cpus_evenly()` from the CPU grouping code.

## Risks and test signals
Risks include off-by-one handling of pre/post vectors, mismatched callback set sizes versus available vectors, empty CPU-group allocation failures, `IRQ_AFFINITY_MAX_SETS` overflow, and surprising default-affinity fallback for non-managed vectors. Test signals include vector counts below, equal to, and above reserved pre/post counts; multiple set layouts; CPU hotplug/topology variations; allocation failure; and managed mask propagation into descriptor allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/affinity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/autoprobe.c -->
# sources/distributed-fs/ceph-client/kernel/irq/autoprobe.c

## Purpose
`autoprobe.c` implements the legacy generic IRQ autodetection API. Drivers can enable probing, stimulate hardware, then ask which unassigned interrupt line fired.

## Important APIs, types, and functions
Public exported APIs are `probe_irq_on()`, `probe_irq_mask()`, and `probe_irq_off()`. The file uses the `probing_active` mutex, descriptor iteration helpers, `IRQS_AUTODETECT`, `IRQS_WAITING`, `IRQS_PENDING`, `irq_settings_can_probe()`, `irq_activate_and_startup()`, and `irq_shutdown_and_deactivate()`.

## Control flow
`probe_irq_on()` synchronizes async work, serializes probing, activates eligible unassigned probeable IRQs once to flush old interrupts, waits, then marks them autodetect/waiting and starts them again before waiting for spurious triggers. Lines that already triggered are shut down; low-numbered waiting lines are returned in a mask. `probe_irq_mask()` and `probe_irq_off()` scan all autodetect descriptors, determine which lines cleared `IRQS_WAITING`, shut them down, clear autodetect state, unlock the mutex, and return a bitmap or a single IRQ/negative ambiguous result.

## State and persistence
Probe state lives transiently in descriptor `istate` bits and the global `probing_active` mutex. The API mutates hardware interrupt activation state during the probe window and restores lines by shutdown/deactivation afterward.

## Dependencies and integration points
The file depends on generic IRQ descriptors, chip startup/shutdown, descriptor locking, async synchronization, and legacy driver APIs exported to modules. It assumes unassigned handlers leave triggered autodetect interrupts disabled with `IRQS_WAITING` cleared.

## Risks and test signals
Risks include races with real IRQ users, ambiguous multiple triggers, limited return masks for low IRQ numbers, drivers forgetting to call off/mask and holding the mutex, and chip callbacks that do not support probe type. Test signals include no-trigger, single-trigger, multi-trigger, longstanding-spurious filtering, `probe_irq_mask()` cleanup, and overlap attempts from multiple callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/autoprobe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/chip.c -->
# sources/distributed-fs/ceph-client/kernel/irq/chip.c

## Purpose
`chip.c` is the generic IRQ-chip and flow-handler core. It configures IRQ chips and handlers, manages startup/shutdown/disable/mask/unmask state, implements standard level/edge/fasteoi/percpu/NMI flow handlers, supports chained interrupts, forwards operations through IRQ domain hierarchies, and manages chip runtime PM.

## Important APIs, types, and functions
Configuration APIs include `irq_set_chip()`, `irq_set_irq_type()`, `irq_set_handler_data()`, `irq_set_msi_desc[_off]()`, `irq_set_chip_data()`, `irq_get_irq_data()`, `__irq_set_handler()`, `irq_set_chained_handler_and_data()`, `irq_set_chip_and_handler_name()`, and `irq_modify_status()`. Lifecycle helpers include `irq_startup()`, `irq_activate()`, `irq_shutdown()`, `irq_shutdown_and_deactivate()`, `irq_disable()`, `mask_irq()`, `unmask_irq()`, and percpu enable/disable. Flow handlers include `handle_simple_irq()`, `handle_level_irq()`, `handle_fasteoi_irq()`, `handle_fasteoi_nmi()`, `handle_edge_irq()`, `handle_percpu_irq()`, and `handle_percpu_devid_irq()`. Hierarchy helpers include the `irq_chip_*_parent()` family, MSI compose, redirect affinity, and PM get/put.

## Control flow
Startup clears disable depth, handles managed-affinity interrupts specially, activates domains, optionally sets affinity before or after chip startup, and may resend pending interrupts. Shutdown clears resend state, increments depth, calls chip shutdown or disable, marks disabled/masked, and deactivates the domain when requested. Flow handlers lock the descriptor, perform chip-specific ack/mask/eoi operations, test PM and action eligibility, update stats, run handlers through `handle_irq_event()`, and unmask or resend according to type and oneshot state. Chained handler installation marks descriptors no-probe/no-request/no-thread, installs a synthetic action, takes chip PM, and starts the line immediately.

## State and persistence
Persistent state is stored in `struct irq_desc` and `struct irq_data`: chip pointers, handler data, MSI descs, status bits, `IRQD_*` state, disable depth, action list, threaded oneshot state, affinity, and PM references. Hierarchical domains persist parent `irq_data` chains. No disk persistence exists.

## Dependencies and integration points
This file is used by nearly every irqchip driver and interrupt consumer. It depends on descriptor locking from `irqdesc.c`, status helpers from `settings.h`, event execution from `handle.c`, irqdomain activation/deactivation, resend/spurious/PM support, tracepoints, kernel stats, SMP affinity, and MSI/domain hierarchy callbacks.

## Risks and test signals
Risks include imbalanced disable depth for managed interrupts, lazy disable leaving unsafe devices unmasked, action-less chained IRQ misuse, incorrect ack/mask/eoi ordering for controller type, pending resend loops on edge interrupts, parent hierarchy callback absence, runtime PM reference leaks, and races with affinity migration. Test signals include level/edge/fasteoi/oneshot threaded IRQs, chained controller setup/removal, managed IRQ CPU hotplug, domain activation failure, wakeup during suspend, parent-domain forwarding, `IRQCHIP_EOI_THREADED`, and KUnit depth/hotplug tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/chip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/cpuhotplug.c -->
# sources/distributed-fs/ceph-client/kernel/irq/cpuhotplug.c

## Purpose
`cpuhotplug.c` migrates interrupts away from CPUs going offline and restores managed interrupt affinity when CPUs come online. It protects both ordinary affinity masks and managed MSI-style interrupts across CPU hotplug and isolation scenarios.

## Important APIs, types, and functions
Public functions are `irq_migrate_all_off_this_cpu()` and `irq_affinity_online_cpu()`. Internal helpers are `irq_needs_fixup()`, `migrate_one_irq()`, `hk_should_isolate()`, and `irq_restore_affinity_of_irq()`. It uses `irq_fixup_move_pending()`, `irq_force_complete_move()`, `irq_do_set_affinity()`, managed-shutdown flags, pending masks, `cpu_online_mask`, and housekeeping masks.

## Control flow
During offline migration, every active IRQ is locked and passed to `migrate_one_irq()`. That function skips per-CPU, stopped, or non-affine interrupts, completes pending move cleanup, chooses a pending or current affinity mask, masks chips that cannot move in process context, shuts down managed IRQs with no online target, or reassigns non-managed IRQs to the online CPU mask if necessary. On CPU online, the code scans active IRQs under sparse-lock protection and restarts managed shutdown IRQs whose affinity includes the new CPU, then optionally updates affinity to isolate from non-housekeeping CPUs.

## State and persistence
State changes persist in descriptor and irqdata flags: pending move masks, effective affinity, managed shutdown, disable depth/start state, and optional affinity notification work. No state is external to the IRQ core.

## Dependencies and integration points
The file integrates with the CPU hotplug state machine, generic pending IRQ migration, managed IRQ affinity, housekeeping CPU isolation, irqchip affinity callbacks, and descriptor iteration. It relies on the outgoing CPU already being removed from `cpu_online_mask` when migration runs.

## Risks and test signals
Risks include failing to migrate an IRQ whose effective mask contains only the dying CPU, breaking user affinity unexpectedly, not preserving a pending setaffinity request, managed IRQ depth imbalance, `-ENOSPC` from vector allocation, and isolation behavior moving single-target IRQs unexpectedly. Test signals include CPU offline/online with managed and unmanaged IRQs, pending affinity move during hotplug, chips requiring mask during migration, no online CPU in affinity mask, vector exhaustion fallback, and housekeeping isolation configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/cpuhotplug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/debug.h -->
# sources/distributed-fs/ceph-client/kernel/irq/debug.h

## Purpose
`debug.h` provides a small internal diagnostic helper for printing an IRQ descriptor to the kernel log. It is included by `internals.h` for use in bad/spurious IRQ paths.

## Important APIs, types, and functions
The only function is `print_irq_desc(unsigned int irq, struct irq_desc *desc)`. It uses local macros to print selected descriptor status flags and internal state bits, and a static ratelimit state to avoid flooding.

## Control flow
When called, the helper checks its ratelimit, prints the IRQ number, descriptor pointer, depth, counts, flow handler pointer, chip pointer, action/handler pointer, and selected `_IRQ_*` and `IRQS_*` bits.

## State and persistence
The helper has only a static ratelimit state. It reads descriptor fields but does not mutate them.

## Dependencies and integration points
It depends on `struct irq_desc`, internal `IRQS_*` definitions, and printk symbol formatting. It is used by `handle_bad_irq()` and dummy chip bad-ack paths to aid debugging of illegal or unhandled interrupts.

## Risks and test signals
Risks include printing stale or partially updated descriptor state if called without appropriate locking, incomplete bit coverage due to the disabled `___PD` macro, and rate limiting hiding repeated issues. Test signals include bad IRQ injection, spurious IRQ reports, and verifying output includes chip/action symbols without log flooding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/debugfs.c -->
# sources/distributed-fs/ceph-client/kernel/irq/debugfs.c

## Purpose
`debugfs.c` exposes IRQ descriptor, irqdata, chip, affinity, and domain state through debugfs when `GENERIC_IRQ_DEBUGFS` is enabled. It also supports writing `trigger` to an IRQ file to inject an interrupt for debugging.

## Important APIs, types, and functions
Public helpers are `irq_debug_show_bits()`, `irq_debugfs_copy_devname()`, and `irq_add_debugfs_entry()`. Core functions are `irq_debug_show()`, `irq_debug_open()`, `irq_debug_write()`, and `irq_debugfs_init()`. Static descriptor tables map chip flags, irqdata states, descriptor settings, and internal states to names.

## Control flow
Initialization creates `/sys/kernel/debug/irq`, initializes domain debugfs, creates `irqs/`, then adds one file per active IRQ. `irq_debug_show()` locks the descriptor, prints handler, device, status, internal state, depth, wake depth, irqdata state, NUMA node, affinity masks, chip hierarchy, and domain-specific debug output. `irq_debug_write()` copies a small command and invokes `irq_inject_interrupt()` for the `trigger` command.

## State and persistence
Debugfs files persist while descriptors exist and the debugfs tree is mounted. `irq_debugfs_copy_devname()` duplicates a device name into `desc->dev_name`, later freed by `irq_remove_debugfs_entry()`. There is no durable persistence.

## Dependencies and integration points
This file integrates with debugfs, irqdomain debugfs, descriptor allocation/free in `irqdesc.c`, injection support selected by Kconfig, SMP affinity masks, hierarchy domains, and chip/domain debug callbacks. It reads live IRQ core state under descriptor lock.

## Risks and test signals
Risks include leaking duplicated device names if descriptors are not removed cleanly, command parsing accepting prefixes by `strncmp()` length, debug output racing with domain removal beyond descriptor lock coverage, and exposing internals in production debugfs. Test signals include debugfs files for early and dynamically allocated IRQs, `trigger` injection, affinity/effective/pending mask output, hierarchy parent output, and descriptor free cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/devres.c -->
# sources/distributed-fs/ceph-client/kernel/irq/devres.c

## Purpose
`devres.c` provides device-managed wrappers for requesting/freeing IRQs, allocating IRQ descriptors, setting up generic IRQ chips, and instantiating IRQ domains. It lets driver probe paths register IRQ resources that are automatically released on device detach or probe failure.

## Important APIs, types, and functions
Public APIs include `devm_request_threaded_irq()`, `devm_request_any_context_irq()`, `devm_free_irq()`, `__devm_irq_alloc_descs()`, `devm_irq_alloc_generic_chip()`, `devm_irq_setup_generic_chip()`, and `devm_irq_domain_instantiate()`. Internal resource records are `struct irq_devres`, `struct irq_desc_devres`, and `struct irq_generic_chip_devres`.

## Control flow
Managed request functions allocate a devres record, call the corresponding request API, fill the IRQ/dev_id on success, and attach the record to the device; failures free the resource and return/log via `dev_err_probe()`. `devm_free_irq()` releases the matching resource manually. Descriptor allocation and generic chip setup follow the same pattern: allocate resource, perform core IRQ operation, then register a release callback that frees descriptors or removes the chip. Domain instantiation stores the domain pointer and removes it on release.

## State and persistence
State is the device's devres list plus underlying IRQ subsystem state. Resources persist until manual devm release, driver unbind, probe failure cleanup, or device teardown. No state survives the device lifecycle.

## Dependencies and integration points
The file integrates driver core devres with generic IRQ request/free, descriptor allocation, generic-chip setup, IRQ domains, module ownership, and device error reporting. It is a convenience and safety layer over core APIs in `manage.c`, `irqdesc.c`, `generic-chip.c`, and `irqdomain.c`.

## Risks and test signals
Risks include mismatched `dev_id` preventing `devm_free_irq()` release, double-free warnings when drivers mix managed and unmanaged APIs, release ordering between domains/chips/descriptors, and over-logging if callers add duplicate probe messages. Test signals include probe failure cleanup, manual `devm_free_irq()`, threaded and any-context requests, descriptor allocation release, generic-chip setup removal, and domain instantiate/remove under driver unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/devres.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/dummychip.c -->
# sources/distributed-fs/ceph-client/kernel/irq/dummychip.c

## Purpose
`dummychip.c` defines generic placeholder IRQ chips used when an interrupt has no real controller or is backed by a very simple dummy source. It prevents NULL chip callbacks and provides diagnostic behavior for illegal vectors.

## Important APIs, types, and functions
The file defines `no_irq_chip` and exported `dummy_irq_chip`. Helpers are `ack_bad()`, `noop()`, and `noop_ret()`. Both chips set `IRQCHIP_SKIP_SET_WAKE`.

## Control flow
`no_irq_chip` uses no-op startup/shutdown/enable/disable and an ack path that prints descriptor diagnostics and calls `ack_bad_irq()`. `dummy_irq_chip` uses no-op startup, shutdown, enable, disable, ack, mask, and unmask callbacks. The generic IRQ core installs `no_irq_chip` by default and drivers may use `dummy_irq_chip` for software/simple sources.

## State and persistence
The chip structures are static global runtime objects. They hold no mutable per-IRQ state.

## Dependencies and integration points
This file integrates with descriptor default initialization, bad IRQ handling, and drivers/tests that need a simple chip implementation. It depends on `print_irq_desc()` and architecture `ack_bad_irq()`.

## Risks and test signals
Risks include accidentally leaving production IRQs on `no_irq_chip`, hiding missing hardware operations behind dummy no-ops, and bad-ack diagnostics firing in paths that should have been masked earlier. Test signals include descriptor defaults, bad IRQ injection, dummy-chip request/startup paths, and no wake callback attempts because of `IRQCHIP_SKIP_SET_WAKE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/dummychip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/generic-chip.c -->
# sources/distributed-fs/ceph-client/kernel/irq/generic-chip.c

## Purpose
`generic-chip.c` provides reusable IRQ chip implementations for common MMIO register layouts. It handles mask/unmask/ack/eoi/wake register operations, allocates and maps generic chips into IRQ domains, sets up direct IRQ ranges, supports alternate chip types by trigger mode, and hooks generic chips into syscore suspend/resume/shutdown.

## Important APIs, types, and functions
Register helpers include `irq_gc_mask_disable_reg()`, `irq_gc_mask_set_bit()`, `irq_gc_mask_clr_bit()`, `irq_gc_unmask_enable_reg()`, `irq_gc_ack_set_bit()`, `irq_gc_ack_clr_bit()`, `irq_gc_mask_disable_and_ack_set()`, `irq_gc_eoi()`, and `irq_gc_set_wake()`. Allocation/setup APIs include `irq_init_generic_chip()`, `irq_alloc_generic_chip()`, `irq_domain_alloc_generic_chips()`, `irq_domain_remove_generic_chips()`, `__irq_alloc_domain_generic_chips()`, `irq_get_domain_generic_chip()`, `irq_map_generic_chip()`, `irq_unmap_generic_chip()`, `irq_setup_generic_chip()`, `irq_setup_alt_chip()`, and `irq_remove_generic_chip()`. `irq_generic_chip_ops` is the standard domain ops table.

## Control flow
Generic callbacks lock `gc->lock`, update mask caches, and write the configured register offset relative to `gc->reg_base`. Domain allocation creates one `irq_chip_generic` per `irqs_per_chip`, initializes optional big-endian accessors and caller init hooks, then links chips into `gc_list`. Mapping validates the hwirq index, initializes mask cache on first install, computes the interrupt bit mask, installs chip/handler/domain info, and applies status flags. Removal unregisters handlers/chips and clears status. Syscore callbacks iterate `gc_list` to call chip or chip-generic suspend/resume/shutdown hooks.

## State and persistence
Persistent runtime state is in each `irq_chip_generic`: register base, lock, mask caches, wake masks, installed/unused bitmaps, chip types, domain pointer, and optional PM callbacks. The global `gc_list` tracks chips for system PM. Per-domain generic chip arrays live until domain removal; direct chips live until explicit removal or driver cleanup.

## Dependencies and integration points
The file depends on MMIO accessors, IRQ domains, descriptor configuration helpers, syscore PM, lockdep class assignment, and driver-provided `struct irq_chip_type` register descriptions. It is used heavily by simple irqchip drivers that do not need bespoke callbacks.

## Risks and test signals
Risks include incorrect mask-cache polarity for hardware, missing locking around shared registers, `irqs_per_chip` over 32-bit mask assumptions, installed/unused bitmap mistakes, alternate chip selection mismatch with trigger type, syscore iterating removed chips, and big-endian accessor misconfiguration. Test signals include register write traces for each helper, domain map/unmap, direct setup/remove, suspend/resume/shutdown callbacks, wake enable validation, nested lock class use, and trigger-type switching through `irq_setup_alt_chip()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/generic-chip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/handle.c -->
# sources/distributed-fs/ceph-client/kernel/irq/handle.c

## Purpose
`handle.c` runs registered IRQ actions once a flow handler has decided an interrupt is serviceable. It handles bad IRQs, no-op actions, threaded handler wakeups, optional long-duration warnings, interrupt randomness/spurious accounting, and architecture root IRQ dispatch for `GENERIC_IRQ_MULTI_HANDLER`.

## Important APIs, types, and functions
Public functions include `handle_bad_irq()`, `no_action()`, `__irq_wake_thread()`, `__handle_irq_event_percpu()`, `handle_irq_event_percpu()`, `handle_irq_event()`, `set_handle_irq()`, and `generic_handle_arch_irq()`. Key state includes `handle_arch_irq`, static key `irqhandler_duration_check_enabled`, and `irqhandler_duration_threshold_ns`.

## Control flow
`handle_irq_event()` clears pending state, marks the irq in-progress, drops the descriptor lock, calls `handle_irq_event_percpu()`, then reacquires the lock and clears in-progress. The per-action loop traces entry/exit, optionally measures handler duration, calls each primary handler, warns if it re-enables interrupts, and wakes the IRQ thread when the result is `IRQ_WAKE_THREAD`. Thread wakeup sets `IRQTF_RUNTHREAD`, updates `threads_oneshot`, increments `threads_active`, and wakes the kthread. Root arch handling wraps the architecture handler in `irq_enter()`, irq-reg save/restore, and `irq_exit()`.

## State and persistence
The file mutates descriptor in-progress and pending bits, action thread flags, oneshot masks, and active thread counters. Duration warning configuration is boot-time state from `irqhandler.duration_warn_us=`. No state is persisted beyond runtime.

## Dependencies and integration points
It integrates with flow handlers in `chip.c`, threaded IRQ management in `manage.c`, spurious detection in `spurious.c`, tracepoints, lockdep hardirq-thread annotations, randomness, per-CPU stats, scheduler kthreads, and architecture entry code.

## Risks and test signals
Risks include lost threaded wakeups, incorrect oneshot mask serialization, handlers enabling IRQs, long-duration static key overhead, lock state mismatches around action execution, and root handler registration races. Test signals include shared IRQ return aggregation, `IRQ_WAKE_THREAD` with and without `thread_fn`, oneshot threaded interrupts, duration warning boot parameter, handler tracepoints, spurious accounting, and architecture multi-handler registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/internals.h -->
# sources/distributed-fs/ceph-client/kernel/irq/internals.h

## Purpose
`internals.h` is the private header for `kernel/irq`. It centralizes internal descriptor state bits, threaded IRQ flags, function prototypes, scoped descriptor lock helpers, irqdata state mutators, stats helpers, PM/debugfs/proc stubs, and optional feature shims used across the IRQ core.

## Important APIs, types, and functions
It defines `MAX_SPARSE_IRQS`, `IRQTF_*` thread bits, `IRQS_*` internal descriptor bits, `IRQ_RESEND`, `IRQ_START_FORCE`, descriptor lock classes/macros `scoped_irqdesc_get_and_lock()` and `scoped_irqdesc_get_and_buslock()`, `irqd_set()/irqd_clear()/irqd_has_set()`, `irq_state_set_disabled()`, `irq_state_set_masked()`, stats helpers, and many prototypes for chip, handle, manage, resend, proc, affinity, PM, debugfs, and pending-move operations.

## Control flow
The header provides inline control helpers rather than standalone runtime flow. Notably, scoped descriptor locks acquire optional chip bus locks then `desc->lock`, and release in reverse order. Feature conditionals replace missing procfs, PM, generic-chip, pending-IRQ, irqdomain hierarchy, and debugfs functionality with no-op stubs.

## State and persistence
It defines names and accessors for state stored in `struct irq_desc` and `struct irq_data`: internal `istate`, thread flags, `IRQD_*` bits, stats, pending masks, and debugfs metadata. The header owns no separate state.

## Dependencies and integration points
Every core IRQ source file depends on this header for shared private contracts. It includes descriptor/stat/PM/scheduler-clock headers, `debug.h`, and `settings.h`, and bridges configuration-specific code paths with inline stubs.

## Risks and test signals
Risks include private state bit collisions, accessor misuse bypassing public IRQ APIs, lock guard lifetime mistakes, feature-stub behavior diverging from compiled implementations, and external inclusion despite the warning. Test signals include sparse and non-sparse builds, procfs/debugfs/PM on-off configs, lockdep coverage of scoped guards, pending migration builds, and compiler warnings when prototypes drift from definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/internals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/ipi-mux.c -->
# sources/distributed-fs/ceph-client/kernel/irq/ipi-mux.c

## Purpose
`ipi-mux.c` multiplexes several virtual IPIs over one physical parent IPI. It creates an IPI irq_domain whose virtual IRQs set per-CPU pending bits and use a caller-provided callback to trigger the actual hardware IPI.

## Important APIs, types, and functions
The central type is per-CPU `struct ipi_mux_cpu` with atomic `enable` and `bits` masks. Public APIs are `ipi_mux_create()` and `ipi_mux_process()`. Internal chip callbacks are `ipi_mux_mask()`, `ipi_mux_unmask()`, and `ipi_mux_send_mask()`, installed in `ipi_mux_chip`. Domain allocation uses `ipi_mux_domain_alloc()` and `ipi_mux_domain_ops`.

## Control flow
`ipi_mux_create()` allocates per-CPU state, creates a named fwnode and linear IPI domain, marks it as single-HW-IPI, allocates virtual IRQs, and stores the send callback. Sending a virtual IPI sets the target CPU's pending bit with release semantics, then sends the physical IPI if the bit was newly pending and enabled. Unmasking enables the local bit and sends a self IPI if work was already pending. The parent physical IPI handler calls `ipi_mux_process()`, which atomically clears enabled pending bits and dispatches each set hwirq through `generic_handle_domain_irq()`.

## State and persistence
State persists globally after creation: `ipi_mux_pcpu`, `ipi_mux_domain`, and `ipi_mux_send`. Each CPU maintains enabled and pending virtual IPI masks atomically. There is no teardown path in this file and no disk persistence.

## Dependencies and integration points
This file depends on SMP, IRQ domains, per-CPU allocation, atomic ordering, generic per-CPU devid IRQ handling, and architecture/irqchip parent IPI code that calls `ipi_mux_process()` when the physical interrupt arrives. It exposes virtual IPIs through the standard generic IPI domain API.

## Risks and test signals
Risks include missing teardown support, `nr_ipi` limited by `int` bit width, memory-ordering bugs that lose IPIs around mask/unmask, duplicate creation returning `-EEXIST`, and parent handlers failing to call `ipi_mux_process()`. Test signals include sending masked then unmasking, multiple virtual IPIs to one CPU, multi-CPU masks, duplicate create failure, invalid `nr_ipi`/callback rejection, and stress tests around concurrent send/unmask.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/ipi-mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/ipi.c -->
# sources/distributed-fs/ceph-client/kernel/irq/ipi.c

## Purpose
`ipi.c` implements generic APIs for reserving, destroying, querying, and sending inter-processor interrupts through IRQ domains. It abstracts both single-HW-IRQ IPI domains and per-CPU-HW-IRQ domains.

## Important APIs, types, and functions
Public functions are `irq_reserve_ipi()`, `irq_destroy_ipi()`, `ipi_get_hwirq()`, `ipi_send_single()`, and `ipi_send_mask()`. Internal fast paths are `__ipi_send_single()`, `__ipi_send_mask()`, and verification helper `ipi_send_verify()`. The code uses `irq_domain_is_ipi*()` helpers, `__irq_domain_alloc_irqs()`, `irq_domain_free_irqs()`, descriptor allocation/free, irqdata affinity masks, and chip `ipi_send_single`/`ipi_send_mask` callbacks.

## Control flow
Reservation validates the domain and destination mask, computes the number of Linux IRQs needed, requires consecutive CPU masks for per-CPU domains, allocates descriptors, allocates domain IRQs, copies destination affinity into each irqdata, stores the per-CPU offset, and marks IRQs no-balancing. Destroy validates that the target is an IPI and that the requested destroy mask is a subset of the reservation, then frees one or many virqs depending on domain type. Send APIs validate chip callbacks and destination subset, then either call a mask send callback or iterate CPUs calling single-send with adjusted per-CPU irqdata.

## State and persistence
IPI reservation state persists in allocated descriptors, irqdomain mappings, irqdata affinity masks, and `ipi_offset`. It lasts until `irq_destroy_ipi()` or domain teardown. No state is persistent outside the running kernel.

## Dependencies and integration points
The file integrates SMP core code, architecture irqchip IPI drivers, IRQ domains, descriptor allocation, and generic chip send callbacks. It is selected by `GENERIC_IRQ_IPI` and assumes domain flags correctly identify IPI type and bus token behavior.

## Risks and test signals
Risks include accepting non-consecutive per-CPU masks, failing to unwind descriptor/domain allocation, invalid subset checks on destroy/send, using wrong irqdata for per-CPU domains, and chip implementations missing required send callbacks. Test signals include single and per-CPU IPI domains, masks with holes, empty and impossible destination masks, reserve/destroy subset behavior, `ipi_get_hwirq()` for valid and invalid CPUs, and send-single/send-mask fallback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/ipi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/irq_sim.c -->
# sources/distributed-fs/ceph-client/kernel/irq/irq_sim.c

## Purpose
`irq_sim.c` implements an interrupt simulator backed by an IRQ domain and `irq_work`. It is useful for tests and drivers that need software-triggerable IRQ lines without real hardware.

## Important APIs, types, and functions
Core types are `struct irq_sim_work_ctx` and `struct irq_sim_irq_ctx`. Public APIs are `irq_domain_create_sim()`, `irq_domain_create_sim_full()`, `irq_domain_remove_sim()`, `devm_irq_domain_create_sim()`, and `devm_irq_domain_create_sim_full()`. The simulated chip is `irq_sim_irqchip` with mask/unmask, set_type, get/set pending state, and resource request/release callbacks. Domain operations are `irq_sim_domain_map()` and `irq_sim_domain_unmap()`.

## Control flow
Domain creation allocates work context, a pending bitmap, and a linear IRQ domain using the work context as host data. Mapping allocates per-IRQ context, installs `irq_sim_irqchip`, chip data, `handle_simple_irq`, and status flags. Setting pending state on an enabled IRQ sets a bit and queues hard irq_work. The irq_work handler drains pending bits, resolves each hwirq to a virq, and calls `handle_simple_irq()` on its descriptor. Removal synchronizes irq_work, frees the bitmap/work context, and removes the domain; devm variants register this removal as a device action.

## State and persistence
Simulator state persists in the domain host data, pending bitmap, hard irq_work item, optional user ops/data, and per-IRQ enabled flags. Pending bits are transient and cleared by the work handler. The state ends with explicit or devm domain removal.

## Dependencies and integration points
The file depends on IRQ domains, simple IRQ flow handling, irq_work, bitmap allocation, irqchip state APIs, devres, and optional `struct irq_sim_ops` callbacks for request/release notifications. It is selected by `IRQ_SIM`.

## Risks and test signals
Risks include pending-state operations ignored while masked, work handler resolving an unmapped IRQ during teardown if synchronization is wrong, unsupported non-edge trigger types, callback failures during request, and missing descriptor freeing by domain callers. Test signals include create/remove, devm cleanup, pending state set/get, masked pending behavior, request/release callbacks, trigger type rejection, and multiple pending IRQ drain ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/irq_sim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/irq_test.c -->
# sources/distributed-fs/ceph-client/kernel/irq/irq_test.c

## Purpose
`irq_test.c` is a KUnit suite for IRQ management behavior, focused on descriptor disable depth, free/re-request behavior, managed IRQ shutdown/startup depth, and CPU hotplug interaction.

## Important APIs, types, and functions
The suite defines a fake `irq_chip` with no-op callbacks and an affinity setter that updates effective affinity. Test helpers include `irq_test_setup_fake_irq()`, `noop_handler()`, and chip no-op callbacks. Test cases are `irq_disable_depth_test()`, `irq_free_disabled_test()`, `irq_shutdown_depth_test()`, and `irq_cpuhotplug_test()`, registered in `irq_test_suite`.

## Control flow
Each test allocates one sparse IRQ descriptor, assigns the fake chip and `handle_simple_irq`, clears no-request state, requests the IRQ, manipulates disable/free/shutdown/hotplug operations, and asserts descriptor depth and irqdata state. Managed shutdown tests create managed affinity descriptors, call `irq_shutdown_and_deactivate()` under descriptor lock, reactivate/start managed IRQs, then verify disabled depth is preserved until `enable_irq()`. The hotplug test removes and re-adds CPU1 for a managed IRQ affine to CPU1.

## State and persistence
State is temporary test state in dynamically allocated IRQ descriptors and a fake chip. Tests may affect CPU hotplug state but restore CPU1 by calling `add_cpu(1)` after removal. No state should persist after the suite beyond normal KUnit lifecycle cleanup assumptions.

## Dependencies and integration points
The suite depends on built-in KUnit, sparse IRQ support, IRQ domains/descriptor allocation, CPU hotplug APIs, SMP for managed tests, and internal IRQ helpers via `internals.h`. Kconfig gates it behind `IRQ_KUNIT_TEST`.

## Risks and test signals
Risks include CPU1 availability/hotpluggability assumptions causing skips, allocated descriptors not explicitly freed in some paths, architecture defaults requiring no-request clearing, and test behavior that is too tied to internal depth semantics. Passing test signals are preserved disable depth across disable/enable, free/re-request after disabled free, managed shutdown depth balance, and hotplug not re-enabling a manually disabled managed IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/irq_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/irqdesc.c -->
# sources/distributed-fs/ceph-client/kernel/irq/irqdesc.c

## Purpose
`irqdesc.c` manages IRQ descriptors: early initialization, sparse/non-sparse allocation, descriptor lookup, sysfs/debugfs/proc registration, generic IRQ dispatch by number/domain, demux redirection, dynamic descriptor allocation/free, per-CPU statistics, and lockdep class assignment.

## Important APIs, types, and functions
Key APIs include `early_irq_init()`, `irq_to_desc()`, `irq_get_nr_irqs()`, `irq_set_nr_irqs()`, `irq_lock_sparse()`, `irq_unlock_sparse()`, `handle_irq_desc()`, `generic_handle_irq()`, `generic_handle_irq_safe()`, `generic_handle_domain_irq()`, `generic_handle_domain_irq_safe()`, `generic_handle_domain_nmi()`, `generic_handle_demux_domain_irq()`, `irq_free_descs()`, `__irq_alloc_descs()`, `irq_get_next_irq()`, `__irq_get_desc_lock()`, `__irq_put_desc_unlock()`, `irq_set_percpu_devid()`, `kstat_irqs_cpu()`, `kstat_irqs_usr()`, snapshot helpers, and `__irq_set_lockdep_class()`. Internal structures include sparse maple tree `sparse_irqs`, `sparse_irq_lock`, sysfs kobjects, and per-descriptor masks/stats.

## Control flow
Early init establishes default affinity, asks the architecture for IRQ counts, allocates initial descriptors, and calls architecture early IRQ init. Sparse builds store descriptors in an RCU-enabled maple tree, allocate/free descriptors dynamically, and expose sysfs attributes for counts/chip/hwirq/type/wakeup/name/actions. Non-sparse builds initialize a static array and reset descriptors on free. Dispatch helpers resolve IRQ numbers or domain hwirqs to descriptors and call the installed flow handler, with safe variants saving local IRQ state. Dynamic allocation finds a free range, expands `nr_irqs` when possible, initializes masks/stats/locks, inserts descriptors, and registers sysfs/debugfs/proc entries.

## State and persistence
Persistent runtime state includes global `nr_irqs`, sparse maple tree or static descriptor array, descriptor locks/masks/actions/stats, sysfs kobjects, RCU-delayed descriptor frees, and default affinity masks. Per-IRQ stats persist since boot and may have per-CPU snapshot references when enabled. No disk persistence exists.

## Dependencies and integration points
This file is the backbone for `chip.c`, `handle.c`, irqdomain, procfs, sysfs, debugfs, CPU affinity, KVM symbol users, architecture IRQ initialization, and interrupt statistics exposed to userspace. It depends on maple tree, RCU, kobjects, percpu allocation, cpumasks, and architecture hooks.

## Risks and test signals
Risks include descriptor lifetime races across RCU/debugfs/sysfs/proc, sparse tree allocation range mistakes, non-sparse reset divergence, dispatch from wrong context when IRQ context is enforced, demux redirection to offline CPUs, managed affinity flags set from affinity descriptors, and stat races tolerated with data-race reads. Test signals include sparse and non-sparse boots, dynamic allocation/free/reuse, sysfs attributes, generic domain dispatch, demux redirection, percpu devid setup, kstat reads during free, snapshot stats, and lockdep class changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/irq/irqdesc.c -->

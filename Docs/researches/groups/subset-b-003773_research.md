# Research: subset-b-003773

Grouped source research for subset B work item `subset-b-003773`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bo.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bo.c

## Purpose
This is the main Xe buffer-object implementation. It adapts DRM GEM and TTM buffer objects to Xe memory regions, including system/TT, VRAM, stolen memory, imported dma-bufs, GGTT mappings, CPU mmap faults, shrinker reclaim, purgeable memory, pinned-kernel suspend handling, and user GEM creation ioctls.

## Important APIs, Types, and Functions
Major exported entry points include `xe_bo_init_locked`, `xe_bo_create_locked`, `xe_bo_create_user`, pinned/mapped creation helpers, `xe_bo_pin`, `xe_bo_pin_external`, `xe_bo_unpin`, `xe_bo_validate`, `xe_bo_migrate`, `xe_bo_evict`, `xe_bo_vmap`, `xe_bo_read`, `xe_gem_create_ioctl`, `xe_gem_mmap_offset_ioctl`, `xe_bo_decompress`, shrinker helpers, and pinned suspend helpers such as `xe_bo_evict_pinned` and `xe_bo_restore_pinned`. `xe_ttm_funcs` binds Xe into TTM through create/populate/unpopulate/move/evict/io-memory/access/release callbacks.

## Control Flow
Creation validates flags, size, placement, alignment, fixed ranges, VM reservation sharing, and GGTT insertion before returning a locked or unlocked BO depending on helper. Placement construction converts Xe flags to `ttm_place` arrays, choosing VRAM regions, stolen memory, TT fallback, CPU-visible VRAM constraints, contiguous requirements, and 64K/2M alignment.

TTM movement is centered on `xe_bo_move`. It handles first placement, dma-buf imports, purgeable eviction, TT/System dummy moves, multi-hop system-to-VRAM transitions through TT, GPU copy/clear via `xe_migrate`, CCS side data, and runtime PM bracketing. CPU faults first try a nonblocking fast path, then drop/retry mmap locks when needed, migrate/populate backing store, reject imported or purgeable objects, and install PTEs through TTM. GEM create ioctl validates uAPI fields, VM lookup, caching modes, scanout/visible VRAM constraints, PXP extensions, and GEM handle installation.

## State and Persistence Behavior
The file mutates `struct xe_bo` fields such as flags, placement, tile/vm association, GGTT nodes, `vmap`, pinned-list membership, purgeable state, `backup_obj`, `parent_obj`, CCS metadata, and VM/GPUVA links. It maintains shrinker accounting for populated TT pages, purgeable pages, and global GPU memory tracing. Pinned VRAM BOs can be backed up into system BOs before power loss and restored later, preserving exact placement where required. Purged BOs become terminally invalid and CPU faults/mmap reject them.

## Dependencies and Integration Points
It depends on TTM core, DRM GEM/prime/vma helpers, `dma_resv` fences, Xe validation/drm_exec, VM bind and GPUVA tracking, migrate engines, GGTT, stolen and VRAM managers, runtime PM, PXP, shrinker, SR-IOV VF CCS helpers, and tracepoints. It is called from device creation, ioctls, VM bind, display dumb-buffer creation, PM eviction, debug/test paths, and dma-buf import/export.

## Risks
The highest risks are reservation-lock ordering, asynchronous migration fences, stale VM bindings after move/purge, mismatched shrinker accounting on pin/unpin/populate/unpopulate, and losing VRAM contents across suspend if pinned lists or backup objects are mishandled. CPU mmap behavior must stay consistent with purgeable states and imported dma-bufs. Fixed placement and GGTT insertion are sensitive to tile/SR-IOV assumptions. The purge path must invalidate mappings before freeing pages or userspace/GPU could access discarded memory.

## Test Signals
Useful signals include KUnit `tests/xe_bo.c`, GEM create/mmap ioctl tests, VM bind/evict/rebind stress, dma-buf import/export migration, suspend/resume and hibernate with pinned VRAM, shrinker pressure including DONTNEED/PURGED BOs, visible-VRAM mmap faults, CCS compression/decompression paths, SR-IOV VF CCS movement, and runtime PM fault/migration races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bo.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bo.h

## Purpose
This header defines the public Xe BO contract: memory placement flags, page constants, purgeable states, creation/pinning/migration/mapping APIs, address helpers, shrinker interfaces, and inline accounting helpers used by VM, exec, PM, display, and memory-management code.

## Important APIs, Types, and Functions
Key definitions include `XE_BO_FLAG_*`, memory type aliases `XE_PL_SYSTEM`, `XE_PL_TT`, `XE_PL_VRAM0/1`, `XE_PL_STOLEN`, `enum xe_madv_purgeable_state`, conversion helpers `ttm_to_xe_bo` and `gem_to_xe_bo`, and lifecycle APIs such as `xe_bo_create_user`, `xe_bo_pin`, `xe_bo_validate`, `xe_bo_migrate`, `xe_bo_evict`, `xe_bo_vmap`, `xe_bo_put`, `xe_bo_put_async`, and `xe_bo_shrink`.

## Control Flow
The header itself has no standalone flow, but its inlines enforce required object-lock context for purgeable and memory-type checks. `xe_bo_willneed_get_locked`, `xe_bo_willneed_put_locked`, and VMA count helpers couple VM mappings and dma-buf exports to purgeable state transitions. Deferred put helpers avoid final object destruction in reclaim-tainted or atomic contexts by queuing final reference drops.

## State and Persistence Behavior
Flags declared here determine persistent BO behavior: user vs kernel, valid placements, GGTT mapping, pinned/late restore/no restore, deferred backing, CPU cache requirements, fixed placement, page-table backing, CCS/compression needs, and test-only/internal alignment bits. The purgeable state enum is terminal once `PURGED` is reached.

## Dependencies and Integration Points
It exposes TTM, DRM GEM, GGTT, VM, validation, VRAM, and scatter-gather types to the wider Xe driver. Callers include VM bind, exec, PM eviction, display dumb buffers, dma-buf code, SR-IOV CCS, pagefault handling, and debug/testing modules.

## Risks
Flag combinations are dense and some ranges must remain contiguous, especially VRAM flags. Inlines assume the caller holds the correct `dma_resv` lock; misuse can corrupt purgeable counters or observe stale placement. Header defaults and fallbacks must remain synchronized with `xe_bo.c` and uAPI validation.

## Test Signals
Build coverage catches signature drift. Runtime signals include GEM create placement tests, purgeable madvise/VMA accounting tests, async put paths from interrupt/reclaim-like contexts, migration/pin validation, and address helper checks for system, stolen, and VRAM BOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bo_doc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bo_doc.h

## Purpose
This documentation header describes the design model for Xe buffer objects. It explains TTM-managed placement and eviction, differences between kernel/user/private/external BOs, runtime moves, VM rebinds, and suspend/resume backup of VRAM contents.

## Important APIs, Types, and Functions
There are no executable APIs in this file. The important artifact is the `DOC: Buffer Objects (BO)` kernel-doc block, which documents the intended behavior implemented primarily in `xe_bo.c`, `xe_bo.h`, `xe_bo_types.h`, and `xe_bo_evict.c`.

## Control Flow
The documented flow is creation through placement masks, TTM validation, runtime eviction through the migration engine, VMA invalidation/rebind after moves, suspend-time eviction of user and pinned objects, and resume-time restoration of GGTT mappings and pinned contents.

## State and Persistence Behavior
The document captures persistence expectations: user BOs are evictable, kernel BOs are often pinned/contiguous/GGTT mapped, private BOs share VM reservation state, external BOs can be shared by dma-buf, and VRAM contents must be saved before power loss. It also records current constraints such as contiguous pinned kernel BOs for restore simplicity.

## Dependencies and Integration Points
It describes the relationship between TTM, VM bind, GGTT, migrate engines, suspend/resume PM paths, and user ioctls such as GEM create, mmap offset, and VM bind.

## Risks
The file can become stale as implementation evolves. Its future-work section highlights known design limitations: overbroad pinned backup, contiguous kernel BO requirements, and opportunities to make some kernel BOs evictable. If documentation and code diverge, PM and VM rebind assumptions become harder to audit.

## Test Signals
Documentation accuracy is indirectly tested by BO creation, runtime eviction/rebind, suspend/resume, external dma-buf pinning, and VM fault-mode behavior matching the described model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bo_doc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bo_evict.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bo_evict.c

## Purpose
This file coordinates whole-device BO eviction and restoration for suspend, hibernate, runtime PM transitions, and PCI removal. It is the list-management layer over per-BO helpers in `xe_bo.c`, especially for pinned VRAM objects that TTM cannot evict normally.

## Important APIs, Types, and Functions
Public entry points are `xe_bo_notifier_prepare_all_pinned`, `xe_bo_notifier_unprepare_all_pinned`, `xe_bo_evict_all_user`, `xe_bo_evict_all`, `xe_bo_restore_early`, `xe_bo_restore_late`, `xe_bo_pci_dev_remove_all`, and `xe_bo_pinned_init`. The key internal helper is `xe_bo_apply_to_pinned`, which safely walks pinned lists while dropping the spinlock around slow BO operations.

## Control Flow
Pinned-list operations take a BO reference, move the entry to a temporary list, drop `xe->pinned.lock`, run the requested callback, then splice entries into a destination list. Suspend first evicts non-pinned user BOs via TTM, then pinned external and late kernel BOs, waits for migrate engines, and finally evicts early kernel BOs. Resume restores early BOs before GT init, then late kernel/external BOs after migrate engines are available, remapping GGTT entries where needed. PCI remove evicts/purges normal BOs and dma-unmaps pinned BOs.

## State and Persistence Behavior
The file owns transitions among `xe->pinned.early.kernel_bo_present`, `early.evicted`, `late.kernel_bo_present`, `late.evicted`, and `late.external`. It preserves pinned BO contents through backup/restore and ensures remaining pinned DMA mappings are dropped on teardown. The lists are volatile runtime state but determine whether VRAM contents survive power loss.

## Dependencies and Integration Points
It integrates with TTM resource managers, `xe_bo_evict_pinned`, `xe_bo_restore_pinned`, `xe_bo_notifier_prepare_pinned`, GGTT remapping, tile migrate waits, PM notifier paths in `xe_pm.c`, and PCI remove in `xe_device_remove`.

## Risks
Ordering is critical: early BOs may be required before GT/migrate engines are available, while late BOs can use GPU copies. List movement must handle races with unpinning during PM notifier callbacks. Missing migrate waits can leave backup/restore copies incomplete. PCI removal deliberately purges many BOs, so only exported/pagemap-relevant data should be preserved.

## Test Signals
Suspend/resume on DGFX, hibernation with flat CCS, external pinned dma-buf scenarios, forced PCI removal/unplug, PM notifier failure injection, list-state assertions after pin/unpin, and migrate-engine wait coverage are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bo_evict.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bo_evict.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bo_evict.h

## Purpose
This header declares the Xe whole-device BO eviction/restoration API used by PM and device teardown code.

## Important APIs, Types, and Functions
It exposes `xe_bo_evict_all`, `xe_bo_evict_all_user`, pinned notifier prepare/unprepare functions, early and late restore functions, `xe_bo_pci_dev_remove_all`, and `xe_bo_pinned_init`.

## Control Flow
There is no executable flow in the header. The declared functions represent explicit lifecycle phases: initialize pinned tracking, prepare pinned backups, evict user/all BOs, restore early/late pinned BOs, undo prepare state, and remove PCI-device mappings.

## State and Persistence Behavior
The header stores no state but gives callers access to state transitions in `xe->pinned` lists and pinned BO backup objects.

## Dependencies and Integration Points
It forward-declares `struct xe_device` and is consumed by PM, debug, and device lifecycle code. It pairs with `xe_bo.c` per-object helpers and `xe_bo_evict.c` list orchestration.

## Risks
Misordering declared phases can lose VRAM contents or attempt GPU-assisted restore before GT/migrate infrastructure is available. Signature drift would break PM integration at build time.

## Test Signals
Build coverage, system suspend/resume, hibernate, PCI remove, and DGFX pinned BO tests validate that these hooks stay wired correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bo_evict.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bo_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bo_types.h

## Purpose
This header defines `struct xe_bo`, the Xe-specific wrapper around `struct ttm_buffer_object`. It is the central data model for buffer placement, VM association, GGTT mappings, pin tracking, CPU mappings, purgeable accounting, CCS metadata, and SVM device-memory links.

## Important APIs, Types, and Functions
The main type is `struct xe_bo`. Important fields include `ttm`, `backup_obj`, `parent_obj`, `flags`, `vm`, `tile`, placement arrays, `ggtt_node`, `vmap`, `kmap`, `pinned_link`, process-client tracking under `CONFIG_PROC_FS`, `attr.atomic_access`, `pxp_key_instance`, `devmem_allocation`, `vram_userfault_link`, `min_align`, `purgeable`, and SR-IOV VF `bb_ccs` pointers.

## Control Flow
The header has no executable flow. Its fields are mutated by BO creation, TTM move callbacks, VM bind/unbind, mmap fault handling, PM eviction, shrinker reclaim, PXP setup, and SR-IOV CCS attach/detach paths.

## State and Persistence Behavior
`backup_obj`/`parent_obj` preserve pinned VRAM contents across suspend. `placement` records allowed TTM locations while `ttm.resource` records current location. `purgeable` tracks terminal purge state plus VMA and WILLNEED holder counts. `vram_userfault_link` persists runtime PM mmap-release tracking. `created` distinguishes initialized BOs from partially constructed objects.

## Dependencies and Integration Points
The type embeds DRM/TTM objects and references Xe device, tile, VM, GGTT, memory-pool, DRM SVM pagemap, and client accounting types. Because it is included widely, it is part of the ABI between memory management, VM, PM, debug, and display subsystems inside the driver.

## Risks
Field ownership is spread across subsystems, so lock discipline is essential. Reservation lock protects purgeable counters and atomic attributes, while `xe->pinned.lock` protects pinned-list membership. Incorrect lifetime handling of `backup_obj`, VM refs, or client links can leak objects or use freed memory.

## Test Signals
Tests should stress BO create/destroy, VM close, client fdinfo accounting, suspend backup lifetime, purgeable VMA transitions, SVM device-memory teardown, SR-IOV CCS attach/detach, and debug object dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bo_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_configfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_configfs.c

## Purpose
This file implements the Xe configfs subsystem. It lets administrators create per-PCI-device configfs groups before driver bind and set probe-time policies such as survivability mode, allowed GT types, allowed engines, PSMI enablement, context-restore batch buffers, and SR-IOV PF limits.

## Important APIs, Types, and Functions
Key types are `struct xe_config_group_device`, nested `struct xe_config_device`, and `struct wa_bb`. Public getters include `xe_configfs_check_device`, `xe_configfs_get_survivability_mode`, `xe_configfs_primary_gt_allowed`, `xe_configfs_media_gt_allowed`, `xe_configfs_get_engines_allowed`, `xe_configfs_get_psmi_enabled`, context-restore BB getters, `xe_configfs_admin_only_pf`, and `xe_configfs_get_max_vfs`. Init/exit functions register and unregister the `xe` configfs subsystem.

## Control Flow
`xe_config_make_device_group` validates canonical PCI BDF names, resolves PF/VF relationships, matches Xe PCI IDs, allocates a config group, seeds defaults, and conditionally creates an `sriov` subgroup. Attribute stores parse user text, take the device mutex, reject changes if the PCI device is already bound, then update in-memory config. Engine parsing accepts class names with instance numbers or `*`; context-restore BB parsing counts dwords first, allocates a single command buffer, then reparses to store MI commands or register-write sequences.

## State and Persistence Behavior
Configuration lives only in configfs kernel objects and is consumed during probe. It is not persistent across module unload or configfs object deletion. The `lock` serializes attributes, while `config_group_find_item` and `config_group_put` manage lookup lifetimes. Custom values are reported during probe by `xe_configfs_check_device`.

## Dependencies and Integration Points
It depends on Linux configfs, PCI lookup, Xe PCI descriptor data, module parameters, GT/engine enumerations, SR-IOV mode helpers, and MI command encodings. Consumers include PCI probe, survivability mode, HW engine filtering, PSMI/RTP/GUC setup, LRC context restore programming, and SR-IOV PF initialization.

## Risks
Input parsing is security-sensitive because it accepts root-provided strings that alter probe behavior and context restore commands. Bound-device detection is best effort through PCI drvdata and must prevent late mutation. Incorrect PF/VF resolution could configure the wrong device. Context restore BB allocation uses shared per-class storage, so length/pointer consistency matters.

## Test Signals
Configfs create/remove tests, invalid BDF/name tests, pre-bind vs post-bind attribute writes, engine mask parsing, GT type disabling, PSMI and survivability probe behavior, context-restore BB programming, SR-IOV max_vfs/admin_only_pf combinations, and module unload cleanup are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_configfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_configfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_configfs.h

## Purpose
This header declares the configfs interface and provides no-op/default fallbacks when `CONFIG_CONFIGFS_FS` is disabled.

## Important APIs, Types, and Functions
It exposes subsystem lifecycle functions, device-check diagnostics, getters for survivability, GT type masks, engine masks, PSMI, context restore mid/post BB data, and SR-IOV PF options. Fallback inlines return conservative defaults such as both GTs allowed, all engines allowed, PSMI disabled, and module/default SR-IOV limits.

## Control Flow
There is no executable flow beyond inline fallback returns. Compile-time conditionals select the real configfs implementation or default behavior.

## State and Persistence Behavior
The header stores no state. With configfs enabled, state is held by `xe_configfs.c`; without it, all settings are effectively immutable defaults.

## Dependencies and Integration Points
It includes defaults, engine class types, and module parameter declarations. Callers can use the getters unconditionally without scattering configfs `#ifdef` logic through probe and engine code.

## Risks
Fallback defaults must match `xe_configfs.c` defaults or behavior diverges by kernel configuration. SR-IOV fallback is especially important because it mixes module parameters and default admin-only PF policy.

## Test Signals
Build both with and without configfs enabled. Probe tests should confirm that disabling configfs preserves normal GT/engine discovery, PSMI off, and module-parameter max_vfs behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_configfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_debugfs.c

## Purpose
This file registers Xe debugfs files for device information, workarounds, residencies, forcewake control, wedged-mode control, SVM scheduling knobs, late-binding toggles, page-reclaim testing, fault injection, TTM memory-manager views, tile/GT subtrees, PXP, PSMI, and SR-IOV debug.

## Important APIs, Types, and Functions
The public entry point is `xe_debugfs_register`. Important file operations include `forcewake_all_fops`, `wedged_mode_fops`, `page_reclaim_hw_assist_fops`, `atomic_svm_timeslice_ms_fops`, `min_run_period_lr_ms_fops`, `min_run_period_pf_ms_fops`, and `disable_late_binding_fops`. Static `drm_info_list` entries expose `info`, `sriov_info`, `workarounds`, and Battlemage residency counters.

## Control Flow
Registration adds generic DRM info files, conditionally adds Battlemage telemetry and CSC fault injection, creates writable tuning files, registers TTM manager debugfs nodes, then delegates to tile, GT, PXP, PSMI, and SR-IOV debugfs registration. `forcewake_all` gets runtime PM and all GT forcewake domains on open, then releases them on close. `wedged_mode` validates modes and updates GuC ADS reset policy if changing to/from no-reset hang mode.

## State and Persistence Behavior
Debugfs writes mutate live driver state such as `xe->wedged.mode`, inconsistent reset policy flag, `has_page_reclaim_hw_assist`, SVM timeslice/min-run settings, and `late_bind.disable`. These are runtime settings only and disappear when the device/module is removed.

## Dependencies and Integration Points
It depends on DRM debugfs, Linux fault injection, PM runtime guards, forcewake, PMT telemetry, workarounds, GuC ADS scheduler policy, TTM managers, tile/GT debugfs, PXP, PSMI, and SR-IOV PF/VF debug registration.

## Risks
Debugfs is privileged but can destabilize hardware: forcewake can time out, wedged mode changes reset policy across GTs, and writable tuning knobs can expose racey scheduling behavior. Policy updates across multiple GTs can become inconsistent if a later GT update fails.

## Test Signals
Debugfs smoke tests, forcewake open/close leak checks, wedged mode validation and reset-policy failure injection, Battlemage telemetry reads, TTM manager debugfs presence, SR-IOV PF/VF registration, and runtime PM suspend/resume while files are open are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_debugfs.h

## Purpose
This header declares the Xe debugfs registration hook and provides a stub when debugfs is disabled.

## Important APIs, Types, and Functions
The only public function is `xe_debugfs_register(struct xe_device *xe)`, guarded by `CONFIG_DEBUG_FS`.

## Control Flow
There is no executable flow except the disabled-config inline stub. Device probe can call `xe_debugfs_register` unconditionally.

## State and Persistence Behavior
The header owns no state. The implementation creates debugfs files that mutate runtime state, but when debugfs is disabled no debugfs state exists.

## Dependencies and Integration Points
It forward-declares `struct xe_device` and is consumed from device probe after DRM registration and sysfs/PMU setup.

## Risks
The main risk is configuration skew: callers must not assume debugfs files exist when `CONFIG_DEBUG_FS` is off. Signature drift is caught by build coverage.

## Test Signals
Build with debugfs enabled and disabled, and probe devices in both configurations to ensure no missing-symbol or registration-order regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_defaults.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_defaults.h

## Purpose
This header centralizes default values for Xe module/runtime configuration, including GuC logging, display probing, VRAM BAR size, force-probe policy, SR-IOV PF limits, wedged mode, and SVM notifier sizing.

## Important APIs, Types, and Functions
It defines constants such as `XE_DEFAULT_GUC_LOG_LEVEL`, `XE_DEFAULT_PROBE_DISPLAY`, `XE_DEFAULT_VRAM_BAR_SIZE`, `XE_DEFAULT_FORCE_PROBE`, `XE_DEFAULT_MAX_VFS`, `XE_DEFAULT_ADMIN_ONLY_PF`, `XE_DEFAULT_WEDGED_MODE`, `XE_DEFAULT_WEDGED_MODE_STR`, and `XE_DEFAULT_SVM_NOTIFIER_SIZE`.

## Control Flow
There is no runtime flow. Some defaults depend on compile-time configuration, such as debug builds selecting a higher GuC log level and display probing following `CONFIG_DRM_XE_DISPLAY`.

## State and Persistence Behavior
The file stores no mutable state. The constants seed module parameters, configfs defaults, and device initialization choices.

## Dependencies and Integration Points
It includes `xe_device_types.h` for wedged-mode enum values and is used by module parameter setup, configfs fallback/default logic, and device probe wedged-mode initialization.

## Risks
Defaults are user-visible policy. Changing them affects boot behavior, debug verbosity, SR-IOV exposure, and recovery semantics. Default strings must match numeric defaults to avoid misleading sysfs/module parameter presentation.

## Test Signals
Build tests, module parameter default inspection, configfs default reads, wedged-mode startup behavior, debug vs non-debug GuC log level checks, and display-enabled/disabled kernel configs validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_defaults.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_dep_job_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_dep_job_types.h

## Purpose
This header defines a generic dependency job abstraction layered on top of the DRM GPU scheduler. It lets Xe schedule non-engine work only after dependency fences have signaled.

## Important APIs, Types, and Functions
It defines `struct xe_dep_job_ops` with `run_job` and `free_job` callbacks, and `struct xe_dep_job` containing a base `drm_sched_job` plus operation pointers.

## Control Flow
There is no executable flow in the header. The scheduler implementation calls `ops->run_job` when DRM scheduler dependencies are satisfied and `ops->free_job` when the job is released.

## State and Persistence Behavior
Each dependency job persists as a DRM scheduler job until dependencies complete and scheduler cleanup calls the free hook. The operation table defines job-specific lifetime behavior.

## Dependencies and Integration Points
It includes `<drm/gpu_scheduler.h>` and is consumed by `xe_dep_scheduler.c` and users such as exec queue dependency scheduling.

## Risks
Callback contracts must be honored: `run_job` must return a valid fence or error-style fence according to DRM scheduler expectations, and `free_job` must release job-private allocations exactly once. Missing ops would crash at scheduler callback time.

## Test Signals
Compile tests, dependency scheduler users submitting jobs with resolved/unresolved fences, cancellation/fini tests, and memory-leak checks for callback free paths are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_dep_job_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_dep_scheduler.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_dep_scheduler.c

## Purpose
This file implements a small Xe wrapper around the DRM GPU scheduler for generic dependency jobs. It runs callback-based jobs once their fences are ready, without tying the work to a hardware engine scheduler.

## Important APIs, Types, and Functions
The private `struct xe_dep_scheduler` contains a `drm_gpu_scheduler`, one `drm_sched_entity`, and an RCU head for deferred free. Public functions are `xe_dep_scheduler_create`, `xe_dep_scheduler_fini`, and `xe_dep_scheduler_entity`. Static scheduler ops map DRM callbacks to `xe_dep_job_ops`.

## Control Flow
Creation allocates the wrapper, initializes a DRM scheduler with one run queue, the provided workqueue, a credit limit from `job_limit`, no finite timeout, and the device pointer. It then initializes a single scheduler entity. Runtime job dispatch calls `xe_dep_scheduler_run_job`, which downcasts to `xe_dep_job` and invokes its `run_job`; cleanup invokes `free_job`. Fini tears down entity and scheduler, then frees the wrapper through RCU because scheduler fences can export timeline names.

## State and Persistence Behavior
The scheduler object persists until `xe_dep_scheduler_fini`. Jobs persist in DRM scheduler queues and are freed by their callbacks. RCU-delayed freeing protects external fence/timeline readers after scheduler teardown.

## Dependencies and Integration Points
It depends on DRM GPU scheduler, Xe device types, and `xe_dep_job_types.h`. It is used by exec queue code for deferred dependency-driven work such as resource freeing or invalidation sequencing.

## Risks
The wrapper assumes one entity and one scheduler run queue are enough for its users. Incorrect `job_limit` can throttle or over-admit dependency jobs. Fini must not race live submissions. Job callback bugs propagate through the DRM scheduler context.

## Test Signals
Dependency-job submission tests, scheduler teardown with exported fences, job-limit pressure, workqueue-backed execution, and callback free coverage are relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_dep_scheduler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_dep_scheduler.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_dep_scheduler.h

## Purpose
This header declares the generic Xe dependency scheduler API.

## Important APIs, Types, and Functions
It forward-declares scheduler, DRM entity, workqueue, and Xe device types, then exposes `xe_dep_scheduler_create`, `xe_dep_scheduler_fini`, and `xe_dep_scheduler_entity`.

## Control Flow
There is no executable flow. Callers create a scheduler, obtain its DRM scheduler entity for job submission, and later finalize it.

## State and Persistence Behavior
The header stores no state; it describes ownership of a heap-allocated scheduler object managed by create/fini.

## Dependencies and Integration Points
It is included by code that needs a dependency-only scheduler, especially exec queue infrastructure. It hides the internal DRM scheduler wrapper layout.

## Risks
Callers must not use the returned entity after `xe_dep_scheduler_fini`. Header/API drift would break scheduler users at build time.

## Test Signals
Build coverage plus create/submit/fini tests with dependency jobs validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_dep_scheduler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_devcoredump.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_devcoredump.c

## Purpose
This file implements Xe device coredumps using Linux `dev_coredump`. On the first GPU hang/error, it captures a stable snapshot of device, GT, GuC, exec queue, job, HW engine, and VM state and exposes it through sysfs for postmortem debugging.

## Important APIs, Types, and Functions
Public functions are `xe_devcoredump`, `xe_devcoredump_init`, and `xe_print_blob_ascii85`. Important internals include `devcoredump_snapshot`, `xe_devcoredump_deferred_snap_work`, `xe_devcoredump_read`, `__xe_devcoredump_read`, `xe_devcoredump_snapshot_free`, and `xe_devcoredump_free`.

## Control Flow
`xe_devcoredump` takes the device coredump lock, ignores later hangs while one dump is active, stores a formatted reason, captures immediate snapshots under forcewake/signaling constraints, and queues deferred work. The worker registers the devcoredump node, reacquires runtime PM and forcewake, captures delayed VM/exec queue details, computes formatted dump size, pre-renders either the whole dump or a 1.5 GB chunk window, and frees raw snapshots when possible. Reads flush deferred work, page through large dump chunks, copy data, and use runtime PM for large regenerated chunks.

## State and Persistence Behavior
State lives in `xe->devcoredump`: a mutex, `captured` flag, snapshot structures, delayed work, reason string, and optional formatted read buffer. Only the first failure is retained until userspace releases the devcoredump or the timeout expires. Freeing clears snapshot fields and resets `captured`.

## Dependencies and Integration Points
It depends on Linux devcoredump, DRM printers, runtime PM, forcewake, GuC CT/log/capture, GuC submit snapshots, scheduler job snapshots, HW engine snapshots, VM snapshots, and device snapshot printing. GuC submit timeout paths call `xe_devcoredump`.

## Risks
Capture runs near failure paths and must avoid sleeping/allocating in signaling-sensitive contexts; delayed work handles heavier allocations. Very large dumps require chunk regeneration and runtime PM. Locking must prevent stale reads while allowing release. If snapshot free misses a subobject, repeated hangs leak memory or expose stale data.

## Test Signals
GPU hang injection, multiple-hang suppression, devcoredump sysfs read/release, timeout cleanup, large-dump chunk reads, runtime PM during reads, forcewake failure handling, and ASCII85 blob output tests are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_devcoredump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_devcoredump.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_devcoredump.h

## Purpose
This header declares Xe devcoredump hooks and the ASCII85 blob printer, with no-op fallbacks when `CONFIG_DEV_COREDUMP` is disabled.

## Important APIs, Types, and Functions
It exposes `xe_devcoredump`, `xe_devcoredump_init`, and `xe_print_blob_ascii85`. Forward declarations cover DRM printer, Xe device, exec queue, and scheduler job types.

## Control Flow
With devcoredump enabled, callers can initialize the coredump lock/cleanup and trigger snapshots. With it disabled, trigger/init calls compile to no-op success, while ASCII85 printing remains available.

## State and Persistence Behavior
The header owns no state. Enabled builds operate on `xe->devcoredump`; disabled builds never capture or retain dump state.

## Dependencies and Integration Points
It is included by GuC submit/capture/log paths and device probe. The stub design lets callers avoid local `#ifdef CONFIG_DEV_COREDUMP` guards.

## Risks
Disabled builds silently skip coredump capture, so debugging expectations differ by config. Function signatures must remain synchronized with the implementation and call sites.

## Test Signals
Build both devcoredump-enabled and disabled kernels, trigger GuC timeout paths, and verify ASCII85 blob users compile independently of devcoredump support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_devcoredump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_devcoredump_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_devcoredump_types.h

## Purpose
This header defines the in-memory data structures used by Xe devcoredump capture and readout.

## Important APIs, Types, and Functions
`struct xe_devcoredump_snapshot` stores capture time, boot time, process identity, reason string, affected GT, deferred work item, GuC CT/log snapshots, GuC execution queue snapshot, HW engine snapshots, job snapshot, matched GuC capture node, VM snapshot, and formatted-read buffer metadata. `struct xe_devcoredump` wraps the snapshot with a mutex and a `captured` flag.

## Control Flow
The types are populated synchronously by `devcoredump_snapshot`, extended by deferred work, read by the devcoredump read callback, and freed/reset by the release callback. The `work_struct` embedded in the snapshot bridges immediate hang capture to later allocation-heavy capture.

## State and Persistence Behavior
Snapshot fields persist from first captured hang until userspace/kernel releases the devcoredump. The formatted read buffer may hold either the full dump or a chunk window. `captured` prevents overwriting the first failure with subsequent hangs.

## Dependencies and Integration Points
It depends on ktime, mutex, workqueue, hardware-engine types, and forward-declared GuC/VM/job snapshot types supplied by other Xe subsystems. `xe_device_types.h` embeds `struct xe_devcoredump` in `struct xe_device`.

## Risks
Because the structure aggregates many subsystem-owned snapshot pointers, free/reset code must match every capture field. The single matched-node model assumes one hardware-engine capture per devcoredump event. Process identity and reason strings must remain valid after the originating file/job is gone.

## Test Signals
Snapshot allocation/free leak tests, repeated hang suppression, deferred capture completion, VM/job/engine snapshot print coverage, and coredump release/reset tests validate the type contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_devcoredump_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device.c

## Purpose
This file implements the top-level Xe DRM device and file lifecycle. It defines DRM ioctls/fops, per-open file state, special mmap behavior, device allocation/destruction, early and full probe sequencing, remove/shutdown paths, cache flush helpers, snapshot printing, wedged-device handling, and ASID-to-VM lookup.

## Important APIs, Types, and Functions
Major entry points include `xe_device_create`, `xe_device_probe_early`, `xe_device_probe`, `xe_device_remove`, `xe_device_shutdown`, `xe_file_get`, `xe_file_put`, `xe_is_xe_file`, `xe_device_wmb`, `xe_device_l2_flush`, `xe_device_td_flush`, `xe_device_ccs_bytes`, `xe_device_snapshot_print`, `xe_device_declare_wedged`, `xe_device_validate_wedged_mode`, `xe_wedged_mode_to_string`, and `xe_device_asid_to_vm`. Static structures include the DRM ioctl table, `xe_driver_fops`, and the `drm_driver`.

## Control Flow
Open allocates `xe_file`, client accounting, VM and exec-queue xarrays, and process identity. Close kills exec queues, removes them from HW engine groups, closes VMs, and drops the file ref under runtime PM. Ioctls reject wedged devices and acquire runtime PM before dispatch. Mmap handles a DGFX PCI barrier special offset or falls back to GEM mmap.

Device creation removes conflicting apertures, allocates `xe_device`, initializes TTM with `xe_ttm_funcs`, creates BO/shrinker/pagemap infrastructure, IRQ state, validation state, ASID tracking, pinned BO lists, workqueues, and PMT locking. Early probe initializes workarounds, early MMIO, SR-IOV mode, pcode, survivability mode, LMEM readiness, wedged mode, and VRAM region allocation. Full probe initializes PAT, SR-IOV, DMA masks, tiles, GTs, GGTT, FLR cleanup, flat CCS, VRAM, TTM managers, display, IRQ, pagefaults, devcoredump, NVM, remapper, HECI, late bind, OA, PXP, PSMI, DRM registration, sysfs/debugfs/hwmon/I2C/VSEC/SR-IOV late hooks, and sanitize cleanup.

## State and Persistence Behavior
The file initializes long-lived device state: TTM device, workqueues, shrinkers, `xe->info`, ASID xarray, pinned BO state, runtime wedged flags/methods, PM/runtime fields, and per-file VM/queue xarrays. Wedging is terminal until external recovery; it blocks ioctls and emits DRM wedged events. Remove unplugs DRM and evicts/purges BOs; shutdown tears down display/IRQ/GTs and may trigger driver FLR.

## Dependencies and Integration Points
It is the integration hub for aperture, DRM core, GEM/TTM, display, IRQ, GGTT, GT, GuC, pagefault, VM madvise, BO eviction, PM, PXP, PSMI, OA/PMU, sysfs/debugfs/hwmon, SR-IOV, survivability, workarounds, NVM, HECI, VSEC, and PCI probe/remove code.

## Risks
Probe ordering is fragile: display must own the first allocation after TTM managers, FLR cleanup is registered only after certain init steps, and many later subsystems assume tiles/GTs/VRAM are ready. Runtime PM must wrap ioctls, faults, debugfs, and memory access correctly. Wedged-mode changes affect recovery semantics and reset policy. Remove/shutdown must prevent new users while preserving exported BO data as intended.

## Test Signals
PCI probe/remove fault injection, runtime PM ioctl/mmap tests, open/close leak checks, ASID allocation wrap tests under debug config, suspend/shutdown FLR behavior, wedged uevent tests, debugfs/sysfs registration, display-first allocation assertions, SR-IOV PF/VF probe modes, and cache-flush helper tests are strong signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device.c -->

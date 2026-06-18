# Research: subset-b-001375

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_smi_events.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_smi_events.c

## Purpose
Implements the KFD SMI event stream exported through an anonymous file descriptor. User space opens the stream through `kfd_smi_event_open`, writes an event mask, then polls and reads textual SMI records for GPU reset, thermal throttling, VM faults, SVM page faults, migrations, queue eviction/restore, GPU unmap, and process start/end.

## Important APIs, Types, And Functions
`struct kfd_smi_client` is the per-open state: RCU list node, `kfifo`, wait queue, enabled event bitmask, target `kfd_node`, spinlock, opener pid, and `CAP_SYS_ADMIN` status. `kfd_smi_ev_fops` wires `poll`, `read`, `write`, and `release` to the anonymous inode. `kfd_smi_ev_write` updates the 64-bit event mask with `WRITE_ONCE`; `kfd_smi_ev_read` drains bytes from the FIFO under spinlock and copies them to user memory after unlocking. `kfd_smi_event_add` formats records using KFD SMI event format macros and dispatches through `add_event_to_kfifo`. The exported `kfd_smi_event_*` helpers convert KFD, SVM, VM, reset, and queue lifecycle events into SMI records.

## Control Flow
`kfd_smi_event_open` allocates a client, allocates an 8192-byte FIFO, records `current->tgid` and admin status, links the client into `dev->smi_clients` under `dev->smi_lock`, and returns an anonymous fd. Producers call event helpers, which format into a fixed `KFD_SMI_EVENT_MSG_SIZE` buffer, then walk `dev->smi_clients` under RCU. `kfd_smi_ev_enabled` allows per-pid events only for the owning pid unless the client is privileged. Matching clients receive FIFO bytes under their client spinlock and waiters are woken. `release` removes the client with `list_del_rcu` and frees it via `call_rcu`.

## State And Persistence
State is in-memory and per open fd. Event masks persist until userspace writes a new mask or closes the fd. FIFO contents are transient and dropped if there is insufficient FIFO space. `dev->reset_seq_num` is incremented on pre-reset events and included in both pre/post reset messages.

## Dependencies And Integration Points
Uses Linux `anon_inode_getfd`, `poll_wait`, `kfifo`, RCU, wait queues, and user copy helpers. Integrates with `amdgpu_vm_get_task_info_pasid`, `amdgpu_vm_get_task_info_vm`, `amdgpu_reset_get_desc`, `amdgpu_dpm_get_thermal_throttling_counter`, KFD process lookup, and SVM event producers. The header exposes these helpers to reset, VM fault, queue, and SVM code paths.

## Risks
Events can be silently lost when a client FIFO lacks space. `kfd_smi_event_add` relies on bounded formatting into a fixed buffer; format macro changes need size scrutiny. `kfd_smi_ev_read` returns `-EAGAIN` for empty streams, so blocking behavior depends on userspace using poll/select correctly. Authorization is pid based unless the opener had `CAP_SYS_ADMIN`; incorrect pid selection in producers can leak or suppress process-scoped events. RCU removal and FIFO access rely on consistent use of `dev->smi_lock` and per-client spinlocks.

## Test Signals
Useful tests include opening SMI events, writing individual masks, verifying poll readiness after injected reset/fault/migration events, reading partial and full FIFO records, closing while events are produced, validating non-admin pid filtering, validating admin sees cross-process events, and stress tests that intentionally overflow the FIFO and confirm debug-only drops without memory corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_smi_events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_smi_events.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_smi_events.h

## Purpose
Declares the KFD SMI event producer interface used by KFD, SVM, reset, VM fault, and queue management code.

## Important APIs, Types, And Functions
The header forward-declares `struct amdgpu_reset_context` and exports `kfd_smi_event_open` plus event update functions for VM fault, thermal throttling, GPU reset, page fault start/end, migration start/end, queue eviction/restore, delayed restore rescheduling, GPU unmap, and process lifecycle.

## Control Flow
Callers emit events by passing the relevant `kfd_node`, pid, address range, GPU ids, trigger code, timestamp, or reset context. The implementation handles formatting, filtering, queuing, and wakeups.

## State And Persistence
No state is defined in the header. It exposes the stateful implementation in `kfd_smi_events.c`, where clients and FIFOs are held per opened fd.

## Dependencies And Integration Points
Requires KFD core types such as `struct kfd_node`, `struct kfd_process_device`, `pid_t`, `ktime_t`, and AMD reset context definitions from including translation units. The API is consumed by SVM migration/fault code, queue eviction/restore paths, GPU reset paths, and process attach/detach paths.

## Risks
The prototypes are tightly coupled to SMI record formats. Adding fields or changing units in producers must stay synchronized with userspace expectations and the format macros from KFD UAPI headers.

## Test Signals
Compile coverage should catch signature drift. Runtime coverage should verify each declared producer path can be called with masks enabled and produces parseable records in the SMI fd.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_smi_events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_svm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_svm.c

## Purpose
Implements AMD KFD shared virtual memory management. It owns SVM range creation, attribute updates, interval-tree lookup, MMU interval notifier invalidation, HMM page collection, DMA mapping, GPU page-table mapping/unmapping, migration between system memory and VRAM, retry-fault recovery, XNACK mode memory accounting, TTM eviction handling, deferred range-list mutation, and CRIU checkpoint/restore of SVM metadata.

## Important APIs, Types, And Functions
`struct svm_range` instances are stored in `kfd_process.svms` as both a list and an interval tree. `svm_ioctl` dispatches `KFD_IOCTL_SVM_OP_SET_ATTR` to `svm_range_set_attr` and `KFD_IOCTL_SVM_OP_GET_ATTR` to `svm_range_get_attr`. `svm_range_restore_pages` is the retry-fault recovery entry point from the GPU fault path. `svm_range_validate_and_map` is the central validation pipeline: reserve VM page-table BOs, collect pages with HMM or use VRAM BO state, DMA-map pages, check the notifier sequence, update GPU page tables, and optionally wait/flush. `svm_range_vram_node_new/free` manage VRAM backing BOs through `struct svm_range_bo`. `svm_range_cpu_invalidate_pagetables` is the MMU interval notifier callback. `svm_range_list_init/fini` initialize and tear down per-process SVM state. `kfd_criu_checkpoint_svm`, `kfd_criu_restore_svm`, and `kfd_criu_resume_svm` preserve SVM range attributes across CRIU.

## Control Flow
For `SET_ATTR`, the code validates requested GPU ids and attributes, takes the process-info lock, flushes deferred work while holding the mmap write lock, validates the CPU virtual range, transactionally clones/splits/creates ranges with `svm_range_add`, links new notifiers, applies attributes, removes replaced ranges, then downgrades to mmap read lock to trigger prefetch migration and validation/mapping. For GPU retry faults, `svm_range_restore_pages` looks up the KFD process by PASID, checks SVM support and XNACK, locates the faulting node, takes mmap and SVM locks, creates an unregistered range when needed, verifies VMA permissions, determines the best restore location, emits SMI page fault events, migrates if needed, validates and maps, then counts the fault. For CPU invalidation, the MMU notifier either unmaps and schedules deferred structural removal for `MMU_NOTIFY_UNMAP` or evicts/unmaps GPU mappings for other invalidations. For TTM eviction, `svm_range_schedule_evict_svm_bo` schedules a worker that migrates VRAM-backed ranges to RAM and signals the eviction fence.

## State And Persistence
Primary state is per process in `svm_range_list`: list, interval tree, supported-GPU bitmap, deferred work list, restore work, CRIU metadata list, retry-fault drain state, and checkpoint timestamps. Each `svm_range` tracks page range, attributes, access bitmaps, actual/preferred/prefetch location, DMA address arrays per GPU, notifier, VRAM BO reference, invalid count, validation timestamp, and queue reference count. State is not persistent across process lifetime except through explicit CRIU checkpoint/restore metadata.

## Dependencies And Integration Points
Depends on Linux MM, `mmu_interval_notifier`, HMM, DMA mapping, workqueues, interval trees, locks, TTM/DRM exec, amdgpu VM update APIs, amdgpu BO allocation/fencing, amdgpu HMM helpers, XGMI topology, KFD process/device lookup, KFD migration helpers, queue quiesce/resume, and SMI event emission. It also relies on UAPI SVM attribute definitions and KFD process/device indexing.

## Risks
This file has high race complexity. Notifier invalidation, deferred work, range splitting, migration, and retry-fault recovery all interact through mmap locks, `svms->lock`, `prange->lock`, and `migrate_mutex`; lock ordering regressions can deadlock. Partial failures after attributes are applied can leave partially migrated or partially mapped ranges. FIFO SMI events are best effort and not transactional with mapping state. DMA address arrays mix normal DMA addresses and a VRAM-domain tag bit, so masking mistakes can corrupt map/unmap behavior. XNACK on/off transitions must reserve or unreserve memory limits consistently. CRIU restore assumes compatible device counts and topology validation outside this file.

## Test Signals
Key signals include SVM ioctl set/get attribute tests across overlapping ranges, split/merge boundary tests, mmap/munmap invalidation under GPU access, retry-fault recovery with read/write permission failures, prefetch migration to VRAM and back to system memory, XGMI multi-GPU access/in-place policy, TTM eviction migration, XNACK mode switches with memory accounting, CRIU checkpoint/restore/resume, process teardown while deferred work and retry faults are pending, and lockdep/KASAN/KCSAN stress runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_svm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_svm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_svm.h

## Purpose
Defines the public and internal SVM data structures and function declarations used by KFD process, migration, fault, eviction, and CRIU code.

## Important APIs, Types, And Functions
`SVM_RANGE_VRAM_DOMAIN` tags DMA address entries that represent VRAM-domain addresses. `SVM_ADEV_PGMAP_OWNER` groups HMM ownership by XGMI hive or device. `struct svm_range_bo` owns an amdgpu BO, KRef, range list, eviction fence/work, and associated KFD node. `enum svm_work_list_ops` and `struct svm_work_list_item` describe deferred range-list operations. `struct svm_range` carries the interval, notifier, DMA mappings, VRAM BO state, attributes, access bitmaps, deferred/child lists, migration lock, and mapped/invalid bookkeeping. The header declares range initialization/finalization, ioctl dispatch, fault restore, VRAM node management, deferred work scheduling, DMA unmap helpers, CRIU helpers, SVM support checks, and XNACK reserve transitions.

## Control Flow
When SVM is enabled, callers use the full implementation. When `CONFIG_HSA_AMD_SVM` is disabled, inline stubs make initialization/finalization mostly no-op, report no SVM ranges, reject restore/restore-from-CRIU paths, and make `KFD_IS_SVM_API_SUPPORTED` false.

## State And Persistence
The header defines in-memory per-range state only. CRIU functions declared here serialize selected state through KFD private checkpoint data; no direct persistent storage exists in the header.

## Dependencies And Integration Points
Includes Linux list/mutex/rwsem/mm headers plus amdgpu and KFD private headers. It is a shared contract between `kfd_svm.c`, KFD process lifecycle code, KFD migration code, amdgpu eviction fences, and CRIU integration.

## Risks
`svm_range_lock` also enters `memalloc_noreclaim_save`, so callers must pair unlocks exactly. The stub and enabled APIs must stay signature-compatible. The VRAM-domain tag consumes a low address bit and depends on page-aligned DMA/VRAM representations. Any struct layout change affects a broad set of lock, migration, and notifier assumptions.

## Test Signals
Build both enabled and disabled SVM configurations. Exercise eviction, migration, CRIU, and process teardown paths that compile through this header, and run lockdep to catch unpaired `svm_range_lock`/`svm_range_unlock` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_svm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_topology.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_topology.c

## Purpose
Maintains KFD's HSA topology model and exports it through sysfs. It creates a CPU topology node from virtual CRAT data during init, adds/removes GPU nodes as KFD devices appear and disappear, synthesizes cache/memory/I/O/P2P details not present in CRAT, assigns stable-ish GPU ids, exposes node properties under `/sys/class/kfd/kfd/topology`, and updates capability bits such as SVM, debug, RAS, doorbells, atomics, and coherent host access.

## Important APIs, Types, And Functions
Global state includes `topology_device_list`, `sys_props`, `topology_lock`, and `topology_crat_proximity_domain`. Lookup helpers include `kfd_topology_device_by_proximity_domain`, `kfd_topology_device_by_id`, and `kfd_device_by_id`. Lifecycle entry points are `kfd_topology_init`, `kfd_topology_shutdown`, `kfd_topology_add_device`, and `kfd_topology_remove_device`. Sysfs show/build/remove paths are implemented by `sysprops_show`, `node_show`, `mem_show`, `kfd_cache_show`, `iolink_show`, `perf_show`, `kfd_build_sysfs_node_entry`, and `kfd_topology_update_sysfs`. GPU enrichment is handled by `kfd_generate_gpu_id`, `kfd_fill_cache_non_crat_info`, `kfd_fill_iolink_non_crat_info`, `kfd_dev_create_p2p_links`, `kfd_topology_set_capabilities`, and `kfd_update_svm_support_properties`.

## Control Flow
Initialization creates and parses a CPU VCRAT, moves parsed devices into the master list under the write lock, builds sysfs, increments `generation_count`, and patches CPU memory data from DMI. Adding a GPU first tries to attach it to a parsed GPU topology entry; otherwise it creates/parses a GPU VCRAT, moves the result to the master list, assigns the `kfd_node`, fills cache data, rebuilds sysfs, then assigns a GPU id and fills non-CRAT properties such as public name, clocks, render minor, SDMA counts, RAS/SVM/debug capabilities, memory clock, I/O link flags, and P2P links. Removal deletes the sysfs node, frees the topology device, decrements device counts, renumbers proximity domains and links, rebuilds sysfs, and sends a placeholder change notification.

## State And Persistence
Topology is in-memory kernel state rebuilt from VCRAT/CRAT, PCI/amdgpu device data, DMI, and runtime partition data. `sys_props.generation_count` changes on accepted topology/sysfs updates. `gpu_id` is generated from PCI identity, local memory size, and XCC mask with collision avoidance against the current live list; it is stable for a given boot/device view but not a persistent registry.

## Dependencies And Integration Points
Uses KFD CRAT parsing/creation, KFD queue manager/debug helpers, SVM support macro, amdgpu device, RAS, XGMI, PCIe capability reads, DMI, sysfs/kobject APIs, cpufreq, devcgroup permission checks, optional P2P configuration, and debugfs hooks for HQD/runlist dumps. It is consumed by userspace ROCm/HSA tooling through sysfs and by in-kernel KFD lookups by GPU id or proximity domain.

## Risks
Sysfs rebuilds are all-or-partial operations; error paths can leave sysfs partially constructed until later release/rebuild. The topology list is protected by an rwsem, but sysfs show functions read object fields that can change across device add/remove and rely on object lifetime through kobjects. GPU id hashing is collision-handled but not globally stable. P2P and indirect-link synthesis has many topology assumptions around CPU nodes, large BAR, XGMI hives, and peer accessibility. Capability bits depend on firmware version tables, so new ASICs require careful updates.

## Test Signals
Signals include boot topology sysfs presence, generation counter increments on GPU add/remove and SVM support update, correct node counts and proximity-domain renumbering after hot unplug, devcgroup permission denial in show paths, P2P link creation for PCIe and XGMI systems, cache sibling maps across XCC partitions, render minor correctness for XCP partitions, debug capability bits across firmware versions, and debugfs HQD/runlist enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_topology.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_topology.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_topology.h

## Purpose
Defines KFD topology property structures used to represent HSA nodes, memory banks, caches, I/O links, performance blocks, system properties, and DMI memory descriptors.

## Important APIs, Types, And Functions
`struct kfd_node_properties` mirrors node-level sysfs properties including capability fields, debug properties, clocks, device identifiers, queue counts, SDMA counts, CWSR/control stack sizes, and public name. `struct kfd_mem_properties`, `struct kfd_cache_properties`, and `struct kfd_iolink_properties` carry per-child sysfs attributes and optional GPU pointers for permission checks. `struct kfd_topology_device` groups all lists and kobjects for one HSA node. `struct kfd_system_properties` owns global topology sysfs kobjects and generation/platform fields. The header declares topology device allocation/release helpers and `kfd_update_svm_support_properties` when KFD is enabled.

## Control Flow
The implementation allocates these structures while parsing CRAT/VCRAT, links them into topology lists, builds sysfs from embedded attributes/kobjects, and frees them on topology removal/shutdown.

## State And Persistence
All structures are runtime state. They mirror sysfs output but do not persist outside the kernel. OEM fields are copied from CRAT data; DMI memory device data is used to patch CPU memory width and clock values.

## Dependencies And Integration Points
Depends on Linux DMI, list, types, and `linux/kfd_sysfs.h` constants plus KFD CRAT structures. The shape of these structs is tightly coupled with sysfs show/build code in `kfd_topology.c` and CRAT parser fill routines.

## Risks
Embedded `struct attribute` and kobject pointers require strict lifetime pairing. Changing property fields without updating sysfs show code or CRAT parsing can silently hide or misreport topology data. `CACHE_SIBLINGMAP_SIZE` bounds generated cache sibling maps and must remain large enough for supported XCC/CU layouts.

## Test Signals
Compile checks catch type drift. Runtime tests should compare sysfs `properties` files against expected struct fields, especially for cache sibling maps, P2P links, debug properties, and SVM capability updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_topology.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/soc15_int.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/soc15_int.h

## Purpose
Provides KFD interrupt source constants and decode macros for SOC15-style interrupt handler entries.

## Important APIs, Types, And Functions
Defines source IDs for CP end-of-pipe, CP bad opcode, SQ interrupt message, VMC fault, VMC UTCL2 poison, SDMA trap/ECC, and SOC21 SDMA trap/ECC variants. Macros extract client id, source id, ring id, VMID, VMID type, PASID, node id, and context IDs 0 through 3 from little-endian interrupt entry dwords.

## Control Flow
There is no executable control flow. Interrupt handlers include this header to classify and unpack IH entries.

## State And Persistence
No state. Macros decode the caller-provided IH entry array.

## Dependencies And Integration Points
Includes `soc15_ih_clientid.h` and uses `le32_to_cpu`. It integrates with KFD interrupt paths that need PASID, VMID, node, and context data for dispatching faults/traps.

## Risks
Macros assume the IH entry layout and word indexes are correct for the targeted SOC generation. Using SOC15 macros on incompatible entry formats can misroute faults or traps. Lack of bounds checks means callers must provide a valid entry array.

## Test Signals
Unit-style decode tests with known synthetic IH entries, plus hardware fault/trap tests that verify decoded PASID, VMID, source, and node ids match expected events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/soc15_int.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdxcp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdxcp/Makefile

## Purpose
Builds the AMD XCP helper module object as part of the amdgpu DRM build.

## Important APIs, Types, And Functions
Defines `amdxcp-y := amdgpu_xcp_drv.o` and adds `amdxcp.o` to `obj-$(CONFIG_DRM_AMDGPU)`.

## Control Flow
Kbuild compiles `amdgpu_xcp_drv.c` into the composite `amdxcp.o` when `CONFIG_DRM_AMDGPU` is enabled.

## State And Persistence
No runtime state. Build output affects module/object composition.

## Dependencies And Integration Points
Depends on the parent amdgpu Kbuild context and the `CONFIG_DRM_AMDGPU` option. It packages the exported XCP platform DRM-device allocation helpers for amdgpu users.

## Risks
If this Makefile is not included from the parent build, exported XCP symbols will be unavailable. The object is tied to amdgpu configuration rather than a separate XCP config switch.

## Test Signals
Kernel build with `CONFIG_DRM_AMDGPU=y/m` should produce `amdxcp.o` and resolve `amdgpu_xcp_drm_dev_alloc/free/release` symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdxcp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdxcp/amdgpu_xcp_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdxcp/amdgpu_xcp_drv.c

## Purpose
Provides a small DRM render-device wrapper for AMD XCP partitions. It allocates platform devices and devm-managed DRM devices so partitioned GPU nodes can have separate DRM render nodes.

## Important APIs, Types, And Functions
`struct xcp_device` embeds `struct drm_device` and stores the backing `platform_device`. `amdgpu_xcp_driver` advertises `DRIVER_GEM | DRIVER_RENDER` with name `amdgpu_xcp_drv`. Global state is `pdev_num`, `xcp_dev[MAX_XCP_PLATFORM_DEVICE]`, and `xcp_mutex`. Exported functions are `amdgpu_xcp_drm_dev_alloc`, `amdgpu_xcp_drm_dev_free`, and `amdgpu_xcp_drv_release`.

## Control Flow
Allocation takes the mutex, finds a free slot below 64, registers a simple platform device named `amdgpu_xcp_%d`, opens a devres group, allocates a DRM device with `devm_drm_dev_alloc`, records it in the slot table, returns the embedded DRM pointer, and increments the count. Free scans for the DRM pointer under the mutex and calls `free_xcp_dev`, which releases devres, unregisters the platform device, clears the slot, and decrements the count. Module exit calls release for all remaining devices.

## State And Persistence
State is runtime-global in the slot array and count. Device resources are tied to platform-device devres groups and are released on explicit free or module exit.

## Dependencies And Integration Points
Uses Linux platform device APIs, devres, DRM driver/device allocation, module exit, and exported symbols. KFD topology consumes the resulting XCP DRM render minor through `gpu->xcp->ddev`.

## Risks
The fixed 64-device table can return `-ENODEV` under extreme partition counts or leaks. Correctness depends on callers freeing exactly the DRM devices returned. `int8_t` indexes/counts are adequate for 64 entries but fragile if the limit grows. Allocation failure after platform registration must keep devres/platform cleanup balanced.

## Test Signals
Tests should allocate and free multiple XCP devices, verify unique platform names/render devices, hit allocation failure cleanup paths, call release with live devices, and run module unload/leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdxcp/amdgpu_xcp_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdxcp/amdgpu_xcp_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdxcp/amdgpu_xcp_drv.h

## Purpose
Declares the XCP DRM platform-device helper API.

## Important APIs, Types, And Functions
Exports prototypes for `amdgpu_xcp_drm_dev_alloc`, `amdgpu_xcp_drm_dev_free`, and `amdgpu_xcp_drv_release`.

## Control Flow
No implementation flow. Callers allocate a DRM device pointer, later free it, and can release all devices during teardown.

## State And Persistence
No state in the header. State lives in `amdgpu_xcp_drv.c`.

## Dependencies And Integration Points
Requires `struct drm_device` to be visible to including C files. Used by amdgpu/KFD XCP partition code that needs per-partition DRM render nodes.

## Risks
The API does not encode ownership beyond a raw pointer; callers must avoid double-free and must not pass unrelated DRM devices.

## Test Signals
Build coverage for users of the declarations and runtime allocation/free cycles through the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdxcp/amdgpu_xcp_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/Kconfig

## Purpose
Defines configuration switches for AMDGPU Display Core and related display-engine options.

## Important APIs, Types, And Functions
`DRM_AMD_DC` enables the newer AMD display engine, defaults to yes, depends on DRM/AMDGPU and architecture/compiler constraints, and selects CEC, CEC notifier, optional HDA component support, and `DRM_AMD_DC_FP` when kernel FPU support is safe. `DRM_AMD_DC_FP` is an internal floating-point support symbol for DCN SoCs. `DRM_AMD_DC_SI` enables DC support for Southern Islands ASICs. `DEBUG_KERNEL_DC` enables kgdb break behavior in DC asserts. `DRM_AMD_SECURE_DISPLAY` enables secure display CRC/debugfs support when DC floating point and debugfs are available.

## Control Flow
Kconfig evaluates these symbols during kernel configuration. The selected values control which display Makefiles compile objects and which preprocessor paths are active.

## State And Persistence
Configuration state is stored in the kernel `.config`; there is no runtime state in this file.

## Dependencies And Integration Points
Integrates with DRM, AMDGPU, architecture FPU support, compiler constraints, CEC, sound HDA, KGDB, DEBUG_FS, and downstream display Kbuild files. The Clang architecture constraint protects against excessive stack use in bandwidth calculations.

## Risks
Dependency mistakes can expose unsupported DC builds or hide supported ones. The `DRM_AMD_DC_FP` selection is architecture and compiler sensitive; getting it wrong can create unsafe kernel FPU use or build/runtime failures. Secure display depends on debugfs and specific firmware behavior.

## Test Signals
Run config matrix builds across x86_64, ARM64, RISC-V, LoongArch, SPARC64, and Clang/GCC combinations; verify object inclusion for DC, DCN FP, SI, debug, and secure display options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/Makefile

## Purpose
Top-level AMD Display Core Kbuild file. It establishes include paths, feature defines, and includes subcomponent Makefiles for DAL/DC, modules, DMUB, and HDCP.

## Important APIs, Types, And Functions
Defines `AMDDALPATH = $(RELATIVE_AMD_DISPLAY_PATH)`. Adds many `subdir-ccflags-y` include directories under `dc`, `modules`, and `dmub`. Defines `BUILD_FEATURE_TIMING_SYNC=0`. `DAL_LIBS` lists `amdgpu_dm`, `dc`, FreeSync, color, info packet, power, `dmub/src`, and HDCP. `AMD_DAL` turns those into Makefile paths and includes them.

## Control Flow
Kbuild includes this file from the amdgpu display build. This file includes each subcomponent Makefile, which appends objects into aggregate variables such as `AMD_DISPLAY_FILES`.

## State And Persistence
No runtime state. It controls compile-time object lists, include search paths, and feature macros.

## Dependencies And Integration Points
Depends on parent variables `RELATIVE_AMD_DISPLAY_PATH` and `FULL_AMD_DISPLAY_PATH`. Integrates all display subdirectories into the amdgpu driver build and provides include paths used by those sources.

## Risks
Include path order is broad and can hide accidental header coupling. `BUILD_FEATURE_TIMING_SYNC=0` is a compile-time feature gate marked temporary. Any missing subcomponent Makefile breaks display builds. Adding a new display module requires updating `DAL_LIBS` or a subcomponent Makefile.

## Test Signals
Build AMDGPU with DC enabled, confirm `AMD_DISPLAY_FILES` includes expected DM/DC/module/DMUB/HDCP objects, and verify no include path regressions with W=1 or sparse-style checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/Makefile

## Purpose
Builds the AMDGPU Display Manager subcomponent when Display Core is enabled.

## Important APIs, Types, And Functions
When `CONFIG_DRM_AMD_DC` is set, `AMDGPUDM` includes core DM objects such as `amdgpu_dm.o`, plane/CRTC/IRQ/MST/color/services/helpers/SMU/PSR/replay/quirks/writeback/colorop/ISM support. `dc_fpu.o` is added when `CONFIG_DRM_AMD_DC_FP` is set. HDCP support adds `amdgpu_dm_hdcp.o`. Debugfs builds add CRC and debugfs objects. The file adds the DC include path and appends prefixed objects to `AMD_DISPLAY_FILES`.

## Control Flow
Kbuild conditionals decide which object names are appended. The parent display Makefile includes this file as part of the DAL build.

## State And Persistence
No runtime state. It controls compile-time inclusion of DM code.

## Dependencies And Integration Points
Depends on `CONFIG_DRM_AMD_DC`, optional `CONFIG_DRM_AMD_DC_FP`, optional `CONFIG_DEBUG_FS`, `AMDDALPATH`, and `FULL_AMD_DISPLAY_PATH`. It contributes objects consumed by the parent amdgpu display build.

## Risks
Object lists must stay synchronized with source files and feature gates. FPU-sensitive code must remain behind `CONFIG_DRM_AMD_DC_FP`. Debugfs-only CRC/debug objects should not be built without debugfs. HDCP is unconditionally added within DC, so missing HDCP source/dependency handling would break DC builds.

## Test Signals
Build with DC disabled, DC enabled without FP, DC enabled with FP, and DC plus DEBUG_FS. Confirm expected object inclusion and no unresolved symbols from optional DM features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/Makefile -->

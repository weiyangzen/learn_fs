# Group Research: subset-b-001371

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_chardev.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_chardev.c

## Purpose

`kfd_chardev.c` is the userspace ABI front door for AMD KFD through `/dev/kfd`. It registers the character device, binds opened file descriptors to `struct kfd_process`, dispatches all KFD ioctls, and implements KFD-specific `mmap` offsets for doorbells, events, reserved memory, and remapped MMIO.

The file is intentionally broad because it is the ABI glue between HSA runtimes/debuggers/checkpoint tooling and the KFD kernel subsystems. It covers queue creation and updates, event management, process aperture queries, GPUVM allocation/mapping/import/export, SVM and XNACK mode control, CRIU checkpoint/restore, debug runtime enablement, debugger trap operations, dma-buf interop, SMI event subscription, and secondary KFD process creation.

## Important APIs, Types, and Entry Points

- Device lifecycle: `kfd_chardev_init()` registers major `kfd`, class `kfd`, and `/dev/kfd`; `kfd_chardev_exit()` destroys them.
- File operations: `kfd_open()` rejects nonzero minors and 32-bit tasks, creates or references a `kfd_process`, initializes CWSR-on-APU support, and stores the process in `filep->private_data`; `kfd_release()` drops the owned process reference and handles secondary context notifier release.
- Ioctl core: `amdkfd_ioctls[]` maps every `AMDKFD_IOC_*` number to a handler and optional validator; `kfd_ioctl()` normalizes command size, copies user data to stack or heap scratch storage, checks process ownership and CRIU capability, runs validators, calls the handler, and copies output back.
- Queue ABI: `set_queue_properties_from_user()`, `kfd_ioctl_create_queue()`, `destroy_queue`, `update_queue`, `set_cu_mask`, `get_queue_wave_state`, and `alloc_queue_gws` convert ioctl arguments into `queue_properties`/`mqd_update_info` and call PQM/DQM helpers.
- Memory ABI: `kfd_ioctl_alloc_memory_of_gpu()`, `free_memory_of_gpu()`, `map_memory_to_gpu()`, `unmap_memory_from_gpu()`, `get_available_memory()`, `acquire_vm()`, `import_dmabuf()`, `export_dmabuf()`, and `get_dmabuf_info()` manage KFD handles around AMDGPU GPUVM objects.
- SVM/XNACK ABI: `kfd_ioctl_svm_validate()`, `kfd_ioctl_svm()`, and `kfd_ioctl_set_xnack_mode()` gate SVM operations on primary KFD contexts and compiled SVM support.
- CRIU ABI: `kfd_ioctl_criu()` dispatches process-info, checkpoint, unpause, restore, and resume stages using helpers that serialize devices, BOs, queues, events, SVM ranges, and KFD-private state.
- Debug ABI: `kfd_ioctl_runtime_enable()` toggles the debug runtime state; `kfd_ioctl_set_debug_trap()` handles enable/disable, runtime event forwarding, exception masks, wave launch controls, queue suspend/resume, address watches, flags, debug-event queries, exception info, and snapshots.
- Mapping ABI: `kfd_mmap()` decodes `KFD_MMAP_TYPE_*` and routes to doorbell, event, reserved-memory, or MMIO remap helpers; `kfd_mmio_mmap()` maps one uncached page from the remapped MMIO BAR.

## Control Flow

Open starts with a strict process model. A successful `open()` creates a KFD process for the calling task group leader and stores it on the file descriptor. Later ioctls verify that the file descriptor is being used by the same process group leader, except for checkpoint/restore operations where a ptracing CRIU helper may be allowed. This ownership check is central to keeping KFD process state from being shared accidentally across forked children.

The ioctl path first verifies that `_IOC_NR(cmd)` is in the KFD command range and that the driver has a descriptor for it. It uses the driver's canonical command definition rather than trusting userspace, allocates temporary ioctl storage sized for the larger of user and driver structures, zeros any extension tail, copies input, runs an ioctl-specific validator when present, executes the handler, and copies output fields back. CRIU ioctls additionally require `CAP_CHECKPOINT_RESTORE` or `CAP_SYS_ADMIN`.

Queue creation validates user pointers, ring sizes, queue type, priority, queue percentage, and the encoded PM4 target XCC. It locks `p->mutex`, finds and binds the requested GPU PDD, allocates process doorbells if necessary, acquires user queue buffers, then asks `pqm_create_queue()` for a queue ID and doorbell offset. On success it reports a KFD mmap doorbell offset and raises a debugger `EC_QUEUE_NEW` event. Destroy/update/CU-mask/wave-state operations similarly lock process state and delegate to PQM helpers.

GPU memory allocation rejects zero-size allocations and unsupported userptr on non-primary KFD contexts. With SVM enabled it flushes deferred SVM work and checks interval trees for overlapping VA or user-buffer registrations before taking the process mutex. It validates public VRAM against large-BAR capability, handles special doorbell and MMIO-remap offsets, calls `amdgpu_amdkfd_gpuvm_alloc_memory_of_gpu()`, creates an IDR handle in the PDD, updates VRAM accounting, and returns a combined user handle. Mapping/unmapping copies a user GPU-ID array, resumes from `n_success`, binds peer PDDs as needed, maps or unmaps through AMDGPU GPUVM, syncs page-table updates when required, flushes KFD TLBs, and removes DMA mappings after unmap flushes.

CRIU is a staged protocol. `PROCESS_INFO` evicts queues, marks them paused, and returns counts and private-data size. `CHECKPOINT` requires queues to remain evicted and serializes process private data, device ID mapping, queue/event/SVM metadata, and BO buckets; BO export is deliberately last because exported dma-buf file descriptors are committed only after failure-prone copies are complete. `RESTORE` evicts the new process, restores XNACK state, validates devices and render-node FDs, restores doorbells/VMs, blocks MMU notifications, recreates BOs with original IDR handles, maps them to recorded devices, restores queues/events/SVM ranges by object type, and verifies that all private bytes were consumed. `UNPAUSE` restores queues, while `RESUME` finds the target process by PID and re-enables SVM/MMU notifications through KFD and AMDGPU.

Debug runtime and trap ioctls layer policy on top of the helpers in `kfd_debug.c`. Runtime enable refuses processes that already have queues, primes MES or per-VMID debug state, records `r_debug` and TTMP setup policy, and may block on `runtime_enable_sema` while the debugger hands the event to the runtime. Trap operations locate a target process by PID, enforce primary contexts, ptrace ownership for external debugging, runtime-state requirements for mutating operations, and then call the appropriate debugger helper.

## State and Persistence Behavior

Persistent per-open state is the referenced `struct kfd_process` stored in `filep->private_data`. Most ioctl handlers mutate process-wide state under `p->mutex`: PDD arrays, queue manager state, doorbell allocations, GPUVM handles, aperture fields, XNACK mode, CRIU paused state, debug runtime fields, and debugger references.

GPU memory is persisted as AMDGPU `kgd_mem` objects referenced from each PDD's `alloc_idr`. User handles combine GPU ID and IDR slot. VRAM usage is tracked in `pdd->vram_usage`, with special adjustment for AQL queue memory. Doorbell and MMIO allocations do not behave like regular user BOs; they return synthetic mmap offsets that `kfd_mmap()` later decodes.

Queue state is persisted by the process queue manager and DQM, not by this file. This file validates ABI arguments, acquires BO references for ring-related buffers, and records returned queue IDs and doorbell offsets. Queue exception creation is also observable through debug-event state when debugging is active.

CRIU state is serialized into UAPI buckets and private-data records. It persists enough KFD-local identifiers to restore user GPU IDs, IDR handles, mapped GPU lists, queue/event/SVM metadata, XNACK mode, and restored mmap offsets. File descriptors for exported BOs are installed only after the associated serialization or restoration path has succeeded.

Debug runtime state is persisted in `p->runtime_info`, `p->debug_trap_enabled`, `p->debugger_process`, `p->dbg_ev_file`, exception masks, semaphore state, and per-PDD debug fields updated through `kfd_debug.c`/KGD callbacks.

## Dependencies and Integration Points

This file is tightly integrated with KFD process management (`kfd_create_process`, `kfd_lookup_process_by_pid`, PDD helpers), PQM/DQM queue management, KFD events, doorbells, SVM, topology, SMI events, debug support, CRIU helpers, KFD TLB flushing, and reserved-memory mapping. Its GPU memory calls delegate to AMDGPU KGD/GPUVM entry points for allocation, mapping, dma-buf import/export, memory sync, available memory, MMIO bus addresses, tile config, and VM initialization from DRM render-node files.

It consumes UAPI definitions from `uapi/linux/kfd_ioctl.h` and therefore must preserve ABI struct sizing, ioctl numbers, handle encodings, and mmap-offset encodings. It also relies on Linux facilities such as `copy_from_user`, `copy_to_user`, `access_ok`, capabilities, `fget`/`fput`, dma-buf FDs, IDRs, interval trees, `ptrace_parent`, task/mm references, and VMA remapping.

The debug path integrates with `kfd_debug.c` for trap activation and exception transport, with KGD callbacks for hardware debugger registers, and with MES/HWS scheduling mode. CRIU integrates with external checkpoint tooling through capability-gated ioctls and ptrace-based FD ownership exceptions.

## Risks and Edge Cases

- The ioctl dispatcher deliberately supports ABI extension by accepting smaller userspace structures and zeroing the driver-side tail. Any handler that reads unvalidated pointer/count pairs must still validate them independently.
- `kfd_ioctl_alloc_memory_of_gpu()` temporarily releases `current->mm` write locking through SVM flush helpers before later taking `p->mutex`; ordering regressions here can reintroduce SVM/GPUVM overlap races or lock inversions.
- The map/unmap ioctls update `n_success` incrementally for restartability. Error paths must preserve partial progress accurately or userspace can double-map/unmap or leak DMA mappings.
- Public VRAM allocation depends on large-BAR detection and debug override behavior. Misclassification can expose inaccessible VRAM to userspace or reject valid host-visible VRAM.
- CRIU BO export installs file descriptors late to avoid leaks, but the code has many exits after partial allocations. `commit_files()` and object cleanup are the critical leak-prevention points.
- CRIU restore recreates old IDR handles exactly. Conflicts, malformed private data, or mismatched device counts return errors, but partially restored BOs and blocked MMU notifications require later cleanup/resume paths to be correct.
- Debug trap operations cross process boundaries and rely on PID, task, mm, ptrace, process-reference, and mutex lifetimes. Missing any reference drop or using a stale target after unlock would be severe.
- `kfd_ioctl_set_debug_trap()` rejects many operations unless runtime is enabled, but enable/disable paths intentionally defer activation in some states. Runtime state transitions and semaphore wakeups are easy to regress.
- `kfd_mmap()` trusts encoded offsets to choose mapping type. Each sub-mapper must validate device existence, size, and permissions because the offset itself is user controlled.
- Several deprecated debug ioctls return `-EPERM`; keeping them in the table preserves ABI numbers but callers must migrate to `AMDKFD_IOC_DBG_TRAP`.

## Test and Validation Signals

- Open/close tests should cover normal open, nonzero minor rejection, 32-bit compat rejection, FD use from the wrong process, secondary process creation, and process reference cleanup.
- Ioctl ABI tests should exercise old/smaller struct sizes, invalid ioctl numbers, missing input/output pointers, command extension tails, CRIU capability failures, and copy fault injection.
- Queue tests should cover compute, AQL, SDMA, SDMA-XGMI, SDMA-by-engine-ID, small ring-size clamping, invalid priorities, CU-mask bounds, GWS allocation with and without debugger state, and debug `EC_QUEUE_NEW`.
- GPUVM tests should cover VRAM/GTT/userptr/doorbell/MMIO allocations, public VRAM on small vs large BAR, handle translation failures, import/export dma-buf, map/unmap restart through `n_success`, TLB flush behavior, and SVM overlap rejection.
- CRIU tests should cover process-info/checkpoint/unpause/restore/resume sequencing, queue eviction preconditions, dma-buf FD leak checks on injected copy failures, restored IDR handle preservation, restored mmap offsets, SVM private data, and invalid object type rejection.
- Debug tests should cover ptrace ownership, runtime enable/disable with and without queues, MES and non-MES devices, trap enable/disable, event FD notification, queue suspend/resume, watchpoint set/clear, wave launch controls, exception queries, and snapshots.
- Mmap tests should verify doorbell, event, reserved-memory, and MMIO offset decoding, one-page MMIO size enforcement, process ownership checks, and invalid GPU IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_chardev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_crat.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_crat.c

## Purpose

`kfd_crat.c` parses and synthesizes Component Resource Association Table (CRAT) data for KFD topology. It converts CRAT subtype records into `kfd_topology_device` nodes and their memory, cache, and IO-link properties, and it builds virtual CRAT images when firmware/ACPI does not provide a usable table for CPUs or discrete GPUs.

The file also owns AMD GPU cache description tables and fallback logic. For older ASICs it uses static cache arrays, while newer IP-discovery-capable GPUs can derive cache sizes and sharing information from `adev->gfx.config` and MALL/GMC data.

## Important APIs, Types, and Entry Points

- `kfd_parse_crat_table()` validates a CRAT image, creates topology devices for its domains, copies OEM metadata, walks enabled subtype records, and dispatches each subtype to a parser.
- `kfd_create_crat_image_virtual()` allocates and fills a virtual CRAT for CPU-only or GPU-only topology and returns the image/size to callers; `kfd_destroy_crat_image()` frees it.
- `kfd_get_gpu_cache_info()` selects static or dynamically filled `struct kfd_gpu_cache_info` records for a `kfd_node`.
- Subtype parsers: `kfd_parse_subtype_cu()`, `kfd_parse_subtype_mem()`, `kfd_parse_subtype_cache()`, and `kfd_parse_subtype_iolink()` attach compute, memory, cache, and IO-link records to topology devices.
- CPU VCRAT helpers: `kfd_create_vcrat_image_cpu()`, `kfd_fill_cu_for_cpu()`, `kfd_fill_mem_info_for_cpu()`, and, on x86-64, `kfd_fill_iolink_info_for_cpu()`.
- GPU VCRAT helpers: `kfd_create_vcrat_image_gpu()`, `kfd_fill_gpu_memory_affinity()`, `kfd_fill_gpu_direct_io_link_to_cpu()`, `kfd_fill_gpu_xgmi_link_to_gpu()`, and optional SRAT lookup in `kfd_find_numa_node_in_srat()`.

## Control Flow

Parsing begins by ensuring the caller supplied an empty device list and a non-null image. It creates one `kfd_topology_device` per CRAT domain, assigning sequential proximity domains starting from the caller's base. It then walks subtype records from immediately after the header until the image length is reached. Enabled subtype records are parsed by type; unknown subtypes are warned about but ignored.

Compute-unit parsing identifies the topology device by proximity domain. CPU-present records fill CPU core count/base and ATS capability; GPU-present records fill SIMD ID base/count, LDS size, wave properties, array/CU layout, scratch slots, and hot-plug capability. Memory parsing maps CRAT memory records to HSA heap types. GPU nodes with no CPU cores interpret `visibility_type` as public/private framebuffer heap type, while CPU nodes become system memory. Memory banks with matching heap type, flags, and width are aggregated into one topology memory property.

Cache parsing has no proximity-domain field, so it maps a cache record by `processor_id_low` against CPU core ID ranges or GPU SIMD ID ranges. It copies cache sizing, associativity, line, latency, and sibling-map data into topology cache properties and translates CRAT cache flags into HSA cache type flags. This depends on compute-unit records being parsed before cache records.

IO-link parsing creates a link property on the `node_from` device, sets type/version/latency/bandwidth/transfer size, and assigns weight. PCIe gets a fixed weight, XGMI takes the CRAT XGMI weight, and other types use `node_distance()`. If the CRAT record is bidirectional, the parser also clones the link in reverse on the destination topology device.

Virtual CPU CRAT creation allocates enough space for online NUMA nodes, fills a CRAT header using DSDT OEM metadata when available, and emits compute, memory, and CPU-to-CPU IO-link subtypes for each online node with a valid APIC ID. Virtual GPU CRAT creation emits one GPU compute-unit subtype, one memory subtype based on public/private VRAM and large-BAR state, one GPU-to-CPU IO-link subtype, and additional XGMI GPU-to-GPU links to already-created peers in the same hive.

GPU cache selection first keys on legacy `asic_type`, then on `KFD_GC_VERSION()`. Some generations use hard-coded static arrays; newer generations call the IP-discovery fill helpers. GC 11 paths mark cache-line sizes missing and hard-code conservative line sizes where IP discovery lacks fields. Unknown hardware falls back to a dummy cache table and warns.

## State and Persistence Behavior

The only file-global mutable state is `gpu_processor_id_low`, a monotonically increasing synthetic GPU processor-ID base. Each GPU VCRAT consumes a range sized by total CU slots so synthetic GPU SIMD IDs do not collide between generated GPU nodes.

Generated CRAT images are heap allocations returned to callers and freed through `kfd_destroy_crat_image()`. The image contents are transient input for topology parsing; long-lived state is the resulting `kfd_topology_device` list and its linked property lists.

Topology state persisted by parsing includes proximity domains, OEM fields, CPU/GPU node properties, memory heap descriptors, cache descriptors, and IO-link descriptors. Memory records with matching characteristics are intentionally coalesced, while IO-link bidirectionality is materialized as separate linked-list entries on both topology devices.

Cache metadata is mostly static read-only arrays. Dynamic cache fill writes into caller-provided `struct kfd_gpu_cache_info` storage through `*pcache_info`; callers must ensure that pointer references valid writable storage for the dynamic cases.

## Dependencies and Integration Points

The file integrates with KFD topology allocation/release helpers, KFD node/device structures, AMDGPU ASIC/IP-discovery data, local memory info, XGMI hive/sharing/bandwidth APIs, PCI and ACPI NUMA/SRAT data, Linux NUMA node APIs, and HSA sysfs/topology property structures. The public CRAT layout and flags come from `kfd_crat.h`.

Virtual GPU links depend on `kfd_dev_is_large_bar()` from `kfd_chardev.c`, AMDGPU PCIe bandwidth helpers, `amdgpu_xgmi_get_bandwidth()`, `amdgpu_xgmi_get_hops_count()`, and the topology database of already-created peer devices. CPU virtual CRAT depends on online NUMA nodes, APIC ID mapping, per-node managed pages, and, on x86-64, vendor-specific link-type selection.

## Risks and Edge Cases

- `kfd_parse_crat_table()` trusts subtype `length` for forward progress. It checks the generic header fits inside the image but does not deeply validate every subtype length before casting.
- Cache parsing relies on compute-unit records having been parsed earlier so CPU/GPU ID bases and CU counts are populated. A CRAT image with cache records before CU records may lose cache properties.
- `kfd_parse_crat_table()` copies OEM metadata only into the last created topology device, which is a subtle behavior callers may not expect if they assume every node gets OEM fields.
- Dynamic cache-info paths call fill helpers with `*pcache_info` as the output pointer. A caller that passes an uninitialized or undersized destination for dynamic GC versions can corrupt memory.
- `gpu_processor_id_low` is global and monotonically increasing. It avoids synthetic ID collisions during one boot, but generated IDs depend on creation order.
- GPU VCRAT allocates a fixed `4 * PAGE_SIZE`. The code checks available space while filling records, but future subtype growth or many peer links can return `-ENOMEM`.
- IO-link bidirectional cloning assumes the destination topology device already exists. Missing CPU or peer topology entries turn otherwise valid links into `-ENODEV`.
- SRAT parsing has workaround behavior for invalid GPU proximity mappings and falls back to NUMA node 0 in some bad binding cases; topology distance may be approximate on malformed firmware.
- Unknown hardware falls back to dummy cache metadata, which keeps topology usable but can expose inaccurate cache hierarchy to userspace.

## Test and Validation Signals

- CRAT parser tests should cover empty input, non-empty output list rejection, unknown subtype tolerance, disabled subtype skipping, zero or malformed subtype lengths, and cleanup on allocation failure.
- Topology tests should verify CPU, GPU, memory, cache, and IO-link properties from representative CRAT images, including memory-bank aggregation and bidirectional link cloning.
- Cache mapping tests should include CRAT ordering with CU before cache, cache IDs at CPU/GPU range boundaries, sibling-map preservation, and all cache flag combinations.
- Virtual CPU CRAT tests should run on single-node and multi-node NUMA systems, validate DSDT OEM copying, memory-size calculation, CPU link count, and non-x86 behavior.
- Virtual GPU CRAT tests should cover large BAR vs small BAR, private/public VRAM sizing, APP/APU-style host links, PCIe bandwidth fields, XGMI CPU links, XGMI peer links, multi-node KFD devices, and fixed-buffer exhaustion.
- Cache-info tests should cover legacy ASIC tables, dynamic IP-discovery fill paths, missing cache-line-size fallback, MALL/L3 reporting, and dummy fallback warnings for unknown IP versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_crat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_crat.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_crat.h

## Purpose

`kfd_crat.h` defines the packed CRAT binary ABI structures, subtype IDs, flags, IO-link constants, and KFD-facing CRAT helper prototypes used by KFD topology code. It is the shared contract between CRAT image parsing/generation in `kfd_crat.c` and the rest of KFD topology initialization.

The header deliberately mirrors firmware/ACPI-style table records. Its structures are byte-packed and therefore represent persistent binary layout, not just internal C convenience types.

## Important APIs, Types, and Symbols

- `CRAT_SIGNATURE`, OEM length constants, and `struct crat_header` describe the top-level CRAT table header, entry count, domain count, OEM metadata, and total byte length.
- Subtype IDs define compute unit, memory, cache, TLB, CCompute, and IO-link records.
- `CRAT_SIBLINGMAP_SIZE` is fixed at 32 bytes and explicitly documented as ABI-sensitive.
- Packed subtype records include `struct crat_subtype_computeunit`, `memory`, `cache`, `tlb`, `ccompute`, `iolink`, and the generic header `struct crat_subtype_generic`.
- Flag definitions map CRAT record state to enabled, hot-plug, CPU/GPU/IOMMU presence, memory volatility, cache/TLB type, IO-link atomics/coherency, peer DMA, and bidirectional link behavior.
- IO-link type constants enumerate PCIe, XGMI, coherent fabric, RDMA, and other transport categories.
- `struct kfd_gpu_cache_info` is KFD's compact GPU cache descriptor used to generate cache subtypes.
- Public helpers: `kfd_get_gpu_cache_info()`, `kfd_destroy_crat_image()`, `kfd_parse_crat_table()`, and `kfd_create_crat_image_virtual()`.

## Control Flow

Consumers use the header in two main flows. For parsing, a caller obtains or creates a CRAT image, casts the image header to `struct crat_header`, then iterates packed subtype records using `struct crat_subtype_generic.length` and dispatches based on `type`. For synthesis, `kfd_create_crat_image_virtual()` fills the same packed records into an allocated image, and callers later parse or free the image.

The subtype structures are arranged exactly as the binary image expects: one-byte type and length fields followed by record-specific data. Because `#pragma pack(1)` is active around the structures, pointer arithmetic and `sizeof()` values match the serialized layout used by `kfd_crat.c`.

## State and Persistence Behavior

The header stores no runtime state. Its values are persistent in the ABI sense: changing structure field order, sizes, subtype IDs, flag values, or `CRAT_SIBLINGMAP_SIZE` changes how existing CRAT images are interpreted and can break userspace topology consumers.

`struct kfd_gpu_cache_info` is not itself a CRAT subtype, but it is used as a stable internal input format for generating CRAT cache affinity records. Its fields persist cache size, level, line size, flags, and sharing count.

## Dependencies and Integration Points

The header depends on Linux integer types and forward-declares `struct kfd_node`. It is included by `kfd_crat.c` and topology code that needs to parse virtual or firmware CRAT data. The resulting topology properties are exposed through KFD/HSA topology sysfs and consumed by userspace runtimes.

It integrates with UAPI-like binary data even though it is an internal driver header. The packed records must stay compatible with firmware CRAT conventions and with KFD topology parser expectations.

## Risks and Edge Cases

- The `length` fields are `uint8_t`; subtype structures must remain within that range or parser stepping breaks.
- `#pragma pack(1)` makes unaligned fields possible. Code must avoid assumptions about natural alignment when accessing records from arbitrary images.
- `CRAT_SIBLINGMAP_SIZE` is explicitly ABI-fixed. Changing it would alter cache/TLB record sizes and userspace-visible topology.
- IO-link flags include both low-order capability bits and bit 31 for bidirectionality. Masking or sign-extension mistakes can drop reverse-link creation.
- The compute-unit `max_slots_scatch_cu` field name contains a spelling error preserved in the structure; renaming it would be source-compatible only if all users are updated, but binary layout must not change.

## Test and Validation Signals

- Compile-time or unit checks should assert `sizeof()` for every packed CRAT structure and verify subtype lengths fit in `uint8_t`.
- Parser tests should feed synthetic records using every subtype ID and important flag combination from this header.
- ABI tests should ensure `CRAT_SIBLINGMAP_SIZE`, IO-link type values, and flag values do not drift.
- Virtual CRAT generation tests should verify that emitted `length` fields equal the packed `sizeof()` values from this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_crat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_debug.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_debug.c

## Purpose

`kfd_debug.c` implements the KFD debugger event and trap-control backend used by `AMDKFD_IOC_DBG_TRAP` and runtime debug enablement. It tracks exceptions at process, device, and queue scope; notifies a debugger through a writable event file; forwards selected exceptions to the runtime when no debugger subscription handles them; programs hardware trap/watchpoint/wave-launch state through KGD callbacks; and coordinates debug-session activation/deactivation across all GPUs attached to a KFD process.

The file is not the ioctl parser; `kfd_chardev.c` performs ABI dispatch and authorization. This file owns the state transitions and hardware-facing debugger operations once the target process has been selected and locked.

## Important APIs, Types, and Entry Points

- Event query/raise: `kfd_dbg_ev_query_debug_event()`, `kfd_dbg_ev_raise()`, `kfd_set_dbg_ev_from_interrupt()`, and `debug_event_write_work_handler()`.
- Runtime forwarding: `kfd_dbg_send_exception_to_runtime()` handles memory-violation eviction/signaling, runtime semaphore wakeups, and queue exception delivery.
- Debug activation: `kfd_dbg_trap_enable()`, `kfd_dbg_trap_activate()`, `kfd_dbg_trap_deactivate()`, and `kfd_dbg_trap_disable()`.
- Workaround control: `kfd_dbg_set_queue_workaround()` and `kfd_dbg_set_workaround()` apply the CWSR debugger workaround to existing queues when required by the device.
- MES/per-VMID programming: `kfd_dbg_set_mes_debug_mode()` allocates a process context BO if needed and calls `amdgpu_mes_set_shader_debugger()`.
- Address watches: `kfd_dbg_trap_set_dev_address_watch()`, `kfd_dbg_trap_clear_dev_address_watch()`, and watch-ID helpers allocate up to four device watchpoints while coordinating global device usage.
- Trap controls: `kfd_dbg_trap_set_wave_launch_override()`, `kfd_dbg_trap_set_wave_launch_mode()`, and `kfd_dbg_trap_set_flags()` validate capabilities and refresh runlists or MES state.
- Information queries: `kfd_dbg_trap_query_exception_info()`, `kfd_dbg_trap_device_snapshot()`, and `kfd_dbg_set_enabled_debug_exception_mask()`.

## Control Flow

Event raising starts with `kfd_dbg_ev_raise()`. If the target process is debug-enabled, it locks `event_mutex`, records the event mask on the matching device, process, or queue, and writes a single byte to the debugger event file if the event is subscribed in `exception_enable_mask`. Device memory violations may copy one exception-data payload into the PDD for later query. If `use_worker` is set, notification is deferred through `debug_event_workarea`; otherwise it writes synchronously.

Interrupt-driven exceptions enter through `kfd_set_dbg_ev_from_interrupt()`, which looks up the process/PDD by PASID and calls `kfd_dbg_ev_raise()`. If the debugger did not subscribe to the event, queue exceptions can be forwarded to the runtime when runtime debugging is enabled. Device memory violations that are not delivered to a debugger evict the process device and signal a VM fault event.

Debug enable first performs device prechecks: only SOC15-style devices are accepted, and processes with GWS allocations may be rejected on devices without debugger/GWS compatibility. It takes a reference to the supplied event file, optionally activates immediately if the runtime is already enabled, takes an extra process reference for the debug session, marks debug enabled, increments the debugger-process count for external debugging, and copies current runtime info to userspace.

Activation applies an all-or-nothing policy. It enables queue workarounds, reserves a debug trap VMID on devices without per-VMID debug support, disables GFX off where register access requires it, programs debug trap registers through KGD callbacks, sets the trap-debug flag in each QPD, and refreshes non-MES runlists or updates MES debug mode. On failure it deactivates the devices already touched and records a runtime error/busy state.

Deactivation resumes suspended queues, cancels pending event-work writes, clears all address watches, resets wave launch mode and debug flags, clears QPD debug flags, disables hardware debug trap state, releases non-per-VMID debug VMIDs, refreshes runlists or MES state, and disables queue workarounds. Disable additionally closes the event file, drops debugger references, clears exception state, and releases the debug-session process reference.

Address-watch setup allocates a watch ID under the device watchpoint spinlock, unmaps debug queues on non-MES HWS, disables GFX off, programs the address watch for each active XCC, restores GFX off, then remaps/unlocks or updates MES debug mode. Clear follows the reverse flow and releases the watch ID after hardware state has been cleared.

Exception queries lock `event_mutex`, locate queue/device/process exception state based on exception-code type, optionally copy structured data such as VM-fault payloads or runtime info to userspace, and clear the selected bit when requested. Device snapshots copy topology, PCI, firmware, aperture, XCC, capability, and current exception status for each PDD.

## State and Persistence Behavior

Process-level debug state includes `debug_trap_enabled`, `dbg_ev_file`, `debug_event_workarea`, `exception_enable_mask`, `exception_status`, `dbg_flags`, `runtime_info`, `runtime_enable_sema`, and a debug-session process reference. If one process debugs another, `debugger_process` and its `debugged_process_count` persist that relationship.

Per-PDD state includes `exception_status`, optional VM fault exception data, `spi_dbg_override`, `spi_dbg_launch_mode`, `watch_points[]`, `alloc_watch_ids`, optional MES process context BO/GPU/CPU pointers, and QPD trap-debug flags. Per-queue state uses `queue->properties.exception_status` plus workaround flags such as `is_dbg_wa`.

Device-level watchpoint allocation is shared through `pdd->dev->alloc_watch_ids` protected by `watch_points_lock`, while each PDD tracks the subset it owns. This prevents two debug sessions from programming the same hardware watch slot concurrently.

MES debug setup persists a kernel allocation of `AMDGPU_MES_PROC_CTX_SIZE` per PDD and reuses it across calls. Hardware register/debug state is refreshed through DQM runlist updates or MES set-debugger calls after every relevant state mutation.

## Dependencies and Integration Points

The file depends on `kfd_debug.h`, KFD process/PQM/DQM internals, topology lookups, runtime exception signaling, queue suspend/resume helpers, `kfd2kgd` hardware callbacks, AMDGPU GFX-off control, MES shader debugger APIs, memory allocation for MES process context, Linux file writes, workqueues, spinlocks, and user-copy helpers.

It integrates directly with `kfd_chardev.c` through the debug-trap ioctl and runtime-enable ioctl. It also integrates with interrupt handlers through `kfd_set_dbg_ev_from_interrupt()`, with VM-fault signaling through process-device eviction and fault events, and with KFD topology/sysfs through device snapshot fields and capability validation.

## Risks and Edge Cases

- `kfd_dbg_ev_raise()` only stores one VM-fault exception-data payload per PDD and logs later payloads instead of replacing them. Debuggers must query and clear promptly to avoid losing detail.
- Event notification uses `kernel_write()` of a single byte to a debugger-supplied file. Closed, unsuitable, or backpressured files can affect debugger notification behavior; file references must be balanced exactly.
- Activation is all-or-nothing but touches hardware and scheduler state incrementally. The unwind count must match the number of PDDs successfully activated or a failed enable can disturb an unrelated session.
- Address-watch setup returns `0` even if the later MES/runlist update failed after programming hardware; it releases the ID on error but does not fully roll back programmed watch registers in all paths.
- Watchpoint IDs are limited to four. Invalid or stale watch IDs are rejected, but forced clear during process cleanup loops over all possible IDs and tolerates failures.
- GFX-off control must stay paired around register programming. Devices without RLC restore can intentionally keep GFX off disabled for the session, making power-management side effects expected but sensitive.
- `kfd_dbg_trap_set_flags()` rewinds software flags and refreshes hardware after partial failure; skipped non-per-VMID devices make the rewind count logic easy to misread.
- Runtime and debugger exception delivery share state. Unsubscribed queue exceptions may go to the runtime, while subscribed ones are held for the debugger; tests must cover both paths.

## Test and Validation Signals

- Event tests should raise process, device, queue-new, queue-doorbell, and memory-violation events with subscribed and unsubscribed masks, then verify query, clear, event-file writes, and runtime fallback.
- Activation tests should cover per-VMID and non-per-VMID devices, MES and non-MES scheduling, GWS incompatibility, CWSR workaround enable/disable, multi-GPU unwind on injected failure, and process reference/file reference counts.
- Watchpoint tests should allocate all four IDs, reject the fifth, clear stale IDs, program multiple XCCs, and inject runlist/MES failures.
- Trap-control tests should validate unsupported wave launch modes, trap override capability masks, debug flags against topology capabilities, and state refresh after every mutation.
- Exception-info tests should cover queue/device/process exception codes, VM-fault data copy/clear, runtime-info copy, invalid source IDs, missing info pointers, and zero-sized buffers.
- Snapshot tests should validate entry-size truncation, number-of-devices reporting, exception-clear masks, and topology/PCI/firmware field population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_debug.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_debug.h

## Purpose

`kfd_debug.h` is the internal declaration boundary for KFD debugger events, trap activation, runtime exception forwarding, debug snapshots, and hardware capability predicates. It allows the KFD character-device ioctl path, interrupt paths, and process/queue code to call the debugger backend without depending on the implementation details in `kfd_debug.c`.

The header also centralizes generation-specific debugger capability decisions, such as per-VMID support, RLC restore support for debug registers, CWSR workaround needs, GWS debug compatibility, and TTMP setup policy.

## Important APIs, Types, and Symbols

- Session lifecycle: `kfd_dbg_trap_enable()`, `kfd_dbg_trap_disable()`, `kfd_dbg_trap_activate()`, and `kfd_dbg_trap_deactivate()`.
- Event handling: `kfd_dbg_ev_query_debug_event()`, `kfd_set_dbg_ev_from_interrupt()`, `kfd_dbg_ev_raise()`, `debug_event_write_work_handler()`, and `kfd_dbg_set_enabled_debug_exception_mask()`.
- Runtime forwarding: `kfd_dbg_send_exception_to_runtime()`.
- Trap configuration: `kfd_dbg_trap_set_wave_launch_override()`, `kfd_dbg_trap_set_wave_launch_mode()`, address-watch set/clear helpers, flag setting, exception-info query, and device snapshot collection.
- MES/debugger programming: `kfd_dbg_set_mes_debug_mode()`.
- Capability predicates: `kfd_dbg_is_per_vmid_supported()`, `kfd_dbg_is_rlc_restore_supported()`, `kfd_dbg_has_cwsr_workaround()`, `kfd_dbg_has_gws_support()`, and `kfd_dbg_has_ttmps_always_setup()`.

## Control Flow

Callers enter this API after they have selected and locked or referenced the relevant KFD process/PDD. `kfd_chardev.c` uses the lifecycle and trap-control declarations to implement `AMDKFD_IOC_DBG_TRAP` and runtime enable/disable. Interrupt handling uses `kfd_set_dbg_ev_from_interrupt()` to translate PASID/doorbell/trap-mask data into process events. Process cleanup and runtime transitions use activate/deactivate helpers to keep hardware and queue state synchronized with debug-session state.

The inline predicates are used before and during debug operations to select hardware programming strategy. Per-VMID devices use VMID-targeted trap state and MES context setup, while older devices may need a reserved debug VMID. Devices without RLC restore support require special GFX-off handling. Devices in the CWSR workaround range constrain GWS/debug coexistence and queue workaround programming.

## State and Persistence Behavior

The header does not allocate or store state. Its predicates encode persistent policy based on `KFD_GC_VERSION(dev)`, MEC firmware version, and MES scheduler version. Because these decisions gate ABI-visible debug support and power-management behavior, changes alter what userspace debuggers can do on specific GPU generations.

## Dependencies and Integration Points

The header includes `kfd_priv.h` for core KFD process/device types and relies on AMDGPU IP-version macros and MES version masks through included KFD/AMDGPU headers. It is included by `kfd_debug.c`, `kfd_chardev.c`, and other KFD paths that need to raise debugger events or test debug capability.

It also maps internal hardware generation checks to UAPI-visible debug behavior, because unsupported flags or operations become ioctl errors in the character-device layer.

## Risks and Edge Cases

- Capability predicates are hard-coded by IP version and firmware thresholds. New GPU generations need deliberate updates or they may get overly restrictive fallback behavior.
- `kfd_dbg_has_gws_support()` returns false for known incompatible firmware/device combinations and for CWSR-workaround devices, then assumes support otherwise. Firmware threshold mistakes can expose broken cooperative/GWS debug behavior.
- TTMP setup policy combines pre-GFX11, selected GFX9 exception, MES scheduler version, and GFX12+ logic. A wrong condition can leave debug scratch registers uninitialized or do unnecessary setup.
- The header exposes functions that expect the caller to hold the right process locks/references; the prototypes do not encode those preconditions.

## Test and Validation Signals

- Predicate tests should cover every listed IP-version boundary, MEC firmware threshold, and MES scheduler-version threshold.
- Ioctl-level tests should verify that unsupported capability predicates become the expected `-ENODEV`, `-EBUSY`, `-EACCES`, or no-op behavior.
- Build tests should ensure all declarations match `kfd_debug.c` definitions and that callers include the header rather than open-coding capability checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_debugfs.c

## Purpose

`kfd_debugfs.c` creates KFD debugfs entries used for diagnostics and controlled fault injection. It exposes root-level debugfs files for MQD/HQD/RL inspection, HWS hang triggering, and KFD memory-limit diagnostics, and it creates per-process debugfs directories that expose PASID values per GPU.

This is developer/debug infrastructure, not the stable userspace ABI. It is gated by debugfs availability and uses KFD-internal data structures directly.

## Important APIs, Types, and Entry Points

- `kfd_debugfs_init()` creates `/sys/kernel/debug/kfd`, `/sys/kernel/debug/kfd/proc`, initializes the internal process-entry list, and registers root debugfs files.
- `kfd_debugfs_fini()` recursively removes the process directory and root directory.
- `kfd_debugfs_add_process()` allocates a `debugfs_proc_entry`, creates `proc/<pid>`, and creates `pasid_<gpu_id>` files for each current PDD.
- `kfd_debugfs_remove_process()` finds the entry by PID, recursively removes its directory, unlinks it, and frees the entry.
- `kfd_debugfs_hang_hws_write()` parses a GPU ID from userspace and calls `kfd_debugfs_hang_hws()` for the matching KFD node.
- `kfd_debugfs_pasid_read()` exposes `pdd->pasid` through simple read semantics.
- `kfd_debugfs_open()` adapts single-show debugfs files to seq_file.

## Control Flow

Initialization creates the root and process directories first, then registers `mqds`, `hqds`, `rls`, `hang_hws`, and `mem_limit`. Most read-only root files share `kfd_debugfs_fops`, where `inode->i_private` is treated as the show callback passed to `single_open()`. `hang_hws` uses a write-capable fops table and the same open/read path for its usage text.

Writing `hang_hws` copies at most 15 bytes plus terminator into a local buffer, parses a decimal GPU ID, looks up the KFD node, and triggers the HWS hang helper if found. Invalid size, copy failure, parse failure, or missing device returns an error.

When a KFD process is added, the code creates a list entry keyed by lead-thread PID and creates one PASID file per PDD available at that moment. Removal searches the list under `kfd_processes_mutex`, removes the entire process debugfs subtree, and frees the entry.

## State and Persistence Behavior

File-global state consists of `debugfs_root`, `debugfs_proc`, and the `procs` list. Each `debugfs_proc_entry` stores the PID and directory dentry for one process debugfs subtree. PASID files store a raw `struct kfd_process_device *` in `i_private`; their correctness depends on process debugfs removal happening before the PDD memory becomes invalid.

Debugfs dentries and list entries persist until `kfd_debugfs_remove_process()` or `kfd_debugfs_fini()` removes them. Root files persist for the KFD module lifetime.

## Dependencies and Integration Points

The file depends on Linux debugfs, seq_file, user-copy helpers, and KFD process/device internals. Root show callbacks such as `kfd_debugfs_mqds_by_process`, `kfd_debugfs_hqds_by_device`, `kfd_debugfs_rls_by_device`, `kfd_debugfs_hang_hws`, and `kfd_debugfs_kfd_mem_limits` are implemented elsewhere in KFD.

It integrates with process lifecycle hooks that call add/remove, with KFD device lookup by GPU ID, and with the KFD scheduler diagnostics/fault-injection helpers.

## Risks and Edge Cases

- `kfd_debugfs_add_process()` modifies `procs` without taking `kfd_processes_mutex`, while removal iterates under that mutex. The caller's locking context must provide serialization or the list can race.
- Per-process PASID files hold PDD pointers. If debugfs removal lags behind PDD teardown, reads can dereference stale memory.
- `kfd_debugfs_fini()` removes both `debugfs_proc` and `debugfs_root` recursively; because `debugfs_proc` is under root, double-recursive removal must remain tolerated by debugfs semantics.
- `hang_hws` is a write-only fault-injection trigger. It validates input size and parse format but intentionally allows a privileged debugfs writer to hang scheduling on a selected GPU.
- Process entries are keyed only by PID. PID reuse after missed removal could create confusing debugfs state.

## Test and Validation Signals

- Debugfs lifecycle tests should initialize/finalize repeatedly, add/remove processes with multiple PDDs, and verify no stale dentries remain.
- PASID read tests should validate output format and behavior during process removal.
- `hang_hws` tests should cover oversized input, bad decimal input, missing GPU IDs, valid GPU IDs, and callback invocation.
- Concurrency tests should add/remove/read process entries while process teardown is active to catch stale pointer or list races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_debugfs.c -->

# subset-b-005971 Research

Grouped source research for DRM UAPI headers under `sources/distributed-fs/ceph-client/include/uapi/drm`. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/i915_drm.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/i915_drm.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/drm/i915_drm.h` is the userspace ABI contract for the Intel i915 DRM driver. It defines the ioctl command numbers, ioctl payload structures, capability parameters, GEM buffer object controls, execution submission ABI, context and VM configuration ABI, performance stream ABI, engine/memory discovery queries, protected-content extensions, and uevent/perf counter identifiers. The source was read as a complete 3916-line UAPI header.

## Important APIs, Types, and Functions

The header exports no callable C functions; its public surface is ioctl macros, constants, enums, and structs consumed by userspace and the kernel ioctl dispatch layer. The top-level ioctl range runs from legacy `DRM_I915_INIT`/`DRM_I915_BATCHBUFFER` through modern `DRM_I915_QUERY`, `DRM_I915_GEM_VM_CREATE`, `DRM_I915_GEM_VM_DESTROY`, and `DRM_I915_GEM_CREATE_EXT`. Core payloads include legacy DRI1 structs (`drm_i915_init_t`, `drm_i915_sarea_t`, batchbuffer, cmdbuffer, IRQ, vblank, heap management), GEM object APIs (`drm_i915_gem_create`, `drm_i915_gem_pread`, `drm_i915_gem_pwrite`, `drm_i915_gem_mmap`, `drm_i915_gem_mmap_offset`, `drm_i915_gem_set_domain`, `drm_i915_gem_caching`, tiling, aperture, madvise, wait, busy), submission APIs (`drm_i915_gem_relocation_entry`, `drm_i915_gem_exec_object2`, `drm_i915_gem_exec_fence`, `drm_i915_gem_execbuffer2`, timeline fence extension), and context APIs (`drm_i915_gem_context_create_ext`, `drm_i915_gem_context_param`, `drm_i915_gem_context_param_sseu`, engine map/load-balance/bond/parallel-submit extensions, `drm_i915_gem_vm_control`).

Discovery and profiling APIs are centered on `drm_i915_getparam`, `drm_i915_query`, `drm_i915_query_item`, topology/engine/perf/memory-region/GUC query structs, `drm_i915_perf_open_param`, OA format/property enums, OA config upload, and perf stream control ioctls (`I915_PERF_IOCTL_ENABLE`, `I915_PERF_IOCTL_DISABLE`, `I915_PERF_IOCTL_CONFIG`). Extension chaining is standardized by `struct i915_user_extension`, which appears in context, execbuffer, VM, and GEM create-extension flows. Memory placement is represented by `drm_i915_gem_memory_class_instance`, `drm_i915_query_memory_regions`, and `drm_i915_gem_create_ext_memory_regions`; protected-content and PAT creation policies use `drm_i915_gem_create_ext_protected_content` and `drm_i915_gem_create_ext_set_pat`.

## Control Flow

The header itself has no executable control flow. Runtime flow is encoded by ioctl usage sequences. Typical GEM object flow is: query capabilities with `GETPARAM` or `QUERY`, create a BO with `GEM_CREATE` or `GEM_CREATE_EXT`, optionally choose memory regions or protected/PAT extensions, retrieve a CPU mmap offset with `GEM_MMAP_OFFSET`, synchronize domains or caches, submit work through `GEM_EXECBUFFER2`, and wait via explicit fences, syncobjs, `GEM_WAIT`, or BO busy checks. Modern engine flow is: query engines with `DRM_I915_QUERY_ENGINE_INFO`, create a context with `CONTEXT_CREATE_EXT`, set `I915_CONTEXT_PARAM_ENGINES` and optional load-balance/bond/parallel-submit extensions, then use execbuffer ring bits as engine-map indexes. Query flow is usually two-pass: call with `length == 0`, allocate the returned size, then call again with `data_ptr` populated.

## State and Persistence Behavior

Most persistent state is fd-scoped: GEM handles, context IDs, VM IDs, perf stream fds, per-file object handles, and context engine maps live until explicit destroy/close or file teardown. BO contents and placement can persist across submissions and may migrate under memory pressure; madvise can make backing pages discardable and reports retention. Context persistence is controllable through `I915_CONTEXT_PARAM_PERSISTENCE`, and protected contexts/objects are invalidated when the PXP protected-content session is torn down. VM IDs created by `GEM_VM_CREATE` can be shared by contexts on the same fd and destroyed explicitly. Perf streams are separate fds with enable/disable/configuration state. The UAPI comments repeatedly mark reserved fields and undefined flag bits as must-be-zero, making zero initialization part of the persistence/compatibility contract.

## Dependencies and Integration Points

The header depends on `drm.h` for DRM base types, ioctl construction macros, fixed-width UAPI types, `drm_clip_rect`, vblank definitions, handles, and `__user` annotations. It integrates with the i915 kernel ioctl table, Mesa/Intel userspace drivers, intel-gpu-tools, perf event sources, dma-buf/PRIME, sync_file, DRM syncobj/timeline syncobj, protected content/PXP services, GuC firmware interfaces, and KMS/display paths for scanout, overlay, and sprite colorkeying. PMU defines integrate with `/sys/bus/event_sources/drivers/i915`; uevent names integrate with device node event consumers.

## Risks and Edge Cases

This is a large stable ABI, so any field reordering, type-width change, ioctl number change, or reuse of removed IDs is high risk. Legacy pointer-bearing structs such as `drm_i915_getparam` require compat32 handling; newer structs use `__u64` user pointers to avoid that problem. Execution submission has many synchronization hazards: `EXEC_OBJECT_ASYNC`, `I915_EXEC_NO_RELOC`, pinned objects, explicit fences, timeline fences, and output fence writeback can cause hangs, corruption, fd leaks, or missing synchronization if userspace and kernel disagree. Discrete/local-memory behavior changes caching and domain semantics, so `SET_DOMAIN`, `SET_CACHING`, mmap modes, small-BAR CPU visibility, and create-extension placement rules need strict validation. Protected-content context creation has system dependency timing failures and stricter recovery/bannability constraints. Query and extension chains require loop detection, size validation, MBZ checks, and robust copy-from-user handling.

## Test Signals

Useful tests include UAPI compile checks for C and C++, ioctl number ABI tests, struct size/offset tests across 32-bit and 64-bit builds, invalid flag/MBZ rejection tests, compat ioctl tests for pointer-bearing legacy structs, two-pass query coverage, GEM create/mmap/domain/cache/tiling/wait/madvise coverage, execbuffer tests for relocations, no-reloc, softpin, fence in/out, fence arrays and timeline fences, context creation with engine maps/load-balance/bond/parallel-submit/SSEU/VM/persistence/protected content, memory-region query and create-extension placement tests, perf stream open/read/config/error-record tests, and fault-injection coverage for GPU reset, PXP teardown, userptr invalidation, small-BAR pressure, and async synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/i915_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/ivpu_accel.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/ivpu_accel.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/drm/ivpu_accel.h` defines the userspace ABI for Intel VPU/NPU accelerator devices. It covers device/context parameter queries, SHMEM and userptr-backed GEM buffer creation, BO information and wait, command submission, explicit command queues, job priorities, and hardware metric streaming. The source was read as a complete 564-line UAPI header.

## Important APIs, Types, and Functions

The ioctl surface includes `DRM_IOCTL_IVPU_GET_PARAM`, `SET_PARAM`, `BO_CREATE`, `BO_INFO`, `SUBMIT`, `BO_WAIT`, metric streamer start/stop/get-data/get-info, command queue create/destroy/submit, and `BO_CREATE_FROM_USERPTR`. Important structs are `drm_ivpu_param`, `drm_ivpu_bo_create`, `drm_ivpu_bo_create_from_userptr`, `drm_ivpu_bo_info`, `drm_ivpu_submit`, `drm_ivpu_cmdq_submit`, `drm_ivpu_bo_wait`, `drm_ivpu_metric_streamer_start`, `drm_ivpu_metric_streamer_get_data`, `drm_ivpu_cmdq_create`, `drm_ivpu_cmdq_destroy`, and `drm_ivpu_metric_streamer_stop`. Parameters expose device ID/revision/platform/core clock/context limits/context ID/firmware API/engine heartbeat/inference ID/tile config/SKU/capabilities/preempt buffer size. Capability bits advertise metric streaming, DMA memory range, managed command queues, and BO creation from user pointers.

## Control Flow

A typical userspace flow is: open the DRM accelerator fd, query capabilities and context metadata, create BOs with the requested VPU virtual address and cache/memory flags, submit a command buffer with a BO handle array where the first BO is the command buffer, then wait for command-buffer inactivity and job status with `BO_WAIT`. Newer managed-queue flow creates a command queue with a priority and optional turbo flag, submits command buffers to that queue with a preemption buffer index, and later destroys the queue. Metric streaming flow starts a selected metric group, periodically probes or copies data through get-data, and stops the group when profiling is complete.

## State and Persistence Behavior

VPU contexts are created on file open and have private virtual address space, job queues, priority, and a unique context ID. BOs persist as GEM handles until closed and carry a returned VPU virtual address plus optional mmap offset. Command queue IDs persist until `CMDQ_DESTROY`. Metric streamer state is keyed by metric group mask and remains active until stopped; data can be lost if userspace reads much later than the advertised read period. Job status is reported through `drm_ivpu_bo_wait` for command buffers.

## Dependencies and Integration Points

The header depends on `drm.h` for DRM ioctl macros and UAPI integer types. It integrates with the iVPU DRM accelerator driver, GEM/dma-buf memory management, firmware command formats, engine heartbeat/firmware API reporting, profiler tooling for metric streamer data, and userspace inference runtimes that manage command buffers and referenced BO lists.

## Risks and Edge Cases

Risk centers on validating user pointers, BO flag combinations, VPU address ranges, command offsets, and queue IDs. `BO_CREATE_FROM_USERPTR` requires page-aligned pointers/sizes and must defend against invalid or revoked user memory. Reserved fields and unsupported flags such as `DRM_IVPU_BO_UNCACHED` must be rejected consistently. Metric streaming can overflow or lose samples if buffer sizing/read period handling is wrong. Command submission depends on a complete BO list; missing referenced BOs or wrong first-buffer command semantics can lead to firmware faults.

## Test Signals

Tests should cover get/set param permissions and indexed heartbeat queries; BO creation for high memory, DMA memory, mappable, read-only, cached and WC modes; userptr alignment and invalid-memory failure; BO info mmap offsets; legacy submit and managed command-queue submit; queue priority/turbo handling; BO wait timeout and aborted job status; metric streamer start/get-info/get-data/stop including zero-size probe; and MBZ/reserved-field rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/ivpu_accel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/lima_drm.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/lima_drm.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/drm/lima_drm.h` defines the DRM UAPI for the Lima driver for Arm Mali-400/Mali-450 GPUs. It exposes GPU parameter discovery, GEM BO creation/info/wait, GP/PP task submission frame layouts, explicit syncobj submission, and context create/free operations. The source was read as a complete 176-line UAPI header.

## Important APIs, Types, and Functions

Public ioctls are `DRM_IOCTL_LIMA_GET_PARAM`, `GEM_CREATE`, `GEM_INFO`, `GEM_SUBMIT`, `GEM_WAIT`, `CTX_CREATE`, and `CTX_FREE`. Types include `drm_lima_get_param`, `drm_lima_gem_create`, `drm_lima_gem_info`, `drm_lima_gem_submit_bo`, Mali GP/PP frame structs (`drm_lima_gp_frame`, `drm_lima_m400_pp_frame`, `drm_lima_m450_pp_frame`), `drm_lima_gem_submit`, `drm_lima_gem_wait`, `drm_lima_ctx_create`, and `drm_lima_ctx_free`. Parameters expose GPU ID, number of pixel processors, and GP/PP versions. `LIMA_BO_FLAG_HEAP` marks heap buffers whose backing memory can grow after GP out-of-heap failures.

## Control Flow

Userspace queries GPU identity, creates a context, creates GEM BOs, obtains GPU virtual addresses and mmap offsets with `GEM_INFO`, builds GP or PP frame data, submits a task with a BO table and frame pointer, optionally supplies input syncobjs and an output syncobj under `LIMA_SUBMIT_FLAG_EXPLICIT_FENCE`, waits for BO read/write completion if CPU access is needed, and frees the context when finished.

## State and Persistence Behavior

Context IDs persist until `CTX_FREE`. GEM handles persist under standard DRM handle lifetime rules and have driver-assigned GPU virtual addresses. Heap BOs have dynamic backing behavior, with the declared size acting as an upper bound for memory that may be added when GP execution needs more heap. Syncobj handles are external DRM synchronization objects and are not owned by this header, but submissions can wait on and signal them.

## Dependencies and Integration Points

The header depends on `drm.h`. It integrates with the Lima kernel scheduler/MMU, Mesa Lima userspace, DRM GEM/mmap infrastructure, syncobj/timeline synchronization infrastructure, and Mali-400/450 command frame formats.

## Risks and Edge Cases

The ABI is compact but sensitive to frame-size validation, GP versus PP pipe selection, Mali-400 versus Mali-450 frame layout differences, and BO read/write flag correctness. Heap BO growth must not exceed the declared upper bound. Explicit fence arrays have fixed slots and must handle zero handles correctly. Absolute timeout handling in `GEM_WAIT` must be robust to interrupted syscalls.

## Test Signals

Tests should cover all get-param values, GEM create/info for normal and heap BOs, invalid flags and padding rejection, context create/free lifetime, GP and PP submissions with Mali-400 and Mali-450 frame sizes, explicit fence in/out syncobj behavior, read/write BO wait timeouts, and negative tests for wrong pipe, frame size, BO handle, and sync handle values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/lima_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/msm_drm.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/msm_drm.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/drm/msm_drm.h` is the UAPI for the Qualcomm/Adreno MSM DRM driver. It defines parameter query/set operations, GEM allocation and metadata, CPU prep/fini synchronization, command stream submission with relocations and fences, VM_BIND mode, fence waits, madvise, and submitqueue management. The source was read as a complete 529-line UAPI header.

## Important APIs, Types, and Functions

The ioctl surface includes `GET_PARAM`, `SET_PARAM`, `GEM_NEW`, `GEM_INFO`, `GEM_CPU_PREP`, `GEM_CPU_FINI`, `GEM_SUBMIT`, `WAIT_FENCE`, `GEM_MADVISE`, `SUBMITQUEUE_NEW`, `SUBMITQUEUE_CLOSE`, `SUBMITQUEUE_QUERY`, and `VM_BIND`. Important types are `drm_msm_timespec`, `drm_msm_param`, `drm_msm_gem_new`, `drm_msm_gem_info`, `drm_msm_gem_cpu_prep`, `drm_msm_syncobj`, `drm_msm_gem_submit_reloc`, `drm_msm_gem_submit_cmd`, `drm_msm_gem_submit_bo`, `drm_msm_gem_submit`, `drm_msm_vm_bind_op`, `drm_msm_vm_bind`, `drm_msm_wait_fence`, `drm_msm_gem_madvise`, `drm_msm_submitqueue`, and `drm_msm_submitqueue_query`. Parameters include GPU/chip identity, GMEM, frequencies, timestamps, fault/suspend counters, VA range, tiling/compression details, PRR support, VM_BIND enablement, and AQE support.

## Control Flow

Classic flow is: query device and VA properties, create GEM BOs with scanout/read-only/private/cache flags, get mmap offset or IOVA/name/metadata with `GEM_INFO`, prepare/finalize CPU access, create submitqueues with priority/preemption properties, submit command buffers with a BO table and command table, process relocations sorted by submit offset, and wait using fence sequence numbers, fence fds, or syncobjs. VM_BIND flow is explicitly opt-in through `MSM_PARAM_EN_VM_BIND` before BO or VM_BIND submitqueue creation; after that userspace allocates IOVA itself, uses `VM_BIND` map/unmap/map-null operations, and submits without a submit BO table because residency is determined by bound mappings.

## State and Persistence Behavior

GEM handles, submitqueue IDs, fence sequence numbers, and optional VM_BIND enablement are fd/context state. `MSM_PARAM_EN_VM_BIND` is a write-once switch and cannot be disabled. In VM_BIND mode, failed async bind operations or GPU faults can mark the VM unusable; later submit calls fail with `-EPIPE`, and recovery requires new state. Private BOs share a single reservation object within a context to reduce per-BO submission overhead and cannot be shared or used for scanout. Madvise can discard BO backing pages under pressure and reports retention. Submitqueue ID 0 is reserved for backwards compatibility.

## Dependencies and Integration Points

The header depends on `drm.h`. It integrates with the MSM/Adreno kernel scheduler, per-process page tables, DRM GEM and dma-buf, DRM syncobj/timeline syncobj, sync_file fence fds, Mesa freedreno/turnip userspace, KMS scanout, and GPU fault accounting/debug metadata.

## Risks and Edge Cases

The main risk areas are ABI extensibility rules, user pointer/length handling in `GEM_INFO`, relocation validation and sorted-order enforcement, synchronization mode combinations, and VM_BIND state transitions. VM_BIND changes the meaning of `GEM_INFO_GET_IOVA`/`SET_IOVA` and submit BO tables, so mixed-mode behavior must be rejected clearly. `MSM_SUBMIT_NO_IMPLICIT`, BO-level no-implicit flags, syncobj reset flags, and fence fd in/out can cause data races or missed waits if mishandled. Private BO restrictions must prevent sharing/scanout/import/export lifetime bugs.

## Test Signals

Tests should cover param get/set permissions including write-only sysprof/comm/cmdline and write-once VM_BIND; GEM create flags and cache modes; `GEM_INFO` scalar and pointer metadata paths including null-probe length behavior; CPU prep/fini with absolute timeout; submit reloc sorting, presumed IOVA writeback, command types, fence fd in/out, syncobj in/out, submitqueue priority/preempt flags; VM_BIND map/unmap/map-null/dump, multi-op arrays, op stride, async fences, VM unusable after injected failure; madvise retention; and submitqueue query faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/msm_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/nouveau_drm.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/nouveau_drm.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/drm/nouveau_drm.h` defines the userspace ABI for the Nouveau NVIDIA DRM driver. It spans legacy channel/GPU object allocation, GEM BO allocation and pushbuffer submission, CPU prep/fini, SVM migration, modern VM initialization and VM_BIND, modern EXEC submission with sync objects, and zcull information queries. The source was read as a complete 586-line UAPI header.

## Important APIs, Types, and Functions

Public ioctls include `GETPARAM`, `CHANNEL_ALLOC`, `CHANNEL_FREE`, `SVM_INIT`, `SVM_BIND`, `GEM_NEW`, `GEM_PUSHBUF`, `GEM_CPU_PREP`, `GEM_CPU_FINI`, `GEM_INFO`, `VM_INIT`, `VM_BIND`, `EXEC`, and `GET_ZCULL_INFO`; several old IDs remain marked deprecated. Important structs include `drm_nouveau_getparam`, `drm_nouveau_channel_alloc/free`, notifier/gpuobj legacy structs, `drm_nouveau_gem_info`, `drm_nouveau_gem_new`, pushbuf BO/reloc/push structures, `drm_nouveau_sync`, `drm_nouveau_vm_init`, `drm_nouveau_vm_bind_op`, `drm_nouveau_vm_bind`, `drm_nouveau_exec_push`, `drm_nouveau_exec`, `drm_nouveau_get_zcull_info`, `drm_nouveau_svm_init`, and `drm_nouveau_svm_bind`. Constants define VRAM/GART/CPU/mappable/coherent/no-share domains, tile flags, push limits, syncobj versus timeline syncobj types, sparse VM_BIND mappings, and SVM migration bitfields.

## Control Flow

Legacy flow creates channels, GEM BOs, validates pushbuffer BO lists/relocs/push arrays, submits via `GEM_PUSHBUF`, and synchronizes with CPU prep/fini. Modern flow starts by calling `VM_INIT` before any BOs or channels are created, partitioning VA space between userspace and kernel-managed regions. Userspace then allocates BOs, uses `VM_BIND` operations to map/unmap GEM objects or sparse regions with optional asynchronous sync waits/signals, and submits command pushes by virtual address via `EXEC` with wait and signal sync arrays. SVM flow initializes an unmanaged range and uses encoded bind headers to migrate ranges, currently with GPU VRAM as a target flag.

## State and Persistence Behavior

Channels, GEM handles, VM initialization state, VA mappings, sparse regions, sync dependencies, and SVM state are fd/client-scoped. `VM_INIT` must happen before BO or channel creation, so it establishes long-lived mode/state for the client. Asynchronous VM_BIND operations can outlive the ioctl and signal DRM sync objects. `GEM_PUSHBUF` reports available VRAM/GART after submission. Zcull information describes hardware state needed for context switching and region setup.

## Dependencies and Integration Points

The header depends on `drm.h`. It integrates with Nouveau's channel and memory managers, GEM/dma-buf, NVIDIA GPU pushbuffer formats, DRM syncobj/timeline syncobj, SVM/HMM migration paths, sparse residency, Mesa/NVK/Nouveau userspace, and zcull hardware state management.

## Risks and Edge Cases

High-risk areas include preserving deprecated ioctl numbers, enforcing push/reloc/buffer maximums, validating relocation domains and presumed offsets, guaranteeing `VM_INIT` ordering, and handling async VM_BIND synchronization correctly. Sparse VM_BIND unmap has special semantics: unmapping inside a sparse region recreates sparse mappings unless the sparse flag removes the sparse region. SVM bitfield validation must reject unknown high bits. Modern EXEC by virtual address relies on valid prior VM bindings; stale or overlapping bindings can fault if not checked.

## Test Signals

Tests should cover getparam values, channel allocation/free and engine selection, GEM domain/tile allocation and info, pushbuf limits and relocation variants, CPU prep nowait/write behavior, VM_INIT ordering failures, VM_BIND map/unmap/sparse/async wait-signal paths, EXEC multi-push and syncobj/timeline syncobj waits/signals, SVM init/bind migration bitfield validation, zcull info query, and negative tests for unknown flags, bad handles, overlapping VA ranges, and exceeding push/reloc/BO limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/nouveau_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/nova_drm.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/nova_drm.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/drm/nova_drm.h` is a deliberately unstable testing UAPI for the in-development Nova driver. It currently exposes only VRAM BAR size query plus minimal GEM create/info operations. The source was read as a complete 101-line UAPI header.

## Important APIs, Types, and Functions

The UAPI defines `NOVA_GETPARAM_VRAM_BAR_SIZE`, `drm_nova_getparam`, `drm_nova_gem_create`, and `drm_nova_gem_info`. It assigns ioctl IDs `DRM_NOVA_GETPARAM`, `DRM_NOVA_GEM_CREATE`, and `DRM_NOVA_GEM_INFO`. Unlike most C UAPI headers that use `#define` ioctl macros, the ioctl numbers are placed in an anonymous enum so Rust bindgen can resolve them.

## Control Flow

The only supported flow is: query driver/device metadata through `GETPARAM`, create a GEM object with a requested size through `GEM_CREATE`, and query a GEM object's size through `GEM_INFO`. No submission, mapping offset, synchronization, VM, or command queue control is described in this header.

## State and Persistence Behavior

GEM handles returned by `GEM_CREATE` persist under standard DRM GEM handle lifetime rules. The header itself warns that the UAPI is not stable and exists only for testing driver infrastructure while Nova is under development.

## Dependencies and Integration Points

The header depends on `drm.h` and integrates with early Nova kernel driver infrastructure, GEM allocation, and Rust/C userspace binding generation tests. It is not a stable userspace contract for production drivers.

## Risks and Edge Cases

The explicit disclaimer is the main risk signal: external userspace must not rely on this ABI. Even small field or ioctl changes are possible while the driver is being developed. Padding must be zero, sizes must be validated and aligned by the driver, and bindgen-friendly enum ioctl generation must remain compatible with C consumers.

## Test Signals

Tests should cover bindgen visibility of ioctl enum values, getparam for VRAM BAR size, GEM create size alignment and invalid-size rejection, GEM info for valid and invalid handles, padding rejection, and build coverage from both C and Rust-generated bindings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/nova_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/omap_drm.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/omap_drm.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/drm/omap_drm.h` defines the TI OMAP DRM UAPI for chipset parameter access and GEM buffer allocation/information, including scanout, cacheability, and TILER-backed tiled buffer modes. The source was read as a complete 126-line UAPI header.

## Important APIs, Types, and Functions

Public ioctls are `DRM_IOCTL_OMAP_GET_PARAM`, `SET_PARAM`, `GEM_NEW`, deprecated `GEM_CPU_PREP`, deprecated `GEM_CPU_FINI`, and `GEM_INFO`. Important types are `drm_omap_param`, `union omap_gem_size`, `drm_omap_gem_new`, `omap_gem_op`, `drm_omap_gem_cpu_prep`, `drm_omap_gem_cpu_fini`, and `drm_omap_gem_info`. Flags cover scanout buffers, cached/WC/uncached CPU mapping modes, and TILER modes with 8/16/32-bit container units.

## Control Flow

Userspace can query or set driver parameters, create a GEM object by passing either byte size or tiled width/height depending on flags, retrieve mmap offset and virtual mmap size with `GEM_INFO`, and use the deprecated CPU prep/fini ioctls around CPU access when older userspace requires them.

## State and Persistence Behavior

GEM handles persist under standard DRM lifetime rules. Tiled buffers have a user-visible virtual mmap size that may differ from the physical backing size. CPU prep/fini do not own long-lived state in the header but signal cache synchronization operations around software access.

## Dependencies and Integration Points

The header depends on `drm.h`. It integrates with the OMAP DRM driver, OMAP DSS scanout, TILER memory layout, GEM mmap/open infrastructure, and older userspace that still calls the deprecated CPU synchronization ioctls.

## Risks and Edge Cases

The key risk is interpreting `union omap_gem_size` correctly for tiled versus non-tiled allocations. Cache and TILER flag masks must reject invalid combinations. Deprecated CPU prep/fini paths should remain compatible until removed and must keep full-buffer cache synchronization semantics despite the placeholder region fields.

## Test Signals

Tests should cover chipset parameter query, GEM_NEW for linear and tiled 8/16/32 buffers, scanout and cache mode flag combinations, `GEM_INFO` mmap offset and virtual size for tiled buffers, padding/invalid flag rejection, and legacy CPU prep/fini compatibility paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/omap_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/panfrost_drm.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/panfrost_drm.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/drm/panfrost_drm.h` defines the DRM UAPI for Arm Mali Midgard/Bifrost Panfrost GPUs using the job-manager model. It covers job submission, BO wait/create/mmap/offset, device parameter queries, performance counter debug ioctls, madvise, BO labeling and sync, BO info, JM context priority management, and coredump decoding structures. The source was read as a complete 476-line UAPI header.

## Important APIs, Types, and Functions

Stable ioctls include `SUBMIT`, `WAIT_BO`, `CREATE_BO`, `MMAP_BO`, `GET_PARAM`, `GET_BO_OFFSET`, `MADVISE`, `SET_LABEL_BO`, `JM_CTX_CREATE`, `JM_CTX_DESTROY`, `SYNC_BO`, and `QUERY_BO_INFO`. `PERFCNT_ENABLE` and `PERFCNT_DUMP` are explicitly unstable debug ioctls gated by the unsafe `unstable_ioctls` module parameter. Important structs include `drm_panfrost_submit`, `drm_panfrost_wait_bo`, `drm_panfrost_create_bo`, `drm_panfrost_mmap_bo`, `drm_panfrost_get_param`, `drm_panfrost_get_bo_offset`, `drm_panfrost_perfcnt_enable`, `drm_panfrost_perfcnt_dump`, `drm_panfrost_madvise`, `drm_panfrost_set_label_bo`, `drm_panfrost_bo_sync_op`, `drm_panfrost_sync_bo`, `drm_panfrost_query_bo_info`, coredump header/register structs, and `drm_panfrost_jm_ctx_create/destroy`.

## Control Flow

Userspace queries GPU feature registers and selected coherency, creates BOs with executable/heap/WB-mmap choices, obtains GPU offsets and CPU mmap offsets, submits a job descriptor address with referenced BO handles plus optional input/output syncobjs and JM context handle, waits on BO completion when necessary, labels BOs for diagnostics, performs explicit BO cache sync for imported or noncoherent mappings, and manages JM contexts for non-default priorities. Performance counter flow is separate and debug-only: enable a counter set and dump samples to a userspace buffer.

## State and Persistence Behavior

BOs persist as GEM handles and receive fd-private GPU offsets. Heap BOs and JM contexts have driver-managed lifetime. JM context handles persist until destroyed and encode priority subject to capability checks. Madvise can mark BO backing discardable and report whether pages were retained. BO labels persist for diagnostics until cleared or object destruction. Coredump structs describe persisted crash artifacts exported for userspace decoding, not live control state.

## Dependencies and Integration Points

The header depends on `drm.h`. It integrates with Panfrost kernel job scheduling, GEM/shmem and dma-buf import, DRM syncobj, Mali feature register decoding, Mesa Panfrost userspace, GPU coredump tooling, and cache maintenance paths for noncoherent or imported BOs.

## Risks and Edge Cases

Risks include unstable perfcnt ioctl reliance, BO flag restrictions such as `PANFROST_BO_WB_MMAP` not combining with heap, imported BO cache-coherency handling, priority privilege checks, and sync object validation. Job submission must validate job descriptor addresses, BO handle arrays, requirements bits, and JM context handles. Coredump structures are native-endian and magic-based, so tools must detect endianness. BO sync range rounding must avoid overflow.

## Test Signals

Tests should cover get-param feature values, create/mmap/get-offset/query-info for normal, heap, noexec, WB-mapped and imported BOs; submit with syncobj waits/signals and JM context handles; wait timeout behavior; madvise retained status; BO label set/clear and length limit; BO sync flush/invalidate ranges; JM context priority permission checks; perfcnt gating by module parameter; and coredump header decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/panfrost_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/panthor_drm.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/panthor_drm.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/drm/panthor_drm.h` defines the modern DRM UAPI for Arm Mali CSF GPUs handled by Panthor. It documents strict UAPI extensibility rules and covers device queries, user MMIO offsets, VM lifecycle and async VM_BIND, BO creation/mmap/sync/info/labels, scheduling group and queue creation/submission/state, tiler heap creation, sync operations, and timestamp/GPU/CSIF/priority information. The source was read as a complete 1305-line UAPI header.

## Important APIs, Types, and Functions

The ioctl ID enum exports `DEV_QUERY`, `VM_CREATE`, `VM_DESTROY`, `VM_BIND`, `VM_GET_STATE`, `BO_CREATE`, `BO_MMAP_OFFSET`, `GROUP_CREATE`, `GROUP_DESTROY`, `GROUP_SUBMIT`, `GROUP_GET_STATE`, `TILER_HEAP_CREATE`, `TILER_HEAP_DESTROY`, `BO_SET_LABEL`, `SET_USER_MMIO_OFFSET`, `BO_SYNC`, and `BO_QUERY_INFO`; final ioctl numbers are generated through `DRM_IOCTL_PANTHOR`. Core shared structs are `drm_panthor_obj_array` with stride/count/pointer versioning and `drm_panthor_sync_op` for binary or timeline syncobj wait/signal operations. Query structs include `drm_panthor_gpu_info`, `drm_panthor_csif_info`, `drm_panthor_timestamp_info`, `drm_panthor_group_priorities_info`, and `drm_panthor_dev_query`.

VM and memory APIs include `drm_panthor_vm_create/destroy`, `drm_panthor_vm_bind_op`, `drm_panthor_vm_bind`, `drm_panthor_vm_get_state`, `drm_panthor_bo_create`, `drm_panthor_bo_mmap_offset`, `drm_panthor_bo_sync_op`, `drm_panthor_bo_sync`, and `drm_panthor_bo_query_info`. Scheduling APIs include `drm_panthor_queue_create`, `drm_panthor_group_create`, `drm_panthor_group_destroy`, `drm_panthor_queue_submit`, `drm_panthor_group_submit`, and `drm_panthor_group_get_state`. Tiler and debug/user integration APIs include `drm_panthor_tiler_heap_create/destroy`, `drm_panthor_bo_set_label`, and `drm_panthor_set_user_mmio_offset`.

## Control Flow

A typical userspace flow is: query GPU/CSIF/timestamp/priority information, create a VM with a user/kernel VA split, create BOs with optional exclusive VM ownership, bind BO ranges into the VM synchronously or asynchronously using arrays of bind ops and sync operations, create scheduling groups with queue definitions and core masks tied to the VM, create tiler heaps when tiler jobs require firmware-managed heap chunks, submit command streams to queues within a group using `GROUP_SUBMIT`, and query group/VM state after faults or timeouts. Cache-flush reduction flow maps the read-only latest-flush-id MMIO page at the architecture-appropriate user MMIO offset, optionally overriding that offset for emulation environments.

## State and Persistence Behavior

VM IDs, BO handles, scheduling group handles, tiler heap handles, queue state, labels, and async VM_BIND queue work are fd-scoped state. VM state can become `UNUSABLE` after an async VM_BIND failure; after that MAP operations and GPU jobs fail, while UNMAP remains accepted, and recovery requires creating a new VM. Group state can become timed out or fatally faulted, after which no more queue submissions are allowed and userspace should create a replacement group. Exclusive-VM BOs cannot be exported as PRIME fds and can only bind to the specified VM. Tiler heaps form firmware-managed linked chunk lists with initial and maximum chunk counts.

## Dependencies and Integration Points

The header depends on `drm.h` and uses `uintptr_t` in the `DRM_PANTHOR_OBJ_ARRAY` helper. It integrates with Panthor CSF firmware scheduling, DRM GEM/dma-buf, DRM syncobj/timeline syncobj, VM page-table management, Mali GPU/CSIF feature discovery, userspace command stream generation, cache maintenance and flush-id MMIO mapping, PRIME import/export policy, tiler heap firmware objects, and Mesa Panthor userspace.

## Risks and Edge Cases

The header explicitly encodes compatibility rules: 64-bit alignment, natural alignment, zeroed padding, append-only ioctl IDs, append-or-padding field additions, stride-sized indirect arrays, version bumps for new fields, and no unions. Violating these rules risks breaking old or new userspace. VM_BIND risk is high because async failure makes the VM unusable; sync-only ops require async mode and at least one sync. Group creation must validate queue arrays, core masks, maximum core counts, VM IDs, and privileged priorities. Queue submissions require 8-byte stream size alignment and 64-byte stream address alignment. Imported BOs may need explicit `BO_SYNC` even on coherent systems because exporter-side migration or cache behavior can be hidden. User MMIO offsets differ for 32-bit and 64-bit pgoff handling and can be wrong under emulation without override.

## Test Signals

Tests should cover query size-probe and partial-copy behavior for all query types; 32-bit and 64-bit user MMIO offset selection and override; VM create user VA split, bind map/unmap/sync-only, async sync waits/signals, VM unusable failure injection, and get-state; BO create flags/exclusive VM/export rejection, mmap offset, labels, imported BO query and sync flush/invalidate ranges; group create with queue stride/count, priority permission checks, core mask validation, submit alignment and synchronization, group timeout/fatal/innocent state; tiler heap bounds and returned GPU VAs; object-array stride forward/backward compatibility; and strict MBZ/unknown flag rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/panthor_drm.h -->

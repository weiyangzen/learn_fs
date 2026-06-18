# subset-b-005972 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/pvr_drm.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/pvr_drm.h

## Purpose
This header is the public userspace/kernel ABI for the Imagination PowerVR DRM driver. It defines ioctl numbers, fixed-layout argument records, query records, object-array versioning, GPU virtual-memory controls, render context setup, PM/free-list setup, HWRT dataset setup, and syncobj-backed job submission. It is not executable code, but it is a persistent ABI: field ordering, numeric ioctl IDs, enum values, padding requirements, and reserved-bit handling are part of the contract with Mesa/userspace.

## Important APIs and types
The `PVR_IOCTL()` macro maps driver ioctl IDs `0x00` through `0x0d` to `DRM_IOCTL_PVR_*` commands. The lifecycle is built around `DRM_IOCTL_PVR_DEV_QUERY`, `CREATE_BO`, `GET_BO_MMAP_OFFSET`, `CREATE_VM_CONTEXT`, `VM_MAP`, `CREATE_CONTEXT`, `CREATE_FREE_LIST`, `CREATE_HWRT_DATASET`, and `SUBMIT_JOBS`, with matching destroy/unmap calls.

`struct drm_pvr_obj_array` is the important extensibility primitive. It carries `stride`, `count`, and a userspace array pointer so indirect arrays can be versioned the same way ioctl structs are. Query records include GPU BVNC identity, runtime limits, quirks, enhancements, heap information, and static data areas. BO flags cover device-cache bypass, PM/firmware protection, and CPU userspace mapping. VM map/unmap structs bind GEM handles into userspace-managed GPU VA heaps. Context enums distinguish render, compute, and transfer-fragment contexts with low/normal/high priorities. `drm_pvr_sync_op`, `drm_pvr_job`, and `drm_pvr_ioctl_submit_jobs_args` define job submission with binary or timeline syncobj wait/signal operations.

## Control flow and state
Userspace first queries device/runtime data, especially heaps and static data areas. It then creates GEM BOs, asks for mmap offsets if CPU access is permitted, creates a VM context, and maps BO ranges into one of the advertised heaps. Render-capable workloads create typed contexts, PM protected free lists, and HWRT datasets. `SUBMIT_JOBS` passes an array of typed jobs, each with a command stream pointer, sync operation array, compatible context handle, flags, and optional HWRT reference. On submission error, `jobs.count` is repurposed as the failing job index, which is an ABI-visible control-flow signal.

## State and persistence behavior
Handles returned by create ioctls are per-DRM-file kernel objects and remain valid until explicit destroy/close or file teardown. GPU virtual mappings persist in the VM context until unmapped. HWRT datasets reference previously created free lists and GPU addresses, so stale handles or address-space reuse can corrupt later submissions. Query values are runtime/device facts and may vary by GPU generation. Padding and implicit union padding are required to be zero, giving the kernel deterministic ABI validation and room for forward-compatible expansion.

## Dependencies and integration points
The header depends on `drm.h`, `linux/types.h`, and `linux/const.h`. It integrates with DRM GEM handles, real `mmap()` on DRM fake offsets, DRM syncobj/timeline syncobj semantics, UMD command stream generation, and PowerVR firmware/runtime heap layouts. Userspace must coordinate with kernel heap information rather than invent GPU virtual addresses outside advertised regions.

## Risks and test signals
Main risks are ABI breakage from reordering append-only enums, changing struct layout, ignoring MBZ padding, accepting reserved flag bits, or failing 32/64-bit pointer compatibility. Security-sensitive paths include userspace pointers, command streams, BO/VM mapping ranges, and PM/firmware-protected BO flags. Test signals should include ioctl struct size/alignment checks, zero-padding rejection, invalid flag rejection, heap-boundary mapping failures, destroy-after-use behavior, syncobj wait/signal paths, timeline values, failed multi-job index reporting, and 32-bit compat tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/pvr_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/qaic_accel.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/qaic_accel.h

## Purpose
This file defines the DRM accelerator UAPI for Qualcomm AI Cloud devices. The ABI exposes management transactions, GEM BO allocation/mapping, DBC activation/deactivation, BO slicing, execution, waits, and performance-stat collection. The file is pure UAPI data definition: the semantics live in the kernel driver and device firmware, but these structs are the stable wire format.

## Important APIs and types
`QAIC_MANAGE_MAX_MSG_LENGTH` caps management messages at 4 KiB including `qaic_manage_msg` fields. Management transactions share `qaic_manage_trans_hdr` with `type` and `len`; transaction types cover passthrough, DMA transfer, activate/deactivate/status, terminate, validate-partition, and continuation flows. `qaic_manage_msg` carries total length, transaction count, and a userspace pointer to packed transactions.

BO ioctls use `qaic_create_bo` and `qaic_mmap_bo`. Execution setup is centered on `qaic_attach_slice`, whose header binds a GEM handle to a DBC ID and direction, while entries describe BO slices, up to four semaphore commands, device addresses, doorbell addresses/data, and offsets. Execution uses `qaic_execute` over `qaic_execute_entry` records or the partial-resize equivalent. Synchronization fields include semaphore command constants and fence flags for in/out sync fences. Performance stats use `qaic_perf_stats` and `qaic_perf_stats_entry`.

## Control flow and state
Typical userspace control flow is: send `DRM_IOCTL_QAIC_MANAGE` status/activation transactions to obtain a DBC, create BOs, map BOs if CPU access is needed, attach slice metadata to BOs for a specific DBC, execute one or more BOs, wait for completion, optionally gather perf stats, then detach slices and deactivate through management transactions. Partial execute lets userspace resize a BO transfer for one submission without reallocating the original BO.

## State and persistence behavior
GEM BO handles persist as DRM objects. Slice attachment persists per BO until detach, and embeds DBC association, direction, DMA device address, semaphore actions, and doorbell programming. DBC IDs are assigned by device activation and must be used consistently across attach/execute/wait/stats calls. Perf entries report transient queue and latency measurements for submitted BOs. Reserved `pad` fields must remain zero for deterministic ABI compatibility.

## Dependencies and integration points
The header includes `drm.h` and relies on DRM ioctl encoding, GEM handles, mmap offsets, firmware-defined transaction payloads, DBC queues, doorbells, and device DMA addressing. It also integrates with Linux DMA direction conventions through numeric `dir` values documented as 1-to-device and 2-from-device.

## Risks and test signals
Risks include malformed packed management transactions, length/count mismatches, endian mistakes in passthrough payloads, nonzero padding, stale DBC IDs, slice offsets exceeding BO size, invalid semaphore bit widths, and doorbell programming with unsupported lengths. Tests should cover max-size management messages, mixed transaction sequences, activation failure paths, BO size and mmap offsets, attach/detach lifetime, partial execute resize `0` and oversized values, wait timeout handling, perf stats count validation, and compat behavior for userspace pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/qaic_accel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/qxl_drm.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/qxl_drm.h

## Purpose
This header defines the userspace ABI for the QXL virtual GPU DRM driver used by SPICE/QEMU-style virtual display stacks. It provides GEM allocation, mapping, command submission, relocation records, update regions, driver parameter queries, client capability bits, and surface allocation.

## Important APIs and types
The ioctl range includes `DRM_IOCTL_QXL_ALLOC`, `MAP`, `EXECBUFFER`, `UPDATE_AREA`, `GETPARAM`, `CLIENTCAP`, and `ALLOC_SURF`. `drm_qxl_alloc` creates CPU, VRAM, or surface-domain GEM objects. `drm_qxl_map` returns an mmap offset for a handle. `drm_qxl_reloc` describes command-buffer relocation from a source BO or surface into a destination BO or inline command buffer. `drm_qxl_command` packages a command pointer, relocation pointer, command type, size, and relocation count; `drm_qxl_execbuffer` submits an array of those commands. `drm_qxl_update_area` invalidates a rectangular region of a surface/BO. `drm_qxl_getparam` exposes `QXL_PARAM_NUM_SURFACES` and `QXL_PARAM_MAX_RELOCS`, and `drm_qxl_clientcap` toggles one-bit client capabilities.

## Control flow and state
Userspace allocates BOs or surfaces, obtains mmap offsets, builds command buffers in userspace memory, describes every address dependency via relocation records, and submits the command array through `EXECBUFFER`. When display contents change, `UPDATE_AREA` tells the device/host which rectangle changed. Capability and parameter ioctls are used during initialization to size relocation arrays and advertise feature support.

## State and persistence behavior
Handles are GEM resources scoped to the DRM file and command relocation references. Surface handles created by `ALLOC_SURF` encode format, dimensions, and stride and remain referenced until closed by generic GEM/DRM mechanisms. Client capability bits are persistent per client/device context depending on kernel implementation. No explicit fence object is defined here; synchronization is implicit in the virtual device command flow.

## Dependencies and integration points
The header includes `drm.h` and uses DRM command-base ioctls, GEM handles, `mmap()`, virtual-device command formats, QXL surface IDs, and SPICE display update semantics. Userspace must maintain 32/64-bit compatibility by using `__u64` for pointers as required by the comments.

## Risks and test signals
Main risks are relocation validation errors, command size/count mismatches, incompatible pointer handling on 32-bit userspace, stale handles in relocation records, and invalid update rectangles. Tests should cover max relocation limits from `GETPARAM`, relocations into command-buffer destination `0`, BO versus surface relocation types, invalid surface dimensions/stride, capability toggles, and update rectangles outside allocated surfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/qxl_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/radeon_drm.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/radeon_drm.h

## Purpose
This file is the long-lived public ABI for the legacy Radeon DRM driver. It preserves pre-KMS SAREA/CP command submission interfaces, old memory-manager and IRQ ioctls, and newer KMS GEM/CS/VM ioctls. Much of the file exists for backward compatibility with old X server and Mesa userspace, so numeric constants and structure layouts are effectively immutable.

## Important APIs and types
The legacy side defines upload/state flags, command-buffer packet IDs, R100/R200/R300 command headers, clear/primitive flags, texture heap constants, context register snapshots, texture register snapshots, primitive records, and `drm_radeon_sarea_t` shared-area state. Legacy ioctls include CP init/start/stop/reset/idle, fullscreen, swap, clear, vertex/indices/vertex2, command buffer, texture upload, indirect buffer, get/set param, memory alloc/free/init heap, IRQ emit/wait, surface alloc/free, and tiling toggles.

The KMS/GEM side defines domains (`CPU`, `GTT`, `VRAM`), `drm_radeon_gem_info`, GEM create/userptr/mmap/pread/pwrite/set-domain/wait-idle/busy/set/get-tiling/op, VM mapping via `drm_radeon_gem_va`, command submission chunks via `drm_radeon_cs_chunk`, relocations via `drm_radeon_cs_reloc`, and `drm_radeon_info` query IDs for device identity, tiling, clocks, rings, firmware, memory usage, temperature, reset counters, and virtual-address support.

## Control flow and state
Legacy userspace initializes the command processor, communicates state through SAREA structures and command buffers, performs clears/draws/swaps, manages old GART/FB memory regions, and waits on IRQ sequence numbers. KMS userspace queries memory sizes, creates GEM BOs in an initial domain, optionally configures tiling and userptr backing, maps/preads/pwrites or sets access domains, maps BOs into a VM address with readable/writeable/system/snooped flags, and submits command streams as chunk arrays containing IBs, relocations, flags, and ring/priority selection.

## State and persistence behavior
Legacy SAREA fields persist in shared memory and include cliprects, throttle counters, texture LRU data, CRTC/page state, and tiling state. GEM handles persist until closed. Tiling flags, initial domain, userptr registration, and VM mappings are persistent BO attributes or VM entries. CS submission updates returned `gart_limit` and `vram_limit` budget fields, making memory-pressure state visible to userspace. Info queries expose dynamic telemetry such as usage, clocks, temperature, and reset counter.

## Dependencies and integration points
The file depends on `drm.h` for clip rectangles, texture regions, ioctl encoding, and pointer annotations. It integrates with old DRI/X server SAREA contracts, Mesa command stream generation, KMS GEM memory management, VM address-space management, UVD/VCE/compute rings, and GPU tiling mode arrays. Several comments explicitly warn that definitions are mirrored in X server headers and cannot be changed.

## Risks and test signals
Risks are high because this header combines historical ABI and modern GEM ABI. Changing packet IDs, SAREA layout, ioctl numbers, tiling bits, or info IDs can break old userspace. Security-sensitive areas include userptr memory, command stream parsing, relocations, register read queries, VM map/unmap, and legacy userspace pointers. Test signals should include old ioctl compat coverage, 32-bit pointer compat for legacy pointer fields, GEM domain transitions, tiling set/get, userptr fallback behavior, CS chunk validation, invalid ring IDs, VM duplicate/unmap results, info-query bounds, and reset-counter observation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/radeon_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/rocket_accel.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/rocket_accel.h

## Purpose
This header defines an MIT-licensed DRM accelerator UAPI for Rocket NPU devices. The ABI is intentionally small: create NPU-addressable BOs, prepare/finalize BO CPU ownership, and submit jobs made of sequential NPU tasks with explicit input/output BO handle arrays.

## Important APIs and types
The ioctl set is `DRM_IOCTL_ROCKET_CREATE_BO`, `SUBMIT`, `PREP_BO`, and `FINI_BO`. `drm_rocket_create_bo` returns a GEM handle, an NPU DMA address valid for the DRM file and GEM lifetime, and an mmap offset. `drm_rocket_prep_bo` waits for outstanding NPU usage and synchronizes caches before CPU access, bounded by `timeout_ns`. `drm_rocket_fini_bo` synchronizes caches for NPU access after CPU writes. `drm_rocket_task` points at a register-command buffer by NPU DMA address and command count. `drm_rocket_job` carries task arrays plus input and output BO handle arrays. `drm_rocket_submit` submits an array of jobs and includes struct-size fields for extensibility.

## Control flow and state
Userspace creates BOs, mmaps them through the returned offset if needed, uses prep/fini to transfer ownership between NPU and CPU, builds register-command buffers in BOs, groups tasks into jobs, lists BO dependencies by read/write direction, and submits all jobs. The kernel scheduler is expected to order jobs by dependencies, while tasks inside a job execute sequentially on the same core.

## State and persistence behavior
The returned DMA address is private to the DRM fd and valid only for the lifetime of the GEM handle. BO ownership and cache state transition through prep/fini calls rather than implicit coherency. Job and task arrays are transient submission records, while GEM handles and DMA mappings are persistent resources. Reserved fields must be zero.

## Dependencies and integration points
The header depends on `drm.h`, DRM GEM, DRM mmap offsets, kernel accelerator scheduling, NPU DMA address space, and cache-maintenance semantics. The `*_struct_size` fields indicate intended forward compatibility for task/job records.

## Risks and test signals
Risks include stale DMA addresses after handle close, missing cache synchronization, invalid timeout handling, dependency under-declaration in input/output BO arrays, and struct-size mismatches. Tests should cover BO create/mmap, prep timeout and busy paths, fini cache transitions, single and multi-task jobs, dependency ordering between jobs, invalid reserved fields, zero counts, and forward-compatible struct-size validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/rocket_accel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/tegra_drm.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/tegra_drm.h

## Purpose
This header defines both the legacy staging Tegra DRM UAPI and the newer Host1x channel/syncpoint UAPI. It covers GEM creation/mapping/tiling/flags, syncpoint read/increment/wait, legacy channel submission with relocations and wait checks, newer channel open/map/submit/unmap flows, syncobj integration, and explicit syncpoint allocation/free/wait.

## Important APIs and types
Legacy GEM structs include `drm_tegra_gem_create`, `gem_mmap`, set/get tiling, and set/get flags. Legacy syncpoint structs include `syncpt_read`, `syncpt_incr`, and `syncpt_wait`, with `DRM_TEGRA_NO_TIMEOUT`. Legacy channel submission uses `open_channel`, `close_channel`, `get_syncpt`, `get_syncpt_base`, `drm_tegra_cmdbuf`, `drm_tegra_reloc`, `drm_tegra_waitchk`, and `drm_tegra_submit`.

The newer ABI starts at command IDs `0x10` and `0x20`. `drm_tegra_channel_open` selects a Host1x class and returns a context, engine version, and capabilities such as cache coherence. `drm_tegra_channel_map` maps GEM handles to channel-local mapping IDs with read/write flags. `drm_tegra_submit_buf` defines relocation patching against mappings. `drm_tegra_submit_cmd` represents gather-uptr and syncpoint wait commands. `drm_tegra_channel_submit` passes buffer, command, gather-data arrays, optional syncobj in/out handles, and a syncpoint increment descriptor. `drm_tegra_syncpoint_allocate/free/wait` manage explicit syncpoints.

## Control flow and state
Legacy userspace creates GEM buffers, opens a channel for a client ID, obtains syncpoint IDs and wait bases, builds command buffers, relocations, wait checks, and syncpoint increment arrays, then submits and receives a fence threshold. New userspace opens a Host1x channel, maps BOs to that channel, builds gather data and relocation descriptors, submits command arrays with optional DRM syncobj dependencies, receives the final syncpoint value, and later unmaps/closes resources. Syncpoint waits compare an ID against a threshold with either millisecond legacy timeout or absolute nanosecond timeout in the new ABI.

## State and persistence behavior
GEM handles persist per DRM file; tiling and bottom-up flags are persistent BO metadata. Legacy channel contexts are opaque `__u64`, while new channel contexts are `__u32`; both remain valid until close. Channel mappings persist until unmapped and are the stable IDs used for relocations. Syncpoints are persistent counters, and allocated syncpoints must be freed. Submission fence values are thresholds, not opaque fence handles.

## Dependencies and integration points
The header depends on `drm.h`, Host1x engine classes, Tegra syncpoints, DRM GEM, DRM syncobjs, and memory-layout modifiers such as tiled/block/bottom-up surfaces. It integrates with host command streams and gather opcodes, where userspace provides Host1x command words but the kernel patches relocations and enforces synchronization.

## Risks and test signals
Risks include incorrect legacy/new context mixing, wrong array counts, command-buffer relocation beyond bounds, nonzero reserved fields, unsafely mapped write-only/read-only buffers, syncpoint leaks, and timeout semantic confusion. Test signals should cover both legacy and new ioctl families, tiling/flag round trips, syncpoint wait timeout/no-timeout behavior, channel map/unmap lifetime, gather-uptr command parsing, relative and absolute syncpoint waits, syncobj in/out replacement, cache-coherent capability reporting, and invalid relocation shift/offset handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/tegra_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/v3d_drm.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/v3d_drm.h

## Purpose
This header defines the Broadcom V3D DRM UAPI for newer V3D GPUs. It covers BO creation/mapping/address lookup, CL/TFU/CSD/CPU queue submissions, syncobj and timeline-sync extensions, device parameter queries, performance monitor creation/querying, and reset/timestamp/performance query helper jobs.

## Important APIs and types
Ioctls include `SUBMIT_CL`, `WAIT_BO`, `CREATE_BO`, `MMAP_BO`, `GET_PARAM`, `GET_BO_OFFSET`, `SUBMIT_TFU`, `SUBMIT_CSD`, perfmon create/destroy/get-values/get-counter/set-global, and `SUBMIT_CPU`. `drm_v3d_extension` is a linked-list extension base with IDs for multi-sync, indirect CSD, timestamp query reset/copy, and performance query reset/copy. `drm_v3d_sem` describes binary or timeline syncobj wait/signal entries. `drm_v3d_submit_cl` submits binner and render command lists, BO handles, QMA/QMS/QTS tile allocation data, syncobjs, flags, perfmon ID, and extensions. `drm_v3d_submit_tfu` and `drm_v3d_submit_csd` define texture-formatting and compute dispatch submissions. CPU jobs use extension-specific records and BO-handle expectations.

## Control flow and state
Userspace creates BOs, obtains mmap offsets and V3D virtual offsets, queries capabilities, builds CL/TFU/CSD submissions with BO handle lists, and coordinates queue dependencies with in/out syncobjs or multi-sync extensions. CL submission stages binner before render and has per-FD ordering rules, but cross-FD or cross-queue ordering is explicit via syncobjs. Perfmon objects are created with selected counters, attached to jobs or made global, then values are read after explicit synchronization.

## State and persistence behavior
BO offsets are private to the DRM fd and valid for the GEM handle lifetime. Per-FD queue ordering persists across submissions. Perfmon IDs persist until destroyed, and a global perfmon affects all jobs while active. Syncobj operations can be binary or timeline-based. CPU query jobs write timestamp/performance results and availability state into BOs and syncobjs.

## Dependencies and integration points
The header depends on `drm.h`, DRM GEM, DRM syncobjs/timeline syncobjs, Broadcom V3D queues, CL command streams, TFU and CSD hardware packets, and Mesa query/performance infrastructure. Device capability queries gate optional submission paths such as TFU, CSD, cache flush, perfmon, multi-sync, CPU queue, and super pages.

## Risks and test signals
Risks include extension-chain validation bugs, stale BO offsets, missing cross-queue synchronization, incorrect cache-flush flag handling, perfmon/global perfmon conflicts, timeline point mishandling, and CPU-job extension/BO-count mismatches. Tests should cover each queue, wait-bo timeout, get-param capability gates, multi-sync with multiple waits/signals, indirect CSD uniform rewrite offsets, timestamp/performance query reset/copy, perf counter metadata bounds, global perfmon exclusion, and reserved MBZ field rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/v3d_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/vc4_drm.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/vc4_drm.h

## Purpose
This header defines the Broadcom VC4 DRM UAPI for VideoCore IV GPUs. It exposes command-list submission, sequence/BO waits, BO creation/mapping, immutable shader BO creation, hang-state capture, parameter queries, tiling metadata, BO debug labels, madvise/purge hints, and performance monitors.

## Important APIs and types
`drm_vc4_submit_cl` is the central submission record. It passes userspace pointers to bin CL, shader records, uniforms, BO-handle arrays, render dimensions, tile bounds, RCL surfaces, clear values, flags, returned seqno, perfmon ID, and syncobj in/out handles. The comments explain an important design choice: because VC4 lacks an MMU, userspace submits command/state in plain memory for kernel copy and validation rather than in GPU BOs. `drm_vc4_create_shader_bo` creates non-mmappable shader BOs to prevent shader modification during execution. Waits are available by seqno or by BO. `drm_vc4_get_hang_state` returns register and BO state after GPU hangs. Perfmon records select up to 16 events and return counter arrays.

## Control flow and state
Userspace creates BOs and shader BOs, prepares bin CL/shader/uniform streams with BO handle indices, submits through `SUBMIT_CL`, receives a seqno, and waits by seqno or by BO. Syncobj input delays render start and syncobj output receives a completion fence. Tiling get/set and madvise calls adjust BO metadata and purge behavior. Perfmon objects are created, attached to jobs by ID, synchronized externally, then read.

## State and persistence behavior
GEM BOs persist by handle; shader BOs are immutable and not mappable. Submit seqnos are returned as persistent wait tokens. BO tiling modifiers, labels, and madvise retained state are persistent metadata. Hang-state ioctls expose a snapshot of fault-time hardware registers and BO physical addresses. Perfmon IDs persist until destroyed and require explicit synchronization before reading values.

## Dependencies and integration points
The header depends on `drm.h`, DRM GEM, syncobjs, VC4 CL validation, QPU shader validation, render command list surface layout, and Mesa VC4 userspace. It also integrates with DRM format modifiers for tiling and memory pressure handling through GEM madvise.

## Risks and test signals
Risks include command validation mistakes without an MMU, mutable shader security bugs, incorrect BO-handle indexing in uniforms/shader records, invalid tile bounds or RCL surfaces, missing syncobj waits, and perfmon reads without synchronization. Tests should cover malformed CL/shader records, immutable shader mapping denial, seqno and BO waits, hang-state BO count negotiation, get-param feature gates, tiling round trips, label length validation, madvise purge/retained states, and perfmon event count bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/vc4_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/vgem_drm.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/vgem_drm.h

## Purpose
This small header defines the vgem DRM UAPI for attaching and signaling fences on virtual GEM BOs. It is primarily a testing and synchronization helper ABI rather than a rendering command interface.

## Important APIs and types
The ABI has two ioctls: `DRM_IOCTL_VGEM_FENCE_ATTACH` and `DRM_IOCTL_VGEM_FENCE_SIGNAL`. `drm_vgem_fence_attach` takes a GEM `handle`, `flags`, and returns an `out_fence` file descriptor or handle depending on kernel semantics; `VGEM_FENCE_WRITE` marks the fence as a write dependency. `drm_vgem_fence_signal` takes a fence and flags and signals it.

## Control flow and state
Userspace creates or imports a vgem BO through generic GEM paths, attaches a fence with read or write semantics, passes that fence to other DRM or dma-buf users, and later signals it. There are no command queues, BO mappings, or device-specific memory layouts in this file.

## State and persistence behavior
The fence object persists until signaled and released by the fd/handle lifecycle. The attachment records synchronization state against a BO handle. Flags must remain compatible because this simple ABI is often used by tests that assert exact synchronization behavior.

## Dependencies and integration points
The header depends on `drm.h` and integrates with GEM BO handles, DMA fence semantics, dma-buf style synchronization tests, and cross-driver explicit fencing.

## Risks and test signals
Risks are concentrated in fence lifetime and signaling: double signal, stale BO handle, incorrect write/read dependency semantics, and invalid flags. Tests should attach read and write fences, signal them, verify poll/wait behavior, validate error paths for invalid handles and fences, and ensure unknown flags are rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/vgem_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/virtgpu_drm.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/virtgpu_drm.h

## Purpose
This header defines the virtio-gpu DRM UAPI used by virtual GPU stacks such as virgl, venus, gfxstream, and cross-domain resource sharing. It covers resource creation, host transfers, command submission, fence fd and syncobj synchronization, capset queries, blob resources, host-visible memory, context initialization, and fence-signaled events.

## Important APIs and types
Core ioctls include `MAP`, `EXECBUFFER`, `GETPARAM`, `RESOURCE_CREATE`, `RESOURCE_INFO`, `TRANSFER_FROM_HOST`, `TRANSFER_TO_HOST`, `WAIT`, `GET_CAPS`, `RESOURCE_CREATE_BLOB`, and `CONTEXT_INIT`. `drm_virtgpu_execbuffer` carries flags, command pointer/size, BO handle array, fence fd in/out, ring index, and arrays of timeline-capable syncobjs. `drm_virtgpu_resource_create` describes classic 3D resources with target/format/bind/dimensions/levels/samples/stride. Transfer structs identify BO handles and 3D boxes. `drm_virtgpu_get_caps` fetches capsets such as VIRGL, VIRGL2, GFXSTREAM Vulkan, Venus, cross-domain, and DRM. `drm_virtgpu_resource_create_blob` adds guest, host3D, and host3D_guest blob memory with mappable/shareable/cross-device flags and optional creation command payload. `drm_virtgpu_context_init` passes context parameters such as capset ID, ring count, poll rings, and debug name.

## Control flow and state
Userspace queries feature params, initializes a context if supported, creates resources or blobs, maps host-visible resources when allowed, submits encoded host commands through execbuffer, performs explicit transfers to/from host for non-coherent resources, waits on resources, and queries capsets to size userspace protocol structures. Fence fd flags import/export native fences, while syncobj arrays provide more expressive wait/signal dependencies.

## State and persistence behavior
BO handles and resource handles persist as guest kernel objects tied to host resources. Blob IDs and host-visible mappings can represent host or cross-device shared state. Context parameters persist for the DRM context and influence command routing/rings/events. Fence fd and syncobj state persists outside individual ioctls and can be shared with other subsystems.

## Dependencies and integration points
The header depends on `drm.h`, virtio-gpu host protocols, DRM GEM, dma-fence fd synchronization, DRM syncobjs/timeline syncobjs, virglrenderer/Venus/gfxstream capsets, and host memory/resource transfer mechanisms. Userspace must respect advertised params before using blob, host-visible, cross-device, or context-init paths.

## Risks and test signals
Risks include host command buffer validation, capset size/version mismatches, resource transfer bounds, blob flag combinations, cross-device sharing security, ring index validation, fence fd leaks, and syncobj stride/count mistakes. Tests should cover every `GETPARAM` gate, classic and blob resource creation, map/resource-info behavior, transfer box bounds, execbuffer with fence fd in/out and ring index, timeline syncobjs, context debug-name params, capset query sizes, and event delivery for poll rings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/virtgpu_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/vmwgfx_drm.h -->
# sources/distributed-fs/ceph-client/include/uapi/drm/vmwgfx_drm.h

## Purpose
This header defines the VMware SVGA/vmwgfx DRM UAPI. It is a broad virtual GPU ABI for querying device capabilities, allocating host-visible BOs, creating contexts/surfaces/shaders, submitting SVGA command buffers, managing fences/events, presenting surfaces, synchronizing CPU access, updating display layout, sending guest messages, and exporting MKS statistics.

## Important APIs and types
The ioctl command IDs span `GET_PARAM`, BO allocation/handle close, cursor bypass, overlay streams, context create/unref, legacy and guest-backed surface create/ref/unref, `EXECBUF`, 3D caps, fence wait/signaled/unref/event, present/readback, layout update, shader create/unref, CPU sync, extended context create, extended GB surface create/ref, message, and MKSSTAT reset/add/remove. `drm_vmw_getparam_arg` exposes stream counts, 3D support, FIFO and hardware caps, max memory/object sizes, screen targets, DX/SM/GL support, and device ID. Surface structs distinguish legacy surfaces with face/mip arrays from guest-backed surfaces with backup buffers, scanout/coherent flags, array sizes, and extended 64-bit SVGA flags. `drm_vmw_execbuf_arg` submits userspace SVGA commands, supports throttle, context handle, fence import/export fds, and returns `drm_vmw_fence_rep`.

## Control flow and state
Userspace queries capabilities, allocates BOs, creates contexts and surfaces, builds SVGA command buffers that reference host-visible handles, submits through `EXECBUF`, and receives fence data for wait/poll/event synchronization. Display paths present surfaces to framebuffers or read back clips. CPU access to BOs is explicitly bracketed by `SYNCCPU` grab/release. Advanced paths create DX contexts, shaders, guest-backed surfaces, and MKS stats records. Overlay stream ioctls claim/control/unref streams when stream support exists.

## State and persistence behavior
Contexts, surfaces, shaders, streams, BO handles, and MKS stat records are persistent resources until unreferenced/closed/removed. Fence handles and sequence numbers persist as synchronization objects; sequence numbers can wrap, so `passed_seqno` is part of the ABI. CPU sync grabs block or constrain command submissions referencing a BO until release or fd close. Guest-backed surfaces may own or reference backup buffers and expose map handles. Layout updates persist preferred connector modes/positions.

## Dependencies and integration points
The header depends on `drm.h`, SVGA3D host command semantics, VMware FIFO capability pages, DRM events, GEM/BO mmap offsets, dma-fence fd import/export, framebuffer/present paths, and userspace drivers such as Mesa svga. It also integrates with guest/host communication through `DRM_VMW_MSG` and with MKS guest statistics shared pages.

## Risks and test signals
Risks include very wide ABI surface, legacy aliasing of DMABUF and BO ioctls, command-buffer pointer validation, fence error tri-state handling, sequence wraparound, surface ref/create union layout, CPU sync deadlocks, coherent-surface semantics, and page-aligned MKS stats pointers. Tests should cover getparam gates, BO allocation/mmap/handle close, context/surface/shader lifecycle, execbuf fence import/export and error paths, fence wait/signaled/event behavior, present/readback clips, synccpu grab/release flags, extended surface fields/MBZ validation, message send/receive lengths, and MKS stat add/remove/reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/drm/vmwgfx_drm.h -->

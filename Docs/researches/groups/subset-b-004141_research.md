# subset-b-004141 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-comp.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-comp.h

## Purpose
This header defines the MDP3 component model used by MediaTek's image processor driver. It names every public hardware component, classifies components by functional type, and provides command-queue register/event helper macros used by the component operation implementations.

## Important APIs, Types, And Functions
The register macros wrap `cmdq_pkt_write[_mask]`, `cmdq_pkt_wfe`, `cmdq_pkt_clear_event`, `cmdq_pkt_set_event`, and `cmdq_pkt_poll[_mask]`. `enum mtk_mdp_comp_id` is the stable component namespace, while `enum mdp_comp_type` groups components into RDMA, RSZ, WROT, WDMA, path, color, HDR, merge, dummy, and external/direct-link classes. `struct mdp_comp_data` binds match data, clock/register offsets, and blend metadata. `struct mdp_comp` is the runtime component object. `struct mdp_comp_ctx` binds a component to firmware parameters and frame input/output arrays. `struct mdp_comp_ops` defines the per-component command-building callbacks.

## Control Flow
The header does not execute control flow directly. It defines the callback phases used by command construction: flag derivation, component init, frame config, subframe config, event wait, subframe advance, and post-processing. Runtime code builds `mdp_comp_ctx` objects from firmware component parameters, then dispatches these callbacks while emitting CMDQ packets.

## State, Persistence, And Dependencies
State is runtime-only: MMIO bases, GCE events, clocks, component IDs, and operation tables are kept in `struct mdp_comp`. It depends on `mtk-mdp3-cmdq.h`, V4L2 geometry types through users, and firmware image parameter structs.

## Integration Points
`mtk-mdp3-core.c` allocates and destroys components through `mdp_comp_config()` and `mdp_comp_destroy()`. `mtk-mdp3-m2m.c` and the CMDQ path consume component contexts after VPU path planning. Platform data in `mtk-mdp3-cfg.h` supplies `mdp_comp_data`.

## Risks
The component ID order is a firmware/platform contract; reordering breaks table indexes. The mask macros assume a matching `ofst##_MASK` symbol. Clock count and DTS register offsets must match device tree data.

## Test Signals
Useful signals are successful probe with all components configured, correct CMDQ packets for each pipeline component, no missing clocks/events in device tree, and image transforms completing without GCE timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-comp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-core.c

## Purpose
This is the MDP3 platform driver. It binds supported MediaTek MDP3 device tree compatibles, discovers shared MMSYS/mutex/SCP infrastructure, configures components, initializes workqueues/CMDQ/V4L2 mem2mem state, and handles suspend cleanup.

## Important APIs, Types, And Functions
`mdp_probe()` is the main setup path. `__get_pdev_by_id()` finds infrastructure platform devices by platform data compatibles. `mdp_mm_subsys_deploy()` stores MMSYS and mutex devices for each multimedia subsystem. `mdp_vpu_get_locked()` boots the remote processor, registers IPI handlers, and initializes VPU shared buffers on first use; `mdp_vpu_put_locked()` deinitializes on last release. `mdp_video_device_release()` performs deferred global teardown when the video device is released. `mdp_suspend()` waits for outstanding CMDQ jobs before system suspend.

## Control Flow
Probe allocates `struct mdp_dev`, checks whether the node is the controlling MDP instance, deploys infra devices, obtains mutexes from platform pipe info, configures components, creates job and clock workqueues, obtains SCP/rproc handles, creates CMDQ clients, registers V4L2 and the mem2mem video device, then returns. Error labels unwind in reverse order. Remove unregisters V4L2; final resource destruction is delegated to the video-device release callback.

## State, Persistence, And Dependencies
Persistent driver state lives in `struct mdp_dev`: platform data, component array, mutex handles, workqueues, VPU reference count, CMDQ clients, V4L2 devices, and suspend/job counters. There is no filesystem persistence. Dependencies include OF platform discovery, runtime PM, SCP/remoteproc, CMDQ mailbox, mtk-mutex, V4L2, and videobuf2 DMA-contig.

## Integration Points
The file connects `mtk-mdp3-cfg.h` platform data to `mdp_comp_config()`, `mdp_m2m_device_register()`, VPU helpers in `mtk-mdp3-vpu.c`, and CMDQ execution code.

## Risks
Resource lifetime is split between probe/remove and video-device release, so failure paths and late users must keep ordering correct. `res->start` selects the controlling node; incorrect resource data can silently skip full setup. Suspend can fail if `job_count` never drains. VPU refcount calls are expected to be protected by `vpu_lock`.

## Test Signals
Probe/unprobe on each compatible, runtime V4L2 device creation, suspend during active jobs, SCP/VPU boot errors, CMDQ client creation across `pp_used`, and fault injection along probe unwind are the strongest signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-core.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-core.h

## Purpose
This header centralizes MDP3 driver-wide platform data and runtime device state. It describes supported infrastructure blocks, multimedia subsystems, buffer usage classes, platform quirks, mutex pipe mappings, and the primary `struct mdp_dev`.

## Important APIs, Types, And Functions
`struct mdp_platform_config` records per-SoC feature quirks for RDMA, RSZ, WROT, and TDSHP behavior. `struct mtk_mdp_driver_data` is the full platform-data contract: infra compatibles, component data, format tables, default limits, pipe info, parallel-processing criteria, and component DT IDs. `struct mdp_mm_subsys` stores MMSYS/mutex devices plus `mtk_mutex` handles. `struct mdp_dev` holds all live driver state, including workqueues, VPU/SCP handles, CMDQ clients, V4L2 objects, suspend/job counters, and locks. Exported declarations include VPU reference helpers and `mdp_video_device_release()`.

## Control Flow
No direct control flow is implemented. The declarations define how probe code initializes the device, how M2M contexts access the shared device, and how VPU lifetime is reference-counted.

## State, Persistence, And Dependencies
State is in-memory kernel device state. `vpu_lock` protects working buffer metadata and VPU count operations; `m2m_lock` serializes V4L2 mem2mem device operations; `job_count` and `callback_wq` synchronize suspend with CMDQ completion. Dependencies include V4L2, mem2mem, MediaTek MMSYS/mutex, MDP components, and MDP VPU definitions.

## Integration Points
Used by all MDP3 implementation files: core probe, M2M ioctls, register conversion, VPU IPC, component setup, CMDQ submission, and platform config tables.

## Risks
Many fields are platform-data indexed, so mismatched table lengths or enum values can corrupt pipe/component selection. Locking expectations are implicit in comments and call sites. The `pp_used` value controls CMDQ client array bounds.

## Test Signals
Compile coverage across all supported SoCs, lockdep during concurrent opens/streaming/suspend, and probe coverage with one and two multimedia subsystems exercise this header's contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-m2m.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-m2m.c

## Purpose
This file implements the MDP3 V4L2 mem2mem video node. It exposes image processing operations to userspace, manages per-file contexts, negotiates formats/crop/compose controls, prepares vb2 buffers, invokes VPU path planning, and submits CMDQ work.

## Important APIs, Types, And Functions
`mdp_m2m_device_register()` creates the video device and `v4l2_m2m_dev`. `mdp_m2m_open()` allocates a context, controls, queues, and default formats. `mdp_m2m_device_run()` converts source/destination vb2 buffers into `img_ipi_frameparam`, calls `mdp_vpu_process()`, and sends an `mdp_cmdq_param` via `mdp_cmdq_send()`. `mdp_m2m_start_streaming()` checks scaling and initializes the VPU. Format and selection ioctls call `mdp_try_fmt_mplane()`, `mdp_try_crop()`, and V4L2 helpers. Controls map hflip, vflip, and rotation into the capture frame.

## Control Flow
Open creates an isolated context and default OUTPUT/CAPTURE formats. Userspace sets formats, selection, and controls, queues buffers, and starts both queues. The mem2mem scheduler calls `mdp_m2m_device_run()`, which populates input/output firmware descriptors, optionally switches to dual-bitblt for large work, asks the VPU for a pipeline config, waits for previous job drain, sends CMDQ, and later `mdp_m2m_job_finish()` completes both buffers.

## State, Persistence, And Dependencies
Per-context state includes `curr_param`, frame counters, controls, and queue state. `ctx_lock` serializes vb2 queues; device-level `m2m_lock` serializes open/release and video ioctls. There is no persistence. Dependencies include V4L2 mem2mem, vb2 DMA-contig, MDP regs helpers, VPU IPC, and CMDQ.

## Integration Points
Core probe calls `mdp_m2m_device_register()`. Register helpers convert V4L2 frames to firmware images. VPU returns `config` memory consumed by CMDQ. Job completion is called from the CMDQ callback path.

## Risks
VPU lifecycle depends on start/release state bits; missing `mdp_vpu_put_locked()` would leak firmware state. `device_run()` waits for outstanding `job_count`, serializing jobs and risking timeout. Selection type checks use single-planar type constants in places, so compliance coverage matters. Buffer errors complete both queues as error.

## Test Signals
V4L2 compliance for M2M MPLANE ioctls, format/crop/compose boundary tests, rotation/flip transformations, streamon/streamoff with queued buffers, VPU failure injection, CMDQ timeout handling, and suspend while jobs are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-m2m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-m2m.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-m2m.h

## Purpose
This header defines the MDP3 mem2mem context and its small public interface to the rest of the driver.

## Important APIs, Types, And Functions
`MDP_MAX_CTRLS` sizes the V4L2 control handler. The queue-role enum maps source and destination frame counters. `struct mdp_m2m_ctrls` stores hflip, vflip, and rotate controls. `struct mdp_m2m_ctx` contains a V4L2 file handle, control handler, mem2mem context, frame counters, current MDP frame parameters, and a context mutex. Public functions are `mdp_m2m_device_register()`, `mdp_m2m_device_unregister()`, and `mdp_m2m_job_finish()`.

## Control Flow
The header itself has no execution. It defines the object created by `mdp_m2m_open()` and consumed by queue callbacks, VPU/CMDQ submission, and completion.

## State, Persistence, And Dependencies
State is per-open-file and in memory only. `curr_param` is the key mutable processing state. The header depends on V4L2 controls, MDP core state, VPU types, and register/format definitions.

## Integration Points
Core probe registers the M2M device. CMDQ completion calls `mdp_m2m_job_finish()` to return queued vb2 buffers. Register helpers rely on the context's `mdp_frameparam`.

## Risks
The context state bits are stored in `curr_param.state`, not directly in this header, so callers must use the M2M state helpers in the C file. `MDP_M2M_MAX` must match the frame counter array.

## Test Signals
Open/close leaks, control lifetime, frame counter sequencing, and job completion ordering validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-m2m.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-regs.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-regs.c

## Purpose
This file implements MDP3 format negotiation, crop/compose validation, scaling checks, and conversion from V4L2/vb2 buffers into firmware `img_input` and `img_output` descriptors.

## Important APIs, Types, And Functions
`mdp_enum_fmt_mplane()` enumerates platform formats. `mdp_try_fmt_mplane()` validates and aligns pixel formats, dimensions, plane counts, bytesperline, and sizeimage. `mdp_map_ycbcr_prof_mplane()` converts V4L2 color metadata to MDP profiles. `mdp_try_crop()` clamps selection rectangles with alignment and flags. `mdp_check_scaling_ratio()` enforces platform up/downscale limits. `mdp_check_pp_enable()` chooses dual-pipe processing based on configured criteria. `mdp_set_src_config()` and `mdp_set_dst_config()` fill firmware buffer, crop, and orientation structures. `mdp_frameparam_init()` initializes default M2M frame parameters.

## Control Flow
Userspace ioctls reach this file through `mtk-mdp3-m2m.c`. Format setup finds a platform format, bounds dimensions, adjusts plane data, and stores the result in the context. Selection setup clamps rectangles. When a job runs, source/destination vb2 buffers are converted to DMA addresses, hardware strides, plane sizes, fixed-point crop data, and orientation flags before VPU planning.

## State, Persistence, And Dependencies
There is no global persistence. It mutates caller-owned `v4l2_format`, `mdp_frameparam`, `img_input`, and `img_output` data. Dependencies include platform format/limit tables, V4L2 common helpers, vb2 DMA-contig, and packed firmware ABI structs.

## Integration Points
The M2M ioctl layer calls the validation functions; VPU IPC consumes the generated `img_ipi_frameparam`; CMDQ configuration relies on the same buffer format fields.

## Risks
Integer division in scaling checks can miss near-limit ratios due to truncation and can divide by zero if invalid rectangles escape earlier checks. `mdp_clamp_align()` contains a no-op-looking `min = 0 ? 0 : ...` expression that deserves scrutiny. Plane size/stride math must match firmware and hardware layout, especially contiguous multi-plane and block/tiled formats.

## Test Signals
V4L2 compliance, fuzzing format/selection inputs, stride/size validation against real hardware, zero/one-pixel crop boundaries, 90/270 rotation scale checks, and dual-pipe threshold tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-regs.h

## Purpose
This header defines MDP3 color encoding, pixel-format metadata, scaling limits, stream types, frame state, and the public helpers used by the M2M pipeline.

## Important APIs, Types, And Functions
`MDP_COLOR()` packs color attributes, while `MDP_COLOR_*` macros decode compression, 10-bit packing, block mode, plane count, subsampling, bits-per-pixel, group, swap, and hardware format ID. `enum mdp_color` covers raw Bayer, RGB, packed YUV, planar YUV, NV formats, block/tile/UFO formats, and 10-bit variants. Inline helpers compute minimum strides and plane sizes. `struct mdp_format`, `struct mdp_limit`, `struct mdp_frame`, and `struct mdp_frameparam` model V4L2-visible and hardware-visible state. Public functions cover enumeration, try-format, color profile mapping, crop validation, scaling checks, PP enable, source/destination config, and frameparam initialization.

## Control Flow
The header provides declarations and inline calculations used during format negotiation and job setup. The main flow is V4L2 format/selection input to validated `mdp_frameparam`, then to firmware image descriptors.

## State, Persistence, And Dependencies
State is stored in caller-owned `mdp_frameparam` and `mdp_frame` structures. Dependencies include Linux V4L2 types, vb2 core, and the image IPI ABI.

## Integration Points
Used by `mtk-mdp3-m2m.c`, `mtk-mdp3-regs.c`, VPU processing, and platform config format tables.

## Risks
The packed color bit layout is a driver/firmware/hardware ABI. Mistakes in bit fields can produce wrong stride or unsupported hardware formats. `MDP_VPU_INIT` and `MDP_M2M_CTX_ERROR` live in an atomic state field and must remain unique.

## Test Signals
Compile-time coverage of platform format tables, per-format bytesperline/sizeimage tests, 10-bit/block format validation, and V4L2 try/s_fmt compliance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-type.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-type.h

## Purpose
This small header defines packed image geometry and MMSYS control structures shared by MDP3 firmware command descriptions.

## Important APIs, Types, And Functions
Constants define maximum hardware inputs, outputs, planes, and pipeline components. `struct img_crop` stores integer and subpixel crop dimensions. `struct img_region` stores rectangle edges. `struct img_offset` stores integer/subpixel offsets. `struct img_mux` stores a register/value/subsystem tuple. `struct img_mmsys_ctrl` carries up to twice the maximum component count of mux writes plus a count field.

## Control Flow
There is no direct execution. These packed data structures are filled by register/command preparation and consumed by firmware or command-building code.

## State, Persistence, And Dependencies
The structures are ABI data with `__packed` layout and no persistence. They depend only on Linux integer types.

## Integration Points
`mtk-mdp3-regs.c` writes `img_crop` fields for VPU frame parameters. MMSYS control data is part of the MDP3 image pipeline configuration generated by firmware and consumed by CMDQ/component code.

## Risks
Because the structs are packed firmware-facing ABI, field order, signedness, and width changes are high risk. Maximum constants bound fixed arrays in multiple structures and must match firmware expectations.

## Test Signals
ABI size/layout checks, firmware compatibility tests, and command execution across pipelines with multiple components and outputs validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-vpu.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-vpu.c

## Purpose
This file implements MDP3 communication with the MediaTek SCP/VPU firmware. It registers IPI handlers, allocates shared DMA working buffers, sends init/deinit/frame messages, and waits for firmware acknowledgements.

## Important APIs, Types, And Functions
`mdp_vpu_register()` and `mdp_vpu_unregister()` bind SCP IPI handlers for init, deinit, and frame messages. `mdp_vpu_dev_init()` performs a two-stage init: first asks firmware for work size, then allocates aligned parameter/work/config buffers and sends the work address back. `mdp_vpu_dev_deinit()` sends deinit. `mdp_vpu_process()` copies an `img_ipi_frameparam` into shared memory and sends a frame request. `mdp_vpu_shared_mem_free()` releases the DMA buffers. Internal ack handlers update `vpu->status` and complete `ipi_acked`.

## Control Flow
The core driver boots the remote processor and calls init on first stream use. For each job, M2M code fills a frame parameter and calls `mdp_vpu_process()`. The function locks shared memory, allocates if needed, clears buffers, writes virtual/physical self/config pointers into the parameter, copies it to shared memory, unlocks, sends an SCP IPI, and waits up to 500 ms for completion.

## State, Persistence, And Dependencies
State lives in `struct mdp_vpu_dev`: SCP handle, shared DMA virtual/physical addresses, sizes, completion, lock, and firmware status. No persistent storage is used. Dependencies include SCP IPI APIs, remoteproc, DMA write-combine allocation, and image IPI structs.

## Integration Points
`mtk-mdp3-core.c` manages VPU lifetime and IPI registration. `mtk-mdp3-m2m.c` calls `mdp_vpu_process()` before CMDQ submission and consumes `vpu.config`.

## Risks
The completion object is reused for multiple messages, so serialization through `vpu->lock` and higher-level VPU references is important. Shared-memory allocation failure unwinds partially allocated buffers. DMA addresses are stored in 32-bit message fields, relying on device addressing constraints. Timeout or nonzero firmware status maps to generic errors.

## Test Signals
SCP boot/init/deinit cycles, firmware timeout injection, shared-memory allocation failure, repeated stream open/close, and valid CMDQ config returned for real image transforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-vpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-vpu.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-vpu.h

## Purpose
This header defines the MDP3 firmware IPC message ABI and the runtime state object used by the VPU/SCP communication layer.

## Important APIs, Types, And Functions
`enum mdp_ipi_result` maps firmware result codes to kernel-visible statuses. `struct mdp_ipi_init_msg` carries status, driver data, work buffer address, and size. `struct mdp_ipi_deinit_msg` carries status, driver data, and work address. `struct mdp_vpu_dev` stores the SCP handle, completion, shared parameter/work/config buffers, DMA addresses, sizes, lock, and last status. Public functions are `mdp_vpu_shared_mem_free()`, `mdp_vpu_dev_init()`, `mdp_vpu_dev_deinit()`, and `mdp_vpu_process()`.

## Control Flow
The header defines the message payloads used by the C file's init, deinit, and frame-processing sequences. `drv_data` carries a kernel pointer through firmware acknowledgements so handlers can find the `mdp_vpu_dev`.

## State, Persistence, And Dependencies
All state is runtime memory and DMA memory. The header depends on platform device support and the MDP image IPI ABI.

## Integration Points
Included by MDP3 core and M2M code. Firmware-facing structs must match SCP firmware. The VPU device is embedded in `struct mdp_dev`.

## Risks
`drv_data` is a pointer encoded as `u64`, so firmware must preserve it exactly. `work_addr` fields are 32-bit despite `dma_addr_t` storage. Packed struct layout is ABI-sensitive.

## Test Signals
IPI ack routing to the correct device, successful firmware init on each platform, DMA address range validation, and repeated stream lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-vpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/Kconfig

## Purpose
This Kconfig file defines the MediaTek video codec driver option and internal booleans for SCP and VPU firmware backends.

## Important APIs, Types, And Functions
`VIDEO_MEDIATEK_VCODEC` is a tristate option for the combined MediaTek encoder/decoder driver. It depends on V4L2 mem2mem, IOMMU or compile-test support, video devices, MediaTek architecture or compile-test, either legacy VPU or SCP firmware, and MTK SMI. It selects videobuf2 DMA-contig, V4L2 mem2mem, backend booleans, H.264/VP9 helpers, and media controller support.

## Control Flow
Kconfig selection controls which Makefile objects are compiled and which firmware backend initializers are available. The dependency lines keep module/built-in linkage aligned with VPU and SCP dependencies.

## State, Persistence, And Dependencies
No runtime state. Build-time dependencies determine whether VPU/SCP backend code and debug/media support are compiled.

## Integration Points
`common/Makefile` uses `VIDEO_MEDIATEK_VCODEC_VPU` and `VIDEO_MEDIATEK_VCODEC_SCP` to include firmware backend implementations. Decoder and encoder Makefiles build modules under `VIDEO_MEDIATEK_VCODEC`.

## Risks
Incorrect dependency states can create unresolved symbols when a backend is built as a different linkage type. Compile-test depends on MTK_SMI being disabled unless available.

## Test Signals
Build matrix coverage for built-in/module/compile-test, VPU-only, SCP-only, and both-backend configurations is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/Makefile

## Purpose
This top-level Makefile includes the MediaTek vcodec common, encoder, and decoder subdirectories.

## Important APIs, Types, And Functions
It adds `common/`, `encoder/`, and `decoder/` to `obj-y`, delegating actual module object selection to each subdirectory Makefile and Kconfig symbols.

## Control Flow
During kernel build traversal, this file ensures all vcodec subdirectories are visited so their `obj-$(CONFIG_VIDEO_MEDIATEK_VCODEC)` rules can contribute objects.

## State, Persistence, And Dependencies
There is no runtime state. Build state depends on Kbuild and `CONFIG_VIDEO_MEDIATEK_VCODEC`.

## Integration Points
This file links the vcodec subtree into `drivers/media/platform/mediatek` build traversal. The common library objects are then shared by encoder and decoder modules.

## Risks
Using `obj-y` means subdirectory traversal always happens when the parent directory is visited; incorrect subdirectory Makefiles would still be evaluated. Omitting a subdir would silently remove that driver half from builds.

## Test Signals
Kbuild coverage that produces `mtk-vcodec-common`, `mtk-vcodec-dec`, `mtk-vcodec-dec-hw`, and encoder objects for enabled configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/Makefile

## Purpose
This Makefile builds the shared MediaTek vcodec support module and optional debugfs support.

## Important APIs, Types, And Functions
`mtk-vcodec-common.o` includes interrupt, utility, and firmware-dispatch code. It conditionally adds `mtk_vcodec_fw_vpu.o` when the VPU backend is enabled and `mtk_vcodec_fw_scp.o` when the SCP backend is enabled. With `CONFIG_DEBUG_FS`, it also builds `mtk-vcodec-dbgfs.o` from `mtk_vcodec_dbgfs.o`.

## Control Flow
Kbuild evaluates backend booleans derived from Kconfig and assembles the common object list. Decoder/encoder code then links against exported symbols from these objects.

## State, Persistence, And Dependencies
No runtime state is defined here. Build-time state depends on `CONFIG_VIDEO_MEDIATEK_VCODEC`, backend symbols, and debugfs.

## Integration Points
Provides shared symbols for decoder and encoder firmware IPC, memory allocation, interrupts, register access, current-context tracking, and debugfs controls.

## Risks
Missing backend objects make `mtk_vcodec_fw_select()` return `-ENODEV` through stub initializers. Debugfs object is only built when debugfs is enabled, so header stubs must remain complete.

## Test Signals
Builds with VPU, SCP, both, neither backend stubs under compile-test, and debugfs enabled/disabled validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_cmn_drv.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_cmn_drv.h

## Purpose
This common header defines shared MediaTek vcodec queue, register, clock, power-management, format, and instance state types used by both decoder and encoder code.

## Important APIs, Types, And Functions
`enum mtk_q_type` indexes source and destination queue data. `enum mtk_hw_reg_idx` defines shared decoder and encoder register-base indexes. `struct mtk_vcodec_clk_info`, `struct mtk_vcodec_clk`, and `struct mtk_vcodec_pm` describe clock/PM resources. `enum mtk_vdec_hw_id` distinguishes core/LAT hardware. `enum mtk_instance_state` models codec instance lifecycle from free through init, header, flush, and abort. `struct mtk_video_fmt` and `struct mtk_q_data` store V4L2 format metadata and queue geometry. `enum mtk_instance_type` distinguishes decoder and encoder contexts.

## Control Flow
No direct control flow. These types are consumed by probe, ioctl, queue setup, worker, PM, and firmware paths.

## State, Persistence, And Dependencies
State is in-memory per-device or per-context. Dependencies include platform devices, V4L2 controls/devices/ioctls/mem2mem, and videobuf2 core.

## Integration Points
Included by decoder/encoder driver headers, common util, firmware, interrupt, and debugfs code.

## Risks
Several common helpers infer instance type by reading the first field of decoder/encoder contexts, so `enum mtk_instance_type type` must stay first in those structs. Register indexes are shared across modules and must match mapped arrays.

## Test Signals
Compile coverage for decoder and encoder, runtime memory alloc/free from both instance types, and register-index bounds testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_cmn_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_dbgfs.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_dbgfs.c

## Purpose
This file implements optional debugfs support for MediaTek vcodec decoder and encoder devices. Decoder debugfs can list active instances, picture information, output/capture formats, and runtime debug level controls.

## Important APIs, Types, And Functions
`mtk_vcodec_dbgfs_init()` creates either `vcodec-dec` or `vcodec-enc` debugfs roots. Decoder init creates `mtk_v4l2_dbg_level`, `mtk_vcodec_dbg`, and `vdec`. `mtk_vcodec_dbgfs_create()` and `mtk_vcodec_dbgfs_remove()` maintain the decoder instance list. `mtk_vdec_dbgfs_write()` stores command text; `mtk_vdec_dbgfs_read()` parses `-help`, `-picinfo`, and `-format`, then renders information for each instance. `mtk_vcodec_dbgfs_deinit()` removes the tree.

## Control Flow
Probe calls init. Each decoder open adds an instance and each release removes it. Userspace writes a command string to debugfs and reads back a synthesized report. Deinit removes the whole root.

## State, Persistence, And Dependencies
Debugfs state lives in `struct mtk_vcodec_dbgfs`: list head, root dentry, mutex, command buffer, command size, and instance count. It is runtime-only and disappears on driver unload. Dependencies include debugfs, decoder/encoder private headers, and common debug globals.

## Integration Points
Decoder probe/release and encoder probe paths call the exported functions. Common util exports the debug-level globals that debugfs exposes.

## Risks
Read buffer sizing is a fixed estimate of 200 bytes per instance, so long output can truncate silently. The instance list is protected by `dbgfs_lock` during reads but create/remove list updates are not explicitly locked in this file. The decoder debugfs file is created with write-only mode while a read handler is present, which deserves permissions review.

## Test Signals
Debugfs smoke tests with zero/multiple decoder instances, concurrent open/close while reading, command parsing for help/picinfo/format, and debugfs disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_dbgfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_dbgfs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_dbgfs.h

## Purpose
This header defines vcodec debugfs data structures and exposes debugfs lifecycle helpers, with no-op stubs when debugfs is disabled.

## Important APIs, Types, And Functions
`enum mtk_vdec_dbgfs_log_index` defines decoder report selectors for picture info and format. `struct mtk_vcodec_dbgfs_inst` links a decoder context into the debugfs instance list. `struct mtk_vcodec_dbgfs` stores the list, root dentry, mutex, command buffer, buffer size, and instance count. Public functions are `mtk_vcodec_dbgfs_create()`, `mtk_vcodec_dbgfs_remove()`, `mtk_vcodec_dbgfs_init()`, and `mtk_vcodec_dbgfs_deinit()`, with inline stubs under `!CONFIG_DEBUG_FS`.

## Control Flow
No direct execution. The API lets probe initialize the tree, open/release add or remove decoder instances, and remove tear the tree down.

## State, Persistence, And Dependencies
Debugfs state is runtime-only and stored inside codec device structs. The header forward-declares decoder device/context types to avoid broad include dependency.

## Integration Points
Included by decoder driver state and common debugfs implementation. Encoder state uses the same aggregate debugfs struct.

## Risks
Stub functions must match the real prototypes exactly to keep non-debugfs builds compiling. The command buffer has a fixed 1024-byte size.

## Test Signals
Builds with and without `CONFIG_DEBUG_FS`, decoder open/release list lifecycle, and debugfs deinit during module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_dbgfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_fw.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_fw.c

## Purpose
This file provides the common firmware abstraction dispatcher for MediaTek vcodec. It selects a VPU or SCP backend and forwards operations through a backend ops table.

## Important APIs, Types, And Functions
`mtk_vcodec_fw_select()` chooses `mtk_vcodec_fw_vpu_init()` or `mtk_vcodec_fw_scp_init()` based on `enum mtk_vcodec_fw_type` and whether the caller is an encoder or decoder. The exported wrappers `mtk_vcodec_fw_release()`, `mtk_vcodec_fw_load_firmware()`, capability getters, `mtk_vcodec_fw_map_dm_addr()`, `mtk_vcodec_fw_ipi_register()`, `mtk_vcodec_fw_ipi_send()`, and `mtk_vcodec_fw_get_type()` call the selected backend.

## Control Flow
Probe code selects firmware once, stores the returned `struct mtk_vcodec_fw`, then all later operations are virtual dispatch through `fw->ops`.

## State, Persistence, And Dependencies
State is the backend object allocated by SCP or VPU init. No persistence. Dependencies include decoder/encoder device structs and `mtk_vcodec_fw_priv.h`.

## Integration Points
Decoder probe uses selection, load, capability, and release. Codec interfaces use IPI registration/send and DM address mapping. Encoder code uses the same abstraction.

## Risks
The wrappers assume `fw` and `fw->ops` are valid. Invalid firmware type returns an error pointer after logging through the caller platform device. Backend stubs under disabled Kconfig return `-ENODEV`.

## Test Signals
Probe with VPU and SCP device-tree properties, disabled backend builds, invalid type handling, firmware release on probe errors, and IPI send/register smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_fw.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_fw.h

## Purpose
This public firmware header exposes the vcodec firmware abstraction to decoder and encoder code without revealing backend internals.

## Important APIs, Types, And Functions
`enum mtk_vcodec_fw_type` selects VPU or SCP. `enum mtk_vcodec_fw_use` distinguishes decoder and encoder users. `mtk_vcodec_ipi_handler` defines the common callback signature. The declared API covers firmware selection/release, firmware load, decode/encode capability queries, data-memory mapping, IPI registration, IPI send, and backend type retrieval.

## Control Flow
Caller probe selects a backend, loads firmware on first use, registers IPI handlers, and sends messages through this API. The implementation dispatches to backend ops.

## State, Persistence, And Dependencies
The header forward-declares device structs and the opaque `struct mtk_vcodec_fw`. It depends on remoteproc/SCP and legacy VPU headers for type availability.

## Integration Points
Used by decoder/encoder probe and codec-specific VPU interfaces. `mtk_vcodec_fw_priv.h` extends it for backend implementers.

## Risks
The common IPI handler signature must remain compatible with both SCP and VPU APIs. Exposing backend type allows callers to branch and can leak abstraction details.

## Test Signals
Builds across backend configurations, IPI handler registration for decoder and encoder, and capability queries after firmware load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_fw_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_fw_priv.h

## Purpose
This private firmware header defines the concrete firmware object, backend operations table, and conditional backend initializer declarations.

## Important APIs, Types, And Functions
`struct mtk_vcodec_fw` stores backend type, ops table, VPU platform device, SCP handle, and firmware use. `struct mtk_vcodec_fw_ops` defines backend methods for load, capability queries, DM address mapping, IPI register/send, and release. Conditional declarations expose `mtk_vcodec_fw_vpu_init()` and `mtk_vcodec_fw_scp_init()` only when their Kconfig options are enabled; otherwise inline stubs return `ERR_PTR(-ENODEV)`.

## Control Flow
Common selection code creates one of these backend objects. Later public wrapper calls dispatch to the ops table stored in the object.

## State, Persistence, And Dependencies
Backend state is runtime-only. The header depends on `mtk_vcodec_fw.h` and forward-declares decoder/encoder device structs.

## Integration Points
Included by `mtk_vcodec_fw.c`, backend implementations, and decoder driver state. Kconfig/backend Makefile choices control which initializers are real.

## Risks
Backend objects are allocated with devm but release methods also drop references to VPU/SCP devices; misuse can leave stale firmware handles. Stub behavior must match probe error handling.

## Test Signals
Compile matrix for backend enablement, firmware select error paths, and release behavior for both VPU and SCP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_fw_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_fw_scp.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_fw_scp.c

## Purpose
This file implements the SCP firmware backend for the vcodec firmware abstraction.

## Important APIs, Types, And Functions
Backend ops map common operations to SCP APIs: `rproc_boot(scp_get_rproc())`, `scp_get_vdec_hw_capa()`, `scp_get_venc_hw_capa()`, `scp_mapping_dm_addr()`, `scp_ipi_register()`, `scp_ipi_send()`, and `scp_put()`. `mtk_vcodec_fw_scp_init()` selects the caller platform device from decoder or encoder private data, obtains the SCP handle with `scp_get()`, allocates `struct mtk_vcodec_fw`, and fills type, ops, and SCP fields.

## Control Flow
Probe calls init after discovering an SCP firmware phandle. Init validates caller use, gets SCP, allocates the backend object, and returns it. Later public wrappers call the SCP ops. Release drops the SCP reference.

## State, Persistence, And Dependencies
State is the SCP handle stored in `fw->scp` plus devm-allocated backend metadata. Dependencies include decoder/encoder private structs, SCP remoteproc helpers, and the common firmware private header.

## Integration Points
Decoder and encoder probes use this backend when device tree exposes `mediatek,scp`. Codec-specific interfaces use common IPI wrappers over SCP.

## Risks
`scp_get()` failure returns `-EPROBE_DEFER`, so probe ordering matters. The backend does not set `fw_use`, unlike VPU init, so code must not depend on it for SCP. Release assumes an SCP handle is present.

## Test Signals
SCP probe defer, firmware boot, capability query, IPI register/send, release on probe error, and decoder/encoder users both selecting SCP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_fw_scp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_fw_vpu.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_fw_vpu.c

## Purpose
This file implements the legacy VPU firmware backend for the vcodec firmware abstraction and registers watchdog reset handlers.

## Important APIs, Types, And Functions
Backend ops map to VPU APIs: `vpu_load_firmware()`, capability getters, `vpu_mapping_dm_addr()`, `vpu_ipi_register()`, `vpu_ipi_send()`, and `put_device()`. `mtk_vcodec_fw_vpu_init()` obtains the VPU platform device, registers decoder or encoder watchdog handlers, allocates the backend object, and stores the firmware use. Reset handlers mark every active decoder or encoder context `MTK_STATE_ABORT` under the device context spinlock.

## Control Flow
Probe selects the VPU backend when device tree exposes `mediatek,vpu`. Init finds the VPU device, registers a reset callback for the appropriate reset ID, creates the backend, and returns it. Runtime wrappers dispatch firmware operations. Watchdog callbacks asynchronously abort all contexts after a firmware timeout.

## State, Persistence, And Dependencies
State is the referenced VPU platform device and firmware use stored in `struct mtk_vcodec_fw`. It depends on legacy VPU APIs, decoder/encoder device lists, spinlocks, and common firmware private definitions.

## Integration Points
Used on MT8173-style platforms and other VPU-backed configurations. The reset path integrates with V4L2 instance state by preventing further buffer queue/dequeue after abort.

## Risks
Watchdog handlers iterate all contexts and must hold the right lock. Encoder reset logs with the decoder debug macro name, which is harmless but confusing. `vpu_ipi_send()` ignores the common `wait` argument. Missing VPU device returns `-EINVAL`, not probe defer.

## Test Signals
VPU probe readiness, firmware load, IPI send/register, watchdog timeout forcing `MTK_STATE_ABORT`, and open/close after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_fw_vpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_intr.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_intr.c

## Purpose
This file implements a shared wait helper for vcodec hardware completion interrupts.

## Important APIs, Types, And Functions
`mtk_vcodec_wait_for_done_ctx()` receives a decoder or encoder context pointer, command ID, timeout in milliseconds, and hardware index. It infers instance type from the first context field, selects context ID/type, interrupt condition/type arrays, waitqueue array, and platform device, then waits for `ctx_int_cond[hw_id]` with `wait_event_interruptible_timeout()`.

## Control Flow
Codec-specific worker code enables hardware and starts decode/encode. Interrupt handlers set condition/type and wake the queue. This helper blocks until the condition is true, timeout expires, or a signal interrupts the wait. It logs timeout/interruption and clears condition/type before returning 0 or -1.

## State, Persistence, And Dependencies
It mutates per-context interrupt condition and type arrays. There is no persistence. Dependencies include decoder and encoder context layouts, waitqueues, and common interrupt constants.

## Integration Points
Called by codec-specific decode/encode implementation files after hardware submission. Woken by parent or subdevice interrupt handlers.

## Risks
The type inference depends on decoder/encoder context first field layout. It returns generic -1 rather than standard errno. No bounds check is done on `hw_id`; callers must validate. Clearing condition after every wait can hide late status if incorrectly shared.

## Test Signals
Successful interrupt wake, timeout path, signal interruption, multiple hardware indexes, and lockdep/race testing around interrupt and wait paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_intr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_intr.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_intr.h

## Purpose
This header exposes the shared vcodec interrupt wait helper and the interrupt-received reason bit.

## Important APIs, Types, And Functions
`MTK_INST_IRQ_RECEIVED` marks a normal hardware completion interrupt. `mtk_vcodec_wait_for_done_ctx()` waits on a decoder or encoder context for a command to finish on a selected hardware index. Decoder and encoder context structs are forward-declared.

## Control Flow
No direct execution. Hardware interrupt handlers wake context queues with this reason; codec workers call the declared helper to wait for completion.

## State, Persistence, And Dependencies
No state in the header. It depends on context definitions at implementation call sites and the common wait implementation.

## Integration Points
Included by decoder parent/subdevice drivers, PM/hardware code, and codec-specific interface files.

## Risks
The API uses `void *priv`, so type safety is weak and depends on caller discipline. The `hw_id` parameter must be valid for the context's arrays.

## Test Signals
Compile coverage from decoder and encoder code and runtime interrupt wait coverage for each hardware index.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_intr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_util.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_util.c

## Purpose
This file implements shared utility functions for vcodec register access, DMA buffer allocation, VDEC_SYS writes, hardware subdevice lookup, and current decoder context tracking.

## Important APIs, Types, And Functions
`mtk_vcodec_get_reg_addr()` bounds-checks register-base indexes. `mtk_vcodec_write_vdecsys()` writes through regmap when present or MMIO otherwise. `mtk_vcodec_mem_alloc()` and `mtk_vcodec_mem_free()` allocate/free DMA memory for decoder or encoder contexts. `mtk_vcodec_get_hw_dev()` returns decoder hardware subdevice state. `mtk_vcodec_set_curr_ctx()` and `mtk_vcodec_get_curr_ctx()` update/read the current context either on the main device or per subdevice under `irqlock`. Debug globals are exported under `CONFIG_DEBUG_FS`.

## Control Flow
Workers allocate firmware buffers and set current context before hardware execution. Interrupt handlers use current context lookup to wake the right waitqueue. PM and codec-specific code use VDEC_SYS writes and register access during hardware setup.

## State, Persistence, And Dependencies
It mutates DMA memory descriptors and decoder current-context pointers. No persistence. Dependencies include decoder/encoder private structs, regmap, DMA APIs, subdevice hardware structs, and debugfs globals.

## Integration Points
Common to decoder, encoder, interrupt handlers, firmware codec implementations, and debugfs controls.

## Risks
Like other common helpers, instance type is inferred from the first context field. Allocation uses `dma_alloc_attrs(... DMA_ATTR_ALLOC_SINGLE_PAGES)` but free uses `dma_free_coherent()`, which may be intentional API compatibility or a review point. `mtk_vcodec_get_hw_dev()` logs and returns NULL for invalid/missing subdevices; callers must handle it.

## Test Signals
DMA alloc/free fault injection, register index bounds tests, regmap and MMIO VDEC_SYS paths, multi-hardware current-context lookup, and debugfs variable changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_util.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_util.h

## Purpose
This header defines shared vcodec memory structs, logging/debug macros, and utility function declarations.

## Important APIs, Types, And Functions
`struct mtk_vcodec_mem` holds size, virtual address, and DMA address. `struct mtk_vcodec_fb` holds framebuffer size and DMA address. Logging macros produce V4L2 and vcodec scoped messages, with debug-level gating under `CONFIG_DEBUG_FS`. Declarations expose register-base lookup, VDEC_SYS write, DMA allocation/free, current decoder context setters/getters, and hardware subdevice lookup.

## Control Flow
No direct execution. Macros and function declarations are used throughout worker, firmware, interrupt, and probe code.

## State, Persistence, And Dependencies
Debug state is held in exported globals when debugfs is enabled. Memory descriptors are caller-owned. Dependencies include Linux types and DMA direction plus decoder forward declarations.

## Integration Points
Included by decoder/encoder drivers, firmware backends, debugfs, and codec interface implementations.

## Risks
Macros evaluate arguments in logging contexts and assume valid platform devices. Debug macros change behavior depending on debugfs config. Function APIs use `void *priv` for encoder/decoder polymorphism.

## Test Signals
Builds with debugfs enabled/disabled, logging at different levels, DMA helper users from decoder and encoder, and current-context helper coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/Makefile

## Purpose
This Makefile builds the MediaTek decoder modules and selects codec-specific implementation objects.

## Important APIs, Types, And Functions
`mtk-vcodec-dec.o` includes decoder interface implementations for H.264, VP8, VP9, AV1, HEVC request paths, common request helpers, driver probe, firmware VPU interface, message queue, shared decoder ioctls, stateful/stateless APIs, and decoder PM. `mtk-vcodec-dec-hw.o` contains subdevice hardware support. Both are built under `CONFIG_VIDEO_MEDIATEK_VCODEC`.

## Control Flow
Kbuild aggregates all listed objects into the decoder module and hardware-subdevice module. Runtime platform data decides which stateful/stateless and hardware architecture paths are used.

## State, Persistence, And Dependencies
No runtime state in this file. Build state depends on Kconfig and object list correctness.

## Integration Points
Connects common vcodec objects to codec-specific decoder implementations and parent/subdevice platform drivers.

## Risks
The decoder module includes many codec implementations unconditionally under the main vcodec config, so missing symbols in any one break all decoder builds. Adding a codec requires updating both this object list and capability/format/control tables.

## Test Signals
Full decoder build, module load with parent and subdevice objects, and compile coverage for all codec-specific paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec.c

## Purpose
This file implements the shared V4L2 mem2mem decoder ioctl and vb2 queue logic used by both stateful and stateless MediaTek decoder variants.

## Important APIs, Types, And Functions
`mtk_vcodec_dec_set_default_params()` initializes context queue defaults. `vidioc_vdec_s_fmt()`, `vidioc_vdec_g_fmt()`, try-format, enum-format, enum-framesizes, and selection handlers implement V4L2 format negotiation. `vb2ops_vdec_queue_setup()`, `vb2ops_vdec_buf_prepare()`, `vb2ops_vdec_buf_finish()`, start/stop streaming, and queue initialization implement vb2 lifecycle. `m2mops_vdec_device_run()` queues decode work; `m2mops_vdec_job_ready()` gates scheduling on header state and no pending resolution change. Decoder command helpers dispatch to stateful or stateless semantics.

## Control Flow
Open creates a context in the driver file, then this file initializes defaults and queues. Userspace sets OUTPUT codec format, which initializes the codec instance via `vdec_if_init()` from `MTK_STATE_FREE`. Stateless S_FMT also updates capture dimensions immediately. During streaming, buffers are prepared and queued through pdata-specific vb2 ops. Mem2mem scheduling queues the decode worker supplied by stateful/stateless pdata. Stop streaming flushes, completes queued buffers as errors, and updates resolution state.

## State, Persistence, And Dependencies
It mutates `struct mtk_vcodec_dec_ctx`: queue data, state, colorspace, current codec, capture fourcc, picinfo, last decoded picinfo, and buffer error state. No persistence. Dependencies include V4L2 mem2mem, media requests, vb2 DMA-contig, decoder interface `vdec_if_*`, and platform pdata.

## Integration Points
Driver probe exposes `mtk_vdec_ioctl_ops` and `mtk_vdec_m2m_ops`. Stateful/stateless files provide pdata-specific workers and queue callbacks. Codec implementations provide `vdec_if_*`.

## Risks
State transitions are subtle around `MTK_STATE_INIT`, `HEADER`, `FLUSH`, and `ABORT`. `vidioc_try_fmt_vid_cap_mplane()` and output fallback write `f->fmt.pix.pixelformat` while operating on mplane formats, which merits review. `m2mops_vdec_job_ready()` blocks while resolution change is pending until userspace acknowledges with capture streamoff. Request completion must be paired on error paths.

## Test Signals
V4L2 compliance for stateful and stateless APIs, dynamic resolution change streams, streamoff on both queues with requests, buffer size validation, abort state qbuf/dqbuf behavior, and enum-format filtering for 10-bit capture formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec.h

## Purpose
This decoder public header defines decoder limits, buffer-private structures, exported V4L2 ops, platform pdata symbols, and shared decoder helper prototypes.

## Important APIs, Types, And Functions
Constants define default/min/max dimensions, 4K capability flags, and decode success IRQ bit. `struct vdec_fb` describes a decoded frame buffer with Y and C plane memory and framebuffer status. `struct mtk_video_dec_buf` extends `v4l2_m2m_buffer` with state flags for capture-buffer ownership, queued state, errors, and a union of frame buffer or bitstream buffer. Externs expose ioctl/m2m/media ops and platform data for MT8173, MT8183, LAT single-core, and single-core variants. Helper prototypes cover hardware locking, queue initialization, default params, release, and vb2 callbacks.

## Control Flow
The header does not execute control flow. It defines the shared structures passed among the parent driver, common ioctl layer, stateful/stateless queue callbacks, and codec implementations.

## State, Persistence, And Dependencies
Buffer state is per-vb2 buffer and in memory only. Dependencies include vb2 core, V4L2 mem2mem, and decoder driver state.

## Integration Points
Used throughout decoder files and codec-specific `vdec` implementations. The platform-data externs are selected by OF match in the driver.

## Risks
`mtk_video_dec_buf`'s union means source and capture buffers interpret the same storage differently; queue type must be respected. Ownership flags are central to stateful reference-buffer recycling and are protected by context locks in call sites.

## Test Signals
Buffer lifecycle tests, stateful reference-buffer requeue tests, codec platform matching, and compile coverage of exported ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_drv.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_drv.c

## Purpose
This file is the parent MediaTek V4L2 decoder platform driver. It probes the decoder device, maps resources, selects firmware, creates V4L2/media/mem2mem devices, handles opens/releases, manages context lists, and services single-core interrupts.

## Important APIs, Types, And Functions
`mtk_vcodec_probe()` is the main device setup path. `mtk_vcodec_get_reg_bases()` supports both legacy named register mapping plus syscon VDEC_SYS and newer indexed mapping. `mtk_vcodec_init_dec_resources()` maps registers, installs IRQs for non-subdevice platforms, initializes clocks, and enables runtime PM. `fops_vcodec_open()` allocates per-instance contexts, checks subdevice readiness, creates controls and mem2mem queues, loads firmware on the first open, queries capabilities, initializes pdata-specific parameters, links debugfs, and adds the context to the list. `fops_vcodec_release()` tears the context down. `mtk_vcodec_dec_irq_handler()` wakes the current core context.

## Control Flow
Probe allocates device state, identifies chip and firmware backend from device tree, maps resources, creates optional LAT/core workqueues, initializes locks, registers V4L2 and video devices, creates mem2mem and decode workqueues, populates subdevices when supported, registers media controller for stateless APIs, and initializes debugfs. Open prepares per-instance state and firmware. Remove reverses registration and releases firmware.

## State, Persistence, And Dependencies
Device state includes register bases, firmware handler, context list, current context, locks, workqueues, IRQs, PM state, capability bits, subdevice bitmap, racing-info snapshot, media device, and debugfs. No persistence. Dependencies include OF, syscon/regmap, runtime PM, V4L2/mem2mem/media controller, firmware abstraction, and decoder PM/hardware helpers.

## Integration Points
OF match selects pdata from stateful/stateless files. Hardware subdevices attach through child platform population. Common firmware and util modules provide backend and current-context helpers.

## Risks
Probe error paths are long and architecture-dependent. Firmware loading only on singular first open means capability-dependent format tables initialize lazily. Subdevice readiness must be complete before opening. IRQ handler assumes a valid current context. Media controller cleanup is conditional on registration state.

## Test Signals
Probe/remove on all compatibles, legacy and syscon register layouts, VPU/SCP firmware paths, first and concurrent opens, subdevice population failures, interrupt completion, and stateless media controller registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_drv.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_drv.h

## Purpose
This is the main decoder private header. It defines chip IDs, capability bits, platform-data callbacks, per-request data, per-context state, device state, and decoder logging/wakeup helpers.

## Important APIs, Types, And Functions
Enums cover supported chip names, decoder format/capability flags, hardware count, and hardware architecture. `struct vdec_pic_info` stores visible/aligned dimensions, framebuffer sizes, and capture fourcc. `struct mtk_vcodec_dec_pdata` is the per-platform behavior table, including init, controls, worker, flush, capture-buffer hooks, vb2 ops, formats, defaults, hardware architecture, subdevice support, and stateless flag. `struct mtk_vcodec_dec_ctx` contains all per-instance V4L2, codec, interrupt, request, color, queue, worker, and hardware state. `struct mtk_vcodec_dec_dev` contains parent device state, resources, firmware, locks, workqueues, subdevice pointers, capability, racing state, and debugfs.

## Control Flow
The header defines the state machine and callback model used by the driver. Pdata chosen at probe determines whether stateful or stateless callbacks handle queues and decode workers.

## State, Persistence, And Dependencies
All state is runtime kernel state. Context state tracks `FREE`, `INIT`, `HEADER`, `FLUSH`, and `ABORT`. Interrupt arrays and queues are per hardware index. Dependencies include common vcodec types, debugfs, firmware private API, utilities, and LAT/core message queue types.

## Integration Points
Included by every decoder file, common debugfs/util/firmware modules, and codec-specific implementation files.

## Risks
The first field of `mtk_vcodec_dec_ctx` is used polymorphically by common helpers. Capability bits drive format/control exposure and must match firmware. Subdevice arrays are indexed by `enum mtk_vdec_hw_id`. `wake_up_dec_ctx()` has no internal bounds or NULL checks.

## Test Signals
Compile coverage, platform pdata matching, state-machine tests, multi-hardware interrupt wakeups, request lifecycle validation, and debugfs context-list tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_hw.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_hw.c

## Purpose
This file implements child hardware platform drivers for decoder LAT/core subdevices used by newer MediaTek decoder architectures.

## Important APIs, Types, And Functions
`mtk_vdec_hw_match` maps compatible strings to hardware IDs for LAT0, CORE, and LAT_SOC. `mtk_vdec_hw_probe()` obtains the parent decoder device, initializes clocks/runtime PM, records subdevice state in the parent bitmap, maps the subdevice MISC registers, and optionally installs an IRQ. `mtk_vdec_hw_prob_done()` verifies all present compatible subdevices have probed. `mtk_vdec_hw_irq_handler()` checks active status, validates decode-success IRQ status, clears the interrupt, and wakes the current context for that hardware index.

## Control Flow
The parent decoder probe populates child platform devices. Each child probe attaches itself to the parent. Open checks `subdev_prob_done()` before allowing contexts. During decode, PM code enables the selected child hardware and IRQ; IRQ completion wakes the waiting context.

## State, Persistence, And Dependencies
State lives in `struct mtk_vdec_hw_dev`: platform device, parent pointer, register bases, current context, IRQ, PM, and hardware index. Dependencies include OF platform, PM runtime, decoder PM, common interrupt helpers, and current-context utility functions.

## Integration Points
Parent driver stores subdevice pointers and bitmap. PM uses subdevice PM/IRQ data. Codec workers use hardware indexes that correspond to these subdevices.

## Risks
IRQ handler calls logging macros with `ctx` from current-context lookup; if no current context is set, null handling is fragile. Subdevice readiness scans global compatible nodes, so multiple decoder instances in a system could complicate readiness. LAT_SOC intentionally has no IRQ.

## Test Signals
Device-tree child population, all subdevice combinations, IRQ success/ignored-status paths, PM runtime enablement, and open before all subdevices probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_hw.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_hw.h

## Purpose
This header defines decoder hardware-subdevice register constants, hardware register indexes, and the subdevice runtime state structure.

## Important APIs, Types, And Functions
Register constants identify active-status and interrupt configuration bits. `IS_SUPPORT_VDEC_HW_IRQ()` excludes LAT_SOC from IRQ use. `enum mtk_vdec_hw_reg_idx` indexes subdevice SYS and MISC register bases. `struct mtk_vdec_hw_dev` stores child platform device, parent decoder device, mapped registers, current context, IRQ number, PM resources, and hardware index.

## Control Flow
No direct execution. Parent/subdevice probe, IRQ handling, PM, and current-context helpers consume these definitions.

## State, Persistence, And Dependencies
State is runtime-only per hardware subdevice. Dependencies include I/O access, platform devices, and decoder driver state.

## Integration Points
Included by child hardware driver, decoder parent driver, decoder PM, and common util code for subdevice lookup.

## Risks
Register offsets and IRQ masks are hardware ABI. Hardware indexes must align with `enum mtk_vdec_hw_id`. LAT_SOC no-IRQ behavior must match device tree and PM requirements.

## Test Signals
Compile coverage, child probe, IRQ clear sequence, and PM enable/disable for LAT/core/SOC blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_pm.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_pm.c

## Purpose
This file implements decoder clock discovery, runtime power/clock gating, IRQ enable/disable, and inner-racing register snapshot management.

## Important APIs, Types, And Functions
`mtk_vcodec_init_dec_clk()` reads `clock-names`, obtains clocks, and stores them in `struct mtk_vcodec_pm`. Internal helpers power devices on/off with runtime PM, enable/disable clocks, and enable/disable IRQs for parent or subdevice hardware. `mtk_vcodec_dec_enable_hardware()` locks the selected hardware mutex, powers/clocks required blocks, enables IRQ, and loads racing info. `mtk_vcodec_dec_disable_hardware()` records racing info, disables IRQ, powers/clocks off, and unlocks.

## Control Flow
Probe initializes clocks. Before hardware execution, codec workers call enable for a hardware index. On LAT architecture, enabling CORE also powers LAT0; enabling LAT0 also powers LAT_SOC. After completion or error, workers call disable in reverse. Inner-racing capability snapshots/restores 132 registers when transitioning between zero and nonzero active decode count.

## State, Persistence, And Dependencies
State includes clock arrays, runtime PM usage counts, hardware mutexes, IRQ enable state, `dec_active_cnt`, `vdec_racing_info`, and `dec_racing_info_mutex`. It is runtime-only. Dependencies include Linux clocks, IRQ APIs, runtime PM, subdevice hardware state, and capability bits.

## Integration Points
Called by codec-specific decoder implementations around hardware access. Parent and subdevice probe use `mtk_vcodec_init_dec_clk()`.

## Risks
`mtk_vcodec_dec_clock_on()` logs errors but returns void, so callers cannot fail early after partial clock enable failure. PM get failures are logged but not propagated in child-on path. IRQ calls assume valid subdevice data. Racing snapshot offsets/count are hard-coded.

## Test Signals
Clock-name parsing failures, runtime PM errors, enable/disable nesting across hardware indexes, LAT/core dependency coverage, IRQ enable state, and inner-racing capability tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_pm.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_pm.h

## Purpose
This header exposes decoder power-management helpers for clock initialization and per-hardware enable/disable.

## Important APIs, Types, And Functions
`mtk_vcodec_init_dec_clk()` initializes a `struct mtk_vcodec_pm` from a platform device. `mtk_vcodec_dec_enable_hardware()` and `mtk_vcodec_dec_disable_hardware()` wrap locking, runtime PM, clocks, IRQs, and racing-state handling for a decoder context and hardware index.

## Control Flow
No direct execution. Probe calls clock init; codec workers call enable before accessing hardware and disable afterward.

## State, Persistence, And Dependencies
The helpers operate on runtime PM and clock state stored in decoder device/subdevice structures. The header depends on decoder driver state.

## Integration Points
Included by parent probe, subdevice probe, shared decoder operations, stateful/stateless workers through codec interfaces, and hardware driver code.

## Risks
Callers must pair enable/disable for the same hardware index or deadlock/leak PM references. The API does not expose failure from enable.

## Test Signals
Pairing tests, lockdep around hardware mutexes, runtime PM traces, and clock prepare/unprepare balancing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_stateful.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_stateful.c

## Purpose
This file implements the stateful decoder behavior used by older MediaTek platforms such as MT8173. It manages stream-header parsing, DPB sizing, dynamic resolution change events, and reference/display buffer recycling.

## Important APIs, Types, And Functions
Static format table exposes H.264, VP8, VP9 coded formats and MT21C capture. `get_display_buffer()` returns decoded display frames to userspace. `get_free_buffer()` recycles capture buffers no longer referenced by firmware. `mtk_vdec_flush_decoder()` drains the decoder. `mtk_vdec_pic_info_update()` fetches picture info and DPB size. `mtk_vdec_worker()` performs normal frame decode or empty-flush handling. `vb2ops_vdec_stateful_buf_queue()` has special header-parse logic for early OUTPUT buffers and capture-buffer ownership flags. Controls expose `V4L2_CID_MIN_BUFFERS_FOR_CAPTURE` plus VP9/H.264 profile limits. `mtk_vdec_8173_pdata` wires these callbacks.

## Control Flow
After OUTPUT format setup initializes the codec, the first queued output buffers are decoded with no framebuffer to parse headers and detect resolution. Once header info is available, the driver updates capture sizes, DPB size, moves to `MTK_STATE_HEADER`, and emits `SOURCE_CHANGE`. During normal decode, a source and destination buffer are passed to `vdec_if_decode()`. Display buffers are completed, free reference buffers are requeued or released, and resolution changes trigger flush plus a source-change event. Decoder STOP queues an empty flush buffer that returns a LAST capture buffer.

## State, Persistence, And Dependencies
State includes context `picinfo`, `last_decoded_picinfo`, `dpb_size`, decoded frame count, capture-buffer flags (`used`, `queued_in_vb2`, `queued_in_v4l2`), and codec state. Dependencies include V4L2 events, vb2 DMA-contig, decoder PM via codec implementations, and `vdec_if_*`.

## Integration Points
Selected by OF pdata for MT8173. Shared decoder ioctls call these vb2 ops and worker through pdata.

## Risks
Capture-buffer ownership is complex and protected by `ctx->lock`; incorrect flags can leak buffers or return reference frames too early. Resolution-change condition uses width or height equality logic that may miss one-dimension changes. Empty flush consumes a destination buffer and must set LAST correctly.

## Test Signals
Stateful V4L2 compliance, header-only buffers, dynamic resolution streams, DPB minimum buffer control, flush/STOP/LAST semantics, reference-frame recycling, and error injection from `vdec_if_decode()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_stateful.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_stateless.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_stateless.c

## Purpose
This file implements the stateless/request-API decoder behavior for newer MediaTek platforms. It defines supported stateless codec controls, media-request operations, dynamic format exposure from firmware capability, request-based decode workers, and platform pdata for single-core and LAT/core architectures.

## Important APIs, Types, And Functions
`mtk_stateless_controls` defines H.264, VP8, VP9, HEVC, and AV1 controls plus profile/level/decode-mode/start-code limits. `mtk_vdec_worker()` consumes one OUTPUT request buffer, applies request controls, decodes, completes source and capture buffers, and manages request refcounts. `vdec_get_cap_buffer()` returns the current capture framebuffer to codec implementations. `mtk_vdec_s_ctrl()` validates bit depth/subsampling and switches capture format for 10-bit streams. Media request ops allocate, validate exactly one buffer, mark manual completion, and queue via `v4l2_m2m_request_queue()`. `mtk_vcodec_get_supported_formats()` populates global format tables from firmware capability bits. Pdata symbols cover MT8183, LAT single-core, and subdevice single-core variants.

## Control Flow
Probe selects stateless pdata and registers a media controller. On first open, firmware capability bits populate capture and coded formats. OUTPUT queues require media requests. Queueing the first OUTPUT buffer moves the context from INIT to HEADER. The worker applies request controls, increments request refcount, calls `vdec_if_decode()`, completes source controls/buffer, and either completes capture immediately or leaves LAT/core paths to complete later through `cap_to_disp()`. Request completion is manual and tied to kref release.

## State, Persistence, And Dependencies
State includes global static format arrays/defaults, per-context request/control state, 10-bit bitstream flag, capture format, picinfo, and message queue/VPU instance data used by codec implementations. No persistence. Dependencies include media requests, V4L2 stateless controls, vb2 DMA-contig, decoder interface, firmware capability bits, and optional LAT/core message queues.

## Integration Points
Selected by MT8183/MT8186/MT8188/MT8192/MT8195 pdata. Shared decoder ioctls use this file's controls, media ops, vb2 ops, worker, `get_cap_buffer`, and `cap_to_disp`.

## Risks
`mtk_video_formats`, defaults, and `num_formats` are global static state initialized once from the first context's firmware capability, which can be risky if multiple devices differ. `fops_media_request_alloc()` does not check allocation failure before returning `&req->req`. Request completion has multiple paths and must avoid double completion or leaks. 10-bit format switching depends on SPS/frame controls arriving before capture negotiation expectations.

## Test Signals
Stateless V4L2/media-request compliance, one-buffer request validation, H.264/VP8/VP9/HEVC/AV1 control coverage, 8-bit and 10-bit streams, LAT/core delayed capture completion, VP8 immediate completion, request error paths, and multi-device capability tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_stateless.c -->

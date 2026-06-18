# subset-b-004145 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/v4l2.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/v4l2.c

Purpose: Implements the V4L2/media-controller front end for the NVIDIA Tegra VDE stateless H.264 decoder. It exposes a mem2mem multiplanar video node, request API validation, H.264 stateless controls, buffer queueing, and job scheduling into the hardware-specific decode callbacks supplied by the selected SoC format descriptor.

Important APIs, types, and functions: `ctrl_cfgs` declares the mandatory stateless H.264 decode controls, frame-based decode mode, Annex-B start code, profile, and level. `tegra_ctx` stores per-open control pointers, coded/capture formats, and the work item used after hardware submission. `tegra_queue_init()` creates OUTPUT and CAPTURE `vb2_queue`s with request support required on OUTPUT. `tegra_buf_init()`, `tegra_buf_prepare()`, and `tegra_buf_cleanup()` map MMAP/DMABUF planes through the Tegra DMA/IOMMU helpers and allocate capture auxiliary BOs for reference data. Format ioctls are implemented by `tegra_try_*_fmt()`, `tegra_s_*_fmt()`, and enumeration helpers. `tegra_device_run()` is the mem2mem submit hook, and `tegra_decode_complete()` runs `decode_wait()` on the workqueue.

Control flow: `tegra_open()` allocates a flexible `tegra_ctx`, initializes controls and mem2mem queues, then resets coded and decoded formats to SoC defaults. Userspace queues exactly one requested OUTPUT buffer carrying stateless H.264 controls and one CAPTURE buffer. `tegra_device_run()` calls `v4l2_ctrl_request_setup()`, invokes `ctx->coded_fmt_desc->decode_run(ctx)`, completes the request controls, and either finishes with error or queues work. The work item waits for hardware completion through the descriptor `decode_wait()` callback and then completes the mem2mem job. Streaming stop drains queued buffers as errors and completes any attached requests.

State and persistence behavior: Per-filehandle state is in `tegra_ctx`; device-wide state is in `tegra_vde`. Coded format changes reset capture format and propagate colorimetry. DMABUF attachments are cached through helpers in other Tegra VDE files and synchronized on release. Capture buffers may own an auxiliary BO used by later B-frame decoding. The request validator rejects empty requests and requests with more than one buffer.

Dependencies and integration points: Depends on V4L2 mem2mem, media requests, videobuf2 DMA-contig/DMA-sg, H.264 stateless control ABI, Tegra VDE IOMMU/DMABUF helpers, and hardware callbacks `tegra_vde_h264_decode_run()`/`tegra_vde_h264_decode_wait()`. It registers the media device, V4L2 device, video node, and media controller entity via `tegra_vde_v4l2_init()`.

Risks: Buffer size and alignment checks are hardware-sensitive: coded OUTPUT is padded to `SXE_BUFFER`, CAPTURE uses `FRAMEID_ALIGN`, and planar YVU swaps DMA addresses. Request misuse is mostly rejected, but userspace must provide consistent controls and buffer geometry. Dynamic resolution is limited by queue busy/streaming checks. DMABUF and IOMMU cleanup correctness is critical because mappings can outlive individual queue operations until release synchronization.

Test signals: Probe should create `/dev/video*` named `tegra-vde` with mem2mem media topology. `v4l2-compliance` should cover format enumeration, request validation, streamon/off, and EBUSY cases. Decode tests need stateless H.264 slices with SPS/PPS/decode params, MMAP and DMABUF buffers, YUV420/YVU420 capture formats where supported, resolution change attempts, stop-streaming cleanup, and error injection for bad payload alignment/size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/v4l2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/vde.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/vde.c

Purpose: Provides the platform driver, register tracing helpers, DMA buffer-object allocation, IRQ handling, runtime/system PM, SoC capability tables, and V4L2 front-end bring-up for the Tegra VDE hardware block.

Important APIs, types, and functions: `tegra_vde_writel()`, `tegra_vde_readl()`, and `tegra_vde_set_bits()` wrap MMIO with tracepoints. `tegra_vde_alloc_bo()`/`tegra_vde_free_bo()` allocate DMA memory, derive SG tables, map for DMA and optional IOMMU IOVA, and return a `tegra_vde_bo`. `tegra_vde_isr()` completes `decode_completion` from the `sync-token` IRQ. Runtime PM is handled by `tegra_vde_runtime_suspend()` and `tegra_vde_runtime_resume()`. `tegra_vde_probe()` maps named register resources, obtains clocks/resets/IRAM/IOMMU, allocates the secure BO, and calls `tegra_vde_v4l2_init()`.

Control flow: Probe gathers all MMIO windows (`sxe`, `bsev`, `mbe`, `ppe`, `mce`, `tfe`, `ppb`, `vdma`, `frameid`), requests the sync-token IRQ, initializes OPP and IRAM, initializes IOMMU and runtime PM, power-cycles the block once, allocates a secure BO, and registers V4L2. Remove unregisters V4L2, frees the secure BO, balances runtime PM, leaves the domain on/clock-gated for reboot safety, clears DMABUF cache, deinitializes IOMMU, and returns IRAM to the gen_pool. Shutdown forces runtime resume for bootloader compatibility.

State and persistence behavior: Device state is held in `struct tegra_vde`, including MMIO bases, completion, IRAM address, IOMMU domain/group, DMABUF map list, secure BO, and media/V4L2 objects. Runtime PM acquire/release owns reset and clock lifetimes; system suspend locks `vde->lock` around forced runtime suspend/resume. SoC tables persist capabilities such as supported decoded formats and whether reference picture marking is supported.

Dependencies and integration points: Integrates with platform resources from device tree, Tegra powergate/PMC APIs, reset framework, common Tegra OPP helper, gen_pool IRAM, Linux DMA/IOMMU APIs, IRQs, PM runtime, tracepoints, and the V4L2 layer in `v4l2.c`. Device-tree compatibles select Tegra20/30/114/124 descriptors.

Risks: Error unwind spans IRAM, IOMMU, runtime PM, secure BO, and V4L2 registration; leaks or double releases would affect scarce IRAM and DMA mappings. `tegra_vde_pm_suspend()` returns early on force-suspend failure without unlocking `vde->lock`, which is a notable control-flow risk to audit against surrounding kernel version expectations. Warm reboot behavior depends on leaving VDE powered in shutdown/remove paths. Tegra124 advertises no decoded formats in this file, so userspace format enumeration may intentionally fail until tiled formats are supported.

Test signals: Platform probe should validate all named resources and IRQ, then register the video node. Runtime PM tests should exercise open/stream/idle autosuspend, remove after use, shutdown, and suspend/resume. DMA tests should cover IOMMU and non-IOMMU systems, secure BO allocation failure unwinds, and tracepoint-enabled MMIO access. Device-tree tests should cover all compatibles and missing optional `mc` reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/vde.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/vde.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/vde.h

Purpose: Shared internal header for the Tegra VDE driver. It defines register offsets, hardware alignment constants, core device/context/buffer structures, SoC format descriptors, and cross-file function prototypes for V4L2, H.264 decode, IOMMU, DMABUF cache, and platform code.

Important APIs, types, and functions: Register constants cover BSE command queue/control/interrupt fields and hardware buffer alignment (`BSEV_ALIGN`, `FRAMEID_ALIGN`, `SXE_BUFFER`, `VDE_ATOM`). `struct tegra_video_frame` describes decoded/reference frame addresses and metadata. `struct tegra_coded_fmt_desc` binds a coded fourcc to frame-size limits, decoded formats, and decode callbacks. `struct tegra_vde_soc` carries per-SoC capabilities. `struct tegra_vde_bo`, `struct tegra_vde`, `struct tegra_ctx`, and `struct tegra_m2m_buffer` define persistent device, filehandle, and vb2 buffer state. `vb_to_tegra_buf()` converts vb2 buffers to driver buffers.

Control flow: The header itself has no runtime control flow, but it defines the contracts used by the runtime path: V4L2 queues store `tegra_m2m_buffer`; `decode_run()`/`decode_wait()` operate on `tegra_ctx`; platform code allocates `tegra_vde_bo`; IOMMU and DMABUF helpers map buffers before hardware programming; register helpers provide tracing-aware MMIO access.

State and persistence behavior: `tegra_vde` is the long-lived platform device state and includes MMIO bases, locks, completion, IOMMU state, IRAM, secure BO, V4L2/media devices, workqueue, and a DPB-sized `frames` array. `tegra_ctx` is per-open and stores the active H.264 controls and formats. `tegra_m2m_buffer` is per-buffer and stores DMA/IOMMU addresses, attachments, auxiliary BO, and B-frame marker.

Dependencies and integration points: Pulls in Linux completion, DMA direction, IOVA, list/mutex/workqueue, and media/V4L2/videobuf2 headers. It links platform code (`vde.c`), V4L2 code (`v4l2.c`), H.264 decode implementation, IOMMU implementation, and DMABUF cache implementation.

Risks: The structs encode ownership boundaries; misuse can leak IOVA, SG tables, DMABUF attachments, or auxiliary BOs. Flexible array `ctrls[]` requires allocation with enough elements. The register-base-name helper is used for diagnostics and must stay in sync with MMIO fields. Alignment constants are part of ABI-adjacent buffer validation because userspace-provided planes are accepted or rejected based on them.

Test signals: Compile coverage should include all translation units that include this header. Static analysis should verify flexible-array allocation and container conversions. Runtime decode tests indirectly validate `frames`, per-buffer DMA address bookkeeping, and SoC descriptor callbacks. Tracepoint tests can check `tegra_vde_reg_base_name()` labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/vde.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/Kconfig

Purpose: Top-level Kconfig menu for NXP media platform drivers. It declares camera receiver/bridge drivers and mem2mem engines, and sources subdirectory Kconfig files for i.MX8 ISI, DW100, and i.MX JPEG.

Important APIs, types, and functions: Defines `VIDEO_IMX7_CSI`, `VIDEO_IMX8MQ_MIPI_CSI2`, `VIDEO_IMX_MIPI_CSIS`, `VIDEO_IMX_PXP`, and `VIDEO_MX2_EMMAPRP`, then sources `drivers/media/platform/nxp/dw100/Kconfig` and `drivers/media/platform/nxp/imx-jpeg/Kconfig`. Each option expresses architecture, V4L2, DMA, media-controller, fwnode, subdev, mem2mem, and videobuf2 dependencies.

Control flow: Build configuration enters this file under the media platform tree. Enabled symbols select helper frameworks so corresponding objects in the Makefile can be compiled and linked. Subdirectory source lines extend the menu for nested drivers.

State and persistence behavior: No runtime state. Persistent effect is the generated kernel configuration symbols that decide which drivers exist in the built kernel or modules.

Dependencies and integration points: Integrates with `drivers/media/platform/nxp/Makefile`; each `config` symbol maps to an object or subdirectory. It also coordinates with architecture symbols (`ARCH_MXC`, `SOC_IMX27`) and `COMPILE_TEST`.

Risks: Missing `select` lines can cause link failures or disabled runtime APIs. Overly broad `COMPILE_TEST` coverage may expose code to architectures without real hardware assumptions. Help text and symbol names are user-facing kernel configuration ABI.

Test signals: `allyesconfig`, `allmodconfig`, and targeted configs should verify symbol dependency closure. `scripts/kconfig/conf` and build tests should cover both built-in and module modes, especially subdirectory Kconfig source paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/Makefile

Purpose: Top-level build glue for NXP media platform drivers.

Important APIs, types, and functions: Adds subdirectories `dw100/`, `imx-jpeg/`, and `imx8-isi/` unconditionally to `obj-y`, allowing their own Makefiles to decide object inclusion. Maps top-level Kconfig symbols to objects: `imx7-media-csi.o`, `imx8mq-mipi-csi2.o`, `imx-mipi-csis.o`, `imx-pxp.o`, and `mx2_emmaprp.o`.

Control flow: Kbuild evaluates this file after Kconfig selection. `obj-y += subdir/` descends into subdirectories, while `obj-$(CONFIG_...) += file.o` includes selected objects.

State and persistence behavior: No runtime state; it persists build composition based on `.config`.

Dependencies and integration points: Must remain synchronized with `Kconfig` symbols and actual source filenames. Subdirectories `dw100` and `imx-jpeg` have their own Makefiles mapping local config symbols to module objects.

Risks: Unconditional subdirectory descent is normal but relies on child Makefiles guarding objects correctly. A symbol/object mismatch causes missing driver builds or stale object references.

Test signals: Kbuild with each `CONFIG_VIDEO_*` option as built-in and module should produce the expected object or module name. `make drivers/media/platform/nxp/` catches path and symbol drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/dw100/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/dw100/Kconfig

Purpose: Declares the `VIDEO_DW100` configuration option for the NXP i.MX DW100 hardware dewarper mem2mem driver.

Important APIs, types, and functions: `VIDEO_DW100` is a tristate depending on `V4L_MEM2MEM_DRIVERS`, `VIDEO_DEV`, and `ARCH_MXC || COMPILE_TEST`; it selects `MEDIA_CONTROLLER`, `V4L2_MEM2MEM_DEV`, and `VIDEOBUF2_DMA_CONTIG`.

Control flow: When the symbol is enabled, the child Makefile builds `dw100.o`. The help text describes the hardware as a memory-to-memory geometrical transform engine driven by a programmable dewarping map.

State and persistence behavior: No runtime state; it persists the build-time inclusion mode of the DW100 driver.

Dependencies and integration points: Coordinates with `drivers/media/platform/nxp/dw100/Makefile`, V4L2 mem2mem core, media controller, and DMA-contiguous vb2 memory.

Risks: If request/control dependencies evolve, this Kconfig may need additional selects. `COMPILE_TEST` can build the driver on non-MXC platforms, so code must keep compile-time hardware assumptions isolated.

Test signals: Build `CONFIG_VIDEO_DW100=y` and `m` with `ARCH_MXC` and `COMPILE_TEST`. Verify the resulting module name is `dw100`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/dw100/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/dw100/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/dw100/Makefile

Purpose: Kbuild rule for the DW100 dewarper driver.

Important APIs, types, and functions: `obj-$(CONFIG_VIDEO_DW100) += dw100.o` maps the Kconfig symbol to the single translation unit.

Control flow: Kbuild includes `dw100.o` as built-in or module according to `CONFIG_VIDEO_DW100`.

State and persistence behavior: No runtime state; persistent effect is build output composition.

Dependencies and integration points: Must match the symbol declared in `dw100/Kconfig` and the source file `dw100.c`.

Risks: Minimal; symbol drift or filename changes are the main maintenance concerns.

Test signals: `make M=drivers/media/platform/nxp/dw100` or a full media build should generate `dw100.o`/`dw100.ko` when selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/dw100/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/dw100/dw100.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/dw100/dw100.c

Purpose: V4L2 mem2mem driver for the NXP DW100 hardware dewarper. It accepts YUV input/output buffers, applies a programmable 16x16 vertex map and crop/scale configuration, and drives the hardware through MMIO and threaded IRQ completion.

Important APIs, types, and functions: `struct dw100_device` holds platform, media, MMIO, clocks, debugfs, and frame-failure state. `struct dw100_ctx` stores per-open queues, controls, crop, and DMA coherent LUT mapping. `formats[]` describes supported semiplanar/multiplanar/packed YUV formats and register encodings. `dw100_ctrl_dewarping_map_init()` builds an identity UQ12.4 vertex map, and `dw100_s_ctrl()` marks user maps dirty. `dw100_queue_setup()`, `dw100_buf_prepare()`, `dw100_m2m_queue_init()`, and format/selection ioctls implement V4L2. `dw100_device_run()` programs source, destination, crop, map, IRQs, and start bit. `dw100_irq_handler()` and `dw100_irq_thread_fn()` finish jobs.

Control flow: `dw100_probe()` acquires clocks, MMIO, IRQ, runtime PM, V4L2/media/m2m devices, video node, media controller, and debugfs. `dw100_open()` creates a context with default 640x480 NV16 source/capture formats and a custom dewarping-map control. Streaming allocates a coherent map and resumes the device. A mem2mem job sets up any request controls, copies the dirty map, completes controls, assigns sequence numbers, copies metadata, programs all hardware registers, enables IRQs, starts the dewarper, and enables AXI master. The hard IRQ disables IRQ/bus, records success/error from status bits, clears pending bits, and wakes the threaded handler to call `v4l2_m2m_buf_done_and_job_finish()`.

State and persistence behavior: Device state persists across opens; per-context state includes current source/capture formats, crop rectangle, sequence counters, and LUT. The map exists only while streaming and is rebuilt when streaming starts or capture format changes dimensions. Dynamic LUT updates require V4L2 requests on queued source buffers; without requests, dirty maps trigger a warning and are not dynamically copied. Runtime PM is taken on stream start and dropped on stop.

Dependencies and integration points: Uses V4L2 mem2mem, media controller, videobuf2 DMA-contig, custom uAPI control `V4L2_CID_DW100_DEWARPING_16x16_VERTEX_MAP`, runtime PM, clk bulk API, platform IRQ/MMIO, debugfs, and device-tree compatible `nxp,imx8mp-dw100`.

Risks: LUT dimension changes depend on capture format and `v4l2_ctrl_modify_dimensions()`, so controls and buffers must stay synchronized. The crop/scale math uses fixed-point rounding and flag semantics that need careful edge testing. Streaming start creates a map for either queue independently, so source/capture start ordering should be tested. Hardware errors set a device-wide `frame_failed` flag in IRQ context; concurrent context assumptions rely on mem2mem serialization. Register programming assumes DMA addresses can be represented by the register macros' shifted fields.

Test signals: Use `v4l2-compliance` for mem2mem ioctls, requests, selections, and stream lifecycle. Functional tests should process NV12/NV16/NV21/NV61/YUYV/UYVY, single- and multi-plane forms, default identity map and custom maps, crop flags `GE`/`LE`, DMABUF and MMAP, IRQ error paths, streamoff while queued, runtime suspend/resume, and debugfs `dump_regs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/dw100/dw100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/dw100/dw100_regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/dw100/dw100_regs.h

Purpose: Register map and bitfield helper macros for the DW100 dewarper hardware.

Important APIs, types, and functions: Defines offsets for control, LUT address/size, source/destination image bases/sizes/strides, swap control, split lines, scale, ROI, boundary pixel, interrupt status, bus control, timeout, and destination plane sizes. Macros such as `DW100_DEWARP_CTRL_INPUT_FORMAT()`, `DW100_MAP_LUT_ADDR_ADDR()`, `DW100_IMG_SIZE_WIDTH()`, `DW100_SWAP_CONTROL_*()`, `DW100_INTERRUPT_STATUS_INT_*`, and `DW100_BUS_CTRL_AXI_MASTER_ENABLE` encode register fields.

Control flow: No runtime control flow. `dw100.c` consumes these macros while programming the hardware before each job, handling IRQ status, clearing interrupts, and enabling/disabling the AXI master.

State and persistence behavior: No software state. The definitions represent hardware state layout that persists in device registers while powered.

Dependencies and integration points: Requires Linux bit macros (`BIT`, `GENMASK`) through including code. It is tightly coupled to the DW100 MMIO programming sequence in `dw100.c`.

Risks: Field macros shift DMA addresses by 4 and mask to 30 bits, so address alignment and addressable range are implicit requirements. Incorrect masks or swapped source/destination fields would cause image corruption or bus faults. Interrupt status combines status, enable, busy, and clear fields in one register, increasing risk of write-side mistakes.

Test signals: Register dumps before/after a job should match expected source/destination geometry, LUT, swap, and interrupt bits. Static compile tests catch macro syntax, while hardware tests with each supported pixel format catch format/swap field errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/dw100/dw100_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-jpeg/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-jpeg/Kconfig

Purpose: Declares the `VIDEO_IMX8_JPEG` Kconfig option for the i.MX8 QXP/QM integrated JPEG encoder/decoder V4L2 mem2mem driver.

Important APIs, types, and functions: `VIDEO_IMX8_JPEG` is a tristate depending on `V4L_MEM2MEM_DRIVERS`, `ARCH_MXC || COMPILE_TEST`, and `VIDEO_DEV`; it selects `VIDEOBUF2_DMA_CONTIG`, `V4L2_MEM2MEM_DEV`, and `V4L2_JPEG_HELPER`.

Control flow: Enabling the symbol causes the Makefile to build the combined `mxc-jpeg-encdec` object from hardware and core source files.

State and persistence behavior: No runtime state; build-time selection controls module availability.

Dependencies and integration points: Coordinates with `imx-jpeg/Makefile`, the V4L2 JPEG parser/helper library, mem2mem core, and DMA-contiguous vb2 memory.

Risks: The driver relies on `V4L2_JPEG_HELPER`; missing select would create unresolved symbols. Architecture/compile-test settings need to keep non-MXC build coverage possible.

Test signals: Build tests for `CONFIG_VIDEO_IMX8_JPEG=y/m`, plus compile-test builds on non-MXC architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-jpeg/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-jpeg/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-jpeg/Makefile

Purpose: Kbuild composition for the i.MX JPEG encoder/decoder module.

Important APIs, types, and functions: `mxc-jpeg-encdec-objs := mxc-jpeg-hw.o mxc-jpeg.o` combines register helper and core V4L2 logic into one module/object. `obj-$(CONFIG_VIDEO_IMX8_JPEG) += mxc-jpeg-encdec.o` ties it to Kconfig.

Control flow: Kbuild first builds both object files, then links them into `mxc-jpeg-encdec`.

State and persistence behavior: No runtime state.

Dependencies and integration points: Must match symbols in `Kconfig` and exported function prototypes between `mxc-jpeg-hw.c`, `mxc-jpeg-hw.h`, and `mxc-jpeg.c`.

Risks: Renaming either object without updating this Makefile breaks module linkage. Function definitions in `mxc-jpeg-hw.c` are required by `mxc-jpeg.c`.

Test signals: Selecting `VIDEO_IMX8_JPEG` should produce `mxc-jpeg-encdec.ko` in module builds and link both object files in built-in builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-jpeg/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-jpeg/mxc-jpeg-hw.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-jpeg/mxc-jpeg-hw.c

Purpose: Low-level helper implementation for the i.MX8 JPEG wrapper and CAST encoder/decoder registers. It centralizes debug printing, interrupt enable/disable, reset, encoder mode control, global enable, slot enable, endian selection, and descriptor field setters.

Important APIs, types, and functions: `print_descriptor_info()`, `print_cast_status()`, and `print_wrapper_info()` emit register/descriptor diagnostics. `mxc_jpeg_enable_irq()` and `mxc_jpeg_disable_irq()` manage per-slot status/IRQ registers. `mxc_jpeg_sw_reset()`, `mxc_jpeg_enable()`, `mxc_jpeg_enable_slot()`, and `mxc_jpeg_set_l_endian()` control wrapper state. Encoder helpers `mxc_jpeg_enc_mode_conf()`, `mxc_jpeg_enc_mode_go()`, and `mxc_jpeg_enc_set_quality()` program CAST mode/quality. Descriptor setters write buffer size, image resolution, line pitch, next descriptor pointer, and clear descriptor validation.

Control flow: The core driver calls these helpers during probe-time version checks, per-job descriptor setup, encoder config/GO phases, decoder GO, IRQ handling, timeout reset, and cleanup. The functions are thin MMIO or structure writes without their own locking; callers provide hardware serialization.

State and persistence behavior: The file mutates hardware registers and `struct mxc_jpeg_desc` fields. It does not own persistent state; persistence is in the device registers and DMA descriptors allocated by `mxc-jpeg.c`.

Dependencies and integration points: Includes `mxc-jpeg-hw.h` and `mxc-jpeg.h`, uses `readl()`/`writel()` and `dev_dbg()`. It is linked into `mxc-jpeg-encdec` and consumed by the core V4L2 driver.

Risks: Register constants are shared for read-only status and write-only control aliases, so helper misuse can be subtle. IRQ helpers clear all status bits and configure a fixed mask (`0xF0C`), which must match hardware expectations. `mxc_jpeg_enable()` reads back `reg` rather than `reg + GLB_CTRL`, relying on `GLB_CTRL` being zero.

Test signals: Dynamic debug should show descriptor and wrapper state during encode/decode. Hardware tests should verify IRQ enable/disable, software reset recovery, encoder quality effects, little-endian setting, and descriptor pointer validation for configured slots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-jpeg/mxc-jpeg-hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-jpeg/mxc-jpeg-hw.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-jpeg/mxc-jpeg-hw.h

Purpose: Hardware register and bitfield definition header for the i.MX8 JPEG wrapper/CAST block, plus low-level helper prototypes.

Important APIs, types, and functions: Defines wrapper offsets (`GLB_CTRL`, `COM_STATUS`, buffer/stream/image fields), CAST status/control aliases, per-slot register offsets via `MXC_SLOT_OFFSET()`, GLB/COM/STM/SLOT field macros, next-descriptor enable and decoder exit-idle values, and `enum mxc_jpeg_image_format`. Declares all helper functions implemented in `mxc-jpeg-hw.c`.

Control flow: No runtime control flow. `mxc-jpeg.c` uses these constants to encode descriptors, inspect IRQ status, query version, and control encode/decode phases.

State and persistence behavior: No software state; describes hardware register state and descriptor bit encodings.

Dependencies and integration points: Includes Linux `bitfield.h` and `mxc-jpeg.h` for descriptor structures. It is the contract between the core driver and helper implementation.

Risks: CAST decoder and encoder control registers alias status offsets, requiring mode-aware access. `GLB_CTRL_CUR_VERSION()` derives encoder config behavior; wrong masks select the wrong descriptor/manual config flow. Image format enum values must match hardware `STM_CTRL_IMAGE_FORMAT()`.

Test signals: Compile tests validate macro/prototype consistency. Runtime encode/decode on v0 and v1 hardware validates version-dependent paths, image format encodings, slot offsets, and status bit handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-jpeg/mxc-jpeg-hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-jpeg/mxc-jpeg.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-jpeg/mxc-jpeg.c

Purpose: Core V4L2 mem2mem driver for i.MX8 QXP/QM JPEG decode and encode. It handles raw/JPEG format negotiation, JPEG marker parsing, descriptor construction, source-change events, encoder quality control, queueing, IRQ completion, runtime PM, power-domain attachment, and platform registration.

Important APIs, types, and functions: `mxc_formats[]` lists JPEG, BGR/ABGR, NV12/P012, YUYV/Y212, YUV24/YUV48, and gray formats with subsampling, precision, plane counts, and alignment. `mxc_jpeg_src_buf` adds parse flags and detected dimensions/format to source buffers. Allocation helpers manage descriptors/config streams in SRAM gen_pool or coherent DMA. `mxc_jpeg_parse()` uses `v4l2_jpeg_parse_header()` and may patch component IDs. `mxc_jpeg_source_change()` updates capture queue state and queues `V4L2_EVENT_SOURCE_CHANGE`. `mxc_jpeg_config_dec_desc()` and `mxc_jpeg_config_enc_desc()` build hardware descriptors, including injected DHT/config streams. `mxc_jpeg_device_run()` submits jobs, and `mxc_jpeg_dec_irq()` completes encode/decode results. Ioctl tables expose formats, selection, events, encoder/decoder commands, buffers, and streaming.

Control flow: Probe selects encode or decode mode from compatible data, maps registers, requests IRQ, obtains optional SRAM, clocks, and power domains, registers V4L2/mem2mem/video device, enables runtime PM, and for encoders chooses v0 manual or v1 descriptor config ops by hardware version. Open creates a context, mem2mem queues, controls, defaults, and timeout work. OUTPUT queueing in decode mode parses JPEG headers before scheduling. Job readiness blocks decode until source-change handling is resolved. Device run validates buffers, handles parse errors, enables the hardware/slot, allocates slot data, configures descriptors, starts encoder config or decoder GO, and schedules a timeout. IRQ handles config-phase completions, DHT injection chaining, payload sizing, buffer completion, slot release, and mem2mem job finish.

State and persistence behavior: Device state includes mode, locks, clocks, V4L2/media objects, one slot data structure, optional SRAM pool, power domains, and version-specific encoder ops. Context state includes output/capture queue geometry, crop, source-change flags, parsed-header state, slot number, encoder state, JPEG quality, and timeout work. Source buffers persist parse outcomes (`dht_needed`, `jpeg_parse_error`, detected format/size). Descriptor memory is reused per device slot and freed at remove.

Dependencies and integration points: Uses V4L2 mem2mem, videobuf2 DMA-contig, V4L2 JPEG helper/parser, events, encoder/decoder command helpers, runtime PM, gen_pool SRAM, PM domains/device links, clk bulk, platform IRQ/MMIO, and low-level helpers from `mxc-jpeg-hw.c`. Device-tree compatibles distinguish `nxp,imx8qxp-jpgdec` and `nxp,imx8qxp-jpgenc`.

Risks: The driver uses a single tested slot and shared `slot_data`; multi-context correctness depends on mem2mem serialization and `used` checks. JPEG parsing mutates invalid component IDs in the source buffer, so writable/linear vb2 mappings are assumed. Source-change handling, draining, and last-buffer logic are complex and should be regression-tested. Descriptor/config stream offsets and 1 KiB alignment are hardware workarounds. Timeout work and IRQ both finish jobs under `hw_lock`; races around canceling delayed work or release need scrutiny. Address alignment is enforced at 16 bytes, and large images depend on CMA/SRAM capacity.

Test signals: `v4l2-compliance` for mem2mem codecs, plus decode tests for baseline and extended sequential JPEG, missing-DHT streams, invalid component IDs, dynamic resolution/source-change events, EOS/drain commands, single/multi-plane raw outputs, 8-bit and 12-bit precision. Encode tests should cover quality control, crop, raw input formats, v0 and v1 config flows, timeout recovery, streamoff cleanup, runtime suspend/resume, and SRAM versus DMA descriptor allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-jpeg/mxc-jpeg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-jpeg/mxc-jpeg.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-jpeg/mxc-jpeg.h

Purpose: Shared core definitions for the i.MX JPEG driver: limits, modes, format metadata, descriptor layout, queue/context/device state, encoder config ops, and parsed JPEG marker structures.

Important APIs, types, and functions: Constants define default/min/max dimensions, maximum line/stream/image sizes, plane count, pattern buffer size, and DMA alignment. `enum mxc_jpeg_enc_state` tracks encoder config versus encoding phase; `enum mxc_jpeg_mode` distinguishes decode and encode platform instances. `struct mxc_jpeg_fmt` describes raw/JPEG formats. `struct mxc_jpeg_desc` matches the hardware descriptor, including v1 encoder fields. `struct mxc_jpeg_q_data`, `struct mxc_jpeg_ctx`, `struct mxc_jpeg_slot_data`, `struct mxc_jpeg_enc_ops`, and `struct mxc_jpeg_dev` define queue, per-file, slot, version-op, and device state. SOF/SOS structs model parsed JPEG marker payloads.

Control flow: The header has no executable flow, but its structures are traversed by `mxc-jpeg.c` during open, format negotiation, parse, descriptor allocation, encode/decode submission, IRQ completion, and PM operations.

State and persistence behavior: Context state persists for an open filehandle; device state persists for the platform instance. Slot data owns coherent/SRAM descriptor and config-stream memory. Queue data stores adjusted hardware dimensions separately from visible crop dimensions, which is critical for source-change and selection behavior.

Dependencies and integration points: Includes V4L2 control/device/filehandle headers. Included by both `mxc-jpeg.c` and `mxc-jpeg-hw.h`, forming the ABI between descriptor helpers and V4L2 logic.

Risks: `struct mxc_jpeg_desc` is `__packed` and must stay exactly compatible with hardware DMA expectations. Size and alignment constants directly affect userspace buffer validation and descriptor sizing. SOF/SOS packed bitfields are endian-sensitive and are patched in-place in JPEG buffers.

Test signals: Compile-time checks indirectly verify structure visibility. Runtime encode/decode validates descriptor layout, queue adjusted dimensions, JPEG marker parsing structures, and slot allocation/free behavior. Static analysis should inspect packed bitfields and DMA descriptor writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-jpeg/mxc-jpeg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-mipi-csis.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-mipi-csis.c

Purpose: V4L2 sub-device driver for the Samsung/NXP MIPI CSI-2 CSIS receiver found on i.MX7 and i.MX8 SoCs. It bridges a remote CSI-2 source to downstream media entities, configures D-PHY/CSI registers, propagates media-bus formats, counts errors/events, and exposes frame-sync events/debugfs.

Important APIs, types, and functions: Register macros define CSIS common control, clock, interrupt, D-PHY, ISP channel, debug, packet-data, and frame-counter registers. `struct mipi_csis_device` holds resources, subdev/pads/notifier, source link, parsed CSI-2 bus, lane timing, event counters, and debugfs overrides. `mipi_csis_formats[]` maps media-bus codes to CSIS output codes, CSI-2 data types, and bits per sample. Hardware helpers include `mipi_csis_calculate_params()`, `mipi_csis_set_params()`, `mipi_csis_start_stream()`, and `mipi_csis_irq_handler()`. Subdev ops include stream control, format enum/set/get, frame descriptor, log status, and frame-sync event subscription.

Control flow: Probe allocates state, parses DT (`clock-frequency`, `fsl,num-channels`), maps registers, gets IRQ, initializes PHY reset/regulator for v3.3, gets clocks, resets PHY, requests IRQ, initializes the subdev entity/pads, registers an async notifier for the remote endpoint, creates debugfs, and enables runtime PM. Link setup records the active upstream source pad. On stream enable, the driver locks active state, reads sink format, gets active data lanes from the source, computes lane rate and settle parameters from link frequency, resumes PM, resets/programs/enables CSIS, enables the upstream subdev stream, logs counters, and unlocks. Stream disable disables the upstream stream, stops CSIS, logs counters if debugging, and drops PM.

State and persistence behavior: Format state is V4L2 subdev active/try state, with sink propagated to source and source code possibly adjusted for output packing. Event counters persist in `csis->events` until cleared at stream start. Runtime PM owns PHY regulator and clocks. Debugfs can override settle timings and enable verbose event logging. `source.sd`/`source.pad` persist while the media link is enabled.

Dependencies and integration points: Uses V4L2 subdev/media-controller APIs, fwnode async notifier, MIPI CSI-2 helpers, runtime PM, clk bulk, regulator/reset for i.MX7, platform IRQ/MMIO, debugfs, and device tree compatibles `fsl,imx7-mipi-csi2` and `fsl,imx8mm-mipi-csi2`. It connects upstream sensors/bridges to downstream capture pipelines via media links.

Risks: Lane reordering is explicitly unsupported; invalid endpoint data lanes fail registration. Link frequency must be available from the source and produce a lane rate within 80 MHz to 1.5 GHz. JPEG media-bus code is mapped to RAW8 due downstream limitations, which may surprise generic CSI-2 expectations. `mipi_csis_remove()` unregister/cleanup ordering should be watched because notifier and subdev cleanup interact. Debug settle overrides can produce nonfunctional PHY timing. Interrupt counters are protected by a spinlock but logging snapshots are best-effort.

Test signals: Media graph tests should bind a remote sensor endpoint, enable links, propagate formats, and verify source/sink pad behavior. Streaming tests should cover RAW8/10/12/14, YUV422 dual-pixel mode, RGB, JPEG-as-RAW8, different lane counts, missing link frequency failures, SOF frame-sync events, error counter increments, runtime suspend/resume, debugfs register dumps, and i.MX7 regulator/reset versus i.MX8 clock-only behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-mipi-csis.c -->

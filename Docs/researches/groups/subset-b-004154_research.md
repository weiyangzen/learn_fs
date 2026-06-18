# Research: subset-b-004154

Grouped research for Raspberry Pi media platform drivers, Renesas media build metadata, and Qualcomm Venus encoder files. Each section preserves its source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/venc.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/venc.c

Purpose: implements the Qualcomm Venus V4L2 mem2mem encoder platform driver. It exposes `/dev/video*` encoder nodes for raw NV12 input and compressed H.264, VP8, HEVC, MPEG4, and H.263 capture output, translating V4L2 ioctls, vb2 buffers, and encoder commands into Venus HFI session operations.

Important APIs, types, and functions: `venc_formats` is the local format table. `find_format()` and `find_format_by_index()` filter formats through `venus_helper_check_codec()`. `venc_ioctl_ops` wires querycap, enum/try/get/set format, crop selection, frame interval, mem2mem buffer ioctls, events, and encoder commands. `venc_set_properties()` is the central V4L2-control-to-HFI programming path. `venc_init_session()`, `venc_queue_setup()`, `venc_start_streaming()`, `venc_vb2_buf_queue()`, and `venc_buf_done()` bridge vb2 queue lifecycle to firmware. `venc_open()`, `venc_close()`, `venc_probe()`, and runtime PM handlers bind the instance and platform device lifecycle.

Control flow: open allocates `venus_inst`, initializes controls via `venc_ctrl_init()`, creates v4l2-m2m context, and creates an HFI session. Format negotiation clamps and aligns dimensions, keeps output and capture dimensions synchronized, and records colorspace for encoded output. Queue setup resumes the encoder PM domain, initializes the firmware session, fetches HFI buffer requirements, and computes plane sizes. Streaming only starts once both output and capture queues are on; it acquires a Venus core, replays encoder properties, verifies buffer counts, programs buffer counts, then starts HFI/vb2 streaming. STOP encoder command injects an EOS HFI input buffer and moves the state to drain; LAST capture buffer completion moves the state to stopped.

State and persistence: all state is per open instance and in memory: selected formats, dimensions, crop, fps, buffer sizes/counts, streamon bits, HFI codec, sequence counters, registered buffer list, and `enc_state`. Runtime PM state is held on the encoder device with autosuspend. No durable persistence is used.

Dependencies and integration: depends on V4L2, v4l2-mem2mem, vb2 dma-contig, Venus `core.h`, `helpers.h`, HFI helpers, and PM helpers. It registers a platform driver compatible with `venus-encoder`; the parent Venus core supplies `venus_core`, PM ops, V4L2 device, firmware resources, and supported codec limits.

Risks: format alignment changes requested dimensions, so userspace must re-read formats. `venc_set_properties()` has many firmware-version and codec conditionals, making regressions likely around H.264 hierarchical layers, HDR10 SEI, QP ranges, and intra refresh. EOS relies on a sentinel empty HFI input buffer and state transitions. Error paths must correctly return queued buffers and release PM/core references. Buffer count validation depends on current firmware requirements.

Test signals: exercise V4L2 compliance for mem2mem encoder ioctls, format fallback/enumeration for unsupported codecs, streamon order independence, EOS STOP/START behavior, dynamic bitrate/header/keyframe controls while streaming, nonblocking sys-error wait behavior, runtime suspend/resume, and buffer underrun/count failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/venc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/venc.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/venc.h

Purpose: small public header for the Venus encoder implementation. It declares the encoder control initialization entry point used by `venc.c`.

Important APIs/types/functions: forward-declares `struct venus_inst` and exports `int venc_ctrl_init(struct venus_inst *inst);`. The include guard is `__VENUS_VENC_H__`.

Control flow: no runtime control flow; it is a compile-time interface between the encoder core and control registration implementation.

State and persistence: no state is defined here. `venus_inst` ownership and control-handler storage live in shared Venus structures included by `.c` files.

Dependencies and integration: included by `venc.c` and `venc_ctrls.c`. It avoids including full Venus instance definitions, keeping the dependency surface minimal.

Risks: any signature change must be coordinated across the encoder open path and control implementation. Because the header is minimal, hidden coupling exists through `struct venus_inst` fields accessed only in `.c` files.

Test signals: build coverage is the main signal; encoder open should fail cleanly if `venc_ctrl_init()` returns an error from control handler initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/venc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/venc_ctrls.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/venc_ctrls.c

Purpose: registers and handles V4L2 encoder controls for the Venus encoder. It stores control values into `inst->controls.enc` and performs a small set of live HFI updates while both queues are streaming.

Important APIs/types/functions: `venc_calc_bpframes()` converts GOP size and requested consecutive B frames into total B/P frame counts. `dynamic_bitrate_update()` sends `HFI_PROPERTY_CONFIG_VENC_TARGET_BITRATE` for live bitrate/layer bitrate changes. `venc_op_s_ctrl()` handles all standard and compound control writes. `venc_op_g_volatile_ctrl()` reports minimum output buffers from HFI requirements. `venc_ctrl_init()` creates menus, scalar controls, HDR10 compound controls, LTR controls, intra refresh controls, and optional V4/V6 hierarchical coding controls.

Control flow: control setup initializes a V4L2 handler, creates controls with bounds/defaults, checks `ctrl_handler.error`, then runs `v4l2_ctrl_handler_setup()` to seed `venc_controls`. On `s_ctrl`, most controls only update cached state; bitrate and hierarchical layer bitrate can be pushed to firmware immediately; header mode, force key frame, LTR mark, and LTR use are also sent immediately when output and capture queues are streaming.

State and persistence: control values persist only in the lifetime of a `venus_inst`. They are later replayed by `venc_set_properties()` during session setup/start. No persistent storage is used.

Dependencies and integration: depends on V4L2 controls, Venus `core.h`, HFI property constants, and helper functions. It is called from `venc_open()` before instance defaults are fully used by streaming.

Risks: GOP/B-frame validation rejects combinations that cannot produce an exact ratio, which can surprise userspace. Several controls cache per-plane min/max QP fields but `venc_set_properties()` primarily uses packed aggregate min/max fields, so control-to-firmware expectations must be verified by codec/firmware version. Live updates require `inst->lock`; missed lock coverage would race streaming transitions. Hierarchical coding is conditionally registered for V4/V6 cores, so userspace behavior differs by hardware.

Test signals: use `v4l2-ctl --list-ctrls`, set every registered control within and outside bounds, test invalid H.264 8x8 transform/profile combinations, verify live bitrate/keyframe/LTR/header changes during streaming, and confirm volatile min-buffers returns firmware-derived values after session initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/venc_ctrls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/Kconfig

Purpose: top-level Kconfig menu entry for Raspberry Pi media platform drivers.

Important APIs/types/functions: declares a comment label and sources `drivers/media/platform/raspberrypi/pisp_be/Kconfig` and `drivers/media/platform/raspberrypi/rp1-cfe/Kconfig`.

Control flow: Kconfig inclusion only; it delegates actual symbols to child directories.

State and persistence: no runtime state. It affects kernel configuration state by making child driver options visible.

Dependencies and integration: integrated from the media platform Kconfig tree. Child symbols provide their own dependency and select clauses.

Risks: if source paths drift, Raspberry Pi drivers disappear from menuconfig/builds. Ordering is simple and has no symbol dependency between the two children.

Test signals: `make menuconfig` visibility and `make olddefconfig` parsing with `CONFIG_VIDEO_RASPBERRYPI_PISP_BE` and `CONFIG_VIDEO_RP1_CFE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/Makefile

Purpose: top-level build dispatcher for Raspberry Pi media platform driver subdirectories.

Important APIs/types/functions: unconditional `obj-y += pisp_be/` and `obj-y += rp1-cfe/` let child Makefiles decide whether to produce objects based on Kconfig symbols.

Control flow: kbuild descends into both subdirectories during the media platform build.

State and persistence: no runtime state; build graph only.

Dependencies and integration: relies on child Makefiles for `CONFIG_VIDEO_RASPBERRYPI_PISP_BE` and `CONFIG_VIDEO_RP1_CFE` object selection.

Risks: unconditional descent is normal but requires child directories to remain build-clean even when symbols are disabled.

Test signals: allmodconfig and disabled-config builds should both parse these directories without missing-object or missing-header failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/pisp_be/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/pisp_be/Kconfig

Purpose: defines the Kconfig symbol for the Raspberry Pi PiSP Back End ISP driver.

Important APIs/types/functions: `config VIDEO_RASPBERRYPI_PISP_BE` is tristate, depends on `V4L_PLATFORM_DRIVERS`, `VIDEO_DEV`, `ARCH_BCM2835 || COMPILE_TEST`, and `PM`; selects `VIDEO_V4L2_SUBDEV_API`, `MEDIA_CONTROLLER`, and `VIDEOBUF2_DMA_CONTIG`.

Control flow: selecting the symbol controls whether `pisp-be.o` is built and registered as a module/built-in.

State and persistence: kernel config state only.

Dependencies and integration: the selects match `pisp_be.c` usage of V4L2 subdevices, media controller entities/links, runtime PM, and dma-contig vb2 queues.

Risks: missing dependencies would surface as link/build errors or runtime unavailable subsystems. The `ARCH_BCM2835 || COMPILE_TEST` gate limits production visibility to Raspberry Pi platforms but keeps build testing broad.

Test signals: build with `m`, `y`, and disabled; compile-test on non-BCM platforms; modinfo should report module name `pisp-be`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/pisp_be/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/pisp_be/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/pisp_be/Makefile

Purpose: kbuild rules for the PiSP Back End driver.

Important APIs/types/functions: `pisp-be-objs := pisp_be.o` defines the module object composition. `obj-$(CONFIG_VIDEO_RASPBERRYPI_PISP_BE) += pisp-be.o` ties the object to the Kconfig symbol.

Control flow: no runtime flow; kbuild compiles `pisp_be.c` into `pisp-be.o` when enabled.

State and persistence: build graph only.

Dependencies and integration: module name matches Kconfig help. Any future split source files must be added to `pisp-be-objs`.

Risks: object-name mismatch would change module naming or break builds. Single-object composition means all driver code currently lives in `pisp_be.c`.

Test signals: `make M=drivers/media/platform/raspberrypi/pisp_be` and module load/unload smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/pisp_be/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/pisp_be/pisp_be.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/pisp_be/pisp_be.c

Purpose: implements the Raspberry Pi PiSP Back End ISP driver as a media-controller/V4L2 device with multiple video/meta nodes representing main input, TDN/stitch inputs, image outputs, TDN/stitch outputs, and configuration metadata input.

Important APIs/types/functions: `pispbe_node`, `pispbe_job_descriptor`, and `pispbe_dev` hold node, queued job, and device state. `pispbe_queue_job()` writes sanitized addresses/config to hardware. `pispbe_prepare_job()` pulls buffers from required queues and builds a job. `pispbe_schedule()` submits queued jobs when hardware is idle. `pispbe_isr()` tracks queued/running job completion through hardware started/done counters. Format negotiation uses `pispbe_find_fmt()`, `pispbe_try_format()`, and `pispbe_set_plane_params()`. Probe/remove use `pispbe_hw_init()`, `pispbe_init_devices()`, and `pispbe_destroy_devices()`.

Control flow: probe maps registers, requests IRQ, sets a 36-bit DMA mask, enables runtime PM/clock, validates hardware version, initializes media/V4L2 devices, registers a processing subdev and eight video nodes, then allocates coherent config/tile buffers. Buffer prepare copies config metadata into coherent storage and validates it against active node formats. Buffer queue appends to a node ready list, tries to prepare a complete job, then schedules hardware if possible. A valid job requires CONFIG and MAIN_INPUT plus any streaming nodes whose config enables require buffers. ISR completes running or queued jobs, stamps all involved buffers with a shared sequence/timestamp, and schedules the next job.

State and persistence: in-memory state includes `streaming_map`, per-node ready queues/formats, coherent config array, `job_queue`, `queued_job`, `running_job`, `hw_busy`, hardware counters, and sequence. Runtime PM controls the clock with autosuspend. No durable persistence exists.

Dependencies and integration: depends on V4L2, media controller, vb2 dma-contig, runtime PM, platform resources, and UAPI `pisp_be_config.h`. Media links connect each video node to the PiSP BE subdev. Format capabilities come from `pisp_be_formats.h`.

Risks: job construction can deadlock userspace if enabled config blocks do not correspond to streaming/queued buffers. Hardware lockups are explicitly guarded against by disabling invalid TDN/stitch/Bayer/RGB enables and by config size/stride checks. ISR counter mismatch handling must stay synchronized with hardware semantics where a new job can start and finish in one interrupt. Address readback failure prevents queueing but leaves the job path sensitive to hardware/IOMMU setup.

Test signals: media graph enumeration, per-node format set/get/enum, config validation failures for undersized strides and invalid tiles, multi-node streaming with optional outputs disabled/enabled, IRQ completion sequencing under back-to-back jobs, runtime PM autosuspend, and stress tests that stop one node while other nodes have queued buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/pisp_be/pisp_be.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/pisp_be/pisp_be_formats.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/pisp_be/pisp_be_formats.h

Purpose: static format capability table for the PiSP Back End driver.

Important APIs/types/functions: defines `PISPBE_MAX_PLANES`, `struct pisp_be_format`, colorspace mask helpers, `supported_formats[]`, and `meta_out_supported_formats[]`. Each image format records V4L2 FourCC, bytes-per-line alignment, bit depth, fixed-point plane factors, number of memory planes, allowed colorspaces, and default colorspace.

Control flow: no executable functions, but `pisp_be.c` iterates `supported_formats[]` for enum/try/set format and uses the table for plane sizing and address translation.

State and persistence: immutable compile-time data.

Dependencies and integration: depends on V4L2 pixel formats and PiSP compressed pixel format definitions. Supports single-plane and multiplane YUV, RGB, Bayer, unpacked Bayer, PiSP compressed Bayer/mono, greyscale, and config metadata.

Risks: plane factors use a fixed-point convention via `P3(x)`, and several entries use fractional macro arguments; mistakes directly affect buffer sizes and computed plane offsets. Colorspace masks constrain userspace negotiation. Missing formats here are invisible to all PiSP BE nodes.

Test signals: enumerate every format, try/set each format on relevant nodes, verify bytesperline alignment and sizeimage for single-plane and multiplane variants, and run DMA with non-mplane YUV formats that require derived plane addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/pisp_be/pisp_be_formats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/Kconfig

Purpose: defines the Kconfig symbol for Raspberry Pi RP1 Camera Front End capture support.

Important APIs/types/functions: `config VIDEO_RP1_CFE` is tristate, depends on `VIDEO_DEV` and `PM`, and selects `VIDEO_V4L2_SUBDEV_API`, `MEDIA_CONTROLLER`, `VIDEOBUF2_DMA_CONTIG`, and `V4L2_FWNODE`.

Control flow: selecting the symbol builds the composite `rp1-cfe` driver.

State and persistence: kernel configuration only.

Dependencies and integration: selected dependencies match the driver use of async fwnode subdev binding, media-controller graph links, V4L2 subdev streams/routing, runtime PM, and DMA-contiguous vb2 queues.

Risks: no architecture dependency is present here, so compile coverage is broad; runtime binding still depends on a matching `raspberrypi,rp1-cfe` device tree node and resources.

Test signals: compile as built-in/module, config dependency resolution, and device-tree probe on RP1 hardware with sensor endpoint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/Makefile

Purpose: kbuild object composition for the RP1 CFE driver.

Important APIs/types/functions: `rp1-cfe-objs := cfe.o csi2.o pisp-fe.o dphy.o` and `obj-$(CONFIG_VIDEO_RP1_CFE) += rp1-cfe.o`.

Control flow: kbuild links the core capture driver, CSI-2 receiver, PiSP front-end, and DPHY helper into one module/built-in object.

State and persistence: build graph only.

Dependencies and integration: object ordering is conventional; symbols exported between these local objects are declared in `cfe.h`, `csi2.h`, `pisp-fe.h`, and `dphy.h`.

Risks: missing a new source file from `rp1-cfe-objs` would cause unresolved symbols. Renaming any component must update this file and Kconfig module naming expectations.

Test signals: `make M=drivers/media/platform/raspberrypi/rp1-cfe`, allmodconfig link checks, and modinfo for `rp1-cfe`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/cfe-fmts.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/cfe-fmts.h

Purpose: central format table for RP1 CFE CSI-2 capture and PiSP FE output negotiation.

Important APIs/types/functions: `formats[]` maps V4L2 FourCC to media bus code, bit depth, CSI-2 data type, optional remap FourCCs, and flags (`META_OUT`, `META_CAP`, `FE_OUT`). Entries cover YUV, RGB, Bayer packed RAW8/10/12/14, 16-bit Bayer/mono, PiSP compressed outputs, greyscale, generic CSI-2 metadata, and FE config/stats metadata.

Control flow: no functions; lookup helpers in `cfe.c` iterate this table for ioctl validation, CSI-2 data type selection, source-pad remap/compressed code checks, and FE format filtering.

State and persistence: immutable compile-time data.

Dependencies and integration: depends on `cfe.h`, V4L2 pixel/meta formats, media bus formats, and `media/mipi-csi2.h` data type constants.

Risks: incorrect `csi_dt` will make CSI-2 channel filtering capture the wrong packets. Incorrect `remap` entries break 16-bit unpacked or PiSP compressed output modes. FE output flags restrict which formats can traverse the PiSP FE path.

Test signals: enumerate video and metadata formats on CSI2/FE nodes, route sink formats to source pads with normal/remap/compressed codes, validate FE outputs only expose `FE_OUT` formats, and capture RAW metadata data types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/cfe-fmts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/cfe-trace.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/cfe-trace.h

Purpose: tracepoint definitions for RP1 CFE, CSI-2, and PiSP FE runtime diagnostics.

Important APIs/types/functions: declares `TRACE_SYSTEM cfe`, events for returned buffers, buffer prepare/queue/schedule/complete, frame start/end, job preparation, CSI-2 IRQs, and FE IRQs. It duplicates CSI-2 status bit definitions needed for trace formatting and ends with `TRACE_INCLUDE_FILE` pointing back to this header.

Control flow: compiled into tracepoint callsites when included with `CREATE_TRACE_POINTS` in `cfe.c`; other files include it for trace event declarations.

State and persistence: tracepoints do not own driver state; emitted records are consumed by ftrace/perf infrastructure.

Dependencies and integration: depends on Linux tracepoint API and vb2 types. Events are called from `cfe.c`, `csi2.c`, and `pisp-fe.c`.

Risks: trace include path is relative and must remain valid under kernel trace generation. Format strings expose assumptions about buffer index, frame counters, and CSI-2 status bit meanings.

Test signals: kernel builds with trace events enabled, `trace-cmd list | grep cfe`, and runtime capture showing schedule, IRQ, and completion events in expected order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/cfe-trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/cfe.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/cfe.c

Purpose: main RP1 Camera Front End driver. It binds platform resources, registers the media device, CSI-2 and PiSP FE subdevices, async sensor links, and video/meta nodes for CSI-2 channels plus FE image/config/statistics paths.

Important APIs/types/functions: `cfe_device` owns the media graph, state bitmap, CSI-2 device, FE device, notifier, source subdev, and node array. `cfe_node` owns per-node vb2 queue, formats, current/next buffers, DMA queue, and video device. Format helpers include `find_format_by_code()`, `find_format_by_pix()`, `cfe_find_16bit_code()`, and `cfe_find_compressed_code()`. Scheduling is handled by `cfe_check_job_ready()`, `cfe_prepare_next_job()`, `cfe_schedule_next_csi2_job()`, and `cfe_schedule_next_pisp_job()`. Streaming uses `cfe_start_streaming()`, `cfe_start_channel()`, `cfe_stop_streaming()`, and `cfe_stop_channel()`.

Control flow: probe maps CSI-2 DMA, DPHY, MIPI config, and FE resources, requests IRQ, sets DMA limits, registers V4L2/media devices, initializes CSI-2 and FE subdevices, registers the media device, then waits for async source binding. Async completion registers video nodes and creates media links. Link notifications maintain `NODE_ENABLED` and detect CSI2-to-FE routing. Streaming validates enabled links, starts the media pipeline, marks nodes streaming, starts individual CSI-2/FE channels, enables MIPI interrupts once all enabled nodes stream, opens DPHY/CSI-2 RX, and enables remote source streams. IRQ handling collects CSI-2/FE SOF/EOF flags, updates current/next buffers, handles coalesced FS/FE cases, completes buffers, and queues the next job when every enabled node has a ready buffer.

State and persistence: all runtime state is volatile: node flags, `job_ready`, `job_queued`, current/next buffers, frame counters, timestamps, stream mask, source pad/subdev, FE channel selection, and debugfs entries. Runtime PM controls the device clock.

Dependencies and integration: depends on V4L2 async/fwnode, subdev streams/routing, media controller, vb2 dma-contig, debugfs, runtime PM, CSI-2 and FE helper modules, and Raspberry Pi PiSP FE UAPI structs.

Risks: multi-node scheduling requires all enabled nodes to have buffers; missing buffers stall the entire job. Interrupt ordering is complex because FS and FE/FE_ACK can coalesce. `cfe_calc_meta_format_size_bpl()` uses `f->fmt.pix.bytesperline` in the buffer-size expression while calculating meta sizes, a line worth targeted review/testing. Link state drives streaming validity, so stale media links can make streamon fail. Sensor `get_frame_desc` fallback assumes VC 0 and data type from current sink format.

Test signals: media graph link enable/disable, async sensor bind, route setup with multiple streams, image and metadata format validation, streamon ordering across enabled nodes, frame sync/source change events, coalesced interrupt stress, stop-streaming buffer return, debugfs register reads, and runtime suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/cfe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/cfe.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/cfe.h

Purpose: shared RP1 CFE definitions for format lookup and remapping across the core, CSI-2, and FE components.

Important APIs/types/functions: declares `enum cfe_remap_types`, format flags, `struct cfe_fmt`, `cfe_default_format`, `find_format_by_code()`, `find_format_by_pix()`, `cfe_find_16bit_code()`, and `cfe_find_compressed_code()`.

Control flow: no direct runtime flow; consumers call lookup/remap helpers implemented in `cfe.c`.

State and persistence: no mutable state. `cfe_fmt` instances are static table entries in `cfe-fmts.h`.

Dependencies and integration: includes media bus and V4L2 types. Used by `cfe.c`, `csi2.c`, and `pisp-fe.c` to keep format semantics consistent.

Risks: flags and remap enum order are ABI-internal but cross-file; changing them requires synchronized updates to the static format table and users.

Test signals: build/link coverage for helper declarations and behavioral tests where CSI-2/FE remap decisions match the format table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/cfe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/csi2.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/csi2.c

Purpose: implements the RP1 CSI-2 receiver/DMA subdevice used by CFE. It configures per-channel packet filtering, DMA buffers, optional remap/compression, interrupt decoding, error tracking, and V4L2 subdev routing/format operations.

Important APIs/types/functions: register helpers `csi2_reg_read/write()`, debugfs show functions, `csi2_isr()`, `csi2_set_buffer()`, `csi2_set_compression()`, `csi2_start_channel()`, `csi2_stop_channel()`, `csi2_open_rx()`, `csi2_close_rx()`, `csi2_pad_set_fmt()`, `csi2_set_routing()`, `csi2_init()`, and `csi2_uninit()`. Module parameter `track_csi2_errors` enables discard/overflow accounting.

Control flow: `csi2_init()` initializes error locks, probes the DPHY, creates debugfs files, initializes pads, finalizes a streams-capable V4L2 subdev, and registers it. The default subdev state creates one active sink-to-source route with `cfe_default_format`. Sink format changes are propagated to the opposite source stream. Source format changes are limited to sink code, 16-bit remap, or compressed remap. Channel start clears old state, programs frame size, VC/DT, mode, pack flags, auto-arm, and FS/FE_ACK IRQs. Buffer programming writes length/stride/high address before low address to trigger hardware double buffering.

State and persistence: state is in `csi2_device`: MMIO base, DPHY data, bus flags, per-channel line counts, subdev/pads, and optional error counters protected by `errors_lock`. Debugfs error reads snapshot and clear counters.

Dependencies and integration: depends on CFE format helpers, DPHY helper, V4L2 subdev routing, media controller, debugfs, runtime PM for register dumps, and vb2 DMA addresses supplied by the CFE core.

Risks: channel stop needs FORCE and two ADDR0 writes, indicating hardware-sensitive sequencing. Wrong VC/DT or routing can silently discard packets. Error tracking is optional and counters are cleared on debugfs read. Source multiplexing is disallowed, so route validation must match userspace expectations. `set_field()` call argument order should be reviewed because the helper parameters are named as field value then mask.

Test signals: subdev routing validation, sink/source format remap attempts, normal/remap/compressed capture, embedded metadata pack-bytes mode, start/stop mid-frame, debugfs register and error counters, and interrupt trace events for FS/FE_ACK.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/csi2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/csi2.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/csi2.h

Purpose: public interface and data model for the RP1 CSI-2 receiver component.

Important APIs/types/functions: defines channel and pad counts, `enum csi2_mode`, `enum csi2_compression_mode`, discard counter indexes, `struct csi2_device`, and function prototypes for ISR, buffer programming, compression, channel start/stop, RX open/close, init, and uninit.

Control flow: no implementation; the CFE core calls these functions during stream setup, scheduling, ISR dispatch, and teardown.

State and persistence: `struct csi2_device` stores V4L2 device pointer, MMIO base, DPHY state, bus flags, line counts, pads/subdev, and discard/overflow counters.

Dependencies and integration: includes debugfs, MMIO types, V4L2 device/subdev, and `dphy.h`. The structure is embedded in `struct cfe_device`.

Risks: constants such as `CSI2_NUM_CHANNELS` and pad indexes must stay aligned with CFE node descriptions and media links. Changes to `struct csi2_device` affect the core driver layout.

Test signals: build/link coverage and runtime validation that each CFE CSI2 node maps to the expected source pad/channel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/csi2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/dphy.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/dphy.c

Purpose: controls the DesignWare MIPI D-PHY block used by the RP1 CSI-2 receiver.

Important APIs/types/functions: low-level MMIO helpers, test-interface bit setters, `dphy_transaction()`, `dphy_set_hsfreqrange()`, `dphy_init()`, `dphy_start()`, `dphy_stop()`, and `dphy_probe()`. The HS frequency table maps Mbps limits to databook HSFREQRANGE codes.

Control flow: `dphy_start()` writes active lane count, resets/shuts down the PHY, toggles the test interface clear/clock/data lines, programs HSFREQRANGE from `dphy_rate`, releases shutdown/reset, then releases host reset. `dphy_stop()` reduces active lanes to one and asserts reset. `dphy_probe()` reads and logs the hardware version.

State and persistence: consumes mutable `dphy_data` fields `dphy_rate`, `active_lanes`, and `max_lanes` set by the CFE/CSI-2 path. No persistent state is stored.

Dependencies and integration: called from `csi2_open_rx()`, `csi2_close_rx()`, and `csi2_init()`. Relies on CFE stream setup to calculate link frequency and active lane count before starting.

Risks: out-of-range rates only log an error and still choose a table entry, which may be unsafe for bad sensor/link-frequency data. Timing sleeps and reset ordering are hardware-sensitive. Active lanes must be nonzero before `dphy_start()` because it writes `active_lanes - 1`.

Test signals: hardware stream bring-up across lane counts and link frequencies, suspend/resume cycles, invalid link frequency handling, and CSI-2 packet stability after repeated start/stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/dphy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/dphy.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/dphy.h

Purpose: shared DPHY data structure and control function declarations for the RP1 CSI-2 stack.

Important APIs/types/functions: `struct dphy_data` contains device pointer, MMIO base, selected DPHY rate, maximum lanes, and active lanes. Declares `dphy_probe()`, `dphy_start()`, and `dphy_stop()`.

Control flow: no implementation; CSI-2 code owns call sequencing.

State and persistence: state is embedded in `struct csi2_device` and updated during endpoint parsing and stream start.

Dependencies and integration: includes MMIO and integer types. Used only by `csi2.h`/`csi2.c` and `dphy.c`.

Risks: fields are trusted by `dphy_start()` without defensive clamping; callers must validate lane count and rate.

Test signals: compile coverage and stream tests confirming endpoint lane counts propagate into DPHY programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/dphy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/pisp-fe.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/pisp-fe.c

Purpose: implements the PiSP Front End subdevice used by RP1 CFE for raw stream processing, optional compression, image outputs, and statistics output.

Important APIs/types/functions: `pisp_fe_config_map[]` maps dirty flags to config struct offsets. `pisp_fe_isr()` reports SOF/EOF to the CFE core. `pisp_fe_validate_config()` checks input, output, crop, downscale, and stats safety. `pisp_fe_submit_job()` patches DMA addresses into the config, writes changed hardware config blocks, and queues the FE job. `pisp_fe_start()` and `pisp_fe_stop()` control reset/interrupt/abort. Subdev ops are implemented by `pisp_fe_init_state()`, `pisp_fe_pad_set_fmt()`, and `pisp_fe_link_validate()`.

Control flow: init registers a five-pad processing subdev: stream input, config input, output0, output1, and stats. Format state defaults to 16-bit Bayer stream/output and fixed-size config/stats pads. CFE validates FE config during buffer prepare. When a job is submitted, output and stats buffer DMA addresses are inserted, output line interrupts are computed, status is read as a barrier, required config sections are written based on dirty flags/enables, and `FE_CONTROL_QUEUE` starts the hardware. ISR latches registers, clears interrupt status, traces status, and reports SOF/EOF for source pads.

State and persistence: `pisp_fe_device` holds V4L2 device pointer, MMIO base, hardware revision, in-frame count, pads, and subdev. Per-frame config is supplied by userspace metadata buffers and copied/validated in the CFE core.

Dependencies and integration: depends on PiSP FE UAPI config/statistics headers, CFE format helpers, vb2 DMA addresses, media controller subdevs, debugfs, runtime PM, and CFE tracepoints.

Risks: config writing uses dirty flags from userspace/config buffers, so missing dirty bits can leave stale hardware state; some blocks are forced dirty when enabled to reduce that risk. Validation explicitly guards zero-sized crops/outputs that could lock hardware. `pisp_fe_pad_set_fmt()` has TODOs for propagation and validation. `pisp_fe_submit_job()` mutates the copied config with DMA addresses and clears dirty flags, so callers must not reuse shared userspace memory directly.

Test signals: FE media link validation, config buffer validation for invalid input/output/stats crops, compressed output format negotiation, job submission with output0/output1/stats combinations, FE IRQ trace events, abort/stop behavior, and register debugfs reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/pisp-fe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/pisp-fe.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/pisp-fe.h

Purpose: public interface for the RP1 PiSP Front End component.

Important APIs/types/functions: defines `enum pisp_fe_pads`, `struct pisp_fe_device`, and prototypes for ISR, config validation, job submission, start/stop, init, and uninit.

Control flow: no implementation; `cfe.c` calls these functions when scheduling FE jobs, dispatching interrupts, and managing stream lifecycle.

State and persistence: `pisp_fe_device` stores parent V4L2 device, MMIO base, hardware revision, in-frame count, media pads, and subdev.

Dependencies and integration: includes media/V4L2 subdev types and PiSP FE UAPI config definitions. The FE device is embedded in `struct cfe_device`.

Risks: pad enum indexes are used across CFE node descriptions, vb2 buffer arrays, and media links; changing them requires coordinated updates.

Test signals: build/link coverage and media graph validation that FE pads connect to expected CFE nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/pisp-fe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/Kconfig

Purpose: Kconfig menu for Renesas media platform drivers, grouped by V4L capture, mem2mem, and SDR devices.

Important APIs/types/functions: defines symbols for CEU, R-Car CSI-2, SuperH VOU, FCP, FDP1, JPU, VSP1, and R-Car DRIF, and sources subdirectory Kconfigs for `rcar-isp`, `rcar-vin`, `rzg2l-cru`, and `rzv2h-ivc`.

Control flow: configuration dependencies expose only applicable drivers for V4L platform, V4L mem2mem, or SDR platform builds. Symbols select needed helpers such as media controller, V4L2 subdev API, reset controller, vb2 dma-contig/vmalloc, V4L2 mem2mem, V4L2 fwnode, or async support.

State and persistence: kernel config state only.

Dependencies and integration: matches Renesas architecture gates (`ARCH_RENESAS`, `ARCH_SHMOBILE`, `ARCH_R7S72100`) with `COMPILE_TEST` escape hatches. Some mem2mem drivers depend on FCP availability or absence according to architecture.

Risks: Kconfig dependency errors can hide drivers or allow impossible link combinations. The ARM64/FCP conditions for FDP1/VSP1 are subtle and should be preserved when refactoring. Sourced subdirectories must remain in sync with the Makefile.

Test signals: `make olddefconfig`, allmodconfig, allyesconfig, and targeted configs for capture, mem2mem, and SDR symbols on Renesas and COMPILE_TEST platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/Makefile

Purpose: kbuild dispatcher for Renesas media platform drivers.

Important APIs/types/functions: unconditionally descends into `rcar-isp/`, `rcar-vin/`, `rzg2l-cru/`, `rzv2h-ivc/`, and `vsp1/`; conditionally builds single-object drivers for R-Car CSI-2, DRIF, CEU, FCP, FDP1, JPU, and SH VOU.

Control flow: kbuild uses `obj-y` for subdirectories and `obj-$(CONFIG_...)` for individual modules/objects based on Kconfig symbols.

State and persistence: build graph only.

Dependencies and integration: must stay aligned with `renesas/Kconfig` symbols and source filenames such as `rcar-csi2.o`, `rcar_drif.o`, `renesas-ceu.o`, `rcar-fcp.o`, `rcar_fdp1.o`, `rcar_jpu.o`, and `sh_vou.o`.

Risks: unconditional subdirectory descent requires child Makefiles to be safe for disabled configs. Filename/symbol drift causes missing objects or unused Kconfig options.

Test signals: build Renesas media drivers as modules and built-ins, allmodconfig link checks, and disabled-symbol builds to ensure unconditional subdirectories are harmless.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/Makefile -->

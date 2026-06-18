# subset-b-004158 research

Grouped research report for the requested VSP1 and Rockchip media platform files. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_pipe.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_pipe.c

Purpose: implements the common R-Car VSP1 pipeline support used by the V4L2 video node, display-list programming, and VSPX single-shot flow. It owns the supported V4L2 pixel-format tables, color-space normalization, pipeline run/stop state machine, alpha propagation into UDS, and partition calculation for hardware that must process large frames in slices.

Important APIs/functions: `vsp1_get_format_info()` maps a V4L2 fourcc to `struct vsp1_format_info`, with Gen2-only and HSIT-only extensions. `vsp1_get_format_info_by_index()` enumerates those formats for `ENUM_FMT`, optionally filtered by media-bus code. `vsp1_adjust_color_space()` fixes default/out-of-range colorspace fields and restricts non-YUV encodings to stable defaults. `vsp1_pipeline_init()`, `vsp1_pipeline_reset()`, `vsp1_pipeline_run()`, `vsp1_pipeline_stop()`, `vsp1_pipeline_ready()`, and `vsp1_pipeline_frame_end()` are the public pipeline lifecycle. `vsp1_pipeline_calculate_partition()` computes one slice and calls entity partition callbacks in reverse pipeline order.

Control flow and state: a pipeline starts in `VSP1_PIPELINE_STOPPED`; `vsp1_pipeline_run()` writes `VI6_CMD_STRCMD` for the output WPF and marks it running under `pipe->irqlock`. Stop either resets the WPF when a LIF display output is present or transitions to `STOPPING` and waits up to 500 ms for frame-end handling to mark the pipe stopped. Frame end notifies the display-list manager, HGO/HGT statistics units, the optional pipeline callback, and increments `sequence`.

Dependencies/integration: this file is central glue for `vsp1_video.c`, `vsp1_rpf.c`, `vsp1_wpf.c`, `vsp1_uds.c`, `vsp1_sru.c`, and VSPX. It depends on V4L2 media-bus definitions, media graph entities, VSP1 display-list helpers, and VI6 register macros. Partition correctness depends on entity list order matching data-flow order.

Risks and test signals: format table mistakes manifest as wrong register format, bytes-per-pixel, plane count, or swap flags. Stop handling is timing sensitive around frame-end interrupts and DL commits. Partition risks include off-by-one last slices and too-small final partitions. Test with V4L2 format enumeration, RGB/YUV CSC combinations, multi-planar YUV, alpha scaling through UDS, streaming stop timeouts, suspend/resume, and large widths requiring multiple partitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_pipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_pipe.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_pipe.h

Purpose: declares the shared VSP1 pipeline data model and exported helpers used by VSP1 entities and video nodes. It defines video format metadata, pipeline state values, partition rectangles, and the main `struct vsp1_pipeline`.

Important APIs/types: `struct vsp1_format_info` carries the contract between V4L2 fourccs, media-bus codes, VI6 hardware formats, swap flags, plane counts, bpp, Y/C and U/V swaps, subsampling, and alpha-channel presence. `enum vsp1_pipeline_state` describes stopped/running/stopping. `struct vsp1_partition` stores per-slice rectangles for RPFs, UDS sink/source, SRU, and WPF. `struct vsp1_pipeline` embeds a `media_pipeline`, IRQ lock, waitqueue, kref, stream and buffer readiness counters, entity pointers, ordered entity list, cached stream display-list body, interlace flag, partition table, and underrun count.

Control flow/state: the header expresses two locking domains: `irqlock` for state and buffer readiness in IRQ-sensitive paths, and `lock` for use count/stream count. The `frame_end` callback lets `vsp1_video.c` and `vsp1_vspx.c` install different completion behavior over the same pipeline primitive.

Dependencies/integration: included by nearly all VSP1 blocks. It forward-declares display-list and RWPF types while depending on Linux list/kref/wait/spinlock and media entity types. The debug macro wraps dynamic debug when configured and compiles away otherwise.

Risks and test signals: changes to `struct vsp1_pipeline` affect many files and IRQ paths. Partition fields must stay synchronized with entity callbacks. Test by compiling all VSP1 configurations, running media graph setup/teardown, and exercising multi-input, UDS/SRU, LIF, interlaced, and VSPX paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_pipe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_regs.h

Purpose: provides the VI6/VSP1 register address and bitfield macro contract used by the Renesas VSP1 driver. It is a pure header with no runtime state; correctness is determined by matching the hardware register map.

Important definitions: general control macros cover `VI6_CMD`, reset/status, WPF interrupts, display interrupts, and line counters. Display-list control definitions cover DL enable, headers, swap, extended command control, AUTOFLD interrupt flags, and body sizes. RPF macros describe source size, input format, byte swaps, location, alpha, masks/color-keying, strides, DMA addresses, multiplier alpha, Gen4 extended input formats, and dithering. WPF macros describe source selection, clipping, output format, rotation, destination stride/address, and writeback. UIF, DPR routing, SRU, UDS, LUT/CLU/HST/HSI, BRU/BRS blending, HGO/HGT statistics, LIF, security, version, CLUT/LUT/CLU tables, and hardware format IDs are also covered.

Control flow/state: there is no control flow, but macro composition drives all display-list bodies and direct MMIO writes in sibling files. Offset macros such as `VI6_RPF_OFFSET`, `VI6_WPF_OFFSET`, `VI6_UIF_OFFSET`, and `VI6_UDS_OFFSET` are used to address indexed hardware instances.

Dependencies/integration: consumed by `vsp1_pipe.c` format tables, RPF/WPF/UDS/SRU/UIF programming, display-list management, route setup, and interrupt/status handling. It relies on kernel `BIT()` and standard integer arithmetic in callers.

Risks and test signals: bitfield shifts and masks are high blast-radius: a single bad value can corrupt image layout, routes, interrupts, DMA addresses, or CSC. Particular risk areas are Gen4 extended RPF formats, WPF writeback, indexed offsets, and DPR node IDs. Test signals include register trace comparison against known-good kernels, streaming across every supported block, color/plane swap validation, and hardware version detection on Gen2/Gen3/Gen4/RZ-G2L variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_rpf.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_rpf.c

Purpose: implements the Read Pixel Formatter entity, the VSP1 block that reads input image planes from memory or VSPX/IIF input and feeds the pipeline. It programs input strides, formats, color conversion, alpha handling, crop windows, plane addresses, interlaced AUTOFLD commands, and partition-specific reads.

Important APIs/functions: `vsp1_rpf_create()` allocates and registers an RPF subdevice. Entity callbacks are `rpf_configure_stream()`, `rpf_configure_frame()`, `rpf_configure_partition()`, and `rpf_partition()`. `vsp1_rpf_configure_autofld()` fills a pre extended display-list command for interlaced top/bottom field addresses. `vsp1_rpf_write()` writes RPF-indexed registers into a display-list body.

Control flow/state: stream configuration uses `rpf->fmtinfo`, `rpf->format`, active sink/source pad formats, and pipeline context. It writes `VI6_RPF_SRCM_PSTRIDE`, `VI6_RPF_INFMT`, `VI6_RPF_DSWAP`, optional Gen4 `EXT_INFMT*`, output location through BRx compose rectangles, alpha selection, multiplier setup, and disables mask/color-keying. Frame configuration writes current alpha and propagates it to UDS. Partition configuration starts from `rpf->mem`, applies crop and interlace adjustments, computes per-plane DMA offsets, manually swaps U/V addresses for Gen3+ 3-planar swapped formats, then writes addresses or AUTOFLD data.

Dependencies/integration: depends on `vsp1_rwpf` for shared subdevice state, `vsp1_video` for queued buffer memory, `vsp1_pipe` for alpha/partition helpers, `vsp1_dl` for display lists, and VI6 register macros. It integrates with BRU/BRS through `brx_input` and with VSPX by skipping memory-output-only configuration when `pipe->iif` is present.

Risks and test signals: DMA address calculations are sensitive to crop alignment, subsampling, bytesperline, and interlaced field layout. Gen3 three-plane U/V swap and Gen4 extended input formats are variant-sensitive. Test with all supported planar/semi-planar/packed formats, cropped YUV with even alignment, alpha and premultiplied-alpha inputs, interlaced pipelines, BRx positioning, and VSPX raw/config transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_rpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_rwpf.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_rwpf.c

Purpose: implements the shared V4L2 subdevice operations and common controls for RPF and WPF pixel formatter entities. It handles media-bus code enumeration, frame-size enumeration, pad format propagation, RPF crop selection, and the alpha component control.

Important APIs/functions: `vsp1_rwpf_subdev_ops` exposes core and pad operations. `vsp1_rwpf_enum_mbus_code()` and `vsp1_rwpf_enum_frame_size()` describe RWPF source-pad capabilities, including the HSV no-conversion rule. `vsp1_rwpf_set_format()` clamps sink dimensions, normalizes colorspace fields, propagates sink to source, and accounts for WPF rotation. `vsp1_rwpf_get_selection()` and `vsp1_rwpf_set_selection()` implement RPF-only sink crop. `vsp1_rwpf_init_ctrls()` installs `V4L2_CID_ALPHA_COMPONENT`.

Control flow/state: sink format is the authoritative input format. On source pads, only code/encoding/quantization may change for RGB/YUV conversion, and V4L2 requires `V4L2_MBUS_FRAMEFMT_SET_CSC` before honoring requested encoding/quantization. For RPF crop, YUV rectangles are aligned to even coordinates/sizes, bounded to the sink format, then propagated to the source dimensions.

Dependencies/integration: common code is used by `vsp1_rpf_create()` and `vsp1_wpf_create()`. It relies on `vsp1_entity_get_state()`, `vsp1_entity_adjust_color_space()`, V4L2 subdev state helpers, and `vsp1_video` for WPF rotation queue-busy constraints.

Risks and test signals: accepting odd YUV crops can lead to invalid hardware, so link validation and video format alignment are important test signals. Source-pad CSC rules can surprise userspace. Rotation changes affect source dimensions and must be rejected while buffers are allocated. Test pad format set/get/try flows, HSV source restrictions, RGB/YUV CSC negotiation, RPF crop bounds/defaults, and alpha-control propagation into RPF/WPF programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_rwpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_rwpf.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_rwpf.h

Purpose: declares the shared Read/Write Pixel Formatter model used by VSP1 RPF and WPF implementations and their video-node wrappers.

Important APIs/types: defines pad indices `RWPF_PAD_SINK`/`RWPF_PAD_SOURCE`, minimum dimensions, `struct vsp1_rwpf_memory` with up to three DMA plane addresses, and `struct vsp1_rwpf`. The RWPF structure embeds a `vsp1_entity`, V4L2 control handler, optional video node, active multi-plane format, format info, BRx input index, alpha, alpha multiplier, output format, flip/rotation state with spinlock and controls, current memory addresses, writeback flag, and WPF display-list manager.

Control flow/state: state is runtime-only and split between media-subdev state, queued video buffer memory, and controls. `flip.pending` is updated by controls; `flip.active` is latched per frame by WPF programming. `mem` is updated when VB2 queues select the next buffer.

Dependencies/integration: included by RPF/WPF/RWPF common code, video node code, VSPX, and pipeline helpers. It exposes `vsp1_rpf_create()`, `vsp1_wpf_create()`, `vsp1_wpf_stop()`, `vsp1_rwpf_init_ctrls()`, and `vsp1_rwpf_subdev_ops`.

Risks and test signals: the structure is shared across IRQ, streaming, and control paths, so locking discipline matters. Test signals include races between controls and streaming, buffer queue updates, writeback one-shot operation, and RPF/WPF cleanup through `vsp1_entity_destroy()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_rwpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_sru.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_sru.c

Purpose: implements the Super Resolution Unit entity, a scaler/sharpener that can pass through or upscale by 2x in both dimensions. It exposes a V4L2 subdevice with an intensity control and programs SRU parameters into display lists.

Important APIs/functions: `vsp1_sru_create()` allocates/registers the SRU. `sru_set_format()` and `sru_try_format()` clamp pad formats and propagate sink to source while enforcing no format conversion. `sru_enum_frame_size()` advertises source sizes as either same-as-input or 2x when the input is small enough. `sru_configure_stream()` writes `VI6_SRU_CTRL0/1/2` based on input format, upscale mode, and intensity. `sru_max_width()` and `sru_partition()` integrate the SRU into the partition algorithm.

Control flow/state: the custom `V4L2_CID_VSP1_SRU_INTENSITY` stores `sru->intensity` from 1 to 6, indexing fixed parameter tables. Source pad sizing compares requested output area against input area and chooses either no scale or exact 2x. Partition propagation halves the downstream window when SRU x2 is active.

Dependencies/integration: uses VSP1 entity helpers, V4L2 subdev state, `vsp1_pipe` partition state, and `vsp1_regs` SRU register fields. It supports ARGB8888 and AYUV media-bus codes and registers as `MEDIA_ENT_F_PROC_VIDEO_SCALER`.

Risks and test signals: the area threshold in `sru_try_format()` controls whether scaling is enabled and can affect user expectations. Partition limits reserve overlap room, so large-frame slicing should be tested with and without scaling. Validate all six intensity settings, RGB/YUV inputs, pad propagation, maximum-size boundaries, and visual output for 2x upscale.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_sru.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_sru.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_sru.h

Purpose: declares the SRU subdevice structure and constructor for the VSP1 Super Resolution Unit.

Important APIs/types: defines `SRU_PAD_SINK` and `SRU_PAD_SOURCE`, `struct vsp1_sru` with embedded `vsp1_entity`, V4L2 control handler, and current `intensity`, `to_sru()` for container conversion, and `vsp1_sru_create()`.

Control flow/state: state is runtime-only and stored in the subdevice state plus the integer intensity control. No persistence is defined.

Dependencies/integration: included by SRU implementation and any VSP1 device initialization code that creates optional SRU hardware. It depends on media entity, V4L2 controls/subdev, and `vsp1_entity.h`.

Risks and test signals: header changes affect entity initialization and control access. Compile-test configurations with and without SRU support and exercise control setup/cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_sru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_uds.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_uds.c

Purpose: implements the Up/Down Scaler entity. It provides V4L2 pad negotiation for ARGB/YUV scaling, computes fixed-point scaling ratios and passband filter widths, configures alpha scaling, and participates in partitioned frame processing.

Important APIs/functions: `vsp1_uds_create()` registers an indexed UDS subdevice. `vsp1_uds_set_alpha()` programs the fixed alpha output value used when alpha scaling is disabled. `uds_output_limits()`, `uds_compute_ratio()`, and `uds_passband_width()` implement hardware scaling calculations. `uds_set_format()`/`uds_try_format()` handle pad format negotiation. Entity callbacks configure stream registers, clip per partition, report max width, and map downstream partition windows back to UDS input windows.

Control flow/state: sink format is clamped to 4..8190 and color-normalized. Source format keeps the sink code/colorspace and clamps width/height to limits derived from U4.12 ratio range. `uds_configure_stream()` computes horizontal/vertical scale, disables multitap when alpha scaling and strong downscale conflict, writes control, passband, and scale registers. `uds_partition()` maps output window coordinates to input coordinates and updates the upstream window.

Dependencies/integration: driven by `vsp1_video_setup_pipeline()` for `scale_alpha` based on upstream alpha/BRx state and by `vsp1_pipeline_propagate_alpha()` for fixed alpha. It depends on VSP1 display-list writes, V4L2 subdev state, and partition helpers.

Risks and test signals: `uds_compute_ratio()` is explicitly approximate, so edge scaling ratios can be sensitive. Division assumes valid nonzero output dimensions enforced by format constraints. Test min/max sizes, strong downscale with alpha, RGB/YUV propagation, passband values, multi-partition scaling, and UDS after BRU/BRS where alpha should be fixed at 255.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_uds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_uds.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_uds.h

Purpose: declares the VSP1 UDS entity interface.

Important APIs/types: defines `UDS_PAD_SINK` and `UDS_PAD_SOURCE`, `struct vsp1_uds` with embedded `vsp1_entity` and `scale_alpha` flag, `to_uds()` conversion helper, `vsp1_uds_create()`, and `vsp1_uds_set_alpha()`.

Control flow/state: `scale_alpha` is set by pipeline setup from upstream alpha availability and influences stream programming. The rest of state lives in V4L2 subdevice pad formats.

Dependencies/integration: included by `vsp1_uds.c`, `vsp1_pipe.c`, and `vsp1_video.c`. It needs media entity/subdev definitions and `vsp1_entity.h`.

Risks and test signals: API risk is mainly around `scale_alpha` semantics and alpha propagation from RPF/BRx. Test UDS pipelines with alpha formats and with BRU/BRS before UDS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_uds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_uif.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_uif.c

Purpose: implements the User Logic Interface entity, used here as a statistics/CRC window block. It exposes a V4L2 subdevice with crop selection, programs DISCOM comparison registers, and provides a function to read the current CRC.

Important APIs/functions: `vsp1_uif_create()` allocates/registers an indexed UIF as `uif.4` or `uif.5` because datasheets name instances that way. `vsp1_uif_get_crc()` reads `VI6_UIF_DISCOM_DOCMCCRCR`. `uif_get_selection()` and `uif_set_selection()` implement sink-pad crop bounds/default/current selection. `uif_configure_stream()` writes DISCOM mode, crop origin/size, and compare enable.

Control flow/state: on create, `soc_device_match()` detects r8a7796 and enables `m3w_quirk`; stream programming halves horizontal crop coordinates/sizes for that SoC. The crop rectangle is clamped to the active sink format and stored in V4L2 subdev state. There is no persistent storage.

Dependencies/integration: depends on VSP1 entity/display-list helpers, V4L2 subdev state, sys_soc matching, and VI6 UIF registers. It integrates into media graphs as a statistics entity and may be read by higher-level display validation/statistics paths.

Risks and test signals: the M3-W coordinate quirk is hardware-specific and easy to regress. Crop constraints use unsigned clamping against `format->width - 1`/`height - 1`, so valid format dimensions are assumed. Test CRC readback, crop set/get/bounds, r8a7796 horizontal coordinate behavior, and media graph routing with UIF instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_uif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_uif.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_uif.h

Purpose: declares the UIF entity structure and public functions.

Important APIs/types: defines `UIF_PAD_SINK`, `UIF_PAD_SOURCE`, `struct vsp1_uif` with embedded `vsp1_entity` and `m3w_quirk`, `to_uif()`, `vsp1_uif_create()`, and `vsp1_uif_get_crc()`.

Control flow/state: `m3w_quirk` is set at creation based on SoC matching and affects stream configuration. CRC access is direct register read.

Dependencies/integration: included by UIF implementation and device setup code; depends on `vsp1_entity.h`.

Risks and test signals: callers need a valid subdevice and powered hardware for CRC reads. Compile and runtime-test with UIF-enabled SoCs and verify crop/CRC behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_uif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_video.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_video.c

Purpose: implements the VSP1 V4L2 video nodes and memory-to-memory streaming pipeline control. It bridges video devices, videobuf2 queues, media-controller graph validation, display-list execution, buffer completion, partition setup, and suspend/resume behavior.

Important APIs/functions: `vsp1_video_create()` registers an input/output video node for an RPF/WPF. IOCTL handlers implement querycap, enum/get/try/set format, streamon, and VB2 buffer operations. `vsp1_video_pipeline_build()` walks the media graph and builds a `vsp1_pipeline`; `vsp1_video_setup_pipeline()` computes partitions, UDS alpha policy, and cached stream configuration. `vsp1_video_pipeline_run()` builds and commits per-frame display-list chains, including multiple partitions. `vsp1_video_pipeline_frame_end()` completes all current buffers, updates state, and restarts if ready. `vsp1_video_suspend()` and `vsp1_video_resume()` stop/reconfigure running pipelines.

Control flow/state: open gets a device reference; streamon allocates/gets a pipeline under the media graph lock, starts a media pipeline, verifies remote subdev format, then calls `vb2_streamon()`. Buffers are prepared with DMA addresses, queued on `irqqueue`, and the first queued buffer marks the corresponding `pipe->buffers_ready` bit. The last stream to start configures the whole pipeline; frame-end IRQ completion returns current buffers to VB2, selects next queued buffers, marks the pipeline stopped, and immediately re-runs if all buffers are ready and no stop is pending.

Dependencies/integration: uses V4L2, media-controller graph walking, videobuf2 DMA-contig memory, VSP1 entity operations, display-list manager, RPF/WPF structures, BRx/HGO/HGT/UDS helpers, and pipeline state from `vsp1_pipe.c`.

Risks and test signals: concurrency spans media graph locks, queue mutexes, `video->irqlock`, and `pipe->irqlock`. Risk areas include start-streaming races across multiple video nodes, incomplete display-list chains for partitions, format mismatch returning `-EPIPE`, stop timeout, suspend while streaming, and buffer release on errors. Test with multi-input pipelines, BRU/BRS branches, UDS/SRU partitioning, capture/output format negotiation, DMABUF/MMAP queues, queue underrun/requeue, streamoff while busy, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_video.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_video.h

Purpose: declares VSP1 video-node and VB2-buffer structures plus lifecycle helpers.

Important APIs/types: `struct vsp1_vb2_buffer` wraps `vb2_v4l2_buffer`, an IRQ queue list node, and `vsp1_rwpf_memory` DMA addresses. `struct vsp1_video` stores the owning VSP1 device, RWPF, `video_device`, buffer type, media pad, queue mutex, pipeline index, VB2 queue, IRQ lock, and queued buffers. It declares `vsp1_video_suspend()`, `vsp1_video_resume()`, `vsp1_video_create()`, and `vsp1_video_cleanup()`.

Control flow/state: `pipe_index` maps each video node to a bit in `pipe->buffers_ready`; output WPF uses index 0 and RPF inputs use incremented indices. `irqqueue` holds buffers available to the hardware and is protected by `irqlock`.

Dependencies/integration: included by RPF/WPF/RWPF and video implementation. It depends on videobuf2-v4l2 and `vsp1_rwpf.h`.

Risks and test signals: ABI-internal structure changes affect VB2 buffer sizing and queue conversion helpers. Test queue setup/prepare/complete paths and ensure buffer structure size matches `video->queue.buf_struct_size`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_vspx.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_vspx.c

Purpose: implements Gen4 VSPX support and exports an ISP-facing API from `include/media/vsp1.h`. It builds a fixed single-shot RPF0 -> IIF -> WPF0 pipeline for transferring optional ConfigDMA parameter buffers and RAW image buffers for the ISP.

Important APIs/functions: exported GPL symbols include `vsp1_isp_init()`, `vsp1_isp_get_bus_master()`, `vsp1_isp_alloc_buffer()`, `vsp1_isp_free_buffer()`, `vsp1_isp_start_streaming()`, `vsp1_isp_stop_streaming()`, `vsp1_isp_job_prepare()`, `vsp1_isp_job_run()`, and `vsp1_isp_job_release()`. Internal helpers map ISP formats to VSP1 formats (`vsp1_vspx_rwpf_set_subdev_fmt()`), configure RPF0 for a transfer (`vsp1_vspx_pipeline_configure()`), and handle frame-end callbacks. `vsp1_vspx_init()` creates the fixed pipeline.

Control flow/state: `struct vsp1_vspx_pipeline` embeds a `vsp1_pipeline`, one static partition, a mutex for start/stop sequences, a spinlock-protected `enabled` flag for IRQ/job-run interaction, and caller callback data. Start obtains a VSP1 runtime reference, verifies WPF0 is idle, and sets enabled. Job prepare allocates display-list(s), configures IIF/WPF routing, optionally adds a ConfigDMA transfer if pair count is more than 16, configures RAW transfer, and chains lists. Job run refuses busy/stopped hardware, commits the display list, clears ownership of `job->dl`, and starts the pipeline under `pipe->irqlock`. Stop disables the flag, stops the pipeline, resets WPF0 DLM, and drops the device reference.

Dependencies/integration: depends on RPF/WPF/IIF entities, display-list manager, runtime PM via `vsp1_device_get/put`, DMA coherent allocation through the FCPX/bus-master device, V4L2 pixel formats, and ISP-provided job descriptors.

Risks and test signals: the API is IRQ-context aware, so the spinlock/mutex split is important. Pair-count validation exists because 16 or fewer ConfigDMA pairs can corrupt/freeze VSPX. Test start/stop idempotence, busy WPF0 detection, stopped-job rejection, display-list release ownership, ConfigDMA plus image chains, RAW formats GREY/Y10/Y12/Y16, callback invocation, and cleanup after prepared-but-unrun jobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_vspx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_vspx.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_vspx.h

Purpose: declares the internal VSPX initialization and cleanup hooks for the VSP1 device driver.

Important APIs/types: includes `vsp1.h` and declares `vsp1_vspx_init(struct vsp1_device *vsp1)` and `vsp1_vspx_cleanup(struct vsp1_device *vsp1)`.

Control flow/state: no state is defined here; implementation allocates and initializes `vsp1->vspx`.

Dependencies/integration: used by VSP1 probe/remove paths when Gen4 VSPX support is present. The public ISP API is exported from the C file through `include/media/vsp1.h`, not this internal header.

Risks and test signals: compile-time integration depends on `struct vsp1_device` visibility. Test device probe/remove on VSPX-capable hardware and configurations where VSPX is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_vspx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_wpf.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_wpf.c

Purpose: implements the Write Pixel Formatter entity, the VSP1 output block that writes processed frames to memory, feeds display pipelines, handles writeback, and applies WPF0 flip/rotation controls.

Important APIs/functions: `vsp1_wpf_create()` allocates/registers WPF instances and creates a display-list manager. `vsp1_wpf_stop()` disables WPF interrupts and sources directly during stream stop. Control helpers initialize VFLIP/HFLIP/ROTATE where supported and update pending flip state. Entity callbacks configure stream, frame, partition, max width, destruction, and partition mapping. `wpf_configure_writeback_chain()` builds a chained display list to disable one-shot writeback after a frame.

Control flow/state: rotation changes that swap width/height are rejected while VB2 buffers are busy. Stream configuration writes output format, stride, byte swap, optional rotation memory config, CSC mode, source RPF/virtual source selection, interrupts, and writeback enable. Per frame, pending flip bits are latched into active bits and merged into `VI6_WPF_OUTFMT` with alpha. Partition configuration clips output size, returns early for display-only LIF paths without writeback, computes destination plane addresses with partition offset, rotation, H/V flip, subsampling, and Gen3 U/V swap, then clears `wpf->writeback` because writeback is one-shot.

Dependencies/integration: shares `vsp1_rwpf` state, uses VSP1 display-list manager, pipeline and partition helpers, V4L2 controls, WPF register macros, and feature flags for H/V flip availability. It is the output side used by `vsp1_video.c` and VSPX.

Risks and test signals: output address arithmetic is complex and sensitive to rotation/flip/subsampling/partition combinations. Writeback must be disabled safely to avoid memory corruption. WPF0-only flip feature checks vary by SoC. Test all rotation values, horizontal/vertical flip combinations, multi-planar YUV, rotated partition widths, LIF display pipeline with and without writeback, Gen2 vs Gen3 max sizes, and stream stop cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_wpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/Kconfig

Purpose: top-level Kconfig include file for Rockchip media platform drivers.

Important content: emits the menu comment "Rockchip media platform drivers" and sources the per-driver Kconfig files for RGA, RK CIF, RKISP1, and RKVDEC.

Control flow/state: no runtime behavior or persisted state; it only influences kernel configuration menu visibility and dependency resolution.

Dependencies/integration: included by the parent media platform Kconfig. It delegates actual option definitions to child directories.

Risks and test signals: path mistakes break Kconfig traversal and hide drivers. Test with `make menuconfig`/`olddefconfig` and config fragments enabling Rockchip media drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/Makefile

Purpose: top-level Rockchip media platform build dispatch.

Important content: unconditionally descends into `rga/`, `rkcif/`, `rkisp1/`, and `rkvdec/` via `obj-y`; each subdirectory Makefile gates objects on its own Kconfig symbols.

Control flow/state: no runtime state; it controls kbuild traversal.

Dependencies/integration: relies on child Makefiles defining module/object rules. It is paired with the top-level Rockchip Kconfig includes.

Risks and test signals: missing child directories or bad object names cause build failures. Test with all Rockchip media configs disabled/enabled and with `COMPILE_TEST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/Kconfig

Purpose: defines the `VIDEO_ROCKCHIP_RGA` configuration option for the Rockchip Raster 2D Graphics Acceleration Unit V4L2 mem2mem driver.

Important content: the option is tristate, depends on `V4L_MEM2MEM_DRIVERS`, `VIDEO_DEV`, and `ARCH_ROCKCHIP || COMPILE_TEST`, and selects `VIDEOBUF2_DMA_SG` plus `V4L2_MEM2MEM_DEV`. Help text identifies accelerated operations such as drawing, scaling, rotation, BitBLT, alpha blending, and blur/sharpness, although the driver implementation in this subset focuses on BitBLT-style transform.

Control flow/state: no runtime behavior; controls whether `rockchip-rga.o` is built in or as a module.

Dependencies/integration: sourced by the Rockchip platform Kconfig and paired with `rga/Makefile`.

Risks and test signals: dependency drift can allow builds without required V4L2/VB2 support. Test `allyesconfig`, `allmodconfig`, and `COMPILE_TEST` across non-Rockchip architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/Makefile

Purpose: kbuild rules for the Rockchip RGA driver.

Important content: builds `rockchip-rga.o` from `rga.o`, `rga-hw.o`, and `rga-buf.o` when `CONFIG_VIDEO_ROCKCHIP_RGA` is enabled.

Control flow/state: no runtime behavior. The object grouping defines the module link unit and internal symbol visibility.

Dependencies/integration: used by the parent Rockchip Makefile. Source files share `rga.h` and `rga-hw.h`.

Risks and test signals: missing object entries create unresolved symbols such as `rga_qops` or `rga_hw_start`. Test module and built-in builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/rga-buf.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/rga-buf.c

Purpose: implements videobuf2 queue operations and per-buffer RGA MMU descriptor preparation for the Rockchip RGA V4L2 mem2mem driver.

Important APIs/functions: exports `rga_qops`. `rga_queue_setup()` validates plane counts/sizes. `rga_buf_init()` allocates a coherent descriptor table sized to the frame size in pages. `rga_buf_prepare()` validates fields, sets payloads, fills descriptors from each scatter-gather DMA page, computes per-plane offsets, and stores Y/U/V offsets in `struct rga_vb_buffer`. `rga_buf_queue()` queues buffers into the V4L2 mem2mem context. Streaming start/stop handle runtime PM and return pending buffers on failure/stop.

Control flow/state: each VB2 buffer owns a coherent `rga_dma_desc` array and DMA address consumed by hardware command programming. For multi-planar and single-memory multi-component formats, offsets are derived either from descriptor table position or from frame geometry. Output buffers must be progressive (`V4L2_FIELD_NONE`).

Dependencies/integration: depends on `videobuf2-dma-sg`, V4L2 mem2mem queue helpers, runtime PM, SG DMA iterators, `rga_get_frame()`, and `rga-hw.c` command programming that consumes descriptor DMA addresses and offsets.

Risks and test signals: `fill_descriptors()` checks `n_desc > max_desc`, so boundary behavior at exactly max descriptors deserves attention. Plane offset calculations assume format geometry and `uv_factor` match V4L2 format layout. Test MMAP/DMABUF queues, SG buffers crossing many pages, NV12/NV12M/YUV planar formats, invalid field values, stream start PM failure, and stop returning queued buffers with error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/rga-buf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/rga-hw.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/rga-hw.c

Purpose: converts an `rga_ctx` plus queued source/destination buffers into an RGA hardware command buffer and starts execution.

Important APIs/functions: `rga_hw_start()` is the exported hardware entry point. Internal helpers compute scaling (`rga_get_scaling()`), crop/rotation/mirror address offsets (`rga_get_addr_offset()`, `rga_lookup_draw_pos()`), set source/source1/destination MMU descriptor bases, program transform information, source/destination base offsets, render mode, and command buffer address. `rga_cmd_set()` assembles the command buffer and syncs it for device access.

Control flow/state: command setup clears the shared command buffer, writes descriptor table addresses shifted by four bits, enables MMU control bits, disables alpha blending, computes CSC only when input/output colorspace families differ, applies H/V flip and 0/90/180/270 rotation, swaps scaling destination dimensions for 90/270 rotation, programs virtual strides and active sizes, writes base offsets for cropped source and rotated/mirrored destination, then kicks registers `RGA_SYS_CTRL`, `RGA_INT`, and `RGA_CMD_CTRL`.

Dependencies/integration: called from `device_run()` in `rga.c` under `ctrl_lock` with `rga->curr` set. It uses `rga.h` context/frame/buffer structures and bitfield unions/register macros from `rga-hw.h`.

Risks and test signals: address-offset math is highly sensitive for YUV subsampling, rotation, and mirroring. A version workaround adjusts source dimensions for old hardware around 90/270 rotation. CSC mode uses input or output colorspace depending on conversion direction. Test RGB->RGB, YUV->RGB, RGB->YUV, scaling up/down, all rotations/flips, nonzero crop/compose, old RGA version values, and DMA sync correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/rga-hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/rga-hw.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/rga-hw.h

Purpose: declares Rockchip RGA hardware limits, register offsets, field values, format IDs, and bitfield unions used to build command buffers.

Important definitions: size limits include min/default/max width and height plus `RGA_TIMEOUT`. Register macros cover system, command, interrupt, MMU, version, source/destination base addresses, virtual/active sizes, scaling factors, colors, alpha/fading/pattern/ROP, and MMU descriptor bases. Format macros define RGB/YUV/palette IDs and helpers `RGA_COLOR_FMT_IS_YUV()`/`RGA_COLOR_FMT_IS_RGB()`. Unions model `RGA_MODE_CTRL`, source/destination info, virtual/active info, scale factors, transparency, alpha controls, fading, and pattern registers.

Control flow/state: no runtime state; unions are local packing helpers used by `rga-hw.c` to write 32-bit command-buffer words.

Dependencies/integration: included by all RGA source files. Values must match hardware and the driver format table in `rga.c`.

Risks and test signals: C bitfield layout can be compiler/endianness sensitive in general, though this driver relies on target layout. Bad register values affect every transform. Test by comparing command buffer dumps to known-good hardware programming and compiling across supported architectures for warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/rga-hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/rga.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/rga.c

Purpose: implements the Rockchip RGA platform driver and V4L2 mem2mem device. It handles probe/remove, runtime PM, V4L2 file operations/ioctls, format and selection management, controls, interrupt completion, and mem2mem job dispatch.

Important APIs/functions: `device_run()` selects the next source/destination buffers and calls `rga_hw_start()`. `rga_isr()` acknowledges interrupts, completes buffers, copies metadata, advances sequences, and finishes the mem2mem job. `queue_init()` initializes output/capture VB2 queues. `rga_setup_ctrls()` installs HFLIP, VFLIP, ROTATE, and BG_COLOR controls. IOCTL helpers enumerate formats, get/try/set formats, and get/set crop/compose selections. `rga_probe()` parses DT resources, initializes V4L2/mem2mem/video devices, reads hardware version, allocates the command buffer, and registers `/dev/video*`.

Control flow/state: each open file gets an `rga_ctx` with default input/output frames and an m2m context. Format set is rejected while the corresponding queue is busy, stores frame geometry/stride/size/colorspace, and resets crop. Selection set validates positive in-bounds crop/compose rectangles with min dimensions. Runtime PM enables clocks on streaming start and during version read. `rga->curr` tracks the running context until IRQ completion clears it.

Dependencies/integration: depends on platform resources, reset controls named `core`/`axi`/`ahb`, clocks `sclk`/`aclk`/`hclk`, 32-bit DMA mask, V4L2 mem2mem, VB2 DMA-SG queue ops from `rga-buf.c`, and hardware programming in `rga-hw.c`.

Risks and test signals: interrupt handling assumes one current job and a done bit `0x04`. Probe error unwinding must release V4L2, mem2mem, video, PM, and DMA resources correctly. Format/crop validation is simple and may not enforce every hardware alignment constraint. Test probe/remove deferral/errors, runtime suspend/resume clocks, IRQ completion, streamon/off, format changes while busy, all supported formats, crop/compose bounds, controls under load, and 32-bit DMA restrictions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/rga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/rga.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/rga.h

Purpose: declares the internal data structures and helpers shared by the Rockchip RGA V4L2 driver, buffer code, and hardware command code.

Important APIs/types: `struct rga_fmt` maps V4L2 fourcc to depth, subsampling factors, color swap, and hardware format. `struct rga_frame` stores dimensions, colorspace, crop, format, V4L2 pix format, stride, and total size. `struct rga_ctx` is per-file state with m2m file handle, input/output frames, controls, sequences, transform controls, and fill color. `struct rockchip_rga` is device-wide state with V4L2/m2m/video devices, MMIO, clocks, version, mutex, control spinlock, current context, and command buffer. `struct rga_vb_buffer` extends VB2 buffers with RGA MMU descriptors and plane offsets.

Control flow/state: `file_to_rga_ctx()` and `vb_to_rga()` provide container conversion. Inline `rga_write()`, `rga_read()`, and `rga_mod()` encapsulate MMIO. `rga_get_frame()`, `rga_qops`, and `rga_hw_start()` are cross-file entry points.

Dependencies/integration: included by `rga.c`, `rga-buf.c`, and `rga-hw.c`; depends on V4L2 controls/device and videobuf2-v4l2 types.

Risks and test signals: shared structure layout affects buffer allocation and hardware programming. The unused `regmap *grf` and `op` fields may be legacy or future hooks. Test builds with sparse/compiler warnings and runtime operations that touch each shared field: format setup, controls, queueing, command start, IRQ completion, and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/rga.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/Kconfig

Purpose: defines the Rockchip Camera Interface (`VIDEO_ROCKCHIP_CIF`) Kconfig option.

Important content: tristate option depending on `VIDEO_DEV`, `ARCH_ROCKCHIP || COMPILE_TEST`, `V4L_PLATFORM_DRIVERS`, and `PM && COMMON_CLK`. It selects media controller support, `VIDEOBUF2_DMA_CONTIG`, `V4L2_FWNODE`, and `VIDEO_V4L2_SUBDEV_API`. Help text describes CIF variants including PX30 VIP and RK3568 VICAP with DVP and MIPI CSI-2 receiver support; module name is `rockchip-cif`.

Control flow/state: no runtime state; it gates whether the CIF capture driver is built.

Dependencies/integration: sourced by Rockchip top-level Kconfig and paired with `rkcif/Makefile`.

Risks and test signals: dependency selection must cover subdevice, fwnode, PM, clocks, and DMA-contig requirements. Test allmodconfig/allyesconfig, non-Rockchip COMPILE_TEST, and module build naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/Makefile

Purpose: kbuild rules for the Rockchip CIF capture driver.

Important content: builds `rockchip-cif.o` when `CONFIG_VIDEO_ROCKCHIP_CIF` is enabled. The composite object includes `rkcif-capture-dvp.o`, `rkcif-capture-mipi.o`, `rkcif-dev.o`, `rkcif-interface.o`, and `rkcif-stream.o`.

Control flow/state: no runtime behavior; it controls which implementation units are linked into the module/built-in object.

Dependencies/integration: paired with `rkcif/Kconfig` and the source files named in the object list.

Risks and test signals: object list drift creates unresolved symbols or missing capture paths. Test module and built-in builds for DVP and MIPI paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/Makefile -->

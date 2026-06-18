# Research Group: subset-b-004132

This grouped report covers the requested Amlogic C3 ISP/MIPI, Meson GE2D, and Amphion build-integration files. Each file section is delimited for source-tree-aligned splitting into the required per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-core.c

## Purpose

`c3-isp-core.c` implements the central V4L2 subdevice for the Amlogic C3 ISP pipeline. It models the ISP core as a media entity with video sink, parameter sink, statistics source, and three video source pads. Its responsibilities are format negotiation, frame-size programming, raw Bayer phase offset programming, stream propagation to the upstream source, and frame-sync event delivery.

## Important APIs, Types, And Functions

The local `struct c3_isp_core_format_info` table maps supported media-bus codes to valid pads, raw/YUV behavior, and Bayer phase offsets. `core_find_format_by_code()` and `core_find_format_by_index()` are the table lookup helpers behind pad enumeration and validation.

Hardware-facing helpers include `c3_isp_core_enable()`, `c3_isp_core_disable()`, `c3_isp_core_lswb_ofst()`, `c3_isp_core_3a_ofst()`, `c3_isp_core_dms_ofst()`, and `c3_isp_core_cfg_format()`. They program top-level path selection, frame-end/frame-reset IRQ masks, input/core frame sizes, hold size, AF/AE/AWB windows, and Bayer phase offsets for BLC/WB/lens/demosaic/3A blocks.

V4L2/media integration is exposed through `c3_isp_core_pad_ops`, `c3_isp_core_core_ops`, `c3_isp_core_internal_ops`, and `c3_isp_core_entity_ops`. Public entry points are `c3_isp_core_queue_sof()`, `c3_isp_core_register()`, and `c3_isp_core_unregister()`.

## Control Flow

Initialization creates a `V4L2_SUBDEV_FL_HAS_DEVNODE` and event-capable subdevice named `c3-isp-core`, assigns pad flags, initializes the media entity, finalizes subdev state, and registers it with the parent `v4l2_device`. Default state sets the sink to RAW10 RGGB at default size, the video sources to YUV10 at matching size, and metadata pads to `MEDIA_BUS_FMT_METADATA_FIXED`.

Format setting is pad-sensitive. The video sink accepts RAW10/RAW12 Bayer codes and clamps dimensions to ISP min/max. Source formats mirror sink dimensions and accept YUV10 or 16-bit raw Bayer output codes. Parameter and statistics pads retain fixed metadata format.

Streaming is coordinated with capture-path readiness. `c3_isp_core_enable_streams()` returns early until the number of enabled core source links matches `isp->pipe.start_count`. Once all consumers are ready, it resets `frm_sequence`, programs current format state, enables core input and interrupts, locates the unique upstream pad, and enables upstream stream 0. Disable only tears down the upstream stream and core hardware when `start_count` drops to one.

## State And Persistence

Persistent runtime state is in `struct c3_isp_core` and the parent `struct c3_isp_device`: `src_pad` stores the current upstream media pad, `frm_sequence` is incremented by the top-level IRQ handler, and subdev state stores per-pad formats. No file-backed persistence exists. Register state is volatile and rebuilt during stream enable.

## Dependencies And Integration Points

This file depends on V4L2 subdev active-state APIs, media-controller pad/link validation, V4L2 events, runtime PM through the broader device, and register helpers from `c3-isp-dev.c`. It integrates with parameter and statistics video nodes via metadata pads, with three resizers through video source pads, and with the upstream MIPI adapter/sensor through an immutable media link.

## Risks

`c3_isp_core_streams_ready()` compares `link->flags == MEDIA_LNK_FL_ENABLED`; links with additional flag bits would not be counted. Source-pad loops from `C3_ISP_CORE_PAD_SOURCE_VIDEO_0` to `C3_ISP_CORE_PAD_MAX` include the stats metadata pad, so the sink-format propagation writes width/height into all later pads before metadata pads are explicitly initialized only in `init_state`. The enable path calls `c3_isp_core_enable()` before resolving the upstream pad; an `-EPIPE` leaves the core enabled. Bayer phase offsets rely on the format table being complete and correct for every accepted sink code.

## Test Signals

Build with `CONFIG_VIDEO_C3_ISP` and run media-graph enumeration to verify six pads and expected default formats. Exercise `VIDIOC_SUBDEV_ENUM_MBUS_CODE`, `S_FMT`, `G_FMT`, and frame-sync event subscription. Streaming tests should start one, two, and three capture paths and verify the core only starts the upstream source after all enabled capture paths are ready, then stops when the last path stops. Hardware tests should confirm frame-end IRQs update stats/params/captures and frame-reset IRQs queue `V4L2_EVENT_FRAME_SYNC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-dev.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-dev.c

## Purpose

`c3-isp-dev.c` is the platform-driver and media-device glue for the Amlogic C3 ISP pipeline. It owns MMIO access helpers, runtime clock control, IRQ dispatch, V4L2/media registration, async upstream binding, internal media-link creation, and platform probe/remove sequencing.

## Important APIs, Types, And Functions

The exported register helpers are `c3_isp_read()`, `c3_isp_write()`, and `c3_isp_update_bits()`. Runtime PM hooks `c3_isp_runtime_suspend()` and `c3_isp_runtime_resume()` gate the `vapb` and `isp0` clocks through `clk_bulk_disable_unprepare()` and `clk_bulk_prepare_enable()`.

`c3_isp_irq_handler()` reads `ISP_TOP_RO_IRQ_STAT`, writes the same value to `ISP_TOP_IRQ_CLR`, and dispatches frame-end and frame-reset work. Frame-end calls `c3_isp_stats_isr()`, `c3_isp_params_isr()`, `c3_isp_captures_isr()`, then increments `frm_sequence`. Frame-reset queues SOF/frame-sync through `c3_isp_core_queue_sof()`.

Media graph setup is split across `c3_isp_media_register()`, `c3_isp_core_register()`, `c3_isp_resizers_register()`, `c3_isp_videos_register()`, and `c3_isp_create_links()`. Async notifier helpers bind the remote fwnode endpoint to the core video sink and register subdev nodes when complete.

## Control Flow

Probe allocates `struct c3_isp_device`, fetches match data, maps the named `isp` resource, gets the platform IRQ, obtains clocks, stores driver data, and enables runtime PM. It then registers the media device and V4L2 device, registers the core subdev, registers all resizers, registers the async notifier, requests the shared IRQ, and registers capture/stats/params video nodes plus internal links.

Internal link creation wires each resizer source to the matching capture device, each core video source to a resizer sink, the core stats source to the stats video node, and the params video node to the core params sink. Capture/resizer links are enabled, and the resizer-to-capture links are immutable.

Remove reverses the graph: unregister videos and remove links, unregister async notifier, unregister core and resizers, unregister media/V4L2 devices, and disable runtime PM.

## State And Persistence

`struct c3_isp_device` persists MMIO base, clocks, media/V4L2 devices, notifier, core/resizer/video-node subobjects, pipeline start counters, and frame sequence for the lifetime of the platform device. There is no disk state. Hardware state is volatile and restored during streaming and parameter/stat pre-configuration.

## Dependencies And Integration Points

The driver depends on platform resources named `isp`, an IRQ, device-tree compatible `amlogic,c3-isp`, clocks `vapb` and `isp0`, V4L2 async fwnode graph endpoints, media-controller APIs, and the local ISP modules for core, resizers, captures, stats, and params. The IRQ handler is the runtime integration point that synchronizes stats DMA completion, parameter-buffer consumption, capture completion, and frame-sync events.

## Risks

`pm_runtime_enable()` is not paired with an initial resume in probe; downstream stream paths must ensure clocks are active before touching registers. IRQ status is cleared by writing all read bits, so unexpected bits are acknowledged even if not handled. If `c3_isp_videos_register()` fails after `devm_request_irq()`, devm will release the IRQ later, but the failure path only unregisters the async notifier and lower graph pieces. Link creation assumes fixed counts and one-to-one mapping between `C3_ISP_NUM_RSZ` and capture devices. Async binding requires an endpoint at port 0 endpoint 0; missing firmware graph data returns `-ENOTCONN`.

## Test Signals

Compile coverage should include `CONFIG_COMPILE_TEST` or Meson platform builds. Device-tree tests must provide the `isp` resource, IRQ, clocks, and fwnode graph. Runtime tests should inspect `media-ctl -p` for expected links, verify `/dev/media*` and subdev/video nodes appear only after notifier completion, and confirm frame IRQs drive stats, params, capture completion, and frame-sync events without sequence gaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-params.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-params.c

## Purpose

`c3-isp-params.c` implements the ISP metadata-output video node used by userspace 3A/image-processing algorithms to submit per-frame parameter blocks. It validates V4L2 ISP parameter buffers, copies them into driver-owned scratch memory, queues them, and programs AWB gains/configuration, AE, AF, post gamma, CCM, CSC, and BLC hardware blocks at stream start and frame end.

## Important APIs, Types, And Functions

`union c3_isp_params_block` overlays the generic block header with each supported block-specific structure from `linux/media/amlogic/c3-isp-config.h`. `c3_isp_params_handlers[]` maps block type IDs to handlers, and `c3_isp_params_block_types_info[]` maps the same IDs to validation sizes. `static_assert()` enforces table length parity.

Hardware handlers include `c3_isp_params_cfg_awb_gains()`, `c3_isp_params_cfg_awb_config()`, `c3_isp_params_cfg_ae_config()`, `c3_isp_params_cfg_af_config()`, `c3_isp_params_cfg_pst_gamma()`, `c3_isp_params_cfg_ccm()`, `c3_isp_params_cfg_csc()`, and `c3_isp_params_cfg_blc()`. Helpers write zone weights/coordinates and LUT data.

The video-node entry points are `c3_isp_params_register()`, `c3_isp_params_unregister()`, `c3_isp_params_pre_cfg()`, and `c3_isp_params_isr()`. VB2 operations allocate scratch buffers with `kvmalloc()`, validate/copy user payloads in `buf_prepare`, enqueue under `buff_lock`, and return pending buffers on stop.

## Control Flow

Userspace opens the metadata-output node, allocates VMALLOC/DMABUF buffers of `sizeof(struct c3_isp_params_cfg)`, fills a validated `v4l2_isp_params_buffer`-style block stream, and queues buffers. `buf_prepare` checks the payload size, copies user data to `buf->cfg`, and calls `v4l2_isp_params_validate_buffer()` against the block type table.

At resizer stream start, `c3_isp_params_pre_cfg()` disables many unused ISP modules, disables AE/AF/AWB stats until explicitly enabled by parameter blocks, sets WB limits to max, and applies only the first pending buffer if one exists. On each frame-end IRQ, `c3_isp_params_isr()` removes the first pending buffer, walks its block list in `c3_isp_params_cfg_blocks()`, programs hardware, stamps sequence/timestamp/field, and marks the VB2 buffer done.

## State And Persistence

`struct c3_isp_params` stores video format, VB2 queue, mutex, spinlock, pending list, and current `buff`. Each queued `struct c3_isp_params_buffer` owns scratch `cfg` memory until cleanup. State is in memory only; hardware register state changes when parameter buffers are processed and is not persisted across power/runtime reset.

## Dependencies And Integration Points

The file depends on the V4L2 ISP parameter validation helpers, C3 ISP public parameter ABI in `c3-isp-config.h`, VB2 VMALLOC memory ops, metadata-output V4L2 ioctls, media-controller pads, and register definitions from `c3-isp-regs.h`. It integrates with `c3-isp-dev.c` through `c3_isp_params_isr()`, with `c3-isp-resizer.c` through `c3_isp_params_pre_cfg()`, and with the core params sink media link.

## Risks

`c3_isp_params_cfg_blocks()` indexes `c3_isp_params_handlers[block->header.type]` without local bounds or NULL checks, relying entirely on prior validation. The while loop advances by `block->header.size`; corrupted internal scratch data would risk an infinite loop or out-of-bounds access. Several coordinate and zone-weight writers trust `horiz_zones_num * vert_zones_num` and point counts to fit the ABI arrays. Pre-configuration keeps the first pending buffer on the list while applying it, so the same buffer can be applied again at the next frame-end unless the queue order is intended as an initial programming pass.

## Test Signals

Run V4L2 metadata-output format enumeration and verify only `V4L2_META_FMT_C3ISP_PARAMS` is accepted. Queue valid and invalid block streams to exercise buffer-size, block-size, type, and payload validation. Hardware tests should verify enable/disable flags gate module bits, AWB/AE weights are written in groups of eight plus remainder, gamma LUT writes all entries for three channels, and frame-end completion returns exactly one params buffer with the current sequence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-params.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-regs.h

## Purpose

`c3-isp-regs.h` is the register map and bitfield macro header for the Amlogic C3 ISP driver. It defines offsets, masks, and value-construction macros used by the core, parameter, resizer, stats, and capture paths to program ISP top-level routing, processing blocks, display/scaler blocks, statistics engines, writeback MIF, and statistics DMA.

## Important APIs, Types, And Functions

The header exports preprocessor constants only. Key groups are `ISP_TOP_*` for input/core sizes, path enable/select, display input select, IRQ enable/clear/status, and feature enable bits; `ISP_LSWB_*` for BLC/WB offsets, gains, limits, and phase offsets; `ISP_DMS_*` for demosaic phase; `ISP_CM0_*`, `ISP_CCM_*`, and `ISP_PST_GAMMA_*` for color conversion, color correction, and gamma; `DISP0_*` and `ISP_SCALE0_*` for per-resizer crop/output/PPS scaler setup; `ISP_AF_*`, `ISP_AE_*`, and `ISP_AWB_*` for 3A stat block windows, coordinates, weights, and controls; `ISP_WRMIFX3_0_*` for capture writeback; and `VIU_DMAWR_*` for statistics DMA base/size.

Value macros use standard kernel helpers such as `BIT()` and `GENMASK()`, and often encode hardware-specific units, for example base addresses shifted by four bytes and size fields stored in 16-byte units by caller convention.

## Control Flow

There is no executable control flow. Runtime flow is embodied by users: `c3-isp-core.c` writes top sizes, path selection, IRQ masks, and phase offsets; `c3-isp-params.c` updates image-processing and statistics control fields; `c3-isp-resizer.c` applies display/scaler register offsets through `C3_ISP_DISP_REG()` in its own file; stats/capture code programs DMA address, size, and writeback format registers.

## State And Persistence

The file defines the symbolic contract for volatile MMIO state. It has no variables or persistent state. Correctness depends on macros matching silicon register layout and field widths.

## Dependencies And Integration Points

Every C3 ISP source file that touches hardware includes this header. It integrates with Linux bitfield idioms but mostly uses simple shift macros rather than `FIELD_PREP()`. The register names align with the ISP functional blocks visible in the media pipeline: input/core, resizer/display, writeback, 3A stats, and DMA.

## Risks

Many value macros do not mask their input before shifting, so callers must clamp and validate widths, heights, coordinates, gains, and matrix coefficients. Some constants encode zero values as `(0 << n)`, which is clear but offers no runtime protection against stale bits unless used with the correct mask in `c3_isp_update_bits()`. Address macros such as `ISP_WRMIFX3_0_CH0_BASE_ADDR(x)` and `VIU_DMAWR_*_BASE_ADDR(x)` shift DMA addresses right by four and assume suitable alignment. Register offset or mask drift from hardware documentation would create silent corruption across multiple modules.

## Test Signals

Compile with `W=1` to catch macro type/overflow warnings in call sites. Hardware bring-up should compare register dumps against expected values after each pipeline operation: core format setup, AWB/AE/AF config, gamma/CCM/CSC programming, resizer scaling, writeback format, and stats DMA. Static review should verify every value macro is paired with the intended mask and that callers clamp to field width before shifting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-resizer.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-resizer.c

## Purpose

`c3-isp-resizer.c` implements three ISP resizer/scaler V4L2 subdevices. Each resizer receives one ISP core video source, supports crop and compose selection on its sink pad, programs display-path crop/output/PPS scaling hardware, and forwards the stream to the corresponding capture node.

## Important APIs, Types, And Functions

`struct c3_isp_rsz_format_info` lists RAW16 Bayer and YUV10 formats accepted on both sink and source pads. `struct c3_isp_pps_io_size` captures the scaler input/output geometry used by `c3_isp_rsz_pps_size()`. `c3_isp_pps_lut` is a 33-entry four-tap coefficient table written for luma and chroma.

Scaler helpers are `c3_isp_rsz_pps_size()`, `c3_isp_rsz_pps_lut()`, `c3_isp_rsz_pps_disable()`, and `c3_isp_rsz_pps_enable()`. Stream helpers `c3_isp_rsz_start()` and `c3_isp_rsz_stop()` choose raw MIPI output versus core output, program input size, crop, output size, and path enable bits. Public registration functions are `c3_isp_resizers_register()` and `c3_isp_resizers_unregister()`.

V4L2 subdev operations include media-bus code enumeration, format get/set, selection get/set, and stream enable/disable. `c3_isp_rsz_init_state()` seeds default YUV10 1920x1080-style state.

## Control Flow

Sink format setting validates the requested code, clamps dimensions, resets crop to full frame, resets compose to crop, and mirrors the source format dimensions. Source format setting is derived from sink code and compose size; callers cannot independently choose a different source code.

Selection control supports crop and compose only on the sink pad. Crop is clamped inside the sink frame and aligned to even dimensions. Compose is clamped inside crop size, aligned to even dimensions, and updates the source pad dimensions. At stream enable, the resizer programs path source selection based on whether input is raw, writes crop registers, enables crop, enables PPS scaling for non-raw input if compose differs from crop, writes output size, enables the selected display path, pre-configures params and stats, then enables its upstream core source stream. Disable reverses the display path and disables upstream core stream.

## State And Persistence

Each `struct c3_isp_resizer` stores its ID, parent ISP pointer, source subdev pointer, source pad index, pads, and subdev state. Crop/compose/format state persists in the V4L2 subdev active state while the device exists. Hardware state is volatile and reprogrammed on each start.

## Dependencies And Integration Points

The file depends on the ISP core for upstream streaming, the capture devices for downstream links, C3 register helpers, media-controller validation, and V4L2 subdev selection APIs. It invokes `c3_isp_params_pre_cfg()` and `c3_isp_stats_pre_cfg()` as part of stream start, making resizer start the point where metadata processing and stats DMA are primed.

## Risks

`c3_isp_rsz_set_source_fmt()` dereferences `rsz_fmt` without checking for NULL; it is safe only if source code is always derived from a validated sink code. PPS scaling calculations divide by output width/height, so selection clamping must prevent zero dimensions. The pre-scaler rate and tap-selection logic is hardware-specific and has several threshold branches, especially for `C3_ISP_RSZ_2`; off-by-one geometry can produce bad scaling or line-buffer overflow. Raw paths skip PPS but still program output size, so raw resize requests are effectively crop/pass-through rather than scale.

## Test Signals

Exercise `VIDIOC_SUBDEV_S_SELECTION` for crop/compose bounds, odd sizes, minimum sizes, and source-pad rejection. Verify media-bus enumeration for RAW16 and YUV10. Hardware tests should compare register programming for no-scale, simple downscale, downscale over 4x, large-width paths, and raw-vs-YUV input selection. Streaming tests should confirm params/stats pre-configuration happens before frame IRQs and that each resizer controls the matching capture path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-resizer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-stats.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-stats.c

## Purpose

`c3-isp-stats.c` implements the ISP metadata-capture video node for AF, AWB, and AE statistics. It manages DMA-contiguous buffers, programs hardware DMA target addresses and sizes, returns completed stats buffers on frame-end IRQs, and exposes a fixed `V4L2_META_FMT_C3ISP_STATS` capture interface.

## Important APIs, Types, And Functions

`c3_isp_stats_cfg_dmawr_addr()` lays out one stats buffer as AWB first, AE second, and AF third, then writes `VIU_DMAWR_BADDR0/1/2`. `c3_isp_stats_pre_cfg()` selects the newer AF stats mode, sets AE luma filter mode, programs AF/AWB/AE DMA sizes in 16-byte units, and primes the first queued buffer.

VB2 operations validate buffer size, derive DMA address with `vb2_dma_contig_plane_dma_addr()`, queue buffers under `buff_lock`, and return active/pending buffers with error on stream stop. Public entry points are `c3_isp_stats_register()`, `c3_isp_stats_unregister()`, `c3_isp_stats_pre_cfg()`, and `c3_isp_stats_isr()`.

## Control Flow

Userspace allocates and queues metadata-capture buffers. On stream pre-configuration, the driver programs stats module modes and sizes, then removes the first pending buffer and points the hardware DMA engine at its contiguous DMA memory. On each frame-end IRQ, `c3_isp_stats_isr()` completes the current buffer with sequence, timestamp, and `V4L2_FIELD_NONE`, then immediately dequeues and programs the next pending buffer if available.

Registration builds a video node named `c3-isp-stats` with `V4L2_CAP_META_CAPTURE | V4L2_CAP_STREAMING`, VB2 DMA-contig memory operations, `V4L2_BUF_TYPE_META_CAPTURE`, and `min_queued_buffers = 2`.

## State And Persistence

`struct c3_isp_stats` holds the fixed metadata format, VB2 queue, pending list, spinlock, current buffer pointer, and mutex. Each `struct c3_isp_stats_buffer` stores a DMA address captured during buffer initialization. There is no persistent storage; statistics live in user-provided DMA buffers and register state is reprogrammed each stream.

## Dependencies And Integration Points

This module depends on DMA-contiguous VB2 memory, C3 ISP stats ABI structures in `c3-isp-config.h`, register definitions in `c3-isp-regs.h`, the core IRQ path in `c3-isp-dev.c`, and media links from the ISP core stats source. It is synchronized with resizer stream start through `c3_isp_stats_pre_cfg()`.

## Risks

The DMA layout assumes `struct c3_isp_stats_info` is large enough and ordered compatibly with AWB, AE, then AF structures. `c3_isp_stats_cfg_dmawr_addr()` programs addresses shifted by register macros, so buffer alignment must satisfy hardware requirements. If no next pending buffer exists at frame end, stats DMA may continue pointing at the completed buffer until another pre-config path updates it. IRQ completion runs under a spinlock and calls VB2 completion, so lock ordering must remain compatible with VB2 expectations.

## Test Signals

V4L2 tests should verify fixed metadata format, queue minimums, buffer-size rejection, and streamoff error-return of active and pending buffers. Hardware tests should queue several buffers, start streaming, and confirm each frame returns one stats buffer with monotonically increasing sequence and plausible AWB/AE/AF regions. Register dumps should confirm DMA sizes match ABI structure sizes divided by 16 bytes and base addresses are correctly aligned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/mipi-adapter/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/mipi-adapter/Kconfig

## Purpose

This Kconfig file introduces `CONFIG_VIDEO_C3_MIPI_ADAPTER`, the build option for the Amlogic C3 MIPI adapter V4L2 subdevice driver. The adapter receives data from the C3 MIPI CSI-2 receiver, organizes RAW MIPI data, and sends it onward to the ISP pipeline.

## Important APIs, Types, And Functions

The file defines a single tristate symbol, `VIDEO_C3_MIPI_ADAPTER`, with user-visible prompt `"Amlogic C3 MIPI adapter"`. It has no C APIs or runtime functions, but its selects and dependencies directly control which media framework APIs are available to `c3-mipi-adap.c`.

## Control Flow

Kconfig evaluation permits the symbol when building for `ARCH_MESON` or under `COMPILE_TEST`, when `VIDEO_DEV` and `OF` are available. If selected as built-in or module, it also selects `MEDIA_CONTROLLER`, `V4L2_FWNODE`, and `VIDEO_V4L2_SUBDEV_API`.

## State And Persistence

There is no runtime state. The configuration state persists in the kernel build configuration and determines whether the Makefile emits `c3-mipi-adap.o`.

## Dependencies And Integration Points

The option integrates the adapter into the media platform driver build. `OF` is required because the driver relies on device-tree resources and fwnode graph endpoints. The selected V4L2/media symbols match the driver's use of subdev pads, async notifier, and fwnode link creation.

## Risks

The symbol does not explicitly depend on the C3 MIPI CSI-2 or ISP drivers, so users can build it alone; this is valid for modular media graphs but may produce incomplete runtime pipelines if device-tree and companion drivers are absent. It selects media-controller support unconditionally when enabled, increasing build footprint.

## Test Signals

Run `make olddefconfig` and compile with `CONFIG_VIDEO_C3_MIPI_ADAPTER=m` and `=y` under both Meson and `COMPILE_TEST` environments. Confirm the generated module is named from the Makefile object and that enabling this symbol pulls in the required V4L2 subdev/fwnode/media-controller infrastructure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/mipi-adapter/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/mipi-adapter/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/mipi-adapter/Makefile

## Purpose

This Makefile connects `CONFIG_VIDEO_C3_MIPI_ADAPTER` to the C3 MIPI adapter object file. It is the build-system bridge between the Kconfig symbol and `c3-mipi-adap.c`.

## Important APIs, Types, And Functions

There are no C APIs. The key build directive is `obj-$(CONFIG_VIDEO_C3_MIPI_ADAPTER) += c3-mipi-adap.o`.

## Control Flow

During Kbuild evaluation, `c3-mipi-adap.o` is included in the built-in object list when the symbol is `y`, in the module list when the symbol is `m`, and omitted when disabled.

## State And Persistence

The file has no runtime state. The object-selection result is derived from the kernel configuration and persists only in build artifacts.

## Dependencies And Integration Points

It depends on the enclosing media platform Makefile including this directory. It integrates with the Kconfig file of the same directory and compiles exactly one source file into the adapter driver module or built-in object.

## Risks

The Makefile does not define composite objects, so any future split of adapter code into multiple C files must update this directive. A mismatch between the Kconfig symbol and object name would silently omit the driver, but the current names align.

## Test Signals

Build with `CONFIG_VIDEO_C3_MIPI_ADAPTER=m` and verify a `c3-mipi-adap.ko`-style module is produced. Build with the symbol disabled and verify no adapter object appears in the directory's generated objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/mipi-adapter/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/mipi-adapter/c3-mipi-adap.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/mipi-adapter/c3-mipi-adap.c

## Purpose

`c3-mipi-adap.c` implements the Amlogic C3 MIPI adapter V4L2 subdevice. It bridges the upstream MIPI CSI-2 receiver to the ISP by configuring adapter top, frontend, DDR reader, pixel, and alignment blocks for direct RAW Bayer delivery.

## Important APIs, Types, And Functions

The file defines register address composition macros for three adapter submodules: TOP, frontend, and reader. `struct c3_adap_device` stores device pointer, three MMIO bases, clocks, subdev, pads, async notifier, current upstream pad, and match-data clock info. `struct c3_adap_pix_format` maps RAW10/RAW12 media-bus codes to MIPI CSI-2 data types.

Hardware helpers include `c3_mipi_adap_update_bits()`, `c3_mipi_adap_cfg_top()`, `c3_mipi_adap_cfg_frontend()`, `c3_mipi_adap_cfg_rd0()`, `c3_mipi_adap_cfg_pixel0()`, and `c3_mipi_adap_cfg_alig()`. V4L2 operations are `c3_mipi_adap_enable_streams()`, `c3_mipi_adap_disable_streams()`, `c3_mipi_adap_enum_mbus_code()`, `c3_mipi_adap_set_fmt()`, and `c3_mipi_adap_init_state()`.

Probe/remove helpers initialize subdev/media pads, async notifier, named resources `top`, `fd`, `rd`, runtime PM, and clocks `vapb` and `isp0`.

## Control Flow

Probe maps all three hardware regions, obtains clocks, enables runtime PM, initializes the bridge subdevice, registers an async notifier for remote endpoint port 0 endpoint 0, and registers the subdev. Bound notifier callbacks create immutable enabled links from the upstream remote subdev to the adapter sink.

Format negotiation accepts RAW10 and RAW12 Bayer sink formats, clamps dimensions to 160x120 through 2888x2240, forces RAW colorspace metadata, and mirrors the sink format to the source pad. Source-pad enumeration exposes only the current source format.

Stream enable finds the unique upstream source pad, resumes runtime PM, gets the sink format, programs top reset/decompress bypass, frontend window and VC0 RAW packet handling, DDR_RD0 direct mode, PIXEL0 data type/start, and alignment blanking/path/start. It then enables the upstream source stream. Disable disables upstream stream if present, clears `src_pad`, and drops runtime PM.

## State And Persistence

Persistent state is per-device memory: MMIO bases, clocks, subdev state, notifier state, and `src_pad`. Format state is held in V4L2 subdev state. Hardware state is volatile and configured at stream enable. There is no file-backed state.

## Dependencies And Integration Points

The adapter depends on platform resources named `top`, `fd`, and `rd`, device-tree compatible `amlogic,c3-mipi-adapter`, V4L2 async fwnode graph links, media-controller validation, MIPI CSI-2 data-type definitions, and runtime PM. In the media graph it sits between the C3 CSI-2 receiver and C3 ISP core.

## Risks

`c3_mipi_adap_cfg_pixel0()` assumes `c3_mipi_adap_find_format(fmt->code)` succeeds; this depends on format state being validated. `pm_runtime_resume_and_get()` return value is ignored, so stream enable may program registers without clocks if runtime resume fails. Stream enable calls the local hardware configuration before enabling upstream; upstream failure drops PM but does not explicitly reset/stop already-started adapter blocks. The adapter forces VC0 and RAW packets only, with no support for multiple virtual channels or YUV despite some register definitions.

## Test Signals

Use media graph tests to verify immutable upstream links and two-pad bridge registration. Subdev format tests should validate RAW10/RAW12 enumeration, default SRGGB10 1920x1080 state, clamping, and sink-to-source mirroring. Hardware tests should stream from a sensor through CSI-2 and adapter into ISP, checking that RAW data type matches the selected bus code and that alignment blanking satisfies ISP requirements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/mipi-adapter/c3-mipi-adap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/mipi-csi2/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/mipi-csi2/Kconfig

## Purpose

This Kconfig file defines `CONFIG_VIDEO_C3_MIPI_CSI2`, the build option for the Amlogic C3 MIPI CSI-2 receiver subdevice driver. The receiver ingests MIPI CSI-2 data from an image sensor and forwards media-bus data into the C3 camera pipeline.

## Important APIs, Types, And Functions

The file defines one tristate symbol, `VIDEO_C3_MIPI_CSI2`, with prompt `"Amlogic C3 MIPI CSI-2 receiver"`. It exposes no runtime APIs but selects framework capabilities required by `c3-mipi-csi2.c`.

## Control Flow

Kconfig allows the option on Meson platforms or under compile testing, requiring `VIDEO_DEV` and `OF`. Enabling it selects `MEDIA_CONTROLLER`, `V4L2_FWNODE`, and `VIDEO_V4L2_SUBDEV_API`.

## State And Persistence

There is no runtime state. The selected build state persists in `.config` and controls whether the Makefile builds `c3-mipi-csi2.o`.

## Dependencies And Integration Points

`OF` is necessary because the driver parses device-tree fwnode endpoints and MIPI CSI-2 bus configuration. The selected media symbols match its use of V4L2 subdevs, async notifier, and media graph links.

## Risks

The symbol does not enforce presence of the adapter or ISP symbols, allowing partial builds. That is useful for modular graphs and compile testing but can surprise integrators expecting a full camera stack from one option.

## Test Signals

Compile with `CONFIG_VIDEO_C3_MIPI_CSI2=m` and `=y`, both on Meson and under `COMPILE_TEST`. Confirm enabling the symbol selects the needed V4L2/media infrastructure and produces the expected object/module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/mipi-csi2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/mipi-csi2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/mipi-csi2/Makefile

## Purpose

This Makefile maps the C3 MIPI CSI-2 Kconfig symbol to its driver object. It is the only build directive needed for the single-file receiver driver.

## Important APIs, Types, And Functions

There are no C interfaces. The relevant Kbuild line is `obj-$(CONFIG_VIDEO_C3_MIPI_CSI2) += c3-mipi-csi2.o`.

## Control Flow

Kbuild includes `c3-mipi-csi2.o` as built-in, module, or not at all depending on whether `CONFIG_VIDEO_C3_MIPI_CSI2` is `y`, `m`, or unset.

## State And Persistence

The Makefile has no runtime state. Build outputs reflect the kernel configuration.

## Dependencies And Integration Points

The file integrates with the same directory's Kconfig and the parent platform media build. It assumes all CSI-2 receiver code remains in `c3-mipi-csi2.c`.

## Risks

Future source splits require Makefile updates. Otherwise, risk is low because the object and Kconfig symbol names match directly.

## Test Signals

Build with `CONFIG_VIDEO_C3_MIPI_CSI2=m` and confirm a module object is produced. Disable the symbol and verify the object is omitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/mipi-csi2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/mipi-csi2/c3-mipi-csi2.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/mipi-csi2/c3-mipi-csi2.c

## Purpose

`c3-mipi-csi2.c` implements the Amlogic C3 MIPI CSI-2 receiver bridge. It configures analog PHY, DPHY timing/lane routing, and CSI-2 host lane count, exposes a two-pad V4L2 subdevice, parses fwnode MIPI bus settings, and propagates streaming to an upstream image sensor.

## Important APIs, Types, And Functions

Register routing macros split the hardware into APHY, DPHY, and HOST submodules. `struct c3_csi_device` stores device pointer, three MMIO bases, clocks, subdev, pads, notifier, upstream pad, parsed `v4l2_mbus_config_mipi_csi2`, and match-data clock info. `c3_mipi_csi_formats[]` lists RAW10 and RAW12 Bayer bus codes.

Hardware helpers are `c3_mipi_csi_write()`, `c3_mipi_csi_cfg_aphy()`, `c3_mipi_csi_cfg_dphy()`, `c3_mipi_csi_cfg_host()`, and `c3_mipi_csi_start_stream()`. V4L2 operations include stream enable/disable, bus-code enumeration, format set/get, and initial state. Platform helpers initialize/deinitialize the subdev, register async notifier, map named resources `aphy`, `dphy`, `host`, get clocks `vapb` and `phy0`, and handle runtime PM.

## Control Flow

Probe maps APHY/DPHY/HOST resources, gets clocks, enables runtime PM, initializes a bridge subdevice with sink/source pads, parses endpoint 0 as `V4L2_MBUS_CSI2_DPHY`, stores bus lane configuration, registers an async notifier for the remote sensor endpoint, and registers the subdev. Bound notification creates an immutable enabled link from the sensor to the CSI-2 sink.

Format negotiation accepts RAW10/RAW12 Bayer formats on the sink pad, clamps dimensions to 160x120 through 2888x2240, forces RAW colorspace metadata, and mirrors the sink format to the source pad.

Stream enable resolves the unique upstream pad, resumes runtime PM, calls `c3_mipi_csi_start_stream()`, then enables the upstream sensor stream. Start obtains link frequency from the upstream pad, computes lane rate as twice link frequency, rejects rates above 1.5 Gbps, programs APHY constants, computes DPHY high-speed settle from lane rate, sets lane mux order, enables all digital lanes and the clock lane, resets host output, and writes `num_data_lanes - 1`.

## State And Persistence

State persists in the allocated `struct c3_csi_device`: resource bases, clock descriptors, parsed bus lane count, subdev state, notifier, and current upstream pad. Hardware programming is volatile and repeated at stream start. There is no disk persistence.

## Dependencies And Integration Points

The receiver depends on device-tree graph endpoints with MIPI CSI-2 DPHY bus data, upstream sensor link-frequency reporting, media-controller links, V4L2 subdev APIs, and runtime PM. It integrates upstream of `c3-mipi-adapter.c` in the C3 camera media graph.

## Risks

`pm_runtime_resume_and_get()` and `c3_mipi_csi_start_stream()` return values are not fully checked in stream enable; the call to start stream ignores its return, so an invalid/missing link frequency may still be followed by upstream stream enable. DPHY programming enables all four data lanes regardless of parsed `num_data_lanes`, while host lane count reflects the parsed value. Lane mux is fixed to identity order and does not use endpoint lane mapping. Timing constants are mostly fixed except HS settle, so unusual sensors may need tuning.

## Test Signals

Device-tree tests should cover one-, two-, and four-lane endpoints with link-frequency controls. Subdev tests should verify RAW format enumeration, clamping, and sink/source mirroring. Hardware stream tests should verify lane-rate rejection, correct host lane count, stable sensor-to-adapter streaming, and no runtime-PM register access failures. Static tests should flag the ignored return from `c3_mipi_csi_start_stream()` as a candidate fix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/mipi-csi2/c3-mipi-csi2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/meson-ge2d/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/meson-ge2d/Kconfig

## Purpose

This Kconfig file defines `CONFIG_VIDEO_MESON_GE2D`, the build option for the Amlogic GE2D 2D graphics accelerator V4L2 mem2mem driver. GE2D provides color conversion, scaling, BitBLT, and alpha-blending hardware, though the current driver implements a narrower RGB blit/transform subset.

## Important APIs, Types, And Functions

The single tristate symbol is `VIDEO_MESON_GE2D`, prompted as `"Amlogic 2D Graphic Acceleration Unit"`. The option selects `VIDEOBUF2_DMA_CONTIG` and `V4L2_MEM2MEM_DEV`, which are required by `ge2d.c`.

## Control Flow

Kconfig allows this driver when V4L2 mem2mem infrastructure, video device support, and either Meson architecture or compile testing are enabled. The help text explains module selection and high-level hardware capability.

## State And Persistence

No runtime state is stored here. The build configuration determines whether the Makefile builds `ge2d.o`.

## Dependencies And Integration Points

The option integrates a platform V4L2 mem2mem accelerator into the media build. It depends on `V4L_MEM2MEM_DRIVERS` and `VIDEO_DEV`, aligning with the driver's V4L2 mem2mem queues, video node, and VB2 DMA-contig memory usage.

## Risks

The help text mentions scaling and color conversion hardware capabilities while `ge2d.c` documents several missing features, including scaling and YUV input support. Integrators should treat the Kconfig description as hardware capability, not full driver feature coverage.

## Test Signals

Build with `CONFIG_VIDEO_MESON_GE2D=m` and `=y` under Meson and `COMPILE_TEST`. Confirm the config selects mem2mem and DMA-contig support and produces the GE2D driver object/module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/meson-ge2d/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/meson-ge2d/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/meson-ge2d/Makefile

## Purpose

This Makefile maps `CONFIG_VIDEO_MESON_GE2D` to the GE2D driver object. It builds the single-source V4L2 mem2mem accelerator driver.

## Important APIs, Types, And Functions

There are no runtime APIs. The only Kbuild directive is `obj-$(CONFIG_VIDEO_MESON_GE2D) += ge2d.o`.

## Control Flow

Kbuild includes `ge2d.o` in the built-in image, module build, or neither according to the Kconfig symbol value.

## State And Persistence

The file has no runtime state. Build artifacts are the only output.

## Dependencies And Integration Points

It integrates with the GE2D Kconfig and parent media platform build. It assumes the whole driver implementation is in `ge2d.c`.

## Risks

Low risk for the current single-file driver. Any future split into register helpers, format tables, or platform variants must update the object list.

## Test Signals

Compile with `CONFIG_VIDEO_MESON_GE2D=m` and confirm `ge2d.o` and a loadable module are generated. Compile with the symbol disabled and confirm the object is not built.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/meson-ge2d/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/meson-ge2d/ge2d-regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/meson-ge2d/ge2d-regs.h

## Purpose

`ge2d-regs.h` defines the MMIO register offsets, bitfields, hardware color format maps, ALU blend/logic constants, and field-prep helper macros used by the Meson GE2D V4L2 mem2mem driver.

## Important APIs, Types, And Functions

The header's central offset macro is `GE2D_REG(x)`, which maps logical GE2D register indices to byte offsets starting at hardware base index `0x8a0 * 4`. It defines control/status registers such as `GE2D_GEN_CTRL0..4`, `GE2D_CMD_CTRL`, `GE2D_STATUS0..2`, source/destination clip/window/canvas/base/stride registers, scale coefficient registers, matrix registers, and ALU registers.

Color format constants include `GE2D_FORMAT_8BIT/16BIT/24BIT/32BIT` and many `GE2D_COLOR_MAP_*` values for RGB/YUV layouts. ALU helpers `GE2D_ALU_COLOR_OP()`, `GE2D_ALU_DO_COLOR_OPERATION_LOGIC()`, `GE2D_ALU_ALPHA_OP()`, and `GE2D_ALU_DO_ALPHA_OPERATION_LOGIC()` combine operation and factor fields using `FIELD_PREP()`.

## Control Flow

There is no executable flow. `ge2d.c` consumes these constants when resetting hardware, programming source/destination base and stride, configuring source/destination pixel formats, writing clipping and window bounds, selecting ALU copy/alpha behavior, and issuing `GE2D_CBUS_CMD_WR`.

## State And Persistence

The file contains no variables. It describes volatile hardware state fields. Correctness depends on matching GE2D silicon documentation and the regmap configuration in `ge2d.c`.

## Dependencies And Integration Points

The header depends on kernel bit helpers (`BIT`, `GENMASK`, `FIELD_PREP`) supplied through including C files. It is tightly integrated with the `struct ge2d_fmt` table in `ge2d.c`, where V4L2 formats map to `GE2D_FORMAT_*` and `GE2D_COLOR_MAP_*` constants.

## Risks

`GE2D_REG(x)` bakes in a base offset; using the header with a differently based MMIO region would program the wrong addresses. Many color-map constants alias between RGB and YUV names, so format-table mistakes can silently reinterpret channels. The ALU factor constants distinguish color and alpha spaces but share some numeric values; wrong helper use can generate invalid blending behavior.

## Test Signals

Build tests should ensure all `FIELD_PREP()` masks are valid for their constants. Runtime register tracing during a simple blit should show `GEN_CTRL2`, clip/window registers, `ALU_OP_CTRL`, and `CMD_CTRL` values matching the selected V4L2 formats and transform controls. Format tests should verify every `ge2d.c` format maps to a defined hardware format/map pair.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/meson-ge2d/ge2d-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/meson-ge2d/ge2d.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/meson-ge2d/ge2d.c

## Purpose

`ge2d.c` implements a V4L2 mem2mem driver for the Amlogic Meson GE2D 2D graphics accelerator. The implemented path copies/transforms RGB buffers with crop/compose rectangles, rotation, horizontal/vertical flip, and alpha handling. The file explicitly notes missing features such as scaling, simple half vertical scaling, YUV input, source global alpha, and colorspace conversion.

## Important APIs, Types, And Functions

`struct ge2d_fmt` maps V4L2 fourcc formats to alpha presence, depth, hardware format, and hardware color map. `struct ge2d_frame` stores the current VB2 buffer, pixel format, crop rectangle, and format descriptor. `struct ge2d_ctx` is per-filehandle state including V4L2 FH, mem2mem context, input/output frames, controls, sequence counters, and transform flags. `struct meson_ge2d` is the device object with V4L2 device, mem2mem device, video node, regmap, clock, mutex, and current running context.

Core execution functions are `ge2d_hw_start()`, `device_run()`, and `ge2d_isr()`. VB2/mem2mem operations include `queue_init()`, `ge2d_queue_setup()`, `ge2d_buf_prepare()`, `ge2d_buf_queue()`, stream start/stop, and `ge2d_m2m_ops`. V4L2 ioctl handlers cover querycap, format enumeration/get/try/set for output and capture, crop/compose selection, buffer ioctls, stream ioctls, and control events. Controls are handled by `ge2d_s_ctrl()` for HFLIP, VFLIP, and ROTATE.

## Control Flow

Probe maps MMIO, initializes regmap, requests IRQ, gets reset and clock, resets hardware, enables the clock, registers the V4L2 device, allocates a video node, initializes the V4L2 mem2mem device, and registers `/dev/video*`.

Open allocates a context, initializes default 128x128 XRGB-like frames, creates mem2mem queues, initializes V4L2 FH, adds controls, and attaches the control handler. Userspace configures output/capture formats and crop/compose rectangles, queues one source and one destination buffer, and starts streaming. `device_run()` selects the next source/destination buffers and calls `ge2d_hw_start()`.

`ge2d_hw_start()` resets GE2D, writes DMA base/stride for source1, source2, and destination, programs control registers, format maps, clipping and full-image extents, constructs an ALU copy operation with alpha behavior based on input/output alpha support, and writes `GE2D_CMD_CTRL` with flip/rotation bits plus command start. The IRQ handler polls `GE2D_STATUS0`; when the busy bit is clear, it removes source/destination buffers, updates sequence numbers, copies timestamp/timecode/flags, marks both done, and finishes the mem2mem job.

## State And Persistence

Per-open state persists in `struct ge2d_ctx` until release. Device state persists in `struct meson_ge2d`; `curr` tracks the in-flight context. Queue state is held by V4L2 mem2mem/VB2. Hardware register state is transient per job. There is no file-backed persistence.

## Dependencies And Integration Points

The driver depends on platform compatible `amlogic,axg-ge2d`, a single MMIO resource, IRQ, reset control, clock, regmap MMIO, V4L2 mem2mem, VB2 DMA-contig, and the local register header. It exposes a V4L2 M2M video node with `V4L2_CAP_VIDEO_M2M | V4L2_CAP_STREAMING`.

## Risks

`ge2d_isr()` treats `!(GE2D_GE2D_BUSY)` as completion, which depends on interrupt behavior and status semantics; spurious IRQs while `ge2d->curr` is NULL would dereference NULL. Format handling supports RGB layouts only despite GE2D color-map definitions for YUV. Rotation changes capture dimensions and refuses changes only when the capture queue is busy; output queue interactions should also be considered. The log message `"queue (%d) bust"` appears to be a typo. There is no explicit runtime PM; the clock is enabled for the driver's lifetime. Hardware scaling registers are defined but not used, so crop/compose must not be interpreted as arbitrary scaling support.

## Test Signals

Run V4L2 mem2mem compliance for format enumeration, try/set behavior, busy-queue rejection, crop/compose validation, and controls. Queue RGB buffers for copy, HFLIP, VFLIP, and rotations 90/180/270 and compare output pixels. IRQ tests should cover normal completion, streamoff with queued buffers, and spurious/early interrupts. Probe/remove tests should validate reset, clock enable/disable, IRQ registration, and clean release of video and mem2mem devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/meson-ge2d/ge2d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/Kconfig

## Purpose

This Kconfig file defines the build option for the NXP Amphion VPU V4L2 mem2mem codec driver. The VPU contains Windsor encoder and Malone decoder blocks and targets NXP i.MX8Q-family hardware for H.264 encode plus H.264/HEVC and other decode workloads.

## Important APIs, Types, And Functions

The file defines a comment group `"Amphion drivers"` and one tristate symbol, `VIDEO_AMPHION_VPU`, prompted as `"Amphion VPU (Video Processing Unit) Codec IP"`. It does not define C functions, but its selected symbols enable the media-controller, V4L2 mem2mem, and VB2 memory infrastructure used by the Amphion source files.

## Control Flow

Kconfig permits the driver when `V4L_MEM2MEM_DRIVERS`, `ARCH_MXC || COMPILE_TEST`, `MEDIA_SUPPORT`, and `VIDEO_DEV && MAILBOX` are satisfied. Enabling it selects `MEDIA_CONTROLLER`, `V4L2_MEM2MEM_DEV`, `VIDEOBUF2_DMA_CONTIG`, and `VIDEOBUF2_VMALLOC`.

## State And Persistence

The only state is the kernel build configuration. Runtime state is implemented in the Amphion C files listed by the Makefile.

## Dependencies And Integration Points

The `MAILBOX` dependency reflects the driver's firmware/control-channel communication. The selected VB2 DMA-contig and VMALLOC allocators match its mixed buffer-management needs. The symbol integrates all Amphion objects into one composite `amphion-vpu` module through the Makefile.

## Risks

The option is broad: one symbol builds encoder, decoder, firmware RPC, mailbox, helper, color, debug, and SoC support code. This simplifies selection but makes it impossible to build only decoder or encoder pieces from Kconfig. Runtime use depends on firmware and platform resources not expressed in this file.

## Test Signals

Run config builds with `CONFIG_VIDEO_AMPHION_VPU=m` and `=y` under i.MX and compile-test configurations. Verify unmet `MAILBOX`, `VIDEO_DEV`, or `V4L_MEM2MEM_DRIVERS` dependencies hide the option. Confirm selected VB2/media symbols appear in the final config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/Makefile

## Purpose

This Makefile builds the NXP Amphion VPU composite driver. It aggregates platform probing, core management, mailbox transport, V4L2 mem2mem glue, firmware command/message/RPC handling, i.MX8Q SoC support, Windsor encoder, Malone decoder, color handling, decoder/encoder frontends, and debug support into `amphion-vpu`.

## Important APIs, Types, And Functions

There are no runtime APIs in the Makefile itself. The important build variables are `amphion-vpu-objs`, which lists all object files, and `obj-$(CONFIG_VIDEO_AMPHION_VPU) += amphion-vpu.o`, which binds the composite object to the Kconfig symbol.

The object list includes `vpu_drv.o`, `vpu_core.o`, `vpu_mbox.o`, `vpu_v4l2.o`, `vpu_helpers.o`, `vpu_cmds.o`, `vpu_msgs.o`, `vpu_rpc.o`, `vpu_imx8q.o`, `vpu_windsor.o`, `vpu_malone.o`, `vpu_color.o`, `vdec.o`, `venc.o`, and `vpu_dbg.o`.

## Control Flow

Kbuild first compiles each listed source to an object, links them into `amphion-vpu.o`, and then includes that composite object as built-in or module based on `CONFIG_VIDEO_AMPHION_VPU`.

## State And Persistence

The file has no runtime state. It defines build composition, which persists in generated objects/modules.

## Dependencies And Integration Points

It integrates tightly with `Kconfig`, which supplies the single symbol controlling the whole object set. The ordered object list is the build-time integration map for the Amphion driver subsystems: platform driver, VPU core lifecycle, V4L2, firmware interface, codec engines, and debug.

## Risks

Because all objects are always linked together, missing symbols or build breakage in an encoder, decoder, RPC, or debug file breaks the entire driver. The object list must be kept in sync with source renames and new subsystem files. The double spacing before `vdec.o` is harmless but shows this is a hand-maintained list.

## Test Signals

Build with `CONFIG_VIDEO_AMPHION_VPU=m` and verify a single `amphion-vpu` module contains all listed objects. Build with the symbol disabled and verify none of the objects are linked. Link-time tests should catch missing cross-object symbols between V4L2, command/message, Windsor, Malone, and platform support files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/Makefile -->

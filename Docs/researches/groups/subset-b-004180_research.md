# Research: subset-b-004180

## sources/distributed-fs/ceph-client/drivers/media/platform/via/via-camera.h
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/via/via-camera.h -->
# Research: sources/distributed-fs/ceph-client/drivers/media/platform/via/via-camera.h

Purpose: this header is a register map for the VIA capture engines used by the VIA camera platform driver. It has no functions or storage; its API is the set of `VCR_*` offsets and bit masks for interrupt control, transport stream input, capture interface configuration, active/VBI ranges, DMA buffer addresses, stride, and error counters.

Important definitions include `VCR_INTCTRL` status/interrupt bits for EAV, VBI, active buffer, field, FIFO full, and interrupt enables; `VCR_TSC` transport stream enable/drop/count/endianness/serial flags; `VCR_CAPINTC` capture-enable, input format, byte order, deinterlace, filtering, polarity, FIFO threshold, and clock-enable bits; and address/stride registers such as `VCR_VBUF1..3`, `VCR_VBIBUF1..2`, `VCR_VBUF_MASK`, and `VCR_VS_STRIDE`.

Control flow is external: callers include the header and program memory-mapped registers, adding `0x1000` for the second capture engine. State is entirely hardware state persisted in registers and DMA buffer addresses; this file does not cache or synchronize anything. Dependencies are only C preprocessor inclusion and the downstream driver using Linux I/O helpers.

Risks are incorrect bit composition, especially byte-order, CCIR mode, polarity, clock, and buffer-stride fields that directly affect capture corruption or DMA addressing. Test signals are compile success of the VIA camera driver plus hardware tests that verify frame interrupt delivery, buffer selection, stride, VBI buffer handling, and second-engine offset programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/via/via-camera.h -->

## sources/distributed-fs/ceph-client/drivers/media/platform/video-mux.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/video-mux.c -->
# Research: sources/distributed-fs/ceph-client/drivers/media/platform/video-mux.c

Purpose: implements a generic V4L2 media-controller subdevice for a device-tree `video-mux` whose active input is selected through the Linux mux-control consumer API. It presents N-1 sink pads and one source pad, propagates formats from the enabled sink to the source, and forwards stream control upstream.

Important types and APIs: `struct video_mux` owns a `v4l2_subdev`, async notifier, media pads, `struct mux_control`, mutex, and `active` sink index. Key functions are `video_mux_probe/remove`, `video_mux_link_setup`, `video_mux_s_stream`, `video_mux_set_format`, `video_mux_init_state`, and `video_mux_async_register`. It integrates with `media_entity_operations`, V4L2 subdev pad/video ops, `v4l2_create_fwnode_links`, `v4l2_async_nf_add_fwnode_remote`, and `devm_mux_control_get`.

Control flow: probe counts graph endpoints and treats the largest numbered port as the output, allocates pads, initializes the subdev, finalizes active state, then registers an async notifier for connected input endpoints. Link setup is the main state transition: enabling a sink link calls `mux_control_try_select`, rejects a different active sink with `-EBUSY`, records `active`, and copies that sink format to the source pad; disabling the active sink deselects the mux and sets `active = -1`. Streaming requires an active sink, finds the remote upstream subdevice, and calls its `video.s_stream`.

State and persistence: runtime state is only in memory and the mux-control hardware selection. Active-pad and format state are protected by the mux mutex plus V4L2 subdev active-state locking. There is no persistent userspace state.

Dependencies and integration: requires OF graph endpoints, a mux provider, V4L2 subdev/media-controller APIs, async notifier binding, and accepted media bus codes. It is selected by platform OF compatible `video-mux`.

Risks: source-pad link toggles intentionally do not affect selection, so userspace must enable exactly one sink link. Format propagation only mirrors the active sink; inactive sink formats can diverge. Streaming fails if the remote pad is missing or not a V4L2 subdev. Test signals include `media-ctl` link enable/disable behavior, `v4l2-compliance` subdev format operations, format mirroring on active input changes, and mux-control provider error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/video-mux.c -->

## sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/Kconfig
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/Kconfig -->
# Research: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/Kconfig

Purpose: declares Xilinx media platform driver configuration symbols. `VIDEO_XILINX` is the base composite video IP pipeline driver and selects media-controller, V4L2 subdev API, contiguous DMA vb2 memory, and V4L2 fwnode support.

Important entries: `VIDEO_XILINX` depends on platform V4L drivers, `VIDEO_DEV`, OF, and DMA; `VIDEO_XILINX_CSI2RXSS` depends on the base driver; `VIDEO_XILINX_TPG` depends on the base and selects `VIDEO_XILINX_VTC`; `VIDEO_XILINX_VTC` depends on the base. The help texts identify the composite pipeline, MIPI CSI-2 Rx subsystem, test pattern generator, and video timing controller.

Control flow/state: no runtime logic; Kconfig controls which objects are compiled and which helper symbols are pulled into a kernel build. Dependencies integrate with the media subsystem and device-tree platforms.

Risks: missing `VIDEO_XILINX` prevents the CSI-2/TPG/VTC drivers from being available; missing selected media/vb2 dependencies breaks runtime registration or DMA queue support. Test signals are Kconfig dependency resolution for built-in/module builds and compile coverage for all enabled combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/Kconfig -->

## sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/Makefile
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/Makefile -->
# Research: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/Makefile

Purpose: maps Xilinx media Kconfig symbols to build objects. The composite `xilinx-video` module is built from `xilinx-dma.o`, `xilinx-vip.o`, and `xilinx-vipp.o`.

Important build outputs: `obj-$(CONFIG_VIDEO_XILINX) += xilinx-video.o`, `obj-$(CONFIG_VIDEO_XILINX_CSI2RXSS) += xilinx-csi2rxss.o`, `obj-$(CONFIG_VIDEO_XILINX_TPG) += xilinx-tpg.o`, and `obj-$(CONFIG_VIDEO_XILINX_VTC) += xilinx-vtc.o`.

Control flow/state: no runtime state; this file controls link composition. Integration risk is mostly symbol linkage: `xilinx-dma.c`, `xilinx-vip.c`, and `xilinx-vipp.c` must be linked together because the composite driver calls exported/shared helper routines. Test signals are module build success for each enabled symbol and modpost verification of exported symbol use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/Makefile -->

## sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-csi2rxss.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-csi2rxss.c -->
# Research: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-csi2rxss.c

Purpose: V4L2 subdevice driver for the Xilinx MIPI CSI-2 Rx Subsystem. It accepts a CSI-2 sensor stream on a sink pad, converts it to AXI4-Stream on a source pad, manages reset/clock/interrupt resources, validates device-tree data type/lane configuration, and exposes status logging.

Important types and APIs: `struct xcsi2rxss_state` stores subdev, active/default formats, interrupt counters, remote subdev, reset GPIO, bulk clocks, MMIO base, max lanes, configured CSI-2 data type, mutex, pads, and streaming flags. Key routines include register helpers, `xcsi2rxss_soft_reset/hard_reset`, `xcsi2rxss_irq_handler`, `xcsi2rxss_s_stream`, format get/set/enumeration, `xcsi2rxss_log_status`, `xcsi2rxss_parse_of`, `probe`, and `remove`.

Control flow: probe validates OF properties such as `xlnx,csi-pxl-format`, `xlnx,vfb`, `xlnx,en-csi-v2-0`, `xlnx,en-vcx`, active lanes, and both graph endpoints; maps registers; requests an IRQ; gets and enables `lite_aclk` and `video_aclk`; resets the core; initializes two media pads and the default format; then registers the subdevice. Stream-on enables the core, soft-resets, enables interrupt masks, marks streaming, finds the remote sensor subdev, and starts it. Stream-off calls remote `s_stream(0)`, disables IRQs/core, clears streaming, and hard-resets through GPIO.

State and persistence: active format is stored in `state->format`; TRY formats live in subdev state. Event counters accumulate IRQ events until reset at stream-on and are printed by `log_status`. Hardware state lives in CSI-2 registers and is not persisted across driver unload.

Dependencies and integration: uses V4L2 fwnode CSI-2 endpoint parsing, MIPI CSI-2 data type constants, media entity link validation, GPIO reset, bulk clocks, platform MMIO/IRQ, and Xilinx VIP pad IDs. It registers for compatible `xlnx,mipi-csi2-rx-subsystem-5.0`.

Risks: `rsubdev` can be NULL if no remote subdev is linked when streaming starts, yet the stream path calls it. Lane/data-type properties are strict, and operation without video frame buffer is rejected. Stream-line-buffer-full disables core/interrupts in IRQ context and relies on stream-off reset for recovery. Test signals include DT validation failures, `media-ctl` graph links, `v4l2-compliance` subdev formats, IRQ counter/status logging under error injection, and sensor-to-DMA streaming with RAW/YUV/RGB formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-csi2rxss.c -->

## sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-dma.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-dma.c -->
# Research: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-dma.c

Purpose: implements V4L2 video-node DMA endpoints for Xilinx video pipelines. It registers capture/output video devices, owns vb2 queues, verifies format consistency against the connected subdevice, submits interleaved DMAEngine transfers, and coordinates media pipeline stream state across one output DMA and at most one input DMA.

Important APIs/types: `struct xvip_dma_buffer` wraps `vb2_v4l2_buffer`; `xvip_dma_init/cleanup` are exported to the composite driver. Core helpers are `xvip_dma_remote_subdev`, `xvip_dma_verify_format`, `xvip_pipeline_start_stop`, `xvip_pipeline_prepare/cleanup/set_stream`, vb2 ops, and V4L2 ioctl ops for querycap, enum/get/set/try format, buffers, and stream on/off.

Control flow: initialization sets default YUYV 1920x1080 format, creates a one-pad media entity, configures video_device/vb2 queue, requests DMA channel `port%u`, computes alignment, and registers the video node. Buffer queueing fills a `dma_interleaved_template` for capture or output, computes line size/interline gap from format and bytesperline, prepares a DMA descriptor, records the buffer on a spinlocked queue, submits, and issues pending when streaming. Start streaming starts the media pipeline, verifies remote format, validates pipeline topology, starts pending DMA, then starts upstream subdevices. Stop streaming stops subdevices, terminates DMA, cleans pipeline state, stops media pipeline, and returns queued buffers as error.

State and persistence: per-DMA state includes active pixel format, format info, sequence counter, queued buffer list, DMA channel, and embedded pipeline object. `xvip_pipeline` tracks `use_count`, `stream_count`, `num_dmas`, and output DMA under a mutex. No persistent storage is used.

Dependencies and integration: uses DMAEngine interleaved API, Xilinx DMA channel naming, media-controller pipeline API, V4L2 video_device/vb2, contiguous DMA memory, and shared `xilinx-vip` format helpers.

Risks: pipeline start ignores the return from `xvip_pipeline_set_stream`, so a subdevice start failure after DMA issue may not propagate. Format verification requires exact code/size/colorspace match and returns `-EINVAL`/`-EPIPE` for graph mismatch. Buffer completion removes queued entries under spinlock; descriptor preparation failures must return buffers as error. Test signals include `v4l2-compliance` on capture/output nodes, DMAEngine failure paths, media pipeline topology validation, stream-on/off sequencing with one or two DMA endpoints, and mismatched subdev format rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-dma.c -->

## sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-dma.h
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-dma.h -->
# Research: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-dma.h

Purpose: declares the Xilinx video DMA endpoint and pipeline data structures shared between the composite device and DMA implementation.

Important types: `struct xvip_pipeline` embeds `media_pipeline` plus mutex-protected use and stream counters, number of DMA engines, and the output DMA pointer. `struct xvip_dma` owns list linkage, `video_device`, media pad, parent composite device, embedded pipeline, DT port, format/fmtinfo, vb2 queue, sequence counter, queued buffer list and spinlock, DMAEngine channel, alignment, and interleaved transfer template/chunk. The `to_xvip_dma` and `to_xvip_pipeline` helpers convert from V4L2 objects.

Control flow and state are implemented by `xvip_dma_init()` and `xvip_dma_cleanup()` declared here. Dependencies include DMAEngine, V4L2/vb2, media entities, mutexes, spinlocks, and composite/format forward declarations.

Risks: structure fields are shared across stream, queue, and graph code, so lock ownership matters: `lock` protects format/queue state, `queued_lock` protects queued buffers, and pipeline lock protects counters. Test signals are build compatibility for users of these structures and runtime stream lifecycle coverage in `xilinx-dma.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-dma.h -->

## sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-tpg.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-tpg.c -->
# Research: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-tpg.c

Purpose: V4L2 subdevice driver for the Xilinx Video Test Pattern Generator. It can be a source-only pattern generator or a two-pad passthrough/pattern block, exposes many V4L2 controls for pattern features, optionally drives a Xilinx VTC timing generator, and supports PM suspend/resume of the core.

Important types/APIs: `struct xtpg_device` embeds `xvip_device`, pads, active formats, parsed VIP format, Bayer state, control handler and controls, streaming flag, optional `xvtc_device`, and optional timing mux GPIO. Key functions are `xtpg_parse_of`, `xtpg_probe/remove`, `xtpg_s_stream`, format get/set/enumeration, `xtpg_s_ctrl`, pattern control range helpers, PM callbacks, and VTC calls.

Control flow: probe parses one or two graph ports and requires matching Xilinx VIP formats, initializes MMIO/clock resources, optional timing GPIO and `xlnx,vtc` phandle, resets the core, builds pads and default format from hardware frame size, creates standard/custom controls, sets initial controls, and registers the subdev. Stream-on writes frame size, optionally configures VTC blanking/sync timing from hblank/vblank controls, locks controls to choose passthrough versus test pattern, adjusts allowed pattern menu values during streaming, writes Bayer phase and timing mux, then enables the core. Stream-off disables the core, stops VTC, restores pattern controls, and clears streaming.

State and persistence: active formats are in `formats[]`, control values are in the V4L2 handler and mirrored into hardware registers by `xtpg_s_ctrl`, and `saved_ctrl` in `xvip_device` is used for PM suspend/resume. No disk persistence exists.

Dependencies and integration: uses shared Xilinx VIP register helpers, VTC provider API, Xilinx custom V4L2 controls, OF graph format properties, optional GPIO, media entity link validation, and async subdev registration for compatible `xlnx,v-tpg-5.0`.

Risks: two-pad mode assumes source format mirrors sink; switching between passthrough and generated pattern is blocked by control range changes only while streaming. `xvtc_of_get()` can defer probe. Bayer phase must be disabled for passthrough on TPG v5.0. Test signals include control enumeration/range changes, pattern register writes, VTC timing output, passthrough with timing mux, Bayer formats, PM suspend/resume, and `media-ctl`/`v4l2-compliance` subdev checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-tpg.c -->

## sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vip.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vip.c -->
# Research: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vip.c

Purpose: shared helper library for Xilinx Video IP drivers. It maps Xilinx AXI4 video formats to media-bus codes and V4L2 fourccs, provides register read/modify/write helpers through the header, initializes common MMIO/clock resources, and supplies generic subdev enum helpers.

Important APIs: exported functions are `xvip_get_format_by_code`, `xvip_get_format_by_fourcc`, `xvip_of_get_format`, `xvip_set_format_size`, `xvip_clr_or_set`, `xvip_clr_and_set`, `xvip_init_resources`, `xvip_cleanup_resources`, `xvip_enum_mbus_code`, and `xvip_enum_frame_size`. The static `xvip_video_formats[]` table covers YUV, RGB, monochrome, and Bayer formats with bpp/fourcc metadata.

Control flow: format lookup scans the static table; OF parsing reads `xlnx,video-format`, `xlnx,video-width`, and optional `xlnx,cfa-pattern`; resource initialization maps BAR/resource 0 and enables the device clock; enum helpers report the currently configured TRY format code and min/max frame sizes for simple sink/source subdevices.

State and persistence: no global mutable state. Per-device state is in `struct xvip_device`, especially `iomem`, `clk`, and `saved_ctrl` handled by header inline helpers.

Dependencies and integration: uses platform resource mapping, common clock framework, device-tree properties, dt-bindings `xilinx-vip.h`, V4L2 subdev states, and exported GPL symbols consumed by Xilinx TPG/VTC/DMA/composite code.

Risks: format table incompleteness silently defaults fourcc lookup to YUYV; OF format mismatch returns errors that stop probing; `xvip_init_resources()` enables clocks but ignores `clk_prepare_enable()` return. Test signals include DT format parsing, all exported symbol users building as modules, format lookup coverage, and subdev enum behavior for TRY versus ACTIVE formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vip.c -->

## sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vip.h
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vip.h -->
# Research: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vip.h

Purpose: common Xilinx Video IP interface header. It defines width/height limits, standard sink/source pad IDs, common control/timing register offsets and bit masks, `struct xvip_device`, `struct xvip_video_format`, exported helper prototypes, and inline MMIO/core-control helpers.

Important APIs: `xvip_read/write/clr/set`, `xvip_reset/start/stop/suspend/resume`, `xvip_set_frame_size/get_frame_size`, `xvip_enable_reg_update/disable_reg_update`, and `xvip_print_version`. It also declares format lookup, OF parsing, format-size, enum, and resource-management helpers implemented in `xilinx-vip.c`.

Control flow/state: inline helpers directly manipulate memory-mapped registers. `xvip_suspend()` saves the control register and disables SW enable; `xvip_resume()` restores it with enable set. Frame-size helpers encode/decode width and height into `XVIP_ACTIVE_SIZE`.

Dependencies and integration: used by all Xilinx media drivers in this subset. Depends on Linux I/O accessors, clocks, V4L2 subdev types, and Xilinx DT binding format codes.

Risks: register masks encode 11-bit active size in this header while some blocks use wider VTC limits; callers must use block-specific limits where needed. Direct read-modify-write helpers are not internally locked. Test signals include static compile coverage, register-level hardware tests for reset/start/stop, and PM tests that validate saved control restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vip.h -->

## sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vipp.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vipp.c -->
# Research: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vipp.c

Purpose: platform driver for the top-level Xilinx video composite device (`xlnx,video`). It creates the media device and V4L2 device, initializes DMA endpoints described by child port nodes, discovers all connected subdevices through the firmware graph, and creates media links when async binding completes.

Important types/APIs: `struct xvip_graph_entity` extends `v4l2_async_connection` with entity/subdev pointers. Key routines are graph parsing (`xvip_graph_parse_one`, `xvip_graph_parse`), DMA setup (`xvip_graph_dma_init_one/init`), link building (`xvip_graph_build_one`, `xvip_graph_build_dma`), notifier callbacks, composite V4L2/media init/cleanup, probe, and remove.

Control flow: probe allocates `xvip_composite_device`, initializes media/V4L2 devices, then calls graph init. DMA init scans `ports` children, reads `direction` and `reg`, creates capture or output `xvip_dma` nodes, and records capabilities. Graph parsing starts from the composite node and recursively adds remote subdevice fwnodes, skipping the composite itself. When all subdevices bind, the notifier builds subdev-to-subdev links from source pads, builds DMA-to-subdev links for composite endpoints, registers subdev nodes, and registers the media device.

State and persistence: runtime state is the V4L2/media device, async notifier lists, and list of DMA endpoints. No persistent state. DMA devices remain in `xdev->dmas` until cleanup.

Dependencies and integration: relies on OF graph/fwnode links, V4L2 async notifier, media-controller APIs, `xilinx-dma`, and child subdevice drivers such as TPG and CSI-2. Compatible is `xlnx,video`.

Risks: `xvip_graph_parse()` returns success when parsing the top-level graph fails, which can mask malformed graph failures until later empty/notifier checks. Link creation assumes firmware port numbers map to media pad indexes. DMA direction strings are inverted to V4L2 buffer type semantics and must match DT convention. Test signals include DT graph parsing with multiple subdevices, async bind completion, media topology inspection, DMA link direction validation, and cleanup after partial probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vipp.c -->

## sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vipp.h
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vipp.h -->
# Research: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vipp.h

Purpose: declares the composite Xilinx Video IP device state shared by the composite driver and DMA helpers.

Important type: `struct xvip_composite_device` contains `v4l2_device`, `media_device`, parent device pointer, V4L2 async notifier, DMA channel list, and aggregate V4L2 capability bits for querycap.

Control flow/state: this header has no functions; `xilinx-vipp.c` initializes media/V4L2/notifier state and `xilinx-dma.c` consumes `xdev` to register DMA video nodes and expose caps.

Dependencies and integration: includes Linux list/mutex and media/V4L2 async/control/device headers. The primary risk is stale assumptions about ownership of `dmas` and `v4l2_caps`. Test signals are build coverage and composite probe/remove tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vipp.h -->

## sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vtc.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vtc.c -->
# Research: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vtc.c

Purpose: platform driver and provider API for the Xilinx Video Timing Controller. It registers VTC instances globally so other Xilinx video blocks, notably TPG, can obtain them by `xlnx,vtc` phandle and start/stop timing generation.

Important APIs/types: `struct xvtc_device` embeds `xvip_device`, global list linkage, detector/generator flags, and generator config. Exported functions are `xvtc_of_get`, `xvtc_put`, `xvtc_generator_start`, and `xvtc_generator_stop`. Register definitions cover control, status, detector/generator timing blocks, polarity, active size, frame size, sync, blanking, and frame sync.

Control flow: probe parses `xlnx,detector`/`xlnx,generator`, initializes common Xilinx resources, prints version, and adds the device to a global mutex-protected list. `xvtc_of_get()` parses the consumer phandle and returns a matching registered VTC or `-EPROBE_DEFER`. Generator start enables the clock, writes active-high polarity, default encoding, active/frame/sync timing registers, then enables generator and register update. Stop clears control and disables the clock.

State and persistence: global `xvtc_list` is runtime registry state; per-device state includes capabilities and MMIO/clock. No persistent state. `xvtc_put()` is currently empty because lookup does not take references.

Dependencies and integration: uses common clock, OF phandles, Xilinx VIP MMIO helpers, and platform driver compatible `xlnx,v-tc-6.1`. Consumers must handle probe deferral.

Risks: `xvip_init_resources()` already enables the clock, and `xvtc_generator_start()` prepares/enables it again; reference balancing depends on matching stop/remove paths. No validation clamps `xvtc_config` fields against masks. Test signals include phandle lookup ordering, TPG-driven timing generation, detector/generator property combinations, and repeated start/stop/remove cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vtc.c -->

## sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vtc.h
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vtc.h -->
# Research: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vtc.h

Purpose: public provider interface for Xilinx VTC consumers. It defines maximum horizontal/vertical sizes, the `struct xvtc_config` timing payload, an opaque `struct xvtc_device`, and get/put/start/stop prototypes.

Important API: `xvtc_of_get(struct device_node *np)` resolves a consumer's `xlnx,vtc` phandle; `xvtc_generator_start()` programs blanking/sync/frame sizes from `xvtc_config`; `xvtc_generator_stop()` disables generation; `xvtc_put()` is a placeholder release hook.

Control flow/state is implemented in `xilinx-vtc.c`. Dependencies are minimal forward declarations, allowing consumers such as TPG to avoid internal register knowledge.

Risks: consumers must populate timing fields consistently and handle `NULL` for no VTC versus `ERR_PTR()` for deferral/error. Test signals are compile coverage for consumers and runtime phandle/provider tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-vtc.h -->

## sources/distributed-fs/ceph-client/drivers/media/radio/Kconfig
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/Kconfig -->
# Research: sources/distributed-fs/ceph-client/drivers/media/radio/Kconfig

Purpose: defines configuration entries for radio receiver/transmitter drivers in the media subsystem, including USB, PCI, I2C, MFD-backed, TEA575x, and legacy ISA boards.

Important entries in this subset: `RADIO_ADAPTERS` gates all radio adapters. USB entries include `USB_DSBR`, `USB_KEENE`, `USB_MA901`, `USB_MR800`, and `USB_RAREMONO`. ISA support is gated by `V4L_RADIO_ISA_DRIVERS`, with board symbols such as `RADIO_AZTECH`, `RADIO_CADET`, `RADIO_GEMTEK`, `RADIO_RTRACK`, and helper `RADIO_ISA`. `RADIO_MAXIRADIO` depends on PCI/HAS_IOPORT and selects `RADIO_TEA575X`.

Control flow/state: no runtime code; symbols drive which drivers and helper objects are built and whether fixed I/O port configuration prompts are exposed.

Dependencies and integration: depends broadly on `VIDEO_DEV`, `MEDIA_RADIO_SUPPORT`, bus features (`USB`, `PCI`, `I2C`, `ISA`, `HAS_IOPORT`), and helper libraries such as TEA575x or `radio-isa`.

Risks: many legacy ISA drivers can be built for `COMPILE_TEST`, but real hardware needs correct I/O ports and sometimes unsafe probing. Test signals are Kconfig dependency checks, allmodconfig/COMPILE_TEST builds, and symbol-to-Makefile consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/Kconfig -->

## sources/distributed-fs/ceph-client/drivers/media/radio/Makefile
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/Makefile -->
# Research: sources/distributed-fs/ceph-client/drivers/media/radio/Makefile

Purpose: maps radio driver Kconfig symbols to object files and subdirectories. It keeps entries alphabetically sorted by Kconfig name.

Important mappings in this subset: `CONFIG_RADIO_ISA` builds `radio-isa.o`; `CONFIG_RADIO_AZTECH`, `RADIO_CADET`, `RADIO_GEMTEK`, `RADIO_RTRACK`, and `RADIO_MAXIRADIO` build their respective drivers; `CONFIG_USB_DSBR`, `USB_KEENE`, and `USB_MA901` build USB drivers. `shark2-objs` composes a multi-object driver outside this subset.

Control flow/state: no runtime state; it controls compilation/linking. Risks are stale Kconfig symbol names or missing helper object linkage. Test signals are build success for each symbol and `make W=1`/modpost coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/Makefile -->

## sources/distributed-fs/ceph-client/drivers/media/radio/dsbr100.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/dsbr100.c -->
# Research: sources/distributed-fs/ceph-client/drivers/media/radio/dsbr100.c

Purpose: USB V4L2 radio receiver driver for D-Link DSB-R100/Gemtek USB Radio 21. It controls only initialization, frequency, mute/on-off, and stereo-status reporting; audio remains analog through a sound card input.

Important types/APIs: `struct dsbr100_device` stores USB device, video/v4l2 devices, control handler, transfer buffer, lock, current frequency, stereo, and muted state. Device operations include `dsbr100_setfreq`, `dsbr100_start`, `dsbr100_stop`, `dsbr100_getstat`, V4L2 tuner/frequency ioctls, mute control, USB probe/disconnect, suspend/resume, and release.

Control flow: probe allocates device/buffer, registers V4L2 device and mute control, initializes video_device, stores `usb_set_intfdata`, defaults to muted at 87.5 MHz, and registers the radio node. Setting frequency clamps to 87.5-108 MHz and sends vendor control request `DSB100_TUNE` only if not muted. Mute toggles `DSB100_ONOFF`; unmute starts and retunes. Tuner status sends vendor GET_STATUS and interprets one bit as stereo. Disconnect mutes, unregisters the video node, marks V4L2 device disconnected, and drops the device reference.

State and persistence: current frequency, muted flag, and stereo flag are runtime memory; the USB device stores radio state while powered. No persistence after unplug.

Dependencies and integration: USB core, V4L2 radio/tuner controls, control events, mutex locking, and compatible USB VID/PID `04b4:1002`.

Risks: a single shared transfer buffer is protected by the video_device lock for file ops, but suspend/resume/disconnect must also take that lock. Signal strength is synthesized from stereo only. Test signals include `v4l2-compliance`, tune/mute suspend/resume cycles, disconnect during open file, and USB control-message error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/dsbr100.c -->

## sources/distributed-fs/ceph-client/drivers/media/radio/lm7000.h
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/lm7000.h -->
# Research: sources/distributed-fs/ceph-client/drivers/media/radio/lm7000.h

Purpose: inline bit-bang helper for Sanyo LM7000 tuner chips used by several ISA FM radio drivers. It converts a V4L2 frequency to the LM7000 24-bit register payload and emits DATA/CLOCK/CE transitions through a caller-supplied pin callback.

Important API: `lm7000_set_freq(u32 freq, void *handle, void (*set_pins)(void *, u8))`. It defines pin masks `LM7000_DATA`, `LM7000_CLK`, `LM7000_CE` and mode bits for FM spacing and FM mode.

Control flow: adds 10.7 MHz IF, converts to 25 kHz units, ORs FM mode bits, then shifts 24 bits LSB-first. For each bit it calls `set_pins` with CE and optional DATA, pulses CLK with 2 us delays, then clears pins at the end.

State and persistence: no stored state; hardware state changes in the attached tuner. Dependencies are `udelay` and the caller's GPIO/I/O-port callback.

Risks: frequency unit assumptions must match V4L2 low-frequency units and the target board wiring. Callback errors cannot be reported because the callback is void. Test signals are tuning success on LM7000-based boards and scope/logic-analyzer verification of bit order and timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/lm7000.h -->

## sources/distributed-fs/ceph-client/drivers/media/radio/radio-aimslab.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-aimslab.c -->
# Research: sources/distributed-fs/ceph-client/drivers/media/radio/radio-aimslab.c

Purpose: ISA driver for AIMSlab RadioTrack/RadioReveal FM cards using the `radio-isa` framework and LM7000 tuner helper.

Important types/APIs: `struct rtrack` extends `radio_isa_card` with current analog volume. It implements `alloc`, `init`, `s_mute_volume`, `s_frequency`, and `g_signal` callbacks. Module parameters are `io[]` and `radio_nr[]`; accepted ports are `0x20f` and `0x30f`.

Control flow: module init registers an ISA driver with max two instances. The common framework allocates the card, claims I/O, registers V4L2 controls/device, then calls `rtrack_initialize`, initial frequency/stereo setup, and video registration. Frequency programming calls `lm7000_set_freq` with `rtrack_set_pins`, which maps LM7000 bits to card I/O pins while preserving volume/mute bits. Volume uses timed up/down pulses and a cached `curvol`; mute writes a fixed off pattern.

State and persistence: current volume is runtime memory; hardware volume is analog and changed by timed pulses. Frequency and stereo state are tracked by `radio-isa`.

Dependencies and integration: `radio-isa`, `lm7000`, ISA I/O ports, V4L2 controls. Risks include timed analog volume drift, long initialization delay, and no autodetect probe callback. Test signals include `v4l2-compliance`, tune/mute/volume controls, signal bit reading, and unload muting by `radio-isa`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-aimslab.c -->

## sources/distributed-fs/ceph-client/drivers/media/radio/radio-aztech.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-aztech.c -->
# Research: sources/distributed-fs/ceph-client/drivers/media/radio/radio-aztech.c

Purpose: ISA V4L2 radio driver for Aztech/Packard Bell radio cards, implemented through `radio-isa` plus the LM7000 tuner helper.

Important details: `struct aztech` extends the generic card with `curvol`. Callbacks implement allocation, mute/volume, frequency setting, stereo/mono status, and signal status. Ports are module-configurable, with valid values `0x350` and `0x358`; region size is 8.

Control flow: the `radio-isa` framework handles probe/registration. Frequency setting bit-bangs the LM7000 with `aztech_set_pins`, mixing current two-bit volume with tuner CE/CLK/DATA bits. Mute maps to volume zero; volume is encoded into bits 0 and 2. Status reads `AZTECH_BIT_MONO` and `AZTECH_BIT_NOT_TUNED`.

State and persistence: runtime `curvol` is mirrored to I/O bits and reused while clocking tuner data. The framework stores frequency and stereo choice. No persistent state.

Dependencies and integration: ISA I/O, `radio-isa`, V4L2 tuner API, `lm7000`. Risks are minimal volume granularity, no hardware probe callback, and read-bit polarity assumptions. Test signals are valid-port handling, tuner programming, mute/volume controls, mono/stereo reporting, and signal status under tuned/untuned stations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-aztech.c -->

## sources/distributed-fs/ceph-client/drivers/media/radio/radio-cadet.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-cadet.c -->
# Research: sources/distributed-fs/ceph-client/drivers/media/radio/radio-cadet.c

Purpose: standalone ISA V4L2 driver for the ADS Cadet AM/FM/RDS card. Unlike most ISA FM drivers here, it supports AM and FM bands, RDS read capture, PnP/probing, and custom file operations.

Important types/APIs: global `struct cadet cadet_card` stores V4L2/video devices, control handler, I/O port, AM/FM band flag, current frequency, tune/signal state, wait queue, RDS polling timer, ring buffer indexes, mutex, and read state. Key functions include `cadet_gettune/getfreq/settune/setfreq`, RDS timer/read/poll helpers, V4L2 tuner/frequency/band ioctls, mute control, PnP probe, unsafe I/O probing, module init, and exit.

Control flow: init optionally registers PnP, falls back to probing a fixed list of ports by tuning/reading back FM frequency, claims a two-byte I/O region, registers V4L2 device/control/video node, defaults to FM low frequency, and tunes hardware. Frequency setting chooses AM versus FM by midpoint, encodes a 25-bit FIFO command, tries four tuning sensitivity values, updates signal strength from a table, and resets RDS. RDS starts lazily on read/poll, uses a 50 ms timer to drain the hardware FIFO into a 256-byte ring, wakes readers, and stops the timer when the last file is released.

State and persistence: all driver state is global single-device memory. RDS state persists while a file is open. Hardware frequency/mute persists until retuned or module exit mutes the device.

Dependencies and integration: ISA I/O, optional PnP IDs, V4L2 tuner/frequency-band/RDS capture APIs, timers, wait queues, and control events.

Risks: single global instance, unsafe port probing, ring-buffer index wrap relies on 8-bit fields and simple overflow handling, timer uses trylock and reschedules continuously while active, and read copies at most a stack `RDS_BUFFER`. Test signals include AM/FM band enumeration, RDS read/poll blocking and nonblocking behavior, PnP and manual I/O selection, tune readback, unload timer cleanup, and `v4l2-compliance` including RDS capability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-cadet.c -->

## sources/distributed-fs/ceph-client/drivers/media/radio/radio-gemtek.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-gemtek.c -->
# Research: sources/distributed-fs/ceph-client/drivers/media/radio/radio-gemtek.c

Purpose: ISA/optional PnP V4L2 driver for GemTek radio cards and compatibles, using the shared `radio-isa` framework but implementing its own BU2614/BU2614FS serial protocol.

Important types/APIs: `struct gemtek` extends `radio_isa_card` with muted state and cached 32-bit BU2614 data word. It implements callbacks for allocation, optional I/O probing, mute/volume, frequency, and rxsubchans. Module parameters control automatic probing, `hardmute`, fixed I/O ports, and radio node numbers. Valid ports include `0x20c`, `0x30c`, `0x24c`, `0x34c`, `0x248`, and `0x28c`.

Control flow: probe may automatically test candidate ports by toggling CE/CK/DA and checking echoed bus bits. Frequency calculation adds IF offset and reference divisor scaling, fills BU2614 fields, and serializes 32 bits over I/O pins. Mute either toggles line mute or, with `hardmute`, shuts down the PLL and skips retuning while muted. Module exit sets `hardmute = true` before unregistering to force PLL off.

State and persistence: cached BU2614 data and mute state are runtime memory; `radio-isa` stores current frequency. Hardware PLL/mute state persists until changed or module exit.

Dependencies and integration: ISA I/O, optional PnP ID `ADS7183`, `radio-isa`, V4L2 controls. Risks include reverse-engineered timing/probing, hardmute changing frequency behavior, and stereo status inferred from the no-signal bit. Test signals include port autodetection, hardmute on/off retuning, PnP registration, unload PLL-off behavior, and V4L2 tuner/mute compliance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-gemtek.c -->

## sources/distributed-fs/ceph-client/drivers/media/radio/radio-isa.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-isa.c -->
# Research: sources/distributed-fs/ceph-client/drivers/media/radio/radio-isa.c

Purpose: framework that supplies V4L2 scaffolding for legacy ISA radio drivers. Board-specific drivers provide hardware callbacks while this file handles device allocation flow, I/O region ownership, V4L2 device/video registration, standard radio ioctls, controls, optional PnP, and removal.

Important APIs: exported functions are `radio_isa_match`, `radio_isa_probe`, `radio_isa_remove`, and under PnP `radio_isa_pnp_probe/remove`. V4L2 operations include querycap, tuner get/set, frequency get/set, log status, control subscribe/unsubscribe, and mute/volume control handling.

Control flow: match succeeds if probing is enabled or an explicit I/O parameter exists. Probe allocates a board card through `ops->alloc`, optionally scans candidate ports with `ops->probe`, validates the selected port, then calls common probe. Common probe claims the I/O region, registers V4L2 device, creates mute and optional volume controls, initializes the video device, calls board `init`, sets up controls, programs default low FM frequency and stereo mode, and registers a radio video node. Removal mutes the card, unregisters the video device, frees controls/V4L2 device, releases I/O, and frees memory.

State and persistence: `struct radio_isa_card` holds current frequency, stereo mode, mute/volume controls, V4L2/video objects, mutex, and I/O port. State is runtime only; hardware may remain in last frequency/mute until removal.

Dependencies and integration: ISA bus registration, optional PnP, V4L2 control/event APIs, board callbacks in `radio_isa_ops`, and valid I/O-port lists in `radio_isa_driver`.

Risks: failure paths must free allocated card correctly; `radio_isa_probe` returns `-ENODEV` without freeing `isa` when `isa->io < 0`, which is a leak risk in that path. Only mute control changes call `s_mute_volume`; clustered volume updates rely on V4L2 control behavior. Test signals include board-driver registration, invalid/valid I/O parameters, probe scanning, PnP probe/remove, default frequency setup, mute-on-remove, and `v4l2-compliance` for radio ioctls/events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-isa.c -->

## sources/distributed-fs/ceph-client/drivers/media/radio/radio-isa.h
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-isa.h -->
# Research: sources/distributed-fs/ceph-client/drivers/media/radio/radio-isa.h

Purpose: shared interface for ISA radio board drivers. It defines the generic card structure, board callback table, top-level driver descriptor, and exported framework entry points.

Important types: `struct radio_isa_card` contains driver pointer, V4L2 device/control/video objects, lock, ops pointer, mute/volume controls, I/O port, stereo flag, and current frequency. `struct radio_isa_ops` contains board callbacks for allocation, probe, init, mute/volume, frequency, stereo, rxsubchans, and signal. `struct radio_isa_driver` wraps an `isa_driver`, optional `pnp_driver`, module parameter arrays, probe/port metadata, region size, card name, stereo flag, and max volume.

Control flow/state is implemented in `radio-isa.c`; board drivers instantiate a static `radio_isa_driver` and call `isa_register_driver`. Dependencies include ISA, optional PnP, V4L2 device/control headers.

Risks: callback contracts are not type-enforced beyond signatures; required callbacks such as `s_mute_volume` and `s_frequency` must be present for the framework paths. Test signals are compile coverage for all board users and runtime board probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-isa.h -->

## sources/distributed-fs/ceph-client/drivers/media/radio/radio-keene.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-keene.c -->
# Research: sources/distributed-fs/ceph-client/drivers/media/radio/radio-keene.c

Purpose: USB V4L2 modulator driver for the Keene FM transmitter. It exposes a transmit radio node that sets FM frequency, mute/play state, stereo/mono, power level, preemphasis, and compression gain through HID-style USB control reports.

Important types/APIs: `struct keene_device` stores USB/V4L2/video/control state, mutex, 8-byte report buffer, current frequency, TX/gain/PA settings, stereo, mute, and preemphasis flags. Core functions are `keene_cmd_main`, `keene_cmd_set`, V4L2 modulator/frequency/control ioctls, USB probe/disconnect, suspend/resume, and release.

Control flow: probe filters a shared Logitech VID/PID by product string, allocates state/buffer, creates four controls, registers V4L2/video, stores the V4L2 device in USB interface data, waits for hardware settle, sends an initial idle command at 95.16 MHz, registers the radio node, and sets controls. Frequency and mute call `keene_cmd_main`; stereo/preemphasis/compression call `keene_cmd_set`; resume replays mode and frequency after delay.

State and persistence: runtime state mirrors desired transmitter settings and current frequency. Hardware may preserve settings while powered but the driver replays them on resume. No disk persistence.

Dependencies and integration: USB HID-class interface matching, V4L2 modulator API (`VFL_DIR_TX`), controls for tune power/preemphasis/compression, and control events.

Risks: shared USB ID makes product-string filtering critical. Power-level conversion writes a computed register value and leaves `db2tx` index dependent on control step/min. Suspend/resume do not take the mutex, unlike normal file ops. Test signals include real-device product filtering, modulator ioctls, control range tests, suspend/resume replay, mute/play behavior, and disconnect while open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-keene.c -->

## sources/distributed-fs/ceph-client/drivers/media/radio/radio-ma901.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-ma901.c -->
# Research: sources/distributed-fs/ceph-client/drivers/media/radio/radio-ma901.c

Purpose: USB V4L2 radio receiver driver for the Masterkit MA901 FM radio. It controls frequency, volume, and mono/stereo mode for a V-USB HID-class device with analog audio output.

Important types/APIs: `struct ma901radio_device` stores USB/interface, video/V4L2/control objects, report buffer, mutex, current frequency, volume, stereo mode, and muted flag. Core routines are `ma901radio_set_freq`, `ma901radio_set_volume`, `ma901_set_stereo`, tuner/frequency/control ioctls, USB probe/disconnect, no-op suspend/resume, and release.

Control flow: probe filters a generic VID/PID by product/manufacturer strings, allocates state/buffer, registers V4L2 and a volume control, initializes video_device, stores V4L2 device in USB interface data, defaults current frequency to about 95.21 MHz, and registers the radio node without querying hardware. Setting frequency/volume/stereo fills an 8-byte command report and sends USB control request 9 with type 0x21 and value 0x0300.

State and persistence: driver caches frequency, volume, and stereo mode; comments note the radio has device memory and continues playing if USB power remains. No persistent software state.

Dependencies and integration: USB HID-class matching, V4L2 tuner/radio APIs, volume controls. Risks include generic V-USB ID collisions, unimplemented mute/statistics, no real suspend/resume restoration, and `g_frequency` not setting `f->type`. Test signals include product/manufacturer filtering, frequency clamp, volume control, mono/stereo ioctl behavior, unplug while open, and `v4l2-compliance`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-ma901.c -->

## sources/distributed-fs/ceph-client/drivers/media/radio/radio-maxiradio.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-maxiradio.c -->
# Research: sources/distributed-fs/ceph-client/drivers/media/radio/radio-maxiradio.c

Purpose: PCI V4L2 radio driver for the Guillemot Maxi Radio FM2000/Gemtek PCI FM-style card. It delegates tuner behavior to the shared TEA575x interface and implements board-specific PCI I/O pin access.

Important types/APIs: `struct maxiradio` stores `snd_tea575x`, V4L2 device, PCI device pointer, and I/O base. Board callbacks are `maxiradio_tea575x_set_pins`, `get_pins`, and `set_direction`. PCI entry points are `maxiradio_probe/remove`; IDs use vendor `0x5046` and device `0x1001`.

Control flow: probe allocates state, names/registers a V4L2 device, initializes TEA575x private data/ops/card/radio number, reserves PCI I/O region, enables PCI device, stores I/O base, and calls `snd_tea575x_init` to detect/register the tuner radio node. Remove exits TEA575x, powers off the card by writing zero, unregisters V4L2, releases region, and frees state.

State and persistence: TEA575x framework owns most radio state; this driver stores only I/O base and V4L2/PCI objects. Hardware is powered through an output bit and turned off on removal.

Dependencies and integration: PCI core, I/O ports, `RADIO_TEA575X` helper, V4L2 device. Risks include inability to read TEA data (`cannot_read_data = true`), no `pci_set_drvdata()` visible in this file before remove retrieves driver data, and comments note frequency changes may unmute. Test signals include PCI probe/remove, I/O resource conflict handling, TEA575x detection, mono/stereo pin read, and remove power-off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/radio-maxiradio.c -->

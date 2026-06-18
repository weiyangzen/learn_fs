# Research: subset-b-004172

## Scope

TI media platform drivers under `drivers/media/platform/ti`, covering CAL CSI-2 capture, DaVinci VPIF capture/display, J721E CSI2RX shim capture, and OMAP/DaVinci build integration.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal-video.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal-video.c

## Purpose

This file exposes each CAL DMA context as a V4L2 capture video node. It implements the ioctl surface, video buffer queue management, media-controller links, and stream start/stop glue between userspace buffers, the CAMERARX subdevice, and the CAL context programming helpers in `cal.c`.

## Important APIs, types, and functions

- `cal_ioctl_legacy_ops` and `cal_ioctl_mc_ops` define two user APIs: legacy direct camera capture and media-controller-centric capture selected by `cal_mc_api`.
- `cal_ctx_v4l2_init()`, `cal_ctx_v4l2_register()`, `cal_ctx_v4l2_unregister()`, and `cal_ctx_v4l2_cleanup()` own video-device, media-entity, control-handler, and vb2 setup/teardown for a `struct cal_ctx`.
- `cal_legacy_*` functions negotiate formats through the remote source subdevice, enumerate inputs/frame sizes/intervals, and forward stream parameters to the camera source.
- `cal_mc_*` functions expose local format enumeration and range clamping when pipeline configuration is handled through media controller links.
- `cal_queue_setup()`, `cal_buffer_prepare()`, `cal_buffer_queue()`, `cal_start_streaming()`, and `cal_stop_streaming()` are the vb2 operations.

## Control flow

Initialization builds a DMA queue and `video_device`, attaches the vb2 queue, initializes a single sink pad, and optionally initializes a control handler for legacy mode. Registration initializes the default/current format, registers `/dev/video*`, and creates media links. In legacy mode the video node is linked immutably to its matched CAMERARX; in MC mode every video node gets links from every CAMERARX source pad, with only the default context-to-phy links enabled.

Format negotiation differs by API mode. Legacy mode enumerates source subdevice bus codes, keeps only matching CAL formats in `active_fmt`, calls subdevice `get_fmt`/`set_fmt`, and mirrors subdevice colorspace/field/size into `ctx->v_fmt`. MC mode accepts any non-meta entry in `cal_formats`, clamps dimensions and stride to CAL DMA limits, and relies on link validation at stream-on to ensure the upstream subdevice matches.

Streaming starts by requiring a connected remote pad, starting the media pipeline, resolving `ctx->phy` in MC mode, validating format compatibility against the CAMERARX source pad, preparing CAL context state, taking the first queued buffer, resuming runtime PM, programming the DMA address, starting CAL, and enabling streams on the CAMERARX subdevice. Stop reverses that: stop CAL, disable subdevice streams, put runtime PM, release pixel-processing resources, return buffers with error, stop the media pipeline, and clear `ctx->phy` in MC mode.

## State and persistence behavior

The file stores runtime-only state in `struct cal_ctx`: selected `v_fmt`, `fmtinfo`, legacy `active_fmt`, vb2 queue, media pad, lock, and `cal_dmaqueue`. Buffers flow through `dma.queue`, `dma.pending`, and `dma.active`, guarded by `dma.lock`; queued buffers are returned as `QUEUED`, `DONE`, or `ERROR` depending on start failure, IRQ completion, or stop. No disk persistence exists.

## Dependencies and integration points

It depends on V4L2 core, media controller, videobuf2 DMA-contig, V4L2 subdev pad ops, runtime PM, and the CAL internals declared in `cal.h`. Its stream lifecycle calls `cal_ctx_prepare()`, `cal_ctx_set_dma_addr()`, `cal_ctx_start()`, `cal_ctx_stop()`, and `cal_ctx_unprepare()` from `cal.c`, while receiving DMA completion through CAL IRQ handling in `cal.c`.

## Risks and edge cases

Format mismatch returns `-EPIPE` at stream-on; this is expected in MC mode if userspace configures inconsistent pads. The start path assumes at least one queued buffer, relying on vb2 `min_queued_buffers`. DMA stop errors return all buffers with `ERROR`. Legacy mode depends heavily on subdevice pad operations and rejects sources that do not enumerate a matching media-bus code. Stride and size calculations must stay aligned with hardware register limits; wrong `bpp` metadata can corrupt DMA geometry.

## Test signals

Useful validation includes `v4l2-compliance` for both API modes, media-ctl link and format tests for MC mode, streaming with at least three MMAP/DMABUF buffers, stop/start loops to exercise cleanup, and tests where upstream format intentionally mismatches the video node to confirm `-EPIPE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal.c

## Purpose

This is the main TI CAL platform driver. It defines supported pixel/media-bus formats, SoC-specific CAMERARX layout data, register access helpers, context programming, DMA IRQ handling, async subdevice binding, media/V4L2 registration, probe/remove, and runtime PM programming.

## Important APIs, types, and functions

- Module parameters `video_nr`, `debug`, and `mc_api` select video numbering, debug verbosity, and legacy vs media-controller API behavior.
- `cal_formats[]`, `cal_format_by_fourcc()`, and `cal_format_by_code()` provide the format registry shared with video and context setup.
- `cal_ctx_prepare()`, `cal_ctx_unprepare()`, `cal_ctx_start()`, `cal_ctx_stop()`, and `cal_ctx_set_dma_addr()` are the exported context lifecycle used by `cal-video.c`.
- `cal_irq()`, `cal_irq_wdma_start()`, and `cal_irq_wdma_end()` handle CAL error/status interrupts and move vb2 buffers through pending/active/done states.
- `cal_async_notifier_register()`, `cal_async_notifier_bound()`, and `cal_async_notifier_complete()` bind camera subdevices and register video nodes once sources are available.
- `cal_probe()`, `cal_remove()`, and `cal_runtime_resume()` own the platform-device lifecycle and runtime PM register programming.

## Control flow

Probe obtains match data for the compatible SoC, maps the top-level CAL registers and CAMERARX control regmap, requests the IRQ, enables runtime PM to read hardware revision, initializes media/V4L2 state, creates CAMERARX PHY subdevices, creates capture contexts, and registers the media device plus async notifier. Legacy API creates one context per connected PHY; MC API creates up to all context slots and lets media links select the active source.

When an async source binds, the driver locates the source pad from firmware endpoint data, creates an immutable enabled link from the source into the CAMERARX sink, and stores the source subdevice on the PHY. Notifier completion registers all context video nodes, and MC mode additionally registers subdevice nodes.

At stream prepare, the context reads the upstream frame descriptor if available to select CSI-2 virtual channel and data type; otherwise it uses VC 0 and any data type. Capture contexts reserve one of four pixel processors. Start increments per-PHY VC enable counts, resets VC sequence tracking when first used, programs CSI2 context, pixel processor, and write DMA registers, enables DMA start/end interrupts, and enables constant write-DMA mode. Stop requests DMA shutdown, waits up to 500 ms for IRQ-driven stopped state, force-disables on timeout, disables IRQs, clears CSI2/pixel processor registers, and releases the pixel processor.

## State and persistence behavior

All state is kernel runtime state: `struct cal_dev` holds mapped resources, SoC data, media/V4L2 devices, async notifier, PHYs, contexts, and reserved pixel-processor bitmask. `struct cal_camerarx` holds source endpoint information and per-VC frame sequence counters. `struct cal_ctx` holds current DMA context, cport, CSI2 context, VC, datatype, and buffer queue. The driver persists no state across unload or reboot.

## Dependencies and integration points

The driver integrates with platform OF matching, clocks, syscon/regmap for CAMERARX control, runtime PM, media controller, V4L2 async notifier, V4L2 subdevs, vb2 DMA-contig, and the CAMERARX helper implementation in `cal-camerarx.c`. It exports symbols used by `cal-video.c` and relies on register definitions from `cal_regs.h`.

## Risks and edge cases

The DMA interrupt path explicitly documents racy cases where start and end interrupts arrive together; embedded data under 10 lines uses a different ordering heuristic than normal frames. Pixel processor allocation can fail with `-ENOSPC`. DMA stop can time out and force disable hardware. Bad frame descriptors with multiple entries are rejected. Probe aborts if no port is configured. The DRA72 pre-ES2 LDO erratum must be applied every runtime resume for affected devices.

## Test signals

Probe/remove on each compatible (`ti,dra72-cal`, `ti,dra72-pre-es2-cal`, `ti,dra76-cal`, `ti,am654-cal`), runtime suspend/resume while streaming, stream-on/off loops, multi-context contention for pixel processors, CSI2 VC sequence tests, and debug register dumps at high `debug` levels are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal.h

## Purpose

This header defines the shared data model and helper interfaces for the TI CAL driver: device, CAMERARX PHY, capture context, DMA queue, format metadata, register access wrappers, debug macros, constants, and cross-file function prototypes.

## Important APIs, types, and functions

- Constants describe context counts, CSI2 ports, CAMERARX pads, and DMA width/height limits.
- `struct cal_format_info` maps V4L2 fourcc, media-bus code, bits per pixel, and metadata flag.
- `struct cal_dmaqueue` tracks queued, pending, and active capture buffers plus DMA state and stop wait queue.
- `struct cal_camerarx`, `struct cal_dev`, and `struct cal_ctx` model one PHY, whole CAL subsystem, and one CSI2/pixel/DMA capture context respectively.
- Inline helpers `cal_read()`, `cal_write()`, `cal_read_field()`, `cal_write_field()`, and `cal_set_field()` centralize MMIO and bitfield access.
- Prototypes expose format lookup, CAMERARX lifecycle, CAL context lifecycle, and V4L2 video-node lifecycle.

## Control flow

The header has no executable driver flow by itself, but it encodes the object relationships used by the implementation. Probe creates a `cal_dev`, creates `cal_camerarx` PHYs, then creates `cal_ctx` instances that reference both. Video nodes use `cal_ctx`, while IRQ and runtime PM paths operate through `cal_dev` and `cal_camerarx`.

## State and persistence behavior

The declared structures are in-memory driver state only. The most important mutable state is the DMA queue and state machine, per-VC frame sequence counters, reserved pixel processors, selected format, and currently selected source subdevice. No persistent storage is defined.

## Dependencies and integration points

It pulls in Linux bitfield, I/O, list, mutex, spinlock, waitqueue, V4L2, media-device, V4L2 async/control/subdev/fwnode, and vb2 V4L2 headers. It is the contract between `cal.c`, `cal-video.c`, and `cal-camerarx.c`.

## Risks and edge cases

Because the register helper macros do plain read/modify/write without internal locking, callers must use appropriate context locks when shared registers can be touched concurrently. `cal_rx_pad_is_source()` accepts pads up to `CAL_CAMERARX_NUM_SOURCE_PADS`, which is the last source-pad index because pad zero is the sink. DMA state and buffer pointer invariants must be preserved by all users of `struct cal_dmaqueue`.

## Test signals

Compile coverage is the primary signal for this header, plus runtime tests that stress every structure field: format negotiation, media link setup, VC sequence handling, DMA queue transitions, and CAMERARX pad routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal_regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal_regs.h

## Purpose

This header defines CAL and CSI2/CAMERARX register offsets, bit masks, enum values, interrupt masks, and the DRA72 pre-ES2 LDO erratum flag used by the CAL implementation.

## Important APIs, types, and functions

- `DRA72_CAL_PRE_ES2_LDO_DISABLE` documents and flags erratum i913 handling for affected DRA72 devices.
- Register offset macros cover high-level CAL control/IRQ registers, pixel processors, read/write DMA, CSI2 PPI/ComplexIO/VC/context/status, CSI2 PHY registers, and control-module CAMERARX control.
- Bit masks and field values cover revision decoding, HWINFO, IRQ status/enable, pixel extraction/packing, global control, DMA geometry/mode, CSI2 lane/PHY status, CSI2 virtual-channel IRQs, context DT/VC/CPORT/line fields, and CAMERARX control bits.

## Control flow

There is no direct control flow. The implementation composes these macros with `cal_set_field()` and `cal_write_field()` to program CAL context registers in `cal_ctx_*` functions, decode hardware revision in `cal_get_hwinfo()`, enable/clear interrupts in IRQ paths, and apply CAMERARX PHY errata.

## State and persistence behavior

The header itself has no state. It describes volatile MMIO state held by the hardware. Register writes affect active capture configuration and are reset by hardware/module lifecycle rather than persisted by software.

## Dependencies and integration points

It depends on Linux `BIT()`/`GENMASK()` definitions through including code. It is included by `cal.c` and must remain synchronized with the TI CAL hardware reference and the register helper functions in `cal.h`.

## Risks and edge cases

Incorrect bit masks or field constants can silently program wrong DMA sizes, data types, pixel packing, or interrupt enables. Several width/height fields are bounded by register width, which is why `cal-video.c` clamps formats. The erratum comment is operationally important: skipping LDO disable on affected silicon can cause high current draw.

## Test signals

Signals include successful probe revision/HWINFO reads, valid register dumps with `debug >= 4`, correct frame sizes/strides across 8/10/12/16 bpp formats, interrupt delivery for WDMA start/end, and hardware tests on affected DRA72 silicon for erratum handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/Kconfig

## Purpose

This Kconfig file defines build-time options for the TI DaVinci VPIF V4L2 display and capture drivers.

## Important APIs, types, and functions

- `VIDEO_DAVINCI_VPIF_DISPLAY` builds the VPIF display stack for DM6467/DA850/OMAPL138-class SoCs.
- `VIDEO_DAVINCI_VPIF_CAPTURE` builds the VPIF capture stack for the same family.
- Both options depend on V4L platform drivers, V4L2 video device support, DaVinci architecture or compile testing, and I2C.
- Display selects `VIDEOBUF2_DMA_CONTIG`, and auto-selects ADV7343/THS7303 subdrivers when media subdriver autoselection is enabled.
- Capture selects `VIDEOBUF2_DMA_CONTIG` and `V4L2_FWNODE`.

## Control flow

There is no runtime flow. Selecting either symbol controls which objects the Makefile compiles and which dependent media components are made available.

## State and persistence behavior

Kconfig state is stored in the kernel build configuration. It does not affect runtime persistence beyond deciding whether the drivers are built-in, modules, or omitted.

## Dependencies and integration points

This file integrates the DaVinci VPIF drivers with the kernel media Kconfig hierarchy and ensures vb2 DMA-contig and relevant I2C/media subdevice infrastructure are present.

## Risks and edge cases

If dependencies are too broad, compile-test builds may miss missing platform data assumptions. If dependencies are too narrow, valid DT or board-file systems may be unable to enable the driver. The help text notes each mode builds two modules: common `vpif.ko` plus capture or display-specific module.

## Test signals

Build `allyesconfig`, `allmodconfig`, and `COMPILE_TEST` configurations with both symbols as modules and built-ins. Verify selected subdrivers and generated modules match the help text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/Makefile

## Purpose

This Makefile connects DaVinci VPIF Kconfig symbols to the common VPIF core and capture/display driver objects.

## Important APIs, types, and functions

- `obj-$(CONFIG_VIDEO_DAVINCI_VPIF_DISPLAY) += vpif.o vpif_display.o`
- `obj-$(CONFIG_VIDEO_DAVINCI_VPIF_CAPTURE) += vpif.o vpif_capture.o`

## Control flow

There is no runtime flow. During kernel build, the selected config symbol determines whether `vpif.o` is linked with display and/or capture support.

## State and persistence behavior

It has no runtime state. Build outputs persist as kernel objects/modules.

## Dependencies and integration points

The file depends on the symbols from `Kconfig` and on source-level exports from `vpif.c` used by `vpif_capture.c` and `vpif_display.c`.

## Risks and edge cases

If both capture and display are enabled as modules, `vpif.o` is listed in both module links, so build-system behavior and symbol export expectations matter. The source relies on `vpif.c` being available before either functional driver can access global MMIO helpers.

## Test signals

Compile capture-only, display-only, and both-enabled configurations as modules and built-ins. Confirm module loading order exposes the common VPIF driver before capture/display stream operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif.c

## Purpose

This is the common DaVinci VPIF core. It maps the VPIF register block, exports shared register globals and helpers, defines supported SD/HD mode tables, programs common channel timing/control registers, exposes VBI display parameter programming, and creates capture/display platform devices for DT systems using the legacy child drivers.

## Important APIs, types, and functions

- `vpif_base` and `vpif_lock` are exported shared MMIO base and interrupt/control lock.
- `vpif_ch_params[]` and `vpif_ch_params_count` provide supported NTSC/PAL and several CEA HD timings for capture/display drivers.
- `vpif_set_video_params()` writes horizontal/vertical timing and channel control state; it returns one-channel vs two-channel YC mux usage.
- `vpif_set_vbi_display_params()` writes VANC start/size registers for display channels.
- `vpif_channel_getfid()` reads current hardware field ID.
- `vpif_probe()` maps registers, enables runtime PM, and for DT endpoint-based systems allocates/registers `vpif_capture` and `vpif_display` platform devices sharing the parent IRQ.

## Control flow

The driver is registered at `subsys_initcall`, earlier than the child platform drivers. Probe maps the top-level register resource and enables runtime PM. If the parent VPIF node has graph endpoints, it treats the system as DT-based and manually creates capture and display platform devices with inherited DMA masks, parent device, and shared IRQ resource. Remove unregisters those children and disables runtime PM.

Common register programming flows through `vpif_set_video_params()`: it writes timing for the requested channel and, if YC is not muxed, mirrors timing to the adjacent channel for two-channel HDTV-like operation. It then configures control bits, pitch, request size, and emulation control.

## State and persistence behavior

Runtime state is limited to global `vpif_base`, global `vpif_lock`, static mode tables, and per-parent `struct vpif_data` containing child platform-device pointers. Hardware register state is programmed at stream-on by child drivers and lost on reset.

## Dependencies and integration points

It depends on platform devices, OF graph parsing, runtime PM, IRQ trigger metadata, and the register/structure definitions in `vpif.h`. Capture and display modules depend on its exported symbols and functions.

## Risks and edge cases

The DT child-device creation path returns early with success when no endpoint exists, leaving only common VPIF initialized for legacy board-file child devices. The IRQ resource is static inside probe, so assumptions about a single parent instance matter. Mode table completeness must match all subdevice timing presets. Two-channel modes affect adjacent channels and can surprise independent users of channel 1 or 3.

## Test signals

Probe on DT and legacy platform-data systems, verify child platform devices appear when endpoints exist, stream SD and HD modes through capture/display, check adjacent channel enablement in non-mux mode, and validate runtime PM suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif.h

## Purpose

This header defines VPIF register offsets, bit masks, inline MMIO helpers, channel enable/interrupt helpers, capture/display buffer-address programming helpers, raw ancillary-data toggles, timing structures, and exported common function prototypes.

## Important APIs, types, and functions

- `regr()` and `regw()` access the exported `vpif_base`.
- Channel helpers enable/disable channels 0-3, configure frame interrupts, assert interrupt-on-both-fields, set video buffer addresses, set VBI/HBI addresses, toggle raw VANC/HANC, and enable display clipping.
- `vpif_intr_status()` reads and clears per-channel interrupt status.
- `struct vpif_channel_config_params` describes timing, muxing, field mode, SD/HD identity, VBI support, and DV timings.
- `struct vpif_vbi_params`, `struct vpif_video_params`, and `struct vpif_params` carry runtime channel parameters for common programming.

## Control flow

The inline helpers are called by capture/display start, stop, ISR, and address scheduling paths. Address helper selection depends on channel number and mux mode; interrupt helpers wrap shared register updates in `vpif_lock`.

## State and persistence behavior

The header declares the shared MMIO base and lock but owns no memory itself. It defines structures that capture/display drivers persist in channel objects while the device is loaded. Register writes directly update hardware state and are not persistent.

## Dependencies and integration points

It depends on Linux I/O helpers, V4L2 IDs, and `media/davinci/vpif_types.h` for platform data and interface types. It is the contract among `vpif.c`, `vpif_capture.c`, and `vpif_display.c`.

## Risks and edge cases

Most MMIO helpers are inline read-modify-write operations; only interrupt enable helpers lock, so callers must avoid concurrent unsafe updates. Two-channel Y/C non-mux helpers intentionally write chroma addresses into the adjacent channel. The interrupt disable helpers write to `VPIF_INTEN_SET` after clearing `VPIF_INTEN`, which is hardware-specific and should be regression-tested.

## Test signals

Compile coverage plus streaming tests that exercise all four channels, muxed and non-muxed modes, top/bottom field address programming, interrupt clearing, VBI/HBI toggles, and clipping controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif_capture.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif_capture.c

## Purpose

This file implements the DaVinci VPIF capture V4L2 driver for channels 0 and 1. It registers capture video nodes, binds decoder/sensor subdevices through legacy I2C board data or DT async notifier, handles V4L2 input/standard/DV timing/format ioctls, manages vb2 DMA-contig buffers, and services VPIF frame interrupts.

## Important APIs, types, and functions

- `vpif_ioctl_ops` exposes capture querycap, format, input, streaming, standard, DV timing, and log-status ioctls.
- `vpif_buffer_queue_setup()`, `vpif_buffer_prepare()`, `vpif_buffer_queue()`, `vpif_start_streaming()`, and `vpif_stop_streaming()` are vb2 capture operations.
- `vpif_channel_isr()` handles frame interrupts and advances buffers for progressive and interlaced modes.
- `vpif_update_std_info()`, `vpif_calculate_offsets()`, and `vpif_config_addr()` derive VPIF timing, field layout, pitch, and register address callbacks from selected standard/format.
- `vpif_set_input()` routes selected inputs through board/DT path callbacks and subdevice `s_routing`.
- `vpif_capture_get_pdata()` builds capture platform data from OF graph endpoints when board data is absent.

## Control flow

Probe allocates two channel objects, registers a V4L2 device, requests optional IRQ resources per channel, obtains platform data or builds it from DT endpoints, allocates the subdevice pointer table, and either registers I2C subdevices immediately or registers a V4L2 async notifier. Completion initializes each channel, selects input 0, sets NTSC default format, initializes vb2, and registers `/dev/video0` and `/dev/video1` style capture nodes.

On stream-on, the driver configures board-specific input channel mode, starts the current subdevice stream, calls common `vpif_set_video_params()`, chooses the address programming helper, pulls the first queued buffer, writes its top/bottom Y/C addresses, enables field interrupts, and enables channel 0 plus channel 1 if needed for two-channel mode. The ISR ignores the first interrupt, then for progressive frames completes the current buffer and schedules the next; for interlaced frames it synchronizes software field ID with hardware FID and alternates completion/scheduling on even/odd fields.

## State and persistence behavior

The static `vpif_obj` owns the V4L2 device, two channel objects, subdevice table, async notifier, and platform config. Each channel stores selected input, current subdevice, standard/timing, VPIF parameters, and one `common_obj` with vb2 queue, DMA queue, active/next buffers, field offsets, and a selected `set_addr` function. There is no disk persistence; defaults are recreated on probe.

## Dependencies and integration points

It depends on common VPIF exports from `vpif.c`/`vpif.h`, videobuf2 DMA-contig, V4L2 ioctl/fwnode/async/subdev APIs, OF graph parsing, I2C subdevice registration, and DaVinci VPIF platform data callbacks such as `setup_input_channel_mode` and `setup_input_path`.

## Risks and edge cases

The driver uses global `ycmux_mode` and `channel_first_int`, so simultaneous channel streams can interact in two-channel modes. Buffer addresses and field offsets must be 8-byte aligned. Raw Bayer paths bypass the standard table and set CCD/raw capture mode, while NV16 paths use VPIF timing tables. `vpif_stop_streaming()` assumes `cur_frm` is valid after stream-on. DT data construction indexes channel inputs with `i`, making endpoint ordering important.

## Test signals

Validate input enumeration/selection, standard and DV timing ioctls, raw Bayer sensor capture, BT.656 decoder capture, progressive and interlaced streaming, DMABUF/MMAP/USERPTR queues, insufficient/unaligned buffer rejection, IRQ sharing, suspend/resume during streaming, and async notifier binding with DT endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif_capture.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif_capture.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif_capture.h

## Purpose

This header defines the DaVinci VPIF capture driver's local data structures and constants for capture channels, video state, vb2 buffers, common DMA queue state, channel objects, and the device aggregate.

## Important APIs, types, and functions

- `VPIF_CAPTURE_VERSION`, channel/object count constants, and `VPIF_VALID_FIELD()` define capture capabilities.
- `enum vpif_channel_id` names capture channel 0 and channel 1.
- `struct video_obj` stores selected field, standard, and DV timings.
- `struct vpif_cap_buffer` wraps `vb2_v4l2_buffer` with a DMA queue list node.
- `struct common_obj` stores active/next buffers, format, vb2 queue, DMA queue, lock, address callback, offsets, width, and height.
- `struct channel_obj` and `struct vpif_device` aggregate video node, input/subdev selection, VPIF parameters, channels, V4L2 device, subdevices, async notifier, and platform config.

## Control flow

The header has no direct control flow. `vpif_capture.c` allocates and fills these structures during probe, updates them through ioctl calls, and uses them in vb2 and ISR paths.

## State and persistence behavior

All declared state is runtime memory. Buffer pointers and queue links are transient during streaming; selected input and format reset to defaults after driver reload.

## Dependencies and integration points

It includes vb2 DMA-contig, V4L2 device, and common `vpif.h`. It also depends on platform-data types referenced through `struct vpif_capture_config`.

## Risks and edge cases

The common object holds both synchronization primitives and hardware address callback state; incorrect initialization can break streaming. The valid-field macro admits `ANY`, `NONE`, `INTERLACED`, `SEQ_TB`, and `SEQ_BT`, so offset calculations must match every accepted case.

## Test signals

Compile coverage and runtime capture tests that allocate buffers, switch fields, change inputs, and run both capture channels are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif_capture.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif_display.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif_display.c

## Purpose

This file implements the DaVinci VPIF display/output V4L2 driver for channels 2 and 3. It registers output video nodes, attaches encoder subdevices from platform data, handles output/standard/DV timing/format ioctls, queues user buffers through vb2 DMA-contig, programs VPIF display timing/address registers, and advances frames in the VPIF ISR.

## Important APIs, types, and functions

- `vpif_ioctl_ops` exposes output querycap, video-output format, streaming, standard, output selection, DV timing, and log-status ioctls.
- `vpif_buffer_queue_setup()`, `vpif_buffer_prepare()`, `vpif_buffer_queue()`, `vpif_start_streaming()`, and `vpif_stop_streaming()` are vb2 output operations.
- `vpif_channel_isr()`, `process_progressive_mode()`, and `process_interlaced_mode()` complete displayed buffers and schedule the next buffer.
- `vpif_update_std_info()`, `vpif_update_resolution()`, `vpif_calculate_offsets()`, and `vpif_config_addr()` derive display geometry and hardware address callbacks.
- `vpif_set_output()` maps user output indices to subdevices and routes encoder inputs/outputs.

## Control flow

Probe requires platform data, allocates two display channel objects, registers the V4L2 device, requests optional IRQs, registers I2C encoder subdevices, assigns group IDs, and completes probe by initializing each channel, selecting output 0, setting NTSC default resolution, initializing vb2, and registering video-output nodes numbered around channels 2 and 3.

Stream-on locks the queue, optionally programs the board clock for SD/HD and mux mode, calls common `vpif_set_video_params()` for hardware channel `channel_id + 2`, chooses the address callback, takes the first queued buffer, writes Y/C top/bottom addresses, enables interrupts/channels, and enables clipping where configured. The ISR ignores the first field interrupt, then in progressive mode completes the previous displayed buffer and programs the next; in interlaced mode it syncs hardware FID against software state and alternates completion/scheduling by field.

## State and persistence behavior

The static `vpif_obj` stores the V4L2 device, channel objects, subdevice array, and display platform config. Each channel stores selected output, current encoder subdevice, current standard/timings, VPIF parameters, and one common vb2/DMA state object. There is no persistence beyond the loaded driver instance.

## Dependencies and integration points

It depends on common VPIF exports, V4L2/vb2 DMA-contig, platform data with display channel configs, board clock callback `set_clock`, optional clipping flags, and I2C encoder subdevices such as those selected by Kconfig.

## Risks and edge cases

Unlike capture, display has no DT async path in this file and gives up without platform data. Only YUV422P is exposed. Global `ycmux_mode` affects channel 3 when channel 2 uses two-channel output. Buffer alignment must be 8-byte clean. Stop streaming returns active and queued buffers as errors and assumes stream-on initialized `cur_frm`/`next_frm`.

## Test signals

Validate output enumeration/selection, standard switching, DV timing setup, clipping-enabled channels, progressive/interlaced output, channel 2 two-channel mux behavior, MMAP/USERPTR/DMABUF queues, IRQ handling, and suspend/resume while streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif_display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif_display.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif_display.h

## Purpose

This header defines local types and constants for the DaVinci VPIF display/output driver, including output channels, vb2 display buffers, shared per-channel queue state, selected output/subdevice state, and the device aggregate.

## Important APIs, types, and functions

- `VPIF_DISPLAY_VERSION`, device/object constants, VBI-related constants, and `VPIF_VALID_FIELD()` describe display capabilities.
- `enum vpif_channel_id` names display channel 2 and channel 3 from the display driver's local zero-based perspective.
- `struct video_obj` stores selected field, latest-only flag, standard, and DV timings.
- `struct vpif_disp_buffer`, `struct common_obj`, `struct channel_obj`, and `struct vpif_device` mirror the capture driver with output-specific naming and platform config.

## Control flow

No direct flow is implemented in the header. `vpif_display.c` allocates the structures at probe, initializes vb2 queues and video devices, and consumes them from ioctl, streaming, and ISR paths.

## State and persistence behavior

All fields are runtime-only. The `common_obj` queue and active/next frame pointers exist only while the driver is loaded and especially while streaming.

## Dependencies and integration points

It includes vb2 DMA-contig, V4L2 device, and common `vpif.h`, and references `struct vpif_display_config` from DaVinci media platform data.

## Risks and edge cases

`VPIF_NUMOBJECTS` is set to 1 because HBI/VBI support is not added, despite constants for VBI/HBI indices. Code that assumes three objects would be wrong. The valid field set must stay consistent with offset calculation in the implementation.

## Test signals

Compile coverage plus display runtime tests for both channels, field modes, queue initialization, output selection, and stream-on/off buffer cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif_display.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/j721e-csi2rx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/j721e-csi2rx/Makefile

## Purpose

This Makefile builds the TI J721E CSI2RX shim wrapper driver when its Kconfig symbol is enabled.

## Important APIs, types, and functions

- `obj-$(CONFIG_VIDEO_TI_J721E_CSI2RX) += j721e-csi2rx.o`

## Control flow

There is no runtime flow. Build selection compiles `j721e-csi2rx.c` into the kernel or module.

## State and persistence behavior

No runtime state exists in this file; build artifacts persist as normal kernel objects/modules.

## Dependencies and integration points

It depends on the surrounding media platform Kconfig defining `CONFIG_VIDEO_TI_J721E_CSI2RX` and on the source file's dependencies, including Cadence CSI2RX bridge support and DMA engine APIs.

## Risks and edge cases

The Makefile is minimal; any symbol rename or Kconfig relocation would silently omit the driver from builds if not updated.

## Test signals

Enable `CONFIG_VIDEO_TI_J721E_CSI2RX` as built-in and module and confirm `j721e-csi2rx.o` is compiled and linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/j721e-csi2rx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/j721e-csi2rx/j721e-csi2rx.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/j721e-csi2rx/j721e-csi2rx.c

## Purpose

This is the TI J721E CSI2RX shim wrapper V4L2 capture driver. It bridges a Cadence CSI2RX subdevice to a video capture node, configures the TI shim registers, negotiates pixels-per-clock, receives frames through a DMA engine channel, and exposes a media-controller V4L2 capture interface.

## Important APIs, types, and functions

- `ti_csi2rx_formats[]` maps V4L2 fourcc formats to media-bus codes, MIPI CSI-2 data types, bits per pixel, and shim unpacking sizes.
- `ti_csi2rx_*_fmt*()` ioctl helpers enumerate, clamp, get, try, and set capture formats and frame sizes.
- `ti_csi2rx_notifier_register()`, `csi_async_notifier_bound()`, and `csi_async_notifier_complete()` bind the `csi-bridge` child subdevice, register the video node, create the immutable media link, and register subdev nodes.
- `ti_csi2rx_setup_shim()` programs pixel reset, CSI datatype, YUV422 byte order, multi-pixel mode, and PSI-L tags.
- `ti_csi2rx_start_dma()`, `ti_csi2rx_dma_callback()`, `ti_csi2rx_stop_dma()`, and `ti_csi2rx_drain_dma()` manage DMA transactions and stale endpoint draining.
- `ti_csi2rx_start_streaming()` and `ti_csi2rx_stop_streaming()` coordinate the media pipeline, shim, DMA, and upstream subdevice stream state.

## Control flow

Probe allocates `struct ti_csi2rx_dev`, maps the shim registers, initializes a DMA channel named `rx0` and a coherent drain buffer, initializes media/V4L2/video state with a default UYVY 640x480 capture format, initializes vb2, registers an async notifier for the `csi-bridge` fwnode, and populates child platform devices. Notifier completion registers the video device and creates an immutable enabled link from bridge source pad 1 to the video sink pad.

Userspace configures formats through the video node. Width is rounded down to the number of pixels per 16-byte PSI-L word and clamped to arbitrary 16K limits; interlaced formats are forced to `V4L2_FIELD_NONE`. Link validation compares source pad width, height, field, media-bus code, and fourcc before streaming.

Stream-on requires queued buffers, starts the media pipeline, configures shim registers, resets sequence, starts DMA for the first queued buffer, marks DMA active, and calls upstream `s_stream(1)`. DMA callbacks timestamp and complete buffers, then submit all queued buffers. If DMA goes idle due to no buffers, `buffer_queue()` drains stale data and restarts DMA when a new buffer arrives. Stop disables pipeline and shim, stops upstream streaming, drains/terminates DMA, and returns all queued/submitted buffers as errors.

## State and persistence behavior

`struct ti_csi2rx_dev` stores the device, shim base, V4L2/media/video objects, async notifier, source subdevice, vb2 queue, mutex, current format, DMA state, sequence counter, and negotiated pixels-per-clock. DMA state tracks queued buffers, submitted buffers, state enum, DMA channel, and a persistent coherent drain buffer for the lifetime of the driver. No disk persistence exists.

## Dependencies and integration points

It depends on platform OF matching (`ti,j721e-csi2rx-shim`), DMA engine, Cadence CSI2RX media helper `cdns_csi2rx_negotiate_ppc()`, MIPI CSI-2 datatypes, V4L2/media-controller APIs, videobuf2 DMA-contig, fwnode async registration, and child platform population for the bridge device.

## Risks and edge cases

DMA draining is used to avoid stale PSI-L data after frame drops or stopping one stream in multi-stream cases; drain timeout is tolerated but other drain errors warn that the next frame may be bad. The DMA callback submits every queued buffer while holding the DMA lock, so start-DMA failures must mark individual buffers with error. The shim size calculation changes for multiple pixels per clock and packed YUV; wrong negotiation or format metadata would corrupt packing. Remove unregisters the video device unconditionally, so notifier-completion failures must keep lifecycle ordering correct.

## Test signals

Validate media graph creation with a Cadence bridge child, format enumeration with and without `mbus_code`, link validation failures, MMAP/DMABUF streaming, no-buffer underrun followed by restart, drain timeout behavior, multiple pixel-per-clock negotiation, all supported Bayer/YUV/RGB formats, and repeated probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/j721e-csi2rx/j721e-csi2rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/Kconfig

## Purpose

This Kconfig file defines build options for the OMAP2/OMAP3 V4L2 display driver and optional VRFB support.

## Important APIs, types, and functions

- `VIDEO_OMAP2_VOUT` enables the OMAP2/3 V4L2 display driver.
- `VIDEO_OMAP2_VOUT_VRFB` is a helper bool defaulting to enabled when `VIDEO_OMAP2_VOUT` and OMAP2 VRFB support or compile testing are available.
- The main driver depends on V4L platform drivers, MMU, framebuffer support or compile-test fallback, OMAP2/OMAP3 architecture or compile test, and `VIDEO_DEV`.
- It selects `VIDEOBUF2_DMA_CONTIG` and selects `OMAP2_VRFB` on real OMAP2/3 builds.

## Control flow

There is no runtime flow. These symbols control whether OMAP vout objects and optional VRFB object are compiled.

## State and persistence behavior

State is limited to the kernel build configuration. Runtime driver state is in the compiled source files, not this Kconfig.

## Dependencies and integration points

It integrates the OMAP display driver with the media platform menu, fbdev OMAP2 support, VRFB, vb2 DMA-contig, and compile-test infrastructure.

## Risks and edge cases

The framebuffer dependency has a special compile-test exception when `FB_OMAP2=n`, so compile coverage can include systems without the real framebuffer stack. VRFB selection differs between real hardware and compile-test paths.

## Test signals

Build with OMAP2/3 hardware configs, with `COMPILE_TEST`, with VRFB enabled/disabled where possible, and as both module and built-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/Makefile

## Purpose

This Makefile builds the OMAP2/3 V4L2 output driver objects and conditionally includes VRFB support.

## Important APIs, types, and functions

- `omap-vout-y += omap_vout.o omap_voutlib.o`
- `omap-vout-$(CONFIG_VIDEO_OMAP2_VOUT_VRFB) += omap_vout_vrfb.o`
- `obj-$(CONFIG_VIDEO_OMAP2_VOUT) += omap-vout.o`

## Control flow

There is no runtime control flow. The build system combines the base OMAP vout objects and optional VRFB object into `omap-vout.o` when the main Kconfig symbol is enabled.

## State and persistence behavior

No runtime state exists here. The selected object list affects build artifacts only.

## Dependencies and integration points

It depends on `VIDEO_OMAP2_VOUT` and `VIDEO_OMAP2_VOUT_VRFB` from the adjacent Kconfig and on the implementation files in the same directory.

## Risks and edge cases

If VRFB-related source references are not properly guarded, builds with `VIDEO_OMAP2_VOUT_VRFB=n` can fail at link or compile time. Object naming must stay synchronized with module aliases and source file names.

## Test signals

Compile with and without `CONFIG_VIDEO_OMAP2_VOUT_VRFB`, as module and built-in, and verify `omap_vout_vrfb.o` only appears in VRFB-enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/Makefile -->

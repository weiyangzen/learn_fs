# subset-b-004175 research

Grouped research for TI OMAP3 ISP resizer/statistics/video support and TI VPE scaler/color-space-converter helpers. Each section preserves the original source path for source-tree-aligned reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispresizer.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispresizer.c

## Purpose
Implements the OMAP3 ISP resizer V4L2 subdevice and its memory input/output video-node glue. The module scales interleaved YUV422 frames from either memory or the live video port, applies crop constraints, programs hardware filter coefficients, manages SBL bandwidth throttling, and integrates with media-controller links.

## Important APIs, Types, and Functions
Core public entry points are `omap3isp_resizer_init()`, `omap3isp_resizer_cleanup()`, entity register/unregister helpers, `omap3isp_resizer_isr()`, `omap3isp_resizer_isr_frame_sync()`, `omap3isp_resizer_busy()`, and `omap3isp_resizer_max_rate()`. Important internals include `resizer_calc_ratios()`, `resizer_try_crop()`, `resizer_set_format()`, `resizer_set_selection()`, `resizer_configure()`, `resizer_set_stream()`, and `resizer_video_queue()`.

## Control Flow
Initialization creates a two-pad scaler subdevice plus input and output video nodes. Media link setup selects memory input or video-port input, refusing conflicting links. Format and selection operations clamp sink/source sizes and compute TRM-valid ratios/crops. Stream start enables the resizer clock, programs source, input/output offsets, output size, crop, filters, phase, and luma settings, then starts one-shot processing when buffers are present. IRQ flow applies pending crop updates under `res->lock`, completes queued buffers through `omap3isp_video_buffer_next()`, loads the next DMA addresses, and restarts continuous or single-shot processing as appropriate.

## State and Persistence
Persistent runtime state lives in `struct isp_res_device`: active/requested crop, ratios, input selection, memory base address, crop offset, stream state, wait/stopping synchronization, and a spinlock-protected `applycrop` flag. Hardware state is volatile register programming under the resizer and SBL register blocks; nothing survives module unload or reboot.

## Dependencies and Integration Points
The code depends on `isp.h`, `ispreg.h`, media-controller pads/links, V4L2 subdev pad operations, OMAP3 ISP SBL/subclock helpers, revision-specific hardware limits, and generic `ispvideo` buffer handling. It feeds pipeline maximum-rate decisions through `omap3isp_resizer_max_rate()` during link validation.

## Risks and Edge Cases
The ratio equations are hardware-sensitive and depend on 4-tap versus 7-tap mode, default phase, output width alignment, vertical ratio, and OMAP ISP revision. Memory input crop programming splits byte offset between SDR address alignment and low horizontal start bits. Continuous mode underruns are deferred to frame-sync restart because immediate mid-frame enable causes shifted images. SBL throttling relies on valid `pipe->max_rate` and `max_timeperframe`; divide-by-zero or stale pipeline timing would be dangerous.

## Test Signals
Exercise media link combinations, memory-to-memory single-shot scaling, live sensor-to-memory scaling, crop changes while streaming, YUYV/UYVY ordering, ES1/ES2/3630 output-width limits, underrun recovery, SBL overflow absence under high scaling ratios, and v4l2-compliance for subdev format/selection enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispresizer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispresizer.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispresizer.h

## Purpose
Declares the OMAP3 ISP resizer data model, pad numbering, coefficient container, scaling ratio/luma helper structures, input-source enum, and exported lifecycle/IRQ/query APIs used by the broader ISP driver.

## Important APIs, Types, and Functions
`struct isp_res_device` is the central state object containing the V4L2 subdevice, two media pads, active pad formats, input/output `isp_video` nodes, memory address/crop offset, current ratio, stream state, crop state, waitqueue, stopping atomic, and spinlock. `struct isprsz_coef`, `struct resizer_ratio`, and `struct resizer_luma_yenh` describe hardware programming inputs. Public prototypes cover init/cleanup, entity registration, ISR hooks, suspend/resume, busy check, and max-rate calculation.

## Control Flow
This header does not execute control flow, but its layout defines the contract consumed by `ispresizer.c` and the ISP core. The resizer transitions between `RESIZER_INPUT_NONE`, `RESIZER_INPUT_VP`, and `RESIZER_INPUT_MEMORY`, and exposes sink/source pads `RESZ_PAD_SINK` and `RESZ_PAD_SOURCE` to media graph code.

## State and Persistence
All state is in-memory kernel driver state. The `crop.request` value stores the user-facing crop, while `crop.active` stores the hardware-mangled crop that satisfies resizer equations. `addr_base` and `crop_offset` are volatile DMA programming aids for memory input.

## Dependencies and Integration Points
Depends on Linux spinlocks/types and forward declarations from the ISP stack. It embeds `struct isp_video` and V4L2/media structures through included ISP headers, so ABI drift in video or media entity state affects this structure.

## Risks and Edge Cases
Bitfield `applycrop` and `state` are touched in streaming/IRQ paths and require the spinlock discipline implemented in the C file. Pad constants must stay aligned with entity initialization and subdev callbacks. Adding fields to `struct isp_res_device` requires checking initialization and cleanup paths.

## Test Signals
Compile coverage across OMAP3 ISP configs should catch declaration drift. Runtime evidence comes from correct registration of two video nodes and one scaler subdevice, valid pad link setup, suspend/resume behavior, and no races when changing crop while streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispresizer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispstat.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispstat.c

## Purpose
Provides the generic statistics-engine core used by OMAP3 ISP H3A AF, H3A AEWB, and histogram blocks. It handles configuration, DMA/coherent buffer allocation, magic-word integrity checks, V4L2 statistics events, userspace copyout, enable/disable state transitions, SBL overflow recovery, and common ISR sequencing.

## Important APIs, Types, and Functions
Public APIs include `omap3isp_stat_config()`, `omap3isp_stat_request_statistics()`, `omap3isp_stat_request_statistics_time32()`, `omap3isp_stat_enable()`, `omap3isp_stat_s_stream()`, ISR hooks, suspend/resume, entity register/unregister, init, and cleanup. Key helpers include `isp_stat_bufs_alloc()`, `isp_stat_buf_get()`, `isp_stat_buf_queue()`, `isp_stat_buf_process()`, `isp_stat_try_enable()`, and `__stat_isr()`.

## Control Flow
Userspace config calls module-specific `validate_params()` and `set_params()`, sizes/reallocates the coherent buffer pool, and returns the future config counter. Enable requests move from disabled to enabling; frame-sync calls `isp_stat_try_enable()` to pick an active buffer, set up registers, insert magic, and enable PCR. ISR handling disables the module, optionally invokes module-specific buffer processing, queues completed buffers, applies normal or recovery configuration, reinserts magic, re-enables PCR, and queues V4L2 events. Userspace statistics requests lock one completed buffer, verify magic, copy to user memory, fill timestamp/frame/config metadata, then release it.

## State and Persistence
`struct ispstat` owns a fixed pool of `STAT_MAX_BUFS` buffers, `active_buf`, `locked_buf`, `configured/update/buf_processing/sbl_ovl_recover` flags, frame/config counters, event type, DMA channel, module-private config, and state enum. All state is volatile, but it persists across stream toggles while the subdevice exists.

## Dependencies and Integration Points
The generic layer depends on module-specific `ispstat_ops`, ISP global `stat_lock`, DMA mapping APIs, V4L2 events/subdevs, media entities, timekeeping, and userspace copy APIs. H3A-specific behavior is selected by comparing `stat` against `isp_af` and `isp_aewb`.

## Risks and Edge Cases
The file documents hardware workarounds: AF writes one extra paxel, H3A may resume at the wrong address after SBL overflow, and recovery configs reduce repeated overflows. Magic checks intentionally require the beginning marker to be overwritten and the ending marker to remain intact. Buffer allocation is forbidden while enabled or processing, and `BUG_ON(locked_buf)` enforces no userspace copyout during reallocation. DMA-engine and ISP-IOMMU allocation paths use different devices.

## Test Signals
Test valid/invalid configs, buffer-size correction, time32 compatibility, event delivery with and without errors, EBUSY/EINVAL paths, SBL overflow recovery, streamoff during pending histogram DMA, magic corruption detection, and concurrent userspace statistic requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispstat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispstat.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispstat.h

## Purpose
Defines the generic OMAP3 ISP statistics ABI between common `ispstat.c` and concrete AF/AEWB/histogram engines.

## Important APIs, Types, and Functions
Defines buffer states (`STAT_BUF_DONE`, `STAT_NO_BUF`, `STAT_BUF_WAITING_DMA`), pool/event sizes, `struct ispstat_buffer`, `struct ispstat_ops`, `enum ispstat_state_t`, `struct ispstat`, and `struct ispstat_generic_config`. The ops table requires validate, set, register setup, enable, busy, and optional buffer-processing callbacks.

## Control Flow
Concrete engines embed or own a `struct ispstat`, fill `priv`, `recover_priv`, `event_type`, and `ops`, then call the public helpers for config, enable, stream, ISR, and statistics requests. The common layer drives the engine through the callback table and uses the state enum to sequence disabled, enabling, enabled, disabling, and suspended transitions.

## State and Persistence
The header specifies long-lived per-engine state: coherent buffer pool pointers, DMA channel, active/locked buffers, counters, wait accumulation, update flags, and ioctl mutex. It is kernel-memory state only and is reset by cleanup or driver removal.

## Dependencies and Integration Points
Includes Linux OMAP3 ISP UAPI definitions for userspace statistic data, V4L2 event support, ISP core headers, and generic `ispvideo` pipeline structures. Module-specific files must keep their config structures compatible with `ispstat_generic_config` field ordering.

## Risks and Edge Cases
The comment on `ispstat_generic_config` is a structural contract: `buf_size` and `config_counter` must match the beginning of multiple UAPI config structs. Misordered fields would corrupt validation/config-counter behavior. Callback implementations must be callable under the locking/IRQ expectations imposed by `ispstat.c`.

## Test Signals
Compile concrete stats engines, verify each initializes with correct ops/event type, check UAPI config structures still match generic layout, and exercise suspend/resume plus stream enable/disable transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispstat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispvideo.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispvideo.c

## Purpose
Implements generic V4L2 video-node and videobuf2 support for OMAP3 ISP pipeline endpoints. It converts media-bus formats to memory formats, manages vb2 queues, starts/stops media pipelines, coordinates memory-to-memory and sensor-to-memory streaming, and exposes the V4L2 file/ioctl operations used by ISP modules.

## Important APIs, Types, and Functions
Key exports are `omap3isp_video_init()`, cleanup/register/unregister helpers, `omap3isp_video_format_info()`, `omap3isp_video_buffer_next()`, `omap3isp_video_cancel_stream()`, and `omap3isp_video_resume()`. Major internals include the `formats[]` table, format conversion helpers, `isp_video_get_graph_data()`, vb2 ops, `isp_video_check_external_subdevs()`, `isp_video_streamon()`, `isp_video_streamoff()`, and open/release/poll/mmap handlers.

## Control Flow
Open allocates a per-file handle, powers the ISP pipeline, initializes a vb2 DMA-contig queue, and seeds a default UYVY format. Format ioctls translate between pixel and media-bus formats, querying remote subdevices for capture nodes. Streamon starts the media pipeline, validates format consistency, discovers the far-end video node, checks external sensor pixel-rate constraints, initializes pipe state and frame counters, then calls vb2 streamon. Buffer queueing inserts buffers into an IRQ list; when the first buffer for an input/output side arrives it calls the module `queue()` op and may start single-shot streaming once both sides are ready. IRQ completion returns buffers, stamps sequence/time/field, handles underruns, and updates pipeline state.

## State and Persistence
Persistent runtime state is split between `struct isp_video` and per-open `struct isp_video_fh`. `struct isp_pipeline` tracks media pipeline state, endpoints, frame number, max rates, external sensor info, field, and error flag. Queues and format settings live only while the file handle is open and are destroyed on release.

## Dependencies and Integration Points
Depends on V4L2 device/ioctl/media-controller APIs, videobuf2 DMA-contig memory ops, OMAP3 ISP power/clock helpers, external subdevice controls (`V4L2_CID_PIXEL_RATE`), CCDC rate checks, and module-specific `isp_video_operations.queue()` callbacks.

## Risks and Edge Cases
The format table must keep duplicate pixel formats adjacent for enumeration. Output nodes can set time-per-frame; capture nodes disable parm ioctls. Memory-to-memory pipelines require both input and output buffers before single-shot start. Sensor pipelines can start with output underrun and recover later. Error cleanup deliberately clears DMA queues after failed pipeline start to avoid stale CCDC IRQ buffer access.

## Test Signals
Use v4l2-compliance, media-ctl topology tests, mmap/userptr buffer streaming, format enumeration by mbus code, streamon failure unwinds, external subdevice pixel-rate rejection, memory-to-memory resizer/preview paths, underrun recovery, suspend/resume buffer discard, and sequence propagation with/without CSI frame numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispvideo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispvideo.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispvideo.h

## Purpose
Defines the shared OMAP3 ISP video-node, buffer, pipeline, and media-format structures used by ISP capture/output endpoints.

## Important APIs, Types, and Functions
Important types are `struct isp_format_info`, `enum isp_pipeline_stream_state`, `enum isp_pipeline_state`, `struct isp_pipeline`, `struct isp_buffer`, `struct isp_video_operations`, `struct isp_video`, and `struct isp_video_fh`. Inline helpers map media entities/files/queues back to ISP containers. Public APIs initialize/register video nodes, fetch the next IRQ buffer, cancel/resume streams, find remote pads, and look up format metadata.

## Control Flow
This header provides state-machine flags consumed by `ispvideo.c` and module drivers. `isp_pipeline_ready()` encodes the condition for memory-to-memory single-shot start: both stream bits, both queue bits, and both idle bits must be set.

## State and Persistence
`struct isp_video` stores the video device, pad, queue locks, DMA queue, active flag, pipeline object, bytes-per-line constraints, current queue pointer, and error state. `struct isp_pipeline` persists for the active media pipeline and tracks endpoints, clock/rate constraints, external subdevice state, frame numbering, and error propagation.

## Dependencies and Integration Points
Includes V4L2 media-bus, media-entity, V4L2 device/file-handle, and vb2-v4l2 headers. ISP modules embed `struct isp_video` for their memory-facing endpoints and implement `isp_video_operations.queue()`.

## Risks and Edge Cases
Pipeline state is bitmask-based and protected by spinlocks in the C file; adding flags requires updating readiness and queue transitions. DMA queue flags distinguish underrun from newly queued buffers and are interpreted by module IRQ paths. Bytes-per-line alignment fields must match hardware alignment requirements for each module.

## Test Signals
Compile all ISP modules that embed `struct isp_video`, verify pipeline-ready transitions during M2M streaming, confirm alignment constraints per endpoint, and run capture/output buffer lifecycle tests through open, streamon, queue, IRQ complete, streamoff, and release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispvideo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/luma_enhance_table.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/luma_enhance_table.h

## Purpose
Provides a static numeric include-table for OMAP3 ISP preview luminance enhancement programming. It is data-only and intended to be included where register/table initialization needs these constants.

## Important APIs, Types, and Functions
There are no C APIs or types. The file contains a comma-separated sequence of 128 integer constants after the license/header comment.

## Control Flow
No control flow exists in this file. Build-time inclusion injects the constants into the including translation unit, likely as an initializer list.

## State and Persistence
The table is read-only compiled data. It has no runtime ownership, synchronization, allocation, or persistence beyond the kernel image/module containing the includer.

## Dependencies and Integration Points
It depends on the including C file to provide the array declaration, element type, size expectation, and semantic interpretation. The values appear tuned for the ISP preview luminance enhancement hardware.

## Risks and Edge Cases
Because the file lacks include guards and declaration context, accidental direct inclusion in multiple incompatible contexts can fail or silently change table shape. Editing value count or ordering risks misprogramming hardware coefficients.

## Test Signals
Compile the preview module, verify the expected array length, inspect hardware register/table programming against known-good image output, and regression-test preview luminance enhancement enable/disable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/luma_enhance_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/noise_filter_table.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/noise_filter_table.h

## Purpose
Provides a static numeric include-table for OMAP3 ISP preview noise-filter configuration.

## Important APIs, Types, and Functions
There are no functions or declarations. The file supplies 64 comma-separated integer constants: a block of `16` values followed by a block of `31` values.

## Control Flow
No runtime control flow exists. The table is consumed at compile time as an initializer fragment in the including source file.

## State and Persistence
The values become read-only data in the compiled driver. There is no mutable state, locking, allocation, or persistence outside the module image.

## Dependencies and Integration Points
The file relies on the preview/noise-filter code to define the target array and program the ISP hardware. Its semantics are entirely tied to hardware coefficient/table layout.

## Risks and Edge Cases
No include guard means it should remain an initializer fragment, not a standalone header. Value count/order changes can cause array-size mismatches or subtle image-processing regressions.

## Test Signals
Compile the preview driver, confirm expected table length, compare programmed noise-filter values with hardware documentation or known-good capture output, and test low-light/noise-filter scenarios for visual regression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/noise_filter_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/omap3isp.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/omap3isp.h

## Purpose
Defines board/firmware-facing bus configuration structures for the OMAP3 ISP input interfaces: parallel, CCP2/CSI1, and CSI2.

## Important APIs, Types, and Functions
Important declarations are `enum isp_interface_type`, `struct isp_parallel_cfg`, lane/mode constants, `struct isp_csiphy_lane`, `struct isp_csiphy_lanes_cfg`, `struct isp_ccp2_cfg`, `struct isp_csi2_cfg`, and `struct isp_bus_cfg`. There are no functions.

## Control Flow
No control flow is present. The ISP driver consumes `struct isp_bus_cfg` to determine interface type and interpret the matching union member.

## State and Persistence
Instances of these structures describe static platform/firmware configuration such as lane positions, polarities, data-lane shift, clock/sync polarities, BT.656 mode, CRC enable, and VP clock configuration. The header itself has no state.

## Dependencies and Integration Points
This header is included by ISP platform or sensor-connection code. It bridges board descriptions to the ISP receiver modules, especially parallel, CCP2, and CSI2 PHY setup.

## Risks and Edge Cases
Bitfield widths encode hardware-limited values; callers must validate lane positions, lane counts, and interface enum/union consistency. The comment notes the named union is retained for older GCC initializer compatibility.

## Test Signals
Build platform data/users, verify device-tree or board conversion populates the right interface type, test parallel polarity and lane-shift variants, and validate CSI/CCP2 lane mapping with sensors on each supported PHY.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/omap3isp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/Makefile

## Purpose
Maps TI VPE/VPDMA/scaler/CSC/VIP media Kconfig symbols to kbuild objects and enables debug compiler flags.

## Important APIs, Types, and Functions
The important interfaces are `obj-$(CONFIG_VIDEO_TI_VPE)`, `obj-$(CONFIG_VIDEO_TI_VPDMA)`, `obj-$(CONFIG_VIDEO_TI_SC)`, `obj-$(CONFIG_VIDEO_TI_CSC)`, and `obj-$(CONFIG_VIDEO_TI_VIP)`, plus composite object assignments `ti-vpe-y`, `ti-vpdma-y`, `ti-sc-y`, `ti-csc-y`, and `ti-vip-y`.

## Control Flow
Kbuild evaluates selected `CONFIG_VIDEO_TI_*` symbols and builds the corresponding module or built-in object. `ccflags-$(CONFIG_VIDEO_TI_VPE_DEBUG) += -DDEBUG` enables debug logging compilation when requested.

## State and Persistence
No runtime state exists. Persistent effect is build composition and module naming.

## Dependencies and Integration Points
The Makefile is coupled to Kconfig symbols in the media platform tree and to source filenames `vpe.c`, `vpdma.c`, `sc.c`, `csc.c`, and `vip.c`.

## Risks and Edge Cases
Renaming objects without updating this file breaks builds. Selecting helper modules separately from full VPE/VIP users can expose missing exported-symbol dependencies.

## Test Signals
Run `make M=drivers/media/platform/ti/vpe` under module and built-in configs, with and without `VIDEO_TI_VPE_DEBUG`, and confirm expected `ti-*.ko` artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/csc.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/csc.c

## Purpose
Implements the TI VPE/VIP color-space converter helper library. It selects coefficient matrices for YUV-to-RGB or RGB-to-YUV conversion based on V4L2 pixel format, colorspace encoding, and quantization, fills CSC shadow registers, supports bypass, dumps registers, and maps the hardware resource.

## Important APIs, Types, and Functions
Internal types model coefficient organization: `struct quantization`, `struct colorspace`, `struct encoding_direction`, and `struct csc_coeffs`. Exported functions are `csc_dump_regs()`, `csc_set_coeff_bypass()`, `csc_set_coeff()`, and `csc_create()`.

## Control Flow
`csc_create()` allocates `struct csc_data`, looks up a named memory resource, and maps it with `devm_ioremap_resource()`. `csc_set_coeff()` extracts pixel format, YCbCr encoding, and quantization from single-planar or multiplanar V4L2 formats, obtains format metadata, decides conversion direction, normalizes legacy default encoding/quantization to 601/full, selects one of the static 12-coefficient tables, or sets bypass for non-RGB/YUV conversion. Coefficients are packed in pairs into six 32-bit shadow registers.

## State and Persistence
`struct csc_data` stores mapped base, resource, and platform device pointer. Coefficients are static read-only driver data. Register shadow arrays are provided by the caller and later submitted to hardware by the VPE/VIP pipeline.

## Dependencies and Integration Points
Depends on V4L2 format helpers (`v4l2_format_info()`, `v4l2_is_format_yuv()`, `v4l2_is_format_rgb()`), Linux platform resources, MMIO helpers, and exported symbols consumed by TI VPE/VIP drivers.

## Risks and Edge Cases
If `v4l2_format_info()` returns NULL for an unsupported fourcc, downstream format helper behavior must be safe. Defaults intentionally differ from V4L2 standard defaults for historical compatibility. Unsupported encodings fall back to 601/full or 601 limited paths only through defensive code.

## Test Signals
Test RGB-to-YUV and YUV-to-RGB for 601/709 and full/limited quantization, single and multiplanar formats, same-family bypass cases, register packing, invalid resource names, and debug register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/csc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/csc.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/csc.h

## Purpose
Declares TI CSC register offsets, bit masks/shifts, bypass bit, state structure, and exported helper prototypes.

## Important APIs, Types, and Functions
Defines registers `CSC_CSC00` through `CSC_CSC05`, coefficient field masks/shifts for A/B/C/D terms, `CSC_BYPASS`, and `struct csc_data`. Public prototypes mirror `csc.c`: dump, bypass, coefficient setup, and create.

## Control Flow
No executable control flow. The register layout controls how callers allocate/register shadow payload space and how `csc_set_coeff()` packs coefficients.

## State and Persistence
`struct csc_data` holds the MMIO mapping, resource, and platform device pointer. Hardware register state is external and volatile.

## Dependencies and Integration Points
Consumed by `csc.c` and VPE/VIP users that need CSC register programming. Requires V4L2 format types for the `csc_set_coeff()` prototype through includer context.

## Risks and Edge Cases
Mask/shift mistakes would corrupt color conversion. `CSC_BYPASS` shares register 5 with D coefficients, so callers must preserve register payload ordering.

## Test Signals
Build all users, inspect generated register payloads for known CSC matrices, confirm bypass bit placement, and verify MMIO dump offsets match hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/csc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/sc.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/sc.c

## Purpose
Implements TI VPE/VIP scaler helper logic. It maps scaler resources, dumps registers, chooses horizontal/vertical coefficient tables, lays them into coefficient memory with hardware alignment, and fills scaler register shadows for bypass, linear scaling, decimation, polyphase vertical scaling, or RAV vertical downscaling.

## Important APIs, Types, and Functions
Exports `sc_dump_regs()`, `sc_set_hs_coeffs()`, `sc_set_vs_coeffs()`, `sc_config_scaler()`, and `sc_create()`. It depends on `struct sc_data` and coefficient arrays from `sc_coeff.h`.

## Control Flow
`sc_set_hs_coeffs()` chooses upscaling, one-to-one/downscale, or less-than-N/16 tables after accounting for up to two 2x horizontal decimation stages, then copies luma and chroma phases into 8-slot-aligned coefficient memory. `sc_set_vs_coeffs()` chooses vertical tables by output/input ratio. `sc_config_scaler()` clears feature bits, bypasses if dimensions match, otherwise enables linear scaling, configures horizontal decimation and accumulator increments, selects RAV for >4x vertical downscale or polyphase otherwise, then fills the caller's register shadow blocks.

## State and Persistence
`struct sc_data` stores MMIO base/resource, platform device, last loaded coefficient DMA addresses, and `load_coeff_h/load_coeff_v` flags set when new coefficient memory is prepared. Runtime register values are shadowed by the caller and volatile in hardware.

## Dependencies and Integration Points
Depends on platform resources, MMIO mapping, Linux division helpers, exported symbols for TI VPE/VIP drivers, register definitions from `sc.h`, and static coefficients from `sc_coeff.h`.

## Risks and Edge Cases
Dimension equality bypasses all scaling. Downscale ratio selection clamps table index at 8/16 minimum; very small destinations rely on caller validation. Register pointer arithmetic assumes the caller's payload layout matches scaler MMR block ordering. RAV accumulator math has signed intermediate cases that need careful regression coverage.

## Test Signals
Test 1:1 bypass, horizontal upscales, 2x/4x decimation, downscale buckets from 8/16 to 16/16, vertical RAV for >4x downscale, coefficient memory layout size/alignment, and resource mapping failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/sc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/sc.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/sc.h

## Purpose
Defines TI scaler register offsets, masks, feature bits, coefficient geometry, frame-size limits, state structure, and exported scaler helper prototypes.

## Important APIs, Types, and Functions
Important definitions include `CFG_SC0` feature bits, accumulator/size/threshold masks for registers SC1-SC25, `SC_NUM_PHASES`, `SC_H_NUM_TAPS`, `SC_V_NUM_TAPS`, `SC_NUM_TAPS_MEM_ALIGN`, max dimensions, `SC_COEF_SRAM_SIZE`, and `struct sc_data`. Prototypes expose register dump, coefficient setup, scaler config, and resource creation.

## Control Flow
No executable control flow is present, but constants encode the register contract used by `sc.c` and hardware payload builders.

## State and Persistence
`struct sc_data` tracks mapped registers, coefficient load flags, loaded coefficient DMA addresses, and platform device pointer. The rest is compile-time configuration.

## Dependencies and Integration Points
Used by `sc.c` and TI VPE/VIP drivers. Coefficient geometry must match `sc_coeff.h` array dimensions and the VPDMA/scaler coefficient SRAM payload layout.

## Risks and Edge Cases
Incorrect masks or shifts can corrupt unrelated register fields. Max width/height of 2047 must be enforced by callers before `sc_config_scaler()`. Coefficient SRAM size depends on phase count, two luma/chroma sets, aligned taps, and 16-bit coefficients.

## Test Signals
Compile-time array sizing, register-payload tests for known dimensions, hardware scaling validation at min/max sizes, and coefficient DMA loading checks are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/sc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/sc_coeff.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/sc_coeff.h

## Purpose
Provides static horizontal and vertical polyphase scaler coefficient tables for the TI VPE/VIP scaler.

## Important APIs, Types, and Functions
Defines horizontal table indices `HS_UP_SCALE`, `HS_LT_9_16_SCALE` through `HS_LE_16_16_SCALE`, vertical indices `VS_UP_SCALE` through `VS_1_TO_1_SCALE`, and two static arrays: `scaler_hs_coeffs[13][SC_NUM_PHASES * 2 * SC_H_NUM_TAPS]` and `scaler_vs_coeffs[15][SC_NUM_PHASES * 2 * SC_V_NUM_TAPS]`.

## Control Flow
No functions execute here. `sc_set_hs_coeffs()` and `sc_set_vs_coeffs()` select rows by scale ratio and copy luma/chroma phase coefficients into hardware-aligned coefficient memory.

## State and Persistence
The arrays are read-only compiled data. They persist as part of the module/kernel image and are shared by all scaler instances.

## Dependencies and Integration Points
Requires `SC_NUM_PHASES`, tap counts, and related constants from `sc.h` before inclusion. Coefficient dimensions and ordering must match the copy loops in `sc.c` and hardware coefficient SRAM expectations.

## Risks and Edge Cases
The declared array has more rows than the named indices currently used, so size and index assumptions should be reviewed before edits. Any value/order change can alter image quality or cause hardware coefficient misalignment. Luma and chroma sections are packed back-to-back for every table.

## Test Signals
Compile array bounds with `sc.c`, verify coefficient memory layout for horizontal 7-tap and vertical 5-tap copies, compare known scaling output quality, and regression-test all ratio buckets including 1:1, upscaling, and strongest downscaling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/sc_coeff.h -->

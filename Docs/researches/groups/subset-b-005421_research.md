# Research group: subset-b-005421

This grouped report covers the requested Meson VDEC, Allwinner Cedrus VPU, and Allwinner sun6i ISP source files. Each file section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_hevc.c -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_hevc.c

Purpose: implements the Amlogic `VDEC_HEVC` hardware block operations used by the Meson stateless video decoder for HEVC-family firmware execution, notably VP9 formats in `vdec_platform.c`. It owns firmware upload into HEVC IMEM, stream FIFO setup, ES parser routing, clock/power sequencing, and the exported `struct amvdec_ops vdec_hevc_ops`.

Important APIs/functions: `vdec_hevc_load_firmware()` requests firmware, validates at least `MC_SIZE` bytes, DMA-copies 16 KiB into IMEM through `HEVC_IMEM_DMA_*`, polls DMA completion, and frees the temporary coherent buffer. `vdec_hevc_stbuf_init()` initializes HEVC stream buffer registers from `sess->vififo_paddr/size`. `vdec_hevc_conf_esparser()` routes the parser FIFO to the HEVC engine and enables stream control bits. `vdec_hevc_vififo_level()` reads `HEVC_STREAM_LEVEL`. `vdec_hevc_start()` and `vdec_hevc_stop()` are the public ops; `__vdec_hevc_start()` and `__vdec_hevc_stop()` contain the common power, reset, memory, firmware, and codec delegation steps.

Control flow: start optionally enables the `vdec_hevcf_clk` for G12A/SM1, then enables `vdec_hevc_clk`, powers up the AO domain, resets `DOS_SW_RESET3`, enables DOS clock gates, powers HEVC memory, removes isolation, initializes the stream buffer, loads firmware selected by `sess->fmt_out->firmware_path`, calls `sess->fmt_out->codec_ops->start(sess)`, resets firmware processor bits, starts `HEVC_MPSR`, and waits briefly. Stop masks mailbox IRQs, stops the firmware processor, delegates codec stop when `sess->priv` exists, re-enables isolation, powers down HEVC memory and AO sleep bits, then disables clocks.

State and persistence: no persistent disk state. Runtime state lives in hardware registers, clocks, AO regmap bits, the session FIFO addresses, and codec-private `sess->priv`. Firmware memory is transient: allocated with `dma_alloc_coherent()`, copied to IMEM, and freed before returning.

Dependencies/integration: depends on Linux firmware loading, DMA coherent memory, clk framework, Amlogic DOS/AO register helpers, `vdec_helpers.h`, `hevc_regs.h`, `dos_regs.h`, and codec ops chosen by the format table. It integrates with `vdec_platform.c` via the exported `vdec_hevc_ops` and with codec-specific VP9/HEVC support through `amvdec_codec_ops`.

Risks: `mc_addr` and `mc_addr_map` are static locals even though allocation is per call; this is harmless for normal serialized session startup but awkward if concurrency assumptions change. Firmware DMA polling is a tight decrement loop without sleep or timeout based on time. On `__vdec_hevc_start()` failure after enabling `vdec_hevcf_clk`, common cleanup disables only `vdec_hevc_clk`; outer `vdec_hevc_start()` handles the f-clock path. AO isolation masks differ by SM1 versus older revisions and are easy to regress when adding revisions.

Test signals: verify firmware missing/short-file failures, successful start/stop on GXL/GXM/G12A/SM1, VP9 decode through `vdec_hevc_ops`, FIFO level reporting under parser feed, and error cleanup paths after firmware-load or codec-start failure. Runtime PM/clock-leak tests should check both normal and failed starts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_hevc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_hevc.h -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_hevc.h

Purpose: declares the HEVC-engine VDEC operations exported by `vdec_hevc.c`.

Important APIs/types: includes `vdec.h` for `struct amvdec_ops` and declares `extern struct amvdec_ops vdec_hevc_ops`.

Control flow: none directly; consumers include the header to assign `&vdec_hevc_ops` in platform format tables.

State and persistence: no state.

Dependencies/integration: couples the HEVC hardware backend to `vdec_platform.c` and any future platform tables without exposing private register routines.

Risks: the exported object is non-const, so accidental mutation by another compilation unit would be possible though not expected by driver style.

Test signals: build coverage that includes both `vdec_hevc.c` and platform table users is sufficient; runtime coverage comes through formats that select `vdec_hevc_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_hevc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_platform.c -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_platform.c

Purpose: defines per-SoC Amlogic VDEC format capability tables and exports `struct vdec_platform` instances for GXBB, GXL, GXLX, GXM, G12A, and SM1 revisions. It is the central source of supported compressed pixelformats, limits, firmware names, decoder engine ops, codec ops, capture formats, and V4L2 flags.

Important APIs/types: static `struct amvdec_format` arrays describe each source codec entry. Each entry sets `.pixfmt`, buffer bounds, max resolution, `.vdec_ops` (`vdec_1_ops` or `vdec_hevc_ops`), `.codec_ops` (`codec_h264_ops`, `codec_mpeg12_ops`, `codec_vp9_ops`), firmware path, capture pixfmt list, and compressed/dynamic-resolution flags. The exported `vdec_platform_*` constants point at those arrays and set `enum vdec_revision`.

Control flow: no executable flow beyond module firmware declarations. Probe code elsewhere selects the platform instance from OF data; format negotiation then iterates the table to expose V4L2 capabilities and choose the engine/backend for sessions.

State and persistence: immutable static tables only. Firmware paths are persistent ABI-like strings because userspace/kernel packaging must provide those blobs.

Dependencies/integration: includes `vdec_platform.h`, `vdec.h`, engine headers, and codec headers. Integrates with firmware packaging through `MODULE_FIRMWARE()` declarations and with runtime power quirks through the revision consumed by `vdec_hevc.c`.

Risks: capability drift is easy because entries duplicate MPEG/H264/VP9 limits and firmware names across SoCs. VP9 uses the HEVC hardware ops while H264/MPEG use `vdec_1_ops`; wrong pairing would fail at firmware or register level. SM1 VP9 points to `sm1_vp9_mmu.bin`, unlike older VP9 firmware. Missing `V4L2_FMT_FLAG_DYN_RESOLUTION` for formats that can change resolution would affect userspace behavior.

Test signals: enumerate formats per compatible SoC, request each firmware named by the table, decode H264/MPEG2/VP9 samples at table max and boundary resolutions, and verify dynamic resolution events for H264/VP9 entries only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_platform.h -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_platform.h

Purpose: declares the platform contract for Amlogic Meson VDEC SoC variants.

Important APIs/types: `enum vdec_revision` identifies GXBB, GXL, GXLX, GXM, G12A, and SM1. `struct vdec_platform` stores a pointer to a format array, its count, and the revision. Extern declarations expose one platform descriptor per supported revision.

Control flow: none. Runtime users dereference selected descriptors to drive format enumeration and revision-specific hardware behavior.

State and persistence: immutable platform descriptors are defined in `vdec_platform.c`; no mutable state is declared here.

Dependencies/integration: includes `vdec.h` and forward-declares `struct amvdec_format`. The revision enum is consumed by engine backends such as `vdec_hevc.c` for clock and AO power differences.

Risks: appending revisions is safer than reordering because table initializers use enum values semantically. `num_formats` is `const u32` inside the struct, so descriptors are intended immutable.

Test signals: compile/link checks for all exported platform descriptors and runtime OF matching that picks the correct revision-specific table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/meson/vdec/vdec_platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/Kconfig -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/Kconfig

Purpose: top-level Kconfig menu gate for Allwinner sunXi staging media drivers.

Important APIs/types: `config VIDEO_SUNXI` is a bool depending on `ARCH_SUNXI || COMPILE_TEST`. When enabled, it sources the Cedrus VPU and sun6i ISP Kconfig files.

Control flow: Kconfig-only. Selecting `VIDEO_SUNXI` exposes child prompts but does not itself build a driver.

State and persistence: build configuration state only.

Dependencies/integration: integrates with `drivers/staging/media/Kconfig` and child directories `sunxi/cedrus` and `sunxi/sun6i-isp`.

Risks: disabling this parent hides all child drivers, which may surprise users because the help text notes it does not compile anything directly. `COMPILE_TEST` broadens build coverage beyond sunXi architecture.

Test signals: Kconfig generation with `ARCH_SUNXI`, non-sunxi `COMPILE_TEST`, and parent disabled should show or hide child symbols as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/Makefile -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/Makefile

Purpose: dispatches builds into Allwinner sunxi staging media subdirectories.

Important APIs/types: `obj-$(CONFIG_VIDEO_SUNXI_CEDRUS) += cedrus/` and `obj-$(CONFIG_VIDEO_SUN6I_ISP) += sun6i-isp/`.

Control flow: kbuild descends into each subdirectory only when the corresponding config is enabled.

State and persistence: build graph only.

Dependencies/integration: tied to child Kconfig symbols defined under the same tree.

Risks: none beyond stale symbol names causing a driver to stop building.

Test signals: `make M=drivers/staging/media/sunxi` with each symbol enabled should enter the expected subdirectory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/Kconfig -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/Kconfig

Purpose: defines the build option for the Allwinner Cedrus VPU stateless decoder.

Important APIs/types: `config VIDEO_SUNXI_CEDRUS` is a tristate prompt depending on `VIDEO_DEV`, `RESET_CONTROLLER`, `HAS_DMA`, and `OF`; it selects `MEDIA_CONTROLLER`, `SUNXI_SRAM`, `VIDEOBUF2_DMA_CONTIG`, and `V4L2_MEM2MEM_DEV`.

Control flow: Kconfig-only; when built as a module, the module is named `sunxi-cedrus`.

State and persistence: build configuration only.

Dependencies/integration: declares mandatory framework dependencies used by the driver: V4L2/video device core, media controller, reset, DMA-contiguous vb2, memory-to-memory helpers, OF matching, and SRAM claiming.

Risks: missing `MEDIA_REQUEST_API` is not explicit here even though the driver requires requests on its output queue through vb2; this may be selected elsewhere by media controller/V4L2 configuration in this kernel version.

Test signals: randconfig and COMPILE_TEST builds should confirm all selected frameworks satisfy compile/link dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/Makefile -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/Makefile

Purpose: builds the Cedrus driver objects into `sunxi-cedrus.o`.

Important APIs/types: `obj-$(CONFIG_VIDEO_SUNXI_CEDRUS) += sunxi-cedrus.o`; the composite object includes core, video, hardware, decode dispatcher, and MPEG2/H264/H265/VP8 codec files.

Control flow: kbuild links all listed codec implementations into a single module/built-in object.

State and persistence: build graph only.

Dependencies/integration: object list mirrors extern decoder ops declared in `cedrus.h`; removing a codec object without changing controls/formats would break symbols.

Risks: codec capabilities are runtime gated by SoC variant, not by separate build options, so all listed codec code is always compiled when Cedrus is enabled.

Test signals: compile with `CONFIG_VIDEO_SUNXI_CEDRUS=m` and `=y`; inspect `modinfo sunxi-cedrus` and symbol resolution for all `cedrus_dec_ops_*`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus.c -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus.c

Purpose: main Cedrus VPU platform driver and V4L2 mem2mem device setup. It registers `/dev/video*`, media controller entities, V4L2 controls for stateless codecs, request validation, file operations, SoC variants, OF match data, and runtime PM hooks.

Important APIs/functions: `cedrus_try_ctrl()` validates H264 and HEVC SPS controls, restricting chroma to 4:2:0 and bit depth to hardware capability/current buffer state. `cedrus_controls[]` declares all stateless MPEG2/H264/HEVC/VP8 controls with capability masks. `cedrus_find_control_data()` and `cedrus_get_num_of_controls()` provide per-job control lookup. `cedrus_init_ctrls()` creates only controls supported by `ctx->dev->capabilities`. `cedrus_request_validate()` enforces exactly one buffer per media request. `cedrus_open()` allocates a context, initializes mem2mem queues, default formats, and controls; `cedrus_release()` tears them down. `cedrus_probe()` wires hardware, V4L2, mem2mem, media controller, and video registration. `cedrus_remove()` unwinds runtime resources.

Control flow: platform probe allocates `cedrus_dev`, calls `cedrus_hw_probe()`, registers V4L2 and media devices, initializes `v4l2_m2m_dev`, registers the decoder video node, registers the media controller, and publishes the media device. File open creates a per-file `cedrus_ctx`; queue init is delegated to `cedrus_queue_init()`. Decode jobs later enter through `cedrus_device_run()` from mem2mem ops. Remove cancels watchdog work, unregisters media/V4L2 objects, and releases hardware.

State and persistence: persistent runtime state includes `cedrus_dev` capabilities, mapped base registers, clocks, reset control, mem2mem device, watchdog work, and per-open `cedrus_ctx` controls/formats/codec scratch pointers. No disk state. Capture-buffer codec side data can survive across jobs until streaming stops.

Dependencies/integration: depends on V4L2 controls, media requests, media controller, V4L2 mem2mem, vb2, platform/OF matching, and hardware setup in `cedrus_hw.c`. SoC variants define capability bits and `mod_rate` used by hardware setup.

Risks: request validation only checks buffer count, while codec setup assumes required controls are present and valid. Bit-depth changes are blocked once capture buffers are busy; regressions here can mis-size H265 10-bit capture buffers. Capability-gated controls and formats must stay in sync. Error paths in `cedrus_init_ctrls()` must free partially created handlers and pointer arrays.

Test signals: probe/remove on each compatible, media graph validation, open/close leak tests, request submission with zero/multiple buffers, invalid H264/HEVC SPS controls, HEVC 10-bit buffer allocation behavior on H6-capable variants, and V4L2 compliance for mem2mem/stateless decoder nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus.h -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus.h

Purpose: central Cedrus driver header defining capabilities, shared context/device structures, per-codec run/control state, decoder operation vectors, register access helpers, buffer address helpers, and exported codec ops.

Important APIs/types: capability bits describe untiled output and MPEG2/H264/H265/VP8/H265-10 support. `struct cedrus_run` carries the current source/destination buffers and a union of codec-specific V4L2 control pointers. `struct cedrus_buffer` extends mem2mem buffers with H264/H265 per-buffer MV-column scratch state. `struct cedrus_ctx` stores file handle, source/capture formats, current codec ops, bit depth, control handler array, and codec scratch buffers. `struct cedrus_dec_ops` is the codec backend interface for IRQ clear/disable/status, setup, start/stop, trigger, and extra capture size. `struct cedrus_dev` stores global V4L2/media/hardware state. Inline helpers wrap register IO, polling, DMA plane address calculation, reference buffer timestamp lookup, buffer casting, and capability checks.

Control flow: codec files implement `cedrus_dec_ops_*`; `cedrus_video.c` chooses `ctx->current_codec`; `cedrus_dec.c` builds a `cedrus_run`; hardware IRQ calls through `current_codec` methods.

State and persistence: defines all mutable in-memory driver state, including per-session scratch DMA allocations and per-capture-buffer motion-vector allocations. No persistent storage.

Dependencies/integration: includes V4L2 controls/device/mem2mem/vb2 DMA-contig, platform device, workqueue, and iopoll. It is included by nearly every Cedrus source file and is therefore the shared ABI inside the module.

Risks: unions require codec-specific code to respect the current pixelformat; stale fields can remain from previous sessions unless start/stop paths clean them. Address helpers assume single-plane contiguous buffers with chroma plane offsets computed from `bytesperline * height`. `cedrus_write_ref_buf_addr()` writes zero if a timestamp lookup fails, which may surface as hardware decode errors rather than early validation.

Test signals: compile-time coverage of all codec ops, decode tests with missing/invalid reference timestamps, streamoff cleanup for per-buffer scratch state, and format/address tests for tiled and untiled capture layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_dec.c -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_dec.c

Purpose: mem2mem job dispatcher for Cedrus stateless decode jobs. It converts queued V4L2 buffers and request controls into a `struct cedrus_run`, delegates setup/trigger to the selected codec backend, and completes failed jobs.

Important APIs/functions: `cedrus_device_run(void *priv)` is registered as `v4l2_m2m_ops.device_run`. It fetches next source and destination buffers, applies request controls via `v4l2_ctrl_request_setup()`, fills codec-specific control pointers based on `ctx->src_fmt.pixelformat`, copies metadata from source to destination, configures output format registers through `cedrus_dst_format_set()`, calls `ctx->current_codec->setup()`, completes controls, schedules the watchdog on success, and calls `trigger()`.

Control flow: V4L2 mem2mem core invokes `cedrus_device_run()` when a source/destination pair is ready. On setup error, it logs and calls `v4l2_m2m_buf_done_and_job_finish(..., VB2_BUF_STATE_ERROR)`. On success, IRQ or watchdog later finishes the job.

State and persistence: transient `cedrus_run` only. It relies on controls stored in `ctx->hdl`, queued buffer state in mem2mem queues, and codec scratch state held in `ctx`/capture buffers.

Dependencies/integration: depends on `cedrus_find_control_data()`, `cedrus_get_num_of_controls()`, `cedrus_dst_format_set()`, V4L2 request controls, and codec backend ops selected by `cedrus_video.c`.

Risks: missing controls yield NULL pointers that codec setup code generally dereferences, so robust userspace/request validation matters. HEVC entry point count uses control element count rather than slice value alone and rejects mismatches in codec setup. Watchdog is scheduled only after setup succeeds.

Test signals: submit each supported pixelformat with complete and incomplete control sets, verify metadata propagation, ensure setup errors complete both buffers as error, and confirm watchdog/IRQ finish paths are reached after trigger.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_dec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_dec.h -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_dec.h

Purpose: declares the Cedrus mem2mem job entry point.

Important APIs/types: `void cedrus_device_run(void *priv);`.

Control flow: no logic; included by `cedrus.c` to register mem2mem ops and by implementation users.

State and persistence: none.

Dependencies/integration: binds `cedrus.c` and `cedrus_dec.c`.

Risks: minimal; signature must match `v4l2_m2m_ops.device_run`.

Test signals: build/link check and runtime mem2mem job scheduling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_dec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_h264.c -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_h264.c

Purpose: H.264 stateless decode backend for Cedrus. It programs H264 engine registers/SRAM from V4L2 stateless H264 controls, manages decoded picture buffer mappings, allocates per-session/per-buffer scratch DMA memory, handles IRQ status, and exports `cedrus_dec_ops_h264`.

Important APIs/functions: SRAM helpers write frame list, ref lists, scaling lists, and prediction weight tables. `cedrus_write_frame_list()` maps V4L2 DPB entries to Cedrus frame slots, allocates per-output MV column buffers, and writes `VE_H264_OUTPUT_FRAME_IDX`. `cedrus_set_params()` programs bitstream addresses, optional large-width deblock/intrapred DRAM buffers, software decode initialization, bit skipping, PPS/SPS/slice registers, QP registers, status clear, and IRQ enable. `cedrus_h264_start()` allocates pic-info, neighbor-info, and optional 4K scratch buffers. `cedrus_h264_stop()` frees per-capture-buffer MV columns and context scratch. `cedrus_h264_trigger()` starts slice decode.

Control flow: stream start allocates context scratch. Each decode job enables the engine, clears rotation, points extra buffers, writes scaling/frame/reference state, sets bitstream and slice parameters, then trigger writes `VE_H264_TRIGGER_TYPE_AVC_SLICE_DECODE`. IRQ status maps decode/VLD errors to `CEDRUS_IRQ_ERROR` and slice-complete to `CEDRUS_IRQ_OK`.

State and persistence: per-session scratch buffers live from OUTPUT streamon to streamoff. Per-capture-buffer MV-column buffers are allocated lazily and persist across jobs until stop. Buffer slot `position` and `pic_type` preserve DPB mapping across frames.

Dependencies/integration: consumes V4L2 H264 decode params, SPS, PPS, scaling matrix, slice params, pred weights, vb2 DMA addresses, and common Cedrus engine/format helpers. It uses `cedrus_regs.h` for all register fields.

Risks: comments document unreliable `VE_H264_VLD_OFFSET`, so bit skipping is done through repeated flush triggers. Several buffer-size formulas come from CedarX/BSP sources and include FIXMEs for frame-only streams and 4K H6 behavior. DPB timestamp misses silently skip refs. MV-column allocation failures abort setup mid-job. Large-width paths require extra buffers sized exactly for hardware expectations.

Test signals: H264 baseline/main/high streams, field/MBAFF streams, weighted prediction, scaling matrix present/absent, B-slices with both ref lists, dynamic resolution, 4K streams on H6-like hardware, invalid DPB timestamps, streamoff leak checks, and IRQ error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_h264.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_h265.c -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_h265.c

Purpose: HEVC/H.265 stateless decode backend for Cedrus. It maps V4L2 HEVC controls into H265 engine registers/SRAM, supports tiles/WPP entry points, 8-bit and selected 10-bit capture sizing, per-buffer MV column buffers, and exports `cedrus_dec_ops_h265`.

Important APIs/functions: `cedrus_h265_2bit_size()` computes extra 2-bit plane size for 10-bit output packing. IRQ helpers inspect/clear/disable `VE_DEC_H265_*` status/control. SRAM helpers write frame info, DPB entries, reference lists, prediction weights, and scaling lists. `cedrus_h265_write_tiles()` configures tile start/end CTBs and entry point buffer contents. `cedrus_h265_setup()` validates entry point count, allocates per-output MV column buffer, enables engine, programs bitstream addresses/length, CTB address, tiles, SWDEC bit alignment, NAL/SPS/PPS/slice controls, picture size, scaling list, neighbor buffer, DPB/output frame info, ref lists, weighted prediction, 10-bit offset/stride, and IRQ mask. `cedrus_h265_start()` allocates neighbor info and coherent entry-point buffers; `cedrus_h265_stop()` frees them plus per-buffer MV columns; `extra_cap_size()` reports extra capture size for >8-bit.

Control flow: OUTPUT streamon allocates context buffers. Each job programs source slice data and all HEVC metadata, then trigger writes `VE_DEC_H265_TRIGGER_DEC_SLICE`. IRQ completion is handled by common `cedrus_irq()`.

State and persistence: context neighbor and entry-point buffers persist during streaming. Per-capture-buffer H265 MV column buffers are lazy and persist until streamoff. `ctx->bit_depth` is set by SPS control validation and affects capture format size and 10-bit programming.

Dependencies/integration: consumes V4L2 HEVC SPS/PPS/slice/decode/scaling/entry-point controls, common Cedrus helpers, vb2 timestamp buffer lookup, and register macros. Capability `CEDRUS_CAPABILITY_H265_10_DEC` gates bit depth in `cedrus.c`.

Risks: `cedrus_h265_irq_status()` does not return `CEDRUS_IRQ_NONE` when no status bits are set; with the common IRQ handler this can interpret an irrelevant/early interrupt as error after masking. Tile/entry-point buffer layout differs for WPP versus tiles and is sensitive to `num_entry_point_offsets`. Slice data with `data_byte_offset == 0` is unsupported. Padding parsing depends on hardware show/skip bits and returns `-EINVAL` if the inspected padding byte is zero. Neighbor buffer sizing is BSP-derived and comment notes H6 may need doubled size for 10-bit.

Test signals: HEVC I/P/B slices, tiles, WPP, weighted prediction, scaling lists, 8-bit and 10-bit H6 streams, mismatched entry-point control counts, `data_byte_offset` boundary cases, DPB timestamp misses, large resolution streams, and IRQ behavior under shared interrupt noise.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_h265.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_hw.c -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_hw.c

Purpose: common Cedrus hardware management: engine mode selection, capture output format register programming, IRQ handling, watchdog timeout recovery, runtime PM suspend/resume, and platform hardware resource acquisition/release.

Important APIs/functions: `cedrus_engine_enable()` writes `VE_MODE` based on source codec, width flags, DDR mode, and write mode. `cedrus_engine_disable()` disables the engine. `cedrus_dst_format_set()` configures tiled or untiled capture layout registers. `cedrus_irq()` cancels watchdog, gets current context, dispatches codec IRQ status/clear/disable, and completes the mem2mem job. `cedrus_watchdog()` resets hardware and completes the job as error after timeout. `cedrus_hw_suspend()` disables clocks and asserts reset; `cedrus_hw_resume()` resets hardware and enables AHB/MOD/RAM clocks. `cedrus_hw_probe()` obtains variant data, IRQ, reserved memory, SRAM, clocks, reset, MMIO, module clock rate, and runtime PM. `cedrus_hw_remove()` disables PM and releases SRAM/reserved memory.

Control flow: core probe calls `cedrus_hw_probe()` before registering V4L2 nodes. Streaming output queue calls runtime PM resume through `cedrus_video.c`, which invokes `cedrus_hw_resume()` as needed. Decode jobs enable engine and start hardware; completion happens through IRQ or watchdog.

State and persistence: global hardware state in `cedrus_dev`: capabilities, MMIO base, clocks, reset control, delayed watchdog work. Runtime PM owns clock/reset lifetime.

Dependencies/integration: uses Linux clk, reset, IRQ, PM runtime, OF reserved memory, DMA mapping, sunxi SRAM, V4L2 mem2mem, and codec ops. Register macros come from `cedrus_regs.h`.

Risks: watchdog reset does not call codec-specific IRQ clear/disable and may leave registers in a reset-dependent state. IRQ handler assumes watchdog cancellation tells whether job already timed out. `platform_get_irq()` treats IRQ 0 as failure due `<= 0`, which matches older conventions but can be problematic on systems where IRQ 0 is valid. Output format programming for tiled uses `VE_CHROMA_BUF_LEN` with an output-format constant, which is hardware-specific and easy to misread.

Test signals: runtime PM cycle tests, IRQ completion for all codecs, watchdog timeout injection, reserved memory absent/present, SRAM claim failure, clock rate failure, streamon/streamoff clock balance, and tiled versus untiled capture format register validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_hw.h -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_hw.h

Purpose: declares common Cedrus hardware helper APIs.

Important APIs/types: declarations for engine enable/disable, destination format programming, suspend/resume, probe/remove, and watchdog work function.

Control flow: no logic; implementations are in `cedrus_hw.c` and callers are core, video queue, and codec files.

State and persistence: none directly.

Dependencies/integration: requires `struct cedrus_ctx`, `struct cedrus_dev`, `struct v4l2_pix_format`, and `struct device` definitions available through `cedrus.h` include order.

Risks: helper declarations are broadly used; signature changes ripple through codecs and core queue paths.

Test signals: build coverage and runtime decode paths that exercise engine and PM helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_mpeg2.c -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_mpeg2.c

Purpose: MPEG1/2 stateless decode backend for Cedrus, programming MPEG engine registers from MPEG2 sequence/picture/quantisation controls and exporting `cedrus_dec_ops_mpeg2`.

Important APIs/functions: IRQ helpers inspect `VE_DEC_MPEG_STATUS`, clear status, and disable IRQ bits. `cedrus_mpeg2_setup()` enables the MPEG engine, writes intra and non-intra quant matrices, packs MPEG picture header flags/F-codes, programs coded/bound dimensions, writes forward/backward reference buffer addresses from timestamps, writes destination addresses, source bitstream length/address/end, resets macroblock/error tracking, and enables finish/error/data-request IRQs. `cedrus_mpeg2_trigger()` starts hardware MPEG VLD/MPEG2 decode at macroblock boundary.

Control flow: each MPEG2 job configures all registers in setup, then trigger starts decode. The common IRQ handler maps backend status to buffer done/error.

State and persistence: no codec-private persistent allocations; state is per-job register programming and capture reference buffers located by timestamp.

Dependencies/integration: consumes V4L2 MPEG2 stateless controls, vb2 DMA-contig source/capture buffers, and common Cedrus engine/address helpers.

Risks: quantisation control is assumed present. Reference timestamp lookup can yield zero addresses. MPEG1 source pixfmt shares this backend through platform formats but trigger sets MPEG2 mode here; in this tree Cedrus exposes only `V4L2_PIX_FMT_MPEG2_SLICE` in `cedrus_video.c`.

Test signals: I/P/B MPEG2 slices, custom quant matrices, missing forward/backward references, min/max resolution, short payloads, and IRQ error/data-request paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_mpeg2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_regs.h -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_regs.h

Purpose: register offset and bitfield macro catalog for the Allwinner Cedrus video engine used by MPEG, H264, H265, VP8, and some ISP/AVC-related blocks.

Important APIs/macros: `SHIFT_AND_MASK_BITS()` is the common field packer. Common engine offsets define `VE_MODE`, buffer control, primary/secondary output formats, strides, and version. MPEG macros cover picture headers, coded/bound sizes, control/trigger/status, bitstream addresses, reconstruction/reference addresses, quant matrix input, and error/MB status. H265 macros cover NAL/SPS/PPS/slice headers, CTB addresses, control/trigger/status, bitstream addresses, tile/entry-point/scaling-list/SRAM registers, frame info offsets, ref lists, and 10-bit configuration. H264/VP8 macros share the H264 engine space for SPS/PPS/slice, VLD, SRAM port, trigger/status, VP8 probability/segmentation/filter/refs, and output addresses.

Control flow: no executable flow; codec and hardware source files compose register values through these macros before `cedrus_write()`.

State and persistence: defines hardware ABI constants only.

Dependencies/integration: included by all Cedrus codec/hardware implementations. It assumes Linux `BIT()`, `GENMASK()`, `DIV_ROUND_UP()`, and alignment helpers are available through included kernel headers.

Risks: field macros often mask shifted values but do not validate input range; callers must bound values from V4L2 controls. Address base macros drop low bits or reorder high bits according to hardware requirements; wrong buffer alignment or DMA address width assumptions can corrupt decode. The file also contains unused/less-used ISP/AVC offsets that may not be exercised by current decode paths.

Test signals: compile-time macro use across all codecs, register trace comparison against known-good BSP values, high DMA address tests for address packing, tiled/untiled output validation, and 10-bit HEVC output layout tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_video.c -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_video.c

Purpose: V4L2 ioctl and vb2 queue implementation for Cedrus. It exposes source/capture formats, validates and applies formats, chooses codec backend ops, manages streaming lifecycle, and initializes mem2mem output/capture queues.

Important APIs/functions: `cedrus_formats[]` lists encoded source and decoded capture pixelformats with direction/capability masks. `cedrus_find_format()` picks requested or first valid format. `cedrus_prepare_format()` clamps dimensions and computes bytesperline/sizeimage for encoded, tiled NV12, and untiled YUV formats. `cedrus_try/s/g_fmt_*` implement format negotiation. `cedrus_s_fmt_vid_out_p()` sets source format, toggles `VB2_V4L2_FL_SUPPORTS_M2M_HOLD_CAPTURE_BUF` for H264/HEVC, selects `ctx->current_codec`, propagates colorimetry, and resets capture format. Queue ops validate buffer sizes, queue mem2mem buffers, complete request controls, start codec/PM on OUTPUT streamon, and stop/free on OUTPUT streamoff. `cedrus_queue_init()` creates OUTPUT and CAPTURE vb2 queues, with OUTPUT requiring media requests.

Control flow: open initializes default output format, which selects a default codec and capture format. Userspace sets OUTPUT then CAPTURE. Streamon OUTPUT resumes runtime PM and calls codec `start()`. Jobs are scheduled by mem2mem; streamoff calls codec `stop()`, runtime PM put, and marks queued buffers error.

State and persistence: per-context `src_fmt`, `dst_fmt`, `current_codec`, and bit depth. Queue state persists during streaming. Capture `sizeimage` can include codec-specific extra size, notably H265 10-bit extra 2-bit data.

Dependencies/integration: integrates V4L2 ioctl core, events, mem2mem, vb2 DMA-contig, runtime PM, Cedrus codec ops, and hardware output format programming.

Risks: format changes are constrained by busy/streaming queues and capture buffer allocation; mistakes can break dynamic resolution. OUTPUT queue `requires_requests = true`, so non-request userspace will fail. H264/HEVC hold-capture-buffer support is enabled only for those codecs. Capture format defaults to the first capability-valid output, which differs by untiled capability.

Test signals: V4L2 compliance for enum/try/set/get formats, busy queue format-change rejection, request-required behavior, streamon failure cleanup, H265 10-bit `sizeimage`, dynamic resolution with same source pixfmt, and queue cleanup completing outstanding requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_video.h -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_video.h

Purpose: declares Cedrus video/queue format structures and public video helper APIs.

Important APIs/types: `struct cedrus_format` stores pixelformat, direction mask, and capability mask. Exports `cedrus_ioctl_ops`, `cedrus_queue_init()`, `cedrus_prepare_format()`, `cedrus_reset_cap_format()`, and `cedrus_reset_out_format()`.

Control flow: no implementation; `cedrus.c` uses the ioctl ops and queue init, while control validation uses capture reset.

State and persistence: none directly.

Dependencies/integration: couples core context creation with video format/queue implementation.

Risks: declarations rely on `struct cedrus_ctx`/V4L2 types from inclusion context.

Test signals: build coverage and V4L2 open/queue initialization paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_vp8.c -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_vp8.c

Purpose: VP8 stateless decode backend for Cedrus. It uses the H264 hardware engine mode for VP8, builds/updates the hardware probability table, performs necessary hardware bitstream parsing side effects, programs VP8 registers, and exports `cedrus_dec_ops_vp8`.

Important APIs/functions: static `prob_table_init[]` seeds hardware entropy/probability tables; `k_mv_entropy_update_probs` mirrors VP8 spec probabilities. `read_bits()` drives the hardware bit reader through H264 trigger/status registers. Header-processing helpers parse segmentation, loop filter deltas, quant deltas, reference refresh, and MV probability updates for hardware state. `cedrus_vp8_update_probs()` copies V4L2 VP8 frame entropy fields into the coherent probability buffer. `cedrus_vp8_setup()` enables H264/VP8 engine mode, programs source partition sizes, VLD offsets/address/length, entropy-probability buffer, PPS/filter/segmentation/reference flags, invokes header parsing, resets modified registers, writes quant/size/segment/filter/ref/destination registers, and enables IRQs. `cedrus_vp8_start()` allocates the coherent probability buffer and seeds it; `cedrus_vp8_stop()` disables engine and frees it.

Control flow: stream start allocates and initializes probability memory. Each job updates probabilities from controls, initializes hardware bitstream reader, runs header parsing to mutate internal hardware state, then trigger writes `VE_H264_TRIGGER_TYPE_VP8_SLICE_DECODE`. Completion uses H264-like IRQ bits.

State and persistence: per-session coherent entropy probability buffer persists while streaming. `last_frame_p_type`, `last_filter_type`, and `last_sharpness_level` persist across frames when loop filter level is nonzero and are folded into the next PPS register.

Dependencies/integration: consumes `V4L2_CID_STATELESS_VP8_FRAME`, V4L2 VP8 helpers/macros, vb2 DMA-contig buffers, and common Cedrus reference-address helpers.

Risks: comments explicitly note the driver must parse frame headers with hardware despite userspace parsing; bypassing this produces bad images. Probability buffer offsets were reverse-engineered, including an unknown 2048-byte seed offset. Header size handling differs for key/inter frames. `VE_H264_VLD_LEN` uses full plane size rather than payload for one register, while end address uses payload. Persistent last-filter fields update only when filter level is nonzero.

Test signals: VP8 key/inter frames, segmentation on/off, loop filter delta updates, token partitions, golden/alt reference frames, probability update cases, corrupted headers, stream restart state reset, and comparison against software decode output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_vp8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/Kconfig -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/Kconfig

Purpose: build option for the Allwinner A31-family ISP staging driver.

Important APIs/types: `config VIDEO_SUN6I_ISP` is tristate and depends on V4L platform/video support, sunxi or compile-test, PM, common clock, and DMA. It selects media controller, V4L2 subdev API, DMA-contig and vmalloc vb2 backends, V4L2 fwnode, and regmap MMIO.

Control flow: Kconfig-only; enables building `sun6i-isp.o`.

State and persistence: build configuration state only.

Dependencies/integration: matches the driver’s use of media graph, subdevs, vb2 capture/meta queues, fwnode async discovery, regmap, PM runtime, clocks, reset, and DMA.

Risks: hardware currently matches only a subset of supported-family SoCs in code; prompt text mentions A31/A80/A83T/V3/V3s but OF table in this subset only contains `allwinner,sun8i-v3s-isp`.

Test signals: compile under `ARCH_SUNXI` and `COMPILE_TEST`, ensure selected vb2 backends are present, and verify module name/build object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/Makefile -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/Makefile

Purpose: builds the sun6i ISP composite driver object.

Important APIs/types: `sun6i-isp-y` includes core, proc, capture, and params objects; `obj-$(CONFIG_VIDEO_SUN6I_ISP) += sun6i-isp.o`.

Control flow: kbuild links all four implementation files into one module/built-in object.

State and persistence: build graph only.

Dependencies/integration: object list mirrors setup/cleanup calls in `sun6i_isp.c`; removing one object would break symbols.

Risks: no per-feature build toggles; params/capture/proc are always present when the ISP driver is enabled.

Test signals: module and built-in compile checks; symbol resolution for setup/cleanup functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp.c -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp.c

Purpose: core platform driver for the Allwinner sun6i ISP. It manages shared DMA tables, hardware resources, runtime PM, interrupt handling, media/V4L2 device registration, and orchestrates proc/capture/params subcomponents.

Important APIs/functions: `sun6i_isp_load_read/write()` access the DMA load table. `sun6i_isp_state_update()` coordinates capture and params pending state and optionally sets `SUN6I_ISP_FE_CTRL_PARA_READY`; `sun6i_isp_state_complete()` marks state applied after PARAM_LOAD. Table helpers allocate/free coherent load/save/LUT/DRC/stats tables and `sun6i_isp_tables_configure()` writes their DMA addresses. `sun6i_isp_interrupt()` handles FINISH and PARA_LOAD in chronological order. Resource setup maps registers with regmap, gets `mod`/`ram` clocks, sets exclusive module clock rate, gets shared reset, requests IRQ, and enables PM runtime. Probe sets up resources, tables, V4L2/media, proc, capture, and params; remove unwinds them.

Control flow: probe obtains variant table sizes from OF match data, allocates shared device state, initializes state lock, resources, DMA tables, V4L2/media objects, proc subdev, capture video node, and params meta-output node. Streaming is driven by proc/capture code; interrupts call capture finish and state complete/update. Runtime resume deasserts reset and enables clocks; suspend asserts reset and disables clocks.

State and persistence: shared `sun6i_isp_device` persists for device lifetime. Coherent DMA tables persist from probe to remove. The load table is the staging state copied into hardware registers on PARAM_READY/PARA_LOAD; this is the core persistence mechanism across frames.

Dependencies/integration: uses clk, DMA coherent memory, IRQ, OF platform matching, PM runtime, regmap MMIO, reset, V4L2/media controller. Integrates with `sun6i_isp_proc`, `capture`, `params`, and register definitions.

Risks: `sun6i_isp_tables_setup()` lacks cleanup of previously allocated tables on intermediate allocation failure; probe error path calls cleanup only after the function returns failure, but it will free all tables regardless of whether later `data` pointers were initialized. The interrupt handler processes enabled status only after checking `status & enable`; disabled-but-pending statuses are acknowledged in `complete`. State locking is split between global `state_lock` and component locks; lock ordering must remain consistent.

Test signals: probe/remove with allocation failure injection, IRQ ordering with FINISH+PARA_LOAD set, runtime PM cycles, table DMA address register programming, media device registration failure unwinds, and stream tests confirming params apply on the intended next frame.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp.h -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp.h

Purpose: shared sun6i ISP header defining device-wide structures, tables, variant data, and core helper declarations.

Important APIs/types: `enum sun6i_isp_port` identifies CSI0/CSI1 graph ports. `struct sun6i_isp_buffer` wraps vb2 buffers with a list node. `struct sun6i_isp_v4l2` holds V4L2/media devices. `struct sun6i_isp_table/tables` describe coherent DMA tables for load/save/LUT/DRC/stats. `struct sun6i_isp_device` aggregates subcomponents, regmap, clocks, reset, and global state lock. `struct sun6i_isp_variant` provides table sizes. Helper declarations expose load-table access, address conversion, state update, and table register configuration.

Control flow: no implementation; all submodules include this header and share the same `sun6i_isp_device`.

State and persistence: defines device lifetime state and frame-to-frame load-table state. Subcomponent headers are included so the aggregate struct embeds full proc/capture/params state.

Dependencies/integration: depends on V4L2 device and vb2-v4l2 headers plus local capture/params/proc headers.

Risks: circular inclusion pressure is high because this header embeds subcomponent structs and subcomponent headers forward-declare `sun6i_isp_device`. The declaration `sun6i_isp_address_value()` appears while source uses the macro `SUN6I_ISP_ADDR_VALUE`; ensure implementation exists elsewhere or declaration is stale.

Test signals: build coverage, static analysis for include cycles/stale declarations, and runtime validation that embedded subcomponent state is initialized before use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_capture.c -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_capture.c

Purpose: capture video node implementation for the sun6i ISP. It exposes NV12/NV21 capture formats, configures main-channel output registers in the ISP load table, manages capture buffer state across hardware parameter-load cycles, implements vb2 queue operations, and creates the immutable media link from proc output to capture.

Important APIs/functions: `sun6i_isp_capture_dimensions()` and `sun6i_isp_capture_format()` expose active capture format. `sun6i_isp_capture_format_find()` maps V4L2 pixfmt to hardware output format. `sun6i_isp_capture_buffer_configure()` writes Y/U/V DMA addresses for a queued buffer into load registers. `sun6i_isp_capture_configure()` writes size, output format, and stride registers. State helpers move queued buffers to `pending`, then `current`, then `complete`, timestamping and completing buffers when PARAM_LOAD indicates the pending state became active. `sun6i_isp_capture_finish()` increments sequence on frame finish. Queue ops validate size, set payload, enqueue buffers, start/stop pipeline streaming, and cleanup queued/current buffers. Ioctl ops implement capture format and single camera input handling.

Control flow: userspace opens the video node, sets capture format, queues buffers, and streamon starts the media pipeline through the proc subdev. Queued buffers trigger `sun6i_isp_state_update()` if streaming. On PARAM_LOAD, pending becomes current and prior current is completed; on FINISH sequence increments. Stop streaming turns off proc stream, stops pipeline, and completes all outstanding buffers as error.

State and persistence: `sun6i_isp_capture_state` holds queue, pending/current/complete buffer pointers, sequence, and streaming flag. Format persists in `capture.format`; load-table output address/format registers persist until next state update.

Dependencies/integration: uses V4L2 video device/ioctls/events/media controller, vb2 DMA-contig, proc subdev streaming, proc dimensions for link validation, and core state/update helpers.

Risks: buffer cleanup iterates queued list with `list_for_each_entry()` while completing buffers and then reinitializes the list; this relies on completion not modifying the same list entries unexpectedly. Width alignment comment says stride aligns to 4 but implementation aligns pixel width to 2 before multiplying by bytes-per-pixel. No scaling/cropping is supported; capture dimensions must equal proc dimensions. Capture start sets `state->streaming = true` before source stream succeeds and unwinds on error.

Test signals: NV12/NV21 format negotiation and sizeimage, link validation dimension mismatch, buffer state ordering over FINISH/PARA_LOAD interrupts, streamon source failure unwind, qbuf while streaming causing immediate state update, stop streaming with pending/current/queued buffers, and V4L2 compliance for capture ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_capture.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_capture.h -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_capture.h

Purpose: declares capture-side constants, state, structures, and helper/setup APIs for the sun6i ISP video capture node.

Important APIs/types: width/height min/max constants, `struct sun6i_isp_capture_format` maps pixfmt to hardware output format, `struct sun6i_isp_capture_state` tracks queued/pending/current/complete buffers and sequence/streaming state, and `struct sun6i_isp_capture` embeds video device, vb2 queue, mutex, media pad, and format. Public functions expose dimensions/format, format lookup, hardware configure, state update/complete/finish, setup, and cleanup.

Control flow: no implementation; used by core interrupt/state logic, proc configuration, params sequence tagging, and capture implementation.

State and persistence: declares the capture state machine used across frames and load-buffer sync points.

Dependencies/integration: depends on V4L2 device types and shared `sun6i_isp_buffer` from `sun6i_isp.h`. The `#undef current` avoids conflict with the Linux `current` macro for a struct field named `current`.

Risks: the state field name workaround is fragile and signals macro namespace pressure. Any change to state transitions must coordinate with `sun6i_isp.c` interrupt ordering and params sequence handling.

Test signals: build coverage, stream sequencing tests, and static checks for macro conflicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_capture.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_params.c -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_params.c

Purpose: metadata-output parameter node for sun6i ISP configuration. It accepts `V4L2_META_FMT_SUN6I_ISP_PARAMS` buffers, writes module configuration into the ISP load table, manages pending parameter application synchronized to hardware PARAM_LOAD, and creates the immutable media link into the proc subdev params sink.

Important APIs/functions: `sun6i_isp_params_config_default` seeds Bayer and denoise defaults. Configuration helpers write optical black, auto-exposure defaults, Bayer offsets/gains, white balance defaults, BDNF coefficients, and module enable bits into the load table. `sun6i_isp_params_configure()` applies base config every stream start and default module config only once. State helpers queue one pending params buffer, configure modules from `vb2_plane_vaddr()`, mark it pending, and complete it on PARAM_LOAD with sequence `capture.sequence + 1`. Queue ops use vb2 vmalloc memory, prepare payload size, enqueue buffers, start/stop streaming, and trigger state update when capture is also streaming. Ioctl ops expose fixed meta format.

Control flow: userspace queues a params meta buffer; if params and capture are streaming, state update copies its config into the load table and sets PARAM_READY. When hardware emits PARAM_LOAD, the pending buffer is completed as done and tagged for the next frame. Proc stream start also calls `sun6i_isp_params_configure()` to ensure base/default parameters are present before enabling frontend.

State and persistence: `sun6i_isp_params_state` holds queue, pending buffer, `configured` flag, and streaming flag. The load table persists active/pending module register values across frames.

Dependencies/integration: uses V4L2 meta-output ioctls, vb2-vmalloc, media controller, proc media pad, capture sequence, core state lock/update, register macros, and UAPI `sun6i-isp-config.h`.

Risks: user-provided params are read directly from a vmalloc buffer as `struct sun6i_isp_params_config`; validation of module masks and coefficient ranges is minimal in this file. `sun6i_isp_params_configure_bdnf()` reads coefficient indices beyond the two initialized RB defaults and beyond three initialized G defaults; zero-initialization makes defaults safe but userspace can supply all fields. S_FMT/TRY_FMT for meta output simply returns current fixed format, which is intentional but unusual. Default config applies only once per device state, not every stream restart.

Test signals: meta format enumeration, undersized buffer rejection, params queued before/after capture streaming, PARAM_LOAD completion sequence, module enable masks for Bayer/BDNF, invalid user config fuzzing, stop streaming cleanup, and default output without user params.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_params.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_params.h -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_params.h

Purpose: declares params/meta-output structures and APIs for sun6i ISP runtime configuration.

Important APIs/types: `SUN6I_ISP_PARAMS_NAME`, `struct sun6i_isp_params_state` with queue, lock, pending buffer, configured flag, and streaming flag; `struct sun6i_isp_params` with video device, vb2 queue, mutex, media pad, and meta format. Functions declare params configuration, state update/complete, setup, and cleanup.

Control flow: no implementation; core interrupt code calls state completion/update and proc stream start calls configuration.

State and persistence: declares the state machine for parameter buffers and the `configured` flag that persists default module setup decisions.

Dependencies/integration: depends on V4L2 device types and shared sun6i ISP device/buffer definitions via include order.

Risks: queue comment is attached to `queue` while the spinlock is the actual lock; minor documentation ambiguity. Parameter state sequencing must stay aligned with capture sequence semantics.

Test signals: build coverage and params streaming/sequence tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_params.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_proc.c -->
# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_proc.c

Purpose: ISP processor V4L2 subdev implementation. It models the ISP processing block in the media graph, discovers CSI sources asynchronously, validates/sets raw Bayer media-bus formats, configures frontend input and module registers, controls streaming and runtime PM, and creates links from external CSI sources to proc.

Important APIs/functions: `sun6i_isp_proc_dimensions()` exposes active mbus dimensions. `sun6i_isp_proc_format_find()` maps 8-bit/10-bit Bayer mbus codes to hardware input format. IRQ helpers enable/disable/clear frontend interrupts. `sun6i_isp_proc_enable/disable()` toggles frontend source mode and capture enable. `sun6i_isp_proc_configure()` enables source module and writes input format/mode bits into the load table. `sun6i_isp_proc_s_stream()` resolves the connected CSI source, handles off/on streaming, runtime PM, table/params/proc/capture configuration, initial state update with ready hold, IRQ enable, frontend enable, and upstream source streaming. Subdev pad ops enumerate/get/set mbus format. Async notifier callbacks bind CSI0/CSI1 sources and create media links, enabling CSI0 by preference and CSI1 if CSI0 absent. `sun6i_isp_proc_setup()` registers the subdev, pads, notifier, and sources; cleanup unregisters them.

Control flow: setup registers a three-pad subdev: CSI sink, params sink, capture source. During streamon from capture, proc identifies the single remote CSI source, resumes PM, clears IRQs, configures DMA tables and load-table parameters, stages initial capture/params state without immediately setting ready, enables IRQ/frontend, and starts upstream CSI. Streamoff disables IRQ, stops upstream, disables frontend, and drops runtime PM.

State and persistence: `proc.mbus_format` persists active raw input format and dimensions. `source_csi0/source_csi1` remember expected/bound async sources. Load-table module/input configuration persists until next configure.

Dependencies/integration: depends on PM runtime, regmap, V4L2 fwnode async notifier, media graph pads/links, capture/params/core configuration helpers, and register macros.

Risks: `sun6i_isp_proc_irq_clear()` writes zero to interrupt enable then clears status; streamon re-enables later, but naming may obscure side effects. If upstream source `s_stream(1)` fails after frontend enable, code disables frontend and PM but does not explicitly clear pending state staged earlier. Format set does not clamp width/height here; init defaults are 1280x720 but user-provided dimensions rely on subdev framework/capture link validation. Source selection assumes any non-CSI0 bound source is CSI1 after earlier endpoint parsing.

Test signals: async binding for CSI0 only, CSI1 only, both sources; media link creation/enabled defaults; mbus code enum/get/set for 8/10-bit Bayer; capture dimension mismatch validation; streamon failure from upstream CSI; runtime PM balance; IRQ register enable/clear traces; and full pipeline streaming with params/capture nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_proc.c -->

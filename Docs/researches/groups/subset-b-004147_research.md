# subset-b-004147 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-m2m.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-m2m.c

Purpose: Implements the i.MX8 ISI V4L2 memory-to-memory device, exposing a `/dev/video*` M2M node that reads one queued source buffer from memory, programs an ISI channel, writes a destination buffer, and completes the pair through the V4L2 mem2mem scheduler.

Important APIs/types/functions: The private context is `struct mxc_isi_m2m_ctx`, with per-queue `format/info/sequence` state and control state for alpha/hflip/vflip. `mxc_isi_m2m_device_run()` programs channel input/output format and DMA addresses. `mxc_isi_m2m_frame_write_done()` completes src/dst buffers and finishes the job. VB2 queue operations share `mxc_isi_video_queue_setup()`, `mxc_isi_video_buffer_init()`, and `mxc_isi_video_buffer_prepare()` from the capture driver. Registration is through `mxc_isi_m2m_register()` and teardown through `mxc_isi_m2m_unregister()`.

Control flow/state: Open allocates a context, initializes two VB2 queues through `v4l2_m2m_ctx_init()`, seeds default output/capture formats, and creates controls. Streaming preparation runtime-resumes the device, acquires pipe 0 on first use, gets the channel clock/resource reference, and optionally chains a neighbor channel when input width exceeds `MXC_ISI_MAX_WIDTH_UNCHAINED`. Each job disables the channel, reconfigures only when `m2m->last_ctx` changes, applies controls under the control handler lock, loads source and destination DMA addresses into ISI input and both ping-pong output slots, enables the channel, and starts memory read. Stop/unprepare drains queued buffers as errors, decrements usage and chained counts, releases the channel at last user, and runtime-suspends.

Dependencies/integration: Integrates with V4L2 mem2mem, VB2 DMA-contig, media controller graph, runtime PM, ISI pipe/channel helpers, crossbar topology, and common ISI format tables. It manually adds media entities/interfaces so the M2M source entity links into the existing ISI crossbar and capture entity.

Risks/test signals: Main risks are shared pipe serialization across multiple M2M contexts, incorrect `usage_count/chained_count` unwinding on stream setup failures, stale `last_ctx` after suspend/resume, and format propagation quirks where setting OUTPUT also updates CAPTURE. Test with multi-context streamon/streamoff, width crossing the chained threshold, format conversion vs bypass, alpha/flip controls during queued jobs, runtime/system suspend while streaming, and media graph validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-m2m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-pipe.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-pipe.c

Purpose: Implements the V4L2 subdevice for each i.MX8 ISI processing pipe, including media bus format enumeration, pad format/crop/compose state, channel acquire/release, stream enable/disable, and IRQ dispatch to capture or M2M users.

Important APIs/types/functions: `mxc_isi_bus_formats[]` maps supported sink/source media bus codes to ISI encodings. `mxc_isi_bus_format_by_code()` and `_by_index()` export lookup helpers. `mxc_isi_pipe_enable()` discovers the active crossbar route and programs the channel. Pad ops are `mxc_isi_pipe_enum_mbus_code()`, `mxc_isi_pipe_set_fmt()`, `mxc_isi_pipe_get_selection()`, and `mxc_isi_pipe_set_selection()`. `mxc_isi_pipe_irq_handler()` reads/clears channel IRQ status and calls the installed `pipe->irq_handler` on frame-start/frame-done status.

Control flow/state: Each pipe owns active V4L2 subdev state for sink/source formats plus sink compose and source crop rectangles. Initialization sets defaults, pads, media entity function, register base, available resources, and a per-pipe IRQ. Enabling locks the crossbar active state to find the connected input, locks pipe state to derive sink/source encoding, input size, scale, and crop, calls `mxc_isi_channel_config()`, enables the hardware channel, then enables the matching crossbar stream. Disabling reverses that order. Acquire computes bypass from active formats and chains the channel for wide sink formats.

Dependencies/integration: Depends on `imx8-isi-core.h`, `imx8-isi-regs.h`, the crossbar subdevice, V4L2 subdev active state helpers, media controller link validation, platform IRQ resources, and low-level channel helpers in `imx8-isi-hw.c`.

Risks/test signals: Format conversion only permits RGB/YUV source codes while RAW must remain identical, so invalid propagation can break link validation. Width clamping differs for last vs chain-capable pipes. IRQ status errors are logged but do not directly fail buffers. Test sink/source code enumeration, crop/compose clamping, crossbar route absence returning `-EPIPE`, chained vs unchained maximum width, stream enable rollback, and IRQ completion under overflow/AXI error status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-pipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-regs.h -->
## sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-regs.h

Purpose: Defines the i.MX8 ISI channel register offsets and bitfield macros used by the hardware access layer, video capture path, M2M path, and pipe IRQ handling.

Important APIs/types/functions: This header has no functions; its API is the register contract. Key groups include `CHNL_CTRL` enable/clock/bypass/chain/source fields, `CHNL_IMG_CTRL` output format, alpha, flip, CSC, crop and decimation fields, `CHNL_OUT_BUF_CTRL` load and overflow threshold fields, `CHNL_IER` and `CHNL_STS` interrupt/status bits, scale/crop/CSC coefficient registers, ROI alpha/geometry registers, output/input buffer address and extended address registers, pitch registers, memory-read control fields, and flow-control registers.

Control flow/state: Driver state is persisted in hardware registers addressed by these macros. The capture and M2M paths program image format, input/output DMA addresses, pitch, crop, scale, alpha and flip through helper functions. The pipe IRQ path reads `CHNL_STS` and uses the active-buffer bits to synchronize software queues with hardware ping-pong buffers.

Dependencies/integration: Uses Linux `BIT()` and `GENMASK()` macros. The semantic mapping is consumed by `imx8-isi-hw.c`, `imx8-isi-video.c`, `imx8-isi-m2m.c`, and platform data that describes SoC-specific interrupt masks and panic thresholds.

Risks/test signals: Register macro mistakes are high impact because they silently corrupt hardware configuration. Pay special attention to overlapping fields, extended DMA address handling, active-buffer bit interpretation, and format constants matching `mxc_isi_format_info`. Test by comparing register traces for known capture/M2M formats, validating >32-bit DMA address paths if supported, and checking interrupt/overflow status decoding on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-video.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-video.c

Purpose: Implements the i.MX8 ISI capture video node, including pixel format tables, VB2 queueing, DMA buffer plane setup, ping-pong hardware buffer management, V4L2 ioctls, controls, streaming, suspend/resume, and video-device registration.

Important APIs/types/functions: `mxc_isi_formats[]` maps V4L2 fourccs to media bus codes, ISI input/output format fields, plane counts, depth, subsampling, and encoding. Public helpers include `mxc_isi_format_by_fourcc()`, `mxc_isi_format_enum()`, `mxc_isi_format_try()`, `mxc_isi_video_queue_setup()`, `mxc_isi_video_buffer_init()`, and `mxc_isi_video_buffer_prepare()`. Streaming pivots around `mxc_isi_vb2_prepare_streaming()`, `mxc_isi_vb2_start_streaming()`, `mxc_isi_video_frame_write_done()`, and `mxc_isi_vb2_stop_streaming()`.

Control flow/state: `mxc_isi_video_register()` initializes the capture `video_device`, VB2 DMA-contig queue, media pad, default format, buffer lists, and alpha/flip controls. Format setting is blocked while the queue is busy and must match the pipe source mbus code/size at stream preparation. Streaming starts a media pipeline, acquires the pipe, allocates coherent discard buffers, initializes hardware output format and controls, primes BUF1/BUF2 from pending or discard lists, enables the pipe, and then advances buffers in IRQ context. The IRQ completion path tracks active, pending, and discard lists under `buf_lock`, handles ISI active-buffer bit polarity, detects missed/racing frame interrupts, completes real buffers with sequence/timestamp, and recycles discard buffers.

Dependencies/integration: Depends on VB2 DMA-contig, V4L2 controls/ioctls, media controller pipelines, runtime PM through file open/release, ISI pipe/channel helpers, and register status bits from `imx8-isi-regs.h`.

Risks/test signals: The most sensitive logic is ping-pong buffer synchronization: lost frame IRQs, races while loading a new output address, and no-user-buffer discard fallback. Other risks are single-planar multi-color-plane DMA address derivation, format mismatch against subdev state, and resume rebuilding active buffers in order. Test continuous capture with one, two, and many queued buffers; underrun/discard behavior; RAW/YUV/RGB plane sizing; frame sequence monotonicity; streamoff returning all buffers; and system suspend/resume during active capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8mq-mipi-csi2.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8mq-mipi-csi2.c

Purpose: Provides the NXP i.MX8MQ/i.MX8QXP/i.MX8ULP MIPI CSI-2 receiver bridge as a two-pad V4L2 subdevice that passes sensor media-bus formats to downstream capture hardware while configuring CSI-2 receiver registers, PHY/GPR controls, clocks, resets, PM, and async sensor binding.

Important APIs/types/functions: `struct csi_state` stores device resources, subdev/notifier, bus lane config, state bits, GPR/regmap data, and interconnect state. Platform variants use `imx8mq_gpr_enable()` or `imx8qxp_gpr_enable()/disable()`. Core flow uses `imx8mq_mipi_csi_set_params()`, `imx8mq_mipi_csi_calc_hs_settle()`, `imx8mq_mipi_csi_start_stream()`, `imx8mq_mipi_csi_s_stream()`, pad format ops, async notifier registration, and runtime/system PM callbacks.

Control flow/state: Probe parses DT resets, MMIO, clocks, optional CSR/syscon GPR, endpoint lane order, and optional ICC path, then registers a bridge subdevice and async notifier. Pad state defaults to 640x480 SGBRG10 and source always mirrors sink because no transcoding is supported. On stream enable runtime PM powers clocks/interconnect, software-reset is asserted/deasserted, receiver lane and payload parameters are programmed, HS-settle is calculated from remote link frequency and escape clock, platform PHY/GPR is enabled, then upstream sensor streaming is started. Disable stops the upstream first, disables data lanes, and calls variant disable if present.

Dependencies/integration: Integrates with fwnode graph parsing, V4L2 async notifier, media entity link validation, reset framework, clk bulk APIs, regmap/syscon or CSR MMIO, runtime PM, interconnect bandwidth voting, and upstream sensor link-frequency controls.

Risks/test signals: Risks include unsupported lane reordering, bad link-frequency causing invalid HS-settle, PM state bit races (`ST_POWERED`, `ST_STREAMING`, `ST_SUSPENDED`), cleanup ordering after async registration failures, and variant-specific GPR differences. Test endpoint parsing, all supported mbus codes, stream enable/disable around sensor failures, runtime suspend/resume, system suspend while streaming, ICC vote errors, and lane-rate boundary handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8mq-mipi-csi2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/mx2_emmaprp.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/nxp/mx2_emmaprp.c

Purpose: Implements a legacy V4L2 mem2mem driver for the i.MX2 eMMa-PrP processor, converting/scaling memory input buffers into memory output buffers, specifically from YUYV output queue input to YUV420 capture queue output.

Important APIs/types/functions: Main types are `struct emmaprp_dev`, `struct emmaprp_ctx`, and `struct emmaprp_q_data`. `emmaprp_device_run()` writes source/destination DMA addresses, frame sizes, IRQ enables, and control bits. `emmaprp_irq()` clears interrupt status, handles bus errors, completes buffers, and finishes the M2M job. `vidioc_try_fmt*`, `vidioc_s_fmt*`, `emmaprp_queue_setup()`, `emmaprp_buf_prepare()`, and `queue_init()` implement the V4L2/VB2 surface.

Control flow/state: Probe registers a V4L2 device, allocates a video device, maps PrP registers, gets clocks, requests IRQ, initializes V4L2 M2M, and registers a fixed M2M node. Open creates a context, initializes M2M queues, enables IPG/AHB clocks, and seeds output/capture formats. Each job reads next src/dst buffers, programs source Y and destination Y/Cb/Cr addresses for planar YUV420, enables read/write/complete interrupts, and starts channel 2. IRQ completion copies timestamp metadata and marks both buffers done unless aborting or bus error; abort sets a flag and finishes the job. Release disables clocks and releases context state.

Dependencies/integration: Uses V4L2 mem2mem, VB2 DMA-contig, platform IRQ/MMIO/clock resources, and single-planar V4L2 formats. It does not use media-controller graph plumbing or runtime PM.

Risks/test signals: The driver supports only two formats and simple size calculations; bytesperline for YUV420 is unusual (`width * 3 / 2`) because it represents packed total line sizing for a single plane. Risks include clock reference imbalance with multiple open contexts, early return from `device_run()` on missing DMA addresses without job finish, bus-error recovery via software reset while queues are active, and memory limit reducing requested buffers to zero if dimensions are too large. Test format validation, min/max/alignment clamping, concurrent opens, DMABUF/MMAP/USERPTR paths, IRQ error paths, abort, and module remove while idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/mx2_emmaprp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/Kconfig

Purpose: Top-level Qualcomm media platform Kconfig menu that groups Qualcomm media drivers and sources submenus for CAMSS, Iris, and Venus.

Important APIs/types/functions: This declarative file creates the `"Qualcomm media platform drivers"` comment and includes `drivers/media/platform/qcom/camss/Kconfig`, `iris/Kconfig`, and `venus/Kconfig`.

Control flow/state: No runtime state. Build configuration state flows from this file into child Kconfig files, making their options visible under the Qualcomm media platform area.

Dependencies/integration: Integrated by the kernel media platform Kconfig hierarchy. It is paired with the top-level Qualcomm Makefile that descends into the same subdirectories.

Risks/test signals: Risks are limited to missing or stale submenu source lines, which would hide drivers from configuration. Test with `make menuconfig` or `scripts/kconfig/conf` to ensure CAMSS/Iris/Venus options remain reachable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/Makefile -->
## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/Makefile

Purpose: Top-level Qualcomm media platform build file that recurses into the CAMSS, Iris, and Venus driver directories.

Important APIs/types/functions: Uses `obj-y += camss/`, `iris/`, and `venus/` so child Makefiles control object selection based on Kconfig symbols.

Control flow/state: No runtime state. Build inclusion is unconditional at directory traversal level; actual module/built-in choices are made in child Makefiles.

Dependencies/integration: Consumed by Kbuild from `drivers/media/platform`. Must stay synchronized with the sibling Kconfig source entries.

Risks/test signals: Missing entries prevent entire driver families from building even when Kconfig enables them. Test with allmodconfig or targeted `CONFIG_VIDEO_QCOM_CAMSS=m` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/Kconfig

Purpose: Defines the `VIDEO_QCOM_CAMSS` tristate option for the Qualcomm V4L2 Camera Subsystem driver.

Important APIs/types/functions: The option depends on `V4L_PLATFORM_DRIVERS`, `VIDEO_DEV`, and either `ARCH_QCOM && IOMMU_DMA` or `COMPILE_TEST`. It selects media-controller, V4L2 subdev API, `VIDEOBUF2_DMA_SG`, and `V4L2_FWNODE`.

Control flow/state: No runtime state; it controls whether the `qcom-camss` aggregate object is built and ensures framework dependencies are selected.

Dependencies/integration: Paired with `camss/Makefile`, which builds many CSID/CSIPHY/VFE/video objects into `qcom-camss.o`.

Risks/test signals: Dependency mistakes can either hide CAMSS on valid Qualcomm platforms or allow invalid builds without DMA/IOMMU support. Test compile with ARCH_QCOM, COMPILE_TEST, module and built-in configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/Makefile -->
## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/Makefile

Purpose: Defines the object list for the Qualcomm CAMSS aggregate driver and binds it to `CONFIG_VIDEO_QCOM_CAMSS`.

Important APIs/types/functions: `qcom-camss-objs` includes core `camss.o`, CSID common and generation files, CSIPHY variants, ISPIF, VFE variants, VBIF, video node support, and format support. `obj-$(CONFIG_VIDEO_QCOM_CAMSS) += qcom-camss.o` produces the module or built-in object.

Control flow/state: No runtime state. Object inclusion is static for the aggregate driver, so all SoC variant implementations are linked when CAMSS is enabled.

Dependencies/integration: Tightly coupled to declarations in headers such as `camss-csid.h`, `camss-csiphy.h`, and VFE ops headers; missing objects cause unresolved ops symbols for supported SoCs.

Risks/test signals: The common risk is adding a new SoC ops file but forgetting the Makefile. Test with `CONFIG_VIDEO_QCOM_CAMSS=m`, allmodconfig, and link checks for all exported `*_ops_*` symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-340.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-340.c

Purpose: Implements CSID hardware operations for the Qualcomm 340-generation CSI decoder, focused on RDI raw dump paths without CSID test-generator support.

Important APIs/types/functions: Provides `csid_ops_340`. Helpers configure RX lane/PHY selection, RDI stream format, RDI halt/resume, reset, and IRQ handling. It uses Gen2 decode definitions and common helpers `csid_get_fmt_entry()`, `csid_hw_version()`, and `csid_src_pad_code()`.

Control flow/state: `csid_configure_stream()` programs CSI2 RX registers and loops over enabled virtual channels in `csid->phy.en_vc`, configuring one RDI per VC. RDI config uses data type, VC, and derived `dt_id`, sets decode format to NOP/raw dump, then enables the RDI if requested. Reset masks/clears reset-done IRQ, strobe-resets IRQ/IFE/PHY/CSID clocks while preserving registers, waits on `reset_complete`, and ISR completes that completion on reset IRQ.

Dependencies/integration: Plugged into the common CSID core via `struct csid_hw_ops`; depends on CAMSS media-link setup to fill `csid->phy`, and on VFE/IFE downstream blocks for actual buffer handling.

Risks/test signals: No testgen means sensor path must be linked. Verify reset completion, lane assignment/PHY base index, multi-VC RDI mapping, stream disable clearing RDI enable, and unsupported test pattern returning `-EOPNOTSUPP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-340.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-4-1.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-4-1.c

Purpose: Implements CSID hardware operations for older 4.1-generation Qualcomm CAMSS blocks, including sensor RX configuration, CID LUT programming, RDI/ISPIF enablement, and an internal test generator.

Important APIs/types/functions: Exports `csid_ops_4_1`. `csid_configure_stream()` handles both testgen and real sensor paths. `csid_configure_testgen_pattern()` stores the selected payload mode. `csid_isr()` handles reset completion from IRQ status bit 11. `csid_reset()` issues reset and waits for `reset_complete`. `csid_subdev_init()` enables Gen1 test pattern modes.

Control flow/state: On enable, if testgen is active the source format drives bytes-per-line, line count, data type, and payload mode registers; otherwise sink format and `csid->phy` program core lane and PHY controls. Both paths populate VC0/CID0 LUT and CID config with ISPIF and RDI enabled and raw-dump mode, then enable TG if applicable. Disable only turns off TG when active.

Dependencies/integration: Used by common `camss-csid.c` power, format, control, and media-link code. Uses Gen1 decode constants and `csid_testgen_modes`.

Risks/test signals: It assumes VC0/CID0 only and lacks multi-source-pad RDI handling. Test reset timeout, test-pattern exclusive use vs linked CSIPHY, format byte-count calculations, sensor streaming with lane assignment, and source format propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-4-1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-4-7.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-4-7.c

Purpose: Implements CSID operations for the 4.7-generation block, similar to 4.1 but with updated register offsets and optional packed 10-bit output conversion for selected source-pad formats.

Important APIs/types/functions: Exports `csid_ops_4_7`. Uses `csid_configure_stream()`, `csid_configure_testgen_pattern()`, `csid_isr()`, `csid_reset()`, and `csid_subdev_init()`.

Control flow/state: Enable configures testgen or sensor RX, writes CID LUT and CID config, and starts TG if enabled. It checks sink/source codes for SBGGR10 or Y10 converted to `*_2X8_PADHI_LE`; in that case it sets RDI plain-packing mode, plain16 format, and LSB alignment. Reset and ISR mirror the Gen1 completion model with 4.7 offsets.

Dependencies/integration: Common CSID code supplies active formats, test pattern control, media-link lane data, and power sequencing. VFE/ISPIF downstream consumes the configured RDI/ISPIF path.

Risks/test signals: Key risks are packed-format matching and source-code negotiation in `csid_src_pad_code()`. Test raw10 unpacked vs packed paths, testgen operation, VC0 assumptions, reset IRQ completion, and link validation with 4.7 format tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-4-7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-680.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-680.c

Purpose: Implements CSID operations for Titan 680-style hardware with top wrapper routing, per-RDI register update tracking, buffer-done IRQ handling, and VFE notification.

Important APIs/types/functions: Exports `csid_ops_680`. Major helpers include `csid_reg_update()`, `csid_reg_update_clear()`, `__csid_configure_top()`, `__csid_configure_rx()`, `__csid_configure_rdi_stream()`, `csid_reset()`, `csid_isr()`, and `csid_subdev_reg_update()`.

Control flow/state: Stream configuration writes wrapper path routing, then for each enabled VC configures RDI data type, VC, DT_ID, payload-only decode, timestamp/byte-count/drop/crop/packing flags, IRQ subsampling, and RDI halt/resume. `csid->reg_update` stores outstanding RUP/AUP bits and is written to `CSID_REG_UPDATE_CMD`; RUP-done IRQs clear bits. Reset preserves registers, enables per-RDI RUP done, clears/enables buf-done IRQs, unmasks top IRQs, and waits for reset completion. ISR clears top, RX, buf-done, and per-RDI statuses, clears reg-update bits on RUP done, and calls `camss_buf_done()` for matching RDI buffer-done bits.

Dependencies/integration: Requires common CAMSS `csid_wrapper_base`, VFE parent ops, common CSID link setup, and VFE buffer completion path.

Risks/test signals: Risks include wrapper routing mistakes, RDI offset differences for lite vs full blocks, reg-update bit leaks, and false buf-done port mapping. Test all enabled VC masks, lite/full variants, stream disable, VFE buffer completion, reset with IRQ masks, and reg-update clear/set through `camss_reg_update()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-680.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-gen1.h -->
## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-gen1.h

Purpose: Defines CSID generation-1 decode and plain-format constants used by 4.1 and 4.7 hardware operation files.

Important APIs/types/functions: Provides `DECODE_FORMAT_*` constants for uncompressed and DPCM RAW encodings and `PLAIN_FORMAT_PLAIN8/PLAIN16`.

Control flow/state: No runtime state. Constants are compiled into CID configuration writes for legacy CSID hardware.

Dependencies/integration: Included by `camss-csid-4-1.c`, `camss-csid-4-7.c`, and common format tables in `camss-csid.c`.

Risks/test signals: Incorrect numeric constants cause hardware to decode CSI-2 payloads incorrectly. Test with RAW8/10/12/14 and YUV capture on Gen1 platforms, plus packed RAW10 source-code paths on 4.7.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-gen1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-gen2.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-gen2.c

Purpose: Implements generic Gen2 CSID operations, including RX/RDI configuration, test pattern generation, IRQ handling, and reset for blocks with lite/full register-layout differences.

Important APIs/types/functions: Exports `csid_ops_gen2`. Helpers configure RX, RDI halt/resume, TPG registers, RDI stream registers, test pattern mode, ISR, and reset. It uses `csid_is_lite()` to choose register offsets.

Control flow/state: Streaming loops over `csid->phy.en_vc`. For each VC it optionally configures TPG, configures RDI payload-only decode with data type/VC/DT_ID, timestamp/measure/byte-counter flags, frame/IRQ/pixel/line drop periods, then configures RX and resumes or halts RDI. Reset clears/masks top reset IRQ, strobes reset while preserving registers, and waits for reset completion. ISR clears top, CSI2 RX, and enabled RDI statuses, then clears IRQ command and completes reset when seen.

Dependencies/integration: Common CSID core supplies format/control/link state and power sequencing; Gen2 constants come from `camss-csid-gen2.h`.

Risks/test signals: Risks are offset divergence for lite blocks, defaulting lane count to four when unset, and testgen configuration matching enabled virtual channels. Test lite/full SoCs, multi-VC masks, TPG modes, reset timeout, and CSI error IRQ clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-gen2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-gen2.h -->
## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-gen2.h

Purpose: Defines Gen2 CSID decode, encode, and plain-format constants used by Gen2, 340, and 680 CSID operation files.

Important APIs/types/functions: Includes uncompressed 6/8/10/12/14/16/20-bit decode constants, DPCM decode constants, user-defined and payload-only constants, RAW encode constants for TPG, and `PLAIN_FORMAT_PLAIN8/16/32`.

Control flow/state: No runtime state. Values are written into RDI and TPG configuration bitfields.

Dependencies/integration: Included by `camss-csid-gen2.c`, `camss-csid-340.c`, `camss-csid-680.c`, and format metadata in `camss-csid.c`.

Risks/test signals: Constant drift breaks data interpretation across SoCs. Test with RAW/YUV formats and TPG encode modes on Gen2-derived hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-gen2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-gen3.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-gen3.c

Purpose: Implements Titan Gen3 CSID operations, including wrapper routing, RDI configuration, RUP/AUP register updates, buffer-done forwarding to VFE, reset, and IRQ handling for newer Qualcomm CAMSS SoCs.

Important APIs/types/functions: Exports `csid_ops_gen3`. Helpers include `__csid_configure_wrapper()`, `__csid_configure_rx()`, `__csid_configure_rdi_stream()`, `__csid_ctrl_rdi()`, `csid_subdev_reg_update()`, `csid_isr()`, and `csid_reset()`. Register macros handle lite vs full and CSID 690 offset differences.

Control flow/state: Stream enable configures the wrapper for full CSIDs, then each enabled VC gets RDI payload-only decode, timestamp, pixel store, crop/drop, MIPI packing, IRQ subsampling, RX lane/PHY settings, and RDI start command. `csid->reg_update` tracks RUP/AUP bits written to `CSID_RUP_AUP_CMD`; RUP done IRQ clears bits. Reset enables top and per-enabled-RDI buf-done IRQ masks, sets reset mode/location, issues HW+IRQ reset, and waits for completion. ISR clears top/RX/buf-done/per-RDI statuses, forwards buf-done to `camss_buf_done()`, clears IRQ command, and completes reset.

Dependencies/integration: Depends on common CSID entity/link/power code, CAMSS resource version checks (`CAMSS_8775P`, `CAMSS_8300`), VFE downstream buffer handling, and `camss-csid-gen3.h`.

Risks/test signals: Risks include incorrect buf-done RDI offset per SoC/lite variant, no real testgen support despite a no-op configure hook, and reg-update command bits not being written on clear. Test supported Gen3 SoCs, lite/full paths, multi-VC buf-done, RUP/AUP update flow, reset timeout, and stream disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-gen3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-gen3.h -->
## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-gen3.h

Purpose: Defines decode and plain-format constants for Titan Gen3 CSID hardware.

Important APIs/types/functions: Provides `DECODE_FORMAT_UNCOMPRESSED_8/10/12/14/16/20/24_BIT`, `DECODE_FORMAT_PAYLOAD_ONLY`, and plain-format constants.

Control flow/state: No runtime state. Gen3 stream programming uses these values in RDI decode-format fields.

Dependencies/integration: Included by `camss-csid-gen3.c`; values must match hardware documentation and common CSID format tables.

Risks/test signals: Wrong constants produce corrupted frame payload interpretation. Test RAW8 through RAW24-capable paths and payload-only RDI streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid-gen3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid.c

Purpose: Common Qualcomm CAMSS CSID core: owns format tables, V4L2 subdevice operations, power/clock/reset sequencing, media-link setup, test-pattern control, resource initialization, and entity registration. Generation-specific files plug in through `struct csid_hw_ops`.

Important APIs/types/functions: Exports `csid_formats_4_1`, `csid_formats_4_7`, `csid_formats_gen2`, `csid_find_code()`, `csid_get_fmt_entry()`, `csid_hw_version()`, `csid_src_pad_code()`, `msm_csid_subdev_init()`, `msm_csid_register_entity()`, `msm_csid_unregister_entity()`, `msm_csid_get_csid_id()`, and `csid_is_lite()`. Internal key functions include `csid_set_clock_rates()`, `csid_set_power()`, `csid_set_stream()`, pad format ops, `csid_set_test_pattern()`, and `csid_link_setup()`.

Control flow/state: Init binds resources, maps MMIO or VFE-embedded CSID offsets, requests IRQ with `IRQF_NO_AUTOEN`, builds clock/regulator arrays, initializes completion, and calls hardware `subdev_init()`. Registration creates the CSID subdev with one sink and four source pads, optional test-pattern menu, default UYVY 1920x1080 formats, and media ops. Link setup captures CSIPHY id/lane count/lane assignment on sink links, prevents conflicting testgen/sensor use, tracks enabled source pads as `phy.en_vc`, and marks VC update needed. Power-on gets the parent VFE/IFE, runtime-resumes, enables regulators/clocks, enables IRQ, resets hardware, and reads version. Stream-on syncs controls, requires a sink link unless using testgen, and calls hardware `configure_stream()` only when VC state changed.

Dependencies/integration: Integrates V4L2 subdev, media controller, PM runtime, regulators, clocks, CAMSS parent device ops, CSIPHY lane config, VFE buffer/update callbacks, MIPI CSI-2 data types, and all generation-specific ops.

Risks/test signals: `csid_set_power()` has multiple error exits where parent-device reference unwinding is sensitive. `csid_set_stream()` configures only when `need_vc_update` is true, so format/control changes must correctly set that state elsewhere. Format defaults and packed RAW10 source-code selection affect downstream VFE. Test link setup conflicts, multi-source-pad VC masks, testgen exclusive mode, power failure unwind, clock-rate selection from link frequency, VFE-embedded CSID mapping on CAMSS_8250, and subdev format propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid.h -->
## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid.h

Purpose: Public internal header for the Qualcomm CAMSS CSID module, defining pad layout, testgen modes, format metadata, PHY config, hardware operation callbacks, CSID resource descriptors, and common function prototypes.

Important APIs/types/functions: Defines `MSM_CSID_PAD_SINK`, `MSM_CSID_PAD_FIRST_SRC`, `MSM_CSID_PADS_NUM`, `MSM_CSID_MAX_SRC_STREAMS`, `CSID_RESET_TIMEOUT_MS`, `enum csid_testgen_mode`, `struct csid_format_info`, `struct csid_formats`, `struct csid_testgen_config`, `struct csid_phy_config`, `struct csid_hw_ops`, `struct csid_subdev_resources`, and `struct csid_device`. Declares common helpers and external ops for 4.1, 4.7, 340, 680, Gen2, and Gen3.

Control flow/state: The central persistent state is `struct csid_device`: CAMSS pointer, id, subdev/pads, MMIO base, IRQ, clocks/regulators, reset completion, testgen control state, PHY lane/VC state, per-pad formats, controls, and hardware resource pointer. `struct csid_hw_ops` is the polymorphic dispatch table used by the common core for stream config, reset, ISR, version read, source-code negotiation, subdev init, and optional register updates.

Dependencies/integration: Includes Linux clock/interrupt and media/V4L2 subdev/control headers. It is included by common and generation-specific CAMSS CSID files and by `camss.h`.

Risks/test signals: Header changes affect every CSID generation. Risks include callback contract mismatches, pad-count assumptions, and VC/source-pad indexing errors. Test by compiling all CAMSS variants and running media graph link/stream paths for single and multiple RDI source pads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csiphy-2ph-1-0.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csiphy-2ph-1-0.c

Purpose: Implements hardware operations for Qualcomm CAMSS two-phase CSIPHY v1.0, handling lane masks, reset, settle-count calculation, lane enable/disable, hardware-version logging, and IRQ clearing.

Important APIs/types/functions: Exports `csiphy_ops_2ph_1_0`. Key helpers are `csiphy_get_lane_mask()`, `csiphy_hw_version_read()`, `csiphy_reset()`, `csiphy_settle_cnt_calc()`, `csiphy_lanes_enable()`, `csiphy_lanes_disable()`, `csiphy_isr()`, and `csiphy_init()`.

Control flow/state: Lane mask always includes the clock lane and each configured data lane. Enabling computes settle count from link frequency and timer clock, programs init/wakeup timing, powers the selected lane mask, writes combo mode reset state, then configures every data lane plus the clock lane with CFG2, settle count, interrupt mask, and clear bits. Disabling zeros lane CFG2 registers and global power config. ISR loops over eight lane interrupt status registers, clears each, toggles global IRQ command, and clears again.

Dependencies/integration: Depends on common `camss-csiphy.h` types and higher-level CSIPHY core code for resource management, link frequency, timer clock rate, lane configuration, and ops dispatch.

Risks/test signals: If link frequency is missing, settle count becomes zero; that may work only for tolerant PHY/sensor combinations. Lane-position mistakes break CSI input before CSID sees data. Test lane masks for 1/2/4-lane sensors, link-frequency variations, interrupt storms, reset timing, and disable/re-enable cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csiphy-2ph-1-0.c -->

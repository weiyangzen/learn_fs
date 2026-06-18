# subset-b-004156 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar_fdp1.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar_fdp1.c

Purpose: implements the Renesas R-Car FDP1 V4L2 memory-to-memory deinterlacer and format converter. It exposes one multiplanar M2M video node, accepts YUV source buffers, can output YUV or selected RGB formats, and programs FDP1 read/write pixel formatters plus IPC deinterlacing tables.

Important APIs, types, and functions: `struct fdp1_dev` owns the V4L2 device, video node, mem2mem device, MMIO registers, FCP handle, job pools, and IRQ locks. `struct fdp1_ctx` is per-open state with controls, source/capture queue formats, deinterlace mode, sequence counters, field queues, optional adaptive shared mask DMA memory, and previous-field tracking. `struct fdp1_fmt`, `struct fdp1_q_data`, `struct fdp1_field_buffer`, `struct fdp1_buffer`, and `struct fdp1_job` model hardware formats, vb2 buffers split into fields, and hardware jobs. The main operations are `fdp1_open()`, `fdp1_release()`, `fdp1_try_fmt_*()`, `fdp1_set_format()`, `fdp1_buf_prepare()`, `fdp1_start_streaming()`, `fdp1_m2m_device_run()`, `fdp1_prepare_job()`, `fdp1_device_process()`, `fdp1_irq_handler()`, and `device_frame_end()`.

Control flow: probe maps registers, requests IRQ, gets optional `renesas,fcp`, registers `v4l2_device`, initializes `v4l2_m2m`, registers the video node, powers the device once to read the IP version, then idles under runtime PM. Open creates a context, initializes controls (`V4L2_CID_DEINTERLACING_MODE`, `V4L2_CID_MIN_BUFFERS_FOR_CAPTURE`, `V4L2_CID_ALPHA_COMPONENT`), applies default formats, creates vb2 M2M queues, and runtime-resumes hardware. Streaming validates field layout, allocates the adaptive 2D/3D mask if selected, prepares fields from source buffers, removes destination buffers, queues jobs, and starts FDP1 registers. IRQ reads/clears FDP1 status, completes jobs on frame-end or error, returns source fields and destination buffers, and either starts the next job or finishes the M2M transaction.

State and persistence: all state is volatile kernel state. Persistent hardware programming consists of register writes and runtime-PM managed LUT programming on resume. Context state tracks sequence, active transaction length, previous field, buffer queues, and adaptive mask allocation. Job state lives in fixed in-device free/queued/hardware lists protected by spinlocks.

Dependencies and integration points: depends on V4L2 mem2mem, vb2 DMA-contig, V4L2 controls/events/ioctls, runtime PM, clocks, platform IRQ/MMIO, optional R-Car FCP (`rcar_fcp_get/enable/disable/put`), and DT compatible `renesas,fdp1`. It integrates with userspace through `V4L2_CAP_VIDEO_M2M_MPLANE`.

Risks: field splitting and previous/next field retention are easy to break, especially abort and streamoff paths. `fdp1_stop_streaming()` drains different internal structures for output and capture queues and must not double-complete field-backed buffers. RGB capture depends on input YCbCr encoding and quantization restrictions. The adaptive mask DMA allocation must be freed only when allocated. IRQ clearing uses inverted status masked writes, so register semantics are critical. Hardware job lists are global to the device while contexts are scheduled by M2M, so list corruption or missing job completion would affect all instances.

Test signals: compile with `CONFIG_VIDEO_RENESAS_FDP1` and `COMPILE_TEST`; use v4l2-compliance on the M2M node; exercise `TRY_FMT/S_FMT` for all listed formats and field modes; stream progressive, alternate fields, interlaced TB/BT, adaptive 2D/3D, fixed 2D/3D, previous, and next modes; verify IRQ completion, abort, runtime suspend/resume, FCP optional path, and no leaked DMA mask buffers on repeated streamon/off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar_fdp1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar_jpu.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar_jpu.c

Purpose: implements the Renesas R-Car Gen2 JPEG Processing Unit as V4L2 memory-to-memory encoder and decoder nodes. It converts between JPEG bitstreams and NV12/NV16 single- or multi-planar YUV buffers, builds encoder JPEG headers in software, parses decoder JPEG headers enough to validate dimensions/subsampling, and programs JPU tables and DMA registers per job.

Important APIs, types, and functions: `struct jpu` owns the shared hardware, clock, IRQ, two `video_device` nodes, one `v4l2_m2m_dev`, and current context pointer. `struct jpu_ctx` tracks encoder/decoder mode, source/capture queue data, compression quality control, and V4L2 file handle. `struct jpu_buffer` stores per-buffer encoder quality or parsed decoder subsampling. Core functions include `jpu_parse_hdr()`, `jpu_generate_hdr()`, `__jpu_try_fmt()`, `jpu_streamon()`, `jpu_buf_queue()`, `jpu_buf_finish()`, `jpu_device_run()`, `jpu_irq_handler()`, `jpu_open()`, `jpu_release()`, and `jpu_probe()`.

Control flow: probe maps MMIO, requests IRQ, gets the clock, registers one V4L2 device, creates one M2M scheduler, pre-generates JPEG header blobs for four quality levels, and registers separate encoder and decoder video devices. Open selects encoder mode by video node, creates M2M queues, creates controls, enables the clock on first open, and resets hardware. Format negotiation constrains dimensions, alignment, payload sizes, and queue format compatibility. Decoder `buf_queue` parses the JPEG header from CPU-mapped output buffers, validates dimensions against configured formats, and stores subsampling. `device_run` waits for reset, chooses source/destination buffers, writes encode or decode registers, loads quantization/Huffman tables for encode, and starts hardware. IRQ handles transfer completion or decode errors, computes JPEG payload size for encode, propagates timestamp/flags, completes buffers, resets JPU, and finishes the M2M job.

State and persistence: no persistent storage. The hardware is shared by all contexts and guarded by `jpu->mutex` and `jpu->lock`; `ref_count` gates clock enable. Per-buffer state carries quality/subsampling because completion-time header writing and decode compatibility checks need values captured when the job was queued.

Dependencies and integration points: V4L2 mem2mem, vb2 DMA-contig, JPEG marker definitions from `media/jpeg.h`, V4L2 controls/events/ioctls, platform MMIO/IRQ, clock framework, and OF compatibles for R-Car Gen2 JPU variants. Userspace sees one encoder and one decoder M2M node.

Risks: decoder validation relies on `vb2_plane_vaddr()` and a minimal baseline JPEG parser; non-mappable DMABUF paths or unusual JPEG markers may fail. `jpu_cleanup()` assumes both current source and destination buffers exist. Header generation uses fixed offsets and tables, so changes to `JPU_JPEG_HDR_BLOB` must keep offsets synchronized. Clock reference counting is manual rather than runtime PM. IRQ handling ignores process-complete-only interrupts until transfer completion, which matches intended hardware behavior but should be tested on real silicon.

Test signals: build with JPU enabled or `COMPILE_TEST`; run v4l2-compliance against both nodes; encode/decode NV12/NV16 and single/multiplanar variants; test all four quality settings; feed corrupt/truncated JPEGs, unsupported subsampling, mismatched dimensions, and short destination buffers; verify suspend/resume while open, repeated open/close ref_count behavior, IRQ error paths, and generated JPEG headers via external JPEG decoders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar_jpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/renesas-ceu.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/renesas/renesas-ceu.c

Purpose: implements the Renesas Capture Engine Unit camera host as a V4L2 capture driver for parallel YUYV-style sensors. It binds sensors through V4L2 async, negotiates media-bus formats, configures CEU register conversion/reordering/downsampling, and captures frames into vb2 DMA-contig buffers.

Important APIs, types, and functions: `struct ceu_device` owns the V4L2/video device, async notifier, selected subdevice, active pix format, vb2 queue, capture list, active buffer, MMIO base, locks, and platform IRQ mask. `struct ceu_subdev` wraps async connection, bound sensor, mbus flags, and selected YUYV bus format. `struct ceu_mbus_fmt` maps media-bus code to CEU input ordering. Major functions include `ceu_parse_dt()`, `ceu_parse_platform_data()`, `ceu_notify_complete()`, `ceu_init_mbus_fmt()`, `__ceu_try_fmt()`, `ceu_set_fmt()`, `ceu_hw_config()`, `ceu_start_streaming()`, `ceu_irq()`, and runtime PM handlers.

Control flow: probe allocates the device, maps registers, requests IRQ, enables runtime PM, registers `v4l2_device`, initializes async notifier, parses either DT graph endpoints or legacy platform data, then registers the notifier. When all subdevices bind, vb2 is initialized, the first usable sensor is selected, a default NV16 VGA format is negotiated, and the video node is registered. Open powers the selected sensor and soft-resets CEU via runtime PM. Streaming programs CEU registers, starts sensor streaming, selects the first queued buffer, enables interrupts, and triggers one-frame capture. Each capture-end IRQ timestamps and completes the previous buffer, pulls the next queued buffer if present, and starts another capture; VBP error returns active and queued buffers as errors.

State and persistence: active sensor selection, selected mbus format, current pix format, active buffer, queue list, and sequence counters are volatile. Runtime PM toggles sensor power through `s_power` and resets CEU. There is no disk persistence.

Dependencies and integration points: V4L2 async/fwnode, V4L2 subdev pad ops, V4L2 controls inherited from sensor, vb2 DMA-contig, runtime PM, OF graph or `ceu_platform_data`, and platform-specific interrupt masks for RZ and SH4. Userspace gets one capture video node with input selection for multiple sensors.

Risks: the start-streaming error path iterates queued buffers but calls `vb2_buffer_done()` on `ceudev->active`, which is not set on early errors and looks suspicious. IRQ error handling completes queued buffers without deleting/reinitializing list nodes. Only 8-bit YUYV media-bus permutations are supported; raw/JPEG/binary and 16-bit bus TODOs remain. Format negotiation asks the sensor to set TRY/ACTIVE formats and CEU cannot scale, so sensor behavior drives final dimensions. `ceu_s_input()` powers old/new sensors directly and assumes open/runtime state is coherent.

Test signals: build with OF and platform-data configurations; bind a test sensor exposing each YUYV bus permutation; verify NV12/NV21/NV16/NV61 and packed YUYV/UYVY/YVYU/VYUY output; run v4l2-compliance; test multiple input switching before streaming; exercise streamon failures, VBP IRQ errors, queue underrun, runtime PM open/close, and DT endpoint polarity flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/renesas-ceu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/Kconfig

Purpose: declares build options for the RZ/G2L MIPI CSI-2 receiver (`VIDEO_RZG2L_CSI2`) and Camera Receiving Unit (`VIDEO_RZG2L_CRU`).

Important APIs/types/functions: no runtime code. The two `config` symbols control whether `rzg2l-csi2` and `rzg2l-cru` modules are built. Both depend on Renesas architecture or `COMPILE_TEST`, platform V4L2 drivers, `VIDEO_DEV`, and OF. CSI-2 selects `MEDIA_CONTROLLER`, `RESET_CONTROLLER`, `V4L2_FWNODE`, and subdev API support. CRU selects `MEDIA_CONTROLLER`, `V4L2_FWNODE`, `VIDEOBUF2_DMA_CONTIG`, and subdev API support.

Control flow and state: Kconfig influences compile-time object inclusion only. There is no runtime control flow or persistence.

Dependencies and integration points: integrates the drivers into the kernel media platform driver menu. The selected dependencies match code usage: OF graph/fwnode parsing, media-controller links, reset controls, subdevice nodes, and vb2 DMA-contig for CRU capture buffers.

Risks: CSI-2 code also uses clocks, runtime PM, reset controls, and media-controller APIs; dependency coverage is mostly via selected core media symbols and normal driver framework availability. If a future code path requires DMA buffers in CSI-2 or PM beyond generic availability, Kconfig may need updates. The CRU option does not select the CSI-2 option even though the current graph path only supports CSI-2; that allows modular independent builds but requires users to enable both for complete camera pipelines.

Test signals: run `make olddefconfig` and compile with each symbol as built-in, module, and disabled; run `COMPILE_TEST` on non-Renesas architectures; verify `modinfo` names match help text (`rzg2l-csi2`, `rzg2l-cru`).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/Makefile -->
## sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/Makefile

Purpose: maps the RZ/G2L CRU and CSI-2 Kconfig symbols to build objects.

Important APIs/types/functions: no runtime APIs. `obj-$(CONFIG_VIDEO_RZG2L_CSI2) += rzg2l-csi2.o` builds the standalone CSI-2 receiver. `rzg2l-cru-objs = rzg2l-core.o rzg2l-ip.o rzg2l-video.o` links the CRU composite module from core/media-graph, IP subdev, and video/DMA pieces. `obj-$(CONFIG_VIDEO_RZG2L_CRU) += rzg2l-cru.o` includes that composite.

Control flow and state: compile-time only; no runtime state or persistence.

Dependencies and integration points: relies on Kbuild composite object naming, so exported internal functions declared in `rzg2l-cru.h` are resolved inside `rzg2l-cru.o`. CSI-2 remains a separate module because it represents a separate platform device and OF compatible.

Risks: adding CRU files requires updating `rzg2l-cru-objs`; adding CSI-2 support files would require changing its object definition. Build failures can occur if function declarations in `rzg2l-cru.h` drift from composite member definitions.

Test signals: build `M=drivers/media/platform/renesas/rzg2l-cru` with both config symbols as modules and check that `rzg2l-cru.ko` contains `rzg2l-core.o`, `rzg2l-ip.o`, and `rzg2l-video.o` while `rzg2l-csi2.ko` is separate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-core.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-core.c

Purpose: platform-driver and media-controller core for the RZ/G2L CRU. It allocates the device, maps variant register tables, sets up resets/clocks/IRQ/runtime PM, creates the media device, parses the OF graph, binds the external CSI-2 subdevice, and connects CSI-2, CRU IP, and CRU video entities.

Important APIs, types, and functions: `rzg2l_cru_probe()`, `rzg2l_cru_remove()`, `rzg2l_cru_media_init()`, `rzg2l_cru_mc_parse_of_graph()`, `rzg2l_cru_group_notify_*()`, and variant data `rzg2l_cru_info` / `rzg3e_cru_info`. The variant info carries max dimensions, image-converter register index, register offset table, stride support flag, IRQ handler, interrupt control callbacks, and FIFO-empty callback.

Control flow: probe maps MMIO, acquires `presetn`, `aresetn`, and `video` clock, reads OF match data, requests the variant IRQ handler, registers the CRU DMA/V4L2 core, enables runtime PM, then initializes media-controller state. The media init creates a sink pad on the video entity, fills `media_device`, sets it on `v4l2_dev`, and registers an async notifier for remote endpoint port 1. When the CSI-2 subdevice is bound and the notifier completes, CRU IP is registered, subdev nodes are created, the video node is registered, and immutable links are made from CSI-2 source pad to CRU IP sink and CRU IP source to CRU video sink.

State and persistence: device state is in `struct rzg2l_cru_dev`. Register map arrays are static const. Runtime graph binding state includes `cru->csi.asd`, `cru->csi.subdev`, `cru->ip.remote`, and media entity registration. No persistent storage.

Dependencies and integration points: platform driver, OF graph/fwnode, V4L2 async, media-controller, reset/clock/runtime PM, `rzg2l-video.c` DMA registration, and `rzg2l-ip.c` subdevice registration. OF compatibles distinguish `renesas,rzg2l-cru` and `renesas,r9a09g047-cru`.

Risks: `rzg2l_cru_media_init()` currently returns 0 even after `rzg2l_cru_mc_parse_of_graph()` reports an error, after clearing `v4l2_dev.mdev`; this can hide media graph setup failures. The group-notifier complete path does not unwind already registered IP/video entities if later link creation fails. Only CSI-2 is supported despite comments mentioning possible parallel input. Register-offset tables must stay aligned with `enum rzg2l_cru_common_regs`.

Test signals: probe both compatibles; verify reset/clock names; inspect media graph links with `media-ctl`; test disabled/missing remote endpoint handling; unbind/rebind CSI-2; compile both variants; stream through CRU to ensure the selected callbacks match the variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-cru-regs.h -->
## sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-cru-regs.h

Purpose: centralizes symbolic register IDs and bit definitions for CRU common logic across RZ/G2L and RZ/G3E-style variants.

Important APIs/types/functions: defines bit helpers for CRU control/status, memory bank addresses, AXI attributes, FIFO pointers, image stride, image conversion enable/control, CSI virtual channel selection, and output data mode. `enum rzg2l_cru_common_regs` is the key ABI between code and variant-specific offset tables in `rzg2l-core.c`; each enum value indexes `cru->info->regs`.

Control flow and state: no executable control flow. Runtime read/write helpers in `rzg2l-video.c` consume these IDs and map them through variant offset arrays.

Dependencies and integration points: requires kernel bit macros such as `BIT()` and `GENMASK()` from including C files. It is included by CRU core, IP, and video files. `AMnMBxADDRL/H(x)` depend on enum ordering where bank address IDs are sequential pairs.

Risks: enum ordering is a hard contract; inserting values without updating every variant offset array can make register writes target wrong hardware addresses. Some IDs are unavailable on a given variant and are represented by zero offsets, so call sites must only use registers valid for that variant or rely on guarded helpers. `AMnMBxADDRL/H(x)` arithmetic returns enum indexes, not byte offsets, which is correct only because write helpers translate later.

Test signals: compile with both CRU variants; enable dynamic/debug checks for WARNs in `__rzg2l_cru_write/read`; validate register writes against hardware manuals or tracepoints; stream on both variants to exercise `CRUnIE` vs `CRUnIE2`, `AMnMBS` vs `AMnMADRSL/H`, and stride-capable paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-cru-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-cru.h -->
## sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-cru.h

Purpose: shared private header for the RZ/G2L CRU composite driver. It defines device structures, format descriptors, DMA state, limits, and cross-file function prototypes used by `rzg2l-core.c`, `rzg2l-ip.c`, and `rzg2l-video.c`.

Important APIs/types/functions: `struct rzg2l_cru_dev` is the central state object, holding MMIO base, variant info, reset/clock handles, video and V4L2 devices, async notifiers, CRU IP/CSI/media graph state, vb2 queue, scratch DMA buffer, hardware buffer slots, queued buffers, sequence, DMA state, and active V4L2 format. `struct rzg2l_cru_info` abstracts variant max dimensions, register map, stride support, IRQ and interrupt callbacks, and FIFO-empty callback. `struct rzg2l_cru_ip_format` connects media-bus codes, CSI-2 datatypes, V4L2 pixel formats, `ICnDMR`, and YUV/raw classification.

Control flow and state: no executable flow, but the header defines the state machine values `STOPPED`, `STARTING`, `RUNNING`, and `STOPPING`. The prototypes show module boundaries: core handles platform/media setup, IP handles subdev format/stream handoff, and video handles DMA, IRQs, vb2, and video-node ioctls.

Dependencies and integration points: includes V4L2 async/dev/device and vb2-v4l2 headers plus reset and IRQ types. It is private to this driver directory and not a UAPI. The fixed hardware buffer counts and alignment mask are consumed by DMA slot management.

Risks: `buf_addr` is sized to `RZG2L_CRU_HW_BUFFER_DEFAULT` while `queue_buf` is sized to `RZG2L_CRU_HW_BUFFER_MAX`; current code sets `num_buf` to the default, but raising `num_buf` would overflow `buf_addr`. Function pointer contracts in `rzg2l_cru_info` must match variant register availability. The `enum rzg2l_csi2_pads` name actually describes CRU IP pads, which may confuse future edits.

Test signals: build all CRU objects together; run sparse or Coccinelle for prototype drift; test variant callbacks and hardware slot limits; audit any future change to `num_buf`, pad enum names, or `struct rzg2l_cru_dev` locking fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-cru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-csi2.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-csi2.c

Purpose: implements a V4L2 subdevice driver for Renesas RZ/G2L and RZ/V2H MIPI CSI-2 receiver blocks. It parses CSI-2 endpoints, validates lane count, configures D-PHY and link reception, forwards streaming to the remote sensor, and exposes sink/source media pads for media-controller pipelines.

Important APIs, types, and functions: `struct rzg2l_csi2` stores MMIO, resets, clocks, vclk rate, subdev, pads, async notifier, remote source, lane count, high-speed frequency, and D-PHY state. `struct rzg2l_csi2_info` abstracts D-PHY callbacks, clock requirements, and size bounds. Key functions include `rzg2l_csi2_calc_mbps()`, `rzg2l_csi2_dphy_enable/disable()`, `rzv2h_csi2_dphy_enable/disable()`, `rzg2l_csi2_mipi_link_enable/disable()`, `rzg2l_csi2_s_stream()`, `pre_streamon`, `post_streamoff`, pad format/enum ops, async notifier ops, DT parsing, lane validation, probe/remove, and runtime PM reset handlers.

Control flow: probe gets match data, maps MMIO, acquires resets/clocks, parses port 0 endpoint, registers an async notifier for the remote source, enables runtime PM, validates requested lanes against the hardware maximum from `CSI2nMCG`, initializes the subdev and pads, and registers the subdev. Streaming on runtime-resumes, configures link registers, deasserts common reset, then calls remote sensor `s_stream(1)`. In the CRU pipeline, upstream `pre_streamon` enables D-PHY before CRU image processing starts; `post_streamoff` disables it if an error occurs before normal stop. Streaming off calls remote `s_stream(0)`, disables D-PHY, disables link, and runtime-suspends.

State and persistence: volatile subdevice state contains active pad formats and `dphy_enabled`. Runtime PM asserts/deasserts `presetn`; streaming uses `cmn_rstb`, `sysclk`, and `vclk`. No persisted data.

Dependencies and integration points: V4L2 subdev/media-controller/async/fwnode, `v4l2_get_link_freq`, clocks, resets, runtime PM, OF graph, MIPI CSI-2 media bus formats, and compatibles `renesas,rzg2l-csi2` and `renesas,r9a09g057-csi2`. It links a remote sensor to its sink pad and provides source pad data to CRU.

Risks: `rzg2l_csi2_notify_bound()` creates a pad link from remote source pad index `RZG2L_CSI2_SINK` (0), assuming the remote source pad index is 0; sensors with different source pad indexes could be wrong. `rzg2l_csi2_dphy_enable()` sets `dphy_enabled = true` even after `clk_prepare_enable(sysclk)` fails and calls disable, which may leave misleading state. Link enable disables `vclk` before re-enabling it, which should be checked against runtime PM sequencing. Timing tables are fixed and out-of-range link frequencies fail stream setup.

Test signals: compile both compatibles; use media-ctl to inspect links; test 1/2/4 lane DT values and invalid lanes; stream RAW8/10/12/14 and UYVY formats; verify link-frequency control propagation; exercise pre-streamon failure cleanup, remote sensor stream failure, runtime PM suspend/resume, and high-speed frequency boundaries for both D-PHY implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-csi2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-ip.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-ip.c

Purpose: implements the internal CRU image-processing V4L2 subdevice. It defines supported CRU media bus and memory formats, propagates sink format to source format, validates codes and sizes, and sequences CRU image processing around the upstream CSI-2 subdevice.

Important APIs, types, and functions: `rzg2l_cru_ip_formats[]` maps UYVY and Bayer RAW8/10/12/14 media bus codes to V4L2 pix formats, CSI-2 datatypes, ICnDMR values, and YUV/raw classification. Lookup helpers `rzg2l_cru_ip_code_to_fmt()`, `format_to_fmt()`, `index_to_fmt()`, and `fmt_supports_mbus_code()` are consumed by video/DMA code. Subdev operations are `rzg2l_cru_ip_s_stream()`, `rzg2l_cru_ip_set_format()`, `enum_mbus_code`, `enum_frame_size`, and `init_state`. Registration helpers create a two-pad pixel formatter entity.

Control flow: on format set, source pad requests are read-only, while sink pad requests are validated, clamped to CRU variant bounds, forced to progressive field, and copied to the source pad. Stream-on calls remote `pre_streamon`, waits briefly, starts CRU image processing, then calls remote `s_stream(1)`. On failures it calls remote `post_streamoff` and stops image processing. Stream-off calls remote `s_stream(0)`, remote `post_streamoff`, then stops CRU image processing.

State and persistence: active subdev state stores sink/source media-bus formats. `cru->ip.remote` points to the bound CSI-2 subdevice. There is no persistent state.

Dependencies and integration points: V4L2 subdev state API, media-controller link validation, MIPI CSI-2 datatype constants, `rzg2l-video.c` image-processing start/stop, and `rzg2l-core.c` media graph registration.

Risks: `rzg2l_cru_ip_get_src_fmt()` returns a pointer from active subdev state after unlocking it, which may be fragile if callers assume long-lived stable storage. Format table grouping maps all RAW10 patterns to one packed CRU10 pixelformat, similarly RAW12/14, so media-code compatibility must be validated by video link validation. Stream sequencing is tightly coupled to CSI-2 `pre_streamon/post_streamoff` semantics.

Test signals: enumerate media bus codes and frame sizes; set each supported sink code and verify source propagation; validate media links against CRU video formats; inject remote `pre_streamon`, `s_stream`, and `post_streamoff` failures; stream each supported raw/YUV format through the full pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-ip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-video.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-video.c

Purpose: implements the CRU video node, vb2 queue, DMA slot management, image-conversion programming, stream control, and variant-specific IRQ handling for RZ/G2L and RZ/G3E CRU capture.

Important APIs, types, and functions: `struct rzg2l_cru_buffer` wraps vb2 buffers for `buf_list`. Register helpers map logical register IDs through variant offset tables. Key functions include `rzg2l_cru_dma_register/unregister()`, `rzg2l_cru_video_register/unregister()`, `rzg2l_cru_start_streaming_vq()`, `rzg2l_cru_stop_streaming_vq()`, `rzg2l_cru_set_stream()`, `rzg2l_cru_start_image_processing()`, `rzg2l_cru_stop_image_processing()`, `rzg2l_cru_initialize_axi()`, `rzg2l_cru_initialize_image_conv()`, IRQ handlers `rzg2l_cru_irq()` and `rzg3e_cru_irq()`, and V4L2 ioctl helpers.

Control flow: DMA register initializes `v4l2_device`, locks, buffer list, state, and a single-planar capture vb2 queue. Video register initializes default UYVY format and registers the video node and media device. Stream-on runtime-resumes, enables `vclk`, deasserts resets, allocates a scratch DMA buffer, starts the media pipeline and upstream subdevices, then marks DMA as `STARTING`. CRU IP stream-on calls `rzg2l_cru_start_image_processing()`, which selects CSI input, releases image reset, clears interrupts, fills hardware slots from queued buffers or scratch, configures image conversion and CSI virtual channel, enables interrupts, and enables image reception. IRQs synchronize startup on slot 0, complete buffers with timestamps/sequences, drop scratch frames, and refill the completed slot. Stream-off stops upstream streaming, disables image processing, waits for idle/FIFO/AXI stop, asserts reset, frees scratch, returns all buffers, disables clock, and runtime-suspends.

State and persistence: `cru->state` tracks stopped/starting/running/stopping. `queue_buf[]` maps hardware slots to userspace buffers while `buf_list` holds queued vb2 buffers. `scratch` keeps capture running when userspace under-runs. `buf_addr[]` is used by RZ/G3E IRQ logic to map current memory address back to a slot. All state is volatile.

Dependencies and integration points: V4L2/vb2 DMA-contig, media-controller pipeline helpers, upstream CRU IP/CSI subdevices, runtime PM, clocks, resets, MMIO register maps, MIPI CSI-2 frame descriptors for virtual channel selection, and format lookup helpers from `rzg2l-ip.c`.

Risks: `buf_addr` capacity is smaller than the advertised max hardware slot count if `num_buf` is ever increased. `rzg2l_cru_start_streaming_vq()` leaks enabled runtime resources if scratch allocation fails unless the `assert_presetn` path is reached; current code returns directly after allocation failure. `rzg3e_cru_enable_interrupts()` writes `CRUnIE2` twice rather than ORing FS and FE enables, so the first write may be overwritten depending on register semantics. Logical register helpers warn on zero offset except `CRUnCTRL`; variant tables must be exact. Startup synchronization drops early slots until slot 0, so ordering assumptions should be tested on hardware.

Test signals: v4l2-compliance; media pipeline validation with matching and mismatched pad formats; stream with too few queued buffers to exercise scratch drops; test both RZ/G2L and RZ/G3E IRQ paths; validate virtual-channel selection through `get_frame_desc`; stress streamon/off, allocation failure, queue underrun, runtime PM, and format enumeration for UYVY/RAW8/RAW10/RAW12/RAW14.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/Kconfig

Purpose: declares the `VIDEO_RZV2H_IVC` option for the Renesas RZ/V2H(P) Input Video Control block driver.

Important APIs/types/functions: no runtime code. The tristate depends on platform V4L2 drivers, `VIDEO_DEV`, Renesas architecture or `COMPILE_TEST`, OF, and PM. It selects `VIDEOBUF2_DMA_CONTIG`, `MEDIA_CONTROLLER`, and `VIDEO_V4L2_SUBDEV_API`, matching the composite driver's video queue and media graph requirements.

Control flow and state: compile-time only. It determines whether the `rzv2h-ivc` module is built.

Dependencies and integration points: integrates the RZ/V2H(P) IVC into the media platform build. The PM dependency is explicit because the driver uses runtime PM and system sleep force suspend/resume helpers.

Risks: helper files also use clocks and reset controls via common kernel frameworks; no explicit Kconfig dependency is listed for those because they are generally available behind driver framework stubs or selected elsewhere. The help text uses spaces different from nearby Kconfig style but is functionally harmless.

Test signals: build as module and built-in under Renesas and `COMPILE_TEST`; ensure selected media/vb2/subdev symbols satisfy all composite objects; verify module name `rzv2h-ivc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/Makefile -->
## sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/Makefile

Purpose: defines the composite object layout for the RZ/V2H(P) IVC driver.

Important APIs/types/functions: no runtime APIs. `rzv2h-ivc-y` links `rzv2h-ivc-dev.o`, `rzv2h-ivc-subdev.o`, and `rzv2h-ivc-video.o` into one module. `obj-$(CONFIG_VIDEO_RZV2H_IVC) += rzv2h-ivc.o` includes it when configured.

Control flow and state: compile-time only. Cross-file functions declared in `rzv2h-ivc.h` resolve inside the composite module.

Dependencies and integration points: separates platform/runtime resource management (`*-dev.c`), subdevice/media graph (`*-subdev.c`), and video/vb2 transfer logic (`*-video.c`) while publishing one module for the platform device compatible.

Risks: adding new source files requires updating `rzv2h-ivc-y`. Removing or renaming helper functions in one object breaks the composite link.

Test signals: module build with `CONFIG_VIDEO_RZV2H_IVC=m`; inspect that all three objects are linked into `rzv2h-ivc.ko`; compile-test after any file split.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/rzv2h-ivc-dev.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/rzv2h-ivc-dev.c

Purpose: platform-device, runtime-PM, MMIO helper, resource acquisition, global configuration, and IRQ dispatch layer for the RZ/V2H(P) Input Video Control block. Video queue and subdevice details live in sibling composite objects.

Important APIs, types, and functions: exports internal helpers `rzv2h_ivc_write()` and `rzv2h_ivc_update_bits()` for register access. `rzv2h_ivc_get_hardware_resources()` maps MMIO and acquires three named clock/reset resources: `reg`, `axi`, and `isp`. `rzv2h_ivc_global_config()` programs single-exposure input, disables interrupts while changing context mode, selects single-context software/hardware configuration, and enables frame-end interrupt. `rzv2h_ivc_isr()` coordinates two interrupts per frame with `ivc->vvalid_ifp`, calling `rzv2h_ivc_buffer_done()` after transfer completion and `rzv2h_ivc_transfer_buffer()` after post-frame VBLANK. Runtime PM handlers enable/disable clocks, deassert/assert resets, configure hardware, request/free IRQ, and integrate with system sleep. Probe initializes locks, resources, autosuspend, IRQ number, and the subdevice.

Control flow: probe allocates `struct rzv2h_ivc`, initializes mutex/spinlock, maps resources, enables autosuspend runtime PM, gets the IRQ, and delegates media/subdevice initialization to `rzv2h_ivc_initialise_subdevice()`. Runtime resume powers hardware, configures global mode, and requests IRQ. Runtime suspend asserts resets, disables clocks, and frees IRQ. IRQ runs under spinlock and expects `vvalid_ifp` to be initialized to two events when a frame transfer is active.

State and persistence: device state is volatile in `struct rzv2h_ivc` from `rzv2h-ivc.h`, including MMIO base, clocks, resets, locks, IRQ number, and transfer counters. No persistent storage. Autosuspend delay is 2000 ms.

Dependencies and integration points: platform driver, OF compatible `renesas,r9a09g057-ivc`, runtime PM, system sleep PM, clk/reset bulk APIs, IRQ framework, and sibling IVC video/subdev modules through internal helper calls.

Risks: `pm_runtime_enable()` is not devm-managed and remove does not visibly disable runtime PM in this file, so sibling cleanup or core behavior must cover it. Requesting/freeing IRQ on every runtime resume/suspend is valid but sensitive to balanced PM usage. `rzv2h_ivc_isr()` warns if `vvalid_ifp` is zero; incorrect video-side initialization can make interrupts noisy or drop frames. Runtime suspend frees IRQ after clocks/resets are disabled, which should be verified against possible pending interrupts.

Test signals: build the composite module; probe with all three clock/reset names present and absent optional resets; runtime PM autosuspend/resume while streaming and idle; trigger frame transfers and verify the two-interrupt sequence; unbind/remove after active use; run media/v4l2 compliance through sibling video node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/rzv2h-ivc-dev.c -->

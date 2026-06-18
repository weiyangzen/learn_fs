# subset-b-004162 research

Grouped research report for the requested Rockchip RKVDEC/VDPU38x decoder files and Samsung Exynos G-Scaler platform files. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-rcb.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-rcb.c

Purpose: implements the Rows and Columns Buffer manager used by newer Rockchip decoder variants. RCB buffers are per-context auxiliary work areas whose sizes are derived from decoded picture width or height and whose addresses are programmed by the VDPU381/VDPU383 H.264 and HEVC backends.

Important APIs and functions: `rkvdec_allocate_rcb`, `rkvdec_free_rcb`, `rkvdec_rcb_buf_dma_addr`, `rkvdec_rcb_buf_size`, and `rkvdec_rcb_buf_count`. Internal `rkvdec_rcb_size` applies each `struct rcb_size_info` multiplier against either picture width or picture height.

Control flow: streaming start calls allocation with the variant RCB table. Each requested buffer first attempts SRAM allocation from the optional device-tree `sram` gen_pool; if an IOMMU domain is present, the SRAM physical address is mapped through the domain and the register-visible DMA address is replaced with the virtual/IOMMU address. Failed SRAM allocation or mapping falls back to coherent DMA memory. On partial failure, `rkvdec_free_rcb` tears down every successfully allocated entry.

State and persistence: state is transient and hangs off `ctx->rcb_config`; each entry records CPU pointer, DMA/register address, size, and allocation type. No state persists beyond the V4L2 streaming session. SRAM mappings are explicitly unmapped and gen_pool regions freed; DMA allocations are freed with `dma_free_coherent`.

Dependencies and integration points: depends on `rkvdec.h`, `rkvdec-rcb.h`, genalloc, DMA coherent allocation, and optional IOMMU APIs. Integrated from `rkvdec_start_streaming`, freed from error and stop paths, and consumed by VDPU38x codec register programming.

Risks: the code uses devm allocation for per-stream metadata and then manually frees it, which is valid with `devm_kfree` but makes lifetime assumptions important. IOMMU mapping uses the SRAM CPU pointer value as the IOVA. Buffer IDs are trusted by accessors. Size calculations are multiplier based and may become wrong if hardware tables or alignment requirements change.

Test signals: exercise VDPU381/VDPU383 streaming with and without SRAM, with and without an IOMMU, and force allocation fallback/failure. Useful checks are no IOMMU faults, RCB register addresses matching allocation type, clean stream stop, and kmemleak/dma-debug silence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-rcb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-rcb.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-rcb.h

Purpose: declares the RKVDEC RCB sizing contract and public helper API used by variant setup and codec backends.

Important APIs and types: `enum rcb_axis` selects `PIC_WIDTH` or `PIC_HEIGHT`; `struct rcb_size_info` stores an 8-bit multiplier and axis. Exported declarations cover allocation, free, count, size, and DMA address lookup for buffers in `struct rkvdec_ctx`.

Control flow: variant descriptors define arrays of `struct rcb_size_info`; streaming start passes those arrays to `rkvdec_allocate_rcb`. Codec backends call the accessors while filling register images, then stop-streaming calls `rkvdec_free_rcb`.

State and persistence: the header owns no state. It defines the shape of size metadata and exposes access to context-owned volatile RCB allocations.

Dependencies and integration points: includes Linux integer types and forward-declares `struct rkvdec_ctx`. It bridges core variant tables in `rkvdec.c`, allocation implementation in `rkvdec-rcb.c`, and VDPU381/VDPU383 H.264/HEVC register setup.

Risks: there is no include guard in this header, so repeated inclusion relies on harmless duplicate declarations. The `u8` multiplier bounds the supported size multiplier, which is currently enough for local tables but is part of the ABI between variant data and allocation logic.

Test signals: compile coverage for all RKVDEC variants and successful stream start on VDPU38x paths indirectly validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-rcb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-regs.h

Purpose: describes the original/single-register-region RKVDEC register layout used mainly by legacy HEVC/H.264 code and the VP9 backend. It also defines interrupt, cache, QoS, and decode-mode constants.

Important APIs and types: key constants include `RKVDEC_REG_INTERRUPT`, interrupt/status bits, `RKVDEC_REG_QOS_CTRL`, cache command offsets, and mode values for HEVC/H.264/VP9. Packed register structs include `rkvdec_common_regs`, `rkvdec_h26x_regs`, `rkvdec_vp9_regs`, and top-level `rkvdec_regs`; `struct ref_base` encodes reference surface flags and address fields.

Control flow: codec implementations build an in-memory `struct rkvdec_regs`, fill common and codec-specific fields from V4L2 stateless controls and buffer DMA addresses, then copy the image to MMIO. IRQ handling in `rkvdec.c` reads/writes the interrupt register using the same bit definitions.

State and persistence: no runtime state is stored here; the file is a memory/register contract. Packed bitfields represent volatile hardware configuration and status, so layout correctness is critical.

Dependencies and integration points: depends on Linux `types.h` and bit macros. It integrates with `rkvdec-vp9.c`, legacy H.264/HEVC common backends outside this subset, and core interrupt/watchdog code.

Risks: C bitfield order and packing are compiler/architecture sensitive, though this driver targets Linux kernel build assumptions. Register structs must stay synchronized with hardware manuals. Address bitfields such as 28-bit bases assume alignment and truncation rules that callers must respect.

Test signals: allmodconfig/build coverage, VP9 decode conformance, IRQ status handling, cache command writes, and MMIO traces comparing programmed register words against known-good hardware programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu381-h264.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu381-h264.c

Purpose: implements the VDPU381-specific stateless H.264 backend for RKVDEC. It translates V4L2 H.264 controls, DPB state, reference lists, scaling lists, and CABAC/RPS tables into the register and auxiliary-memory format expected by RK3588-class VDPU381 hardware.

Important APIs and functions: exported format ops are `rkvdec_vdpu381_h264_fmt_ops`. Internal helpers include `assemble_hw_pps`, `config_registers`, `rkvdec_write_regs`, `rkvdec_h264_start`, `rkvdec_h264_stop`, `rkvdec_h264_run`, and `rkvdec_h264_try_ctrl`. Private structures define hardware SPS/PPS packets, `rkvdec_h264_priv_tbl`, and `rkvdec_h264_ctx`.

Control flow: start validates the active SPS and allocates a coherent private table containing CABAC tables. Run builds V4L2 P/B reference lists, assembles scaling list, PPS/SPS, reference buffer indices, and RPS, fills common/codec/address/high-POC register blocks, posts the mem2mem request, schedules a hardware-derived watchdog, then starts decode through `VDPU381_REG_DEC_E`.

State and persistence: per-stream state is `ctx->priv`, containing a coherent private table, reference-list cache, and a register image. Per-frame state is rewritten before each run. No persistent storage exists beyond DMA buffers and context lifetime.

Dependencies and integration points: depends on V4L2 H.264 helpers, vb2 DMA-contig addresses, RKVDEC H.264 common helpers, CABAC tables, RCB accessors, and VDPU381 register definitions. It is selected by `vdpu381_coded_fmts` in `rkvdec.c`.

Risks: the PPS packet uses PPS ID as an array index and assumes userspace-provided control values are validated by common helpers. Reference fallback to the current destination buffer hides unused DPB entries but makes address bugs hard to spot. RCB order must match hardware. Large dimensions rely on timeout and stride arithmetic staying in range.

Test signals: V4L2 stateless H.264 decode on RK3588, conformance clips covering IDR/P/B frames, long-term references, scaling matrices, field pictures, and high resolutions; watchdog timeout/error IRQ behavior; DMA/IOMMU fault absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu381-h264.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu381-hevc.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu381-hevc.c

Purpose: implements the VDPU381 HEVC stateless decode backend. It converts HEVC SPS/PPS/scaling/RPS/decode controls into VDPU381 parameter packets, private tables, reference-address registers, and common decode controls.

Important APIs and functions: exported `rkvdec_vdpu381_hevc_fmt_ops`; private functions `assemble_hw_pps`, `set_ref_valid`, `config_registers`, `rkvdec_write_regs`, `rkvdec_hevc_validate_sps`, `rkvdec_hevc_start`, `rkvdec_hevc_stop`, `rkvdec_hevc_run`, and `rkvdec_hevc_try_ctrl`. Key state types are `rkvdec_hevc_priv_tbl` and `rkvdec_hevc_ctx`.

Control flow: start validates 4:2:0 8-bit/10-bit SPS constraints and allocates a coherent table with CABAC data. Each run gathers V4L2 controls, assembles scaling lists and PPS/tile data, optionally assembles short/long-term RPS, fills VDPU381 register blocks, posts source/destination buffers, schedules the watchdog, and enables decode. Missing extended SPS RPS controls cause a rate-limited warning but do not stop decode on this variant.

State and persistence: `ctx->priv` owns coherent parameter/RPS/scaling/CABAC memory plus caches for scaling matrix and SPS short-term RPS controls. Current frame register images are rebuilt per job. Hardware state exists only while clocks and MMIO programming are active.

Dependencies and integration points: depends on V4L2 HEVC stateless controls, `rkvdec-hevc-common`, CABAC tables, RCB buffer accessors, vb2 DMA-contig, and `rkvdec-vdpu381-regs.h`. Selected by the RK3588 variant table.

Risks: missing RPS controls can produce wrong frames rather than an immediate error. Tile-column/row and bitfield packing must match hardware exactly. Reference validity is set through a switch with no default behavior for out-of-range IDs. DMA address and COLMV offsets must match the capture buffer layout from core format setup.

Test signals: HEVC conformance streams with tiles, scaling lists, short/long-term references, 8-bit and 10-bit Main profiles, resolution changes requiring format renegotiation, and stress runs checking timeout and IOMMU behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu381-hevc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu381-regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu381-regs.h

Purpose: defines the VDPU381 register map used by RK3588-class H.264 and HEVC decode backends. It splits the hardware register space into common control, codec parameter, common address, codec address, and POC-highbit regions.

Important APIs and types: offset macros such as `OFFSET_COMMON_REGS`, `OFFSET_CODEC_PARAMS_REGS`, `OFFSET_COMMON_ADDR_REGS`, and `OFFSET_CODEC_ADDR_REGS`; mode and interrupt constants; packed structs `rkvdec_vdpu381_regs_common`, `rkvdec_vdpu381_regs_common_addr`, H.264/HEVC parameter structs, H.26x address/high-POC structs, and aggregate `rkvdec_vdpu381_regs_h264`/`hevc`.

Control flow: VDPU381 codec backends fill these structs in memory and write each region with `rkvdec_memcpy_toio`; the core IRQ handler reads `VDPU381_REG_STA_INT` and applies status-bit constants.

State and persistence: the header stores no software state. It is a packed representation of hardware register words and must remain stable across all jobs for the same hardware generation.

Dependencies and integration points: includes Linux types and bit macros through kernel headers. Integrated by `rkvdec-vdpu381-h264.c`, `rkvdec-vdpu381-hevc.c`, and core interrupt/probe logic.

Risks: the include guard name `_RKVDEC_REGS_H_` collides conceptually with the older `rkvdec-regs.h` guard style, though the literal names differ enough in this tree. Bitfield layout, reserved holes, and register offsets are high-risk: a one-word drift would program wrong MMIO. RCB array length is fixed at 10 and must match variant tables.

Test signals: compile-time struct size checks would be valuable, but runtime signals are successful H.264/HEVC decode, known-good MMIO dumps, IRQ status handling, and no accesses outside mapped resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu381-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu383-h264.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu383-h264.c

Purpose: implements the VDPU383 H.264 backend for RK3576-class RKVDEC hardware. It uses a newer link/function register split and a different global parameter packet from VDPU381.

Important APIs and functions: exported `rkvdec_vdpu383_h264_fmt_ops`; private helpers `set_field_order_cnt`, `set_dec_params`, `assemble_hw_pps`, `config_registers`, `rkvdec_write_regs`, start/stop/run/try-control hooks, and private H.264 SPS/PPS/table/context structures.

Control flow: start validates SPS and allocates a coherent private table with CABAC data. Run builds H.264 reference lists, scaling data, hardware PPS, buffer indices, and RPS. Register configuration fills common fields, per-codec stream/stride/global length fields, reference/COLMV/payload addresses, RCB offset+size pairs, and auxiliary table base addresses. Decode is started by programming link timeout, IP enable, and decode-enable registers.

State and persistence: `ctx->priv` owns coherent auxiliary memory, reference-list storage, and a VDPU383 register image. Per-frame DPB POC and field flags are stored in the hardware PPS packet rather than the VDPU381 parameter registers. State is released on stream stop.

Dependencies and integration points: depends on V4L2 H.264 helpers, RKVDEC H.264 common code, RCB manager, CABAC table, `rkvdec-vdpu383-regs.h`, vb2 DMA-contig, and the VDPU383 variant table.

Risks: this path writes both reference base and payload-state base arrays, increasing address-programming surface. RCB register entries include size and address, so allocation-size bugs can affect hardware bounds. PPS fields are large packed bitfields, and helper functions manually enumerate all 16 DPB POC entries.

Test signals: H.264 decode on RK3576 hardware, field-picture and long-term-reference conformance, streams with scaling matrices and many DPB entries, link interrupt completion, timeout handling, and DMA/IOMMU fault monitoring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu383-h264.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu383-hevc.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu383-hevc.c

Purpose: implements the VDPU383 HEVC backend. It prepares a VDPU383-specific combined SPS/PPS global packet, RPS/scaling/CABAC private tables, reference address registers, and link-block decode start sequence.

Important APIs and functions: exported `rkvdec_vdpu383_hevc_fmt_ops`; helpers `set_column_row`, `set_pps_ref_pic_poc`, `assemble_hw_pps`, `config_registers`, `rkvdec_write_regs`, `rkvdec_hevc_validate_sps`, and start/stop/run/try-control hooks. Main state is `rkvdec_hevc_ctx` with a coherent `rkvdec_hevc_priv_tbl`.

Control flow: start validates HEVC SPS constraints and allocates private DMA memory with CABAC data. Run requires extended SPS long/short-term RPS controls when the SPS advertises those sets; unlike VDPU381, missing RPS returns `-EINVAL` to avoid IOMMU faults. It then assembles scaling, PPS/tile/POC data, RPS, register images, posts buffers, schedules the watchdog, and starts decode through VDPU383 link registers.

State and persistence: per-context caches track scaling matrix and short-term RPS data. Per-frame state includes current POC, reference POCs, valid-bit masks, tile dimensions, and DMA addresses. All state is volatile and released at stream stop.

Dependencies and integration points: depends on V4L2 HEVC stateless controls, RKVDEC HEVC common helpers, RCB accessors, VDPU383 register definitions, DMA-contig buffers, and core variant operations including VDPU383 matrix flattening.

Risks: tile dimension packing via paired 12-bit values is sensitive to HEVC PPS limits and hardware expectations. The loop over active DPB entries skips the final array slot by using `ARRAY_SIZE(dpb) - 1`, which should be validated against hardware/reference-list expectations. Missing RPS is intentionally fatal here due to observed IOMMU-fault risk.

Test signals: RK3576 HEVC conformance covering tiles, non-uniform tile spacing, Main/Main10, scaling matrices, short/long-term RPS, malformed/missing controls, and link interrupt/timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu383-hevc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu383-regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu383-regs.h

Purpose: defines the VDPU383 register layout and link-register constants used by RK3576-class H.264/HEVC backends.

Important APIs and types: offset macros for common, codec parameter, common address, codec address, and POC-highbit regions; mode, timeout, link interrupt, link IP-enable, and decode-enable constants; packed structs `vdpu383_regs_common`, `vdpu383_regs_common_addr`, `vdpu383_regs_h26x_addr`, `vdpu383_regs_h26x_params`, and aggregate `vdpu383_regs_h26x`.

Control flow: VDPU383 codec backends populate these structs and copy them to the function register block, then write link registers (`VDPU383_LINK_TIMEOUT_THRESHOLD`, `VDPU383_LINK_IP_ENABLE`, `VDPU383_LINK_DEC_ENABLE`) to launch decode. The core IRQ handler uses link status and interrupt-enable constants.

State and persistence: no state is stored in the header; it describes the transient MMIO programming image. RCB entries include both offset/address and size fields, unlike VDPU381.

Dependencies and integration points: includes Linux types and bit macros. Consumed by VDPU383 H.264/HEVC code and `rkvdec.c` variant IRQ handling.

Risks: the include guard says `_RKVDEC_VDPU838_REGS_H_`, apparently a typo for VDPU383; it still works but can confuse maintenance. Struct comments and offset constants must match hardware exactly. RCB array length is 11 while the current variant table has 10 entries, so additions must keep both sides aligned.

Test signals: compile coverage, hardware decode on RK3576, link interrupt clear/disable behavior, timeout thresholds, and register dump comparison against vendor programming sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vdpu383-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vp9.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vp9.c

Purpose: implements the VP9 stateless backend for the original RKVDEC register model. It prepares VP9 probability tables, segmentation maps, reference metadata, symbol-count adaptation, and register programming for profile-0 VP9 frame decode.

Important APIs and functions: exported `rkvdec_vp9_fmt_ops` with adjust/start/stop/run/done hooks. Key helpers include `init_probs`, `init_intra_only_probs`, `init_inter_probs`, `config_registers`, `validate_dec_params`, `rkvdec_vp9_run_preamble`, `rkvdec_vp9_done`, `rkvdec_init_v4l2_vp9_count_tbl`, and allocation helpers in start/stop. Private types model probability-table layout, hardware symbol-count layout, current/last frame info, and context state.

Control flow: run preamble gets VP9 frame and compressed-header controls, validates profile/resolution, resets/updates V4L2 frame contexts, and applies compressed-header probability updates. `init_probs` translates V4L2 probability tables into hardware-aligned layout. `config_registers` resolves reference buffers by timestamp, updates current/last frame state, computes aligned pitch/height and MV buffer address, configures segmentation/ref scaling/loop-filter carry-over, writes DMA bases and error controls, and copies the register image to MMIO. Completion adapts probabilities from the count buffer and saves frame context when requested.

State and persistence: VP9 context persists across frames to track four frame contexts, current/last frame metadata, two alternating segmentation maps, probability tables, and coherent private/count tables. This is stream-local state, freed on stop.

Dependencies and integration points: depends on V4L2 VP9 stateless helpers, vb2 timestamp lookup, DMA-contig buffers, `rkvdec-regs.h`, mem2mem request flow, and core decoded-buffer metadata.

Risks: only profile 0 is accepted. Probability/count layout is highly hardware-specific and alignment-sensitive. Reference lookup by timestamp falls back to the destination buffer, which avoids invalid DMA but can conceal userspace reference mistakes. Resolution changes require userspace to update capture format exactly to aligned dimensions.

Test signals: VP9 profile-0 conformance, key/intra/inter frames, segmentation map update/no-update cases, frame-context refresh modes, resolution-change negotiation, probability adaptation correctness, and IOMMU/dma-debug monitoring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vp9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec.c

Purpose: core V4L2 mem2mem platform driver for Rockchip RKVDEC. It owns device probing, variant selection, V4L2/media/vb2 setup, stateless codec control registration, format negotiation, queue lifecycle, job scheduling, IRQ/watchdog completion, runtime PM, and variant operations.

Important APIs and functions: major groups include format helpers (`rkvdec_try_*_fmt`, `rkvdec_s_*_fmt`, enum/get handlers), queue callbacks (`rkvdec_queue_setup`, `buf_prepare`, `start_streaming`, `stop_streaming`), exported codec helpers (`rkvdec_run_preamble`, `rkvdec_run_postamble`, `rkvdec_memcpy_toio`, `rkvdec_schedule_watchdog`, `rkvdec_quirks_disable_qos`), job/IRQ handling, matrix flatteners, variant tables, `rkvdec_probe`, and `rkvdec_remove`.

Control flow: probe matches a device-tree compatible to a variant, suppresses secondary multicore instances, maps register resources, acquires clocks/IRQ/SRAM/IOMMU state, enables runtime PM, and registers V4L2/media devices. Open creates a context with default coded/capture formats and all stateless controls. Streaming start invokes codec `start` and RCB allocation. Device-run calls the selected codec `run`; IRQ or watchdog finishes buffers, calls codec `done` if present, and completes the mem2mem job.

State and persistence: device state includes V4L2/media devices, m2m scheduler, clocks, MMIO bases, delayed watchdog, optional SRAM pool/IOMMU domains, and immutable variant data. Context state includes coded/decoded formats, controls, image format, COLMV offset, RCB configuration, and codec-private state. All is volatile kernel driver state.

Dependencies and integration points: depends on platform/OF, clocks, PM runtime, IOMMU, gen_pool SRAM, V4L2 mem2mem/media controller, videobuf2 DMA-contig, stateless codec controls, and codec backend ops declared in `rkvdec.h`.

Risks: format/control state is tightly coupled; image-format-changing controls reject busy capture queues. Watchdog writes the legacy interrupt register even for newer variants, so variant behavior should be checked. Multicore support intentionally exposes only the first compatible node. IRQ handlers contain unused `need_reset` variables and different IOMMU-restore policies. RCB lifetime is tied to streaming start/stop.

Test signals: module probe/remove on rk3288/rk3328/rk3399/rk3588/rk3576 compatibles, v4l2-compliance for mem2mem/request API, H.264/HEVC/VP9 decode conformance, runtime PM suspend/resume during idle and active jobs, IRQ timeout/error paths, and SRAM/IOMMU configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec.h

Purpose: central internal header for the Rockchip RKVDEC driver. It defines device/context structures, coded/decoded format descriptors, codec operation interfaces, variant operation interfaces, decoded buffer metadata, allocation records, and exported helpers shared by core and codec backends.

Important APIs and types: `struct rkvdec_dev`, `struct rkvdec_ctx`, `struct rkvdec_variant`, `struct rkvdec_variant_ops`, `struct rkvdec_coded_fmt_ops`, `struct rkvdec_coded_fmt_desc`, `struct rkvdec_decoded_fmt_desc`, `struct rkvdec_run`, `struct rkvdec_decoded_buffer`, `enum rkvdec_image_fmt`, `enum rkvdec_alloc_type`, and `struct rkvdec_aux_buf`. It declares codec ops for legacy, VDPU381, VDPU383, and VP9 backends.

Control flow: core code creates `rkvdec_ctx`, selects a `coded_fmt_desc`, invokes codec ops through `rkvdec_coded_fmt_ops`, and exposes helper functions for backends to acquire buffers, copy registers, schedule watchdogs, and apply quirks.

State and persistence: no state is allocated by the header, but it defines all major in-memory state contracts. Device state persists for the platform-device lifetime; context state persists for file-handle lifetime; codec-private and RCB state persists for streaming lifetime.

Dependencies and integration points: includes Linux platform/video/clock/wait headers, V4L2 controls/device/ioctl/mem2mem, and vb2 DMA-contig. It integrates every file in the RKVDEC driver directory.

Risks: this header is a broad coupling point; changes to context, variant, or ops structures affect multiple codec implementations. `ctx->priv` is untyped and requires correct start/stop pairing. Bitfield flags `has_sps_st_rps` and `has_sps_lt_rps` are set by control changes and consumed by HEVC backends.

Test signals: full RKVDEC build coverage, sparse/compiler warnings for structure changes, and runtime coverage of every codec ops table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/Kconfig

Purpose: top-level Kconfig include file for Samsung media platform drivers.

Important APIs and symbols: it emits a menu comment and sources child Kconfig files for `exynos-gsc`, `exynos4-is`, `s3c-camif`, `s5p-g2d`, `s5p-jpeg`, and `s5p-mfc`.

Control flow: during kernel configuration, inclusion from the media platform Kconfig tree makes each Samsung subdriver's symbols visible. No runtime code is involved.

State and persistence: selected symbols persist only in the kernel build configuration.

Dependencies and integration points: integrates the Samsung platform media subdirectory into the broader media Kconfig hierarchy. The `exynos-gsc` source line is the entry point for `VIDEO_SAMSUNG_EXYNOS_GSC`.

Risks: adding/removing Samsung subdirectories requires keeping this source list synchronized with the Makefile. Incorrect source paths break menuconfig/allconfig processing.

Test signals: `make menuconfig`, `olddefconfig`, and allmodconfig coverage that reaches every sourced child Kconfig.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/Makefile

Purpose: top-level kbuild dispatcher for Samsung media platform driver subdirectories.

Important APIs and entries: unconditionally descends into `exynos-gsc/`, `exynos4-is/`, `s3c-camif/`, `s5p-g2d/`, `s5p-jpeg/`, and `s5p-mfc/` using `obj-y +=`.

Control flow: kbuild visits each subdirectory; each child Makefile decides whether objects are built based on its Kconfig symbols.

State and persistence: no runtime state. Build output is controlled by child `obj-$(CONFIG_...)` rules.

Dependencies and integration points: must stay aligned with top-level Samsung Kconfig and actual child directories. It is the path by which the exynos-gsc Makefile participates in kernel builds.

Risks: unconditional directory descent is standard but means stale or missing child directories cause build failures. New subdrivers need both Kconfig and Makefile updates.

Test signals: `make drivers/media/platform/samsung/` with different Samsung media configs and allmodconfig.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/Kconfig

Purpose: declares the kernel configuration option for the Samsung Exynos5 G-Scaler V4L2 driver.

Important APIs and symbols: `VIDEO_SAMSUNG_EXYNOS_GSC` is a tristate depending on `V4L_MEM2MEM_DRIVERS`, `VIDEO_DEV`, and `ARCH_EXYNOS || COMPILE_TEST`; it selects `VIDEOBUF2_DMA_CONTIG` and `V4L2_MEM2MEM_DEV`.

Control flow: when enabled, the local Makefile builds `exynos-gsc.o` from core, mem2mem, and register implementation objects.

State and persistence: no runtime state; the selected tristate persists in the kernel configuration and controls whether the driver is built-in, modular, or absent.

Dependencies and integration points: integrates the G-Scaler driver with V4L2 mem2mem, vb2 DMA-contig, and Exynos platform builds while retaining compile-test coverage on other architectures.

Risks: the option only expresses core build dependencies; runtime still needs device-tree nodes, clocks, IRQ, and memory resources. Missing media-controller or PM combinations are caught by broader media dependencies rather than this file.

Test signals: Kconfig visibility on Exynos and COMPILE_TEST builds, `allmodconfig`, and module build of `exynos-gsc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/Makefile

Purpose: defines the object composition for the Exynos G-Scaler driver.

Important APIs and entries: `exynos-gsc-objs := gsc-core.o gsc-m2m.o gsc-regs.o`; `obj-$(CONFIG_VIDEO_SAMSUNG_EXYNOS_GSC) += exynos-gsc.o`.

Control flow: kbuild links the core/probe logic, mem2mem operations, and register programming helpers into one module or built-in object according to the Kconfig symbol.

State and persistence: no runtime state; it controls compilation and link composition.

Dependencies and integration points: depends on declarations shared through `gsc-core.h` and Kconfig dependencies selecting V4L2/vb2 support.

Risks: object list drift can cause unresolved symbols or missing functionality. Because all components link into one object, internal symbol visibility is simple but every added compilation unit must be listed here.

Test signals: module/built-in builds with `CONFIG_VIDEO_SAMSUNG_EXYNOS_GSC=y/m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/gsc-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/gsc-core.c

Purpose: core implementation for the Samsung Exynos5 G-Scaler V4L2 mem2mem driver. It provides format tables, scaling/crop validation, V4L2 controls, DMA address preparation, IRQ handling, SoC variant data, platform probe/remove, and runtime PM.

Important APIs and functions: exported-to-driver helpers include `get_format`, `find_fmt`, `gsc_enum_fmt`, `gsc_try_fmt_mplane`, `gsc_g_fmt_mplane`, `gsc_try_selection`, `gsc_set_scaler_info`, `gsc_ctrls_create/delete`, `gsc_prepare_addr`, and `gsc_set_prefbuf`. Platform lifecycle is handled by `gsc_probe`, `gsc_remove`, runtime suspend/resume, and `gsc_irq_handler`.

Control flow: probe reads OF match data and alias ID, chooses a per-entity variant, maps registers, gets/enables clocks, requests IRQ, registers V4L2 and mem2mem devices, resets hardware, sets DMA segment limits, and enables PM runtime. User format/selection/control operations call this file to clamp dimensions, compute prescaler/main-scaler ratios, maintain context state, and calculate plane payload/DMA addresses. IRQ handling clears frame-done or overrun status, finalizes active m2m jobs, and handles suspend transitions.

State and persistence: device state includes locks, clocks, MMIO base, waitqueue, m2m device, V4L2 device, and variant pointer. Context state includes source/destination frames, crop, scaler ratios, rotation/flip/alpha controls, colorspace, and state flags. Hardware state is reset on probe and runtime resume.

Dependencies and integration points: depends on V4L2/vb2 APIs, platform/OF, clocks, PM runtime, `gsc-core.h`, `gsc-regs.h`, and the sibling `gsc-m2m.c`/`gsc-regs.c` implementation.

Risks: many calculations mutate requested crop/format values to hardware alignment; callers must handle adjusted rectangles. Scaling ratio limits are variant-dependent and can reject rotations differently. Probe enables clocks before PM runtime and must unwind carefully. `gsc_set_prefbuf` only logs computed ranges in this snapshot. IRQ and suspend state depend on spinlock-protected flags.

Test signals: v4l2-compliance for mem2mem, format enumeration/try/set across all supported formats, crop/rotation/scale boundary tests per Exynos variant, IRQ completion/overrun tests, runtime suspend/resume during active and idle queues, and DMA address validation for one-, two-, and three-plane formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/gsc-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/gsc-core.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/gsc-core.h

Purpose: primary internal header for the Exynos G-Scaler driver. It defines constants, flags, color/datapath enums, core structures, inline register helpers, and cross-file function prototypes.

Important APIs and types: key types include `gsc_fmt`, `gsc_frame`, `gsc_addr`, `gsc_ctrls`, `gsc_scaler`, `gsc_m2m_device`, `gsc_pix_max`, `gsc_pix_min`, `gsc_pix_align`, `gsc_variant`, `gsc_driverdata`, `gsc_dev`, and `gsc_ctx`. It declares format/scaler/control/address helpers, mem2mem registration functions, job finish, and low-level `gsc_hw_*` register functions.

Control flow: `gsc-core.c`, `gsc-m2m.c`, and `gsc-regs.c` share this contract. File handles map to contexts via `file_to_ctx`; V4L2 controls map via `ctrl_to_ctx`; queue and hardware programming paths use `ctx_get_frame`, state helpers, and register inlines.

State and persistence: the header defines but does not allocate device/context state. Device state persists for the platform instance; context state persists per V4L2 file handle; frame/address/scaler fields are updated during format, selection, and job setup.

Dependencies and integration points: includes Linux delay/sched/spinlock/types/io/PM runtime, V4L2 controls/device/mem2mem/mediabus, vb2 DMA-contig, and `gsc-regs.h`. It is the shared ABI among all exynos-gsc compilation units.

Risks: broad shared structs increase coupling. Inline MMIO helpers directly read/modify/write IRQ and enable registers; callers must hold appropriate state and hardware power. Some comments contain typos and legacy terminology, so code should be treated as authoritative. `GSC_MAX_CLOCKS` and `GSC_MAX_DEVS` bound OF match data.

Test signals: full exynos-gsc build, sparse/compiler warning coverage after struct changes, V4L2 mem2mem runtime tests, and register-programming tests through `gsc-regs.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/gsc-core.h -->

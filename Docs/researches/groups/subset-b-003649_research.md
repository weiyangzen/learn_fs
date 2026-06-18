# subset-b-003649 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_encoder_phys.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_encoder_phys.h

## Purpose
Defines the common physical encoder abstraction used by DPU virtual encoders to drive one output path: video INTF, command INTF, or writeback. It centralizes lifecycle operations, split-display role tracking, shared hardware block pointers, interrupt indexes, wait queues, and pending-kickoff counters used by the concrete `*_vid`, `*_cmd`, and `*_wb` implementations.

## Important APIs, Types, and Functions
Key enums are `dpu_enc_split_role`, `dpu_enc_enable_state`, and `dpu_intr_idx`. `struct dpu_encoder_phys_ops` is the polymorphic vtable for mode set, enable/disable, IRQ control, kickoff waits, writeback job hooks, status reads, and commit validity. `struct dpu_encoder_phys` stores parent DRM encoder, DPU KMS, hardware interfaces (`hw_ctl`, `hw_intf`, `hw_pp`, `hw_wb`, `hw_cdm`), cached mode, vblank locking/refcount, enable state, atomic counters, wait queue, interrupt IDs, and TE capability. Subclasses `dpu_encoder_phys_cmd` and `dpu_encoder_phys_wb` extend the base with command-mode and writeback state. Exported constructors are `dpu_encoder_phys_vid_init`, `dpu_encoder_phys_cmd_init`, and `dpu_encoder_phys_wb_init`; helpers include split config, CWB/CDM setup, IRQ waiting, cleanup, callback dispatch, DSC/format queries, and `dpu_encoder_phys_init`.

## Control Flow and State
The virtual encoder allocates a concrete physical encoder, calls `dpu_encoder_phys_init`, and then drives it through `ops`. Atomic commits increment pending counters with `dpu_encoder_phys_inc_pending`; IRQ callbacks or wait helpers decrement them and wake `pending_kickoff_wq`. `enable_state` is a persistent in-memory lifecycle guard, including `DPU_ENC_ERR_NEEDS_HW_RESET` for timeout recovery. Split roles gate master-only behavior such as vblank reporting.

## Dependencies and Integration Points
This header is tightly integrated with DRM encoder/CRTC state, DPU KMS, CTL/INTF/WB/PP/CDM/TOP hardware wrappers, writeback jobs, and DPU encoder callbacks. `dpu_encoder_helper_get_3d_blend_mode` depends on CRTC mixer count and DSC merge topology.

## Risks and Test Signals
The main risk is stale or mismatched ops/hardware pointers across concrete implementations; many callers assume ops are present only when hardware supports them. Test signals include command/video/writeback modeset, split display master/slave behavior, vblank enable/disable refcounts, pending kickoff drain, timeout recovery, DSC merge, CWB/CDM paths, and suspend/idle power collapse TE handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_encoder_phys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_encoder_phys_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_encoder_phys_cmd.c

## Purpose
Implements command-mode physical encoders for DSI-style panels. It configures CTL/INTF/PP routing, tear-check, command-mode interface compression/widebus flags, external TE connection, vblank emulation through read-pointer IRQs, and kickoff/PP-done synchronization.

## Important APIs, Types, and Functions
The public entry is `dpu_encoder_phys_cmd_init`. The vtable populated by `dpu_encoder_phys_cmd_init_ops` includes `enable`, `disable`, `control_vblank_irq`, `wait_for_commit_done`, `wait_for_tx_complete`, `prepare_for_kickoff`, `trigger_start`, IRQ enable/disable, `restore`, idle power-collapse preparation, and line count. Key helpers are `_dpu_encoder_phys_cmd_update_intf_cfg`, `dpu_encoder_phys_cmd_tearcheck_config`, `_dpu_encoder_phys_cmd_pingpong_config`, `_dpu_encoder_phys_cmd_wait_for_idle`, `_dpu_encoder_phys_cmd_wait_for_ctl_start`, and `_dpu_encoder_phys_cmd_handle_ppdone_timeout`.

## Control Flow and State
Mode set stores IRQ indexes from CTL, PP or INTF TE, and INTF underrun caps. Enable sets split config, programs CTL command-mode topology, binds PP to INTF on DPU 5+, programs command compression/widebus flags, configures tearcheck, and marks `DPU_ENC_ENABLED`. Kickoff preparation waits for previous PP done, resets pending state on timeout, disables autorefresh, and reconnects TE after kickoff. `pending_kickoff_cnt`, `pending_ctlstart_cnt`, `pending_vblank_cnt`, wait queues, and `vblank_refcount` are the key volatile state. Timeout handling snapshots display state, unregisters read-pointer IRQ after selected failures, signals frame error or panel-dead after repeated failures, and requests CTL reset through `enable_state`.

## Dependencies and Integration Points
Uses `dpu_core_irq_register_callback`, PP/INTF tearcheck ops, CTL `setup_intf_cfg`, `bind_pingpong_blk`, encoder frame/vblank/underrun callbacks, tracepoints, `dpu_kms_get_clk_rate("vsync")`, DSC helpers, widebus helpers, and display snapshots. DPU core major version decides whether TE lives on INTF or PP.

## Risks and Test Signals
Risks center on IRQ refcount imbalance, failing to unregister callbacks after timeout, invalid TE source when `has_intf_te` changes by SoC, and stale `pending_kickoff_cnt` causing commit stalls. Tests should cover command-mode panel commits, autorefresh disable, external TE reconnect, split master/slave paths, PP-done timeout recovery, CTL-start wait, DSC command mode, and line-count reads with both PP TE and INTF TE generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_encoder_phys_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_encoder_phys_vid.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_encoder_phys_vid.c

## Purpose
Implements video-mode physical encoders. It translates DRM display modes to INTF timing registers, manages programmable fetch, configures CTL topology for video scanout, handles vblank/underrun IRQs, and controls timing engine enable/disable around atomic kickoff.

## Important APIs, Types, and Functions
The constructor is `dpu_encoder_phys_vid_init`; `dpu_encoder_phys_vid_init_ops` fills the physical encoder vtable. Critical helpers include `drm_mode_to_intf_timing_params`, `programmable_fetch_get_num_lines`, `programmable_fetch_config`, `dpu_encoder_phys_vid_setup_timing_engine`, `dpu_encoder_phys_vid_vblank_irq`, `dpu_encoder_phys_vid_control_vblank_irq`, `dpu_encoder_phys_vid_wait_for_commit_done`, and frame/line count readers.

## Control Flow and State
Mode set records INTF vsync and underrun IRQs. Enable computes format, optional CDM setup, split-display or YUV420 horizontal halving, DP widebus timing shifts, DSC compression timing, INTF timing programming, CTL video topology, PP/INTF binding, merge-3D setup, and pending flush bits for INTF, merge-3D, CDM, and peripheral SDP packets. The timing engine is enabled in `handle_post_kickoff` only after CTL flush, transitioning from `DPU_ENC_ENABLING` to `DPU_ENC_ENABLED`. Disable turns off timing, increments pending counts, waits for vblank latch, optionally waits again if status still says enabled, then calls shared cleanup.

## Dependencies and Integration Points
Depends on DRM mode semantics, `mdp_get_format`, DSC config helpers, INTF ops, CTL ops, merge-3D ops, CDM setup, vblank core IRQ registration, and display snapshots. `dpu_encoder_phys_vid_needs_single_flush` preserves older pre-DPU5 split-display behavior.

## Risks and Test Signals
Timing math is the highest-risk area: split/YUV420 halving, DP widebus porch shifts, DSC data width, and programmable fetch must match hardware. IRQ and pending-flush tests should verify vblank waits, flush register drain, underrun callback, enable/disable latching, DPU4 single-flush split mode, DPU5+ per-block flush, DSC, DP widebus, YUV formats requiring peripheral flush, and frame count adjustment when programmable fetch is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_encoder_phys_vid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_encoder_phys_wb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_encoder_phys_wb.c

## Purpose
Implements writeback physical encoders. It prepares writeback jobs, maps framebuffer layout and addresses, configures WB/CDM/CWB/CTL routing, applies VBIF QoS and outstanding-transaction settings, and waits for WB-done IRQ completion.

## Important APIs, Types, and Functions
The constructor is `dpu_encoder_phys_wb_init`; `dpu_encoder_phys_wb_init_ops` installs writeback-specific encoder ops. Important helpers are `dpu_encoder_phys_wb_prepare_wb_job`, `dpu_encoder_phys_wb_cleanup_wb_job`, `dpu_encoder_phys_wb_setup`, `dpu_encoder_phys_wb_setup_fb`, `dpu_encoder_phys_wb_setup_ctl`, `_dpu_encoder_phys_wb_update_flush`, `dpu_encoder_phys_wb_done_irq`, `dpu_encoder_phys_wb_wait_for_commit_done`, `dpu_encoder_phys_wb_set_ot_limit`, `dpu_encoder_phys_wb_set_qos_remap`, and `dpu_encoder_phys_wb_set_qos`.

## Control Flow and State
Writeback is always considered master. `prepare_wb_job` pins/prepares the framebuffer, derives DPU plane sizes and addresses, records job/connector backpointers, and handles planar Cb/Cr plane swap for selected formats. Pre-kickoff queues the DRM writeback job, configures VBIF, framebuffer output, CDM for YUV, CWB, CTL topology, and pending flush masks. WB-done IRQ sends frame done and vblank callbacks, decrements pending kickoff, signals DRM writeback completion, and wakes commit waiters. Timeouts snapshot once, signal completion anyway, emit frame error, decrement pending count, and set `DPU_ENC_ERR_NEEDS_HW_RESET`.

## Dependencies and Integration Points
Integrates with DRM writeback connector/job APIs, MSM framebuffer prepare/cleanup and IOVA helpers, DPU format helpers, VBIF QoS helpers, catalog performance tables, WB ops, CTL ops, CDM/CWB helpers, merge-3D, and core IRQ registration.

## Risks and Test Signals
Risks include unbalanced framebuffer prepare/cleanup, stale `wb_job` making commits valid incorrectly, format plane-address mistakes for planar/UBWC/YUV output, incorrect RT vs NRT QoS when CWB is active, and missing legacy WB teardown for pre-DPU5 hardware. Tests should cover RGB and YUV writeback, UBWC/tiled layouts, CWB path, WB-done timeout, connector completion signaling, IRQ refcounting, and disable cleanup after active commits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_encoder_phys_wb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_formats.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_formats.c

## Purpose
Computes DPU hardware framebuffer layout metadata from DRM framebuffer state and MSM format descriptors. It validates dimensions and pitches, calculates plane sizes/pitches for linear and UBWC/tiled formats, and maps framebuffer IOVAs into the plane order expected by DPU hardware.

## Important APIs, Types, and Functions
Exports `dpu_format_populate_plane_sizes` and `dpu_format_populate_addrs`. Internal helpers include `_dpu_get_v_h_subsample_rate`, `_dpu_format_populate_plane_sizes_ubwc`, `_dpu_format_populate_plane_sizes_linear`, `_dpu_format_populate_addrs_ubwc`, and `_dpu_format_populate_addrs_linear`. `DPU_UBWC_PLANE_SIZE_ALIGNMENT` enforces 4 KiB plane alignment.

## Control Flow and State
The file is stateless. `dpu_format_populate_plane_sizes` clears `dpu_hw_fmt_layout`, sets image dimensions and format plane count, then chooses UBWC/tile or linear calculations. Linear layouts verify framebuffer pitches are at least the required hardware pitch and use user pitch when larger. UBWC YUV and RGB paths compute bitstream and metadata sizes using format-specific tile sizes, scanline rounding, stride rounding, and an RGB meta-plane quirk where uAPI leaves plane 1 empty and metadata is plane 2. Address population then uses `msm_framebuffer_iova`; UBWC reorders base-address offsets so hardware sees bitstream planes before metadata planes.

## Dependencies and Integration Points
Depends on DRM framebuffer fields, `msm_framebuffer_format`, `msm_framebuffer_iova`, format flags such as `MSM_FORMAT_IS_UBWC`, `MSM_FORMAT_IS_TILE`, `MSM_FORMAT_IS_YUV`, `MSM_FORMAT_IS_DX`, and DPU max image limits from the catalog header. Writeback setup consumes both sizes and addresses.

## Risks and Test Signals
Layout errors lead directly to memory corruption or wrong scanout/writeback content. Risks include unsupported odd dimensions for subsampled formats, DX tight-unpack stride math, RGB UBWC plane count adjustment, YUV metadata offsets, and pitch acceptance for linear multi-plane buffers. Tests should validate known-good offsets and total sizes for RGB linear, NV12/P010 linear, UBWC RGB, UBWC NV12-like formats, oversized dimension rejection, and undersized pitch rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_formats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_formats.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_formats.h

## Purpose
Declares the DPU format helper API and provides a small inline helper for checking whether a DRM fourcc appears in a supported-format table.

## Important APIs, Types, and Functions
`dpu_find_format` linearly searches a `u32` format array and returns true on exact match. `dpu_format_populate_addrs` fills plane IOVA addresses in `struct dpu_hw_fmt_layout`, and `dpu_format_populate_plane_sizes` fills layout dimensions, pitches, sizes, plane count, and total size.

## Control Flow and State
There is no persistent state. The inline lookup is intentionally simple and is used by resource and format validation paths that already hold catalog-backed arrays. The implementation functions declared here operate on caller-provided DRM framebuffer and DPU layout structures.

## Dependencies and Integration Points
Includes DRM fourcc definitions, MSM GEM/framebuffer declarations, and `dpu_hw_mdss.h` for layout types. It is consumed by writeback setup, plane validation, and other DPU paths that need DPU-specific plane layout rather than generic DRM layout.

## Risks and Test Signals
The main header-level risk is passing an incorrect `num_formats` or unsynchronized catalog format table; the helper cannot detect malformed arrays. Tests should check format validation against VIG/DMA/WB catalog format lists and ensure callers handle false results before programming hardware. ABI-sensitive tests should confirm layout helper outputs remain compatible with DRM framebuffer pitch/address expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_formats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_catalog.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_catalog.c

## Purpose
Defines shared static DPU catalog data used by SoC-specific catalog fragments: feature masks, supported formats, SSPP sub-block templates, mixer/DSPP/pingpong/DSC/CDM/VBIF/performance tables, and includes every supported SoC catalog header.

## Important APIs, Types, and Functions
This file has no runtime functions. Its important artifacts are feature-mask macros such as `VIG_MASK`, `DMA_SDM845_MASK_*`, `WB_SDM845_MASK`, format arrays `plane_formats`, `plane_formats_yuv`, `rotation_v2_formats`, `wb2_formats_rgb_yuv`, sub-block constructors such as `_VIG_SBLK`, `_VIG_SBLK_REC0_REC1`, `_DMA_SBLK`, concrete sub-blocks like `dpu_vig_sblk_qseed3_*`, mixer blocks like `sdm845_lm_sblk`, DSPP blocks, pingpong dither blocks, DSC sub-block offsets, CDM configs, VBIF configs, and QoS LUT tables.

## Control Flow and State
State is compile-time constant and consumed through included catalog headers that assemble `struct dpu_mdss_cfg` instances for individual SoCs. The file’s include list at the end pulls in DPU versions from 1.x through 13.x, so changes here can affect many targets.

## Dependencies and Integration Points
Used by `dpu_hw_catalog.h` consumers, DPU KMS initialization, hardware block initializers, resource allocation, format validation, performance/QoS programming, VBIF programming, and encoder paths that depend on core version, CDM presence, CWB presence, DSC blocks, interface counts, and feature bits.

## Risks and Test Signals
Because this is shared metadata, a wrong offset, feature bit, format list, or QoS LUT can break unrelated SoCs. Tests should boot/probe each affected catalog, validate block counts and base ranges, check format exposure, exercise scaling/rotation/CDM/WB/CWB feature bits, and compare register programming against hardware documentation. Static review should ensure SoC headers include compatible shared sub-block structures and that new DPU major versions get correct CTL/INTF/IRQ behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_catalog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_catalog.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_catalog.h

## Purpose
Defines the typed data model for DPU hardware catalogs. Hardware discovery and resource allocation use these structures to describe capabilities, block offsets, feature bits, interrupts, format tables, QoS/performance limits, and SoC configuration instances.

## Important APIs, Types, and Functions
Important constants include `MAX_BLOCKS`, `DPU_MAX_IMG_WIDTH`, `DPU_MAX_IMG_HEIGHT`, `CRTC_DUAL_MIXERS`, and `MAX_XIN_COUNT`. Feature enums describe SSPP, mixer, DSPP, CTL, WB, VBIF, and DSC capabilities. Key structs are `dpu_caps`, `dpu_sspp_sub_blks`, `dpu_lm_sub_blks`, `dpu_dspp_sub_blks`, `dpu_pingpong_sub_blks`, `dpu_dsc_sub_blks`, `dpu_mdp_cfg`, `dpu_ctl_cfg`, `dpu_sspp_cfg`, `dpu_lm_cfg`, `dpu_pingpong_cfg`, `dpu_dsc_cfg`, `dpu_intf_cfg`, `dpu_wb_cfg`, `dpu_cwb_cfg`, `dpu_vbif_cfg`, `dpu_cdm_cfg`, `dpu_perf_cfg`, and the root `dpu_mdss_cfg`. The header also declares extern catalog instances for supported SoCs.

## Control Flow and State
No runtime state is held here; all structures are immutable descriptions. Runtime initializers copy pointers from `dpu_mdss_cfg` into hardware wrapper objects, and ops availability is frequently gated by `mdss_ver->core_major_ver` or feature bits.

## Dependencies and Integration Points
The header is a dependency for nearly every DPU block: CTL, INTF, CDM, CWB, DSC, DSPP, interrupts, VBIF/perf, resource manager, encoder setup, and format validation. Interrupt indexes stored in catalog entries are later passed into the core IRQ layer.

## Risks and Test Signals
The contract risk is semantic drift: a feature bit can mean a required register path, a max dimension constrains framebuffer validation, and incorrect block lengths/bases lead to invalid MMIO. Tests should include catalog compile coverage, probe-time sanity checks, resource manager topology validation, format-list validation, IRQ index mapping, version-gated ops coverage, and per-SoC display/writeback smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_catalog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_cdm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_cdm.c

## Purpose
Implements the chroma down module hardware wrapper. CDM converts RGB source data to YUV output, optionally performs horizontal/vertical chroma downsampling, configures HDMI packing, and binds CDM input to a pingpong/CWB source on newer DPU generations.

## Important APIs, Types, and Functions
The public constructor is `dpu_hw_cdm_init`. Exposed ops are `dpu_hw_cdm_enable` and, for DPU core major >= 5, `dpu_hw_cdm_bind_pingpong_blk`. Internal `dpu_hw_cdm_setup_cdwn` programs CDWN2 op mode, coefficients, output size, bit depth, and clamp. Fixed coefficient arrays encode cosite/offsite horizontal and vertical downsampling filters.

## Control Flow and State
The wrapper stores only register base, log mask, index, catalog caps, and ops. `enable` validates non-null inputs and requires a YUV output format. It programs CSC coefficients through `dpu_hw_csc_setup`, programs downsampling, sets HDMI pack mode when output type is HDMI, marks CSC destination as YUV, binds the PP source when supported, and writes opmode registers. `bind_pingpong_blk` updates the `CDM_MUX` low nibble, mapping CWB-like pingpongs to a fixed value, normal PPs to zero-based IDs, and none to disabled `0xf`.

## Dependencies and Integration Points
Depends on `dpu_hw_cdm_cfg` from encoder helpers, MSM format metadata, CSC matrix helpers, catalog CDM configs, and CTL/encoder pending flush. Video and writeback encoders call shared CDM setup before flushing CDM.

## Risks and Test Signals
Risks include rejecting non-YUV formats late, unsupported `CHROMA_H1V2` HDMI output, coefficient mismatch, mux programming errors, and output-size/bit-depth inconsistencies. Tests should cover WB YUV output, HDMI/DP YUV paths if present, all downsample enum values, invalid format rejection, DPU4 lack of bind op, DPU5+ PP binding, and register dumps for opmode/coefficient/output-size fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_cdm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_cdm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_cdm.h

## Purpose
Declares the CDM hardware wrapper contract and configuration payload for chroma downsampling, CSC, output format, output target, bit depth, and PP binding.

## Important APIs, Types, and Functions
`struct dpu_hw_cdm_cfg` carries output dimensions, bit depth, horizontal/vertical downsample types, output `msm_format`, CSC config, output type, and PP ID. Enums define downsample type (`CDM_CDWN_DISABLE`, `PIXEL_DROP`, `AVG`, `COSITE`, `OFFSITE`), output target (`HDMI`, `WB`), output bit depth, and hardware method field values. `struct dpu_hw_cdm_ops` exposes `enable` and `bind_pingpong_blk`. `struct dpu_hw_cdm` stores base hardware block, register map, catalog caps, CDM index, and ops. `dpu_hw_cdm_init` constructs the wrapper and `to_dpu_hw_cdm` casts from the generic block.

## Control Flow and State
No persistent policy exists in the header. It defines the state shape that encoder helpers populate and the hardware wrapper consumes. The presence of `bind_pingpong_blk` is generation-gated in the implementation.

## Dependencies and Integration Points
Includes DPU MDSS and top-level hardware definitions and references `struct msm_format`, `struct dpu_csc_cfg`, catalog `dpu_cdm_cfg`, `enum dpu_cdm`, and `enum dpu_pingpong`. Video and writeback encoder setup paths build `dpu_hw_cdm_cfg`.

## Risks and Test Signals
Enum values must remain synchronized with register field encoding in `dpu_hw_cdm.c`. Tests should verify callers populate all dimensions and format fields, that YUV format requirements are enforced, and that unsupported ops are checked before use. Static analysis should catch null `output_fmt` or `csc_cfg` passed through helper paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_cdm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_ctl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_ctl.c

## Purpose
Implements CTL-path hardware operations. CTL coordinates which source pipes, mixers, interfaces, DSC/CDM/WB/CWB/merge-3D/DSPP blocks are active and when their register updates are flushed or started.

## Important APIs, Types, and Functions
The public constructor is `dpu_hw_ctl_init`. Core ops include `trigger_start`, `is_started`, `trigger_pending`, `clear_pending_flush`, `get_pending_flush`, `update_pending_flush*`, `trigger_flush`, `get_flush_register`, `setup_intf_cfg`, `reset_intf_cfg`, `reset`, `wait_reset_status`, `setup_blendstage`, `clear_all_blendstages`, and active pipe/LM setters. Internals map SSPP/LM IDs to flush bits, blend-stage bitfields, and generation-specific v1 active/flush registers.

## Control Flow and State
The wrapper maintains software-cached pending masks: global `pending_flush_mask` plus per-block masks for INTF, WB, CWB, peripheral, merge-3D, DSPP, DSC, and CDM. Callers OR bits through update ops, then `trigger_flush` writes either a legacy single CTL_FLUSH mask or DPU5+ per-block flush registers followed by CTL_FLUSH. `setup_intf_cfg_v1` updates active registers for interface, WB, CWB, DSC, CDM, merge-3D, and group ID; legacy `setup_intf_cfg` packs topology into CTL_TOP. Reset paths write/poll `CTL_SW_RESET`. DPU12+ uses active pipe/LM bitmaps instead of legacy blendstage programming.

## Dependencies and Integration Points
Consumes catalog CTL and mixer configs, MDSS version, DPU enum IDs, tracepoints, and MMIO helpers. Encoders, resource manager, plane setup, writeback, DSC/CDM/CWB, and DSPP color paths all depend on CTL flush semantics.

## Risks and Test Signals
Risks include wrong generation path, stale pending masks after flush, invalid SSPP/LM bit mapping, missing CTL flush bit for mixers, active-register leaks during teardown, and reset polling timeouts. Tests should cover DPU4 legacy flush, DPU5+ per-block flush, DPU7+ DSPP sub-block flush, DPU12+ active pipe/LM path, split display master, WB/CWB teardown through `reset_intf_cfg_v1`, CTL reset recovery, and blend stage programming with multirect/source-split.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_ctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_ctl.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_ctl.h

## Purpose
Declares the CTL hardware wrapper interface and data structures used to configure display/writeback topology, pending flushes, resets, blend stages, and active block bitmaps.

## Important APIs, Types, and Functions
`enum dpu_ctl_mode_sel` distinguishes video and command interface mode. `struct dpu_hw_stage_cfg` maps DPU stages and multirect indexes to SSPP pipes. `struct dpu_hw_intf_cfg` describes CTL output topology: INTF, master INTF, WB, 3D mode, merge-3D, mode select, CDM, stream select, DSC mask, and CWB mask. `struct dpu_hw_ctl_ops` is the main vtable with start/pending/flush/reset/topology/blend/active-pipe operations. `struct dpu_hw_ctl` stores catalog caps, mixer caps, MDSS version, cached pending masks, and ops. `dpu_hw_ctl_init` constructs the wrapper.

## Control Flow and State
The header explicitly separates software-cached pending masks from hardware side effects: most `update_pending_flush*` ops have no immediate hardware effect until `trigger_flush`. This contract matters for encoders that accumulate all flush bits before kickoff. Reset and active topology ops are immediate hardware operations in the implementation.

## Dependencies and Integration Points
Includes DPU MDSS, util, catalog, and SSPP definitions. It is a central dependency for encoders, planes, mixers, DSPP, DSC/CDM/WB/CWB, resource manager, and hardware init code.

## Risks and Test Signals
Caller misuse is the key risk: forgetting `trigger_flush`, using a null generation-gated op, passing enum values outside catalog ranges, or failing to clear pending masks after a failed commit. Tests should assert ops availability for each core major version and verify topology structs are populated consistently for video, command, writeback, DSC merge, and CWB commits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_ctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_cwb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_cwb.c

## Purpose
Implements the concurrent writeback mux wrapper. CWB selects a real-time pingpong source and an input tap point so display output can be captured while scanout continues.

## Important APIs, Types, and Functions
The public constructor is `dpu_hw_cwb_init`. The only op is `dpu_hw_cwb_config`, exposed as `config_cwb`, which programs `CWB_MUX` and `CWB_MODE` using `dpu_hw_cwb_setup_cfg`. `CWB_MUX_MASK` and `CWB_MODE_MASK` define the low-bit fields.

## Control Flow and State
The wrapper stores register base, log mask, index, and ops. Config validates non-null config and input enum range. It defaults mux to disabled `0xf`; if `pp_idx` is a real pingpong, it writes the zero-based PP index into the mux field. It writes the input mode into `CWB_MODE`.

## Dependencies and Integration Points
Uses catalog `dpu_cwb_cfg`, DPU pingpong IDs, and register helpers. Encoder helper CWB setup and writeback setup call this block, while CTL tracks CWB active/flush masks.

## Risks and Test Signals
Risks include accepting an invalid pingpong range, wrong tap point, or failing to disable mux when CWB is not active. Tests should cover LM output and DSPP output input modes, PP_NONE disable behavior, each valid PP index, CWB + WB commit, CWB teardown, and CTL CWB active/flush register pairing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_cwb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_cwb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_cwb.h

## Purpose
Declares the concurrent writeback hardware wrapper, setup payload, input-mode enum, and init/cast helpers.

## Important APIs, Types, and Functions
`enum cwb_mode_input` defines `INPUT_MODE_LM_OUT` and `INPUT_MODE_DSPP_OUT`. `struct dpu_hw_cwb_setup_cfg` carries the real-time pingpong index and input tap point. `struct dpu_hw_cwb_ops` exposes `config_cwb`. `struct dpu_hw_cwb` stores the generic hardware block, register map, CWB index, and ops. `to_dpu_hw_cwb` converts from generic block and `dpu_hw_cwb_init` creates the wrapper.

## Control Flow and State
The header defines only transient configuration and wrapper state. Runtime persistence is limited to the allocated hardware object; CWB mux choices live in registers and are usually coordinated by encoder helper and CTL flush state.

## Dependencies and Integration Points
Includes DPU hardware utility definitions and references `enum dpu_pingpong`, `enum dpu_cwb`, and catalog `dpu_cwb_cfg`. It integrates with writeback and concurrent capture paths.

## Risks and Test Signals
The enum-to-register mapping must remain synchronized with hardware documentation. Tests should check both input modes, invalid input rejection in implementation, PP_NONE behavior, and that callers pair CWB config with CTL CWB active and flush updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_cwb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_dsc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_dsc.c

## Purpose
Implements the original DPU DSC hardware wrapper for display stream compression. It programs DSC encoder registers from DRM DSC config, writes rate-control thresholds and range parameters, disables DSC, and optionally binds DSC output to a pingpong block on DPU5+.

## Important APIs, Types, and Functions
The public constructor is `dpu_hw_dsc_init`. Exposed ops are `dpu_hw_dsc_disable`, `dpu_hw_dsc_config`, `dpu_hw_dsc_config_thresh`, and `dpu_hw_dsc_bind_pingpong_blk`. The config path writes common mode, encoder flags, picture/slice size, chunk size, HRD delay, scale intervals, BPG offsets, flatness thresholds, model size, and RC config. Threshold programming iterates DRM DSC buffer threshold and `rc_range_params` arrays.

## Control Flow and State
The wrapper is stateless apart from register map, index, caps, and ops. `dsc_config` derives command/video initial-line adjustment, slice last group size, input bit depth, and flatness threshold through DRM helpers, then writes registers. `dsc_config_thresh` writes contiguous threshold/minQP/maxQP/BPG register ranges. Binding computes a DSC-specific CTL mux offset and writes either a PP index or disabled value.

## Dependencies and Integration Points
Consumes `struct drm_dsc_config`, DRM DSC helper calculations, catalog DSC config, DPU register helpers, and CTL/encoder DSC topology. Encoders call DSC ops while CTL flushes DSC blocks.

## Risks and Test Signals
Risks include bitfield packing mistakes, command-mode initial-line off-by-one, mismatch with DSC v1.2 wrapper selection, and binding wrong pingpong. Tests should cover RGB/DSI DSC, video vs command mode, split/multiplex flags where supported, threshold table programming, disable, PP bind/unbind, and comparison against panel DSC PPS expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_dsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_dsc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_dsc.h

## Purpose
Declares the DSC hardware wrapper API shared by both legacy and v1.2 implementations.

## Important APIs, Types, and Functions
Mode flags are `DSC_MODE_SPLIT_PANEL`, `DSC_MODE_MULTIPLEX`, and `DSC_MODE_VIDEO`. `struct dpu_hw_dsc_ops` exposes `dsc_disable`, `dsc_config`, `dsc_config_thresh`, and `dsc_bind_pingpong_blk`. `struct dpu_hw_dsc` stores generic block, register map, DSC index, catalog caps, and ops. Constructors are `dpu_hw_dsc_init` and `dpu_hw_dsc_init_1_2`; `to_dpu_hw_dsc` casts from generic hardware block.

## Control Flow and State
The header makes DSC programming a two-step operation: base config and threshold config. Callers must select the correct constructor for the catalog/hardware revision, then invoke ops after clocks are enabled and before CTL flush.

## Dependencies and Integration Points
Includes DRM DSC config definitions and references DPU catalog DSC structures and pingpong IDs. Encoders and topology helpers use this API to program DSC blocks and route compressed output.

## Risks and Test Signals
Risks include callers assuming `dsc_bind_pingpong_blk` exists on all hardware, using legacy constructor on v1.2 hardware, or omitting threshold programming. Tests should verify constructor selection, op presence, mode flag combinations, and DSC + CTL flush integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_dsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_dsc_1_2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_dsc_1_2.c

## Purpose
Implements DSC hardware programming for DPU DSC 1.2-style register layout. It supports newer wrapper/control offsets, native 4:2:0 and 4:2:2 encoding flags, packed threshold registers, and pingpong binding through catalog sub-block offsets.

## Important APIs, Types, and Functions
The public constructor is `dpu_hw_dsc_init_1_2`. Ops are installed by `_setup_dcs_ops_1_2`: `dpu_hw_dsc_disable_1_2`, `dpu_hw_dsc_config_1_2`, `dpu_hw_dsc_config_thresh_1_2`, and `dpu_hw_dsc_bind_pingpong_blk_1_2`. `_dsc_calc_output_buf_max_addr` derives output buffer max address from number of active soft slices and native 42x support.

## Control Flow and State
`dsc_config_1_2` writes common main config for split/multiplex topology, computes active slices per encoder, sets video/command and output-buffer fields, programs DSC version minor, native 420/422, bpp doubling for native 42x, block prediction, RGB conversion, line buffer depth, picture/slice sizes, HRD delays, scale intervals, first/second-line offsets, BPG offsets, flatness, RC model/config, and wrapper enable bits. Threshold programming packs 14 buffer thresholds into four registers and 15 min-QP/max-QP/BPG entries into three registers each. Disable clears wrapper and encoder enable/control registers.

## Dependencies and Integration Points
Uses DRM DSC helpers, catalog `dpu_dsc_sub_blks` offsets, feature bit `DPU_DSC_NATIVE_42x_EN`, DPU register helpers, and the same `dpu_hw_dsc_ops` API as legacy DSC.

## Risks and Test Signals
Native 420/422 bpp scaling and slice multiplex math are high-risk. Tests should include DSC 1.2 panels, native 420/422 when catalog supports it, split-panel and multiplex topologies, command/video mode differences, packed threshold register validation, disable path, and PP bind/unbind through `sblk->ctl.base`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_dsc_1_2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_dspp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_dspp.c

## Purpose
Implements DSPP post-processing hardware operations for panel color correction (PCC) and gamma correction (GC).

## Important APIs, Types, and Functions
The public constructor is `dpu_hw_dspp_init`. Ops may include `dpu_setup_dspp_pcc` and `dpu_setup_dspp_gc` depending on catalog sub-block bases. PCC writes a 3x3 color coefficient matrix and enables/disables PCC. GC writes three 512-entry LUT channels, swaps the LUT, and enables gamma correction with optional 8-bit rounding.

## Control Flow and State
The wrapper stores register base, log mask, DSPP index, catalog cap pointer, and ops. PCC and GC functions validate context and sub-block base. Passing NULL config disables the feature. Non-null PCC writes red/green/blue coefficient triplets then enables. Non-null GC resets channel indexes, streams all LUT entries into channel registers, swaps, and writes enable flags.

## Dependencies and Integration Points
Depends on DSPP catalog sub-block offsets, DPU register helpers, and color-management callers. CTL must flush DSPP or DSPP sub-blocks for programmed changes to latch; DPU7+ uses sub-block flush masks for PCC/GC.

## Risks and Test Signals
Risks include LUT length mismatch, missing CTL DSPP flush, null catalog sub-blocks, and programming PCC/GC when clocks are off. Tests should cover enabling/disabling PCC, GC LUT programming, 8-bit rounding flag, catalog targets with only PCC or both PCC/GC, CTL DSPP flush behavior, and visual/color checksum validation such as MISR or known color ramps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_dspp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_dspp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_dspp.h

## Purpose
Declares DSPP color-processing structures and ops for PCC and GC.

## Important APIs, Types, and Functions
`struct dpu_hw_pcc_coeff` and `struct dpu_hw_pcc_cfg` model per-channel PCC coefficients. Constants `DPU_GAMMA_LUT_SIZE`, `PGC_TBL_LEN`, and `PGC_8B_ROUND` define gamma LUT sizing and flags. `struct dpu_hw_gc_lut` carries three 512-entry LUT channels plus flags. `struct dpu_hw_dspp_ops` exposes `setup_pcc` and `setup_gc`. `struct dpu_hw_dspp` stores generic block, register map, DSPP index, catalog cap, and ops. `dpu_hw_dspp_init` creates the wrapper.

## Control Flow and State
The header defines only caller-provided configuration and allocated wrapper state. Passing NULL configs to ops disables the corresponding feature in the implementation.

## Dependencies and Integration Points
DSPP catalog entries decide whether ops are assigned. CTL DSPP flush APIs and DRM color-management paths are the main consumers.

## Risks and Test Signals
The main API risks are LUT size assumptions and callers using unassigned ops on catalog entries without the sub-block. Tests should validate PCC coefficient writes, GC LUT length and round flag, disabled feature handling, and CTL flush pairing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_dspp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_interrupts.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_interrupts.c

## Purpose
Implements DPU core interrupt register mapping, IRQ dispatch, callback registration, enable/disable masking, preinstall/uninstall cleanup, status reads, and debugfs reporting.

## Important APIs, Types, and Functions
Public APIs include `dpu_hw_intr_init`, `dpu_core_irq`, `dpu_core_irq_read`, `dpu_core_irq_register_callback`, `dpu_core_irq_unregister_callback`, `dpu_core_irq_preinstall`, `dpu_core_irq_uninstall`, and debugfs `dpu_debugfs_core_irq_init`. Static interrupt register tables cover legacy DPU <=6.x, DPU >=7.x, and DPU >=13.x layouts. Helpers include `dpu_core_irq_is_valid`, `dpu_core_irq_get_entry`, `dpu_core_irq_callback_handler`, `dpu_hw_intr_enable_irq_locked`, `dpu_hw_intr_disable_irq_locked`, `dpu_clear_irqs`, and `dpu_disable_all_irqs`.

## Control Flow and State
`dpu_hw_intr_init` selects the register table by core major version, anchors MMIO at MDP base, and builds `irq_mask` from top interrupts plus catalog INTF and tear interrupts. The top IRQ handler locks `irq_lock`, scans enabled register groups, reads status and enable masks, clears raw status, masks disabled bits, dispatches each set bit to its registered callback, and writes a memory barrier. Registration stores one callback/arg per IRQ index, clears pending status, enables the bit in cached mask and hardware, and rejects busy entries. Unregister disables and clears the bit, then clears callback state. Atomic counts track dispatches.

## Dependencies and Integration Points
Used by DPU KMS IRQ install path and all encoder/PP/INTF/WB users that register callbacks. Relies on catalog interrupt indexes, DPU IRQ index macros, MMIO helpers, runtime PM during preinstall/uninstall, tracepoints, and debugfs.

## Risks and Test Signals
Risks include wrong register table for a core version, catalog IRQ indexes outside supported registers, single-callback conflicts, unregistering while IRQ fires, and callbacks running under `irq_lock`. Tests should exercise each register layout, INTF tear IRQs, register/unregister error paths, spurious IRQs with no callback, status read clearing, debugfs counts, suspend/resume preinstall/uninstall, and concurrent callback registration protection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_interrupts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_interrupts.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_interrupts.h

## Purpose
Declares DPU interrupt register-group IDs, IRQ index encoding helpers, interrupt table storage, and the hardware interrupt init API.

## Important APIs, Types, and Functions
`enum dpu_hw_intr_reg` defines top, INTF, tear, and AD4 interrupt register groups and must stay synchronized with implementation tables. `MDP_INTFn_INTR`, `DPU_IRQ_IDX`, `DPU_IRQ_REG`, and `DPU_IRQ_BIT` encode and decode 1-based global IRQ indexes. `DPU_NUM_IRQS` is `MDP_INTR_MAX * 32`. `struct dpu_hw_intr_entry` stores one callback, argument, and atomic count. `struct dpu_hw_intr` stores register map, cached masks, optional status storage, lock, active register mask, selected register table, and callback table. `dpu_hw_intr_init` constructs the object.

## Control Flow and State
The header establishes that IRQ callbacks are indexed by a synthetic 1-based ID rather than Linux IRQ numbers. `cache_irq_mask` mirrors hardware enable registers and is protected by `irq_lock`.

## Dependencies and Integration Points
Includes DPU hardware IO, catalog, util, and MDSS definitions. Encoders obtain interrupt IDs from catalog caps and pass them to `dpu_core_irq_*` implementation APIs.

## Risks and Test Signals
Changing enum order breaks every encoded interrupt index and table lookup. Tests should verify `DPU_IRQ_IDX/REG/BIT` round trips, catalog interrupt IDs point at nonzero table entries, and new register groups are added to both enum and implementation tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_interrupts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_intf.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_intf.c

## Purpose
Implements DPU interface/timing-engine hardware operations: timing generator programming, timing enable, programmable fetch, PP mux binding, status counters, MISR, DSI command-mode tearcheck, autorefresh disable, vsync source selection, watchdog timer setup, and command-mode datapath flags.

## Important APIs, Types, and Functions
The public constructor is `dpu_hw_intf_init`. Core ops are `dpu_hw_intf_setup_timing_engine`, `dpu_hw_intf_enable_timing_engine`, `dpu_hw_intf_setup_prg_fetch`, `dpu_hw_intf_bind_pingpong_blk`, `dpu_hw_intf_get_status`, `dpu_hw_intf_get_line_count`, `dpu_hw_intf_setup_misr`, `dpu_hw_intf_collect_misr`, `dpu_hw_intf_enable_te`, `dpu_hw_intf_disable_te`, `dpu_hw_intf_connect_external_te`, `dpu_hw_intf_vsync_sel`, `dpu_hw_intf_vsync_sel_v8`, `dpu_hw_intf_disable_autorefresh`, and `dpu_hw_intf_program_intf_cmd_cfg`.

## Control Flow and State
Timing setup calculates hsync/vsync periods, display and active windows, polarity, panel format, data-valid window, widebus and DSC flags, and DP-specific timing adjustments, then writes INTF registers. DPU5+ gets `INTF_CONFIG2` data timing and compression/widebus registers. Programmable fetch toggles bit 31 of `INTF_CONFIG` and writes a start counter. Status reads use `INTF_STATUS` on DPU5+ or timing enable on older cores, then frame/line counters only when enabled. TE setup programs vsync counter, height, init, thresholds, read pointer IRQ, and start position. Autorefresh disable temporarily disconnects external TE, clears autorefresh, polls write pointer outside active lines, then reconnects TE.

## Dependencies and Integration Points
Consumes catalog INTF caps and MDSS version, MSM format bit depths, DPU tearcheck structs, PP vsync info, vsync source config, MISR helpers, tracepoints, and encoder timing/TE setup. Command and video physical encoders rely on these ops.

## Risks and Test Signals
High-risk areas are timing math, DP special casing, DSC/widebus data window programming, TE/autorefresh sequencing, and generation-gated ops. Tests should cover DSI video, DSI command TE, DP widebus, DSC DSI data compression, programmable fetch, frame/line counters, MISR signature collection, watchdog vsync source on DPU8, INTF_NONE skip, PP binding, and autorefresh disable timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_intf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_intf.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_intf.h

## Purpose
Declares the DPU INTF hardware wrapper API, timing parameter structures, status/config payloads, and init function.

## Important APIs, Types, and Functions
`struct dpu_hw_intf_timing_params` describes active panel size, programmed width/height, porches, sync widths, polarity, colors, skew, widebus, compression, and compressed bytes per line. `struct dpu_hw_intf_prog_fetch` carries fetch enable and start counter. `struct dpu_hw_intf_status` reports timing enable, programmable fetch enable, frame count, and line count. `struct dpu_hw_intf_cmd_mode_cfg` carries command-mode compression and widebus flags. `struct dpu_hw_intf_ops` exposes timing, fetch, status, PP binding, MISR, tearcheck, vsync selection, autorefresh disable, and command-mode config ops. `struct dpu_hw_intf` stores register map, INTF index, catalog cap, MDSS version, and ops. `dpu_hw_intf_init` constructs the wrapper.

## Control Flow and State
The header’s ops assume clocks are enabled and the caller coordinates CTL flush/start. Ops are generation- and interface-type-gated in implementation: PP binding appears on DPU5+, tearcheck only for DPU5+ DSI, command config on DPU7+.

## Dependencies and Integration Points
Depends on catalog, MDSS, utility types, `struct msm_format`, `struct dpu_hw_tear_check`, `struct dpu_hw_pp_vsync_info`, and `struct dpu_vsync_source_cfg`. It is consumed by command/video physical encoders and diagnostics.

## Risks and Test Signals
Callers must handle optional ops and must pass coherent timing parameters after split, widebus, and DSC adjustments. Tests should assert op availability by core major/interface type, validate timing params from video encoder, and verify command-mode TE paths use INTF ops only when advertised.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_intf.h -->

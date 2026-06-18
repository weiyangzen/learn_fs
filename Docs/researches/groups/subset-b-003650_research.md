# subset-b-003650 research

Grouped research for Qualcomm MSM DPU hardware block wrappers, KMS setup, and plane programming under `sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_lm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_lm.c

## Purpose
Implements the DPU layer mixer hardware wrapper. It programs mixer output size, split-left/right mode, border color, alpha blending, v12+ SSPP-to-blend-stage routing, color3 alpha output, and LM MISR capture.

## Important APIs, types, and functions
- `dpu_hw_lm_init()` allocates a `struct dpu_hw_mixer`, binds it to a catalog `dpu_lm_cfg`, and installs version-specific `dpu_hw_lm_ops`.
- `_stage_offset()` maps a logical `enum dpu_stage` to catalog blend-stage register offsets.
- `dpu_hw_lm_setup_out()` writes `LM_OUT_SIZE` and split output bit 31 in `LM_OP_MODE`.
- `dpu_hw_lm_setup_blend_config*()` covers legacy separate FG/BG alpha, v4+ combined alpha, and v12+ combined alpha layouts.
- `dpu_hw_lm_setup_blendstage()` and `dpu_hw_lm_clear_all_blendstages()` are v12+ source-selection paths.

## Control flow
Initialization skips catalog mixers without pingpong blocks, allocates devres-backed state, sets the MMIO base to `addr + cfg->base`, and chooses ops based on `mdss_ver->core_major_ver`. Pre-v4 uses separate alpha registers; v4-v11 uses combined alpha at the legacy offset; v12+ uses the newer constant-alpha and source-selection layout.

Runtime programming is direct MMIO. Mixer output setup preserves existing `LM_OP_MODE` bits except the right-mixer split bit. Blend setup returns early for base stage, validates stage offsets, then writes constant alpha and blend op registers. V12+ blend-stage setup derives one or two staged SSPP source selectors per stage, translating VIG/DMA IDs and multirect record IDs into SWI source values.

## State and persistence
The wrapper stores only catalog pointers, MMIO base, index, and ops in `struct dpu_hw_mixer`; persistent display state is in hardware registers until the next modeset/commit or power reset. `ctx->cfg` can cache display-specific mixer configuration for higher layers.

## Dependencies and integration points
Depends on `dpu_hw_catalog.h` for mixer topology, `dpu_hw_mdss.h` enums, `dpu_hw_util` MMIO/MISR helpers, and `dpu_kms.h` logging. The resource manager creates mixers during KMS hardware init, and CRTC/encoder paths use the ops to stage planes into LMs and program split-display output.

## Risks
Stage indexing is catalog-sensitive; invalid `maxblendstages` or stage bases cause `-EINVAL` or WARN paths. V12+ `_set_staged_sspp()` accepts only DMA and VIG pipes, so new SSPP types need explicit translation. Alpha bit shifts differ by generation, making version gating important. Source-split stages can silently misroute content if multirect indexes are wrong.

## Test signals
Useful signals are atomic state dumps showing stage allocation, visual plane ordering/blending, split display behavior, border color fallback, and MISR values from `setup_misr`/`collect_misr`. Register debugfs for LM blocks and DRM atomic logs help validate written blend/source registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_lm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_lm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_lm.h

## Purpose
Declares the layer mixer abstraction used by DPU display code to configure mixer output, stage blending, border color, and MISR collection.

## Important APIs, types, and functions
- `struct dpu_hw_mixer_cfg` carries output dimensions, right-mixer flag, and flags.
- `struct dpu_hw_lm_ops` defines mixer operations: output setup, blend config, alpha output, v12+ blend-stage routing, border color, MISR setup, and MISR collection.
- `struct dpu_hw_mixer` embeds the opaque hardware block, register map, catalog pointers, ops, and cached display config.
- `to_dpu_hw_mixer()` converts a generic `dpu_hw_blk` to the mixer container.
- `dpu_hw_lm_init()` is the constructor.

## Control flow
This header has no runtime control flow. It defines function-pointer contracts that callers use only after clocks are enabled, with implementation-selected ops based on hardware version.

## State and persistence
The header defines in-memory wrapper state, not hardware persistence. Hardware state is programmed through the ops and remains in MMIO registers.

## Dependencies and integration points
It includes MDSS common definitions and utility register map definitions. It is consumed by KMS/resource-manager code and CRTC/encoder plane staging code that needs an abstract mixer independent of register generation.

## Risks
Ops are optional by generation; callers must check function pointers for v12-only blend-stage APIs. Header changes affect multiple DPU blocks because mixer objects are central to plane composition.

## Test signals
Build coverage catches signature mismatches. Runtime validation comes from successful CRTC commits with correct z-order, alpha blending, split display, and MISR debug reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_lm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_mdss.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_mdss.h

## Purpose
Provides common DPU/MDSS identifiers, blend bit definitions, format layout structures, CSC structures, color structs, debug masks, tear-check config, and pingpong vsync info shared across DPU hardware wrapper files.

## Important APIs, types, and functions
- Hardware block enums: `dpu_hw_blk_type`, `dpu_sspp`, `dpu_lm`, `dpu_ctl`, `dpu_pingpong`, `dpu_merge_3d`, `dpu_intf`, `dpu_wb`, `dpu_cwb`, and others.
- Composition enums: `dpu_stage`, `dpu_3d_blend_mode`, `dpu_intf_type`, and `dpu_intf_mode`.
- Data structures: `dpu_hw_fmt_layout`, `dpu_csc_cfg`, `dpu_mdss_color`, `dpu_hw_tear_check`, and `dpu_hw_pp_vsync_info`.
- Constants define CSC array sizes, plane/stage limits, blend flags, and debug log masks.

## Control flow
The file is declarative. It shapes how other C files translate DRM state and catalog topology into hardware block IDs and register bitfields.

## State and persistence
No state is stored here. The structures declared here are embedded in plane state, writeback config, pingpong setup, and CSC programming objects elsewhere.

## Dependencies and integration points
It depends on MSM driver and MDP format headers. Nearly every DPU hardware wrapper includes it for common enums and shared programming structures; KMS, plane, pingpong, writeback, LM, top, and VBIF code all rely on the numeric enum ranges matching catalog data and register encodings.

## Risks
Enum numeric values are ABI-like inside the driver: many arrays index by `SSPP_*`, `PINGPONG_*`, or `LM_*` ranges, and register encodings rely on stable values. Adding a block or reordering enums can break array sizing, source routing, debug status decoding, or resource-manager mappings. Several comments contain historical semantics for interface types that newer hardware may ignore but callers still preserve.

## Test signals
Compile coverage catches structural drift, while runtime signals include correct resource allocation, debug status decoding, DSI/DP/WB interface selection, tear-check setup, CSC programming, and absence of out-of-bounds status array use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_mdss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_merge3d.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_merge3d.c

## Purpose
Implements the small hardware wrapper for DPU merge_3d blocks, which combine left/right or stereo streams according to a 3D blend mode.

## Important APIs, types, and functions
- `dpu_hw_merge_3d_init()` allocates and initializes a `struct dpu_hw_merge_3d`.
- `dpu_hw_merge_3d_setup_3d_mode()` writes `MERGE_3D_MODE` and, for disable, `MERGE_3D_MUX`.
- `_setup_merge_3d_ops()` installs the single setup callback.

## Control flow
Initialization is devres-backed, binds the register base to `addr + cfg->base`, stores catalog `id` and caps, and installs ops. Runtime setup clears both mode and mux for `BLEND_3D_NONE`; otherwise it enables bit 0 and encodes `(mode_3d - 1)` starting at bit 1.

## State and persistence
Wrapper state is limited to MMIO base, block index, catalog pointer, and ops. Hardware mode persists in merge_3d registers until changed, power-cycled, or reset.

## Dependencies and integration points
Depends on catalog data, MDSS blend-mode enum, and DPU MMIO helpers. Pingpong and encoder/resource-manager paths associate merge_3d blocks with pingpong/output composition for dual-pipe or 3D modes.

## Risks
The function assumes `mode_3d` is a valid enum value; out-of-range values would be encoded directly. The block uses `DPU_DBG_MASK_PINGPONG`, so debug filtering groups it with pingpong rather than a distinct merge mask.

## Test signals
Validation is visual and register-based: correct dual-pipe merge behavior, no stale mux state after disabling 3D, and debugfs/snapshot reads showing expected `MERGE_3D_MODE` and `MERGE_3D_MUX` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_merge3d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_merge3d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_merge3d.h

## Purpose
Declares the merge_3d hardware object and operation used to configure 3D merge mode for DPU output composition.

## Important APIs, types, and functions
- `struct dpu_hw_merge_3d_ops` exposes `setup_3d_mode()`.
- `struct dpu_hw_merge_3d` stores the base block, register map, block index, catalog caps, and ops.
- `to_dpu_hw_merge_3d()` converts from generic hardware block to the merge_3d wrapper.
- `dpu_hw_merge_3d_init()` constructs the block.

## Control flow
No runtime control flow exists in the header. Callers use the function pointer after clocks are enabled.

## State and persistence
The header defines wrapper state only; merge mode persists in hardware registers programmed by the implementation.

## Dependencies and integration points
Includes catalog, MDSS, and utility headers. It is integrated by the resource manager and pingpong/encoder output paths that need a merge block near the final output pipeline.

## Risks
The API is intentionally narrow. Any future merge feature, mux selection, or validation would require expanding the ops while preserving existing users.

## Test signals
Build coverage validates the constructor and ops signature. Runtime testing is covered by merge_3d programming in dual-pipe or 3D-output modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_merge3d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_pingpong.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_pingpong.c

## Purpose
Implements DPU pingpong block operations for command-mode tear-check, autorefresh handling, line-count reads, dither setup, and older-generation DSC glue.

## Important APIs, types, and functions
- `dpu_hw_pingpong_init()` constructs the block and installs generation-specific ops.
- Tear-check functions: `dpu_hw_pp_enable_te()`, `dpu_hw_pp_disable_te()`, `dpu_hw_pp_connect_external_te()`, `dpu_hw_pp_get_line_count()`, and `dpu_hw_pp_disable_autorefresh()`.
- Dither path: `dpu_hw_pp_setup_dither()` and `dither_depth_map`.
- DSC path: `dpu_hw_pp_setup_dsc()`, `dpu_hw_pp_dsc_enable()`, and `dpu_hw_pp_dsc_disable()`.

## Control flow
Initialization installs tear-check/autorefresh ops only for MDSS core versions below 5, older DSC ops below 7, and dither support for core versions 3 and newer. Tear-check enable writes vsync counter, sync height, init, IRQ, start position, thresholds, and finally enables the block. External TE toggles bit 20 in `PP_SYNC_CONFIG_VSYNC` and returns the original state. Autorefresh disable temporarily disconnects external TE, clears autorefresh, polls write-pointer line count until frame transfer is outside the active display area or timeout, then reconnects TE.

## State and persistence
The wrapper stores MMIO base, pingpong index, catalog caps, optional merge_3d pointer, and ops. Programmed state persists in pingpong registers: TE settings, autorefresh bit/count, dither matrix, DSC mode, and line counters.

## Dependencies and integration points
Depends on MDSS structures, register helpers, KMS timeout constants, tracepoints, and catalog sub-block offsets. Encoder command-mode code uses tear-check and autorefresh paths; output/DSC code uses DSC ops on older hardware; post-processing uses dither.

## Risks
Dither bit-depth indexes are used directly into a 9-element table, so callers must pass valid bit depths. Autorefresh disable is timing-sensitive and logs but does not hard-fail on timeout. The PP dither matrix loop writes offsets using `i` increments, which matches existing register packing but is sensitive to matrix size assumptions. Ops availability varies by core version, so callers must check function pointers.

## Test signals
Signals include command-mode panel TE stability, autorefresh disable logs, line-count reads during commits, DSC enablement on pre-v7 cores, visual dithering, and pingpong register snapshots. Tracepoint `trace_dpu_pp_connect_ext_te` captures TE mux changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_pingpong.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_pingpong.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_pingpong.h

## Purpose
Declares the pingpong hardware wrapper and ops for tear-check, autorefresh, dither, and DSC setup.

## Important APIs, types, and functions
- `struct dpu_hw_dither_cfg` carries bit depths, temporal enable, flags, and a 16-entry dither matrix.
- `struct dpu_hw_pingpong_ops` exposes tear-check, external TE, line count, autorefresh disable, dither, and DSC callbacks.
- `struct dpu_hw_pingpong` stores base block, register map, index, caps, optional merge_3d pointer, and ops.
- `to_dpu_hw_pingpong()` and `dpu_hw_pingpong_init()` provide conversion and construction.

## Control flow
The header is declarative. Runtime control is in the implementation and gated by hardware generation through optional ops.

## State and persistence
It defines in-memory wrapper state and configuration structures. Hardware state is held in pingpong registers after ops execute.

## Dependencies and integration points
Includes catalog, MDSS, and utility headers, and forward declares `struct dpu_hw_merge_3d` to associate final composition blocks. Encoder, CRTC, and resource-manager code use the declared object.

## Risks
Several ops can be NULL on newer or older hardware. The dither config does not validate bit-depth bounds in the type system, so implementation-side callers must use supported values.

## Test signals
Build validation covers signatures. Runtime signals include command-mode TE behavior, dither output, DSC programming, and register/debug snapshots for pingpong blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_pingpong.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_sspp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_sspp.c

## Purpose
Implements pre-v13 Source Surface Processing Pipe hardware operations for scanout format, rectangles, source addresses, multirect, pixel extension, scaling, CSC, solid fill, QoS, CDP, and clock force control.

## Important APIs, types, and functions
- `dpu_hw_sspp_init()` creates the hardware pipe and chooses v13 or legacy ops.
- Format path: `dpu_hw_sspp_setup_format()` and shared `dpu_hw_setup_format_impl()`.
- Geometry/address path: `dpu_hw_sspp_setup_rects()`, `dpu_hw_sspp_setup_sourceaddress()`, and inline helper from the header.
- Processing path: `dpu_hw_sspp_setup_pe_config()`, `dpu_hw_sspp_setup_scaler3()`, `dpu_hw_sspp_setup_csc()`, and `dpu_hw_sspp_setup_solidfill()`.
- QoS path: `dpu_hw_sspp_setup_qos_lut()`, `dpu_hw_sspp_setup_qos_ctrl()`, `dpu_hw_sspp_setup_cdp()`, and clock force control.

## Control flow
Legacy ops select REC0 or REC1 register offsets based on `pipe->multirect_index`. Format setup programs UBWC fetch config for non-linear fetch modes, builds source format from `msm_format`, applies flips/rotation/solid-fill bits, writes UBWC static control according to UBWC version, enables CSC opmode for YUV, and clears previous UBWC error. Source-address setup either writes all planes in solo mode or interleaves addresses/pitches between RECT0 and RECT1 for multirect. Pixel extension writes per-component overfetch/repeat and total request pixels. The debugfs initializer creates feature, register-range, xin, and clock-control entries.

## State and persistence
Wrapper state includes UBWC config pointer, hardware index, catalog caps, MDSS version, MMIO base, and ops. Programmed source addresses, formats, scalers, QoS LUTs, and multirect registers persist until the next plane update, disable, or hardware reset.

## Dependencies and integration points
Depends on DPU catalog feature bits, MDSS enums, `dpu_hw_util` scaler/CSC/QoS/CDP helpers, MSM format descriptors, UBWC config, and debugfs. `dpu_plane.c` is the primary caller during atomic updates; resource manager owns pipe allocation.

## Risks
Multirect pitch/address sharing is easy to corrupt if RECT0/RECT1 indexes are wrong. UBWC version handling must track new hardware encodings; unsupported versions only warn and write zero control. Pixel extension writes `lr_pe[3]` to the C3 TB register in this version, which is a sensitive programming detail. Callers must not use ops absent from feature-gated pipes.

## Test signals
Use DRM atomic plane tests for scaling, rotation, YUV, UBWC, solid fill, and multirect. Debugfs `sspp/*/src_blk`, scaler, and CSC dumps, UBWC error status clearing, visual output, and bandwidth/QoS tracepoints validate programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_sspp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_sspp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_sspp.h

## Purpose
Declares the SSPP pipe abstraction, multirect modes, scaler/pixel-extension support types, software pipe configuration, and operation table used by plane programming.

## Important APIs, types, and functions
- Flags: `DPU_SSPP_FLIP_LR`, `DPU_SSPP_FLIP_UD`, `DPU_SSPP_SOURCE_ROTATED_90`, `DPU_SSPP_ROT_90`, and `DPU_SSPP_SOLID_FILL`.
- Multirect enums define solo, rect0, rect1 and none/parallel/time-multiplex modes.
- `struct dpu_hw_pixel_ext`, `dpu_sw_pipe_cfg`, `dpu_hw_pipe_ts_cfg`, and `dpu_sw_pipe` model per-plane programming.
- `struct dpu_hw_sspp_ops` exposes format, rect, PE, address, CSC, solid fill, multirect, QoS, clock, histogram, scaler, and CDP callbacks.
- Shared helpers declare common implementation entry points and `dpu_hw_setup_rects_impl()`.

## Control flow
The header itself has only inline rectangle programming helper control flow. It computes packed source/destination size and XY register values from DRM rectangles and writes them through `DPU_REG_WRITE`.

## State and persistence
`struct dpu_hw_sspp` stores per-pipe wrapper state: base, register map, UBWC config, index, catalog caps, MDSS version, and ops. Software pipe structs in plane state hold resource assignment and multirect mode until atomic state is replaced.

## Dependencies and integration points
It includes catalog, MDSS, utility, and DPU format definitions. It is shared by SSPP implementations, plane allocation/update logic, debugfs, and resource manager pipe reservations.

## Risks
The ops table is highly feature-dependent. Callers must handle NULL callbacks for unsupported CSC, scaler, CDP, QoS, multirect, or clock force. `DPU_SSPP_MAX_PITCH_SIZE` is enforced by plane checks and must match register field width.

## Test signals
Build coverage catches signature drift. Runtime validation includes atomic state printouts showing `sspp`, multirect mode/index, source/destination rectangles, and correct scanout across all supported formats/modifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_sspp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_sspp_v13.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_sspp_v13.c

## Purpose
Provides MDSS/DPU v13+ SSPP operation implementations for the newer common-plus-record register layout while reusing shared SSPP format, rect, solid-fill, scaler, CSC, QoS, and CDP helpers.

## Important APIs, types, and functions
- `dpu_hw_sspp_init_v13()` installs the v13 ops table.
- `dpu_hw_sspp_calculate_rect_off()` chooses the REC0 or REC1 sub-block base from catalog data.
- V13-specific callbacks include setup for multirect, format, pixel extension, rects, source addresses, solid fill, QoS LUT/control, CDP, and clock force.
- Common register offsets include `SSPP_CMN_*` and record offsets `SSPP_REC_*`.

## Control flow
All per-rectangle programming first computes a record offset from multirect index. Format setup points shared `dpu_hw_setup_format_impl()` at record-local format/opmode/unpack/UBWC registers. Rect and source-address setup write record-local geometry and all plane addresses. V13 pitch packing differs from older code: stride0 combines plane 0 and 2, stride1 combines plane 1 and 3. QoS and clock force use common registers rather than per-record legacy offsets.

## State and persistence
No additional wrapper state is stored beyond `struct dpu_hw_sspp`. Persistent hardware state lives in common SSPP registers and REC0/REC1 record blocks.

## Dependencies and integration points
Depends on `dpu_hw_sspp.h`, UBWC helpers, shared SSPP implementation helpers, and catalog sub-block bases for `sspp_rec0_blk`/`sspp_rec1_blk`. It is selected automatically by `dpu_hw_sspp_init()` when MDSS core major version is 13 or newer.

## Risks
Correct catalog record-base definitions are critical; all offsets are relative to those bases. V13 layout differences in pitch packing, pixel-extension registers, common QoS registers, and clock control can break scanout if legacy assumptions leak in. Unlike older code, clock force is always installed for v13.

## Test signals
Validation should cover v13+ platforms with linear and UBWC formats, multirect REC0/REC1, YUV CSC, scaling, CDP, QoS LUT updates, and SSPP common/record register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_sspp_v13.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_top.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_top.c

## Purpose
Implements the MDP TOP hardware wrapper for split-pipe control, clock-force control, danger/safe status reads, watchdog/vsync source programming, audio interface selection, and DP PHY/interface routing.

## Important APIs, types, and functions
- `dpu_hw_mdptop_init()` allocates and initializes `struct dpu_hw_mdp`.
- `dpu_hw_setup_split_pipe()` programs split display lower/upper controls and split flush.
- `dpu_hw_setup_clk_force_ctrl()` uses catalog clock-control registers.
- `dpu_hw_get_danger_status()` and `dpu_hw_get_safe_status()` decode top-level and SSPP status registers.
- `dpu_hw_setup_vsync_sel()` and `dpu_hw_setup_wd_timer()` configure pingpong vsync sources and watchdog timers.
- `dpu_hw_dp_phy_intf_sel()` programs SC8180X-style DP PHY mapping.

## Control flow
Initialization sets the top register base and installs ops based on MDSS major version: older cores get full vsync source selection, mid-generation cores use watchdog timer setup, v5+ get DP PHY interface selection, and v4/v5 get interface audio selection. Split-pipe setup chooses control bits differently for command versus video mode and for INTF_2 versus other interfaces. Vsync selection updates per-pingpong nibble fields and then programs a watchdog timer when requested.

## State and persistence
The wrapper stores catalog pointer, MMIO base, and ops. Hardware TOP registers persist split configuration, watchdog state, vsync source mapping, DP PHY mapping, and danger/safe status until reprogrammed or reset.

## Dependencies and integration points
Depends on `dpu_hwio.h` register offsets, catalog clock-control metadata, `FIELD_PREP`, and utility MMIO helpers. KMS init creates this object; debugfs danger/safe paths and encoder setup use its ops.

## Risks
`dpu_hw_setup_vsync_sel()` has a sparse static pingpong offset table and silently skips out-of-range indexes, so new pingpong IDs need care. Watchdog load calculation divides by frame rate and assumes valid nonzero values. DP PHY mapping is currently hard-coded by platform logic in KMS rather than data-driven DT, so future platforms can regress if they need different mappings.

## Test signals
Signals include correct split display operation, command-mode TE/vsync timing, watchdog timer behavior, debugfs danger/safe status, DP output routing on SC8180X, and MDP top register snapshots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_top.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_top.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_top.h

## Purpose
Declares the MDP TOP wrapper, configuration structures, and ops used for shared top-level display hardware programming.

## Important APIs, types, and functions
- `struct traffic_shaper_cfg`, although declared, is not wired by the current implementation.
- `struct split_pipe_cfg` models dual-pipe enable, interface mode, controlling interface, and split flush.
- `struct dpu_danger_safe_status` holds decoded MDP and SSPP status.
- `struct dpu_vsync_source_cfg` carries pingpong list, frame rate, and vsync source.
- `enum dpu_dp_phy_sel` and `struct dpu_hw_mdp_ops` expose top-level control operations.
- `dpu_hw_mdptop_init()` constructs the wrapper.

## Control flow
No significant control flow exists in the header. Ops are optional by hardware generation and must be checked before use.

## State and persistence
`struct dpu_hw_mdp` stores register map, catalog caps, and ops. Persistent state is written into MDP TOP registers by implementation callbacks.

## Dependencies and integration points
Includes catalog, MDSS, and utility headers. KMS, encoder, debugfs, and VBIF/plane QoS paths use top-level clock and status services.

## Risks
The API exposes `setup_traffic_shaper` but the current implementation never assigns it, so callers must treat it as optional. `ppnumber[PINGPONG_MAX]` assumes pingpong enum bounds from `dpu_hw_mdss.h`.

## Test signals
Compile coverage and runtime checks through split-pipe setup, vsync source programming, danger/safe debugfs files, and DP PHY selection validate this header’s contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_top.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_util.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_util.c

## Purpose
Provides shared DPU hardware utilities: logged register reads/writes, QSEED3/QSEED3Lite scaler programming, CSC programming, QoS LUT setup, MISR control, CDP programming, clock-force helper, and built-in CSC matrices.

## Important APIs, types, and functions
- `dpu_reg_write()` and `dpu_reg_read()` wrap relaxed MMIO and optional hardware logging.
- `dpu_hw_setup_scaler3()` programs QSEED scaler mode, phase, preload, LUTs, detail enhancer, source/destination sizes, and alpha filtering.
- `dpu_hw_csc_setup()` converts S15.16 matrix coefficients to hardware fields and writes clamp/bias values.
- `_dpu_hw_get_qos_lut()`, `_dpu_hw_setup_qos_lut()`, and `dpu_hw_setup_qos_lut_v13()` support pipe/WB QoS programming.
- `dpu_hw_setup_misr()` and `dpu_hw_collect_misr()` handle signature capture.
- `dpu_setup_cdp()` and `dpu_hw_clk_force_ctrl()` provide common block helpers.

## Control flow
Scaler setup exits with only opmode write when disabled, otherwise builds opmode from format and scaler config, optionally programs detail enhancer and LUTs, writes phase registers using either old packed phase or newer per-axis phase registers, then writes opmode. LUT setup validates lengths and indexes before writing directional/circular/separable tables. CSC setup writes a fixed register sequence from the provided config. MISR setup clears status, uses `wmb()`, then enables free-run capture.

## State and persistence
The only file-static state is `dpu_hw_util_log_mask`, exposed to debugfs. All other state is written to hardware registers or read from caller-provided config. CSC constants are immutable global data.

## Dependencies and integration points
Used by SSPP, WB, LM, TOP, VBIF, and other hardware wrappers. Depends on MSM format helpers for YUV/DX/UBWC decisions, catalog QoS tables, and common MDSS structures.

## Risks
Scaler LUT programming is size/index-sensitive and uses caller-provided pointers. `dpu_hw_clk_force_ctrl()` returns whether the clock was previously not forced, not the final state, so callers use it to know whether to undo. `dpu_setup_cdp()` assumes `fmt` is valid. CSC coefficient shifts and clamp widths differ for 10-bit versus 8-bit paths.

## Test signals
Signals include hardware log output when `hw_log_mask` matches block masks, visual scaling/CSC correctness, QoS tracepoints, MISR read status, CDP register dumps, and absence of underruns when clock-force wrapped VBIF programming runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_util.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_util.h

## Purpose
Declares common DPU register-map structures, scaler/detail-enhancer configuration, DRM-facing scaler structures, QoS config, CSC constants, and shared hardware utility APIs.

## Important APIs, types, and functions
- Macros include `REG_MASK`, MISR control bits, `TO_S15D16`, and `CALCULATE_WD_LOAD_VALUE`.
- `struct dpu_hw_blk_reg_map` carries block MMIO base and log mask.
- `struct dpu_hw_scaler3_de_cfg`, `dpu_hw_scaler3_cfg`, `dpu_drm_pix_ext_v1`, `dpu_drm_de_v1`, and `dpu_drm_scaler_v2` describe scaler inputs.
- `struct dpu_hw_qos_cfg` carries danger/safe/CREQ LUTs and danger/safe enable.
- Declares register I/O macros, scaler, CSC, CDP, QoS, MISR, and clock-force helpers.

## Control flow
The header is mostly declarative. `DPU_REG_WRITE` and `DPU_REG_READ` macros feed register names and offsets into implementation wrappers.

## State and persistence
It defines the register-map handle embedded in hardware wrappers and config structures passed by value or pointer during atomic programming. Persistent hardware effects occur in implementation functions.

## Dependencies and integration points
Includes Linux MMIO/slab headers, MDSS common definitions, and DPU catalog. It is one of the central include files for all DPU hardware block wrappers.

## Risks
The utility structs encode hardware register field assumptions such as max planes, LUT sizes, and watchdog clock math. Mismatched scaler or QoS config can corrupt register programming across multiple blocks.

## Test signals
Build coverage across all DPU blocks is the main static signal. Runtime coverage comes from scaling, CSC, QoS, MISR, CDP, and debug logging features that depend on these declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_vbif.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_vbif.c

## Purpose
Implements the VBIF hardware wrapper for memory-interface error clearing, memory type, outstanding transaction limits, halt control, QoS remap, and write gather enable.

## Important APIs, types, and functions
- `dpu_hw_vbif_init()` constructs the VBIF wrapper.
- `dpu_hw_clear_errors()` reads pending/source error registers and clears them.
- `dpu_hw_set_mem_type()` programs AXI AMEMTYPE fields per XIN client.
- `dpu_hw_set_limit_conf()` and `dpu_hw_get_limit_conf()` set/read read or write outstanding limits.
- `dpu_hw_set_halt_ctrl()` and `dpu_hw_get_halt_ctrl()` control XIN halt.
- `dpu_hw_set_qos_remap()` programs both RP and level remap tables when supported.
- `dpu_hw_set_write_gather_en()` enables write gather per XIN.

## Control flow
Initialization installs core ops and only exposes QoS remap if the catalog feature bit is set. Limit configuration computes register and byte field from XIN ID and read/write direction. Memory type supports up to 16 XINs across two registers. QoS remap computes register group from XIN high bit and priority level, then updates matching nibbles in both remap table families.

## State and persistence
Wrapper state is catalog pointer, MMIO base, and ops. VBIF programming persists in memory-interface registers and affects all display clients until reconfigured or reset.

## Dependencies and integration points
Depends on catalog VBIF feature data, `MAX_XIN_COUNT`, register helpers, and DPU VBIF policy code (`dpu_vbif.c`) that calls these ops from plane/QoS paths and runtime resume.

## Risks
Many helpers do limited argument validation; XIN IDs beyond supported hardware can produce bad bit shifts in limit/halt paths. QoS remap depends on catalog `qos_rp_remap_size`. Because VBIF is shared, incorrect settings can cause underruns, hangs, or memory ordering/performance problems across all active pipes.

## Test signals
Signals include underrun absence under bandwidth stress, correct OT/QoS debug behavior, VBIF error counters clearing, runtime resume reprogramming, and register snapshots for limit/remap/memtype/halt registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_vbif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_vbif.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_vbif.h

## Purpose
Declares the VBIF wrapper and operation table for configuring DPU memory-interface behavior.

## Important APIs, types, and functions
- `struct dpu_hw_vbif_ops` exposes limit config, halt control, QoS remap, memory type, error clearing, and write-gather callbacks.
- `struct dpu_hw_vbif` stores the register map, catalog caps, and ops.
- `dpu_hw_vbif_init()` constructs the wrapper.

## Control flow
No runtime control flow is present in the header. All operations assume clocks and register mappings are valid.

## State and persistence
The header defines wrapper state only. Persistent behavior is in VBIF registers programmed by the implementation.

## Dependencies and integration points
Includes DPU catalog, MDSS common types, and utility register map. KMS owns the single VBIF wrapper, while plane/VBIF policy code uses it for QoS and transaction limit programming.

## Risks
The ops table includes optional `set_qos_remap`; callers must check it on catalogs without remap support. Shared memory-interface programming has high blast radius if XIN IDs or limits are wrong.

## Test signals
Build coverage and runtime bandwidth stress are primary signals. Debugfs/snapshot VBIF register dumps and error clear outputs validate operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_vbif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_wb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_wb.c

## Purpose
Implements the DPU writeback hardware wrapper for destination addresses, output format, ROI, QoS, CDP, pingpong binding, and clock force control.

## Important APIs, types, and functions
- `dpu_hw_wb_init()` constructs a `struct dpu_hw_wb` and installs ops.
- `dpu_hw_wb_setup_outaddress()` writes destination plane addresses.
- `dpu_hw_wb_setup_format()` programs destination format, pack pattern, strides, output size, alpha behavior, and address status.
- `dpu_hw_wb_roi()` programs output image size and ROI output size.
- QoS/CDP helpers: `dpu_hw_wb_setup_qos_lut()`, `dpu_hw_wb_setup_qos_lut_v13()`, and `dpu_hw_wb_setup_cdp()`.
- `dpu_hw_wb_bind_pingpong_blk()` muxes writeback to pingpong/CWB paths.

## Control flow
Ops are installed according to catalog features and MDSS major version: ROI if `DPU_WB_XY_ROI_OFFSET`, QoS if `DPU_WB_QOS` with v13 common QoS layout, CDP if supported, pingpong binding from v5, and clock force from v9. Format setup builds a destination format word from `msm_format`, enables alpha channel or alpha fill behavior as needed, chooses YUV bit, packs element order, writes strides and either ROI or full-destination output size.

## State and persistence
Wrapper state stores MMIO base, WB index, catalog caps, and ops. Destination addresses and format/ROI/QoS/mux registers persist in the WB block through the writeback job until reprogrammed.

## Dependencies and integration points
Depends on `dpu_formats`, writeback catalog caps, MDSS format layout, pingpong enums, and shared QoS/CDP/clock utilities. `dpu_kms.c` initializes writeback connector/encoder support when WB_2 exists in the catalog.

## Risks
There is a duplicate `WB_DST_YSTRIDE1` macro definition with the same value; harmless but noisy. Format programming assumes the supplied `msm_format` and layout are consistent with the DRM writeback job. Pingpong mux encodings for CWB and PP paths are hard-coded and must track hardware documentation.

## Test signals
Writeback jobs should validate captured image content, formats, alpha behavior, ROI cropping, UBWC/CDP if supported, CWB mux selection, and register snapshots for WB format/address/QoS blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_wb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_wb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_wb.h

## Purpose
Declares the writeback hardware wrapper, configuration object, and operation table used by DPU writeback support.

## Important APIs, types, and functions
- `struct dpu_hw_wb_cfg` carries destination layout, interface mode, ROI, and crop rectangles.
- `struct dpu_hw_wb_ops` exposes output address/format, ROI, QoS, CDP, clock force, and pingpong binding callbacks.
- `struct dpu_hw_wb` stores register map, index, catalog caps, and ops.
- `dpu_hw_wb_init()` constructs the wrapper.

## Control flow
The header is declarative. Ops are feature/version gated by the implementation, so callers must check optional callbacks.

## State and persistence
Config data is transient per writeback job. Persistent state is in WB registers after ops run.

## Dependencies and integration points
Includes catalog, MDSS, TOP, utility, and pingpong headers. It connects KMS writeback initialization, encoder/writeback code, and hardware programming.

## Risks
The writeback path combines output memory layout, muxing, QoS, and format packing; mismatched config can corrupt captured buffers. Optional ops require defensive callers across hardware generations.

## Test signals
Build coverage catches signature drift. Runtime signals are successful DRM writeback connector jobs across formats, ROI sizes, and CWB/pingpong routes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_wb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hwio.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hwio.h

## Purpose
Defines MDP TOP register offsets and DP PHY interface-selection bit masks shared by DPU top-level hardware code.

## Important APIs, types, and functions
- Register offsets include interrupt status/enable/clear registers, split-display controls, danger/safe status, watchdog timer controls/load values, clock controls/status, interface reset/select, MDP output control, vsync select, DCE select, and DP PHY interface selection.
- `MDP_DP_PHY_INTF_SEL_*` masks identify INTF and PHY mapping fields.
- `MDP_PERIPH_TOP0` and `MDP_PERIPH_TOP0_END` mark snapshot split points for newer top-register layout.

## Control flow
The file is declarative. Callers use the offsets with `DPU_REG_READ` and `DPU_REG_WRITE`.

## State and persistence
No state is stored here; the macros address hardware registers whose state is controlled elsewhere.

## Dependencies and integration points
Includes `dpu_hw_util.h` for bit helpers. `dpu_hw_top.c`, `dpu_kms.c` snapshot code, interrupt code, and other top-level register users depend on these offsets.

## Risks
Incorrect offsets affect low-level hardware programming globally. Snapshot split markers must match MDSS generation layout or register dumps become incomplete or invalid. DP PHY field masks must stay aligned with hardware documentation.

## Test signals
Runtime tests include interrupt handling, split-display operation, danger/safe status reads, watchdog/vsync programming, DP PHY routing, and display snapshot register coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hwio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_kms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_kms.c

## Purpose
Implements the Qualcomm DPU KMS platform driver and MSM KMS backend: probing, MMIO/clock/ICC setup, hardware init, global atomic state, DRM object creation, display initialization, commit hooks, runtime PM, debugfs, snapshots, and driver registration.

## Important APIs, types, and functions
- Platform entry points: `dpu_dev_probe()`, `dpu_dev_remove()`, `msm_dpu_register()`, and `msm_dpu_unregister()`.
- KMS lifecycle: `dpu_kms_init()`, `dpu_kms_hw_init()`, `dpu_kms_destroy()`, `_dpu_kms_hw_destroy()`, `_dpu_kms_mmu_init()`, and `_dpu_kms_mmu_destroy()`.
- DRM object/display setup: `_dpu_kms_setup_displays()`, `_dpu_kms_initialize_dsi()`, `_dpu_kms_initialize_displayport()`, `_dpu_kms_initialize_hdmi()`, `_dpu_kms_initialize_writeback()`, and `_dpu_kms_drm_obj_init()`.
- Atomic/global state: `dpu_kms_get_global_state()`, duplicate/create/destroy/print state funcs, and `kms_funcs`.
- PM/debug: runtime suspend/resume, debugfs danger/register helpers, and `dpu_kms_mdp_snapshot()`.

## Control flow
Probe validates component binding, allocates `dpu_kms`, sets OPP/clock metadata, maps MDP/VBIF regions using either mdp5 or DPU resource names, parses interconnect paths, then calls `msm_drv_probe()`. KMS init sets max OPP rate, initializes the MSM KMS base, stores the DRM device, and enables runtime PM.

Hardware init creates the global private object, resumes runtime PM, reads core revision, obtains catalog data from OF match, initializes the GPU VM/MMU, fetches UBWC config, initializes resource manager, MDP TOP, VBIF, performance state, optional SC8180X DP PHY mapping, interrupts, mode config limits, DRM planes/CRTCs/encoders/connectors, and VBIF memory types. Commit hooks wrap runtime PM, kickoff active CRTCs, wait for encoder commit completion, and complete CRTC commits.

DRM object init first creates display encoders/connectors for DSI, DP, HDMI, and WB_2 writeback, then creates real or virtual planes from catalog SSPPs, assigns primary/cursor plane arrays, creates CRTCs, and marks every encoder compatible with every CRTC. Runtime suspend disables clocks and ICC bandwidth; resume reenables clocks, reinitializes VBIF memtypes, and notifies encoders.

## State and persistence
`struct dpu_kms` owns MMIO pointers, catalog and UBWC data, regulators, clocks, ICC paths, resource manager, hardware wrappers, interrupt wrapper, performance state, global atomic private object, bandwidth refcount, platform device, and runtime-PM state. Hardware register state is reprogrammed during init/resume and commits; atomic resource state persists in `dpu_global_state` snapshots.

## Dependencies and integration points
Integrates with the MSM DRM core (`msm_kms`, `msm_drv_probe`, `msm_mmu`, GEM VM), DRM atomic/vblank/writeback frameworks, DSI/DP/HDMI subdrivers, DPU CRTC/encoder/plane/resource-manager/perf/IRQ/VBIF modules, Linux runtime PM, clocks, OPP, interconnect, OF matching, and debugfs/snapshot infrastructure.

## Risks
This is high blast-radius initialization code. Error paths must release runtime PM and destroy partially initialized MMU/global state. Virtual-plane behavior is module-parameter controlled and changes resource allocation semantics. Display setup assumes WB_2 for DPU writeback. The SC8180X DP PHY mapping is hard-coded. Runtime resume must restore enough VBIF/encoder state after clocks return. Debugfs register reads require PM get/put to avoid reading powered-off MMIO.

## Test signals
Signals include probe success across every OF compatible, clean runtime suspend/resume, vblank enable/disable, atomic commits on DSI/DP/HDMI, writeback connector jobs, debugfs `hw_log_mask`, danger/safe status, SSPP register dumps, display snapshot contents, ICC bandwidth release on suspend, and absence of PM ref leaks on init failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_kms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_kms.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_kms.h

## Purpose
Declares the DPU KMS core object, global atomic state, logging helpers, KMS utility APIs, vblank hooks, and shared constants used by DPU CRTC/encoder/plane/hardware modules.

## Important APIs, types, and functions
- `struct dpu_kms` embeds `struct msm_kms` and owns device, catalog, UBWC data, MMIO bases, regulators, interrupts, perf, global private state, resource manager, VBIF/MDP wrappers, platform device, clocks, bandwidth refs, and ICC paths.
- `struct dpu_global_state` tracks shared hardware block ownership by CRTC ID for pingpong, mixer, CTL, DSPP, DSC, CDM, SSPP, and CWB resources.
- Helpers/macros include `to_dpu_kms()`, `to_dpu_global_state()`, `DRMID()`, DPU logging macros, `ktime_compare_safe()`, timeout constants, and `DPU_KMS_INFO_MAX_SIZE`.
- Declares `dpu_kms_get_global_state()`, `dpu_kms_get_existing_global_state()`, debugfs regset helper, vblank wrappers, and `dpu_kms_get_clk_rate()`.

## Control flow
The header has no runtime flow except macros. It defines the shared object model that implementation files use to access KMS state and atomic resource allocations.

## State and persistence
The structs declared here are central persistent in-memory state for the DPU driver. `dpu_global_state` is duplicated per atomic transaction and becomes persistent after atomic swap; `dpu_kms` persists for the platform device lifetime.

## Dependencies and integration points
Includes Linux interconnect, DRM driver, MSM KMS/MMU/GEM, DPU catalog, CTL, LM, interrupts, TOP, RM, and perf headers. Nearly all DPU modules include it for access to driver state and logging.

## Risks
Resource ownership arrays depend on enum ranges and offsets. Direct access to `global_state` is discouraged; callers must use getter helpers to satisfy DRM locking. Changes to `dpu_kms` affect initialization, runtime PM, debugfs, and plane/CRTC/encoder modules.

## Test signals
Build coverage is broad. Runtime validation includes atomic resource allocation consistency, state printouts, vblank operations, clock-rate queries, debugfs register reads, and suspend/resume behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_kms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_plane.c

## Purpose
Implements DPU DRM plane objects and atomic plane behavior: framebuffer preparation, validation, virtual/real SSPP resource assignment, wide-plane splitting, multirect sharing, scaler/CSC/QoS/VBIF programming, color fill/error fill, format modifier support, state management, and plane creation.

## Important APIs, types, and functions
- Public entry points: `dpu_plane_init()`, `dpu_plane_init_virtual()`, `dpu_assign_plane_resources()`, `dpu_plane_flush()`, `dpu_plane_set_error()`, and debugfs-only `dpu_plane_danger_signal_ctrl()`.
- Atomic validation: `dpu_plane_atomic_check()`, `dpu_plane_atomic_check_nosspp()`, `dpu_plane_atomic_check_pipe()`, and `dpu_plane_split()`.
- Resource assignment: `dpu_plane_virtual_assign_resources()`, `dpu_plane_assign_resources()`, `dpu_plane_assign_resource_in_stage()`, `dpu_plane_try_multirect_parallel()`, and `dpu_plane_try_multirect_shared()`.
- Programming: `dpu_plane_sspp_atomic_update()`, `dpu_plane_sspp_update_pipe()`, `_dpu_plane_setup_scaler()`, `_dpu_plane_set_qos_lut()`, `_dpu_plane_set_ot_limit()`, `_dpu_plane_set_qos_remap()`, and `dpu_plane_flush_csc()`.
- DRM hooks: plane funcs, helper funcs, reset/duplicate/destroy/print state, and format-modifier validation.

## Control flow
Atomic check first runs generic DRM plane checks with DPU scale limits, computes stage from zpos, validates framebuffer dimensions/pitches, populates layout, and marks QoS remap for modesets. Visible planes force CRTC `planes_changed` if geometry or format changes. Later resource assignment splits a plane against mixer halves/stages and max SSPP width or core clock. In virtual-plane mode it reserves SSPPs dynamically and can share adjacent single-pipe planes through multirect parallel/time-mux. In fixed-plane mode it uses the plane's catalog SSPP and can only split through multirect on that pipe.

Atomic update marks the DPU plane state pending, determines real-time client type, populates buffer addresses, then programs every active software pipe: source address, rects, scaler/pixel extension, multirect, format/rotation/flip, CDP, QoS LUT, VBIF OT limit, and QoS remap. Flush then applies error/color-fill override or CSC just before CRTC flush timing and clears pending. Disable clears multirect state for secondary pipes so shared SSPPs can return to solo mode.

## State and persistence
`struct dpu_plane` stores DRM plane, fixed pipe ID or `SSPP_NONE` for virtual planes, color-fill flag/data, error flag, real-time pipe classification, and catalog pointer. `struct dpu_plane_state` stores assigned pipes, per-pipe configs, stage, pending flag, QoS flags, bandwidth/clock calculations, dirtyfb need, and framebuffer layout. Hardware state persists in SSPP/VBIF registers until a later atomic update/disable or reset.

## Dependencies and integration points
Integrates with DRM atomic helpers, DRM damage/fb helpers, MSM framebuffer prepare/cleanup and format layout/address helpers, DPU resource manager, CRTC client type/mixer count, VBIF policy, SSPP ops, utility CSC matrices, tracepoints, and KMS catalog/perf data.

## Risks
This file is high risk because it translates user-visible DRM plane state into hardware resource allocation and MMIO programming. Wide-plane splitting, rotation, multirect sharing with adjacent z-order planes, UBWC tile constraints, YUV alignment/CSC requirements, and QoS/OT programming can all cause underruns or visual corruption if slightly wrong. `crtc_state` must be valid for visible planes. Virtual planes use a broad advertised format set and rely on assignment-time hardware capability checks.

## Test signals
Validation should cover primary/overlay/cursor planes, virtual and fixed-plane modes, zpos ordering, alpha/blend modes, linear and QCOM compressed modifiers, YUV alignment rejection, inline rotation, scaling limits, max linewidth splitting, dual-DSI/quad-pipe topologies, multirect sharing, color fill/error fill, dirtyfb handling, bandwidth/clock accounting, and debug atomic state prints showing pipe assignments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_plane.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_plane.h

## Purpose
Declares DPU plane state extensions and public plane APIs used by KMS, CRTC, encoder, and debugfs code.

## Important APIs, types, and functions
- `struct dpu_plane_state` extends `drm_plane_state` with DPU software pipes, pipe configs, blend stage, QoS remap flag, pending flag, bandwidth/clock estimates, dirtyfb flag, and framebuffer layout.
- `to_dpu_plane_state()` converts DRM state to DPU state.
- Declares `dpu_plane_flush()`, `dpu_plane_set_error()`, `dpu_plane_init()`, `dpu_plane_init_virtual()`, `dpu_plane_color_fill()`, `dpu_plane_danger_signal_ctrl()`, and `dpu_assign_plane_resources()`.

## Control flow
The header contains no runtime control flow except the debugfs stub for `dpu_plane_danger_signal_ctrl()` when debugfs is disabled.

## State and persistence
`dpu_plane_state` is duplicated and swapped through DRM atomic state. It persists per committed plane state and carries resource assignments until the next atomic transaction.

## Dependencies and integration points
Includes DRM CRTC, DPU KMS, MDSS, and SSPP headers. KMS creates planes with these APIs; CRTC/encoder commit code uses flush/error/color-fill/resource assignment paths.

## Risks
`PIPES_PER_PLANE` controls array sizes and must match splitter/resource assignment assumptions. Callers must not treat `pipe[].sspp` as valid until resource assignment has completed.

## Test signals
Atomic state dumps, successful plane allocation, resource assignment for virtual/fixed planes, and flush behavior across visible/disabled states validate this header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_plane.h -->

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

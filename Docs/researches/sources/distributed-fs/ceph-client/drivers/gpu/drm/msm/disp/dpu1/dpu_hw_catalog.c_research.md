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

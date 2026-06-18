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

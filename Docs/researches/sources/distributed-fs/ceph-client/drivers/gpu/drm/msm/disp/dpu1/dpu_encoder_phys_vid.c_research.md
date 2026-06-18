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

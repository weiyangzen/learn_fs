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

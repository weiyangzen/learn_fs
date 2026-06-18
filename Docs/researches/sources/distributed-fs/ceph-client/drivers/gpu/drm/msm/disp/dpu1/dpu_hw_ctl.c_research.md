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

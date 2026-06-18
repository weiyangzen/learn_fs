# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/venc_ctrls.c

Purpose: registers and handles V4L2 encoder controls for the Venus encoder. It stores control values into `inst->controls.enc` and performs a small set of live HFI updates while both queues are streaming.

Important APIs/types/functions: `venc_calc_bpframes()` converts GOP size and requested consecutive B frames into total B/P frame counts. `dynamic_bitrate_update()` sends `HFI_PROPERTY_CONFIG_VENC_TARGET_BITRATE` for live bitrate/layer bitrate changes. `venc_op_s_ctrl()` handles all standard and compound control writes. `venc_op_g_volatile_ctrl()` reports minimum output buffers from HFI requirements. `venc_ctrl_init()` creates menus, scalar controls, HDR10 compound controls, LTR controls, intra refresh controls, and optional V4/V6 hierarchical coding controls.

Control flow: control setup initializes a V4L2 handler, creates controls with bounds/defaults, checks `ctrl_handler.error`, then runs `v4l2_ctrl_handler_setup()` to seed `venc_controls`. On `s_ctrl`, most controls only update cached state; bitrate and hierarchical layer bitrate can be pushed to firmware immediately; header mode, force key frame, LTR mark, and LTR use are also sent immediately when output and capture queues are streaming.

State and persistence: control values persist only in the lifetime of a `venus_inst`. They are later replayed by `venc_set_properties()` during session setup/start. No persistent storage is used.

Dependencies and integration: depends on V4L2 controls, Venus `core.h`, HFI property constants, and helper functions. It is called from `venc_open()` before instance defaults are fully used by streaming.

Risks: GOP/B-frame validation rejects combinations that cannot produce an exact ratio, which can surprise userspace. Several controls cache per-plane min/max QP fields but `venc_set_properties()` primarily uses packed aggregate min/max fields, so control-to-firmware expectations must be verified by codec/firmware version. Live updates require `inst->lock`; missed lock coverage would race streaming transitions. Hierarchical coding is conditionally registered for V4/V6 cores, so userspace behavior differs by hardware.

Test signals: use `v4l2-ctl --list-ctrls`, set every registered control within and outside bounds, test invalid H.264 8x8 transform/profile combinations, verify live bitrate/keyframe/LTR/header changes during streaming, and confirm volatile min-buffers returns firmware-derived values after session initialization.

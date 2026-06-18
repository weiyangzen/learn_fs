# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_ctrls.c

## Purpose
`iris_ctrls.c` maps V4L2 controls to Iris platform firmware capability slots and HFI property setters. It initializes per-instance V4L2 controls from platform capability tables, handles dynamic control updates, and translates user-facing values into Gen1/Gen2 firmware payloads.

## Important APIs, Types, And Functions
`iris_ctrls_init()` creates V4L2 controls for all supported capabilities plus min-buffer controls. `iris_session_init_caps()` copies platform decoder and encoder firmware capability tables into `core->inst_fw_caps_dec` and `core->inst_fw_caps_enc`, with special handling for `PIPE`. `iris_set_properties()` applies config params and then calls every capability `set` callback. Setter helpers include generic `iris_set_u32_enum()`/`iris_set_u32()`, stage/pipe, profile/level, Gen1 profile-level packing, header mode, bitrate/peak bitrate, Gen1/Gen2 bitrate mode, entropy mode, min/max/frame QP, QP range, rotation, flip, and intra-refresh period.

## Control Flow
Control IDs are mapped to `enum platform_inst_fw_cap_type` by `iris_get_cap_id()`, and the reverse mapping is used during control creation. `iris_op_s_ctrl()` rejects unsupported controls and rejects non-dynamic controls while the source queue is streaming. Otherwise it marks `CAP_FLAG_CLIENT_SET`, stores the value, and, if streaming, invokes the cap setter. Setter functions call `hfi_ops->session_set_property()` with HFI property id, host flags, port mapping from cap flags/domain, payload type, and payload data.

## State And Persistence Behavior
State is persisted in `inst->fw_caps[]`: current value, min/max, mask/step, flags, HFI property id, and setter callback. Several setters update derived state: peak bitrate may overwrite the cap value, bitrate mode stores `inst->hfi_rc_type`, Gen2 entropy mode may force CAVLC for baseline H.264, QP setters encode client-set enable bits, and AV/control transforms select HFI values.

## Dependencies And Integration Points
The file depends on V4L2 controls, V4L2 mem2mem streaming state, Gen1/Gen2 HFI defines, platform capability definitions, and HFI command ops. It is integrated with streamon via `iris_set_properties()` and with runtime `S_CTRL` ioctls via `iris_ctrl_ops`.

## Risks And Test Signals
Risk areas include mismatched V4L2-to-cap mappings, incorrect dynamic-control flags, inconsistent Gen1/Gen2 HFI value translations, and packed QP bit errors. `iris_set_bitrate()` leaves `max_bitrate` dependent on codec/entropy branches; HEVC currently falls through to entropy-mode selection, so tests should verify HEVC bitrate clipping. Regression tests should cover control enumeration/defaults, invalid values, changing dynamic controls while streaming, bitrate modes, QP min/max/frame interactions, rotation/flip, and intra-refresh behavior during streaming.

# sources/distributed-fs/ceph-client/drivers/media/i2c/s5c73m3/s5c73m3-ctrls.c

## Purpose
`s5c73m3-ctrls.c` maps V4L2 controls for the S5C73M3 camera to ISP command registers. It covers focus, 3A locks, exposure metering and bias, white balance, ISO, image effects, image tuning, stabilization, JPEG quality, scene mode, flicker control, WDR, and zoom.

## Important APIs, Types, and Functions
The exported entry point is `s5c73m3_init_controls(struct s5c73m3 *state)`, which initializes `state->ctrls.handler`, creates all supported controls, clusters related controls, marks volatile controls, and assigns the handler to `state->sensor_sd`. Runtime callbacks are `s5c73m3_s_ctrl()` and `s5c73m3_g_volatile_ctrl()`.

Helper functions translate control values into `COMM_*` command values from `s5c73m3.h`: `s5c73m3_get_af_status()`, `s5c73m3_set_colorfx()`, `s5c73m3_set_exposure()`, `s5c73m3_set_white_balance()`, `s5c73m3_af_run()`, `s5c73m3_3a_lock()`, `s5c73m3_set_auto_focus()`, and simple setters for contrast, saturation, sharpness, ISO, stabilization, JPEG quality, scene, and power-line frequency.

## Control Flow
Control setup creates menu/int/std controls and builds clusters for auto exposure, auto ISO, and autofocus. `s5c73m3_s_ctrl()` logs, locks `state->lock`, skips hardware writes when the device is powered off so values can be restored later, rejects inactive controls, and dispatches by control ID to ISP commands. `s5c73m3_g_volatile_ctrl()` rejects powered-off reads and refreshes AF status from `REG_AF_STATUS`.

## State and Persistence
Control values persist in the V4L2 control handler and are applied to hardware only while powered. No filesystem state is stored. The volatile AF status control is derived from current hardware status registers. Cluster state such as `is_new`, current value, and inactive flags drives which ISP commands are emitted.

## Dependencies and Integration Points
The file depends on shared `struct s5c73m3`, command/register constants from `s5c73m3.h`, and core helper functions `s5c73m3_read()` and `s5c73m3_isp_command()`. It integrates with the sensor subdev control handler created during I2C probe.

## Risks and Edge Cases
Many controls are silently deferred when powered off; correct restoration depends on `v4l2_ctrl_handler_setup()` after power-on in the core. `s5c73m3_g_volatile_ctrl()` switches on `V4L2_CID_FOCUS_AUTO` but updates `af_status`, which is unusual and should be covered by user-space AF status reads. Stabilization repurposes frame-rate command state and can suppress normal frame-rate programming.

## Test Signals
Useful tests include power-off control set followed by power-on restoration, AF start/stop/status transitions, 3A lock toggling AE/AWB/AF commands, exposure bias and metering cluster updates, manual/auto ISO behavior, JPEG quality thresholds, scene/effect menu mapping, stabilization frame-rate behavior, and `-EINVAL` for inactive controls.

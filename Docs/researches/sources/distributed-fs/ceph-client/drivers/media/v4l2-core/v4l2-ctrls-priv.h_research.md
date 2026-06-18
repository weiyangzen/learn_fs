# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-ctrls-priv.h

## Purpose
This private header defines internal helpers and cross-file prototypes for the V4L2 controls framework implementation. It is shared by the controls API, core, and request files, but is not a public driver-facing header.

## Important APIs, types, and functions
The `dprintk(vdev, fmt, ...)` macro emits control debug messages when the target `video_device` has `V4L2_DEV_DEBUG_CTRL` enabled. `has_op(master, op)` and `call_op(master, op)` safely test and invoke optional `struct v4l2_ctrl_ops` callbacks on a cluster master. `node2id()` maps a list node in a handler's sorted reference list to its control ID.

Small inline helpers encode common control-state tests: `is_cur_manual()` checks whether an auto-cluster master is currently in manual mode, `is_new_manual()` checks whether the staged value would switch to manual mode, and `user_flags()` exposes kernel flags to userspace while adding `V4L2_CTRL_FLAG_HAS_PAYLOAD` for pointer controls.

The prototype block declares internal functions implemented by `v4l2-ctrls-core.c`, `v4l2-ctrls-api.c`, and `v4l2-ctrls-request.c`: value-copy helpers, event helpers, reference lookup, range checking, cluster update/commit, common get/set API paths, and request API paths.

## Control flow
There is no standalone runtime flow in this header. It shapes control flow by making the same helper semantics available across the three implementation files. For example, the API file uses `is_cur_manual()` and `update_from_auto_cluster()` before setting volatile auto-clusters; the core file uses `user_flags()` when filling control events; the request file uses `req_to_new()`, `cur_to_req()`, `new_to_req()`, and `try_or_set_cluster()` to apply queued request controls.

## State and persistence behavior
The header owns no storage. Its helpers inspect existing `struct v4l2_ctrl`, `struct v4l2_ctrl_ref`, and `struct video_device` fields. It is part of the internal consistency contract for current/new/request values, control flags, manual-mode detection, and callback invocation.

## Dependencies and integration points
It expects the including C files to have the V4L2 control, file-handle, and video-device types available via public media headers. It links the internal implementation units together without exposing these helpers to external modules. Changes here can affect all control paths: normal ioctl get/set, request setup/completion, event delivery, and handler lifecycle.

## Risks
Because this header defines shared internal semantics, small changes have broad impact. `call_op()` assumes callbacks take the master control as their argument and return zero when missing; changing that convention would affect volatile, try, and set paths. `user_flags()` determines userspace-visible `HAS_PAYLOAD`; missing it would break pointer control queries. Manual-mode helpers assume auto-cluster masters store integer current/staged values in `cur.val` and `val`. Prototypes must remain synchronized with definitions to avoid accidental ABI or locking contract mismatches inside the controls framework.

## Test signals
There are no direct tests for the header, but good indirect signals are successful compilation of `v4l2-ctrls-api.c`, `v4l2-ctrls-core.c`, and `v4l2-ctrls-request.c`, plus behavioral tests for control debug logging, pointer-control query flags, auto-cluster manual transitions, request setup/completion, and callback invocation when optional ops are absent.

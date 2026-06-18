# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_utils.c

## Purpose
Provides shared helpers for resolution comparison, macroblock accounting, split-mode detection, buffer completion, firmware response waits, instance lookup, aggregate core admission checks, and rotation predicates.

## Important APIs And Functions
- `iris_res_is_less_than()` compares two resolutions using macroblocks and side limits.
- `iris_get_mbpf()` computes macroblocks per frame from max(source format, crop).
- `iris_split_mode_enabled()` returns true for NV12 and QC08C capture/output layouts that use DPB split mode.
- `iris_helper_buffers_done()` drains all queued src or dst m2m buffers with a vb2 state.
- `iris_wait_for_session_response()` waits for session or flush completion with platform timeout, temporarily releasing `inst->lock`, and marks the instance error on timeout.
- `iris_get_instance()` looks up an instance by firmware session ID under `core->lock`.
- `iris_check_core_mbpf()` and `iris_check_core_mbps()` enforce aggregate core capacity across all instances.
- `is_rotation_90_or_270()` checks the ROTATION firmware cap.

## Control Flow And Integration Points
Admission checks are called from vb2 queue setup/start and encoder parameter changes. HFI response code can resolve instances by session ID. Command/close paths use completion waiting. Buffer queue error paths use `iris_helper_buffers_done()`. VPU buffer sizing uses split-mode and rotation helpers.

## State And Persistence Behavior
Mostly read-only. `iris_wait_for_session_response()` mutates instance state to ERROR on timeout. Buffer completion drains queued vb2 buffers and changes their userspace-visible state.

## Dependencies
Depends on PM runtime include, V4L2 mem2mem, `iris_instance`, and utility header definitions.

## Risks
- `iris_wait_for_session_response()` unlocks and relocks `inst->lock`; callers must be prepared for concurrent state changes while waiting.
- Aggregate core checks include all instances and use current format/crop/rate fields; races are controlled only if callers hold appropriate locks.
- Split-mode detection is hard-coded to two formats and affects DPB allocation and buffer sizing.

## Test Signals
- Multi-session admission tests for macroblocks per frame and per second.
- Firmware response timeout injection should mark instance ERROR.
- DRC/split-mode streams validate DPB count and output sizing.

# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_common.h

## Purpose
`iris_common.h` exposes the shared vb2 conversion and stream lifecycle helpers implemented by `iris_common.c`. It is a small interface used by decoder/encoder front-end files and queue operations.

## Important APIs, Types, And Functions
The declarations are `iris_vb2_buffer_to_driver()`, `iris_set_ts_metadata()`, `iris_process_streamon_input()`, `iris_process_streamon_output()`, and `iris_session_streamoff()`. The header forward-declares `struct iris_inst` and `struct iris_buffer`; it relies on including users to have relevant vb2/V4L2 type definitions visible.

## Control Flow
The exported functions sit at V4L2 streamon/streamoff and qbuf boundaries. Decoder and encoder code can call these common helpers after domain-specific validation, avoiding duplicated HFI start/stop, pause/resume, and deferred-buffer completion behavior.

## State And Persistence Behavior
The header itself stores no state, but its API mutates instance state, sub-state, timestamp metadata, buffer attrs, and HFI session state.

## Dependencies And Integration Points
It integrates `iris_common.c` with V4L2 frontend modules, `iris_buffer.c`, HFI command ops, and state management. It is intentionally narrow, making it a stable point for stream lifecycle tests.

## Risks And Test Signals
The main risk is misuse without holding the correct instance or queue locks expected by callers. Tests should exercise the public helpers through normal V4L2 ioctls rather than direct unit calls when possible, because correctness depends on vb2 and mem2mem queue state.

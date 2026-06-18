# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-debug.c

Purpose: provides small formatting and summary helpers for Delta stream/frame information and decoder instance statistics.

Important APIs and functions: `delta_streaminfo_str` formats compressed stream metadata; `delta_frameinfo_str` formats decoded frame metadata; `delta_trace_summary` emits a debug log summary at context release when stream info is known.

Control flow: V4L2 negotiation and release paths call these helpers to produce consistent debug messages. The functions consume already-populated `delta_streaminfo`, `delta_frameinfo`, and counter fields and do not mutate decode flow.

State and persistence: no independent state. Output reflects transient per-context fields such as decoded/output/dropped frame counts and error counters.

Dependencies and integration points: depends on `delta.h`, V4L2 field/fourcc conventions, and the local debug header. The release path in `delta-v4l2.c` uses `delta_trace_summary`.

Risks: formatting uses fixed caller-provided buffers and compact strings; malformed or uninitialized profile/level/other arrays can produce sparse output. `delta_frameinfo_str` checks `DELTA_STREAMINFO_FLAG_*` names against frame flags, relying on equal numeric values with `DELTA_FRAMEINFO_FLAG_*`; that coupling is fragile if flags diverge.

Test signals: enable dynamic debug and inspect GET/S_FMT and release logs for MJPEG streams with crop/pixel-aspect metadata. Static builds catch prototype drift.

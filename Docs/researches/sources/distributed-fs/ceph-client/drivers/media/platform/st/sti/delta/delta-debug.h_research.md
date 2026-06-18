# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-debug.h

Purpose: declares Delta debug formatting and summary helpers shared with the V4L2 implementation.

Important APIs and functions: exposes `delta_streaminfo_str`, `delta_frameinfo_str`, and `delta_trace_summary`.

Control flow: callers pass existing stream/frame/context objects and caller-owned buffers to format state for logging. There is no control logic in the header.

State and persistence: none. The declared functions only observe runtime context state.

Dependencies and integration points: requires consumers to have visible `struct delta_streaminfo`, `struct delta_frameinfo`, and `struct delta_ctx` definitions, typically through `delta.h`.

Risks: the header has a narrow internal API, but it does not include `delta.h` itself, so include order matters. Prototype changes must be kept in sync with `delta-debug.c`.

Test signals: compile coverage from `delta-v4l2.c` and `delta-debug.c`; runtime signal is correct dynamic-debug output during format negotiation and release.

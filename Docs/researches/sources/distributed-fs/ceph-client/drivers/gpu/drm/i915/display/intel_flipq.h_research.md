# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_flipq.h

Purpose: declares the DMC flip-queue interface for display update scheduling.

Important APIs/types/functions: exposes support/init/reset, enable/disable, add, execution-time calculation, DMC halt/unhalt workaround helpers, and dump functions.

Control flow: no implementation here. Atomic/DSB code can query support, enable queues for a CRTC, enqueue DSB buffers with PTS, and disable/reset queues during modeset transitions.

State and persistence: no state in the header. Per-CRTC software tail and hardware queue state are managed by `intel_flipq.c`.

Dependencies and integration: forward-declares DSB IDs, flip queue IDs, pipe, CRTC, CRTC state, display, and DSB types. Used by DSB/modeset code on platforms with DMC flip queues.

Risks: callers must only enqueue when supported and enabled, and must use the correct queue ID/DSB pairing.

Test signals: compile with display versions that both support and do not support flip queues; modeset tests should verify no calls enqueue when unsupported.

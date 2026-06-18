# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi_capture.h

Purpose: declares the capture video-node data model, supported-format metadata shape, capture state machine, and internal capture APIs for sun6i CSI.

Important APIs and types: defines capture name and min/max dimensions, `struct sun6i_csi_capture_format`, `struct sun6i_csi_capture_format_match`, `struct sun6i_csi_capture_state`, and `struct sun6i_csi_capture`. Declares helpers for active dimensions/format, format lookup, hardware configure, state update/sync/frame_done, setup, and cleanup.

Control flow: platform/ISP paths call capture setup/cleanup; bridge calls capture configure and state update during stream start; IRQ dispatch calls frame_done and sync.

State and persistence: queue, locks, pending/current/complete buffers, sequence, streaming, and setup state persist for the device lifetime after setup. Active user format persists in `capture.format` until changed while queues are idle.

Dependencies and integration points: includes V4L2 device types and forward-declares `struct sun6i_csi_device`. It is the private contract between platform, bridge, IRQ, and capture implementation files.

Risks: `#undef current` avoids a macro collision for the field named `current`, which is a portability hint for kernel macro namespace issues. Future state-machine changes must preserve spinlock protection around the three buffer slots.

Test signals: compile coverage, IRQ-driven state transitions, and stream stop cleanup for each buffer slot.

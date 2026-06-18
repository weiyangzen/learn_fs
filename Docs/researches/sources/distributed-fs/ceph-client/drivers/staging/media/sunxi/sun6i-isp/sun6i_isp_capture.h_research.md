# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_capture.h

Purpose: declares capture-side constants, state, structures, and helper/setup APIs for the sun6i ISP video capture node.

Important APIs/types: width/height min/max constants, `struct sun6i_isp_capture_format` maps pixfmt to hardware output format, `struct sun6i_isp_capture_state` tracks queued/pending/current/complete buffers and sequence/streaming state, and `struct sun6i_isp_capture` embeds video device, vb2 queue, mutex, media pad, and format. Public functions expose dimensions/format, format lookup, hardware configure, state update/complete/finish, setup, and cleanup.

Control flow: no implementation; used by core interrupt/state logic, proc configuration, params sequence tagging, and capture implementation.

State and persistence: declares the capture state machine used across frames and load-buffer sync points.

Dependencies/integration: depends on V4L2 device types and shared `sun6i_isp_buffer` from `sun6i_isp.h`. The `#undef current` avoids conflict with the Linux `current` macro for a struct field named `current`.

Risks: the state field name workaround is fragile and signals macro namespace pressure. Any change to state transitions must coordinate with `sun6i_isp.c` interrupt ordering and params sequence handling.

Test signals: build coverage, stream sequencing tests, and static checks for macro conflicts.

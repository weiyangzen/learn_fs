# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_video.h

Purpose: declares Cedrus video/queue format structures and public video helper APIs.

Important APIs/types: `struct cedrus_format` stores pixelformat, direction mask, and capability mask. Exports `cedrus_ioctl_ops`, `cedrus_queue_init()`, `cedrus_prepare_format()`, `cedrus_reset_cap_format()`, and `cedrus_reset_out_format()`.

Control flow: no implementation; `cedrus.c` uses the ioctl ops and queue init, while control validation uses capture reset.

State and persistence: none directly.

Dependencies/integration: couples core context creation with video format/queue implementation.

Risks: declarations rely on `struct cedrus_ctx`/V4L2 types from inclusion context.

Test signals: build coverage and V4L2 open/queue initialization paths.

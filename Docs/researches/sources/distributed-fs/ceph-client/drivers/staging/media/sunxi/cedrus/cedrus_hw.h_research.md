# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_hw.h

Purpose: declares common Cedrus hardware helper APIs.

Important APIs/types: declarations for engine enable/disable, destination format programming, suspend/resume, probe/remove, and watchdog work function.

Control flow: no logic; implementations are in `cedrus_hw.c` and callers are core, video queue, and codec files.

State and persistence: none directly.

Dependencies/integration: requires `struct cedrus_ctx`, `struct cedrus_dev`, `struct v4l2_pix_format`, and `struct device` definitions available through `cedrus.h` include order.

Risks: helper declarations are broadly used; signature changes ripple through codecs and core queue paths.

Test signals: build coverage and runtime decode paths that exercise engine and PM helpers.

# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/cedrus/cedrus_dec.h

Purpose: declares the Cedrus mem2mem job entry point.

Important APIs/types: `void cedrus_device_run(void *priv);`.

Control flow: no logic; included by `cedrus.c` to register mem2mem ops and by implementation users.

State and persistence: none.

Dependencies/integration: binds `cedrus.c` and `cedrus_dec.c`.

Risks: minimal; signature must match `v4l2_m2m_ops.device_run`.

Test signals: build/link check and runtime mem2mem job scheduling.

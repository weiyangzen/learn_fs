<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/null.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/null.c

Purpose: implements the `null` UML channel backend, providing a console/serial endpoint similar to `/dev/null`.

Important APIs/types/functions: `null_init()`, `null_open()`, `null_read()`, `null_free()`, and `null_ops`.

Control flow: initialization returns a unique static token. Open opens the configured host `DEV_NULL` path read/write and reports no device string. Reads always return `-ENODEV`; writes use the generic write path and disappear into the null device.

State and persistence: no per-channel allocated state is used. Host `/dev/null` has no persisted output.

Dependencies and integration points: depends on `DEV_NULL` from Makefile-provided `DEV_NULL_PATH`, generic channel helpers, and host `open()`.

Risks: read side intentionally never produces input, so attaching an interactive console to `null` can make it unusable. Build-time `DEV_NULL` must be valid for the host platform.

Test signals: boot with `con1=null`, verify output is discarded, reads fail cleanly, and mconsole config reports null/empty device details.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/null.c -->

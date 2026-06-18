# sources/distributed-fs/ceph-client/drivers/s390/char/vmcp.c

Purpose: exposes a `/dev/vmcp` misc device for privileged userspace to issue z/VM CP commands through diagnose 8 (`cpcmd`) and read back CP responses.

Important APIs/types/functions: defines `struct vmcp_session`, CMA reservation helpers `early_parse_vmcp_cma` and `vmcp_cma_reserve`, session response alloc/free helpers, file ops `vmcp_open`, `vmcp_release`, `vmcp_read`, `vmcp_write`, and `vmcp_ioctl`, and device init `vmcp_init`.

Control flow: open requires `CAP_SYS_ADMIN`, allocates a per-file session, and defaults the response buffer to one page. Write copies a command up to 240 bytes, allocates response memory if needed, records the command in debug, calls `cpcmd`, stores response size/code, resets file offset, and returns the command length. Read drains the current response through `simple_read_from_buffer`. Ioctls get CP code, set next response buffer size, or get response size.

State and persistence: state is per-open session: response pointer, buffer size, CMA/allocation flag, response size/code, and mutex. CMA area size is configured early by `vmcp_cma=` and reserved only under z/VM. No command history is persisted except debug events.

Dependencies and integration: depends on z/VM detection, `asm/cpcmd.h`, `asm/vmcp.h`, s390 debug feature, miscdevice, CMA for large contiguous response buffers, and user-copy APIs.

Risks: CP commands are powerful, hence CAP_SYS_ADMIN gate; response buffers require physically adjacent pages for diagnose 8 and may fail for large sizes; `VMCP_SETBUF` caps order at 8; command text is debug-logged.

Test signals: load under z/VM vs non-VM, permission checks, command length boundary, SETBUF/GETSIZE/GETCODE ioctls, large response allocation via CMA fallback, repeated writes resetting read offset, and concurrent per-session locking.

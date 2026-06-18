# sources/distributed-fs/openafs/src/config/afs_args.h

Purpose: public kernel/user ABI header for OpenAFS syscall opcodes, syscall classes, initialization structures, proc/ioctl replacements, and socket-proxy payloads.

Important APIs/types/functions: defines `AFSOP_*` operation codes for afsd startup, cache setup, cell configuration, RX daemon control, shutdown, and socket proxy; `AFSCALL_*` syscall classes; RX stats flags; `afs_umv_param`, `afs_usp_param`, `afs_uspc_param`, `afs_cacheParams`, `cm_initparams_v1`, Linux proc ioctl names and `VIOC_SYSCALL*`, Darwin/Solaris syscall argument layouts, cache inode sentinels, socket-proxy structures, and `AFS_SETINT_ATSYS` values.

Control flow: no executable flow, but consumers dispatch on these numeric opcodes. Comments explicitly require updating `afsd_init_syscall_opcodes()` when new `AFSOP_*` values are added.

State and persistence: defines the shape of state passed between afsd, kernel modules, proc/ioctl shims, callback interfaces, and socket proxy helpers. Cache parameter structures describe persistent cache sizing choices but do not store them themselves.

Dependencies and integration: included by kernel code, afsd, pioctl/syscall wrappers, rxstats tools, and platform-specific syscall implementations. It relies on configured `afs_int32`, `afs_uint32`, platform `_IOW/_IOWR` macros, and environment macros from `param.h`.

Risks and test signals: numeric ABI drift is the major risk. Structure size changes require versioning via `AFS_CLIENT_RETRIEVAL_VERSION`. Signals include afsd startup on each platform, syscall tracing opcode names, pioctl/proc ioctl compatibility, RX stats toggles, shutdown opcodes, and socket-proxy send/receive tests.

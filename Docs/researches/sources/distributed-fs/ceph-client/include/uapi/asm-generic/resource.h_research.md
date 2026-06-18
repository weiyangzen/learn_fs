# sources/distributed-fs/ceph-client/include/uapi/asm-generic/resource.h

Purpose: Defines generic resource limit identifiers and infinity value.

Important APIs/types/functions: Exports `RLIMIT_CPU`, `RLIMIT_FSIZE`, `RLIMIT_DATA`, `RLIMIT_STACK`, `RLIMIT_CORE`, guarded `RLIMIT_RSS/NPROC/NOFILE/MEMLOCK/AS`, `RLIMIT_LOCKS`, `RLIMIT_SIGPENDING`, `RLIMIT_MSGQUEUE`, `RLIMIT_NICE`, `RLIMIT_RTPRIO`, `RLIMIT_RTTIME`, `RLIM_NLIMITS`, and guarded `RLIM_INFINITY`.

Control flow: Guards preserve architecture-specific historical order for limits 5-9 and infinity representation.

State/persistence: No runtime state; constants define `getrlimit`/`setrlimit` ABI.

Dependencies/integration: Used by libc resource APIs and kernel resource limit handling.

Risks: Limit numbering is ABI-sensitive, especially for architectures with historical ordering differences.

Test signals: Headers ABI checks and getrlimit/setrlimit tests across generic and overriding architectures.

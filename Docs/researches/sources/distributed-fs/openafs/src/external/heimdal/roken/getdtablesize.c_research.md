# sources/distributed-fs/openafs/src/external/heimdal/roken/getdtablesize.c

Purpose: fallback implementation of `getdtablesize()` returning a process file-descriptor limit.

Important APIs/types/functions: `getdtablesize(void)`.

Control flow: tries `sysconf(_SC_OPEN_MAX)`, else `getrlimit(RLIMIT_NOFILE)`, else `sysctl(KERN_MAXFILES)`, then falls back to `OPEN_MAX` or `NOFILE` macros if available.

State and persistence behavior: read-only query of OS/resource state; no heap or global mutation.

Dependencies and integration points: portability shim for code that needs descriptor table bounds, often before closing descriptors in daemon setup.

Risks: may return -1 if no method or macro is available. Resource limits can change after the call. Some fallback paths use system-wide max rather than per-process soft limit.

Test signals: platform builds for each configured path, expected value under adjusted `RLIMIT_NOFILE`, and fallback macro behavior.

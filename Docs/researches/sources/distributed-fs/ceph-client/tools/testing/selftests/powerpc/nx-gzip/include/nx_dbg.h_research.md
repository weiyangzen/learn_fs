<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/nx_dbg.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/nx_dbg.h

Purpose: Debug and tracing macro header for NX gzip sample code.

Important APIs and types: Declares external debug globals and defines `prt`, `prt_err`, `prt_warn`, `prt_info`, `prt_trace`, `prt_stat`, `hw_trace`, `sw_trace`, plus `nx_lib_debug` prototype.

Control flow: Macros conditionally print to `stderr` or `nx_gzip_log` depending on global trace/debug flags. There is no function body in this header.

State and persistence: State is external: `nx_dbg`, trace masks, implementation flags, and optional log file pointer.

Dependencies and integration points: Used by `gzip_vas.c` and compatible with libnxz-style debug controls.

Risks: Because logging macros evaluate variadic arguments in conditional blocks, callers should avoid side effects. Missing global definitions cause link failures.

Test signals: Trace output during NX failures is the primary test signal; normal tests usually run with debug disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/nx_dbg.h -->

# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/waitid_options.c

Purpose: Formats `waitid` option flags.

Important APIs/types/functions: `syscall_arg__scnprintf_waitid_options` recognizes `WNOHANG`, `WUNTRACED`, and `WCONTINUED`.

Control flow: A macro-driven sequence appends recognized options with optional `W` prefix and clears them; remaining bits print as hex.

State and persistence: Stateless formatting.

Dependencies and integration points: Depends on `<sys/wait.h>` and the perf trace `SCA_WAITID_OPTIONS` binding.

Risks: It covers only a subset of wait flags relevant to waitid-style calls. Platform-specific wait bits print numerically.

Test signals: Trace wait calls with zero, individual, combined, and unknown option bits.

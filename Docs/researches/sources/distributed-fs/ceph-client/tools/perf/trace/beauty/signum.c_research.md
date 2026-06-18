# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/signum.c

Purpose: Formats signal numbers as symbolic `SIG*` names for syscall arguments.

Important APIs/types/functions: `syscall_arg__scnprintf_signum` switches over standard POSIX signals plus conditional platform signals such as `SIGEMT`, `SIGSTKFLT`, and `SIGSWI`.

Control flow: Matching cases return immediately with optional `SIG` prefix; unknown signal numbers print as hex.

State and persistence: Stateless formatting.

Dependencies and integration points: Depends on `<signal.h>` and `SCA_SIGNUM`.

Risks: Real-time signals and platform-specific aliases are not exhaustively named. Alias values may make only the first matching case visible.

Test signals: Format common signals, optional platform signals when defined, real-time signals, and invalid numbers.

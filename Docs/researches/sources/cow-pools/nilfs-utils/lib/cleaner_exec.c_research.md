# File Research: sources/cow-pools/nilfs-utils/lib/cleaner_exec.c

Implements legacy process-level cleaner control. It locates `CORE_SBINDIR/nilfs_cleanerd`, forks, drops setuid/setgid privileges in the child, optionally passes `-p <protection_period>`, execs the daemon, and reads the daemon’s real PID from a pipe.

It provides ping via `kill(pid, 0)` and shutdown via `SIGTERM`, with binary exponential backoff followed by periodic wait messages. Output is routed through configurable logger/printf/flush callbacks.

# File Research: sources/block-storage/util-linux/sys-utils/prlimit.c

This file implements `prlimit(1)`, showing or changing resource limits for the current process, another process, or a command to be executed. It wraps `prlimit64` directly when libc lacks `prlimit()`.

Resource metadata is held in `prlimit_desc[]`, covering address space, core size, CPU, data, file size, locks, memlock, message queues, nice, open files, processes, RSS, realtime priority/time, pending signals, and stack. Requested operations are represented as `struct prlimit` entries in a list; entries either request current values for display or contain new soft/hard limits to apply.

Limit parsing accepts `value`, `soft:hard`, `soft:`, `:hard`, and `unlimited`. If only one side of a limit is supplied, `get_unknown_hardsoft()` fetches the existing limit to preserve the unspecified half. The code rejects soft limits above hard limits and checks `RLIMIT_NOFILE` against `/proc/sys/fs/nr_open`.

Output uses libsmartcols with configurable columns, raw mode, and no headings. If a command is supplied, limits are applied before `execvp()`. `--pid` accepts util-linux PID syntax with optional pidfd inode validation when supported.

# sources/distributed-fs/ceph-client/tools/lib/subcmd/pager.c

Purpose: Starts and manages a pager process for command help/output, redirecting stdout/stderr through the pager and handling cleanup on exit/signals.

Important APIs/types/functions: `pager_init()`, `force_pager()`, `setup_pager()`, `pager_in_use()`, and `pager_get_columns()`. Internal state includes `spawned_pager`, `pager_columns`, `forced_pager`, `pager_argv`, and `pager_process`.

Control flow: `setup_pager()` chooses a pager from forced value, configured env, `PAGER`, `/usr/bin/pager`, `/usr/bin/less`, or `cat`; skips paging for non-tty output unless forced; starts a child with `start_command()`, redirects stdout and tty stderr to the pipe, installs common signal handlers, and registers `atexit()`. `wait_for_pager()` closes output FDs and waits for the child.

State and persistence: Process-global pager state and environment `LESS` set in the child preexec callback. Parent FDs are mutated by `dup2()`.

Dependencies/integration: Uses `run-command.c` for child process handling, `sigchain.c` for signal chaining, `subcmd-config.h` for pager env name, and POSIX select/ioctl/signal APIs.

Risks: Once stdout/stderr are redirected, later code must tolerate closed descriptors during pager shutdown. `pager_preexec()` blocks in `select()` until input is available. Signal handling assumes `wait_for_pager()` is safe enough in that context. Pager choice uses shell `sh -c`, so pager strings come from environment and are shell-interpreted by design.

Test signals: Run with tty/non-tty output, forced pager, `PAGER=cat`, missing pager binaries, signal interruption, and COLUMNS/window-size behavior.

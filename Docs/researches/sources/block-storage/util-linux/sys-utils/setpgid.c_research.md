# File Research: sources/block-storage/util-linux/sys-utils/setpgid.c

This file implements `setpgid(1)`, running a command in a new process group. It calls `setpgid(0, 0)` for the current process before `execvp()`.

With `--foreground`, it opens `/dev/tty`, temporarily blocks `SIGTTOU`, and calls `tcsetpgrp()` to make the new process group foreground for the controlling terminal. The utility otherwise only handles argument validation, help/version output, and exec error reporting.

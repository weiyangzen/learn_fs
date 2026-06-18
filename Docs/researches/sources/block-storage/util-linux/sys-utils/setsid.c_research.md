# File Research: sources/block-storage/util-linux/sys-utils/setsid.c

This file implements `setsid(1)`, running a command in a new session. It optionally forks first, always forks when the current process is already a process-group leader, then calls `setsid()` in the child path before executing the requested command.

Options include `--ctty` to set the controlling terminal with `TIOCSCTTY`, `--fork` to force forking, and `--wait` to have the parent wait and return the child’s exit status. Without `--wait`, the parent exits successfully after forking.

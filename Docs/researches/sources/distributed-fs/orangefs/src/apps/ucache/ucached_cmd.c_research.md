<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/ucache/ucached_cmd.c -->
# sources/distributed-fs/orangefs/src/apps/ucache/ucached_cmd.c

## Purpose
Implements the `ucached_cmd` command-line client for starting `ucached` and sending daemon commands through FIFOs.

## Important APIs, Types, And Functions
`main` is the only function. It recognizes command characters `s`, `c`, `d`, `x`, and `i`. It uses `UCACHED_STARTED`, `FIFO1`, `FIFO2`, `BUFF_SIZE`, and `UCACHED_INFO_FILE` from `ucached.h`.

## Control Flow
For `s`, it checks `/tmp/ucached.started`, removes stale FIFOs, launches `ucached` with `system`, writes the started marker, and returns. Other commands open `FIFO1` for writing, send the command plus optional argument, open `FIFO2` for reading, print the response, and for `i` additionally opens and prints `UCACHED_INFO_FILE`.

## State And Persistence
It mutates the daemon marker and can remove FIFOs before daemon start. It reads daemon-created info and response data but does not manage shared memory directly.

## Dependencies And Integration Points
Depends on the daemon FIFO protocol, `usrint.h`, POSIX file APIs, and matching constants in `ucached.h`. It is the operator-facing control plane for `ucached.c`.

## Risks And Test Signals
Risks include race-prone started-file detection, no verification that `system("ucached")` succeeded, unsafe `strcat` into a fixed command buffer for optional arguments, blocking opens when daemon/FIFOs are absent, and `i` mode reading a possibly missing info file after printing a success response. Test signals are start idempotency, create/destroy/info/exit round trips, daemon-not-running failures, long optional argument handling, and stale marker/FIFO recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/ucache/ucached_cmd.c -->

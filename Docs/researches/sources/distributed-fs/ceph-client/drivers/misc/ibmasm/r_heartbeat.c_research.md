# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/r_heartbeat.c

## Purpose
`r_heartbeat.c` implements reverse heartbeats: user-triggered periodic dot commands from the OS driver to the IBM ASM service processor.

## Important APIs, Types, and Functions
Public functions are `ibmasm_init_reverse_heartbeat()`, `ibmasm_start_reverse_heartbeat()`, and `ibmasm_stop_reverse_heartbeat()`. Static packed `rhb_dot_cmd` is a `sp_read` command `4.3.6`.

## Control Flow
Filesystem read starts a loop that allocates one command, repeatedly copies the reverse-heartbeat command into it, executes it, waits for a normal response, increments a failure count on incomplete responses, then sleeps up to `REVERSE_HEARTBEAT_TIMEOUT` unless stopped. The loop exits on three failures, signal, or explicit stop. Stop sets `rhb->stopped` and wakes the wait queue.

## State and Persistence
Per-open `struct reverse_heartbeat` stores wait queue and stopped flag. No state persists after close; the service processor observes the heartbeat commands.

## Dependencies and Integration Points
It depends on command execution, dot-command layout, wait queues, signal handling, and `ibmasmfs` reverse-heartbeat file operations.

## Risks and Edge Cases
The function returns `1` after three failures rather than a conventional negative errno. Signals and explicit stop both return `-EINTR`. The reusable command object is reset in-place each iteration.

## Test Signals
Validate normal repeated response, three-failure exit, write-triggered stop, signal interruption, command allocation failure, and concurrent read exclusion in ibmasmfs.

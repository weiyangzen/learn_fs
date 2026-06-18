<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/ucache/ucached.c -->
# sources/distributed-fs/orangefs/src/apps/ucache/ucached.c

## Purpose
Implements the `ucached` daemon that creates, destroys, and inspects System V shared-memory regions used by the OrangeFS user cache. It also exposes a FIFO command protocol for `ucached_cmd`.

## Important APIs, Types, And Functions
Important functions are `main`, `run_as_child`, `execute_cmd`, `create_ucache_shmem`, `destroy_ucache_shmem`, `ucached_lockchk`, `clean_up`, and `check_rc`. Global state includes FIFO descriptors, the command buffer, `ucache_avail`, parent/child `pid`, and `locked_time` for every cache block. It uses `ucache`, `ucache_aux`, `ucache_lock`, `ucache_stats`, and lock/file-table helpers from the user-cache library.

## Control Flow
`main` enables gossip logging, daemonizes, optionally creates shared memory through a child, creates two FIFOs, and polls `FIFO1` for commands. Valid commands create (`c`), destroy (`d`), produce info (`i`), or exit (`x`). Creation first obtains/initializes the auxiliary lock segment, locks the global lock, initializes statistics, then attaches or creates the cache segment and file table. Destruction marks selected segments with `IPC_RMID`.

## State And Persistence
The daemon persists `/tmp/ucached.log`, `/tmp/ucached.info`, `/tmp/ucached.started`, two FIFOs, and SYSV shared-memory segments keyed by `/etc/fstab` plus IDs `l` and `m`. Cleanup removes FIFOs and, if enabled, marks shared memory for deletion at parent exit.

## Dependencies And Integration Points
Depends on SYSV IPC, POSIX daemon/FIFO/poll APIs, `gossip`, and `src/client/usrint/ucache.h`. `ucached_cmd.c` is the intended client. The daemon must coordinate with user processes attaching to the same shared-memory cache.

## Risks And Test Signals
Risks include world-writable FIFO permissions, hard-coded `/tmp` and `/etc/fstab` keys, blocking FIFO writes, incomplete cleanup if `mkfifo` fails after daemonization, `shmat` checked against `NULL` instead of `(void *)-1`, unused `ucache_avail`, and TODO-only hung-lock recovery. Test signals are start/create/destroy/info/exit command cycles, restart after stale shared memory, concurrent attach behavior, FIFO timeout behavior, and verifying no orphaned segments or FIFOs remain after shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/ucache/ucached.c -->

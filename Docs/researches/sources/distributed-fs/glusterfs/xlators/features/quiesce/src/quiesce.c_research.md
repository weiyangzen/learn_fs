# sources/distributed-fs/glusterfs/xlators/features/quiesce/src/quiesce.c

## Purpose

`quiesce.c` implements a translator that temporarily queues filesystem operations while its child is unavailable or not in pass-through mode, optionally tries failover hosts, and drains queued operations when connectivity returns or failover attempts are exhausted.

## Important APIs, Types, and Functions

Core queue/failover helpers are `gf_quiesce_enqueue`, `gf_quiesce_dequeue`, `gf_quiesce_dequeue_start`, `gf_quiesce_timeout`, `__gf_quiesce_start_timer`, `gf_quiesce_populate_failover_hosts`, `__gf_quiesce_perform_failover`, `gf_quiesce_failover_cbk`, and `gf_quiesce_local_wipe`. Lifecycle and event hooks are `mem_acct_init`, `init`, `reconfigure`, `fini`, and `notify`.

The `fops` table covers modifying fops, lock/xattr state-changing fops, writev, and a retransmittable group including lookup, stat, fstat, access, readlink, getxattr, fgetxattr, open, readv, flush, fsync, statfs, opendir, readdir, readdirp, fsyncdir, and seek.

## Control Flow

When `priv->pass_through` is false, fop wrappers create a `call_stub_t` for the corresponding default resume function and append it to `priv->req` under lock. Enqueue also starts a timer if one is not active. When the child reports `GF_EVENT_CHILD_UP`, `notify` starts a dequeue thread and marks pass-through true, causing queued stubs to resume and new fops to wind to the child. When the child reports down, pass-through is set false and the timer is started.

On timer expiry, `gf_quiesce_timeout` tries failover if pass-through is still false. `__gf_quiesce_perform_failover` picks the first untried configured failover host and sends a child `setxattr` with `CLIENT_CMD_CONNECT`; the failover callback restarts the timer. If all failover hosts have been tried or setup fails, pass-through is set true and the queue is drained, allowing operations to complete rather than remain quiesced indefinitely.

For selected read-like or idempotent fops, pass-through mode uses custom callbacks that save enough request state in `quiesce_local_t`. If the child returns `-1/ENOTCONN`, the callback creates a default resume stub and queues it for later retry. Many state-changing fops do not use retransmit callbacks; they are either queued before winding or directly wound while pass-through is true.

## State and Persistence Behavior

All state is in memory: `quiesce_priv_t` stores the timer, pass-through flag, queue lock, request list and size, dequeue thread, local mem pool, timeout, failover host string, and parsed failover list. `quiesce_local_t` stores copied loc/fd/name/dict/vector/iobref/offset/flags needed to retry a fop after ENOTCONN. There is no disk persistence; queued operations are lost if the process exits.

## Dependencies and Integration Points

The translator depends on Gluster timers, pthread creation, call stubs, default resume/callback functions, list and lock primitives, dicts, mem pools, `valid_internet_address`, child notify events, and the client command `CLIENT_CMD_CONNECT` sent through setxattr. It requires exactly one child.

## Risks and Edge Cases

Queue growth is unbounded except by memory, and `queue_size` is only informational. Some pass-through paths allocate `quiesce_local_t` without checking allocation failure before dereferencing. `gf_quiesce_populate_failover_hosts` calls `continue` on invalid host tokens without advancing `addr_tok`, which can loop indefinitely on an invalid first token. `fini` does not clean queued stubs, failover list entries, or active timers, so shutdown during queued state can leak or leave callbacks racing. Retransmission is intentionally disabled or not implemented for many state-changing fops; nevertheless, queued pre-wind operations will run later and may observe changed application context.

## Test Signals

Tests should cover child-down queueing for every fop class, child-up dequeue thread behavior, timer expiry with no failover hosts, failover host parsing including invalid entries, failover setxattr success/failure, ENOTCONN retransmit for lookup/stat/read/open/readdir/seek paths, memory cleanup of locals, O_APPEND stripping in create/open, reconfigure of timeout and failover hosts, and process shutdown with nonempty queues.

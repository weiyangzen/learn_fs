<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/barrier/src/barrier.c -->
# sources/distributed-fs/glusterfs/xlators/features/barrier/src/barrier.c

## Purpose
Feature translator that delays acknowledgements for a narrow class of mutating or durability-sensitive FOPs while a runtime barrier is enabled. The child operation still runs immediately; only the callback unwind to the caller is queued.

## APIs, Types, and Functions
Exports FOPs for `rmdir`, `unlink`, `rename`, `removexattr`, `fremovexattr`, `truncate`, `ftruncate`, `fsync`, and synchronous `writev`. Callback wrappers use `BARRIER_FOP_CBK` to either queue a callback stub or unwind immediately. Helpers include `barrier_local_set_gfid()`, `barrier_local_free_gfid()`, `__barrier_enable()`, `__barrier_disable()`, `__barrier_enqueue()`, `__barrier_dequeue()`, `barrier_dequeue_all()`, `barrier_timeout()`, `notify()`, `reconfigure()`, `barrier_dump_priv()`, and queue dump helpers.

## Control Flow, State, and Persistence
`init()` allocates `barrier_priv_t`, initializes the queue/lock, reads `barrier` and `barrier-timeout`, and optionally starts a timer. Each barrier-class FOP winds to the child and stores an allocated GFID in `frame->local`. When the child callback fires, the macro locks private state; if enabled, it creates a callback stub and appends it to `priv->queue`; otherwise it frees local GFID and unwinds. Disabling via translator op/reconfigure or timeout cancels the timer, splices the queue to a local list, marks disabled, and resumes queued stubs. State is volatile memory: queue, timer, timeout, enabled flag, and queue size.

## Dependencies and Integration
Uses GlusterFS timer, call-stub, list, lock, default notify, xlator option, and statedump APIs. Runtime control comes through `GF_EVENT_TRANSLATOR_OP` with a `barrier` dict key and through settable volume options.

## Risks and Test Signals
Risks include callback-stub allocation failure disabling the barrier, queued callback growth until timeout/disable, synchronous writes without `O_SYNC`/`O_DSYNC` bypassing the barrier, cancellation races around timer changes, and `barrier_dump_priv()` returning `-1` even after a successful dump. Test signals are enabling/disabling through volume set and translator op, queued acknowledgement ordering, timeout release, statedump queue contents with GFIDs/paths, sync-write filtering, and cleanup on fini.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/barrier/src/barrier.c -->

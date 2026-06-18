<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/barrier/src/barrier.h -->
# sources/distributed-fs/glusterfs/xlators/features/barrier/src/barrier.h

## Purpose
Private interface and shared macro support for the barrier translator.

## APIs, Types, and Functions
Defines `barrier_priv_t` with timer, lock, queued callback stubs, timeout, queue size, enabled flag, and padding. Declares queue/timer enable/disable helpers. The `BARRIER_FOP_CBK` macro implements callback-time gating: create a callback stub while enabled, enqueue it, or unwind and release frame-local GFID when not queued.

## Control Flow, State, and Persistence
The macro centralizes the callback control flow for all barriered FOPs and is responsible for switching from normal unwind to queued deferred unwind. State is volatile and owned by `barrier_priv_t`.

## Dependencies and Integration
Depends on `barrier-mem-types.h`, call stubs, GlusterFS stack unwind macros, locks, lists, and logging. Included only by `barrier.c`.

## Risks and Test Signals
Macro complexity can obscure ownership of `_stub`, `frame->local`, and lock/unlock paths. Stubs must match each FOP callback signature exactly. Test signals are build coverage of every macro expansion and runtime tests for allocation-failure, enabled, disabled, and timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/barrier/src/barrier.h -->

# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/qmgr.c

## Purpose
Provides sequence-id allocation and lifetime management for falcon command/message queue pairs.

## Important APIs, types, and functions
`nvkm_falcon_qmgr_new()` allocates a queue manager and initializes 16 sequence completions. `nvkm_falcon_qmgr_seq_acquire()` finds a free sequence bit, marks it pending, and returns the sequence. `nvkm_falcon_qmgr_seq_release()` clears callback state, reinitializes completion, and frees the sequence bit.

## Control flow, state, and persistence
Sequence allocation is protected by a mutex and a bitmap. Release uses atomic `clear_bit()` without taking the mutex. Sequence records persist for the queue manager lifetime and are reused across commands.

## Dependencies and integration points
Used by `cmdq.c` and `msgq.c`. Depends on completions, bitmap helpers, mutexes, and falcon owner logging.

## Risks and test signals
Only 16 simultaneous sequences are supported; exhaustion returns `-EAGAIN`. Signals include "no free sequence available" logs and successful command/reply correlation.

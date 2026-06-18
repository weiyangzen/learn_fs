# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/msgq.c

## Purpose
Implements falcon-to-host message queues and response dispatch for firmware command sequences.

## Important APIs, types, and functions
`nvkm_falcon_msgq_new()`, `nvkm_falcon_msgq_init()`, `nvkm_falcon_msgq_empty()`, `nvkm_falcon_msgq_recv()`, `nvkm_falcon_msgq_recv_initmsg()`, and `nvkm_falcon_msgq_del()` manage message queues. Internal helpers open/close the ring, pop data from DMEM, read complete messages, and execute sequence callbacks.

## Control flow, state, and persistence
Message receive locks the queue, reads head/tail, handles wraparound, validates available bytes and maximum message size, then commits the tail. Normal messages are matched by `seq_id` to queue-manager sequences, invoke callbacks, release async sequences, or complete synchronous waits. Init messages use initial registers before the firmware reports final queue indices.

## Dependencies and integration points
Depends on falcon DMEM PIO reads, queue manager sequence state, firmware message layouts, spinlocks, and completions. SEC2 interrupt handlers call into this path.

## Risks and test signals
Oversized messages, unknown sequences, or bad size accounting break command completion. Signals include message-too-big, unknown-sequence, init-size mismatch, and successful SEC2 command replies.

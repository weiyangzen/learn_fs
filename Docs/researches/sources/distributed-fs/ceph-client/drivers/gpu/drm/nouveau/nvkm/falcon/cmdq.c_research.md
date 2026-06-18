# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/cmdq.c

## Purpose
Implements host-to-falcon command queues used by firmware RTOS interfaces such as SEC2 ACR commands and unload requests.

## Important APIs, types, and functions
`nvkm_falcon_cmdq_new()`, `nvkm_falcon_cmdq_init()`, `nvkm_falcon_cmdq_send()`, `nvkm_falcon_cmdq_fini()`, and `nvkm_falcon_cmdq_del()` manage command queues. Internal helpers check room, open/close the ring, push data to DMEM, and insert rewind commands.

## Control flow, state, and persistence
Queue readiness is completion-based and established from firmware init messages. Send waits for readiness, acquires a sequence, stamps `seq_id` and status/interrupt flags, writes the command ring, and either waits for a reply completion or leaves an async sequence. Ring space is computed from firmware head/tail registers with 4-byte alignment and rewind support.

## Dependencies and integration points
Depends on falcon DMEM PIO writes, queue manager sequence tracking, `nvfw_falcon_cmd`, completions, mutexes, and firmware message queues.

## Risks and test signals
Queue full or reply timeout returns errors. Signals include queue init debug logs, timeout waiting for queue space/ready/reply, and successful SEC2 command callbacks.

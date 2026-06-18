# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-dev-v3.c

## Purpose

`ccp-dev-v3.c` implements version 3 CCP hardware operations and device initialization. It allocates key storage blocks, converts generic `ccp_op` objects into v3 command request registers, handles queue interrupts, starts one kthread per hardware queue, registers the device/RNG/DMAengine, and tears all resources down on destroy.

## Important APIs, Types, And Functions

- `ccp_alloc_ksb()`/`ccp_free_ksb()` allocate/free contiguous key storage block entries from the global KSB bitmap.
- `ccp_get_free_slots()` reads queue depth from `CMD_Q_STATUS`.
- `ccp_do_cmd()` writes `CMD_REQ1..6`, then `CMD_REQ0`, waits for interrupts when needed, logs errors, deletes failed/stopped jobs, and refreshes free slots.
- `ccp_perform_aes()`, `ccp_perform_xts_aes()`, `ccp_perform_sha()`, `ccp_perform_rsa()`, `ccp_perform_passthru()`, and `ccp_perform_ecc()` fill v3 register command words for each engine.
- `ccp_irq_bh()` reads global IRQ status, updates per-queue status/error fields, acknowledges bits, and wakes queue waiters.
- `ccp_irq_handler()` disables interrupts and dispatches bottom-half work.
- `ccp_init()` discovers queues, allocates per-queue DMA pools, reserves per-queue KSBs, configures queue registers and interrupts, starts kthreads, registers the device, hwrng, and DMAengine.
- `ccp_destroy()` unregisters DMA/RNG/device, disables interrupts, stops kthreads, frees IRQ/pools, and completes queued commands with `-ENODEV`.
- `ccp3_actions`, `ccpv3_platform`, and `ccpv3` expose the v3 operation table and platform/PCI data.

## Control Flow

Device init reads the queue mask, allocates a DMA pool per available queue up to `max_q_count`, reserves two KSBs per queue for key/context use, programs per-queue status register addresses and interrupt masks, clears stale status, requests a CCP IRQ, starts queue kthreads, enables interrupts, adds the device to the global CCP list, registers hwrng, then registers DMAengine. Queue kthreads come from generic `ccp_cmd_queue_thread()` and call `ccp_run_cmd()`, which uses the vdata action table here.

For each operation, `ccp_perform_*()` encodes engine-specific fields into six request registers. `ccp_do_cmd()` serializes request-register access with `ccp->req_mutex`, writes request words, starts the command, and waits on `cmd_q->int_queue` when interrupt-on-completion is set. IRQ bottom-half records command errors and wakes waiters.

## State And Persistence Behavior

Persistent driver state includes per-queue DMA pools, KSB reservations, free slot counts, interrupt masks/status, command errors, wait queues, kthreads, and global KSB bitmap/wait queue. Hardware state is command request registers, delete-job register, IRQ mask/status, queue status, and optional ARM64 queue cache settings.

## Dependencies And Integration Points

This file depends on generic CCP device scheduling in `ccp-dev.c`, operation conversion in `ccp-ops.c`, SP IRQ helpers, DMA pools, hwrng and DMAengine registration. It integrates through `struct ccp_actions` selected by platform/PCI vdata.

## Risks And Edge Cases

- KSB allocation returns 0 on interrupted wait, which also represents "no allocation"; callers must treat 0 as failure.
- Register command submission is protected by one mutex because request registers are shared across queues.
- Reading queue depth resets some status information according to comments, so free-slot refresh is deliberately limited.
- Destroy completes queued and backlog commands with `-ENODEV`; active hardware commands are stopped by kthread/IRQ teardown ordering.
- DES3 is not supported in v3 action table, so higher-level registration must gate DES3 by version.

## Test Signals

Signals include v3 queue discovery, KSB allocation/free under concurrent AES/SHA/RSA workloads, IRQ wakeups, command error logging and delete-job behavior, suspend/resume through generic queue suspension, hwrng reads, DMAengine memcpy, and clean teardown with queued command callbacks.

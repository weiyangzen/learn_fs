# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-mcq.c

## Purpose

`ufs-mcq.c` implements UFSHCI multi-circular-queue support: queue count policy, queue memory allocation, MCQ register setup, completion polling, queue cleanup, and abort handling.

## Important APIs, Types, and Functions

Exports include `ufshcd_mcq_config_mac()`, `ufshcd_mcq_queue_cfg_addr()`, `ufshcd_mcq_read_cqis()`, `ufshcd_mcq_write_cqis()`, `ufshcd_mcq_poll_cqe_lock()`, `ufshcd_mcq_make_queues_operational()`, `ufshcd_mcq_enable()`, `ufshcd_mcq_enable_esi()`, and `ufshcd_mcq_config_esi()`. Internal/public core functions include `ufshcd_mcq_init()`, `ufshcd_mcq_memory_alloc()`, `ufshcd_mcq_sq_cleanup()`, and `ufshcd_mcq_abort()`. Module parameters configure read/write, read-only, and poll queue counts.

## Control Flow

Init validates requested queue counts against controller capacity, asks variant ops to configure MCQ resources and operational runtime mappings, allocates `ufs_hw_queue` state, and initializes locks. Memory allocation creates coherent SQE and CQE rings per queue. Operational setup programs base addresses, doorbell/status offsets, CQ/SQ attributes, interrupt enables, and queue-local cached register pointers. CQ polling updates tail, processes CQEs by deriving task tags, completes requests, clears CQEs, and advances head. Cleanup stops a SQ, writes cleanup task identity, waits for completion, and restarts the queue. Abort first searches/nullifies an unfetched SQE, then falls back to device task abort.

## State and Persistence Behavior

State is per-HBA queue arrays, DMA rings, queue head/tail slots, `mcq_enabled`, queue-count fields, and controller registers. It is runtime-only, rebuilt after reset or reinit.

## Dependencies and Integration Points

It depends on block-mq request mapping, SCSI commands, UFSHCI MCQ registers, DMA coherent allocation, variant ops for platform-specific resource layout, error handling, task abort helpers, and inline queue helpers in `ufshcd-priv.h`.

## Risks and Test Signals

Risks include invalid module queue counts, at least-one non-poll queue requirement, UFSHCI 4.0 indirect tag derivation, CQE double-completion avoidance during EH, broken RTC quirks causing cleanup/abort failure, and races around SQ stop/start with `sq_mutex`. Test signals include MCQ init on capacity boundaries, reset reinitialization, interrupt and polling completions, HCI 4.0 vs 4.1 tags, SQ cleanup return codes, abort of queued/fetched/completed commands, and vendor-op failure paths.

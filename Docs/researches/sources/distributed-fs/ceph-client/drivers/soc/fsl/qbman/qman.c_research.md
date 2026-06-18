# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman.c

## Purpose
Implements the DPAA QMan software portal runtime and the exported frame queue, congestion group, enqueue, dequeue, and allocator APIs used by QMan clients. It manages cache-enabled and cache-inhibited portal rings, per-CPU affine portals, QMan management commands, frame queue state transitions, interrupt dispatch, message-ring processing, and cleanup of stale or leaked hardware resources.

## Important APIs, types, and functions
The file defines the portal-private ring state for EQCR, DQRR, MR, and MC through `struct qm_eqcr`, `struct qm_dqrr`, `struct qm_mr`, `struct qm_mc`, and low-level `struct qm_portal`. The public runtime object is `struct qman_portal`, which embeds the low-level portal, interrupt source mask, `vdqcr_owned`, static dequeue command state, portal config, congestion-group snapshot and callbacks, and work items.

Exported APIs include portal tuning and polling (`qman_dqrr_set_ithresh`, `qman_portal_set_iperiod`, `qman_p_poll_dqrr`, `qman_p_irqsource_add`, `qman_p_irqsource_remove`), affine lookup (`qman_affine_cpus`, `qman_affine_channel`, `qman_get_affine_portal`), frame queue lifecycle (`qman_create_fq`, `qman_init_fq`, `qman_schedule_fq`, `qman_retire_fq`, `qman_oos_fq`, `qman_destroy_fq`), data movement (`qman_enqueue`, `qman_volatile_dequeue`), congestion groups (`qman_create_cgr`, `qman_delete_cgr_safe`, `qman_update_cgr_safe`, `qman_query_cgr_congested`), and resource pools (`qman_alloc_fqid_range`, `qman_release_fqid`, `qman_alloc_pool_range`, `qman_release_pool`, `qman_alloc_cgrid_range`, `qman_release_cgrid`).

## Control flow and state behavior
Portal creation initializes EQCR in valid-bit production mode, DQRR in push/dequeue-consume mode, MR in valid-bit production plus CI consume mode, and MC response tracking. It then requests the portal IRQ, checks that EQCR, DQRR, and MR are clean or drainable, initializes SDQCR defaults, and registers the portal as CPU-affine. Interrupts flow through `portal_isr`: fast DQRR availability is handled inline by `__poll_portal_fast`, while slow events schedule per-CPU work for congestion and message-ring processing. The fast poll loop demultiplexes scheduled versus volatile dequeues, invokes each FQ's `dqrr` callback, consumes or parks DQRR entries according to the callback result, and clears volatile dequeue ownership on completion.

Frame queue state is mirrored in `struct qman_fq` flags and `state`. Management commands transition OOS, parked, scheduled, retired, and changing states; asynchronous FQRN, FQRL, and FQPN messages complete state transitions in `qm_mr_process_task`. `fq_table` is a valloced lookup table with two slots per FQID, allowing full-service and `NO_MODIFY` references. Dynamic FQID release has an explicit memory ordering comment: the table entry is cleared before `gen_pool_free` to avoid reallocation while a stale pointer remains visible.

## Dependencies and integration points
The code depends on `qman_priv.h`, `include/soc/fsl/qman.h`, DPAA cache helpers, genalloc pools seeded by `qman_ccsr.c`, platform portal config from `qman_portal.c`, Linux IRQ, workqueue, waitqueue, DMA, SMP, and optional PAMU stashing. It exposes symbols consumed by network, crypto, and other DPAA users.

## Risks and test signals
The highest risk areas are lockless portal ring tracking, callback reentrancy, volatile dequeue ownership, cleanup loops that poll hardware state, and management-command timeouts. `qman_enqueue` currently returns `0` even when no EQCR entry is available, which callers cannot distinguish from success. Cleanup paths are hardware-dependent and can busy-wait while draining DQRR/MR. Tests in `qman_test_api.c` and `qman_test_stash.c` exercise enqueue/dequeue, retirement, OOS, FQID cleanup, DMA stashing, and multi-CPU callback routing.

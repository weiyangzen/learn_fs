# sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_ddcb.c

## Purpose
`card_ddcb.c` implements GenWQE Device Driver Control Block queueing. It allocates requests, formats DDCBs for the service layer, starts or appends work on the hardware queue, handles completion through interrupt-woken polling, purges timed-out work, and sets up/tears down the service-layer queue and IRQs.

## Important APIs, Types, and Functions
Public entry points include `ddcb_requ_alloc()`, `ddcb_requ_free()`, `__genwqe_enqueue_ddcb()`, `__genwqe_wait_ddcb()`, `__genwqe_execute_raw_ddcb()`, `__genwqe_purge_ddcb()`, `genwqe_ddcbs_in_flight()`, `genwqe_setup_service_layer()`, `genwqe_finish_queue()`, and `genwqe_release_service_layer()`. Internal queue helpers include `queue_empty()`, `queue_enqueued_ddcbs()`, `queue_free_ddcbs()`, `get_next_ddcb()`, `enqueue_ddcb()`, `copy_ddcb_results()`, and `genwqe_check_ddcb_queue()`. Interrupt handlers are split between PF and VF with `genwqe_pf_isr()` checking GFIR error state and `genwqe_vf_isr()` only waking the queue thread.

## Control Flow
Queue setup resets privileged cards, fills queue register offsets, allocates coherent DDCB memory, initializes every entry as completed, starts a kernel thread, configures MSI, requests the IRQ, and finally marks the card used. Execution copies a user/kernel `genwqe_ddcb_cmd` into the next free DDCB, fills command fields, copies ASIV or ATS+ASIV depending on SLU generation, calculates ICRC, optionally enables completion interrupt, then uses compare-and-swap on the previous DDCB's SHI/HSI word to append with NEXT or taps the hardware queue offset register. The card thread calls `genwqe_check_ddcb_queue()`, copies ASV/status/timestamps back to the request, validates VCRC, marks the request finished, wakes the per-DDCB wait queue and busy waiters, and advances the active ring index. Waiters time out via `GENWQE_DDCB_SOFTWARE_TIMEOUT` and must purge failed requests.

## State and Persistence
Persistent runtime state is in `cd->queue`: coherent DDCB ring, request pointer array, per-entry wait queues, sequence numbers, active/next indices, register offsets, and counters for in-flight/completed/busy cases. DDCB state is hardware-shared big-endian memory; request state mirrors completion state in `ddcb_requ.req_state`. There is no disk persistence.

## Dependencies and Integration Points
The file depends on `card_base.h`, `card_ddcb.h`, coherent DMA allocation from `card_utils.c`, GenWQE MMIO helpers, PCI/MSI IRQ services, kernel wait queues, kthreads, and CRC-ITU-T. It is called by `card_dev.c` ioctls and flash helpers, and its debug data feeds user-requested `genwqe_debug_data`.

## Risks and Edge Cases
Queue correctness depends on strict ring invariants and memory barriers around SHI/HSI updates. Timeout and purge paths must avoid reusing fetched-but-not-completed DDCBs. `queue_wake_up_all()` wakes `ddcb_act` repeatedly rather than each index, which is worth reviewing in fatal paths. Completion VCRC mismatches are logged but do not by themselves fail the request after hardware completion. The file contains several old-SLU/new-ATS conditionals, so regressions can be generation-specific.

## Test Signals
Useful signals include DDCB enqueue/completion under interrupt and polling modes, nonblocking `-EBUSY`, timeout plus purge behavior, VCRC/ICRC error injection, card removal with in-flight requests, PF GFIR recovery wakeups, and debug-data copyout. Ring wrap tests should stress `ddcb_act`, `ddcb_next`, full-queue behavior, and busy waiters.

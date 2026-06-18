# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptvf_main.c

## Purpose
This file is the PCI VF driver entry point. It probes VF devices, initializes PF/VF mailbox and interrupts, receives capabilities from the PF, initializes CN10K LMTST support, attaches LFs for kernel crypto, allocates pending queues/tasklets, registers LF interrupts, and registers Crypto API algorithms.

## Important APIs and functions
Driver entry points are `otx2_cptvf_probe()` and `otx2_cptvf_remove()`. Mailbox setup uses `cptvf_pfvf_mbox_init()`, `cptvf_register_interrupts()`, and interrupt enable/disable helpers. LF setup and teardown are handled by `cptvf_lf_init()` and `cptvf_lf_shutdown()`. Software queue/tasklet helpers are `alloc_pending_queues()`, `free_pending_queues()`, `init_tasklet_work()`, `cleanup_tasklet_work()`, and `lf_sw_init()/lf_sw_cleanup()`.

## Control flow
Probe allocates VF state, enables PCI/DMA/BARs, maps registers, sets hardware capability flags, initializes PF/VF mailbox and bounce buffer, registers mailbox interrupt, sends ready, selects CPT block and hardware ops, requests capabilities, optionally switches to CN10K SGv2 builder, initializes LMTST, then calls `cptvf_lf_init()`. LF init queries SE and AE engine group numbers, reads kernel VF LF limit, attaches LFs with the combined group mask, gets MSI-X offsets, allocates pending queues and tasklets, registers misc/done interrupts, sets affinity, marks LFs started, and registers crypto algorithms. Remove reverses LF, mailbox, and LMTST resources.

## State and persistence
Runtime state includes VF mailbox, VF id, engine capabilities, LF queues, pending queues, tasklets, IRQ affinity, LMTST memory, and Crypto API registrations. The LF atomic state gates request submission. No persistent storage is used.

## Dependencies and integration points
This file depends on PF mailbox services for engine groups, KVF limits, and capabilities; LF common setup for hardware queues; request manager for tasklet completion; algorithm code for Crypto API registration; and CN10K helpers for hardware ops/LMTST.

## Risks and edge cases
Probe ordering is strict: capability messages require mailbox readiness, and crypto registration requires fully initialized LFs and interrupts. Error paths must avoid registering algorithms before tasklets/queues are ready and must unwind interrupts before freeing pending queues. `cptvf_lf_shutdown()` disables queues directly rather than calling full `otx2_cptlf_shutdown()` so it can unregister crypto and interrupts first.

## Test signals
Signals include VF probe/remove, PF unavailable probe defer, valid SE/AE group lookup, KVF LF count selection, pending queue allocation failure unwind, tasklet completion of crypto requests, IRQ affinity cleanup, CN10K SGv2 path selection from capability bit 35, and crypto unregister when the last VF exits.

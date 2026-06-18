# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptlf.c

## Purpose
This file implements common CPT Local Function lifecycle and interrupt handling for both PF inline-IPsec use and VF kernel-crypto use. It initializes LF hardware queues, attaches resources through mailbox, programs engine-group masks and priority, registers MSI-X handlers, manages IRQ affinity, and tears LF state down.

## Important APIs and functions
Exported APIs include `otx2_cptlf_init()`, `otx2_cptlf_shutdown()`, `otx2_cptlf_register_misc_interrupts()`, `otx2_cptlf_register_done_interrupts()`, `otx2_cptlf_unregister_misc_interrupts()`, `otx2_cptlf_unregister_done_interrupts()`, `otx2_cptlf_set_irqs_affinity()`, and `otx2_cptlf_free_irqs_affinity()`. Local helpers configure done interrupt coalescing, AF LF priority and group mask, context input length, hardware queue init/cleanup, and interrupt enable bits.

## Control flow
`otx2_cptlf_init()` validates device/register pointers, initializes LF slots and MMIO/LMT addresses, attaches resources, allocates instruction queues, disables/configures/enables hardware queues, then sets priority and engine group masks. Optional context input length override is written through AF registers. Interrupt registration installs one misc and one done handler per LF; misc interrupts log and acknowledge hardware error bits, while done interrupts acknowledge completion counts and schedule the LF tasklet. Shutdown disables queues, frees queues, detaches resources, and clears `lfs_num`.

## State and persistence
LF state lives in `struct otx2_cptlfs_info` and its `lf[]` array: queue DMA memory, MSI-X offsets, registered IRQ flags, affinity masks, LMT line pointers, slot numbers, and optional tasklet pointers. Hardware queue state is MMIO state. There is no persistent storage.

## Dependencies and integration points
This file uses shared mailbox helpers for AF register reads/writes and resource attach/detach/reset. `otx2_cptlf.h` supplies inline queue operations. VF main owns tasklet and pending-queue allocation before registering done interrupts. PF mailbox code uses LF init for inline IPsec LFs.

## Risks and edge cases
Queue setup depends on mailbox response state and valid MSI-X offsets. Error unwinds must disable queues, free DMA memory, and detach resources in order. Misc interrupt handling uses an `else if` chain, so simultaneous bits are acknowledged one at a time. Done interrupts require `lf->wqe`; PF inline LFs register only misc interrupts, while VF LFs must create tasklet work before enabling done interrupts.

## Test signals
Expected signals are clean LF init/shutdown under PF and VF probes, correct IRQ registration/unregistration after partial failure, no pending/inflight timeout warnings during disable, tasklet scheduling on completed VF crypto requests, and affinity masks distributed across online CPUs.

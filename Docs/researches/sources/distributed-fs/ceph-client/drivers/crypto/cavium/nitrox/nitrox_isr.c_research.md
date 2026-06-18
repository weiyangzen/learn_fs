# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_isr.c

Purpose: registers MSI-X interrupt handlers for NITROX PF queues and non-ring errors/mailboxes, handles completion interrupts, clears hardware error sources, and supports a reduced SR-IOV PF interrupt mode.

Important APIs and control flow: `nitrox_register_interrupts()` allocates all MSI-X vectors, registers per-packet-ring `nps_pkt_slc_isr()` handlers that schedule response tasklets, and registers vector 192 for `nps_core_int_isr()`. The core ISR reads `NPS_CORE_INT_ACTIVE`, clears NPS core/packet/POM/PEM/LBC/EFL/BMI errors, invokes `nitrox_pf2vf_mbox_handler()` on mailbox interrupts, and requests resend. `nitrox_unregister_interrupts()` frees vectors and kills tasklets. SR-IOV register/unregister variants allocate only the non-ring vector.

State and persistence: persistent state is `ndev->qvec`, tasklets, IRQ affinity hints, and hardware interrupt status cleared by W1C writes. Completion tasklets drain response lists in request-manager code.

Dependencies and integration points: depends on PCI MSI-X, `nitrox_hal.h` re-enable helpers, mailbox code, and request manager `pkt_slc_resp_tasklet()`.

Risks and test signals: risks include assuming vector 192 exists in `qvec` allocation, using `get_cpu_mask(num_online_cpus())` for non-ring affinity, empty recovery work for NPS core tasklet, and SR-IOV unregister freeing the same vector in a loop if more than one qvec became valid. Test signals include packet completion IRQ scheduling response processing, error interrupts clearing and re-enabling affected rings/ports, mailbox ISR dispatch, IRQ affinity set/cleared, and clean unregister after partial registration failure.

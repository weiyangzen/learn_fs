# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptvf_main.c

Purpose: implements the Thunder CPT virtual-function PCI driver, including queue allocation, MSI-X setup, PF mailbox negotiation, hardware queue programming, interrupt handling, tasklet completion processing, and crypto algorithm initialization.

Important APIs and control flow: `cptvf_probe()` enables PCI, maps BAR0, allocates two MSI-X vectors, enables mailbox/software-error interrupts, checks PF readiness, allocates command/pending queues and tasklets, sends QLEN/group/priority mailbox messages, registers DONE IRQ, sends VF_UP, and calls `cvm_crypto_init()`. Queue helpers allocate circular coherent command chunks and pending arrays. `cptvf_device_init()` disables the VQ, clears doorbell/inflight, writes queue base, sets coalescing, enables the VQ, and marks ready. Misc and done IRQ handlers clear errors, handle mailbox messages, ACK done counts, and schedule response tasklets.

State and persistence: per-VF persistent state includes coherent command rings, pending queues, tasklets, IRQ affinity masks, PF-negotiated VF identity/type, VQ registers, and crypto registration reference state.

Dependencies and integration points: depends on PCI/MSI-X, DMA coherent memory, PF mailbox protocol, request manager `vq_post_process()`, and crypto algorithm registration.

Risks and test signals: risks include cleanup labels after mid-probe failures not always freeing software queues or DONE IRQ state, duplicated `return NULL` line in WQE lookup, no inflight drain on remove, and fixed VF group/priority values. Test signals include VF probe after PF SR-IOV enable, mailbox ACKs, queue base alignment, DONE interrupts scheduling tasklets, crypto self-tests completing, and remove sending VF_DOWN and freeing queues.

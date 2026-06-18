# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_main.c Research

## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_main.c

### Purpose
`otx_cptvf_main.c` is the PCI VF driver for OcteonTX CPT. It allocates command and pending queues, initializes VF hardware registers, handles misc and done interrupts, manages sysfs VF controls, performs PF mailbox setup, and registers crypto algorithms.

### Important APIs, Types, And Functions
Important functions are `otx_cptvf_probe()`, `otx_cptvf_remove()`, `cptvf_sw_init()`, queue allocation/free helpers, tasklet setup, `cptvf_device_init()`, register writers for VQ control/doorbell/inflight/done wait/saddr, interrupt handlers `cptvf_misc_intr_handler()` and `cptvf_done_intr_handler()`, IRQ affinity helpers, and sysfs show/store functions for `vf_type`, `vf_engine_group`, `vf_coalesc_time_wait`, and `vf_coalesc_num_wait`.

### Control Flow, State, And Persistence
Probe enables PCI, requests BARs, sets a 48-bit DMA mask, maps VF BAR0, allocates MSI-X vectors, requests misc IRQ, enables mailbox and software-error interrupts, sends READY to PF, allocates command chunks as a circular DMA instruction queue, allocates pending queues, initializes tasklets, sends queue size to PF, programs VQ base/coalescing/doorbell/inflight registers, binds to an engine group, sets priority, requests done IRQ, enables done interrupts, sets affinity, sends VF_UP, registers crypto algorithms, and creates sysfs attributes. Done interrupts acknowledge completion count and schedule a high-priority tasklet to call request post-processing. Remove first sends VF_DOWN; on success it removes sysfs, unregisters crypto algorithms, frees IRQ affinity, IRQs, queues, BARs, regions, and drvdata.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on PCI/MSI-X, DMA coherent allocation, PF mailbox, request-manager post-processing, crypto algorithm registration, sysfs, tasklets, and hardware register definitions. Risks include command chunk circular pointer correctness, cleanup asymmetry when VF_DOWN times out, tasklet scheduling after queue teardown, coalescing bounds, IRQ affinity allocation failure handling, and `free_done_irq` label behavior after failed done IRQ request. Test signals include VF probe/remove with PF present and absent, mailbox timeout, queue allocation failure unwind, completion interrupt processing, misc error interrupts, sysfs group rebinding, coalescing writes at min/max bounds, and crypto request completion under load.

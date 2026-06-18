# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/mbox_init.c

Purpose: Implements CN20K-specific RVU mailbox memory allocation, mailbox region mapping, mailbox interrupt handlers/registration, interrupt enable/disable, and additional CINT/QINT context setup for non-OTX2/non-CN20K paths.

Important APIs/types/functions: Public functions include `cn20k_register_afvf_mbox_intr()`, `cn20k_rvu_enable_mbox_intr()`, `cn20k_rvu_unregister_interrupts()`, `cn20k_register_afpf_mbox_intr()`, `cn20k_rvu_get_mbox_regions()`, `cn20k_rvu_mbox_init()`, `cn20k_free_mbox_memory()`, `cn20k_rvu_disable_afvf_intr()`, `cn20k_rvu_enable_afvf_intr()`, and `rvu_alloc_cint_qint_mem()`. Static handlers are `cn20k_afvf_mbox_intr_handler()` and `cn20k_mbox_pf_common_intr_handler()`. Static `rvu_alloc_mbox_memory()` backs AFPF/AFVF mailbox allocations. `cn20k_mbox_ops` binds handler callbacks.

Control flow: Mailbox init first gates on `is_cn20k()`, assigns CN20K mailbox ops, programs mailbox size config registers, and allocates qmem. AFPF allocation writes each PF mailbox IOVA into RVUM PF address registers; AFVF allocation writes the VF mailbox base to the PF VF mailbox address register. Interrupt registration allocates four `rvu_irq_data` entries for PF or VF interrupt groups, fills status registers, device ranges, queue-work handlers, vector numbers, names, and calls `request_irq()` with CN20K handlers. Handlers clear interrupt status, trace active interrupt bits, enforce memory barriers around mailbox memory, and enqueue RVU work. Enable/disable functions program W1S/W1C interrupt masks for PF/VF mailbox, FLR, and ME sources over the first and second 64-VF banks.

State and persistence: Persistent state includes `rvu->ng_rvu->rvu_mbox_ops`, `pf_mbox_addr`, `vf_mbox_addr`, `rvu->irq_allocated[]`, IRQ names, and hardware mailbox config/address/mask registers. Mailbox qmem remains allocated until `cn20k_free_mbox_memory()`.

Dependencies and integration: Depends on RVU register accessors (`rvu_read64/write64`, `rvupf_read64/write64`), qmem allocation, PCI IRQ vectors, tracepoints, workqueue dispatch (`rvu_queue_work`), and CN20K register definitions in `reg.h`.

Risks: IRQ registration error paths return immediately without freeing previously requested IRQs in the same loop, so caller teardown must handle partial allocation through `irq_allocated`. `INTR_MASK(hw->total_pfs - 64)` must be safe when counts are below 64. Mailbox region pointers use `phys_to_virt()` on qmem bases; platform memory mapping assumptions matter. AFVF enable path enables `RVU_PF_VFME_INT_ENA_W1SX(1)` only for the second bank, unlike disable which clears bank 0 and bank 1.

Test signals: CN20K PF/VF mailbox ping, interrupts across PF ranges 0-63 and 64+, VF counts above and below 64, FLR/ME interrupt handling, qmem leak checks on remove, and partial IRQ registration failure injection validate this file.

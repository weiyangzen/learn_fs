# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_isr.c

Purpose: this file manages SNIC MSI-X interrupt mode, requests/free IRQs, and implements the three interrupt handlers for WQ ACK completions, firmware I/O completions, and error/notify events.

Important APIs, types, and functions: `snic_isr_msix_wq()` services WQ completions and returns credits on `SNIC_MSIX_WQ`. `snic_isr_msix_io_cmpl()` services firmware CQ completions and returns credits on `SNIC_MSIX_IO_CMPL`. `snic_isr_msix_err_notify()` returns all credits, logs queue errors, and queues link handling. `snic_set_intr_mode()` allocates exactly three MSI-X vectors and sets vNIC interrupt mode. `snic_request_intr()` assigns names/handlers and calls `request_irq()`. `snic_free_intr()` and `snic_clear_intr_mode()` reverse setup.

Control flow: probe discovers resource counts, calls `snic_set_intr_mode()`, allocates resources, requests interrupts, then unmasks them. Each ISR updates stats, services the relevant queue, and returns vNIC interrupt credits so hardware can reassert interrupts.

State and persistence: runtime state includes `snic->msix[]`, `intr[]`, `intr_count`, `err_intr_offset`, and ISR stats. No persistent state exists.

Dependencies and integration: depends on PCI MSI-X APIs, vNIC interrupt credit helpers, SNIC WQ/FW CQ completion handlers, and queue error/link handlers.

Risks: only MSI-X is supported, with hard assertions if another mode is used. Resource counts must support one WQ, one firmware CQ, and one error/notify vector. Error/notify ISR queues link work that is partly unimplemented for non-DAS.

Test signals: probe on hardware with insufficient MSI-X vectors, IRQ request failure rollback, high-rate WQ and firmware CQ interrupts, error notify interrupts, and unbind while interrupts are active.

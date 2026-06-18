# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_guest.c

Purpose: implements the VMCI PCI guest personality. It probes VMware VMCI PCI hardware, maps register access, allocates datagram DMA or I/O buffers, sends hypervisor datagrams, receives interrupt-driven datagrams/events, manages notification bitmap memory, and exposes active guest context state.

Important APIs/functions: `vmci_guest_init()/exit()` register/unregister the PCI driver. `vmci_guest_probe_device()` performs device enable, BAR mapping, buffer allocation, capability negotiation, global device publication, notification bitmap registration, host capability check, event subscription, IRQ setup, interrupt enabling, and VSOCK callback. `vmci_guest_remove_device()` undoes those resources. `vmci_send_datagram()` serializes outgoing hypercalls under `vmci_dev_spinlock`. `vmci_get_vm_context_id()` lazily sends `VMCI_GET_CONTEXT_ID`. Interrupt handlers call `vmci_dispatch_dgs()`, `vmci_process_bitmap()`, or wake DMA waiters.

Control flow: probe prefers MMIO BAR1 and DMA datagram support, falling back to I/O port access except on ARM64. It negotiates datagram, PPN64, notifications, and DMA datagram capabilities by writing selected caps back to the device. Incoming datagrams are read into a buffer, walked until invalid headers/end markers, then dispatched either as VMCI events or guest datagram callbacks. Shared interrupt mode reads and clears interrupt causes; exclusive MSI-X vectors split datagram, bitmap, and DMA completion work.

State/persistence: singleton globals `vmci_dev_g`, `vmci_pdev`, `vm_context_id`, `ctx_update_sub_id`, `use_ppn64`, and `vmci_num_guest_devices` represent live guest device state. Device buffers and notification bitmap are DMA-coherent where MMIO/DMA is used. No durable state is stored.

Dependencies/integration: integrates with Linux PCI, DMA, IRQ, MMIO/I/O helpers, VMCI event subscriptions, doorbell bitmap registration/scanning, datagram guest handler dispatch, queue-pair guest endpoint cleanup, and VSOCK callback activation.

Risks: `vmci_write_data()` computes `result` but `vmci_send_datagram()` separately reads `VMCI_RESULT_LOW_ADDR`, so result sequencing depends on device semantics. DMA read waits on `buffer_header->busy` and relies on DMA interrupt wakeups. Global singleton publication must be cleared before freeing buffers. Datagram parsing handles partial, oversized, and page-aligned I/O-port cases; off-by-one mistakes here would corrupt dispatch.

Test signals: PCI probe/remove under MMIO and I/O-port modes, capabilities missing/fallback paths, MSI-X/MSI/legacy interrupt setup, DMA datagram send/receive completion, notification bitmap callbacks, context ID update events, invalid/oversized incoming datagrams, and cleanup after mid-probe failures.

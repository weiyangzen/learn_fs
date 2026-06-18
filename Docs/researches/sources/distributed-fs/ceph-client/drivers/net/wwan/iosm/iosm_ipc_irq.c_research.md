# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_irq.c

Purpose: implements IOSM doorbell writes and MSI interrupt acquisition/release. It is the lowest-level interrupt bridge between AP driver code and CP hardware.

Important functions: `ipc_doorbell_fire`, `ipc_acquire_irq`, and `ipc_release_irq`; internal `ipc_write_dbell_reg` computes the doorbell register address from the mapped BAR, IRQ number, and configured offset; `ipc_msi_interrupt` forwards MSI instances to `ipc_imem_irq_process` unless the PCIe object is in s2idle suspend.

Control flow: probe maps registers and calls `ipc_acquire_irq`, which allocates exactly one MSI vector and registers a threaded IRQ handler with `IRQF_ONESHOT`. Runtime callers fire doorbells for HPDA, IPC state transitions, and sleep control. Remove/error paths call `ipc_release_irq`, freeing requested IRQs and PCI vectors.

State/dependencies: state lives in `iosm_pcie` fields `ipc_regs`, `nvec`, doorbell offsets, PCI IRQ base, and `suspend` bit. Dependencies include PCI MSI APIs, threaded IRQs, IO writes, and imem IRQ dispatch. Risks include bad BAR/offset configuration, `irq - pci->irq` instance assumptions, suspend races dropping interrupts, and release loops depending on `nvec`. Test signals: MSI allocation failure, request_irq failure unwind, doorbell write offsets, IRQ ignored while suspended, and vector bounds returning `IRQ_NONE`.

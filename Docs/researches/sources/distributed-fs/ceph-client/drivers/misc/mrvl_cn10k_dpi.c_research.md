# sources/distributed-fs/ceph-client/drivers/misc/mrvl_cn10k_dpi.c

## Purpose
This PCI misc driver controls the Marvell Octeon CN10K DPI physical function. It initializes DPI engines, exposes PF tuning ioctls, handles SR-IOV PF/VF mailbox requests, and configures per-VF DMA queue registers.

## Important APIs, types, and functions
Core data structures are `dpipf`, `dpipf_vf`, `dpivf_config`, `dpi_mbox`, and `dpi_mbox_message`. Key functions are `dpi_probe()`, `dpi_remove()`, `dpi_init()`, `dpi_fini()`, `dpi_irq_init()`, `dpi_pfvf_mbox_setup()`, `dpi_pfvf_mbox_destroy()`, `dpi_mbox_intr_handler()`, `dpi_pfvf_mbox_work()`, `queue_config()`, `dpi_queue_init()`, `dpi_queue_fini()`, `dpi_mps_mrrs_config()`, `dpi_engine_config()`, and `dpi_dev_ioctl()`.

## Control flow and state
Probe enables PCI, maps BARs, initializes global DMA/engine/EBUS registers, creates per-VF mailbox structures for up to 32 VFs, allocates a full MSI-X vector set, requests the PF/VF mailbox IRQ, enables mailbox interrupts, registers a miscdevice, and exposes simple SR-IOV configuration. When a VF mailbox interrupt arrives, the handler schedules per-VF work; work reads mailbox words, validates the VF ID, opens or closes queues, programs queue buffer/aura/PF function IDs/stream IDs, optionally sets WQE completion offset, and writes ACK/NACK.

## State and persistence behavior
Runtime state is per-PF and per-VF in memory: MMIO base, miscdevice, mailbox work/locks, VF config, and setup flags. Hardware registers hold active queue and engine configuration until reset/remove. There is no disk persistence.

## Dependencies and integration points
It depends on PCI, MSI-X, miscdevice, SR-IOV helpers, user-copy, compat ioctl, workqueues, and UAPI `uapi/misc/mrvl_cn10k_dpi.h`. It integrates with VFs through PF/VF mailbox registers and with userspace through `/dev/<module-name>` ioctls.

## Risks and test signals
Risks include mailbox trust of VF-provided fields, queue reset timeout handling, MSI-X vector count assumptions, work cancellation races, ioctl reserved-field validation, MPS/MRRS encoding, and engine FIFO/MOLR bounds. Test signals include PF probe/remove, misc ioctl validation, SR-IOV enable/disable, VF queue open/close mailbox ACK/NACK, interrupt delivery, queue reset timeout injection, and cleanup with pending mailbox work.

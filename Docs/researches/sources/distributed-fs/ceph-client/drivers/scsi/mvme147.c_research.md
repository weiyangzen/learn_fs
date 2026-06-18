# sources/distributed-fs/ceph-client/drivers/scsi/mvme147.c

Purpose: provides the built-in SCSI host driver for Motorola MVME147 m68k systems using a WD33C93 SCSI core and board PCC DMA/interrupt registers. It allocates a single Scsi_Host, wires WD33C93 callbacks, enables board interrupts, and scans the bus.

Important APIs/types/functions: `mvme147_init()` and `mvme147_exit()` are module lifecycle hooks. `mvme147_intr()` dispatches either WD33C93 SCSI-port interrupts or acknowledges DMA interrupts. `dma_setup()` programs PCC DMA registers from `WD33C93_scsi_pointer(cmd)`, handles cache push/invalidate, and records direction. `dma_stop()` disables DMA. `mvme147_host_template` exposes WD33C93 queueing, abort, host reset, proc info, queue depth, and command-private size.

Control flow: init exits successfully without registering anything on non-MVME147 machines. On MVME147 it allocates hostdata, sets fixed MMIO base and IRQ, initializes WD33C93 register pointers, configures hostdata flags, registers SCSI-port and DMA IRQs, enables PCC SCSI/DMA interrupts, calls `scsi_add_host()`, and scans. Exit removes the host, frees both IRQs, and drops the host reference.

State and persistence: the only global state is `mvme147_shost`. Runtime DMA state is in WD33C93 hostdata and PCC registers; no persistent storage is changed.

Dependencies and integration points: depends on m68k `MACH_IS_MVME147`, `asm/mvme147hw.h`, legacy `virt_to_bus()`, cache management, SCSI midlayer, and the shared `wd33c93` core. Built from the parent SCSI Makefile with `wd33c93.o`.

Risks and test signals: this is board-specific legacy code with fixed physical addresses and manual cache coherency. The error path after second IRQ failure frees only the SCSI-port IRQ, as intended, but an `scsi_add_host()` failure uses the same label and does not free the DMA IRQ, which is a cleanup risk. Test signals are m68k cross-builds, boot on MVME147, IRQ/DMA transfer completion, host reset/abort paths, and fault injection for IRQ and host-add failures.

# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_regs_defs.h

Defines the EFA register ABI: reset reasons, BAR register offsets, and masks for version, capabilities, admin queue setup, AENQ setup, interrupts, device control/status, MMIO register reads, and EQ doorbells.

Important definitions include `enum efa_regs_reset_reason_types`, `EFA_REGS_*_OFF` offsets, and masks for version fields, DMA width, reset/admin timeouts, AQ/ACQ/AENQ depths and entry sizes, interrupt enable, reset/fatal status, MMIO read request/response, and EQ doorbell arm/EQN.

There is no executable control flow. These constants drive lower-level reset, version validation, queue initialization, interrupt masking, MMIO read, and EQ notification logic. Register fields are persistent device state; the driver writes control and doorbell registers and polls status/read-response registers.

Dependencies are consumers in EFA common and main driver code. Risks include destructive writes from incorrect offsets/masks, missed reset/status transitions, and reset reason mismatches with firmware diagnostics. Test signals include reset completion, version validation, admin queue bring-up, MMIO read responses, interrupt masking, and EQ doorbell operation.

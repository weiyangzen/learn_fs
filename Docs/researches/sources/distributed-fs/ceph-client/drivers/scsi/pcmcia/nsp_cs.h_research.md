# sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/nsp_cs.h

Purpose: register, state, and prototype header for the 16-bit NinjaSCSI PCMCIA driver.

Important APIs/types: defines base/indexed registers, IRQ/status bits, SCSI bus-phase masks, transfer-mode flags, `sync_data`, `nsp_hw_data`, `scsi_info_t`, phase/data-direction/burst enums, and `BUFFER_ADDR()` for SG access.

Control flow/state: bus monitor constants drive `nspintr()` phase switching. `nsp_hw_data` persists host state: I/O/MMIO addresses, current command, FIFO/timer counters, transfer mode, SDTR table, message buffer, info string, lock, and PCMCIA state. Command phase/SG cursor lives in SCSI command private storage.

Dependencies/integration: consumed by `nsp_cs.c`, `nsp_io.h`, `nsp_message.c`, and optional `nsp_debug.c`; depends on PCMCIA and SCSI structures.

Risks/test signals: old assumptions include initiator ID 7, 8 targets, direct use of `struct scsi_pointer`, and restricted 64-bit suitability. Test compile coverage, phase decoding, PIO/MMIO transfer, and reset/SDTR state transitions.

# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_sli.h

## Purpose
`lpfc_sli.h` is a central private contract for the Emulex/Broadcom LPFC Fibre Channel driver shared by SLI-3 and SLI-4 code. It defines the software wrappers around IOCBs, WQEs, mailbox commands, SLI rings, host-buffer queues, statistics, link counters, and per-I/O buffers that the rest of the LPFC stack uses to submit FC, FCP, NVMe/FC, NVMET, ELS, BSG, and management work to adapter firmware.

## Important APIs, Types, And Functions
Important types include `struct lpfc_iocbq`, `LPFC_MBOXQ_t`, `struct lpfc_sli_ring`, `struct lpfc_sli`, and `struct lpfc_io_buf`. `struct lpfc_iocbq` is the common command/completion envelope; it stores list linkage, I/O/XRI tags, SLI-4 `union lpfc_wqe128`, SLI-3 `IOCB_t`, completion status, timeout, vport, DMA buffers, node pointer, VMID tag, and completion callbacks. `LPFC_MBOXQ_t` wraps SLI-3 mailbox and SLI-4 MQE payloads with vport/node/context buffers, completion callback, extended SGE metadata, and flags such as `LPFC_MBX_WAKE`.

The ring model is represented by `struct lpfc_sli_ring`, `struct lpfc_sli3_ring`, and `struct lpfc_sli4_ring`. It tracks transmit, completion, posted-buffer, IOCB-continuation queues, ring masks for unsolicited receive dispatch, command-available callbacks, statistics, and SLI-version-specific backing state. `struct lpfc_sli` is the HBA-level SLI state: active rings, mailbox queues, active mailbox pointer, mailbox timeout timer, IOCB lookup table, last IOTAG, statistics start time, and link-stat reset offsets. `struct lpfc_io_buf` is the shared fast-path I/O buffer for SCSI and NVMe, containing SGL DMA state, current IOCB, hardware queue pointer, flags, completion status/result, segment counts, node pointer, and protocol-specific command/response fields.

## Control Flow
This header has no standalone executable flow. It shapes runtime flow in implementation files: allocation paths fill `lpfc_iocbq` or `lpfc_io_buf`, issue paths place them on ring or WQ queues, interrupt paths recover them by IOTAG/XRI and dispatch callbacks, and completion paths use the stored protocol context to call SCSI, NVMe, ELS, BSG, or mailbox completion logic. Mailbox flow is similarly dictated by `LPFC_MBOXQ_t`: callers prepare `u.mb` or `u.mqe`, attach buffers and a completion callback, queue the command, and either block on a wait context or complete asynchronously through `mbox_cmpl`.

SLI ring flags (`LPFC_DEFERRED_RING_EVENT`, `LPFC_CALL_RING_AVAILABLE`, `LPFC_STOP_IOCB_EVENT`) gate ring scheduling and completion processing. I/O command flags (`LPFC_IO_FCP`, `LPFC_IO_NVME`, `LPFC_IO_NVMET`, `LPFC_IO_VMID`, `LPFC_EXCHANGE_BUSY`, DIF flags, abort flags, and outstanding flags) are the compact state transitions carried through issue, abort, timeout, and completion paths.

## State And Persistence
All state described here is volatile kernel memory owned by `struct lpfc_hba`, vports, queues, or per-command allocations. Persistent storage is not modified by this header. The primary lifetime boundaries are HBA lifetime for `struct lpfc_sli`, ring lifetime for `struct lpfc_sli_ring`, mailbox-command lifetime for `LPFC_MBOXQ_t`, and command/pool lifetime for `struct lpfc_io_buf`.

Synchronization is implied by fields and comments: ring queues use `ring_lock`, mailbox state is protected by SLI/HBA locks in implementation files, and `lpfc_io_buf.buf_lock` protects simultaneous abort/completion races. The lookup table `iocbq_lookup` persists command identity between issue and completion and is especially sensitive to IOTAG allocation/release ordering.

## Dependencies And Integration Points
The header depends on LPFC hardware definitions from `lpfc_hw.h` and `lpfc_hw4.h`, Linux list, timer, spinlock, waitqueue, DMA, SCSI, NVMe/FC, and debugfs conditional definitions through surrounding includes. Integration points include LPFC SCSI (`lpfc_scsi.c`), ELS/discovery, mailbox, SLI interrupt, NVMe initiator/target, BSG, VMID, debugfs, and fabric scheduler paths.

## Risks And Edge Cases
The same wrapper structures carry multiple protocol interpretations, so stale flags or union members can cause incorrect completion dispatch. IOTAG/XRI lookup correctness is critical because completions arrive asynchronously and abort/timeout paths may race firmware completion. The header also exposes many flag bitmasks with overlapping lifecycle meanings; missing a clear/set operation can leak queue depth, keep an I/O on a completion queue, or lose a deferred free. Debugfs fields are conditionally compiled, so code using timing/error-injection fields must stay guarded.

## Test Signals
Useful signals are clean compile coverage across SLI-3, SLI-4, debugfs, SCSI-only, NVMe, and NVMET configurations; stress I/O with aborts and timeouts; mailbox wait and async completion tests; IOTAG/XRI leak checks; ring full and command-available callback paths; VMID-tagged I/O; DIF insert/strip/pass-through cases; and unload checks proving mailbox, IOCB, ring, and I/O-buffer lists drain to zero.

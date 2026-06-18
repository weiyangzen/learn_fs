# sources/distributed-fs/ceph-client/drivers/scsi/megaraid/mega_common.h

## Purpose
`mega_common.h` defines common in-kernel structures and helpers for the MegaRAID low-level drivers. It abstracts SCSI command block state, adapter state, list locks, SCSI-to-adapter conversions, logical/physical device mapping, debug logging expectations, assertions, and DMA block descriptors.

## Important APIs and Types
`scb_t` is the common command envelope, with driver-specific CCB pointer, list link, serial number, SCSI command pointer, state, DMA direction/type, mapped device channel/target, and completion status. `adapter_t` stores tasklet, PCI, SCSI host, lock, quiesce flag, outstanding command count, kernel and user SCB pools, pending/completed lists, SG limit, device ID table, low-level RAID device pointer, SCSI limits, IRQ, internal buffer, firmware/BIOS versions, CDB size, HA state, max sectors, queue depth, and detach state.

Key macros are `SCSIHOST2ADAP`, `SCP2ADAPTER`, `MRAID_IS_LOGICAL`, `MRAID_IS_LOGICAL_SDEV`, and `MRAID_GET_DEVICE_MAP`, which translate SCSI requests to firmware logical-drive IDs or physical channel/target pairs.

## Control Flow, State, Dependencies, and Risks
Execution lives in the low-level driver, but the state machine is encoded here: SCBs move through free, active, pending, issued, completed, and back to free. `adapter_t.quiescent` is used as a stop-posting counter by the mailbox driver, and `being_detached` blocks management calls during removal. Dependencies include kernel PCI, DMA, SCSI, interrupt, list, delay, lock, and module APIs. Risks include macro coupling to initialized `device_ids`, host-private pointer assumptions, user/kernel SCB separation, and confusing `quiescent` semantics. Test signals include correct virtual logical channel mapping, physical passthrough addressing, hot-remove rejection, and no SCB pool collision.

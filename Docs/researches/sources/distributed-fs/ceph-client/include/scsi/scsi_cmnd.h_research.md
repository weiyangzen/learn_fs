<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_cmnd.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_cmnd.h

## Purpose
This header defines `struct scsi_cmnd`, the SCSI mid-layer command object embedded in block requests, plus data-buffer, scatterlist, DMA, protection-information, residual, status-byte, and request conversion helpers.

## Important APIs, Types, And Functions
Important types are `struct scsi_data_buffer`, legacy `struct scsi_pointer`, `enum scsi_cmnd_submitter`, `struct scsi_cmnd`, `enum scsi_prot_operations`, `enum scsi_prot_flags`, and `enum scsi_prot_target_type`. Helpers convert between command and request (`scsi_cmd_to_rq()`), access driver-private command allocation (`scsi_cmd_priv()`), complete commands (`scsi_done()`, `scsi_finish_command()`), map DMA, inspect SG lists, copy buffers, compute sector/LBA/logical block count, manage residuals, set/get protection operation/type, access protection SG lists, set/get packed status and host bytes, translate SCSI message bytes, compute transfer length including protection information, build sense, and allocate SCSI requests.

## Control Flow
Commands are allocated as request private data, filled by the block/SCSI mid-layer, submitted to the host template, completed by the LLDD through `scsi_done()`, and finalized by the mid-layer. Inline helpers are used in the hot path for scatterlist iteration, LBA conversion, protection metadata handling, and result-byte updates. Message translation maps parallel-SCSI messages into host-byte error categories.

## State And Persistence
`struct scsi_cmnd` is transient per I/O. It tracks retry budget, submitter, command bytes, data buffers, sense buffer, flags, completion state, host scribble, result, residuals, and protection fields. The fields above the LLDD boundary are explicitly not to be modified by low-level drivers.

## Dependencies And Integration Points
It depends on block multiqueue, DMA mapping, T10 PI, scatterlists, timers, and `scsi_device.h`. It is the primary object exchanged between upper-level drivers, the SCSI core, transports, and LLDD queuecommand/EH callbacks.

## Risks
LLDDs modifying protected fields can corrupt mid-layer accounting. `scsi_get_lba()` assumes sector size is a power-of-two relation to 512-byte sectors. Protection transfer length must match integrity metadata. Packed result-byte updates can clobber unrelated bytes if masks are wrong.

## Test Signals
Exercise command allocation/private data sizing, SG copy helpers, DMA map/unmap fallback builds, residual accounting, status/host byte setting, message-to-host-byte mapping, protection metadata length, sense construction, and queuecommand completion lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_cmnd.h -->

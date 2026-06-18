<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_targ.h -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_targ.h

## Purpose

`mpi_targ.h` defines the MPI target-mode ABI for posting command buffers, receiving target command/error replies, representing FCP/SPI/SSP command and task buffers, assisting target data movement, sending target status, aborting target-mode work, and packing target-mode context reply words.

## Important APIs, Types, and Definitions

- `CMD_BUFFER_DESCRIPTOR` and `MSG_TARGET_CMD_BUFFER_POST_REQUEST` post one or more target command buffers by IO index and 32/64-bit physical address.
- `MSG_TARGET_CMD_BUF_POST_BASE_REQUEST` and `MSG_TARGET_CMD_BUF_POST_LIST_REQUEST` support base-address posting and IO-index list posting; `MSG_TARGET_CMD_BUFFER_POST_BASE_LIST_REPLY` completes base/list post operations.
- Error/priority replies include `MSG_PRIORITY_CMD_RECEIVED_REPLY`, `MSG_TARGET_CMD_BUFFER_POST_ERROR_REPLY`, and `MSG_TARGET_ERROR_REPLY`, with priority reason constants for disconnect, task management, parity, CRC, protocol, busy, and unknown causes.
- Command buffer formats include `MPI_TARGET_FCP_CMD_BUFFER`, `MPI_TARGET_SCSI_SPI_CMD_BUFFER`, `MPI_TARGET_SSP_CMD_BUFFER`, and `MPI_TARGET_SSP_TASK_BUFFER`.
- `MSG_TARGET_ASSIST_REQUEST` describes target data movement and optional automatic status. `MSG_TARGET_ASSIST_EXT_REQUEST` adds bidirectional, multicast, SGL offset chain, T10 EEDP, reference/application tag, and bidirectional length fields.
- `MSG_TARGET_STATUS_SEND_REQUEST` sends status data; response buffers include `MPI_TARGET_FCP_RSP_BUFFER`, `MPI_TARGET_SCSI_SPI_STATUS_IU`, and `MPI_TARGET_SSP_RSP_IU`.
- `MSG_TARGET_MODE_ABORT` and reply abort all command buffers, all IO, exact IO, or exact IO request.
- Context macros pack and unpack IO index, initiator index, alias, and port, with separate obsolete MPI v1.0 host/IOC index forms.

## Control Flow

Target-mode setup posts command buffers either as descriptors, a contiguous base region, or a list of IO indexes. Firmware uses posted buffers to deliver incoming FCP/SPI/SSP command or task IUs and returns context information in reply words. The host then issues target assist for data-in/data-out movement, optionally with auto status or EEDP handling. Status send posts the final protocol status IU or FCP response buffer. Error replies and priority reasons report cases where firmware could not use a posted buffer or target operation failed. Abort requests cancel broad or exact target-mode work.

## State and Persistence Behavior

The header defines transient queue and IO state. Posted command buffers remain firmware-owned until consumed, reposted, or aborted. Reply words carry correlation state across command receive, assist, status, and abort flows. No persistent NVRAM state is declared here, but target-mode behavior depends on port capabilities and configuration from IOC/port facts and config pages.

## Dependencies and Integration Points

The header depends on MPI base types plus `SGE_IO_UNION` and `SGE_SIMPLE_UNION`. `mptbase.h` includes it for target-protocol support. It integrates with `mpi_ioc.h` port protocol flags (`TARGET`), FC/SAS/SPI transport semantics, `mpi_sas.h` SSP concepts, and SAS log info target-mode abort/assist/status codes. Normal Linux initiator drivers may not exercise this path heavily, but control/target-capable builds depend on layout correctness.

## Risks and Edge Cases

Command buffer address mode and IO index masks must match firmware expectations; misuse can hand firmware bad DMA addresses. Several structures have one-element SGL or array tails and require correctly sized message frames. FCP, SPI status IU, and SSP response IU comments note big-endian protocol layout; callers on little-endian hosts must avoid accidental byte swapping beyond the intended wire layout. Extended assist EEDP flags can corrupt protection information if operation, block size, tags, or masks are wrong. Abort operations are disruptive and must target the right reply word or message context. Legacy MPI v1.0 context macros remain part of compatibility behavior.

## Test Signals

Tests should cover descriptor/base/list command-buffer posting, 32-bit and 64-bit buffer modes, context word packing/unpacking, FCP/SPI/SSP command decode, data-in and data-out target assist, auto status, explicit status send, confirmed/high-priority/repost flags, extended assist EEDP modes, and exact/all abort behavior. Negative tests should verify priority/error replies for malformed buffers, bad IO indexes, and target busy/protocol error reasons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_targ.h -->

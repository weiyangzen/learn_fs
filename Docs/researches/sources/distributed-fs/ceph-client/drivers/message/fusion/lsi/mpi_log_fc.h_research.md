<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_log_fc.h -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_log_fc.h

## Purpose

`mpi_log_fc.h` defines Fibre Channel `IOCLogInfo` values returned in MPI reply messages. It is a decode table for FC initiator, FC target, LAN, MPI message-layer, link, context-manager, invalid-field, and state-change log subclasses.

## Important APIs, Types, and Definitions

- `MpiIocLogInfoFc_t` is an enum of 32-bit log values.
- The encoded format is `0xabcccccc`: type nibble `a` is FC log type `2`, subclass nibble `b` identifies firmware area, and the low bits carry subclass-specific detail.
- Initiator codes include out-of-order frame, bad SOF/EOF, overrun, RX other, subprocessor dead, RX SGL overrun, bad receive status, unexpected frame, link failure, and transmit timeout.
- Target codes include missing PDISC/login/class 3/validated login, LIP-disrupted data or response paths, missing data, outbound queue clearing after logout, and waiting-for-data after logout.
- LAN codes cover missing transaction SGL, transaction context ordering, reserved context bits, and invalid SGL flags.
- Link codes cover loop initialization timeout, already initialized loop, link not established, and CRC error.
- Invalid field and state-change ranges reserve the lower 24 bits for byte offsets or state details.

## Control Flow

This header has no runtime control flow. The control path is reply decoding: a Fusion FC command completes with `IOCStatus` and `IOCLogInfo`; driver diagnostic code tests the high nibble/type and subclass bits, then maps the value to the relevant FC failure reason. `mptbase.c` references this file when logging FC IOCLogInfo values.

## State and Persistence Behavior

The values are transient diagnostics attached to a failed or noteworthy reply. They do not create persistent driver state. However, some codes report underlying link, login, loop, or queue states that may influence later recovery, rescan, logout, target reset, or rport handling in the FC transport path.

## Dependencies and Integration Points

The enum integrates with common MPI replies from IOC, SCSI IO, FC direct-access messages, LAN messages, target mode, toolbox, and config operations through the shared `IOCLogInfo` field. It complements `mpi_ioc.h` event IDs and `mpi_fc.h` FC message definitions. `mptbase.c` includes this header for FC log decoding and points diagnostics at it.

## Risks and Edge Cases

The file lacks include guards, so repeated direct inclusion could redefine the enum if not controlled by include topology. Numeric values are ABI diagnostics from firmware; renumbering breaks log interpretation across firmware releases. Some enum entries use lower-case hex suffixes while most use upper-case style, but the numeric values are what matter. Invalid-field and state-change ranges require preserving and decoding lower 24-bit payloads rather than treating only exact enum values as meaningful.

## Test Signals

Tests should inject or capture FC replies with each subclass prefix and verify the driver logs a useful message without corrupting command completion. Error-path tests should include invalid-field offsets, link failures, LIP-disrupted target operations, CT/ELS failures, and LAN-over-FC SGL/context errors. Static checks should ensure no switch assumes the enum is exhaustive for future firmware values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_log_fc.h -->

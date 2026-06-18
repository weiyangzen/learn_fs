<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/libiscsi_tcp.h -->
# sources/distributed-fs/ceph-client/include/scsi/libiscsi_tcp.h

## Purpose
This header defines the common TCP data-path helpers for iSCSI. It gives software TCP transports reusable receive segmentation, scatterlist walking, CRC32C digest, task transmit, and R2T pool support on top of `libiscsi`.

## Important APIs, Types, And Functions
`struct iscsi_segment` tracks a receive or transmit segment, copied byte counts, total counts, digest buffers, optional scatterlist mapping, padding, and a completion callback. `struct iscsi_tcp_recv` stores the current PDU header context and a fixed BHS+AHS buffer. `struct iscsi_tcp_conn` binds TCP receive state and optional RX CRC pointer to a generic `iscsi_conn`. `struct iscsi_tcp_task` tracks DataSN/R2T progress and R2T pools/queues.

APIs include header receive preparation, SKB receive processing, task init/cleanup/xmit, segment completion/unmapping, linear and scatter-gather segment initialization, header digest calculation, TCP connection setup/teardown, R2T pool allocation/free, max-R2T parsing, and connection stats export.

## Control Flow
Receive processing prepares a header segment, consumes SKB bytes into the active segment, validates/pads/digests as needed, and advances through header, AHS, data, and digest stages. Transmit paths initialize task-private TCP state, select unsolicited or R2T data, and send task PDUs through the generic iSCSI session/connection framework.

## State And Persistence
All state is per-task or per-connection memory. Segment fields record progress across partial SKBs. R2T pools and FIFOs persist for the session/task lifetime and are protected by spinlocks for pool-to-queue and queue-to-pool transitions. No durable state is represented.

## Dependencies And Integration Points
The header depends directly on `libiscsi.h`, Linux scatterlists, SKBs, and digest constants from the iSCSI protocol. Low-level TCP transports provide socket or offload glue while reusing these helpers for PDU parsing and stats.

## Risks
Partial SKB handling, padding, and digest boundaries are error-prone. Incorrect scatterlist mapping or atomic unmapping can corrupt data or leak mappings. R2T pool sizing and lock use must handle concurrent recovery and cleanup. Digest offload callers must correctly set the `offloaded` receive flag.

## Test Signals
Use segmented SKB tests, header/data digest validation, padding edge cases, scatterlist offset seeks, R2T queue exhaustion, task cleanup during recovery, max-R2T setting changes, and stats accounting for transmitted/received PDUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/libiscsi_tcp.h -->

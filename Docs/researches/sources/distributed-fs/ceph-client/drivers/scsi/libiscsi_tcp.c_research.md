# sources/distributed-fs/ceph-client/drivers/scsi/libiscsi_tcp.c

## Purpose

`libiscsi_tcp.c` is the TCP data-path companion to `libiscsi.c`. It handles stream segmentation, scatterlist mapping, padding, header/data digest calculation and verification, Data-In placement, R2T processing, Data-Out generation, per-task R2T pools, TCP connection setup, and statistics for software or TCP-like iSCSI transports.

## Important APIs, Types, and Functions

Segment helpers include `iscsi_tcp_segment_done()`, `iscsi_tcp_segment_unmap()`, `iscsi_segment_init_linear()`, `iscsi_segment_seek_sg()`, `iscsi_tcp_dgst_header()`, `iscsi_tcp_hdr_recv_prep()`, `iscsi_tcp_recv_segment_is_hdr()`, and `iscsi_tcp_recv_skb()`. Task and transmit APIs include `iscsi_tcp_task_init()`, `iscsi_tcp_task_xmit()`, `iscsi_tcp_cleanup_task()`, `iscsi_tcp_r2tpool_alloc()`, `iscsi_tcp_r2tpool_free()`, and `iscsi_tcp_set_max_r2t()`. Connection APIs include `iscsi_tcp_conn_setup()`, `iscsi_tcp_conn_teardown()`, and `iscsi_tcp_conn_get_stats()`.

The core structures are `struct iscsi_tcp_conn`, `struct iscsi_tcp_task`, `struct iscsi_segment`, `struct iscsi_r2t_info`, base `struct iscsi_conn`, base `struct iscsi_task`, and SCSI scatterlists. The file consumes the base transport callbacks `init_pdu()`, `alloc_pdu()`, `xmit_pdu()`, and `caps` for digest/padding offload.

## Control Flow

Receive starts with `iscsi_tcp_hdr_recv_prep()`, which initializes a linear segment over the connection header buffer. `iscsi_tcp_recv_skb()` walks the skb with `skb_seq_read()`, copies stream bytes into the current segment, and calls the segment completion callback when the expected bytes are present. Segment completion transparently advances through scatterlist elements, consumes iSCSI padding, and splices in data or header digest bytes when software digesting is active.

When a full header is available, `iscsi_tcp_hdr_recv_done()` reads extra AHS bytes if `hlength` is nonzero, verifies the header digest if needed, and calls `iscsi_tcp_hdr_dissect()`. Dissection validates data length, ITT, unsupported AHS for R2T, and opcode-specific expectations. SCSI Data-In looks up the command task, checks DataSN and target offset via `iscsi_tcp_data_in()`, and if data is present sets the receive segment to the SCSI command's scatterlist at the target offset. SCSI responses, login/text/reject/async payloads, logout, NOP-In, and TMF responses either prepare a linear receive buffer or immediately delegate completion to `libiscsi`.

R2T processing is handled in `iscsi_tcp_r2t_rsp()`. It validates the task, direction, datalen, R2TSN sequencing, logged-in state, nonzero length, negotiated burst expectations, and SCSI buffer bounds. It then takes an R2T object from the task's pool, fills target transfer tag, offset, length, StatSN, and DataSN state, queues it on the task's R2T FIFO, and requeues the task for transmit.

Transmit starts in `iscsi_tcp_task_init()`, which initializes management or SCSI command PDUs and immediate data. `iscsi_tcp_task_xmit()` flushes the current PDU through the transport's `xmit_pdu()`, returns for read or management tasks, and for writes repeatedly obtains unsolicited or target-requested R2T state, allocates a Data-Out PDU, calls `iscsi_prep_data_out_pdu()`, initializes the data segment at the requested offset, and flushes again until no R2T work remains.

## State and Persistence Behavior

All state is volatile. `struct iscsi_segment` tracks one in-progress stream segment: current data pointer or scatterlist entry, copied counts, total size, digest buffers, padding, and completion callback. `struct iscsi_tcp_task` tracks expected DataSN/R2TSN, current Data-In offset, current R2T, a per-task R2T pool, R2T queue, and locks that protect pool-to-queue and queue-to-pool transitions. `struct iscsi_tcp_conn` tracks input header/data parsing state and CRC accumulators. Connection counters in `struct iscsi_conn` are accumulated for transport stats.

Scatterlist highmem mappings are intentionally short-lived. Receive maps pages atomically and unmaps before returning from the skb path. Transmit may use `sendpage_ok()` to avoid mapping pages that the network layer can handle, and otherwise uses a sleepable mapping.

## Dependencies and Integration Points

The file depends on CRC32C, skb sequence helpers, highmem page mapping, scatterlists, libiscsi task/session APIs, SCSI command data buffers, and `iscsi_tcp.h`. It calls back into `libiscsi` for CmdSN updates, task lookup, PDU completion, connection failure, Data-Out header preparation, and connection setup/teardown. It integrates with transports that implement socket send/receive and expose digest or padding offload capabilities.

## Risks and Edge Cases

Stream parsing is sensitive to partial skb delivery, AHS length expansion, 4-byte padding, and digest splicing. Data-In validation must reject bad DataSN or offsets before setting up scatterlist writes. R2T handling must tolerate early command completion by holding a task reference and must not leak R2T objects when cleanup races with requeue/transmit. `iscsi_tcp_set_max_r2t()` frees and reallocates per-task pools after negotiation; callers must not change it while tasks are active. Header/data digest errors trigger connection failure, so offload capability bits must match what hardware actually handled.

The code accepts R2T data lengths greater than `max_burst` with a debug message and attempts execution, which is compatibility-oriented but worth testing with strict targets. Management payloads larger than `ISCSI_DEF_MAX_RECV_SEG_LEN` are rejected even though the protocol can represent larger segments. The host SMP-style scatterlist limitation does not apply here, but multi-sg Data-In correctness depends on `iscsi_segment_seek_sg()` finding a valid offset.

## Test Signals

Key tests include fragmented header and data reception across multiple skbs, header/data digest success and mismatch paths, padding consumption, Data-In into multi-entry scatterlists at nonzero offsets, SCSI response with and without sense payload, login/text/reject/async payload reception near the default receive buffer limit, R2T sequencing, R2T pool exhaustion, unsolicited write data followed by solicited Data-Out, `max_r2t` reconfiguration, and stats counters for tx/rx octets and PDU classes.

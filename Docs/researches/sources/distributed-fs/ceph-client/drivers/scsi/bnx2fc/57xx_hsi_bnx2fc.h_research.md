# sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/57xx_hsi_bnx2fc.h

## Purpose

`57xx_hsi_bnx2fc.h` defines the host-side firmware interface for 57xx/B577xx FCoE offload. It describes exact little-endian work-queue elements, completion entries, doorbells, task contexts, scatter-gather contexts, connection database records, hash entries, and statistics records used by firmware and `bnx2fc_hwi.c`.

## Important APIs, Types, and Definitions

Core types include `b577xx_doorbell_hdr`, `b577xx_doorbell_set_prod`, `b577xx_fcoe_rx_doorbell`, `regpair`, `fcoe_bd_ctx`, `fcoe_sqe`, `fcoe_cqe`, `fcoe_xfrqe`, `fcoe_confqe`, `fcoe_conn_db`, and `fcoe_task_ctx_entry`. Slow-path firmware messages are `fcoe_kwqe_init1/2/3`, `fcoe_kwqe_conn_offload1/2/3/4`, `fcoe_kwqe_conn_enable_disable`, `fcoe_kwqe_conn_destroy`, `fcoe_kwqe_destroy`, `fcoe_kwqe_stat`, and `union fcoe_kwqe`. Completions use `fcoe_kcqe`. FCP, ELS, ABTS, cleanup, FC header, SGL, and statistics layouts are represented by the many `fcoe_*_ctx`, union, payload, and stat structures.

## Control Flow

Adapter init fills KWQEs with queue sizes, task-context PBLs, hash tables, HSI version, and error bitmaps. Session offload submits four connection KWQEs describing queues, DMA memory, MACs, VLANs, FC IDs, payload sizes, sequence counts, and recovery support. Fast-path I/O initializes a task context by XID, posts an SQE, rings a doorbell, and later decodes CQ/KCQ entries according to task type and RX state.

## State and Persistence Behavior

The header owns no software state, but defines persistent DMA-visible state: task contexts, queues, producer/consumer indices, request/response buffers, hash-table chains, and statistics buffers. Endianness annotations and conditional big/little-endian layouts are part of the firmware contract.

## Dependencies and Integration Points

It is included by `bnx2fc.h` and consumed by hardware, I/O, target, and ELS code. It integrates with CNIC KWQ/KCQ submission, PCI coherent DMA, libfc/libfcoe FCP/ELS flows, and bnx2x doorbell MMIO. `bnx2fc_constants.h` supplies the opcode and state values used with these structures.

## Risks and Edge Cases

Structure size, field order, bit shifts, and endian mistakes desynchronize driver and firmware. Queue toggle-bit handling and ring wrap must match firmware exactly. Unions overlay unrelated contexts, so the active interpretation must match task type. DMA address splitting must not truncate or omit endian conversion.

## Test Signals

Signals include firmware init with HSI 2.1, session offload/enable/disable/destroy completions, SQ/CQ/RQ wrap stress, FCP reads/writes with one/two/many SGEs, ELS/TMF middle-path commands, unsolicited ELS frames, error-report CQEs, statistics requests, big-endian builds, and DMA API debug.

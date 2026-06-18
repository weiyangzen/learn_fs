<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/conn.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/conn.c

## Purpose

This file implements the transport used by mlx5 FPGA clients to exchange messages with the FPGA sandbox. It creates a host RoCE RC QP and a matching FPGA QP, maps caller buffers for DMA, posts send/receive WQEs, handles CQ completions, and manages per-device connection resources such as RoCE enablement, UAR, PD, and physical-address mkey.

## Important APIs, types, and functions

- `mlx5_fpga_conn_device_init()` enables RoCE, gets a UAR page, allocates a PD, and creates a PA-mode mkey. `mlx5_fpga_conn_device_cleanup()` tears those resources down.
- `mlx5_fpga_conn_create()` allocates a connection, configures a link-local IPv6 SGID from the local MAC, creates CQ/WQ/QP resources, creates the remote FPGA QP, and transitions both endpoints to active/RTS.
- `mlx5_fpga_conn_destroy()` deactivates the QP, synchronizes completions, destroys FPGA and host QPs, destroys the CQ, clears/frees SGID, and frees the connection.
- `mlx5_fpga_conn_send()` maps a two-entry maximum SG buffer, posts it immediately if SQ space is available, or queues it on the SQ backlog.
- CQ handlers `mlx5_fpga_conn_sq_cqe()`, `mlx5_fpga_conn_rq_cqe()`, and `mlx5_fpga_conn_handle_cqe()` unmap DMA, call completion/receive callbacks, drain backlog, and mark the QP inactive on errors.

## Control flow

Device init is per-FPGA and prepares shared connection resources. Connection creation validates `recv_cb`, reserves/sets an SGID, creates and arms a CQ, creates a host QP, fills an FPGA QPC, creates the FPGA QP, activates the FPGA QP, transitions the host QP through RESET, INIT, RTR, and RTS, and pre-posts receive buffers until the RQ is full. Send submission maps the buffer, locks SQ state, posts or backlogs in order, and rings the UAR doorbell. Completion processing is budgeted by `MLX5_FPGA_CQ_BUDGET`; exhausted budget reschedules the tasklet, otherwise the CQ is rearmed.

## State and persistence

Connection state lives in `struct mlx5_fpga_conn`: host and FPGA QPNs/QPC, CQ work queue, tasklet, host QP WQ, SQ/RQ producer/consumer counters, active flag, SGID index, posted buffer arrays, and backlog list. DMA mappings are transient per posted buffer and must be unmapped on completion or teardown. Receive buffers are owned by the connection and reused after callback return. Send buffers remain caller-owned but must not be modified until the completion callback fires.

## Dependencies and integration points

The implementation depends on mlx5 core QP/CQ/WQ helpers, RoCE GID helpers, DMA mapping APIs, generated IFC layouts, `fpga/cmd.c` for remote FPGA QP lifecycle, and `fpga/sdk.c` for exported SBU connection APIs. It is started only for non-lookaside FPGA modes that participate in network processing.

## Risks

The receive-post loop runs until `mlx5_fpga_conn_post_recv_buf()` fails, relying on RQ fullness to return `-EBUSY`; size bugs could produce excessive allocation. Backlog entries are DMA-mapped before queuing and must always be unmapped by flush/error paths. `mlx5_fpga_conn_flush_send_bufs()` walks the backlog but does not delete entries from the list before connection free, which is acceptable only because the connection is being freed and callbacks own buffer lifetime. Completion handlers set `qp.active` without a single global lock, so teardown and CQ/tasklet synchronization are important.

## Test signals

Tests should cover successful create/connect/destroy, SGID allocation failure cleanup, CQ/QP creation failure cleanup, send when SQ is full, backlog drain order, send and receive completion callbacks, receive repost failure, CQ error syndromes, tasklet budget rescheduling, and destroy while sends/receives are outstanding. DMA debug and lockdep are valuable for this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/conn.c -->

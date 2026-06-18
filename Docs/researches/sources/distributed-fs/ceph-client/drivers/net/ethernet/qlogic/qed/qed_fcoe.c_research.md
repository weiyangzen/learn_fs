# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_fcoe.c

## Purpose
`qed_fcoe.c` implements the `qed` core support layer for FCoE offload. It allocates FCoE per-hwfn state, initializes FCoE task contexts, starts and stops the firmware FCoE function, manages connection handles and firmware CIDs, posts FCoE ramrods for connection offload and termination, exposes device and queue information to the upper FCoE client, gathers FCoE statistics, and exports a `struct qed_fcoe_ops` table to protocol drivers.

## Important APIs, Types, And Functions
`struct qed_fcoe_conn` is the central per-connection object. It stores list linkage, ownership behavior, driver and firmware connection ids, DMA/PBL addresses for SQ, transfer queue, confirmation/response queue, termination params, encoded source/destination MAC fields, FC payload/timer/vlan/queue settings, FC source/destination ids, flags, and default queue index.

Slowpath ramrod helpers include `qed_sp_fcoe_func_start()`, `qed_sp_fcoe_func_stop()`, `qed_sp_fcoe_conn_offload()`, and `qed_sp_fcoe_conn_destroy()`. Allocation and lifecycle helpers are `qed_fcoe_alloc()`, `qed_fcoe_setup()`, `qed_fcoe_free()`, `qed_fcoe_allocate_connection()`, `qed_fcoe_free_connection()`, `qed_fcoe_acquire_connection()`, and `qed_fcoe_release_connection()`.

Client-facing operation implementations include `qed_fill_fcoe_dev_info()`, `qed_register_fcoe_ops()`, `qed_fcoe_start()`, `qed_fcoe_stop()`, `qed_fcoe_acquire_conn()`, `qed_fcoe_release_conn()`, `qed_fcoe_offload_conn()`, `qed_fcoe_destroy_conn()`, `qed_fcoe_stats()`, and `qed_get_protocol_stats_fcoe()`. The exported module entrypoints are `qed_get_fcoe_ops()` and `qed_put_fcoe_ops()`.

## Control Flow
Core driver resource allocation calls `qed_fcoe_alloc()` for FCoE personalities, creating `p_hwfn->p_fcoe_info` and its free list. `qed_resc_setup()` later calls `qed_fcoe_setup()`, which initializes the lock and prepares every configured task context by zeroing it, setting timer logical-client valid bits, and marking FCoE task connection type.

The upper FCoE client obtains ops through `qed_get_fcoe_ops()`, calls `.fill_dev_info` to learn common device information, BDQ producer addresses, WWPN/WWNN, and CQ count, registers callbacks with `.register_ops`, and starts offload with `.start`. `qed_fcoe_start()` posts `FCOE_RAMROD_CMD_ID_INIT_FUNC`, sets `QED_FLAG_STORAGE_STARTED`, initializes `cdev->connections`, and optionally returns TID memory layout to the caller.

Connection setup starts with `.acquire_conn`, which allocates a hash wrapper, acquires a FCoE CID from the context manager, obtains or allocates a `qed_fcoe_conn`, computes `fw_cid`, inserts the wrapper into `cdev->connections`, and returns the doorbell address if requested. `.offload_conn` copies caller-provided queue DMA addresses, timers, MACs, FC ids, VLAN, flags, and default queue index into the connection and posts `FCOE_RAMROD_CMD_ID_OFFLOAD_CONN`. `.destroy_conn` sets the termination params DMA address and posts `FCOE_RAMROD_CMD_ID_TERMINATE_CONN`. `.release_conn` removes the hash entry, returns the connection to the free list, and releases the CID.

Function stop requires all connections to have been returned. `qed_fcoe_stop()` rejects stop when `cdev->connections` is non-empty, acquires a PTT, posts `FCOE_RAMROD_CMD_ID_DESTROY_FUNC`, clears the storage-started flag, and releases the PTT. `qed_fcoe_free()` is part of core resource teardown and frees cached connection DMA memory from the free list before freeing `p_fcoe_info`.

## State And Persistence Behavior
FCoE driver state is in `p_hwfn->p_fcoe_info`, the connection free list, `cdev->connections`, `QED_FLAG_STORAGE_STARTED`, protocol callback pointers in `cdev->protocol_ops.fcoe`, `cdev->ops_cookie`, and FCoE fields under `p_hwfn->pf_params.fcoe_pf_params`. Connection DMA pages for transfer and confirmation queues are allocated coherently and cached on the free list for reuse. CID ownership is persisted in the context manager until release. Firmware-visible state is created and destroyed through slowpath ramrods and task context memory.

Statistics are read directly from TSTORM and PSTORM memory through PTT reads and translated into `qed_fcoe_stats` or `qed_mcp_fcoe_stats`. `qed_get_protocol_stats_fcoe()` combines firmware counters with optional upper-client login-failure counters.

## Dependencies And Integration Points
This file depends on `qed_dev.c` for resource setup, FCoE personality detection, queue-manager PQ mapping, BDQ resources, PTT acquisition, and lifecycle calls. It uses context management (`qed_cxt_*`), slowpath queue APIs (`qed_sp_init_request()`, `qed_spq_post()`), LL2 common ops, MCP function WWN data, register address macros, storm context layouts, Linux DMA coherent allocation, kernel hash tables, and exported `linux/qed/qed_fcoe_if.h` client contracts. It is conditionally compiled through `CONFIG_QED_FCOE` with stubs in `qed_fcoe.h`.

## Risks And Edge Cases
The stop path refuses to stop while hash entries remain, so leaked upper-layer connection handles block clean shutdown. Connection objects are recycled on a free list and retain coherent DMA allocations; every acquire/release path must pair CID ownership and hash membership correctly. Some connection allocations are done outside the lock after CID acquisition, with explicit CID release on allocation failure. `qed_fcoe_release_connection()` always caches the connection rather than freeing it immediately, so `qed_fcoe_free()` must run to release DMA memory.

FCoE start allocates `tid_info` with `GFP_ATOMIC` and rolls back by calling stop on failure. Ramrod posting is synchronous blocking mode for the public operations, so firmware timeout/error behavior propagates directly to callers. BDQ producer address helpers return `NULL` and log when `QED_BDQ` was not allocated. Stats acquisition respects atomic context through `qed_ptt_acquire_context()`, but failure only logs and leaves the caller with zeroed or partial stats depending on the wrapper.

## Test Signals
FCoE coverage should include builds with `CONFIG_QED_FCOE=y/m` and disabled builds using stubs. Runtime tests should start/stop FCoE, request TID memory, acquire/release multiple connections, offload and destroy connections with representative queue DMA addresses, verify stop fails with active connections, verify free-list reuse, inject CID and DMA allocation failures, and validate stats reads. Hardware/firmware signals include FCoE init/offload/terminate/destroy ramrod completions, BDQ producer addresses, TSTORM/PSTORM counters, `QED_FLAG_STORAGE_STARTED`, and hash-table emptiness on stop.

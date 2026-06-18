
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_nic_io.h

## Purpose
`hinic3_nic_io.h` defines the public queue and doorbell contract used by the hinic3 NIC data path. It exposes `struct hinic3_io_queue`, `struct hinic3_nic_io`, queue-pair parameter structures, inline SQ index helpers, the doorbell write helper, and lifecycle prototypes implemented by `hinic3_nic_io.c`.

## Important APIs, Types, And Functions
- `HINIC3_SQ_WQEBB_SHIFT`, `HINIC3_RQ_WQEBB_SHIFT`, and `HINIC3_SQ_WQEBB_SIZE` define queue element sizes used by WQ allocation and descriptor programming.
- `enum hinic3_rq_wqe_type` currently exposes `HINIC3_NORMAL_RQ_WQE`.
- `struct hinic3_io_queue` holds a `struct hinic3_wq`, owner bit, queue id, MSI-X entry, doorbell address, and SQ hardware CI pointer.
- `hinic3_get_sq_local_ci()`, `hinic3_get_sq_local_pi()`, and `hinic3_get_sq_hw_ci()` provide masked software/hardware index access.
- `struct hinic3_nic_db` and `hinic3_write_db()` encode and write the 64-bit doorbell.
- `struct hinic3_dyna_qp_params` carries requested queue count/depths and returned SQ/RQ arrays.
- `struct hinic3_nic_io` stores live SQ/RQ arrays, queue counts, coherent CI table, doorbell bases, RX buffer length, and feature capability.

## Control Flow
TX and RX paths obtain a `struct hinic3_io_queue` from `nic_dev->nic_io`. Producers advance the WQ producer index via `hinic3_wq` helpers, then call `hinic3_write_db()` with the queue, COS, SQ/RQ data-path flag, and producer index. TX completion reads `hinic3_get_sq_hw_ci()` from the coherent CI slot and returns WQEBBs using the local CI.

## State And Persistence Behavior
All structures are per-driver runtime state. `cons_idx_addr` points into coherent DMA memory that survives while NIC I/O resources are active. Doorbell MMIO addresses are stored once per SQ/RQ class and shared by queues. `struct hinic3_nic_io` does not persist across device removal or driver unload.

## Dependencies And Integration Points
The header depends on `linux/bitfield.h` and `hinic3_wq.h`. It is consumed by `hinic3_nic_io.c`, `hinic3_tx.c`, `hinic3_rx.c`, and any higher-level NIC device code that allocates/configures queue pairs.

## Risks And Edge Cases
- `hinic3_write_db()` type-puns a local `struct hinic3_nic_db` into a 64-bit write; layout and endianness must remain exactly two 32-bit little-endian words.
- `DB_ADDR()` uses low PI bits to select the doorbell offset, so queue producer indices and MMIO mapping size must match hardware expectations.
- `hinic3_get_sq_hw_ci()` assumes `cons_idx_addr` is initialized and points to coherent memory before TX polling begins.

## Test Signals
Doorbell validation should show packets transmitted and RX buffers replenished after `hinic3_write_db()`. TX completion tests should observe hardware CI movement in the CI table and no false queue-full conditions under wraparound.

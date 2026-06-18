# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/rx.c

## Purpose
`libeth/rx.c` provides common receive buffer queue allocation/destruction and packet-type hash metadata helpers for Intel Ethernet drivers.

## Important APIs, Types, and Functions
- Exported queue helpers: `libeth_rx_fq_create()`, `libeth_rx_fq_destroy()`, and `libeth_rx_recycle_slow()`.
- Buffer sizing internals: MTU-based, truesize-based, and zero-copy/header-split page-pool parameter calculations.
- Packet-type helper: `libeth_rx_pt_gen_hash_type()` fills XDP RSS hash type bits from a parsed packet-type structure.

## Control Flow
`libeth_rx_fq_create()` builds `page_pool_params` from queue metadata, chooses normal or zero-copy/header-split sizing, creates a page pool, allocates FQEs, registers the pool with XDP, and publishes the pool/array. Error paths unwind in reverse. Destroy unregisters the XDP page pool, frees FQEs, and destroys the page pool.

## State and Persistence Behavior
The caller-owned `struct libeth_fq` receives `buf_len`, `truesize`, FQE array pointer, and page-pool pointer. Page-pool memory and XDP registration persist until destroy. Packet-type LUT entries can have `hash_type` generated at runtime.

## Dependencies and Integration Points
The file depends on Linux page_pool, XDP page-pool registration, netmem, NAPI, netdevice MTU, and public `net/libeth/rx.h`. Consumer drivers use it to standardize Rx queue memory sizing.

## Risks and Edge Cases
- Invalid FQE type or header-split combination returns `-EINVAL`.
- `roundup_pow_of_two()` and clamp behavior are sensitive to tiny or huge MTU/truesize values.
- Zero-copy path assumes separate header buffers account for stack overhead.
- Missing destroy would leak registered page pools and FQE arrays.

## Test Signals
Create/destroy for MTU, short, header, XDP and non-XDP queues; invalid queue types; low-memory allocation failures; MTU boundary values; XDP page-pool registration failure; hash type generation for representative packet types.

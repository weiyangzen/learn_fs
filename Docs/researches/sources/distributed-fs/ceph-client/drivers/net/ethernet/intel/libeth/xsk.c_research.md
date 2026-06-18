# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/xsk.c

## Purpose
`libeth/xsk.c` implements common AF_XDP/XSk support for libeth XDP users: XSk buffer free/fragment helpers, XSk program slowpath verdict handling, fill queue setup, NAPI wakeup via call-single-data, and XSk pool DMA mapping.

## Important APIs, Types, and Functions
Exports include `libeth_xsk_buff_free_slow()`, `libeth_xsk_buff_add_frag()`, `libeth_xsk_buff_stats_frags()`, `__libeth_xsk_run_prog_slow()`, `libeth_xskfq_create()`, `libeth_xskfq_destroy()`, `libeth_xsk_init_wakeup()`, `libeth_xsk_wakeup()`, and `libeth_xsk_setup_pool()`. It also defines `libeth_xsktmo_slow` for checksum metadata requests.

## Control Flow
XSk program slowpath handles DROP by freeing, TX/PASS by returning corresponding libeth verdicts, and all other cases by delegating to `libeth_xdp_prog_exception()`. Fill queue creation allocates FQEs, initializes pending count, threshold, frame length, and truesize from the XSk pool. Wakeup first marks scheduled NAPI as missed, then schedules on queue-selected CPU via IPI or local NAPI scheduling. Pool setup maps or unmaps DMA for the queue's XSk pool.

## State and Persistence Behavior
`struct libeth_xskfq` stores FQE array, pending count, threshold, buffer length, truesize, pool, NUMA node, and descriptor count. Wakeup state is stored in caller-owned `call_single_data_t`. DMA mapping persists until pool disable.

## Dependencies and Integration Points
Depends on `net/libeth/xsk.h`, AF_XDP core APIs, NAPI scheduling, SMP call-single-data, and XDP helpers from `xdp.c`. Consumer drivers call this from `ndo_xsk_wakeup`, queue setup, and XSk Rx processing.

## Risks and Edge Cases
- `libeth_xsk_wakeup()` maps queue IDs modulo CPU count when out of range; this is robust but may not match queue affinity.
- Pool setup returns `-EINVAL` if no pool exists for a queue.
- Fragment attach frees both head and frag on failure, so callers must treat null as full ownership loss.
- DMA map/unmap must pair exactly with XSk pool enable/disable.

## Test Signals
XSk pool enable/disable, missing pool path, wakeup from same and remote CPU, queue ID beyond CPU count, fill queue allocation failure, fragmented XSk packets, XDP_DROP/TX/PASS/REDIRECT-failure verdicts, and metadata checksum request behavior.

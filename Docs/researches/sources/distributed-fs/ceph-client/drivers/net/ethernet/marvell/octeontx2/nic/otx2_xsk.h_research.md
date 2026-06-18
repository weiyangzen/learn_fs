# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_xsk.h

## Purpose
`otx2_xsk.h` declares the AF_XDP zero-copy interface used by RVU NIC setup and data-path code.

## Important APIs, Types, and Functions
The header forward-declares `struct otx2_nic` and `struct xsk_buff_pool`, then declares pool setup/enable/disable, zero-copy buffer allocation, netdev wakeup, zero-copy NAPI TX handling, and SQ pool attachment functions.

## Control Flow
There is no executable logic here. The declarations define the call graph: netdev/XSK setup calls `otx2_xsk_pool_setup()`, queue setup calls `otx2_attach_xsk_buff()`, RX refill calls `otx2_xsk_pool_alloc_buf()`, and TX completion/idle paths call `otx2_zc_napi_handler()`.

## State and Persistence
The header exposes no state directly; state resides in `otx2_nic`, queue pools, send queues, and XSK pool objects managed by `otx2_xsk.c` and `otx2_txrx.c`.

## Dependencies and Integration Points
It is included by `otx2_txrx.c` and the XSK implementation. It relies on netdev, DMA, and queue structures already visible to include sites through common driver headers.

## Risks and Edge Cases
Prototype changes require synchronized updates in TX/RX and netdev XSK call sites. Because `otx2_xsk_pool_alloc_buf()` references `struct otx2_pool` without a local forward declaration, include ordering must continue to provide that type.

## Test Signals
Compile tests with AF_XDP enabled and disabled configurations, plus runtime XSK bind/wakeup/TX/RX coverage, are sufficient signals for this header contract.

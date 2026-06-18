# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-rx.h

## Purpose
RX declarations and inline FPA packet-pool refill helper for Octeon Ethernet.

## Important APIs, Types, And Functions
Declares `cvm_oct_poll_controller()`, `cvm_oct_rx_initialize()`, and `cvm_oct_rx_shutdown()`. Defines inline `cvm_oct_rx_refill_pool(int fill_threshold)`.

## Control Flow
The refill helper reads the FAU count of packet buffers to replace, and if the count exceeds the threshold, decrements the debt, fills the FPA packet pool, and restores any unfilled remainder to the counter.

## State And Persistence
Manipulates the hardware FAU packet-buffer debt counter. No header-local state.

## Dependencies And Integration Points
Depends on `FAU_NUM_PACKET_BUFFERS_TO_FREE`, `CVMX_FPA_PACKET_POOL`, `CVMX_FPA_PACKET_POOL_SIZE`, and `cvm_oct_mem_fill_fpa()`.

## Risks
Incorrect thresholding can starve the packet pool or over-refill. Partial fill errors must restore debt accurately.

## Test Signals
RX refill worker and NAPI refill paths, partial FPA allocation failure, threshold behavior, and packet-pool starvation recovery.

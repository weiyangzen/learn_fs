# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/alx.h

## Purpose
Defines the ALX driver's private software data structures for descriptor buffers, RX/TX queues, NAPI vector binding, per-device state, quirks, and the ethtool ops export.

## Important APIs, Types, and Functions
`struct alx_buffer` stores SKB and DMA unmap metadata. `struct alx_rx_queue` owns RRD/RFD rings, DMA addresses, software buffers, and read/write indexes. `struct alx_tx_queue` owns TPD ring state and producer/consumer register offsets. `struct alx_napi` binds a NAPI instance to optional RX/TX queues and an interrupt vector. `struct alx_priv` contains the `net_device`, `struct alx_hw`, descriptor memory block, queue/NAPI counts, IRQ mask lock, ring sizes, work items, message level, stats lock, and lifecycle mutex.

## Control Flow and State
The header has no executable control flow, but it defines state that persists across PCI probe, netdev open/close, suspend/resume, and error recovery. Queue indexes and DMA metadata are the authoritative software view of hardware descriptor rings.

## Dependencies and Integration Points
Includes `hw.h`, DMA mapping, spinlocks, and Ethernet helpers. `main.c` allocates and mutates these structures; `ethtool.c` reads `alx_priv` and `alx_hw`; `hw.c` operates below `alx_hw`.

## Risks and Test Signals
Correct locking around `int_mask`, `stats`, and `mtx` is essential. Tests should stress queue allocation/free, MSI-X fallback, suspend/resume, and reset while traffic is active. Structure changes require matching updates in allocation, cleanup, and ethtool stats paths.

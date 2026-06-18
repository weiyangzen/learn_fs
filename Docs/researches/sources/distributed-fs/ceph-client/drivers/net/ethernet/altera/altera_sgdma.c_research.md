# sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_sgdma.c

## Purpose
`altera_sgdma.c` implements the legacy SGDMA backend for the Altera Triple-Speed Ethernet driver. It maps descriptor memory for DMA, manages simple software TX/RX buffer lists, starts SGDMA read/write transactions, reports completions/status, and exposes the same DMAops contract as the MSGDMA backend.

## Important APIs and functions
- `sgdma_initialize()` sets SGDMA control defaults, initializes TX/RX pending lists, maps RX/TX descriptor memory, clears it with `memset_io()`, and syncs it for hardware.
- `sgdma_uninitialize()` unmaps descriptor memory.
- `sgdma_reset()` clears descriptor memory and toggles RX/TX SGDMA reset controls.
- IRQ hooks are mostly no-ops for enable/disable because SGDMA interrupts stay enabled after initial setup; `sgdma_clear_rxirq()` and `sgdma_clear_txirq()` set the clear-interrupt bit.
- `sgdma_tx_buffer()` waits for TX idle, builds a current/next descriptor pair, starts async write, and queues the buffer for completion.
- `sgdma_tx_completions()` returns one completion when TX is idle, the descriptor is no longer hardware-owned, and a queued TX buffer can be dequeued.
- `sgdma_add_rx_desc()` queues RX buffers; `sgdma_start_rxdma()` starts the first read; `sgdma_rx_status()` reads descriptor status/bytes on EOP, dequeues the RX buffer, clears CSR state, and restarts RX DMA.
- Private helpers handle descriptor setup, physical address calculation, async read/write, queue push/pop/peek, and busy polling.

## Control flow
The main TSE driver allocates descriptor regions, calls `sgdma_initialize()`, refills RX by calling `add_rx_desc()`, then calls `start_rxdma()`. `sgdma_async_read()` peeks the queued RX buffer, programs descriptor 0 with write address and descriptor 1 as terminator, syncs descriptor memory, writes `next_descrip`, and starts the RX controller. On RX EOP, `sgdma_rx_status()` syncs descriptor memory for CPU, extracts status/length, removes the buffer from the pending list, clears controller state, and kicks the next read. TX is single-buffer-at-a-time: `sgdma_tx_buffer()` programs descriptor 0 for the SKB DMA address and starts TX; completion is seen when hardware clears ownership and TX busy is false.

## State and persistence behavior
State is volatile and stored in `struct altera_tse_private`: descriptor virtual/MMIO pointers, descriptor bus addresses, mapped DMA addresses, control words, and `txlisthd`/`rxlisthd`. Hardware descriptor ownership bits and CSR busy/status bits drive progress. No persistent storage is used.

## Dependencies and integration points
It depends on the main TSE private state from `altera_tse.h`, list handling, DMA mapping/sync APIs, register access helpers from `altera_utils.h`, and SGDMA layout constants from `altera_sgdmahw.h`. It is selected by the SGDMA `struct altera_dmaops` in `altera_tse_main.c`.

## Risks and edge cases
This backend supports only one active TX and one active RX descriptor chain at a time despite the main driver ring abstraction. List operations assume the caller holds the appropriate main-driver lock. `sgdma_txbusy()` waits only about 100 microseconds before logging a timeout. Descriptor memory is mapped from an IO memory pointer, so DMA mapping/sync assumptions are sensitive to platform memory attributes. RX status zero after EOP is treated as a serious error and no packet is returned.

## Test signals
Test initialization/uninitialization with DMA API debug, TX busy timeout handling, single-packet TX completion, RX queue empty handling, RX EOP status/length/error propagation, interrupt clear behavior, reset clearing descriptors, and lockdep coverage around list operations in the main driver.

# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-dma.c

Purpose: DMA engine support for Intel THC. It allocates PRD tables and scatterlists, programs DMA base/control registers, starts/stops RXDMA/TXDMA/SWDMA channels, copies data between scatterlists and caller buffers, and waits for interrupt-driven completion.

Important APIs: `thc_dma_init()`, `thc_dma_set_max_packet_sizes()`, `thc_dma_allocate()`, `thc_dma_configure()`, `thc_dma_unconfigure()`, `thc_dma_release()`, `thc_rxdma_read()`, `thc_swdma_read()`, and `thc_dma_write()` are exported in the Intel THC namespace.

Control flow: initialization seeds per-channel register offsets and directions. Allocation creates coherent PRD memory and SG lists for enabled channels, then mirrors SG DMA addresses into PRD entries. Configure resets engines, writes PRD base/control values, and starts RXDMA2. Reads derive pending PRD index from hardware read/write pointers, copy a single frame, refresh PRD descriptors, and advance the write pointer. SWDMA quiesces interrupts and pauses normal RXDMAs, performs a write/read sequence, then restores RXDMA2 and I2C feature state. TXDMA fills a one-table PRD, optionally quiesces interrupts for performance-delay constraints, starts hardware, and waits for `write_done`.

State and persistence: `struct thc_dma_context` persists channel configuration and temporary SWDMA feature-state flags. DMA buffers are held until release. Waitqueue flags are in `struct thc_device` and are set by the common interrupt handler.

Dependencies and integration: relies on DMA mapping, scatterlist helpers, `intel-thc-dev.h` waitqueues/feature toggles, and `intel-thc-hw.h` register bits. Protocol drivers call DMA helpers after controller setup.

Risks: partial allocation failures in `setup_dma_buffers()` return without freeing allocations already made inside the same channel until higher-level unwinding reaches previous channels only. Pointer wrap rules are hardware-specific and easy to regress. SWDMA temporarily disables I2C Rx max-size and interrupt-delay features, so restore paths must run on failures. TXDMA currently always waits for interrupt completion despite `use_write_interrupts` handling in start-bit setup.

Test signals: DMA allocation/unwind tests, RX pointer wrap tests, SWDMA timeout paths, TXDMA completion wakeups, and hardware input/output report transfer validation.

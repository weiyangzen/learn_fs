# sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_dma.h

Purpose: declares the SXGBE DMA operation table and DMA configuration constants used by the main driver and implemented by `sxgbe_dma.c`.

Important APIs: constants include burst-map/PBL shifts and `DEFAULT_DMA_PBL`. `struct sxgbe_dma_ops` contains callbacks for DMA init, channel init, TX/RX start/stop, queue start/stop, IRQ enable/disable, TX/RX interrupt status, RX watchdog programming, and TSO enable. `sxgbe_get_dma_ops()` returns the implementation.

Control flow: probe/open code gets this ops table and calls it to configure DMA hardware, service interrupts, and apply ethtool coalescing or TSO changes.

State and persistence: no state in the header; it defines function-pointer contracts operating on MMIO registers and stats passed by callers.

Dependencies and integration: forward-declares `sxgbe_extra_stats` and uses `dma_addr_t`, `u32`, and `u8` kernel types. It is included by DMA implementation, descriptor implementation, ethtool, and main paths that need DMA ops.

Risks: the `cha_init` parameter name has a typo (`t_rzie`) that does not affect ABI but can confuse users. The closing include guard comment says `__SXGBE_CORE_H__`, inconsistent with the actual guard. Contract changes must stay synchronized with `sxgbe_dma.c` and `struct sxgbe_ops`.

Test signals: compile-time function pointer type matching, probe calling every required op, and warnings from header guard or prototype drift.

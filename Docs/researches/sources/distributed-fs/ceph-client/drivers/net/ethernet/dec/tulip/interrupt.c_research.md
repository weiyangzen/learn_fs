# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/interrupt.c

## Purpose
Implements RX buffer refill, optional NAPI polling, non-NAPI RX processing, PHY interrupt acknowledgement for HPPA, and the main interrupt handler for the shared Tulip driver.

## Important APIs, Types, and Functions
Exports `tulip_rx_copybreak`, `tulip_max_interrupt_work`, `tulip_refill_rx`, optional `oom_timer` and `tulip_poll`, and `tulip_interrupt`. Internal helpers include non-NAPI `tulip_rx`, `phy_interrupt`, and the optional interrupt mitigation table. The code operates on `struct tulip_private` descriptor rings, `rx_buffers`, `tx_buffers`, CSR registers, NAPI state, timers, interrupt masks, and netdev stats.

## Control Flow and State
`tulip_refill_rx` allocates SKBs, maps them for DMA, writes RX descriptor buffer addresses, and returns ownership to hardware; LC82C168 RX-stopped state is explicitly restarted. NAPI mode masks RX interrupts in `tulip_interrupt`, schedules `tulip_poll`, drains descriptors up to budget, acks RX events, copies small packets or passes up ring SKBs, refills, toggles hardware interrupt mitigation, and handles out-of-memory by arming `oom_timer` without re-enabling RX interrupts. Non-NAPI mode performs similar descriptor processing directly in interrupt context. The main interrupt handler acks status, handles RX/NAPI scheduling, cleans completed TX descriptors, frees SKBs and DMA mappings, wakes the queue, restarts TX/RX on selected errors, calls link-change callbacks, handles system errors, masks excessive work, and accounts missed RX frames from CSR8.

## State and Persistence Behavior
Persistent hardware state includes Tulip CSR5 interrupt status, CSR7 mask, CSR8 missed counter, CSR11 timer/mitigation control, descriptor ownership bits, and chip-specific CSR12 PHY status. Software state includes ring cursors (`cur_rx`, `dirty_rx`, `cur_tx`, `dirty_tx`), DMA mappings, NAPI poll state, `mit_on`, out-of-memory timer, interrupt count, timeout timer state, and carrier/link-change callbacks. Descriptor ownership and DMA sync/unmap calls are the central persistence boundary between CPU and device.

## Dependencies and Integration Points
Depends on `tulip.h`, PCI DMA mapping, netdevice/SKB APIs, optional `CONFIG_TULIP_NAPI`, optional `CONFIG_TULIP_NAPI_HW_MITIGATION`, optional HPPA PHY IRQ handling, timer APIs, and the chip table `tulip_tbl`. It is linked into `tulip.o` and is invoked by the main Tulip open path as the IRQ and NAPI handler.

## Risks and Test Signals
Risks include descriptor ownership races, lost RX events around NAPI ack/mask sequencing, DMA sync/unmap mistakes between copy and pass-up paths, out-of-memory polling deadlocks, interrupt mitigation latency tradeoffs, too-much-work masking that hides events, link-change callbacks that delete timers, and recovery from `0xffffffff` hardware disappearance. Test signals include NAPI and non-NAPI builds, high-rate RX, RX allocation failure, TX completion/error counters, queue wake on TX cleanup, LC82C168 RX no-buffer restart, link pass/fail interrupts, system-error logging, netpoll/IRQ sharing behavior, and missed-frame counter accounting.

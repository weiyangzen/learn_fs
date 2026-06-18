# sources/distributed-fs/ceph-client/drivers/mailbox/sun6i-msgbox.c

Purpose: implements the Allwinner sun6i/sun8i/sun9i/sun50i message box, exposing eight channels whose directions are preconfigured by firmware and whose messages are 32-bit FIFO entries.

Important APIs/types/functions: `struct sun6i_msgbox` owns controller, clock, spinlock, and register base. Ops are send, startup, shutdown, `last_tx_done`, and `peek_data`; `sun6i_msgbox_irq` drains RX FIFOs.

Control flow: probe allocates eight channels, enables the clock, deasserts reset without ever reasserting it, maps MMIO, disables local IRQs, requests the IRQ, and registers a poll-txdone controller. Startup checks if the channel is configured as RX, flushes stale FIFO data, clears IRQ status, and enables the RX IRQ bit under lock. TX validates that hardware marks the channel as TX, writes the 32-bit message to the data register, and relies on remote IRQ status for completion. IRQ intersects enabled and pending local IRQ bits, drains each RX FIFO while `peek_data` reports data, passes each word to the client, and clears the IRQ once the FIFO is empty. Shutdown disables RX IRQ and repeatedly drains/clears until pending status is gone.

State and persistence: channel direction is firmware-owned hardware state. Local IRQ enable is protected by a spinlock. The reset line remains deasserted after probe because firmware may share the block.

Dependencies and integration: depends on DT compatible `allwinner,sun6i-a31-msgbox`, clock, reset, one IRQ, mailbox clients, and firmware channel-direction setup.

Risks: using a channel backwards can put hardware into a bad state; the driver warns and drops TX. Probe uses `irq_of_parse_and_map` directly. Shared firmware ownership makes reset/error recovery intentionally conservative.

Test signals: firmware direction matrix, RX FIFO flush and IRQ clear loops, txdone polling via remote IRQ status, reset failure handling, and concurrent RX IRQ enable/disable.

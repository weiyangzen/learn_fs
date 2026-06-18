# sources/distributed-fs/ceph-client/drivers/gpib/eastwood/fluke_gpib.h

Purpose: defines Fluke CB7210 board-private state, register layout, bit fields, and inline MMIO helpers used by `fluke_gpib.c`.

Important types and APIs: `struct fluke_priv` embeds `struct nec7210_priv` and stores MMIO resources for GPIB registers, DMA port, write-transfer counter, IRQ, DMA channel, bounce buffer, buffer size, and transfer-counter mapping. Inline helpers include `cb7210_page_in_bits`, `fluke_read_byte_nolock`, `fluke_write_byte_nolock`, `fluke_paged_read_byte`, and `fluke_paged_write_byte`. Enums define CB7210 paged registers, ISR/IMR bits, source-handshake states, bus-status bits, and Fluke auxiliary commands.

Control flow and state: paged register access writes a page-select auxiliary command, delays, then reads or writes the selected register while holding `nec_priv->register_page_lock`. Bus status bits are active-low and translated by the C file into `BUS_*` line-status flags. `write_transfer_counter_mask` limits accelerated write chunks to 0x7ff bytes.

Dependencies and integration: includes `nec7210.h`, DMAengine, I/O, delay, and interrupt headers. The C file installs these helpers as NEC7210 `read_byte`/`write_byte` callbacks and uses the register constants in interrupt, DMA, line-status, and T1-delay paths.

Risks: the nolock helpers require callers to hold the page lock; misuse can corrupt paged register selection. `readl`/`writel` are used for byte-wide values, which assumes the hardware tolerates 32-bit accesses. The custom `DATA_IN_STATUS` bit and undocumented `AUX_RTL2` behavior are hardware-specific and need matching HDL/firmware.

Test signals: static build coverage, lockdep review around paged access, hardware tests for paged ISR/BUS_STATUS/STATE1 reads, line-status polarity, high-speed/low-speed AUX commands, transfer-counter masking, and RTL behavior.

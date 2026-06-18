# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-ring.c

Purpose: Allocates and initializes software rings and prebuilt SPI messages backing MCP251xFD TEF, RX FIFO, and TX FIFO operation.

Important APIs, types, and functions: `mcp251xfd_ring_alloc()`, `mcp251xfd_ring_init()`, and `mcp251xfd_ring_free()` are exported to core lifecycle code. Helpers prepare register write commands, initialize TEF/TX/RX descriptors, initialize TX object SPI messages, and implement RX/TX coalescing hrtimer callbacks. Defines `mcp251xfd_ram_config`.

Control flow: Allocation recomputes layout when CAN/CAN-FD mode changes, selects object sizes, allocates RX rings, and sets hrtimers. Initialization resets queue state, lays out TEF, RX, then TX RAM, prebuilds IRQ enable/UINC/RTS SPI transfers, logs layout, and validates RAM/coalescing constraints.

State and persistence behavior: Ring counters, object sizes/counts, FIFO numbers, base addresses, prebuilt SPI buffers/transfers, and timers live in `mcp251xfd_priv`. They are allocated on open and freed on stop.

Dependencies and integration points: Uses RAM layout helper, SPI APIs, CRC helper, register constants, ethtool-derived coalescing settings, and netdev queue helpers. RX/TEF/TX paths consume its descriptors.

Risks: Counts are used as power-of-two masks. Final `cs_change` handling is critical to deassert chip select. Coalescing relies on first RX FIFO and half-TEF assumptions.

Test signals: CAN/CAN-FD layout logs, open/stop leaks, ethtool min/max rings, coalescing frame/time modes, SPI transfer lengths in CRC/nocrc modes, and TX/RX wraparound stress.

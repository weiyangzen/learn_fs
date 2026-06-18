# sources/distributed-fs/ceph-client/drivers/net/can/spi/mcp251xfd/mcp251xfd-chip-fifo.c

Purpose: FIFO and acceptance-filter initialization for the MCP251xFD CAN FD controller.

Important APIs/types/functions: `mcp251xfd_chip_rx_fifo_init_one()` builds RX FIFO configuration for one RX ring, enabling timestamps, RX overflow interrupt, and not-empty interrupt. `mcp251xfd_chip_rx_filter_init_one()` enables a filter and points it to the ring FIFO. `mcp251xfd_chip_fifo_init()` initializes TEF, TX FIFO, and all RX FIFOs/filters through regmap writes.

Control flow: full init writes TEFCON based on TX ring object count and enables TEF timestamp/overflow/not-empty interrupts. It writes TX FIFOCON with object count, TX enable, transmit-attempt interrupt, payload size 64 for FD mode or 8 for classic mode, and one-shot or unlimited retry policy from CAN ctrlmode. It then iterates RX rings with `mcp251xfd_for_each_rx_ring()`, programming each RX FIFO and filter.

State and persistence: persistent runtime state is in chip registers programmed through `priv->map_reg`. Ring object counts, FIFO numbers, filter numbers, CAN FD mode, and ctrlmode are read from `mcp251xfd_priv` ring structures. No disk persistence.

Dependencies/integration: depends on `mcp251xfd.h`, regmap, bitfield helpers, ring allocation done elsewhere, and CAN ctrlmode. Integrates with RX, TX, TEF, and timestamp submodules through shared FIFO/register layout.

Risks: FIFO object count is programmed as `obj_num - 1`, so zero-sized rings would underflow if ever allowed. RX overflow interrupt is intentionally enabled on all RX FIFOs to detect RX MAB overflow. Filter index/register math must match hardware grouping of four filters per FLTCON register. Payload size must match CAN FD mode or RX/TX layout breaks.

Test signals: initialize in classic and FD modes; verify TEF/TX/RX FIFOCON register values; test one-shot ctrlmode; receive overflow should raise RXOVIF on affected FIFO; filters should route frames to expected RX FIFO.

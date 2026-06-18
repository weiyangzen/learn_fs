<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_spi.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_spi.h

## Purpose
`qca_spi.h` defines private constants, TX ring layout, statistics, and per-device state for the QCA7000 SPI Ethernet driver.

## Important APIs, Types, and Data
- Driver identity/version constants and protocol limits such as good signature, TX ring min/max, RX frame batch max, sync states, reset timeout, and sync event IDs.
- `struct tx_ring` stores a fixed skb pointer array plus head/tail/size/count.
- `struct qcaspi_stats` stores reset, error, memory, ring, SPI, verify, buffer, and signature counters.
- `struct qcaspi` is netdev private state for the SPI device, thread, ring, stats, RX buffers, sync state, framing handle, flags, reset count, optional debugfs root, legacy mode, and burst length.

## Control Flow
The header has no executable flow. Its constants drive sync state machines, ring management, and runtime validation in `qca_spi.c`.

## State and Persistence
All fields in `struct qcaspi` persist for the netdev lifetime. TX ring entries own queued skbs until transmitted or flushed. Stats persist until the netdev is freed.

## Dependencies and Integration Points
Includes netdev, scheduler, skb, SPI, and common framing headers. It is included by low-level register helpers, SPI driver code, and QCA debug/ethtool code.

## Risks and Edge Cases
- `tx_ring::size` tracks bytes including hardware packet overhead, not just skb payload.
- `sync` is a small integer state shared by thread and error helpers.
- The fixed `QCASPI_TX_RING_MAX_LEN` array constrains ethtool ringparam changes.
- Debugfs field is conditional on `CONFIG_DEBUG_FS`, while helper declarations remain unconditional through stubs.

## Test Signals
TX ring enqueue/drain/flush, stats string count matching struct field count, reset state transitions, and burst/legacy mode operation validate the structure contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_spi.h -->

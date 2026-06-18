# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/fun_port.h

## Purpose
Defines numeric indexes for Fungible port MAC and FEC statistics as exposed by firmware and consumed by funeth stats/ethtool code.

## Important APIs, Types, And Functions
Enums are `port_mac_rx_stats`, `port_mac_tx_stats`, and `port_mac_fec_stats`. Each enum maps stable statistic names such as octets, frames, pause frames, error classes, packet-size buckets, per-priority PFC counters, and FEC correctable/uncorrectable counters to array indexes ending in `*_STATS_MAX`.

## Control Flow
The header has no runtime flow. Consumers use these indexes into `funeth_priv->stats` DMA memory and ethtool stat-name arrays to report counters.

## State And Persistence
No owned state. It defines the schema for firmware-populated port statistic arrays.

## Dependencies And Integration Points
Used by `funeth_ethtool.c` and likely `funeth_main.c` stats paths. It must stay in sync with firmware/port command definitions from `fun_hci.h`.

## Risks
Changing enum values or order breaks stats interpretation. Counters are sparse protocol contract indexes rather than arbitrary local ordering, so adding stats should preserve existing numeric assignments.

## Test Signals
Verify ethtool stats read expected indexes, `*_STATS_MAX` matches allocated stats DMA area, and known traffic increments the corresponding RX/TX/FEC counters.

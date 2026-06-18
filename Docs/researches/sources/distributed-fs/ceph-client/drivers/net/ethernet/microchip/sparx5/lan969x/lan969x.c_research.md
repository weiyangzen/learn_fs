# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x.c

## Purpose
This file defines LAN969x family match data for the common Sparx5 driver. It provides IO target mapping, register table binding, hardware constants, port-speed classification and device-index mapping, scheduler/leak group data, QSGMII mux programming, a LAN969x-specific PTP two-step IRQ handler, and operation hooks used by common Sparx5 code.

## Important APIs, Types, And Functions
The exported object is `lan969x_desc`. Internals include `lan969x_main_iomap[]`, `lan969x_consts`, `lan969x_regs`, `lan969x_ops`, `lan969x_get_dev_mode_bit()`, `lan969x_port_dev_mapping()`, `lan969x_port_mux_set()`, `lan969x_ptp_irq_handler()`, `lan969x_get_sdlb_group()`, and `lan969x_get_hsch_max_group_rate()`.

## Control Flow
Platform matching selects `lan969x_desc`; common Sparx5 probe then uses its target map to bind MMIO ranges, its constants to size driver structures, its register arrays for offset calculation, and its ops for runtime family differences. Port helpers classify fixed LAN969x port numbers into 2.5G, 5G, 10G, or RGMII groups. QSGMII mode sets a per-quad mux bit. The PTP handler drains timestamp FIFO entries, pairs a TX timestamp and ID timestamp, finds the matching queued skb by `ts_id`, computes the hardware timestamp, completes `skb_tstamp_tx()`, and frees the skb.

## State And Persistence
Static descriptor data is read-only. Runtime state touched by this file includes `sparx5->ports[]`, per-port `tx_skbs`, `sparx5->ptp_skbs`, and hardware PTP FIFO/control registers. No persistent storage is modified.

## Dependencies And Integration Points
It depends on generated LAN969x register arrays, generated VCAP metadata, LAN969x calendar/RGMII/FDMA helpers, common Sparx5 PTP helpers, and common `sparx5_match_data` probing. The target IO map must align with the SoC memory map used by device tree resources.

## Risks And Edge Cases
Port-number maps are hard-coded and must match silicon. The PTP handler assumes a valid `sparx5->ports[txport]`; bad FIFO data could dereference a missing port. Timestamp queue matching is O(queue length) and protected by the per-port skb queue lock. `WARN_ON(!skb_match)` indicates lost timestamp correlation. QSGMII mux changes are skipped when the requested port mode already equals the current mode.

## Test Signals
Probe a LAN969x device tree, verify all targets map, bring up ports from each speed class, exercise QSGMII and RGMII modes, run PTP two-step transmit timestamping under load, check scheduler group rates, and confirm common Sparx5 paths call LAN969x FDMA/calendar/RGMII hooks.

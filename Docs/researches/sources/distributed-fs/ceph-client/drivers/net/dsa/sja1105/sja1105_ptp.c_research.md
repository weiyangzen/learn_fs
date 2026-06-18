# sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_ptp.c

## Purpose

This file implements Precision Time Protocol hardware clock support and packet timestamping for SJA1105/SJA1110 switches. It registers a PHC, supports get/set/adjust time and frequency, exposes one configurable PTP_CLK pin for periodic output or external timestamp polling, manages hardware timestamp configuration per port, reconstructs partial timestamps on older chips, and handles SJA1110 meta-frame timestamp completion.

## Important APIs, Types, and Data

- `sja1105_hwtstamp_set()` and `sja1105_hwtstamp_get()` manage per-port TX/RX hardware timestamp enable bitmaps.
- `sja1105_get_ts_info()` reports ethtool timestamping capabilities and PHC index.
- `sja1105et_ptp_cmd_packing()` and `sja1105pqrs_ptp_cmd_packing()` pack generation-specific PTP command register layouts.
- `sja1105_ptp_commit()` reads/writes the PTP control register through chip-specific packing callbacks.
- `__sja1105_ptp_gettimex()`, `__sja1105_ptp_settime()`, and `__sja1105_ptp_adjtime()` are lock-expecting internal helpers used by PHC callbacks and static reload.
- `sja1105_ptp_clock_register()` initializes queues, PHC caps, timer, command defaults, registers the PHC, and resets the PTP clock.
- `sja1105_ptp_txtstamp_skb()`, `sja1105_rxtstamp()`, `sja1110_rxtstamp()`, `sja1110_txtstamp()`, and `sja1110_process_meta_tstamp()` implement TX/RX timestamp delivery.

## Control Flow

PHC operations all serialize on `ptp_data->lock`. `gettimex` reads `PTPCLKVAL` with optional system timestamping. `settime` switches the hardware to set mode, writes ticks converted from nanoseconds, and notifies TAS of a clock step. `adjtime` switches to add mode and writes a signed tick delta. `adjfine` converts scaled ppm into the hardware centered `PTPCLKRATE` representation and notifies TAS of frequency adjustment.

TX timestamping on SJA1105 clones the skb in `sja1105_port_txtstamp()`. Deferred management-route TX later calls `sja1105_ptp_txtstamp_skb()`, which polls the per-port egress timestamp register for the update bit, reads the current PHC, reconstructs a full timestamp from the partial hardware timestamp, and completes the skb timestamp. On SJA1110, `sja1110_txtstamp()` assigns an 8-bit timestamp ID and queues the clone; `sja1110_process_meta_tstamp()` matches a later TX meta timestamp by ID and completes it.

RX timestamping on SJA1105 queues skbs because reconstructing partial timestamps requires a sleepable PHC read. The PTP worker drains the queue, reconstructs timestamps, and reinjects packets via `netif_rx()`. SJA1110 receives full enough timestamps from tag/meta handling and stamps synchronously without deferral.

The PTP_CLK pin can be set to periodic output by programming start time and half-period registers, advancing start to a future base time, and issuing start/stop commands. External timestamp mode switches the AVB parameter pin function and polls `PTPSYNCTS` through a timer because hardware has no FIFO or interrupt.

## State and Persistence Behavior

Persistent driver state lives in `priv->ptp_data`: PHC pointer, caps, command shadow, RX/TX skb queues, external timestamp timer, last `ptpsyncts`, and the lock. Timestamp enablement lives in `priv->hwts_tx_en` and `priv->hwts_rx_en`. The PTP command shadow preserves mode bits such as `corrclk4ts` and `ptpclkadd` across command updates.

Switch static config reload in `sja1105_main.c` locks the PTP data, reads current time with system timestamp, resets/uploads config, sets the hardware time to zero, computes elapsed wall time, and adjusts PHC forward. That makes this file part of the reload persistence story.

## Dependencies and Integration Points

This implementation depends on Linux PTP clock APIs, skb timestamp APIs, timers, SPI helpers, DSA timestamp callbacks, SJA1105 tagger metadata, dynamic AVB parameter writes, and TAS hooks `sja1105_tas_clockstep()` and `sja1105_tas_adjfreq()`. Chip-specific timestamp width, egress timestamp size, register addresses, and optional SJA1110 TX timestamp support come from `struct sja1105_info` and `struct sja1105_regs`.

## Risks and Edge Cases

- E/T partial timestamps wrap in about 0.135 seconds, so queued RX/TX timestamp work must run within one wrap period or reconstruction can be wrong.
- SJA1110 TX timestamp IDs are 8-bit and wrap automatically; heavy outstanding TX timestamp load can misassociate if IDs are reused before meta frames arrive.
- External timestamp support polls a single register at a low rate and has no FIFO, so events faster than supported polling can be lost.
- PTP pin function is shared between periodic output and external timestamp; changing it dynamically writes AVB params and can disturb existing pin users.
- `ptp_clock_register()` error handling uses `IS_ERR_OR_NULL`; callers should handle registration failure and cleanup paths correctly.
- Static reload and PHC operations share the same lock; lock ordering with `fdb_lock` and `mgmt_lock` in reload must remain consistent to avoid deadlocks.

## Test Signals

`ethtool -T` should report hardware TX/RX/raw timestamping and a valid PHC index. `hwstamp_ctl` should enable/disable only `HWTSTAMP_TX_ON` and `HWTSTAMP_FILTER_PTP_V2_L2_EVENT`. `phc2sys` or `testptp` should exercise get/set/adjtime/adjfine. PTP event traffic should produce RX timestamps and management-route TX timestamps on older chips, while SJA1110 should complete TX timestamps through meta frames. Periodic output should toggle the PTP_CLK pin with requested period, and external timestamp mode should report events at the documented low-rate polling limit.

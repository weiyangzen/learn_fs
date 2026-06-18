# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_ptp.c

## Purpose
`ksz_ptp.c` implements hardware timestamping and PTP hardware clock support for PTP-capable KSZ/LAN937x switches. It registers a PHC, controls clock read/set/adjust operations, handles per-output triggers, enables switch timestamp mode, reconstructs partial RX/TX timestamps, and builds nested IRQ domains for transmit timestamp events.

## Important APIs, Types, and Functions
Public functions are `ksz_ptp_clock_register()`, `ksz_ptp_clock_unregister()`, `ksz_get_ts_info()`, `ksz_hwtstamp_get()`, `ksz_hwtstamp_set()`, `ksz_port_txtstamp()`, `ksz_port_deferred_xmit()`, `ksz_port_rxtstamp()`, `ksz_ptp_irq_setup()`, and `ksz_ptp_irq_free()`. PTP clock callbacks include `ksz_ptp_gettime()`, `ksz_ptp_settime()`, `ksz_ptp_adjfine()`, `ksz_ptp_adjtime()`, `ksz_ptp_enable()`, `ksz_ptp_verify_pin()`, and `ksz_ptp_do_aux_work()`. Timestamp IRQ handling is split between a per-port PTP IRQ domain and per-message nested IRQ handlers for Sync, PDelay_Req, and PDelay_Resp.

## Control Flow
Clock registration initializes locks and `ptp_clock_info`, starts the hardware clock, configures P2P transparent-clock behavior, creates pin descriptors, and registers the PHC. `ksz_hwtstamp_set()` validates requested TX/RX modes, updates per-port enable flags and message IRQ enables, sets or clears one-step mode, then calls `ksz_ptp_enable_mode()` to enable PTP tagging and the PTP message parser only when at least one port needs timestamping.

TX timestamping classifies outgoing packets. For one-step P2P, Sync is handled in hardware and PDelay_Resp correction can be updated through the tagger path. For two-step timestampable messages, `ksz_port_txtstamp()` clones the skb and stores it in the KSZ skb control block. `ksz_port_deferred_xmit()` queues the real skb through DSA, waits for a completion triggered by the timestamp IRQ, and completes the clone's TX timestamp. RX timestamping reconstructs full time from the partial timestamp in the tagger metadata and, for one-step P2P PDelay_Req, subtracts the partial ingress timestamp from the correction field.

Clock adjustment paths serialize on `ptp_data.lock`. `settime()` writes shadow time registers and loads the clock; `adjfine()` computes subnanosecond rate correction; `adjtime()` performs hardware step adjustment. If a periodic output is running, set/adjust operations restart it at the next safe event. Auxiliary work refreshes `ptp_data.clock_time` once per second so partial timestamps can be reconstructed around the correct four-second window.

## State and Persistence
PTP state lives in `struct ksz_ptp_data` and per-port PTP fields in `struct ksz_port`: clock pointer, capabilities, pin descriptors, mutex/spinlock, cached clock time, TOU mode, periodic output target/period, hardware timestamp config, TX/RX enable flags, per-message IRQ descriptors, last TX timestamp, and completion. State is volatile and reinitialized on setup; no disk persistence exists. The cached clock time is a software aid for reconstructing partial hardware timestamps.

## Dependencies and Integration Points
The implementation depends on Linux PTP clock APIs, DSA tagger data (`ksz_tagger_data()` and `KSZ_SKB_CB()`), `ptp_classify_raw()`, `ptp_parse_header()`, timestamp completion helpers, irqdomain, common KSZ regmap helpers, and register definitions from `ksz_ptp_reg.h`. `ksz_common.c` calls clock and IRQ setup only for chip data marked `ptp_capable`.

## Risks and Edge Cases
The hardware clock seconds field is 32-bit and trigger target seconds are validated accordingly. Partial timestamp reconstruction depends on the auxiliary worker running often enough and can be wrong if `clock_time` is stale by more than two seconds. `ksz_ptp_tou_reset()` overwrites `ret` after setting `TRIG_RESET`, so an initial reset write failure can be lost if later writes succeed. TX timestamp wait timeout silently drops the timestamp. `HWTSTAMP_TX_ON` is LAN937x-only; other chips support one-step P2P mode. Nested IRQ mask semantics are inverted relative to common IRQ code because the PTP TX interrupt-enable register uses set bits to enable sources.

## Test Signals
Validate `ethtool -T` reports a PHC index and expected modes, `SIOCSHWTSTAMP` accepts supported filters and rejects unsupported TX types, PTP clock get/set/adjfine/adjtime operations, RX timestamp reconstruction across four-second rollover, TX timestamp completion for Sync/PDelay messages, one-step P2P correction updates, perout start/stop with duty-cycle validation, LAN937x GPIO output routing, IRQ mask/unmask behavior, and cleanup through clock unregister and `ksz_ptp_irq_free()`.

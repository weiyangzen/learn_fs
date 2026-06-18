# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_ptp.c

## Purpose
Implements Ocelot PHC/PTP support, hwtstamp configuration, PTP VCAP traps, TX timestamp queueing/completion, perout/PPS, and PHC registration.

## Important APIs/types/functions
PHC callbacks: `ocelot_ptp_gettime64`, `settime64`, `adjtime`, `adjfine`, `verify`, `enable`. Hwtstamp APIs: `ocelot_hwstamp_get/set`, `ocelot_get_ts_info`. TX timestamp APIs: `ocelot_port_txtstamp_request`, `ocelot_get_txtstamp`, queue/dequeue helpers. Init/deinit: `ocelot_init_timestamp`, `ocelot_deinit_timestamp`.

## Control flow, state, persistence
Clock operations serialize on `ptp_clock_lock` and use the TOD access pin. Small time adjustments use hardware delta; large ones read and set time. Perout maps PTP pins and programs waveform periods or PPS sync. Hwtstamp set adds/removes L2 and UDP IPv4/IPv6 VCAP traps and stores per-port rewrite command. TX two-step clones SKBs, assigns timestamp IDs under `ts_id_lock`, queues them, and later matches FIFO entries by port, ID, and sequence ID to complete timestamps. State includes `ptp_clock`, pin descriptors, per-port `trap_proto`, `ptp_cmd`, TX SKB queues, `ptp_skbs_in_flight`, and timestamp stats.

## Dependencies and integration
Depends on Linux PTP/hwtstamp/SKB APIs, PTP classification, Ocelot VCAP traps, SYS/PTP registers, and IFH rewrite operations. Called from `ocelot_net.c`, FDMA RX, and stats paths.

## Risks and test signals
Risks are timestamp-ID exhaustion, stale SKBs, sequence mismatches, FIFO overflow, trap rollback, one-step fallback, and adjtime edge cases. Test with `ptp4l`, `phc2sys`, hwtstamp filters, L2/L4 PTP, one-step and two-step TX, stale timeout stats, PPS/perout, and concurrent PHC adjustment.

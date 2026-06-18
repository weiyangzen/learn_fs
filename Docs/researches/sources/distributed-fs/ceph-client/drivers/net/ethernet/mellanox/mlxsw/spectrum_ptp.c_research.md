# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_ptp.c

## Purpose
This file implements Precision Time Protocol hardware timestamping and PHC support for Spectrum. It provides different clock and packet timestamp paths for Spectrum-1 and Spectrum-2+, hwtstamp get/set operations, PTP trap programming, timestamp matching/garbage collection, shaper setup, ethtool timestamp capabilities, and PTP-specific stats.

## Important APIs, Types, And Functions
Clock APIs include `mlxsw_sp1_ptp_clock_init/fini()` and `mlxsw_sp2_ptp_clock_init/fini()`. State APIs include `mlxsw_sp1_ptp_init/fini()` and `mlxsw_sp2_ptp_init/fini()`. Packet paths are `mlxsw_sp1_ptp_receive()`, `mlxsw_sp1_ptp_transmitted()`, `mlxsw_sp1_ptp_got_timestamp()`, `mlxsw_sp2_ptp_receive()`, and `mlxsw_sp2_ptp_transmitted()`. Hwtstamp APIs are generation-specific get/set and ts-info helpers. Spectrum-1 uses a cyclecounter/timecounter plus an unmatched packet/timestamp rhltable. Spectrum-2 reads UTC registers and reconstructs CQE timestamps.

## Control Flow
Spectrum-1 clock init configures a cyclecounter over free-running FRC registers, starts overflow work, and registers a PTP clock. Its packet path parses PTP headers, matches trapped packets with separately delivered timestamps by port/message/domain/sequence/direction, attaches timestamps when both pieces arrive, or passes packets/timestamps through after GC. Hwtstamp set computes global ingress/egress message-type masks across all ports, updates MTPPPC, balances parsing depth, stores per-port config, and updates the PTP shaper. Spectrum-2 clock init sets UTC time to zero and registers the PHC. Spectrum-2 hwtstamp config is global/refcounted across ports and uses MTPCPC; ingress and egress timestamping must be enabled or disabled together.

## State And Persistence
Spectrum-1 state includes the PTP clock timecounter, overflow work, unmatched hash table, GC work/cycle counter, per-port hwtstamp config/type masks, and GC stats. Spectrum-2 state includes a global hwtstamp config, enabled-port refcount, and mutex. Hardware state includes MTUTC time/frequency adjustment, MTPPS set-at-next-second scheduling, MTPTPT trap mapping, MTPPPC/MTPCPC timestamp classification, MOGCR FIFO clear behavior, QEEC shaper enable, QPSC shaper parameters, and CQE timestamp fields.

## Dependencies And Integration Points
The file depends on Linux PTP clock, timecounter/cyclecounter, hwtstamp, ptp classifier/parser, SKB timestamp APIs, rhashtable/rhltable, mlxsw core register reads, trap IDs, parsing-depth control, port speed queries, and RX/TX listener paths. It is called from port hwtstamp ioctls, ethtool ts-info, trap listeners, and TX completion paths.

## Risks And Edge Cases
Spectrum-1 matching must handle packet-before-timestamp and timestamp-before-packet ordering, duplicate keys, port removal while packets are pending, softirq versus workqueue delivery, and hash growth limits. Spectrum-1 global MTPPPC masks are recomputed from all ports, so parsing-depth balance must stay correct. Spectrum-2 only supports event filters and requires symmetric RX/TX enablement. CQE timestamp reconstruction uses low 8 seconds bits and current UTC, so large delays around wrap would be risky. The checked-out source contains duplicated signature/declaration lines in Spectrum-2 clock and duplicated local declarations in Spectrum-1 update code, compile-risk signals.

## Test Signals
Test PHC register/unregister, `phc2sys` time set/adjust/frequency adjust, hwtstamp ioctl get/set for supported and rejected filters, Spectrum-1 packet/timestamp matching in both arrival orders, GC counters, port removal with pending entries, shaper changes on speed and timestamp state, Spectrum-2 CQE timestamp reconstruction, global refcount enable/disable across multiple ports, and trap programming cleanup.

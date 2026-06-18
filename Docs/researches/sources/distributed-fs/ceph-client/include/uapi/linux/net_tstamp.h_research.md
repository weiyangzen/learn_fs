# sources/distributed-fs/ceph-client/include/uapi/linux/net_tstamp.h

## Purpose
Defines network timestamping UAPI for `SO_TIMESTAMPING`, hardware timestamp configuration, timestamp packet info control messages, transmit-time scheduling, and provider qualifiers.

## Important APIs, Types, And Functions
Exports `hwtstamp_provider_qualifier`, `SOF_TIMESTAMPING_*`, `SOF_TIMESTAMPING_TX_RECORD_MASK`, `so_timestamping`, `hwtstamp_config`, `hwtstamp_flags`, `hwtstamp_tx_types`, `hwtstamp_rx_filters`, `scm_ts_pktinfo`, `txtime_flags`, and `sock_txtime`.

## Control Flow
Applications set socket timestamping flags or pass control messages, configure hardware timestamping through SIOCG/SIOCSHWTSTAMP using `hwtstamp_config`, receive timestamps on normal data or error queues, and optionally schedule transmit times with `SO_TXTIME`.

## State, Persistence, And Dependencies
State persists in socket options, network-device hardware timestamp configuration, PHC binding, and per-packet control metadata. Depends on `linux/types.h` and `linux/socket.h`.

## Integration Points
Used by PTP/IEEE 1588 stacks, time synchronization daemons, packet capture, AF_XDP/NIC timestamp feature reporting, and qdisc transmit-time scheduling.

## Risks
Flags are split between recording and reporting semantics. Drivers may broaden requested RX filters and return the actual filter. Bonded PHC index can change after failover.

## Test Signals
Validate socket option flags/mask, TX software/hardware timestamps, RX filter fallback, PHC binding, packet info cmsgs, one-step timestamp modes, `SO_TXTIME` deadline/error reporting, and invalid flag rejection.

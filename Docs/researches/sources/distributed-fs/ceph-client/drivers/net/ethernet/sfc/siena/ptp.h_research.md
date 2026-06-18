# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/ptp.h

## Purpose

`ptp.h` declares the Siena driver's PTP and hardware timestamping interface. It lets the rest of the driver probe PTP channels, configure timestamping, route PTP packets/events, attach RX timestamps, and start or stop datapath timestamp services.

## Important APIs, Types, and Functions

The header declares probe/channel access (`efx_siena_ptp_defer_probe_with_channel()`, `efx_siena_ptp_channel()`), timestamp config/info operations, PTP TX classification and queuing, mode get/change, MCDI PTP event and time-sync event handling, PTP stats describe/update, RX SKB timestamp attachment, datapath start/stop, MAC TX timestamp capability detection, and TX queue NIC-time conversion.

`efx_rx_skb_attach_timestamp()` is the one inline helper: it calls the heavier attachment function only when `channel->sync_events_state == SYNC_EVENTS_VALID`.

## Control Flow and Integration

RX delivery calls the inline timestamp helper after building an SKB. TX paths use `efx_siena_ptp_is_ptp_tx()` to decide whether a UDP PTP event packet should be diverted to the PTP worker. Event queue processing calls `efx_siena_ptp_event()` for PTP events and `efx_siena_time_sync_event()` for sync events. Netdev timestamp ioctls/ethtool use the config/info methods, while open/close/reset paths use datapath start/stop.

## State and Persistence Behavior

The header exposes no storage but assumes `efx->ptp_data` and channel sync timestamp fields are maintained by `ptp.c`. Its inline helper intentionally avoids work on channels without valid sync events.

## Dependencies, Risks, and Test Signals

It includes `linux/net_tstamp.h` and `net_driver.h`, making it dependent on timestamp config types and channel/NIC state. Contract risks are lifetime and feature gating: callers must handle `-EOPNOTSUPP` when `ptp_data` is absent and must only attach inline RX timestamps when sync state is valid. Tests should compile PTP callers under relevant configs and exercise TX diversion, RX timestamp attachment, event dispatch, and datapath stop/start.

# sources/distributed-fs/ceph-client/net/ncsi/ncsi-aen.c

## Purpose
This file handles NCSI asynchronous event notification packets. It validates AEN packet headers/checksums, updates channel state for link and host-driver events, and triggers failover or reconfiguration when firmware reports link or configuration changes.

## APIs, Types, and Functions
The exported internal entry point is `ncsi_aen_handler()`. Helpers include `ncsi_validate_aen_pkt()`, `ncsi_aen_handler_lsc()` for link status change, `ncsi_aen_handler_cr()` for configuration required, and `ncsi_aen_handler_hncdsc()` for host network controller driver status changes. `ncsi_aen_handlers[]` maps AEN types to expected payload lengths and handlers.

## Control Flow
`ncsi_aen_handler()` reads the skb network header, finds a handler by AEN type, validates revision, length, and checksum, runs the handler, logs errors, and consumes the skb. Link status change handling finds the channel, updates link and OEM status fields, compares previous and new link bits, and then either reshuffles a single-channel setup or updates TX enablement in multi-package/multi-channel setups. Configuration-required handling marks an active, unqueued channel inactive, disables TX mode, queues it, and starts `ncsi_process_next_channel()`. Host-driver-status handling records the firmware status bit and logs whether the host driver is running.

## State and Persistence
AENs mutate `ncsi_channel.modes[NCSI_MODE_LINK]`, `NCSI_MODE_TX_ENABLE`, channel `state`, `link` queue membership, `ndp->flags` such as `NCSI_DEV_RESHUFFLE`, and monitor timers. These changes persist in the per-device topology until later management work reconfigures or suspends channels.

## Dependencies and Integration
The file depends on `internal.h`, `ncsi-pkt.h`, `ncsi_calculate_checksum()`, topology lookup, channel monitors, reset/process helpers, and TX channel update logic in `ncsi-manage.c`. It is called from `ncsi_rcv_rsp()` when a packet type is `NCSI_PKT_AEN`.

## Risks
Failover decisions depend on consistent channel lock and queue state. AENs from inactive channels are only warned about, which is appropriate for firmware noise but can mask sequencing issues. Checksum zero is accepted per spec, so corrupted packets from devices that omit checksums rely on length/revision/type only. Multi-channel update loops must not enable TX on a down or non-whitelisted channel.

## Test Signals
Tests should inject LSC, CR, and HNCDSC packets with good and bad checksums/lengths; verify link mode updates, reshuffle flag behavior, monitor stop/start, queue insertion, reset on last-link loss, and TX channel failover/return-to-preferred behavior.

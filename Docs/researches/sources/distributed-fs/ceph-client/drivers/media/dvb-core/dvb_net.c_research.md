# sources/distributed-fs/ceph-client/drivers/media/dvb-core/dvb_net.c

## Purpose

`dvb_net.c` exposes DVB data services as Linux Ethernet-like network interfaces. It supports MPE section decapsulation and ULE TS-packet decapsulation, manages DVB network interface creation/removal through net ioctls, programs demux feeds and section filters, applies unicast/multicast/promiscuous receive modes, builds `sk_buff` frames, and injects packets into the kernel network stack with `netif_rx`.

## Important APIs, Types, And Functions

`struct dvb_net_priv` is per-net-device state. It stores the PID, host `struct dvb_net`, demux pointer, active section/TS feeds, section filters, multicast filter list, receive mode, work items, feed type, ULE synchronization/continuity state, current ULE skb, ULE header fields, remaining SNDU bytes, TS cell count, and a mutex.

Public module integration is `dvb_net_init` and `dvb_net_release`, exported to adapter code. Userspace-facing net-device management is handled by `dvb_net_do_ioctl` through `NET_ADD_IF`, `NET_GET_IF`, `NET_REMOVE_IF`, and old binary-compatible ioctl variants.

MPE flow uses `dvb_net_feed_start`, `dvb_net_filter_sec_set`, `dvb_net_sec_callback`, and `dvb_net_sec`. ULE flow uses `dvb_net_ts_callback`, `dvb_net_ule`, `dvb_net_ule_new_ts_cell`, `dvb_net_ule_ts_pusi`, `dvb_net_ule_new_ts`, `dvb_net_ule_new_payload`, `dvb_net_ule_check_crc`, `handle_ule_extensions`, and `dvb_net_ule_should_drop`.

Network-device operations are `dvb_net_open`, `dvb_net_stop`, `dvb_net_tx`, `dvb_net_set_multicast_list`, and `dvb_net_set_mac`, installed through `dvb_netdev_ops`. Interface allocation uses `alloc_netdev`, `dvb_net_setup`, `register_netdev`, and `free_netdev`.

## Control Flow

`dvb_net_init` initializes mutexes, clears interface slots, stores the demux pointer, and registers a `DVB_DEVICE_NET`. Userspace opens that DVB net control device and uses privileged ioctls to add/remove interfaces. `NET_ADD_IF` checks `CAP_SYS_ADMIN`, pins the adapter module, allocates a free interface slot, creates a netdev named like `dvbA_B` or `dvbAIDB`, copies the adapter proposed MAC, initializes private state, and registers the netdev.

Opening a netdev increments `in_use` and starts the demux feed. For MPE, the driver allocates a section feed, sets it to the configured PID with CRC checking, programs one or more MAC section filters depending on receive mode, and starts filtering. For ULE, it allocates a TS feed, sets a TS packet feed for the PID, stores the netdev pointer in `tsfeed->priv`, and starts filtering. Stop reverses that state by stopping feed callbacks, releasing section filters or TS feed, and clearing pointers.

MPE callbacks receive complete sections. `dvb_net_sec` validates minimum length and scrambling bits, optionally handles LLC/SNAP, rejects multi-section datagrams, allocates an skb, builds an Ethernet header from the MPE MAC fields and inferred protocol, updates rx stats, and submits the skb.

ULE callbacks receive TS packets. `dvb_net_ule` iterates TS cells, validates sync/TEI/scrambling, synchronizes on PUSI when needed, checks continuity counters, parses ULE SNDU length/D-bit/type, allocates an skb sized for worst-case bridged headers, copies payload across TS cells, verifies CRC32 over length/type/payload, filters destination MAC when present, handles optional and mandatory extension headers, creates or preserves an Ethernet header, updates stats, and calls `netif_rx`.

## State And Persistence Behavior

State is per DVB net control object plus per netdev. `dvbnet->state[]` marks allocated interface slots; `dvbnet->device[]` holds netdev pointers. Per-netdev demux feed state is allocated on open and released on stop. ULE decoder state persists across TS callbacks so fragmented SNDUs can span packets; `reset_ule` clears this state after completion or error.

Receive mode changes and MAC address changes are deferred through work items. The multicast work item stops the feed, computes `RX_MODE_UNI`, `RX_MODE_MULTI`, `RX_MODE_ALL_MULTI`, or `RX_MODE_PROMISC` from netdev flags and multicast list under `netif_addr_lock_bh`, then restarts the feed. MAC changes schedule feed restart if the interface is running.

Removal sets the DVB net control `exit` flag, waits for users, unregisters the DVB control device, then removes all allocated netdevs. `NET_REMOVE_IF` refuses in-use netdevs and drops the adapter module reference only after successful removal.

## Dependencies And Integration Points

The file depends on the DVB demux API for section and TS feeds, Linux netdevice APIs, Ethernet helpers, CRC32, `dvbdev.c` registration/usercopy helpers, and `linux/dvb/net.h` ioctl definitions. It integrates directly with `dvb_demux.c`: MPE uses section feeds and filters, while ULE uses TS feeds.

The net stack sees these as Ethernet-style devices with `IFF_NOARP`, 4096-byte MTU/max MTU, standard Ethernet header ops, receive stats, and an always-drop transmit path (`dvb_net_tx`) because DVB data services are receive-only in this implementation.

## Risks And Edge Cases

ULE decapsulation is stateful and error-prone by design. Invalid sync, TEI, scrambling, continuity jumps, malformed pointer fields, invalid SNDU lengths, CRC failures, unknown mandatory extension headers, and destination MAC mismatches all trigger drops and stats updates. PUSI resynchronization is crucial after partial payload errors.

MPE only handles one-section datagrams; nonzero section number is rejected with frame errors. Some MPE validation is deliberately relaxed for real-world ISP streams, so malformed-but-unscrambled sections may proceed further than strict spec checks.

Feed restart work can race with netdev stop/removal if not flushed. This file flushes both work items during removal, and feed operations use `priv->mutex`, but tests should still exercise concurrent multicast changes, MAC changes, interface close, and removal. Another behavioral edge is `dvb_net_remove_if`: it checks `in_use`, then calls `dvb_net_stop(net)` even when not in use, which decrements `in_use`; tests should verify whether this matches expected lifecycle in this tree.

## Test Signals

Useful tests include adding/removing MPE and ULE interfaces with valid and invalid feed types, permission failures for unprivileged ioctls, get-if bounds checks, netdev open/stop feed allocation failure cleanup, multicast mode transitions with filter programming, MAC change feed restart, MPE sections with IPv4/IPv6/SNAP and bad lengths, ULE TS streams with fragmented SNDUs, D-bit set/unset, bridged extension headers, unknown mandatory extensions, CRC pass/fail, continuity loss, invalid pointer fields, and PUSI resynchronization.

Runtime signals include created/removed network interface logs, rx packet/byte counters increasing on valid data, rx error counters increasing on malformed TS/SNDU/section input, no active demux feeds after netdev stop, and module references balancing after interface removal.

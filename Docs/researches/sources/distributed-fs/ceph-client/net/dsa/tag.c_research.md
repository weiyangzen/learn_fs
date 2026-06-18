# sources/distributed-fs/ceph-client/net/dsa/tag.c

## Purpose
This file implements generic DSA tag driver registration/lookup and the packet receive demultiplexer for tagged frames arriving on DSA conduit devices.

## Important APIs, Types, And Functions
Global state is `dsa_tag_drivers_list` protected by `dsa_tag_drivers_lock`. The packet handler is `dsa_switch_rcv()`, registered through `struct packet_type dsa_pack_type` for `ETH_P_XDSA`. Exported tagger APIs are `dsa_tag_drivers_register()`, `dsa_tag_drivers_unregister()`, `dsa_tag_driver_get_by_name()`, `dsa_tag_driver_get_by_id()`, `dsa_tag_driver_put()`, and `dsa_tag_protocol_to_str()`.

## Control Flow
Module init in `dsa.c` calls `dev_add_pack(&dsa_pack_type)`. On RX, `dsa_switch_rcv()` verifies `dev->dsa_ptr`, unshares the skb, optionally handles hardware port-mux metadata by mapping port ID to a DSA user device, otherwise calls the CPU port tagger receive callback. It then restores Ethernet header context, runs `eth_type_trans()`, handles packets injected directly to upper devices, optionally software-untags VLANs for bridge PVID behavior, updates software stats, defers PTP timestamp delivery when the switch driver asks, and finally submits to GRO cells.

Tag drivers register static `struct dsa_tag_driver` objects. Lookup by name or ID first requests the module alias, then searches the list and pins the owner module with `try_module_get()`. Callers must release with `dsa_tag_driver_put()`.

## State And Persistence
Registered taggers remain in the global list while their modules are loaded. Lookup takes module references. RX uses per-conduit `dev->dsa_ptr` and per-CPU-port receive callbacks set during DSA setup or tagger change.

## Dependencies And Integration Points
This integrates with Linux packet handlers, skb metadata destinations, DSA tagger modules, DSA user netdev private data, GRO cells, PTP classification/timestamp callbacks, bridge VLAN software untagging from `tag.h`, and conduit setup.

## Risks And Edge Cases
Packets arriving after conduit teardown see NULL `dsa_ptr` and are dropped. Tagger receive callbacks must return a valid user skb or NULL to drop. Hardware metadata path assumes device 0 in `dsa_conduit_find_user()`. PTP timestamp deferral depends on temporary header push/pull and switch driver ownership of the skb. Module reference handling is mandatory around runtime tagger changes.

## Test Signals
Tests should cover tagger registration/unregistration, module autoload aliases, lookup by name and ID, RX demux through tag callback and metadata path, VLAN untagging behavior, PTP timestamp deferral, GRO delivery, and drop behavior for NULL `dsa_ptr` or unknown ports.

# sources/distributed-fs/ceph-client/net/batman-adv/tvlv.c

## Purpose
This file implements the batman-adv TVLV API: registration of locally advertised type-version-length-value containers, registration of handlers for received TVLVs, appending TVLVs to outgoing OGMs, parsing received TVLV buffers, and sending unicast TVLV packets to originators.

## Important APIs, Types, And Functions
`batadv_tvlv_container_register()` and `batadv_tvlv_container_unregister()` manage advertised containers stored in `bat_priv->tvlv.container_list`. `batadv_tvlv_container_ogm_append()` resizes an OGM buffer and serializes all current containers after the base OGM header. `batadv_tvlv_handler_register()` and `batadv_tvlv_handler_unregister()` manage callbacks in `bat_priv->tvlv.handler_list`. `batadv_tvlv_containers_process()` parses a received TLV stream and dispatches to OGM, unicast, or multicast callbacks. `batadv_tvlv_ogm_receive()` extracts the OGM TVLV area, and `batadv_tvlv_unicast_send()` builds and sends a `BATADV_UNICAST_TVLV` skb through `batadv_send_skb_to_orig()`.

## Control Flow
Container registration allocates one object containing `struct batadv_tvlv_hdr` plus optional payload, removes any existing type/version match, and inserts the replacement under `container_list_lock`. OGM append first computes total advertised length under the same lock, reallocates the packet buffer, then copies each header and payload in wire order. Receive-side processing walks the buffer while complete headers and payload lengths remain, looks up a matching handler by type/version, calls the protocol-specific callback, and releases the handler reference. After OGM processing, handlers with `BATADV_TVLV_HANDLER_OGM_CIFNOTFND` are called with empty data when they were not seen in the OGM interval. Unicast send resolves an originator by destination MAC, constructs a control-priority skb, embeds one TVLV header and payload, and hands the skb to the originator send path.

## State, Persistence, And Dependencies
State is per mesh interface in `bat_priv->tvlv`. Containers are protected by `container_list_lock`; handlers are inserted and removed under `handler_list_lock` but are traversed with RCU and refcounted with `kref`. Handler objects are freed by `kfree_rcu()`, while container objects are freed after list removal and reference release. There is no disk persistence; advertised TVLVs live until replacement, unregistration, or mesh teardown.

## Integration Points
The file depends on packet definitions from `uapi/linux/batadv_packet.h`, originator lookup in `originator.h`, and the transmit path in `send.h`. Feature modules such as gateway, multicast, translation table, DAT, and algorithm code register TVLV containers or handlers through this API. OGM code calls `batadv_tvlv_container_ogm_append()` for outbound advertisements and `batadv_tvlv_ogm_receive()` for inbound OGMs.

## Risks
Correctness depends on lock discipline: container lookup/removal requires `container_list_lock`, while handlers require RCU-safe lookup and paired `batadv_tvlv_handler_put()`. `batadv_tvlv_container_ogm_append()` returns the desired TVLV length even if packet-buffer reallocation fails, so callers must treat the actual packet buffer length carefully. Handler `flags` are modified while processing OGMs from RCU traversal, so missed or concurrent updates could affect CIFNOTFND notifications. Packet parsing stops silently on malformed truncated TVLV lengths, which is robust for forwarding but can hide peer bugs.

## Test Signals
Useful signals include OGM packets containing all registered containers with correct network-order lengths, replacement/unregistration removing stale TVLVs, malformed TVLV buffers not overrunning, CIFNOTFND callbacks firing exactly once per absent OGM TVLV, unicast TVLV routing only when an originator exists, and KASAN/lockdep coverage for handler/container lifetime races.

# sources/distributed-fs/ceph-client/net/can/gw.c

## Purpose
This file implements the CAN gateway/router/bridge facility exposed through rtnetlink route messages for `PF_CAN`. It creates CAN-to-CAN forwarding jobs between interfaces, optionally modifies CAN/CAN FD frames, updates checksums, limits routing hops, records counters, and removes jobs on request, namespace exit, or device unregister.

## Important APIs, Types, And Functions
`struct cgw_job` is one gateway job. It stores source/destination devices, CAN filter, flags, hop limit, handled/dropped/deleted counters, and an RCU-protected `struct cf_mod`. `struct cf_mod` stores AND/OR/XOR/SET modification frames, precomputed function pointers, checksum definitions, checksum function pointers, and optional UID.

The hot-path callback is `can_can_gw_rcv()`. Netlink operations are `cgw_create_job()`, `cgw_remove_job()`, and `cgw_dump_jobs()`, registered as `RTM_NEWROUTE`, `RTM_DELROUTE`, and `RTM_GETROUTE` handlers for `PF_CAN`. Parsing and serialization are handled by `cgw_parse_attr()` and `cgw_put_job()`.

Modification helpers cover CAN ID, length/DLC, flags, Classic CAN data, CAN FD data, and DLC conversion through `mod_retrieve_ccdlc()`/`mod_store_ccdlc()`. Checksum helpers support XOR and CRC8 over absolute or length-relative data ranges.

## Control Flow
Module init clamps the `max_hops` parameter, registers per-net state, creates a job slab cache, registers a netdevice notifier, and registers rtnetlink handlers.

Creating a route requires `CAP_NET_ADMIN`, an `AF_CAN` route message, and currently `CGW_TYPE_CAN_CAN`. `cgw_parse_attr()` validates and normalizes attributes, precomputes modification/checksum function arrays, reads source/destination ifindices, and rejects incomplete interface combinations. `cgw_create_job()` supports UID-based in-place modification updates when UID, interfaces, and filters match. Otherwise it allocates a new job, resolves source/destination CAN devices under RTNL, rejects same-interface routing unless explicitly allowed, registers the source CAN filter, and adds the job to the per-net hlist under RCU.

When a matching CAN frame arrives, `can_can_gw_rcv()` verifies Classic CAN versus CAN FD mode, finds CAN skb extension state, enforces global/private hop limits, checks destination link up, rejects loop-back-to-incoming-interface unless allowed, clones or copies the skb depending on whether modifications are configured, copies the CAN skb extension to increment hop count, applies modification function pointers, validates the modified length against available frame storage, updates configured checksums, optionally clears timestamps, and sends through `can_send()`.

Removal parses the same attributes, removes all jobs when both ifindices are zero, or finds the first job matching flags, hop limit, UID or full modification content, and CAN gateway tuple. Device unregister removes any job using that source or destination device.

## State And Persistence
Jobs live in `net->can.cgw_list` for the network namespace and persist until deletion, namespace exit, module exit, or device unregister. The counters are in memory and exported through route dumps. `cf_mod` is replaced under RTNL with RCU assignment for UID updates; old modification data is freed after an RCU grace period.

There is no persistence outside kernel memory. The module-level `max_hops` parameter is read-only after load and bounds routing-loop protection.

## Dependencies And Integration Points
The gateway integrates with PF_CAN receive filters and `can_send()`, rtnetlink message dispatch, net namespace lifecycle, netdevice notifiers, CAN skb extensions, and CAN gateway UAPI attributes from `linux/can/gw.h`.

It assumes RTNL protection for route creation/removal and RCU read protection for hot-path job traversal and modification access.

## Risks And Edge Cases
The receive path is a hot path with user-configured transformations. Length/DLC modifications can delete frames if they produce a length larger than the backing skb frame capacity. Checksum parameter validation only constrains configured indices to possible CAN/CAN FD ranges; runtime relative indices can still become negative for short received frames and then skip checksum writes.

Routing-loop protection depends on CAN skb extension hop counters. Frames without a CAN skb extension are ignored by the gateway.

UID updates replace only modification data, not interfaces or filters. Attempts to reuse a UID with a different gateway tuple return `-EINVAL`.

Gateway creation accepts same source and destination only with `CGW_FLAGS_CAN_IIF_TX_OK`; otherwise it rejects self-routing to avoid immediate loops.

`cgw_put_job()` dumps counters only when nonzero, so user-space readers must treat missing stats attributes as zero.

## Test Signals
Strong test signals are rtnetlink route create/delete/dump tests with `CAP_NET_ADMIN`, vcan interface pairs, Classic CAN and CAN FD forwarding, every modification type, checksum profiles, UID update behavior, route loop hop limits, timestamp preservation flags, same-interface rejection/allowance, and device unregister cleanup.

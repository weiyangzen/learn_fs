# sources/distributed-fs/ceph-client/net/can/af_can.c

## Purpose
This file implements the PF_CAN core protocol family. It registers the CAN socket family, dispatches incoming Classic CAN, CAN FD, and CAN XL sk_buffs to protocol subscribers, manages receive-filter lists per network namespace and per CAN device, exports the common CAN transmit helper, and provides protocol registration for CAN transport modules such as BCM, ISO-TP, and J1939.

## Important APIs, Types, And Functions
The external API surface is `can_send()`, `can_rx_register()`, `can_rx_unregister()`, `can_set_skb_uid()`, `can_proto_register()`, `can_proto_unregister()`, and `can_sock_destruct()`. Protocol modules use `can_proto_register()` with a `struct can_proto` containing socket type, protocol number, `proto_ops`, and `struct proto`, and use the receive registration helpers to subscribe callbacks to CAN identifiers and masks.

The core state includes the global RCU `proto_tab[CAN_NPROTO]`, `proto_tab_lock`, a `kmem_cache` for `struct receiver`, per-net `net->can.rx_alldev_list`, `net->can.pkg_stats`, `net->can.rcv_lists_stats`, and each CAN netdevice's `can_ml_priv.dev_rcv_lists`.

Receive-list selection is performed by `can_rcv_list_find()`. It normalizes filters into error, all, inverted, general masked, exact standard ID, or hashed extended ID lists. `effhash()` reduces 29-bit extended identifiers into `rx_eff[]` buckets.

## Control Flow
Socket creation enters through `can_create()`. It validates the protocol number, looks up a registered `can_proto` under RCU, optionally triggers `request_module("can-proto-%d")`, checks socket type, allocates the protocol socket with `sk_alloc()`, attaches `sock_init_data()`, installs `can_sock_destruct()`, and calls the protocol-specific `init()` hook.

Transmit callers provide a fully formed skb to `can_send()`. The helper validates the frame type with `can_is_can_skb()`, `can_is_canfd_skb()`, or `can_is_canxl_skb()`, assigns the Ethernet protocol, enforces device MTU, CAN ARP type, and `IFF_UP`, resets packet headers, optionally prepares local loopback or driver echo behavior, submits to `dev_queue_xmit()`, injects a software-loopback clone with `netif_rx()` when needed, and updates per-net TX statistics.

Receive registration allocates a `receiver`, canonicalizes the filter, and adds it to an RCU hlist under `net->can.rcvlists_lock`. Receive delivery comes from packet handlers `can_rcv()`, `canfd_rcv()`, and `canxl_rcv()`, which reject malformed skbs and then call `can_receive()`. `can_receive()` stamps a nonzero skb hash, runs `can_rcv_filter()` first on the namespace all-device list and then on the device list, consumes the driver skb, and updates RX/match counters.

Module init builds the `can_receiver` slab cache, registers per-net state, registers `PF_CAN`, and attaches packet handlers for `ETH_P_CAN`, `ETH_P_CANFD`, and `ETH_P_CANXL`. Exit removes packet handlers, unregisters PF_CAN, tears down per-net state, waits for RCU callbacks, and destroys the cache.

## State And Persistence
All state is kernel-resident and scoped to module lifetime, net namespace lifetime, or socket/protocol lifetime. Protocol registrations are global but RCU-protected. Receive subscriptions persist until the owning protocol or socket unregisters them. Per-net stats are reset on namespace init and optionally surfaced/updated through proc support. There is no disk persistence.

Receiver deletion is deferred with `call_rcu()`. If a receiver is associated with a socket, the unregister path takes a temporary socket reference before the RCU callback so callbacks cannot race a final free.

## Dependencies And Integration Points
This core depends on the Linux networking stack (`sock_register()`, `dev_add_pack()`, per-net operations, `dev_queue_xmit()`), CAN skb validation helpers from `linux/can/skb.h`, CAN multi-layer device private state from `linux/can/can-ml.h`, and optional proc helpers declared in `af_can.h`.

It is the central integration point for CAN protocol modules. BCM, ISO-TP, J1939, raw CAN, and gateway code all depend on its transmit helper, protocol registry, and receive filter dispatcher.

## Risks And Edge Cases
`can_rx_unregister()` warns rather than failing when no matching receiver is found. That is intentional for races with device removal, but it can hide protocol-layer reference bugs.

Filter canonicalization mutates the caller-provided `can_id` and `mask` locals before storage and before unregister matching. Callers must pass the same logical filter values to unregister, relying on the same normalization to find the same hlist.

`can_send()` consumes the skb on validation failures and on normal transmission. Callers must not reuse the skb after calling it, including on errors.

Receive callbacks run under an RCU read-side section and receive a borrowed skb that is consumed after dispatch. Protocol callbacks must clone if they retain data beyond the callback.

The receive hot path depends on valid CAN skb extensions; malformed or hand-crafted skbs are dropped with a one-time warning.

## Test Signals
Likely test signals are kernel CAN selftests and protocol-specific tests that exercise PF_CAN sockets, local loopback, CAN FD/XL validation, and net namespace teardown. Important coverage includes register/unregister races, software loopback when `IFF_ECHO` is absent, exact SFF/EFF filter fast paths, inverted/error filters, and module autoload through `can-proto-*`.

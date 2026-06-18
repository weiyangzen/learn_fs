# sources/distributed-fs/ceph-client/net/ipv4/xfrm4_protocol.c

## Purpose
This file is the IPv4 XFRM protocol multiplexer for ESP, AH, and IPComp. It registers IPv4 protocol handlers with the inet layer, maintains priority-ordered XFRM protocol handler chains, dispatches input/error/callback events, and registers IPv4 XFRM input AF info.

## Important APIs, Types, and Functions
Key exports are `xfrm4_rcv_encap()`, `xfrm4_protocol_register()`, and `xfrm4_protocol_deregister()`. Important internals are `xfrm4_esp_rcv/err()`, `xfrm4_ah_rcv/err()`, `xfrm4_ipcomp_rcv/err()`, `xfrm4_rcv_cb()`, `proto_handlers()`, `netproto()`, and the `esp4_handlers`, `ah4_handlers`, and `ipcomp4_handlers` RCU lists.

## Control Flow
Registration validates protocol support, inserts the handler by descending priority under `xfrm4_protocol_mutex`, and adds the inet protocol handler when the first XFRM handler for that protocol appears. Receive callbacks iterate the relevant RCU handler chain until a handler accepts the packet by returning something other than `-EINVAL`; otherwise ICMP port-unreachable is sent and the skb is freed. Deregistration removes the handler, unregisters the inet protocol when the chain becomes empty, unlocks, and waits for `synchronize_net()`.

## State and Persistence Behavior
Persistent global state is the RCU head pointer for each protocol's handler chain and the registered `xfrm_input_afinfo`. Handler objects are owned by provider modules; this file only links/unlinks them.

## Dependencies and Integration Points
It integrates with inet protocol registration, ICMP unreachable generation, XFRM input core callbacks, RCU, mutex serialization, ESP/AH/IPComp provider modules, and UDP encap input via `xfrm4_rcv_encap()`.

## Risks
Priority collision returns `-EEXIST`; bad ordering can route packets to the wrong transform implementation. Registering the inet protocol after unlocking can leave partial state if `inet_add_protocol()` fails. Deregistration must wait for RCU readers before module code unloads.

## Test Signals
Test handler priority order, duplicate priority rejection, register/deregister for ESP/AH/IPComp, unknown protocol rejection, no-handler ICMP behavior, encap receive with route lookup, error handler fallback, and concurrent receive during module unload.

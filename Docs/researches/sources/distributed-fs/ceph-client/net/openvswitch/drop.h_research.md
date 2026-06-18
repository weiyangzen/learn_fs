# sources/distributed-fs/ceph-client/net/openvswitch/drop.h

## Purpose
`drop.h` defines the Open vSwitch datapath-specific skb drop reason namespace. It is a small integration header that lets action execution, conntrack, fragmentation, meter handling, and explicit drop actions report a structured `SKB_DROP_REASON_SUBSYS_OPENVSWITCH` reason instead of freeing packets anonymously.

## Important APIs, Types, and Functions
`OVS_DROP_REASONS(R)` is the authoritative list of OVS drop reason symbols. The macro is reused by this header to build `enum ovs_drop_reason` and by datapath registration code to publish string names through the kernel drop reason subsystem. Listed causes include action errors, explicit drop actions, meter drops, recursion/deferred action limits, fragmentation failures, conntrack failures, and IP TTL drops.

`enum ovs_drop_reason` starts from the Open vSwitch subsystem offset by deriving `__OVS_DROP_REASON` from `SKB_DROP_REASON_SUBSYS_OPENVSWITCH << SKB_DROP_REASON_SUBSYS_SHIFT`. This keeps OVS reasons disjoint from core skb reasons and other subsystem reason ranges.

`ovs_kfree_skb_reason(struct sk_buff *skb, enum ovs_drop_reason reason)` is the local convenience wrapper over `kfree_skb_reason()`. Call sites can pass an OVS enum value and avoid repeating casts to `u32`.

## Control Flow and Integration
The header itself has no runtime state. Its values are consumed by files such as `actions.c`, `conntrack.c`, and `datapath.c`: packet execution paths call `ovs_kfree_skb_reason()` when they intentionally drop an skb, and module init registers the generated reason strings with `drop_reasons_register_subsys()`.

## State and Persistence
The only persisted behavior is the ABI-like ordering of reason identifiers inside the subsystem range. Reordering or removing entries can change observed reason values and trace/drop monitor output.

## Dependencies
It depends on `linux/skbuff.h` and `net/dropreason.h`. It assumes the kernel provides subsystem-scoped skb drop reasons.

## Risks
Adding a reason requires updating the macro list and ensuring datapath registration still exports matching strings. Because drop reasons are externally observable through tracing and packet drop monitoring, careless renumbering can break diagnostics. Callers must pass only OVS subsystem reasons to the wrapper.

## Test Signals
Useful signals are kernel build coverage, drop monitor/trace output showing OVS-specific reason strings, action paths that trigger explicit drop, meter drop, TTL drop, and conntrack drop, and module load/unload exercising drop reason registration in `datapath.c`.

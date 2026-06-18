# sources/distributed-fs/ceph-client/net/openvswitch/conntrack.h

## Purpose

This header declares the Open vSwitch conntrack interface used by flow parsing, action execution, and datapath initialization. It also provides no-conntrack stubs so the rest of OVS can build when `CONFIG_NF_CONNTRACK` is disabled.

## Important APIs, Types, and Functions

When conntrack is enabled, the header declares lifecycle (`ovs_ct_init`, `ovs_ct_exit`), attribute verification (`ovs_ct_verify`), action parse/serialize/free (`ovs_ct_copy_action`, `ovs_ct_action_to_attr`, `ovs_ct_free_action`), packet execution (`ovs_ct_execute`, `ovs_ct_clear`), and flow key helpers (`ovs_ct_fill_key`, `ovs_ct_put_key`). It defines `CT_SUPPORTED_MASK` as the set of OVS CT state bits available to matching.

When conntrack is disabled, inline stubs return `-ENOTSUPP`, clear CT key fields, or free/drop skbs as appropriate. If conncount is enabled, it also declares `dp_ct_limit_genl_family`.

## Control Flow

The header has compile-time control flow via `#if IS_ENABLED(CONFIG_NF_CONNTRACK)`. Call sites can use the same function names independent of configuration; either the real implementation in `conntrack.c` or stubs are compiled.

## State and Persistence

No state is owned here. The declarations describe per-net conntrack initialization and flow-key CT fields. Disabled stubs explicitly zero `ct_state`, `ct_zone`, `ct.mark`, labels, and `ct_orig_proto` so keys remain deterministic.

## Dependencies and Integration Points

It includes `flow.h` and is included by datapath and action code. It is the feature boundary between core OVS and netfilter conntrack.

## Risks and Edge Cases

The disabled `ovs_ct_execute()` stub frees the skb before returning `-ENOTSUPP`; callers must not continue to use the skb. Feature availability is compile-time dependent, so userspace must handle action rejection when conntrack is unavailable.

## Test Signals

Build tests with `CONFIG_NF_CONNTRACK=y/m/n` should validate real/stub symbol selection. Runtime tests without conntrack should verify CT actions are rejected during action validation and CT key fields serialize as absent/zero as expected.

# sources/distributed-fs/ceph-client/net/netlink/policy.c

## Purpose

`policy.c` converts kernel `struct nla_policy` arrays into netlink-advertised policy descriptions. It is used by extended ACK reporting and Generic Netlink `CTRL_CMD_GETPOLICY` so userspace can inspect expected attribute types, nested policies, ranges, masks, and length constraints.

## Important APIs, Types, and Functions

`struct netlink_policy_dump_state` stores a linear table of unique policy pointer plus maxattr pairs and cursor fields `policy_idx` and `attr_idx`. Public APIs are `netlink_policy_dump_add_policy()`, `netlink_policy_dump_get_policy_idx()`, `netlink_policy_dump_loop()`, `netlink_policy_dump_attr_size_estimate()`, `netlink_policy_dump_write_attr()`, `netlink_policy_dump_write()`, and `netlink_policy_dump_free()`.

Internal helpers include `alloc_state()`, `add_policy()`, `netlink_policy_dump_finished()`, and `__netlink_policy_dump_write_attr()`.

## Control Flow

Dump setup calls `netlink_policy_dump_add_policy()` with one or more root policies. It allocates state on first use, adds the root policy, then walks every registered policy looking for `NLA_NESTED` and `NLA_NESTED_ARRAY` entries and appends those nested policies as additional indexed entries. This produces a stable index table for the dump.

Output code repeatedly calls `netlink_policy_dump_loop()` and `netlink_policy_dump_write()`. `netlink_policy_dump_write()` emits one non-empty attribute description per call, skipping `NLA_UNSPEC` and `NLA_REJECT`, and advances the policy and attribute cursor. Attribute output records the normalized netlink policy type plus optional nested policy index, numeric min/max, masks, bitfield masks, or string/binary length constraints.

## State and Persistence Behavior

Dump state is per-dump heap memory. It persists only between netlink dump callbacks and is freed by the caller through `netlink_policy_dump_free()`. It references static policy arrays owned by netlink families; it does not copy policies.

## Dependencies and Integration Points

The file depends on netlink attribute policy definitions and range helpers from `<net/netlink.h>`. `genetlink.c` uses it for controller policy dumps, and `af_netlink.c` uses attribute size estimation and single-attribute output for extended ACK policy TLVs.

## Risks and Edge Cases

Policy identity is pointer plus maxattr, so dynamically allocated policies must remain alive for the whole dump. Nested policy discovery can reallocate state, and failure semantics try to preserve caller-visible state only when a state already existed. Output intentionally skips reject/unspecified entries; callers must tolerate `-ENODATA` as "nothing useful to emit." Size estimates must stay in sync with emitted attributes or ACK allocation can be too small.

## Test Signals

Use `CTRL_CMD_GETPOLICY` against families with nested attributes, arrays, masks, signed and unsigned ranges, strings, binaries, flags, and bitfield32 attributes. Extended ACK tests with bad attributes should include `NLMSGERR_ATTR_POLICY` output when `NETLINK_EXT_ACK` is enabled.

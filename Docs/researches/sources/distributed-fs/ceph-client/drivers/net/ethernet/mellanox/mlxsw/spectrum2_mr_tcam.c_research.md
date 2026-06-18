<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum2_mr_tcam.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum2_mr_tcam.c

## Purpose

`spectrum2_mr_tcam.c` adapts the generic Spectrum ACL TCAM machinery for Spectrum-2 multicast-router route lookup. It creates IPv4 and IPv6 ACL rulesets for multicast route keys, binds those rulesets to hardware multicast-router protocol tables, and exposes create/destroy/update callbacks through `mlxsw_sp2_mr_tcam_ops`.

## Important APIs, Types, And Functions

- `struct mlxsw_sp2_mr_tcam` stores the owning `mlxsw_sp`, a private flow block, and IPv4/IPv6 ACL rulesets.
- `struct mlxsw_sp2_mr_route` stores the TCAM instance pointer needed for later action replacement.
- `mlxsw_sp2_mr_tcam_ipv4_init()` and `mlxsw_sp2_mr_tcam_ipv6_init()` build fixed element usages and call `mlxsw_sp_acl_ruleset_get()` with `MLXSW_SP_ACL_PROFILE_MR`.
- `mlxsw_sp2_mr_tcam_bind_group()` writes `PEMRBT` to bind an ACL group id to IPv4 or IPv6 multicast-router lookup.
- `mlxsw_sp2_mr_tcam_rule_parse4()` and `mlxsw_sp2_mr_tcam_rule_parse6()` encode VRID, source, and group fields into ACL key/mask values.
- `mlxsw_sp2_mr_tcam_route_create()`, `route_destroy()`, and `route_update()` create ACL rules, delete them by cookie, and replace their AFA action block.

## Control Flow

Initialization creates a private flow block, then builds and binds IPv4 and IPv6 MR rulesets. IPv4 rules use VRID plus 32-bit source/group addresses. IPv6 rules split the VRID and 128-bit source/group addresses across Spectrum-2 AFK elements. Route creation selects the ruleset by `key->proto`, creates an ACL rule keyed by the route-private pointer, fills priority and key fields, then installs it through `mlxsw_sp_acl_rule_add()`. Destroy looks up the rule in the selected ruleset and deletes it. Update looks up the rule and calls `mlxsw_sp_acl_rule_action_replace()` with a new action block.

## State And Persistence

State is in memory in the MR TCAM object, route-private objects, ACL flow block, rulesets, and ACL rule hash tables. Hardware state persists in the ACL group binding register and in TCAM entries/actions until rules are deleted or the driver tears down the rulesets. There is no disk persistence.

## Dependencies And Integration Points

The file depends on `spectrum_mr.h` route keys and ops, the ACL ruleset/rule APIs in `spectrum_acl.c`, AFK element encoding, AFA action blocks, flow block lifetime helpers, and register packing for `PEMRBT`. It integrates multicast routing with the same TCAM profile backend used by flower offload, but uses the MR profile so group binding is handled by multicast router initialization rather than by port ACL binding.

## Risks

- Wrong VRID or IPv6 element splitting will silently program routes that never match or match the wrong multicast stream.
- The route cookie is the route-private pointer cast to `unsigned long`; route-private lifetime must outlive lookup/delete/update.
- `WARN_ON(!ruleset)` paths return or bail out, but protocol enum expansion would need explicit handling.
- Group binding must happen before route insertion; bind failure unwinds the ruleset, but later hardware failures can leave multicast routing unavailable.
- Route update only replaces actions, not keys or priority.

## Test Signals

Useful signals are Spectrum-2 IPv4 and IPv6 multicast route offload, route deletion and action update, failure injection on `PEMRBT` writes and ACL rule insertion, VRID values near the 12-bit limit, masked source/group routes, and parity between software multicast forwarding and hardware hit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum2_mr_tcam.c -->

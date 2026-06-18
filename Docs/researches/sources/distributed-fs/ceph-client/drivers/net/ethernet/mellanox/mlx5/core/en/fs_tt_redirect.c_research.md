# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/fs_tt_redirect.c

## Purpose

`en/fs_tt_redirect.c` implements auxiliary flow-steering tables that redirect selected traffic types from the main TTC table into feature-specific flow tables. It supports UDP IPv4/IPv6 destination-port rules and an ANY ethertype table, with default rules that fall back to the original TTC destinations.

## Important APIs, Types, and Functions

- `struct mlx5e_fs_udp` owns IPv4/IPv6 UDP flow tables, default rules, and a refcount.
- `struct mlx5e_fs_any` owns the ANY flow table, default rule, and a refcount.
- `mlx5e_fs_tt_redirect_udp_create/destroy()` create/destroy UDP redirect tables and point TTC UDP traffic types at them.
- `mlx5e_fs_tt_redirect_udp_add_rule()` adds a UDP dport rule forwarding to a TIR.
- `mlx5e_fs_tt_redirect_any_create/destroy()` create/destroy the ANY redirect table and point TTC ANY traffic at it.
- `mlx5e_fs_tt_redirect_any_add_rule()` adds an ethertype rule forwarding to a TIR.
- `mlx5e_fs_tt_redirect_del_rule()` deletes a rule handle.

## Control Flow

UDP create allocates state, stores it in `mlx5e_flow_steering`, creates one table for IPv4 UDP and one for IPv6 UDP, creates two groups per table (specific-match and default), adds default rules to the original TTC destinations, then changes TTC destinations to the new tables. Destroy decrements the refcount, restores TTC default destinations, deletes default rules and tables, frees state, and clears the FS pointer.

ANY create follows the same pattern for a single table matching ethertype. Add-rule paths allocate a flow spec, set outer-header match criteria, point the destination to a provided TIR, add the rule to the relevant table, free the spec, and return the rule handle.

## State and Persistence Behavior

Persistent state includes firmware flow tables, flow groups, default flow rules, TTC rule destinations, refcounts, and submodule pointers stored in `mlx5e_flow_steering`. Caller-added rule handles persist until explicitly deleted.

## Dependencies and Integration Points

Depends on `en/fs_tt_redirect.h`, `en/fs.h`, `fs_core.h`, TTC helpers, flow table creation/destruction, mlx5 flow spec macros, and RX TIR numbers. It is used by features that need to steer specific UDP ports or ethertypes away from default TTC handling.

## Risks and Edge Cases

- `fs_any_create_groups()` allocates `MLX5E_FS_UDP_NUM_GROUPS`; this currently equals the ANY group count but is semantically coupled to the UDP constant.
- `fs_any_create_table()` uses `MLX5E_FS_UDP_TABLE_SIZE`; it currently matches the ANY table size formula but is another semantic coupling.
- Destroy paths call `fs_udp_disable()` / `fs_any_disable()` and ignore errors, so TTC restoration failures only log inside helpers if returned there.
- Refcounts are plain ints with no local locking; callers must serialize create/destroy.
- Add-rule functions assume the redirect state exists and table pointers are valid.

## Test Signals

Create UDP and ANY redirect tables, add rules for IPv4/IPv6 UDP ports and ethertypes, verify packets hit selected TIRs, then destroy and confirm TTC defaults are restored. Test multiple create/destroy users via refcount. Fault-inject flow table/group/rule creation failures and validate unwind.

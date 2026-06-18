# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/fs_tt_redirect.h

## Purpose

`en/fs_tt_redirect.h` declares traffic-type redirect APIs for UDP and ANY flow-steering tables.

## Important APIs, Types, and Functions

- `mlx5e_fs_tt_redirect_del_rule()` deletes a returned flow rule.
- UDP APIs create/destroy redirect tables and add dport-to-TIR rules for a TTC UDP traffic type.
- ANY APIs create/destroy the redirect table and add ethertype-to-TIR rules.

## Control Flow

Feature modules call create before adding rules, keep rule handles, delete rules when no longer needed, and call destroy when the redirect table is no longer used.

## State and Persistence Behavior

Implementations persist redirect table state in `struct mlx5e_flow_steering` and firmware flow tables/rules. The header exposes only opaque flow handles.

## Dependencies and Integration Points

Depends on `en/fs.h`, mlx5 traffic type enums, flow handles, and TIR numbers. Integrated with feature steering modules needing traffic-type fanout.

## Risks and Edge Cases

Callers must serialize lifecycle, handle `ERR_PTR` from add-rule/create operations, and not delete rules after destroying the owning table.

## Test Signals

Compile users and exercise UDP/ANY redirect lifecycle with packet steering validation and error-unwind tests.

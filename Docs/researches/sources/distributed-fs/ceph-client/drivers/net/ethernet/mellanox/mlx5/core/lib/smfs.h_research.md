# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/smfs.h

## Purpose
`smfs.h` declares the mlx5 SMFS wrapper API for creating direct-rule matchers, actions, and rules from ordinary mlx5 flow-steering structures.

## Important APIs, types, and functions
The header exposes matcher create/destroy, conversion from `struct mlx5_flow_table` to `struct mlx5dr_table`, destination-table action creation, flow-counter action creation, action destroy, rule create, and rule destroy. It includes the mlx5dr public and direct-rule type headers.

## Control flow
No standalone flow exists. Callers obtain a direct-rule table from an FS table, create matchers/actions, create rules with match specs, and destroy objects in reverse order.

## State and persistence behavior
No state is owned by the header. Object lifetime is external and handled by the implementation plus underlying mlx5dr code.

## Dependencies and integration points
The header ties mlx5 flow steering to software managed flow steering. It depends on direct-rule types and the flow spec/table types visible through included mlx5dr headers.

## Risks and edge cases
The API returns raw pointers and does not encode ownership in types. Callers must destroy only objects they created and must keep table/matcher/action lifetimes ordered correctly.

## Test signals
Build coverage and SMFS rule lifecycle tests validate the declarations. Static analysis can catch missing destroy calls in users.

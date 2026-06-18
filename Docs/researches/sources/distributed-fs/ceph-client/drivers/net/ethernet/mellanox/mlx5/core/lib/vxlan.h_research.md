# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/vxlan.h

## Purpose
`vxlan.h` declares the mlx5 VXLAN UDP-port table API and provides capability/stub helpers around optional `CONFIG_VXLAN` support.

## Important APIs, types, and functions
It forward-declares `struct mlx5_vxlan` and `struct mlx5_vxlan_port`, defines `mlx5_vxlan_max_udp_ports()` from firmware capability with a default of 4, defines `mlx5_vxlan_allowed()` for non-error pointers, and declares or stubs create/destroy/add/delete/lookup/reset functions depending on `CONFIG_VXLAN`.

## Control flow
The header has no standalone flow. Callers create a VXLAN context, guard operations with `mlx5_vxlan_allowed()` or rely on helper no-ops, add/delete ports as tunnel sockets are configured, and reset or destroy during teardown.

## State and persistence behavior
No state is stored here. The allowed helper interprets unsupported state encoded by `mlx5_vxlan_create()` as an error pointer or NULL.

## Dependencies and integration points
It depends on mlx5 driver definitions and optional VXLAN kernel support. It is included by core lifecycle and tunnel offload code.

## Risks and edge cases
Disabled `CONFIG_VXLAN` builds return `-EOPNOTSUPP` and false lookups; callers must not treat VXLAN offload as mandatory. `mlx5_vxlan_max_udp_ports()` supplies a default when capability reports zero, so tests should verify this matches firmware expectations.

## Test signals
Build with `CONFIG_VXLAN` enabled and disabled. Runtime tests should verify max-port capability reporting, allowed/error-pointer behavior, and no-op stubs in disabled builds.

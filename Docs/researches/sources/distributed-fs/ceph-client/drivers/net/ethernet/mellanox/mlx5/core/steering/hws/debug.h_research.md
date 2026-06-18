# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/debug.h

## Purpose
`debug.h` defines the debug dump format version, stable resource type identifiers, pointer-to-ID helper, ICM-address conversion helper, and debugfs init/uninit declarations for HWS.

## Important APIs, Types, And Functions
`HWS_DEBUG_FORMAT_VERSION` is currently `1.0`. `enum mlx5hws_debug_res_type` assigns numeric IDs for context, context attrs/caps/send engine/send ring/STC, table, matcher, matcher attrs/templates/definers, and action STE tables. `HWS_PTR_TO_ID()` truncates a pointer to a 32-bit-ish printable identifier. `mlx5hws_debug_icm_to_idx()` converts an ICM byte address to an index by shifting by six and masking. `mlx5hws_debug_init_dump()` and `mlx5hws_debug_uninit_dump()` are implemented in `debug.c`.

## Control Flow And State
The header contains no mutable state, but its constants are part of the externally consumed debugfs record schema. Resource type IDs govern how each emitted line is interpreted.

## Dependencies And Integration Points
It depends on HWS context declarations and is included by debug implementation and internal users that need debug identifiers. User-space diagnostics must stay aligned with the version and enum values.

## Risks And Test Signals
Risks include changing enum values without a format-version bump, pointer truncation collisions in large systems, and ICM index assumptions tied to STE granularity. Test signals are debug dump parser tests and comparisons of dumped ICM indexes against firmware query data.

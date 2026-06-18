# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/port_tun.c

## Purpose
`port_tun.c` manages port-level tunnel entropy calculation settings for mlx5 tunnel offloads. It coordinates VXLAN/L3-tunnel rules that need entropy calculation enabled with NVGRE rules that may require entropy disabled, using refcounts and firmware PCMR register updates.

## Important APIs, types, and functions
Public functions are `mlx5_init_port_tun_entropy()`, `mlx5_tun_entropy_refcount_inc()`, and `mlx5_tun_entropy_refcount_dec()`. Internal helpers query PCMR state (`mlx5_query_port_tun_entropy()`), set global tunnel entropy calculation, set GRE-specific entropy calculation, and choose the correct control path in `mlx5_set_entropy()`.

## Control flow
Initialization records the device, initializes a mutex, queries support/current enablement, and defaults to enabled when the firmware lacks explicit support. Refcount increment accepts VXLAN/L3 tunnel entries only if entropy is currently enabled, increasing `num_enabling_entries`. For NVGRE, the first disabling entry tries to disable entropy, preferably through GRE-specific control when supported, and subsequent entries only bump the disabling count. Refcount decrement reverses those counts and re-enables entropy when the last NVGRE entry is removed.

## State and persistence behavior
State is kept in `struct mlx5_tun_entropy`: enabling and disabling entry counts, cached enabled flag, mutex, and device pointer. Hardware state is the PCMR port-check register. There is no disk persistence, but firmware register state may affect all tunnel offload users on the port.

## Dependencies and integration points
The file depends on mlx5 port check register access, `MLX5_REFORMAT_TYPE_*` constants, and mlx5 logging. It integrates with flow/reformat code that calls the refcount helpers when tunnel reformat rules are installed or removed.

## Risks and edge cases
The decrement path only treats VXLAN as enabling, while increment also accepts `L2_TO_L3_TUNNEL`; callers using L3 tunnel must ensure symmetry or this can under/over-count. Global entropy disable fails if enabling entries exist. External firmware or other software changing forced entropy state can trigger `-EOPNOTSUPP`. Missing refcount decrements can leave entropy disabled after NVGRE rules are removed.

## Test signals
Test initialization with and without PCMR support, VXLAN/L3 increment success while enabled, NVGRE first-rule disable and last-rule re-enable, mixed VXLAN plus NVGRE conflict, GRE-specific capability path, global force-capability path, and refcount symmetry under add/delete stress.

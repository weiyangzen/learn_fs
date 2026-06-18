# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/vport.h

Purpose: declares the small HWS vport GVMI cache API.

Important APIs: `mlx5hws_vport_init_vports()` initializes per-context vport cache state, `mlx5hws_vport_uninit_vports()` tears it down, and `mlx5hws_vport_get_gvmi()` returns a GVMI for a vport.

Control flow/state: callers are expected to initialize once during context setup, query as vport destinations are used, and uninitialize during context teardown. The actual state fields live in the context and are implemented in `vport.c`.

Dependencies/integration: requires `struct mlx5hws_context` and kernel integer types from the HWS internal include chain.

Risks: the header does not expose locking or lifetime requirements; misuse before init or after uninit can race the implementation's xarray.

Test signals: build coverage and context lifecycle tests that call init/get/uninit in expected order.

# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/post_meter.h

Purpose: Declares post-meter branching types, packet color register mapping, table getters, init, and cleanup APIs.

Important types and APIs: `packet_color_to_reg` maps packet color into metadata register C5. `enum mlx5e_post_meter_type` selects rate or MTU branching. APIs expose FTs and create/cleanup post-meter state when class-act support is enabled.

Control flow and state: Police/meter offload uses these tables to branch from ASO color or MTU comparison to true/false attrs.

Dependencies and integration: Depends on mlx5 flow table/counter/eswitch types and class-act config stubs.

Risks and tests: Stub behavior should be compiled for disabled class-act builds. Runtime tests should confirm branch tables returned by getters match the selected mode.

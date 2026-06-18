# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/hv_vhca.h

Purpose: Declares the Hyper-V vHCA object and agent API.

Important APIs and types: Defines agent types for control and stats with a 32-slot maximum, and the Hyper-V control block layout (`capabilities`, `control`, `command`, `command_ack`, `version`, `rings`). Exports create/destroy/init/cleanup, invalidate callback, agent create/destroy/write, and private-data access when Hyper-V PCI support is enabled; otherwise provides stubs.

State and dependencies: Includes mlx5 ethernet and Hyper-V helper headers. Opaque structs keep implementation state private while callbacks receive agent handles and control blocks.

Risks and test signals: Stub paths return NULL or zero, so consumers must handle absent Hyper-V support. ABI-sensitive control block fields and agent type bit positions need compatibility tests with host-side expectations.

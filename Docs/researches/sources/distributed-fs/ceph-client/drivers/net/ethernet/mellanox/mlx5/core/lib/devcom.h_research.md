# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/devcom.h

Purpose: Declares the devcom registry API used by mlx5 subsystems that coordinate across peer devices.

Important APIs and types: Defines match flags, 32-byte match-key union, match attributes, component IDs (`ESW_OFFLOADS`, `MPV`, `HCA_PORTS`, `SD_GROUP`, `SHARED_CLOCK`), and event handler signature. Exposes device/component registration, event send, component size, ready state, peer iteration macros for locked and RCU contexts, and component lock helpers.

State and dependencies: Opaque `mlx5_devcom_dev` and `mlx5_devcom_comp_dev` handles isolate users from global registry internals. Match attributes optionally include a `struct net *` when namespace matching is requested.

Risks and test signals: Consumers must bracket peer iteration with begin/end or an RCU section as appropriate, and must not change ready state without holding the component lock. Compile and integration tests should cover each component ID user and namespace-key matching.

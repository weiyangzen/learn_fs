# sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/net/mlx5_vnet.h

Purpose: mlx5 vDPA net-private declarations shared between the main vnet implementation and debugfs support.

Important APIs/types/functions: conversion macros `to_mlx5_vdpa_ndev()` and `to_mvdev()`, `struct mlx5_vdpa_net_resources`, IRQ pool structures, `struct mlx5_vdpa_net`, steering counter structures, `struct macvlan_node`, `key2vid()`, and debugfs helper prototypes. Inline no-op counter helpers are provided when steering debug is disabled.

Control flow: no executable control flow except `key2vid()` and compile-time selection of counter helper implementations.

State and persistence: defines all net-level state fields: TIS/TD/TIR/RQT identifiers, config, vq/callback arrays, `reslock`, flow table dentries, setup flags, current queue count, link notifier, CVQ work item, MAC/VLAN hash, IRQ pool, debugfs dentry, and UMEM sizing parameters.

Dependencies and integration: included by `mlx5_vnet.c` and `debug.c`; depends on core `mlx5_vdpa.h`.

Risks: the header centralizes state used across resource, steering, and debugfs code; mismatched cleanup of dentries or IRQ entries can leave stale pointers. Hash size and key packing must align with MAC/VLAN operations.

Test signals: compile with and without `CONFIG_MLX5_VDPA_STEERING_DEBUG`, debugfs operations using header structs, and MAC/VLAN lookup behavior for tagged/untagged keys.

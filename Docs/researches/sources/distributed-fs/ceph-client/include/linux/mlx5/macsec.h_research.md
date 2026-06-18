# `sources/distributed-fs/ceph-client/include/linux/mlx5/macsec.h`

## Purpose

`macsec.h` exposes the mlx5 MACsec-to-RoCE flow-steering bridge when `CONFIG_MLX5_MACSEC` is enabled. It lets MACsec events and RoCE GID updates install or remove MACsec-aware RoCE steering rules for transmit and receive security associations.

## Important APIs, Types, and Constants

- `struct mlx5_macsec_event_data` carries MACsec event context: MACsec flow-steering object pointer, MACsec netdev/private pointer, flow-steering ID, and direction flag.
- `mlx5_macsec_add_roce_rule()` installs RoCE MACsec rules for a MACsec device/address/GID index pair and records transmit and receive rules in caller-provided lists.
- `mlx5_macsec_del_roce_rule()` removes the rules for a GID index from the MACsec flow-steering context and rule lists.
- `mlx5_macsec_add_roce_sa_rules()` installs rules for a specific security-association flow-steering ID and direction.
- `mlx5_macsec_del_roce_sa_rules()` removes rules for a specific security-association flow-steering ID and direction.
- All declarations are compiled only under `CONFIG_MLX5_MACSEC`; there are no non-MACsec stubs in this header.

## Control Flow and Lifetimes

MACsec and RoCE integration starts from capability gating in `driver.h`, where `mlx5_is_macsec_roce_supported()` requires NIC-to-RDMA flow-table capabilities, MACsec device support, and `mdev->macsec_fs`. When a RoCE GID or MACsec SA appears, callers provide the MACsec device pointer, sockaddr, GID index, rule lists, and MACsec flow-steering context to add TX/RX rules. SA-specific add/delete functions update one direction based on `is_tx`. Deletion must remove rules from the same lists and flow-steering context before the GID, SA, MACsec device, or `mlx5_macsec_fs` object is destroyed.

## State and Persistence Behavior

The header exposes event context only. Persistent state is stored in `struct mlx5_macsec_fs` implementation objects and in caller-owned `tx_rules_list` and `rx_rules_list`. Added rules are hardware/software flow-steering handles that persist until corresponding delete functions run.

## Dependencies and Integration Points

The API depends on kernel socket address types, list heads, `struct mlx5_macsec_fs`, and MACsec configuration. Implementation references in this tree include `drivers/net/ethernet/mellanox/mlx5/core/lib/macsec_fs.c`, while RDMA integration calls are visible in `drivers/infiniband/hw/mlx5/macsec.c`. It integrates with flow-steering APIs from `fs.h`, device capability checks from `driver.h`, and MACsec notifier chains stored in `struct mlx5_core_dev` when MACsec is configured.

## Risks and Edge Cases

- No declarations are available without `CONFIG_MLX5_MACSEC`; callers must guard all use.
- Rule list ownership is external. Add/delete mismatches, wrong GID index, or wrong `is_tx` direction can leak rules or remove the wrong SA rules.
- The API uses `void *macdev`, so type safety is delegated to implementation and callers.
- MACsec RoCE depends on multiple capabilities and `mdev->macsec_fs`; bypassing the capability gate can fail late or program unsupported steering paths.
- Address family handling is hidden in implementation; callers should pass sockaddr values that match RoCE GID semantics.

## Test Signals

Validate builds with and without `CONFIG_MLX5_MACSEC`, MACsec RoCE capability gating, RoCE GID add/delete while MACsec is active, TX and RX SA add/delete, rule-list cleanup on error paths, MACsec device teardown before/after RoCE cleanup, and traffic tests verifying encrypted RoCE steering in both directions.

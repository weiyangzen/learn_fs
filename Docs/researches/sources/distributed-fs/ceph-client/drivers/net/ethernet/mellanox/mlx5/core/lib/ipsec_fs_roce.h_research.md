# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/ipsec_fs_roce.h

Purpose: Declares RoCE IPsec flow-steering lifecycle and table access APIs.

Important APIs and types: Forward-declares `struct mlx5_ipsec_fs`. Exports RX/TX create/destroy, RX flow-table getter by address family, init/cleanup, and MPV RoCE support check. Create calls require core device, namespace or policy/default destinations, family/level/prio arguments, and optional devcom pointer from init.

State and dependencies: The header includes devcom declarations because MPV alias flows need peer-device coordination. Implementation state remains opaque to consumers.

Risks and test signals: Callers must pass matching family to RX get/destroy and must call cleanup after RX/TX teardown. Tests should validate NULL `ipsec_roce` no-op behavior and MPV support checks before enabling RoCE IPsec in multiport mode.

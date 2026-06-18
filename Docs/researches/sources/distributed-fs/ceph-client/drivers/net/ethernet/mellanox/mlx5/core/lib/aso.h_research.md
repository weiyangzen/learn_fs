# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/aso.h

Purpose: Defines the wire-format WQE structures and exported helper API for mlx5 ASO operations.

Important APIs and types: Defines ASO WQEBB sizes, control flags, opcode modifier shift, MACsec DS count, ASO control/data segment structs, WQE structs with and without 64-byte data, logical/conditional/data-mask enums, and opcode modifiers for IPsec, flow meter, and MACsec. Exports create/destroy and WQE get/build/post/poll helpers.

State and dependencies: The header forward-declares `struct mlx5_aso`; callers operate on opaque ASO queues while filling WQE fields defined here. It depends on mlx5 QP/core definitions and firmware-compatible big-endian segment layout.

Risks and test signals: Layout and constants must remain ABI-compatible with firmware. Tests should verify WQE sizes/DS counts, opcode modifiers, read-enable semantics, and users that choose bytewise versus bitwise mask modes.

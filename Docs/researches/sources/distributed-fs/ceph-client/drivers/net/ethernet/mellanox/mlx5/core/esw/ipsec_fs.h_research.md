# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/ipsec_fs.h

Purpose: Declares eswitch-specific IPsec flow-steering hooks and provides disabled stubs when eswitch support is not built.

Important APIs/types/functions: Declares RX/TX attribute setters, RX status pass destination getter, RX modify-header setup, RX mapped ID removal/search, uplink destination restore, and RX rule match augmentation. Stubs return `-EINVAL` for operations that require hardware/eswitch state and no-op for void helpers.

Control flow and integration: Generic mlx5e IPsec code can call these hooks to specialize flow creation for FDB/eswitch operation while building without eswitch support. `ipsec_fs.c` provides the actual implementation under `CONFIG_MLX5_ESWITCH`.

State and persistence: The header stores no state. It abstracts SA entry state, IPsec object ID maps, and flow action mutation owned by implementation code.

Risks and test signals: Risks include generic callers not handling `-EINVAL` from stubs, stale prototypes as mlx5e IPsec structures evolve, and missing include coverage for forward declarations. Test signals include builds with and without eswitch, IPsec offload setup in switchdev mode, and clean fallback when eswitch IPsec FS is unavailable.

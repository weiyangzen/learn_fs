# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/macsec_fs.h

## Purpose
`macsec_fs.h` declares the public interface and metadata encoding contract for mlx5 MACsec flow steering. It is compiled only when `CONFIG_MLX5_MACSEC` is enabled and lets MACsec and RoCE code create/delete SA rules, query counters, and translate between SCI and mlx5 steering IDs.

## Important APIs, types, and functions
The header defines RX metadata helpers `MLX5_MACSEC_METADATA_MARKER()` and `MLX5_MACSEC_RX_METADAT_HANDLE()`, TX WQE metadata helpers `mlx5_macsec_fs_set_tx_fs_id()` and `MLX5_MACSEC_TX_METADATA()`, and the `MLX5_MACSEC_NUM_OF_SUPPORTED_INTERFACES` limit. Important types are opaque `struct mlx5_macsec_fs`, opaque `union mlx5_macsec_rule`, `struct mlx5_macsec_rule_attrs`, `struct mlx5_macsec_stats`, and `enum mlx5_macsec_action`. Public functions include initialization, cleanup, rule add/delete, stats fill/get, and SCI-to-fs-id lookup.

## Control flow
The header has no runtime control flow. It establishes the call contract used by the mlx5 MACsec accelerator: callers initialize a steering object, pass MACsec context plus `mlx5_macsec_rule_attrs` to add encrypt or decrypt rules, retain the returned rule handle, and later delete it with the same action and SA fs-id context.

## State and persistence behavior
No state is stored in the header. The macros define in-packet or WQE metadata layout: RX uses bits 31-30 as a MACsec marker and bits 15-0 as an SA handle; TX uses the mlx5 Ethernet WQE flow-table metadata field with a MACsec bit and a small fs-id. These encodings are persistent hardware/software ABI within the driver.

## Dependencies and integration points
The header depends on mlx5 driver types, Linux MACsec `sci_t`, and MACsec configuration guards. It is included by `macsec_fs.c` and higher-level MACsec/RoCE offload code that needs opaque rule handles and metadata helpers.

## Risks and edge cases
Metadata macro changes must remain consistent with flow rules in `macsec_fs.c` and TX WQE producers. The RX max define is misspelled as `MLX5_MACEC_RX_FS_ID_MAX`, so renaming would require broad caller checks. The TX fs-id field supports only 16 interfaces, and callers must not assume arbitrary SA counts fit into TX metadata.

## Test signals
Build coverage under `CONFIG_MLX5_MACSEC=y/m` and disabled configurations is essential. Runtime signals come from successful MACsec TX/RX offload, correct metadata marker recognition on RX, correct SCI lookup for TX RoCE rules, and stats retrieval through the declared APIs.

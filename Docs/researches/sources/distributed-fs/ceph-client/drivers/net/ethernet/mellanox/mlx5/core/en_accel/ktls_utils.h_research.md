# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls_utils.h

Purpose: shared declarations, crypto-info union, hardware WQE structures, size macros, and fetch macros for mlx5e kTLS TX/RX offload.

Important APIs, types, and functions: declares kTLS add/delete/resync entry points for TX and RX. `union mlx5e_crypto_info` provides one storage object that can be interpreted as generic TLS crypto or AES-GCM-128/256 TLS 1.2 structs. WQE structures are `mlx5e_set_tls_static_params_wqe`, `mlx5e_set_tls_progress_params_wqe`, and `mlx5e_get_tls_progress_params_wqe`. Size macros compute WQEBB consumption for stop-room calculations. Fetch macros retrieve typed WQEs from cyclic work queues, including DUMP WQEs declared in TX code. Builder prototypes are exported from `ktls_txrx.c`.

Control flow: this header is used by TX/RX add paths for crypto storage, by SQ posting paths for WQE sizing and typed access, and by completion/resync paths for shared progress-state constants.

State and persistence: no independent state. The struct definitions describe in-ring WQE state that persists until hardware completion. The crypto union is embedded in private TLS offload contexts.

Dependencies and integration points: depends on Linux TLS headers and mlx5e queue helpers from `en.h`. It connects TLS offload control-plane functions with low-level WQE builders.

Risks: WQE layout drift must match firmware IFC definitions and `MLX5_SEND_WQE_BB` sizing. The DUMP fetch macro references `struct mlx5e_dump_wqe`, which is defined in `ktls_tx.c`; include ordering must only use it where that type is visible. Cipher support is intentionally narrow.

Test signals: compile all TLS-enabled objects, verify WQEBB sizes against expected hardware descriptors, and run TX/RX TLS offload tests across AES-GCM-128 and 256.

# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls_txrx.c

Purpose: shared kTLS TX/RX WQE construction for static TLS crypto parameters and progress parameters. It converts Linux TLS crypto structs into mlx5 hardware context fields.

Important APIs, types, and functions: `mlx5e_ktls_build_static_params()` fills a UMR WQE using `MLX5_OPC_MOD_TLS_TIS_STATIC_PARAMS` for TX or `MLX5_OPC_MOD_TLS_TIR_STATIC_PARAMS` for RX. `mlx5e_ktls_build_progress_params()` fills a SET_PSV WQE using TIS/TIR progress opmods. Internal `fill_static_params()` extracts salt and record sequence from `union mlx5e_crypto_info`, sets TLS 1.2, GCM IV, initial record number, DEK index, and resync TCP sequence. `fill_progress_params()` initializes next-record TCP sequence, tracker state, and auth state.

Control flow: callers allocate/fetch a WQE from an SQ, then pass queue producer counter, SQ number, key id, TIS/TIR number, fence mode, and direction. Static params choose AES-GCM-128 or AES-GCM-256 layouts, warn on unsupported ciphers, and encode inline context bytes. Progress params are shorter and set hardware record tracking to start with auth not yet offloaded.

State and persistence: the file does not own long-lived state. It writes WQE memory supplied by callers. Persistent effects occur only after callers ring the SQ and hardware consumes the WQEs.

Dependencies and integration points: depends on `ktls_utils.h` WQE layouts, Linux TLS crypto structs, mlx5 IFC field macros, and TLS offload direction enum. Used by TX (`ktls_tx.c`) and RX kTLS code to post the same hardware context classes.

Risks: wrong opmod/direction pairing would program a TIS as a TIR or vice versa. Record sequence and salt copying assumes TLS 1.2 AES-GCM struct layouts. Unsupported cipher handling is only a warning and early return from fill helper, so callers must already validate ciphers. Fence selection affects ordering with data and DUMP WQEs.

Test signals: inspect generated WQEs for AES-GCM-128/256, TX and RX directions, fenced and unfenced posts, nonzero resync TCP sequence, and correct DEK/TIS/TIR fields. Negative tests should reject unsupported cipher types before these builders are reached.

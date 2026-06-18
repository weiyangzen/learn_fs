# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls_txrx.h

Purpose: public kTLS datapath interface between mlx5e TX/RX core and the kTLS acceleration implementation, with compile-time no-op fallbacks when `CONFIG_MLX5_EN_TLS` is disabled.

Important APIs, types, and functions: `struct mlx5e_accel_tx_tls_state` carries the selected TIS number into normal TX WQE construction. Declarations cover TX stop-room sizing, TX SKB handling, RX SKB handling, kTLS ICO SQ completions, GET_PSV completions, TX resync DUMP completions, RX resync cancellation, and RX resync-list processing. Inline helpers include `mlx5e_ktls_tx_try_handle_resync_dump_comp()`, `mlx5e_ktls_rx_pending_resync_list()`, and `mlx5e_ktls_handle_tx_wqe()`.

Control flow: TX code first calls `mlx5e_ktls_handle_tx_skb()` to validate/update TLS state and fill `tls_tisn`; later WQE build code calls `mlx5e_ktls_handle_tx_wqe()` to write that TIS into the control segment. Completion code can call the try-handle helper, which detects DUMP completions using `wi->resync_dump_frag_page`. RX polling can detect pending async resync work through a channel state bit and budget.

State and persistence: the header owns no storage beyond the transient TX accel state. It exposes state-bit checks and WQE-info flags owned by queue structures.

Dependencies and integration points: includes net TLS, mlx5e `en.h`, and TX/RX queue declarations. It is included by mlx5e datapath files that must compile regardless of TLS acceleration support.

Risks: fallback stubs must preserve caller expectations when TLS is disabled: no stop room, no RX processing, no DUMP completions. The inline TX WQE helper assumes the state was initialized by the kTLS SKB hook before use.

Test signals: build with and without `CONFIG_MLX5_EN_TLS`, verify no unresolved symbols in disabled builds, and validate that enabled builds set `cseg->tis_tir_num` only for TLS-offloaded packets.

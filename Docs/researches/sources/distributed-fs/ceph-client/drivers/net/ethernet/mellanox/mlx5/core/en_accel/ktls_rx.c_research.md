# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ktls_rx.c

Purpose: implements kTLS RX offload contexts, hardware TIR/key setup, TCP acceleration rules, RX CQE handling, and asynchronous resync with GET_PSV/progress WQEs.

Important APIs/types/functions: `mlx5e_ktls_add_rx`, `mlx5e_ktls_del_rx`, `mlx5e_ktls_handle_rx_skb`, `mlx5e_ktls_handle_ctx_completion`, `mlx5e_ktls_handle_get_psv_completion`, `mlx5e_ktls_rx_resync`, `mlx5e_ktls_rx_resync_async_request_cancel`, `mlx5e_ktls_rx_handle_resync_list`, and response-list create/destroy. Key local structs are `mlx5e_ktls_offload_context_rx`, `mlx5e_ktls_rx_resync_ctx`, `mlx5e_ktls_rx_resync_buf`, and `accel_rule`.

Control flow and state: add allocates private RX context, copies crypto info, creates DEK, selects socket RX queue, stores context in TLS driver state, creates TLS TIR, initializes completion/work/refcount/resync state, points TLS async resync at driver context, posts static and progress WQEs, and increments stats. Context completion queues TCP flow rule installation to RX workqueue. RX CQE handling marks decrypted packets or starts resync on RESYNC CQEs. Resync requests lookup socket, queue GET_PSV work, compare hardware tracker/auth state, end or cancel TLS async request, and later post static params with software record sequence via NAPI list handling. Delete marks deleting, clears TLS ctx, synchronizes NAPI, cancels work, deletes rule/TIR/key, and refcounts delayed free if GET_PSV is in flight.

Dependencies and integration: depends on TLS core async resync API, mlx5 ICOSQ WQE builders from `ktls_utils.h`, TCP accel FS, RX resource TLS TIRs, socket lookup, NAPI async ICOSQ, DMA mapping, and per-channel resync response lists.

Risks and test signals: refcounting protects in-flight GET_PSV and delete races; list handling must requeue on ICOSQ full; socket lookup and TCP state checks must avoid stale references; progress state validation gates resync success. Test RX add/delete while WQEs complete, flow rule add work cancellation, decrypted/error/resync CQEs, IPv4/IPv6 socket lookup, ICOSQ full retry, GET_PSV DMA failure, and async resync cancel/end paths.

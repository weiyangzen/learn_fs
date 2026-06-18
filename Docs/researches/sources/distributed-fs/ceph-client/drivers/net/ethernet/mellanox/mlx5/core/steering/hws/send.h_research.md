# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/send.h

Purpose: declares the HWS send-engine wire formats, queue/ring data structures, posting attributes, dependent-WQE records, and public send queue APIs.

Important APIs/types: defines `MAX_WQES_PER_RULE`, WQE opcode/opmod/GTA enums, `mlx5hws_wqe_ctrl_seg`, `mlx5hws_wqe_gta_ctrl_seg`, STE/argument GTA data segments, `mlx5hws_send_ring_cq`, `mlx5hws_send_ring_sq`, `mlx5hws_send_engine`, `mlx5hws_send_engine_post_attr`, and `mlx5hws_send_ste_attr`. Inline helpers expose empty/full/error checks, used-entry accounting, and generated completions.

Control flow/state: the header describes the contract used by `send.c`: callers build posts with `post_start`, one or more `post_req_wqe` buffers, then `post_end`; STE callers fill `mlx5hws_send_ste_attr` so the implementation can target RTC0/RTC1 and retry RTCs. `wr_priv` links posted WQEs back to rules and user data for CQ polling.

Dependencies/integration: types are consumed by HWS rule, action, and queue-management code through `internal.h`. The WQE fields are big-endian hardware layouts, so consumers must use conversion helpers before posting.

Risks: structure layout mirrors hardware PRM expectations; accidental padding/field changes or inconsistent WQE length constants can corrupt device commands. `mlx5hws_send_engine_gen_comp()` is a ring without overflow checks, relying on queue accounting.

Test signals: compile-time layout coverage, posting/polling integration tests, queue accounting around generated completions, and dual-RTC rule cases validate the header contract.

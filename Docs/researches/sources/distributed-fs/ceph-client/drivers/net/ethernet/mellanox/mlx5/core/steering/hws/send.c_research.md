# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/send.c

Purpose: implements the HWS send engine that posts GTA table-access WQEs to mlx5 SQ/CQ rings, drains dependent WQEs, polls completions, advances rule status, and provides a firmware command fallback for WQE generation.

Important APIs/functions: `mlx5hws_send_queues_open/close`, `mlx5hws_send_queue_poll`, `mlx5hws_send_queue_action`, `mlx5hws_send_ste`, `mlx5hws_send_stes_fw`, `mlx5hws_send_engine_post_start/req_wqe/end`, `mlx5hws_send_add_new_dep_wqe`, `mlx5hws_send_all_dep_wqe`, and `mlx5hws_send_engine_flush_queue`. Static helpers allocate/open SQ/CQ objects, ring doorbells, retry collision RTC writes, decode CQEs, and update rule resize state.

Control flow: callers reserve WQEBBs through the post controller, fill GTA control/data, finalize a WQE control segment, and optionally ring the UAR doorbell. `mlx5hws_send_ste()` emits RTC1 then RTC0, preserving notify/fence semantics so the last hardware WQE signals completion. CQ polling walks unsignaled WQEs up to the completed counter, synthesizes success for earlier WQEs, parses the signaled CQE, updates `wr_priv`, and reports either into the caller result array or the internal completion list.

State/persistence: queue state lives in `mlx5hws_send_engine`, `send_sq`, `send_cq`, `wr_priv`, and `completed`. Rule state is mutated through `pending_wqes`, `status`, `rtc_0/rtc_1`, resize info, and action STE cleanup. SQ/CQ objects, work queues, doorbell records, and DMA-backed buffers are kernel/device resources created at queue-open time and destroyed on close. No disk persistence is present.

Dependencies/integration: depends on mlx5 core command and work-queue APIs, `internal.h`, clock timestamp selection, rule helpers, context capability flags, and HWS command `mlx5hws_cmd_generate_wqe`. It is integrated by the HWS rule path and context queue lifecycle; BWC queues add extra locks and queue slots.

Risks: ring arithmetic assumes power-of-two queue sizes and enough `MAX_WQES_PER_RULE` slots; completion handling must keep `pending_wqes`, `used_id`, and retry IDs consistent or rules leak/complete incorrectly. Doorbell ordering relies on DMA/write barriers. Firmware fallback cannot hardware-fence, so it drains synchronously before fenced writes. Error CQE logging intentionally prints only once per engine, which can hide later distinct failures.

Test signals: exercise create/update/delete rule flows with one and two RTCs, retry RTC path, dependent WQE drain, queue full/empty accounting, CQ error decoding, resize move failure/success, firmware WQE fallback, and teardown during device internal error.

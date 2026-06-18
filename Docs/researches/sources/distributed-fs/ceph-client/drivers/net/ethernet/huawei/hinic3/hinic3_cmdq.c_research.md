# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_cmdq.c

## Purpose
Implements the hinic3 synchronous command-queue engine. It allocates DMA command buffers, creates command-queue WQs, programs firmware command-queue contexts, submits long-command WQEs through doorbells, handles CEQ completions, waits for synchronous responses, handles timeout/force-stop cases, and frees or reinitializes command queues.

## Important APIs And Functions
Public APIs are `hinic3_cmdqs_init()`, `hinic3_cmdqs_free()`, `hinic3_alloc_cmd_buf()`, `hinic3_free_cmd_buf()`, `hinic3_cmd_buf_pair_init()`, `hinic3_cmd_buf_pair_uninit()`, `hinic3_cmdq_direct_resp()`, `hinic3_cmdq_detail_resp()`, `hinic3_cmdq_ceq_handler()`, `hinic3_cmdq_flush_sync_cmd()`, `hinic3_reinit_cmdq_ctxts()`, and `hinic3_cmdq_idle()`. Key internals include `cmdq_sync_cmd_exec()`, `wait_cmdq_sync_cmd_completion()`, `cmdq_wqe_fill()`, `cmdq_prepare_wqe_ctrl()`, `cmdq_set_db()`, `cmdq_init_queue_ctxt()`, and `create_cmdq_wq()`.

## Control Flow And State
Initialization allocates `struct hinic3_cmdqs`, creates a DMA pool for 2048-byte command buffers, creates WQs of depth 4096 with 64-byte WQEBBs, allocates a doorbell address, allocates per-WQE `cmd_infos`, and sends command-queue contexts to management firmware. Submission validates buffer size, waits for `HINIC3_CMDQ_ENABLE`, reserves a WQE under `cmdq_lock`, increments input/output buffer refcounts, fills command metadata, writes the WQE header last, rings the doorbell, and waits up to 5000 ms for completion. CEQ handling walks used WQEs, checks busy bits, copies errcode/direct response, completes waiters, clears refcounted buffers, and advances CI. Timeout code distinguishes real timeout, fake timeout after late completion, and force-stop during flush.

## Dependencies And Integration Points
It depends on hinic3 WQ helpers, EQ completion dispatch, hardware device/interface helpers, management mailbox context commands, DMA pools, completions, spinlocks, and bitfield helpers. Other hinic3 modules use direct/detail response APIs for firmware commands.

## Risks And Test Signals
Risks include completion races, refcount leaks, doorbell index mistakes, WQE header ordering, endian conversion, timeout cleanup while firmware still owns buffers, and 0-level versus 1-level CLA handling. Tests should cover command success, SGE response, timeout injection, reset/reinit, device removal with in-flight commands, CEQ storms, DMA pool exhaustion, and lockdep/KASAN around flush paths.

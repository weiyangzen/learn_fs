# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_cmd.c

Purpose: Implements mailbox command submission for HNS RoCE hardware, supporting both polling and event-driven completion modes plus DMA mailbox allocation helpers.

Important APIs/types/functions: `hns_roce_cmd_mbox()` is the main command entry point. `hns_roce_cmd_event()` handles asynchronous command completion events by token. `hns_roce_cmd_init()`/`cleanup()` manage the DMA pool. `hns_roce_cmd_use_events()` allocates command contexts and switches to event mode; `hns_roce_cmd_use_polling()` frees them. Mailbox helpers allocate/free command buffers and create/destroy hardware contexts.

Control flow: Before posting, `chk_mbox_avail()` may short-circuit with `-EBUSY` or success. Poll mode serializes on `poll_sem`, posts via `hw->post_mbox`, waits using `hw->poll_mbox_done`, and uses token `0xffff`. Event mode serializes capacity through `event_sem`, takes a context from a circular free list, increments its token generation, posts with event enable, waits up to `HNS_ROCE_CMD_TIMEOUT_MSECS`, and reads the event result.

State and persistence: `hr_dev->cmd` owns the DMA pool, semaphores, event contexts, free-head index, and mode flag. DFX counters persist posted, polled, and event completions. Mailbox buffers are coherent DMA blocks from a 4 KiB pool.

Dependencies and integration: Depends on hardware callbacks `post_mbox`, `poll_mbox_done`, and optional `chk_mbox_avail`. CQ/QP/MR/HEM creation paths use `hns_roce_create_hw_ctx()` and `hns_roce_destroy_hw_ctx()`.

Risks: Event context free-list handling does not put contexts back onto a conventional free list; correctness relies on bounded semaphore and token modulo indexing. Timeout leaves the hardware command status uncertain. Test signals include command storm in event mode, token mismatch AEQs, mailbox timeout/failure injection, polling-to-event transition during init, and DMA pool allocation failures.

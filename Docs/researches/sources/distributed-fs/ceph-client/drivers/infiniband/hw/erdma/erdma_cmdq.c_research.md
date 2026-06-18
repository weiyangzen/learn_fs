# sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_cmdq.c

Implements the ERDMA firmware command queue: SQ/CQ/EQ allocation, command submission, doorbells, completion polling/interrupt handling, wait context management, timeouts, and response extraction.

Important functions include `erdma_cmdq_init`, `erdma_finish_cmdq_init`, `erdma_cmdq_destroy`, `erdma_cmdq_build_reqhdr`, `erdma_post_cmd_wait`, `get_comp_wait`, `push_cmdq_sqe`, `kick_cmdq_db`, `erdma_cmdq_completion_handler`, `erdma_polling_cmd_completions`, and wait/poll completion helpers.

Initialization allocates the wait pool/bitmap, coherent SQ/CQ buffers, DMA-pool doorbell records, a command EQ, writes queue addresses/depths to BAR registers, and marks the queue OK. Submission takes a semaphore credit, allocates a context cookie, writes the SQE header with opcode, WQEBB count, WQE index, and cookie, rings the SQ doorbell, then waits by interrupt completion or polling. Completion handling drains EQEs, polls CQEs, completes waiters, rearms the CQ, and notifies the EQ.

Persistent state includes DMA queue buffers, producer/consumer indices, DB records, wait bitmap/pool, credits, command serial number, and state bits. A timeout clears `ERDMA_CMDQ_STATE_OK_BIT`, causing later commands to fail. Dependencies include coherent DMA, DMA pools, completions, semaphores, BAR registers, and EQ helpers.

Risks include command queue poisoning on timeout, non-sleepable busy-wait paths, cookie/SQE mismatch, response endian/layout mistakes, and unwind leaks. Test signals include firmware queries during probe, concurrent command submissions, forced completion status errors, timeout behavior, interrupt and polling paths, and unload leak checks.

## sources/distributed-fs/ceph-client/drivers/dma/dmatest.c

Purpose: Kernel DMAengine self-test module that exercises DMA_MEMCPY, DMA_MEMSET, DMA_XOR, and DMA_PQ capabilities across requested channels with configurable module parameters.

Important APIs/types/functions: `struct dmatest_params`, `struct dmatest_info`, `struct dmatest_thread`, `struct dmatest_chan`, module parameters `run`, `channel`, `device`, `iterations`, `timeout`, `polled`, `noverify`, and test helpers `dmatest_func()`, `dmatest_add_channel()`, `dmatest_run_set()`, `dmatest_chan_set()`. It uses DMAengine entry points such as `dma_request_channel()`, `device_prep_dma_memcpy()`, `device_prep_dma_memset()`, `device_prep_dma_xor()`, `device_prep_dma_pq()`, `dma_async_issue_pending()`, `dma_sync_wait()`, and `dmaengine_terminate_sync()`.

Control flow: module parameters are copied into `test_info.params`, channels are requested by capability, and per-operation kernel threads are created in pending state. Setting `run=1` starts pending threads; each thread allocates source/destination test buffers, maps them with the DMA API, prepares a transfer, waits by callback or polling, unmaps, verifies patterns, and loops until stopped or `iterations` is reached. `wait` blocks userspace until finite tests complete.

State and persistence: all runtime state is in memory under `test_info` plus per-thread buffers and DMA descriptors. Channel/thread lists are protected by `test_info.lock`; per-transfer completion uses wait queues and a callback flag. No persistent storage is used.

Dependencies and integration: integrates with the DMAengine framework, kernel module parameter infrastructure, kthreads, freezer support, DMA mapping, wait queues, and logging. It is a consumer used to validate provider drivers such as the DW drivers in this subset.

Risks and test signals: timeout paths warn about possible memory corruption if a DMA provider lacks proper terminate support. Useful signals are kernel log summaries, data mismatch warnings, timeout/error result lines, and dmatest success counts under interrupt and polling modes, random and fixed offsets, and all advertised capabilities.

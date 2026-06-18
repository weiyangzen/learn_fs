# sources/distributed-fs/ceph-client/drivers/dma/bcm-sba-raid.c

Purpose: Broadcom SBA RAID DMAengine provider. It exposes one DMA channel backed by a Broadcom mailbox/ring-manager channel and offloads interrupt, memcpy, XOR, and RAID6 PQ operations by emitting `brcm_sba_command` sequences instead of programming local registers directly.

Important APIs/types/functions: `struct sba_device` owns DT-derived hardware limits, mailbox client/channel, DMA device/channel, preallocated coherent response/command pools, request lists, and debugfs. `struct sba_request` wraps a `dma_async_tx_descriptor`, a `brcm_message`, command array, and chained-request bookkeeping. Key callbacks are `sba_prep_dma_interrupt`, `sba_prep_dma_memcpy`, `sba_prep_dma_xor`, `sba_prep_dma_pq`, `sba_tx_submit`, `sba_issue_pending`, `sba_tx_status`, and `sba_device_terminate_all`.

Control flow: probe identifies `brcm,iproc-sba` versus `brcm,iproc-sba-v2`, derives buffer/PQ command limits, requests mailbox channel 0, resolves the mailbox device, preallocates 8192 request slots plus coherent command/response pools, registers debugfs stats, and registers a DMA device. Prep paths split large operations at `hw_buf_size` boundaries and chain requests through `first`, `next`, and `next_pending_count`. Submit assigns a cookie and moves all chain members to pending. Issue-pending sends up to eight mailbox messages per pass, respecting `SBA_REQUEST_FENCE`. Mailbox receive completes the first descriptor only after all chained messages have returned, invokes callbacks, unmaps, frees the chain, and drains more pending work.

State and persistence: Runtime state is in protected request lists: free, allocated, pending, active, aborted. It also stores `reqs_fence` to serialize fenced work. There is no persistent disk state; device state is reconstructed on probe. Coherent pools persist for the device lifetime.

Dependencies/integration: Linux DMAengine/async_tx, RAID6 GF tables, Broadcom mailbox message ABI, OF platform data, coherent DMA mapping, and debugfs. The DMA device is anchored to the mailbox device because memory access is performed by the ring-manager/SBA path.

Risks: mailbox send errors leave the request pending; aborted active requests rely on eventual receive callbacks for cleanup. PQ slow-path chaining and `DMA_PREP_CONTINUE` ordering are delicate. Request exhaustion depends on `mbox_client_peek_data()` progressing completions. Coherent pool sizing scales with fixed `SBA_MAX_REQ_PER_MBOX_CHANNEL`.

Test signals: boot/probe logs, DMAengine capability registration, debugfs `stats` counts returning to free after work, async_tx memcpy/xor/pq validation, RAID6 parity checks, fence ordering tests, terminate-all while active, mailbox error injection, and module remove with no leaked requests or coherent mappings.

# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_protocol_ops.c

Purpose: implements the Intel IOSM IPC protocol operations that manipulate AP/CP shared-memory message rings and pipe transfer descriptor rings. It is the operational companion to `iosm_ipc_protocol_ops.h`, translating higher-level pipe, sleep, and feature requests into shared-memory messages and moving SKBs through UL/DL TD rings.

Important APIs and functions: `ipc_protocol_msg_prep()` dispatches message preparation for sleep, pipe open/close, and feature-set requests. `ipc_protocol_msg_hp_update()` advances the AP message head and rings the HPDA doorbell through `ipc_pm_signal_hpda_doorbell()`. `ipc_protocol_msg_process()` consumes CP-completed message entries, updates `struct ipc_rsp`, and completes waiters. `ipc_protocol_ul_td_send()` enqueues mapped uplink SKBs into a pipe TD ring, while `ipc_protocol_ul_td_process()` reclaims completed UL buffers. `ipc_protocol_dl_td_prepare()` allocates DMA-capable SKBs for modem downlink, and `ipc_protocol_dl_td_process()` validates completion status, mapping, and length before returning an SKB to the caller.

Control flow and state: pipe open allocates `pipe->skbr_start` and coherent `pipe->tdr_start`, resets pipe counters, writes `head_array[pipe_nr]`, and publishes an `IPC_MEM_MSG_OPEN_PIPE`. Message completions are tracked by `old_msg_tail` and `rsp_ring[]`. Data rings keep AP head in shared memory and keep local `old_head`, `old_tail`, and `nr_of_queued_entries` in `struct ipc_pipe`.

Dependencies and integration points: depends on IOSM protocol state, PCIe DMA helpers (`ipc_pcie_alloc_skb()`, `ipc_pcie_kfree_skb()`), IPC PM doorbells, little-endian shared-memory fields, and SKB DMA metadata in `IPC_CB(skb)`.

Risks and test signals: ring-full handling, off-by-one free-space math, DMA mapping mismatch, invalid CP length/status, and cleanup while descriptors are outstanding are the main risks. Useful tests are pipe open/close stress, UL queue saturation, DL abort/overflow completions, message response timeout paths, and suspend/resume doorbell behavior.

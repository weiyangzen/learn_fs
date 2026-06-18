# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/ccm_mbox.c

## Purpose
This file implements the Netronome NFP control-channel-message transport over the device mailbox. Callers provide a CCM packet in an skb, and this layer serializes one or more queued packets into mailbox TLVs, runs the mailbox reconfiguration command, copies replies back into the original skb for synchronous callers, and wakes waiters. It is the shared transport used by higher-level features such as kTLS crypto control messages.

## Important APIs, types, and functions
- `struct nfp_ccm_mbox_cmsg_cb` overlays `skb->cb` and tracks per-message state, error, maximum request/reply size, expected reply length, and whether the message is posted/asynchronous.
- `nfp_ccm_mbox_msg_alloc()`, `nfp_ccm_mbox_fits()`, `nfp_ccm_mbox_communicate()`, `__nfp_ccm_mbox_communicate()`, and `nfp_ccm_mbox_post()` are the external send/allocation surface.
- `nfp_ccm_mbox_copy_in()` writes request TLVs plus optional reservation TLVs into the BAR mailbox. `nfp_ccm_mbox_copy_out()` parses reply TLVs, validates tag/type/length, and updates skb contents or posted-message state.
- `nfp_ccm_mbox_run_queue_unlock()` owns a batch, copies up to `NFP_CCM_MBOX_BATCH_LIMIT` messages while respecting mailbox space, executes `nfp_net_mbox_reconfig()`, and completes the batch.
- `nfp_ccm_mbox_alloc()`, `nfp_ccm_mbox_clean()`, and `nfp_ccm_mbox_free()` initialize, drain, and destroy the queue/workqueue backing the transport.

## Control flow
The synchronous path prepares the skb, assigns CCM header version/type/tag under `nn->mbox_cmsg.queue.lock`, and queues it. If the skb is not first, the caller sleeps until either its message is done or it becomes the next runner. The first/next runner builds a batch, marks subsequent skbs busy, drops the queue lock, locks the control BAR, writes TLVs, triggers `NFP_NET_CFG_MBOX_CMD_TLV_CMSG`, reads replies, completes/dequeues all batched skbs, marks the next queued skb runnable, unlocks the BAR, and wakes all waiters. The asynchronous `nfp_ccm_mbox_post()` path marks the skb posted, tries to start the mailbox transaction immediately with `nn_ctrl_bar_trylock()`, and uses workqueue jobs to wait for posted completion or to run a posted next runner.

## State and persistence
State is volatile driver state: the skb queue, per-skb control buffer state, monotonic mailbox tag, wait queue, and workqueue. No persistent on-disk state exists. Ordering is enforced with `smp_wmb()` before marking messages done and `smp_rmb()` in waiters before reading copied reply data or errors. Posted messages are consumed internally; synchronous messages are returned to callers unless an error forces skb free.

## Dependencies and integration points
The file depends on NFP mailbox BAR helpers (`nn_readl`, `nn_writel`, `nn_ctrl_bar_lock`, `nfp_net_mbox_reconfig*`), CCM header helpers from `ccm.h`, skb queue primitives, workqueues, and wait queues. Feature drivers rely on this to send firmware CCM operations, especially `crypto/tls.c`.

## Risks
Risks center on concurrency and firmware ABI validation. A missed state transition can strand waiters; incorrect memory barriers can expose stale skb data; malformed firmware TLVs are guarded but cause all remaining batched requests to complete with errors. Queue length is capped for non-critical messages, but critical callers can bypass the cap. Posted messages have no caller-visible completion beyond warnings.

## Test signals
Useful signals include forced mailbox-full and reply-too-large paths, unsupported CCM type validation, timeout behavior for queued and busy skbs, batching boundaries at 64 messages and mailbox-size limits, posted-message workqueue paths, and kTLS add/delete/update operations that exercise synchronous, critical, and posted CCM sends.

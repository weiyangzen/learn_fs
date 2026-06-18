<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/ccm.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/ccm.c

## Purpose
This file implements the common control-message request/reply transport used by NFP apps such as BPF. It allocates unique message tags, sends control skbs, waits for matching firmware replies, validates reply type/size, queues received replies, and handles tag cleanup on success, timeout, and interruption.

## Important APIs, Types, And Functions
- Tag management: `nfp_ccm_alloc_tag()`, `nfp_ccm_free_tag()`, and `nfp_ccm_all_tags_busy()` maintain a bounded in-flight tag window.
- Reply matching: `__nfp_ccm_reply()`, `nfp_ccm_reply()`, and `nfp_ccm_reply_drop_tag()` search the reply queue for a matching tag and free tag state.
- Wait path: `nfp_ccm_wait_reply()` spins briefly, then waits up to five seconds on `ccm->wq`, and finally drops the tag if no reply is found.
- Public transport: `nfp_ccm_communicate()` fills `struct nfp_ccm_hdr`, transmits via `__nfp_app_ctrl_tx()`, waits for reply, and validates reply type and optional fixed size.
- Receive/lifecycle: `nfp_ccm_rx()` queues valid replies and wakes waiters; `nfp_ccm_init()` and `nfp_ccm_clean()` initialize/check state.

## Control Flow
Callers pass a prepared skb to `nfp_ccm_communicate()`. Under the app control lock, CCM allocates a tag, writes ABI version/type/tag into the message header, transmits on the app control channel, and unlocks. It then polls briefly for low-latency replies before sleeping on the waitqueue. Receive-side code validates minimum header length, checks the tag is currently allocated, queues the skb on `ccm->replies`, and wakes all waiters. The waiter removes the matching skb, validates it is the reply type for the request and optionally the exact size, then returns ownership to the caller.

## State And Persistence
State is volatile in `struct nfp_ccm`: tag bitmap, next/last tag cursors, reply skb queue, waitqueue, and app pointer. No disk or hardware state is persisted here beyond messages transmitted to firmware. Tags are deliberately not reused too quickly after timeouts by limiting the in-flight window to `U16_MAX / 4`.

## Dependencies And Integration Points
The file depends on Linux bitops, skb queues, waitqueues, udelay/jiffies behavior, NFP app control locking/transmit functions, and NFP netdev warning logging. BPF map operations and other app protocols use it through `nfp_ccm_communicate()` and deliver replies through app control receive hooks.

## Risks And Edge Cases
- Late firmware replies after timeout are dropped because their tag has been freed; a future request could otherwise match stale replies if tag reuse were too aggressive.
- `nfp_ccm_wait_reply()` logs `err == ERESTARTSYS`, but `wait_event_interruptible_timeout()` returns negative `-ERESTARTSYS`, so that comparison appears sign-sensitive.
- All reply queue operations rely on `nfp_ctrl_lock(app->ctrl)` serialization; receive and send paths must use the same lock.
- `nfp_ccm_clean()` only warns if replies remain queued; callers must ensure no in-flight requests during app teardown.
- A wrong reply type or size is converted to `-EIO` after freeing the skb.

## Test Signals
Exercise successful request/reply, wrong type/size, short receive skb, unknown tag receive, timeout, interrupted wait, tag-window exhaustion, late reply after timeout, concurrent map operations, and app cleanup with no queued replies or busy tags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/ccm.c -->

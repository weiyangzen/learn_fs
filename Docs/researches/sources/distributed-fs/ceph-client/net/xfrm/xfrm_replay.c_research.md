# sources/distributed-fs/ceph-client/net/xfrm/xfrm_replay.c

## Purpose

`xfrm_replay.c` implements anti-replay and outbound sequence-number management for XFRM states. It supports legacy 32-bit replay windows, bitmap replay windows stored in `struct xfrm_replay_state_esn`, Extended Sequence Number mode, asynchronous replay state notifications to key managers, and offload-aware outbound sequence allocation for GSO packets.

## Important APIs, Types, and Functions

Public entry points are `xfrm_replay_seqhi()`, `xfrm_replay_notify()`, `xfrm_replay_advance()`, `xfrm_replay_check()`, `xfrm_replay_recheck()`, `xfrm_replay_overflow()`, and `xfrm_init_replay()`.

Legacy mode uses `x->replay.seq`, `x->replay.oseq`, and `x->replay.bitmap`. BMP and ESN modes use `x->replay_esn`, `x->preplay_esn`, `replay_window`, `bmp_len`, `seq`, `seq_hi`, `oseq`, `oseq_hi`, and a variable-size bitmap. ESN-specific logic derives the high sequence number with `xfrm_replay_seqhi()` and validates `XFRM_SKB_CB(skb)->seq.input.hi` during recheck.

Mode-specific helpers include `xfrm_replay_check_legacy()`, `xfrm_replay_check_bmp()`, `xfrm_replay_check_esn()`, `xfrm_replay_advance_bmp()`, `xfrm_replay_advance_esn()`, `xfrm_replay_notify_bmp()`, `xfrm_replay_notify_esn()`, and overflow helpers for legacy/BMP/ESN plus offload variants under `CONFIG_XFRM_OFFLOAD`.

## Control Flow

Inbound processing first calls `xfrm_replay_check()` to reject zero, stale, or duplicate sequence numbers. The mode switch dispatches to legacy, BMP, or ESN checks. Accepted packets later call `xfrm_replay_advance()` to slide the window, clear skipped bitmap positions, mark the received packet bit, update ESN high bits when wrap is detected, optionally notify devices through `xfrm_dev_state_advance_esn()`, and emit replay update notifications if async events are enabled.

ESN checking divides sequence space into the RFC-style same-subspace and window-spans-two-subspaces cases. `xfrm_replay_seqhi()` predicts the high sequence half for a network-order low sequence. Recheck verifies the saved input high half before performing the normal ESN duplicate/window check.

Outbound processing calls `xfrm_replay_overflow()` to allocate the next outgoing sequence. Legacy and BMP paths reject wrap unless `XFRM_SA_XFLAG_OSEQ_MAY_WRAP` permits it. ESN increments `oseq_hi` on low-half wrap and rejects overflow only when the high half wraps. Offload paths store sequence numbers both in `XFRM_SKB_CB` and `struct xfrm_offload`; for GSO they reserve a range equal to `gso_segs`.

Replay notifications compare current replay state to `preplay` snapshots. Updates are sent when sequence deltas exceed `replay_maxdiff` or when `replay_maxage` timeout fires with changes. Otherwise `XFRM_TIME_DEFER` records deferred notification state. Notifications are delivered as `XFRM_MSG_NEWAE` through `km_state_notify()`.

## State and Persistence Behavior

Replay state persists in each `struct xfrm_state`. Legacy state is embedded in `x->replay`/`x->preplay`; BMP/ESN state is dynamically allocated as `x->replay_esn` and `x->preplay_esn`. Statistics increment `x->stats.replay` and `x->stats.replay_window` on duplicate/window failures. Audit records are emitted for replay failures and outbound overflow.

`xfrm_init_replay()` selects `XFRM_REPLAY_MODE_LEGACY`, `XFRM_REPLAY_MODE_BMP`, or `XFRM_REPLAY_MODE_ESN`. It validates that bitmap storage can cover the replay window and requires a nonzero ESN replay window for inbound or directionless SAs.

## Dependencies and Integration Points

This file integrates with `xfrm_state.c` timers, `km_state_notify()`, XFRM audit helpers, async event sysctls through `xfrm_aevent_is_on()`, skb control blocks, optional device offload metadata, and device ESN advance hooks. Protocol-specific input/output code calls these helpers around authentication/decryption/encryption.

## Risks and Edge Cases

Sequence wrap handling is the main security boundary. Off-by-one errors around `bottom`, `top`, bitmap position, or ESN high-half prediction can accept replayed packets or reject valid wraparound packets. Outbound GSO offload must reserve enough sequence numbers; otherwise hardware and software can disagree about ESP sequence assignment.

Notification throttling assumes the caller holds the state lock, as documented in comments. Calling without serialization can corrupt `preplay` snapshots or timer/defer state. Bitmap size validation is essential because subsequent helpers index `bmp[nr]` based on `replay_window`.

## Test Signals

Replay tests should cover zero sequence rejection, duplicate rejection, packets older than the replay window, out-of-order packets inside the window, ESN low-half wrap, outbound low/high overflow, `XFRM_SA_XFLAG_OSEQ_MAY_WRAP`, GSO offload sequence reservation, async event threshold and timeout notifications, and audit/MIB increments for replay failures.

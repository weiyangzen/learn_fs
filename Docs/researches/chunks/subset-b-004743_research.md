# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/debugfs_htt_stats.c lines 5977-6441

## Scope And Purpose

This chunk is the end of ath12k's debugfs HTT extended-stats implementation. It covers the tail of the TLV tag dispatcher in `ath12k_dbg_htt_ext_stats_parse()`, the target-to-host extended-stats event handler, the debugfs file operations for selecting and dumping a stats type, the synchronous request path that sends an HTT stats command to firmware, the matching open/release/read lifecycle, the debugfs reset command, and registration of the three per-pdev debugfs files.

The code is diagnostic plumbing, not a normal data path. Userspace writes a stats type and optional configuration words to `htt_stats_type`, opens/reads `htt_stats` to trigger one firmware stats upload and collect formatted text, or writes a stats type to `htt_stats_reset` to reset firmware-side counters for that category. The firmware response arrives asynchronously as an HTT target-to-host `EXT_STATS_CONF` message, is matched back to the active per-radio request by a cookie, parsed as TLVs, and appended into a per-request text buffer.

## Important APIs, Types, And Constants

- `ath12k_dbg_htt_ext_stats_parse()` is the TLV iterator callback. The lines in this chunk finish its large `switch (tag)` by routing HTT stats tags to type-specific `ath12k_htt_print_*_tlv()` formatters and then returning `0`.
- `ath12k_debugfs_htt_ext_stats_handler(struct ath12k_base *ab, struct sk_buff *skb)` handles firmware HTT extended-stats confirmations. It validates the cookie, resolves the target pdev to `struct ath12k`, records the done bit, parses TLVs, and completes the pending request when the firmware marks the upload complete.
- `ath12k_read_htt_stats_type()` and `ath12k_write_htt_stats_type()` implement the `htt_stats_type` debugfs file. Reads return the current `ar->debug.htt_stats.type`; writes accept a stats type plus up to four optional config parameters.
- `ath12k_debugfs_htt_stats_req()` sends one host-to-target stats request with `ath12k_dp_tx_htt_h2t_ext_stats_req()` and waits up to `3 * HZ` for the completion set by the event handler.
- `ath12k_open_htt_stats()`, `ath12k_read_htt_stats()`, and `ath12k_release_htt_stats()` implement the read-only `htt_stats` debugfs file. Opening the file allocates a `struct debug_htt_stats_req`, sends the firmware request, and stores the completed request in `file->private_data` for subsequent reads.
- `ath12k_write_htt_stats_reset()` implements the write-only `htt_stats_reset` file by translating the requested stats type into reset bitmap config words and sending an `ATH12K_DBG_HTT_EXT_STATS_RESET` request.
- `ath12k_debugfs_htt_stats_register()` creates `htt_stats_type`, `htt_stats`, and `htt_stats_reset` under `ar->debug.debugfs_pdev`.
- `struct debug_htt_stats_req` is defined in `debugfs_htt_stats.h`. It stores `done`, `override_cfg_param`, `pdev_id`, `type`, four `cfg_param[]` words, a completion, `buf_len`, and a flexible `buf[]` that is allocated with `ATH12K_HTT_STATS_BUF_SIZE`.
- `ATH12K_HTT_STATS_BUF_SIZE` is 512 KiB. The print helpers in this file append human-readable output to this buffer with `scnprintf()` and update `stats_req->buf_len`.
- `struct ath12k_htt_extd_stats_msg` is the firmware upload message: fixed HTT info fields, an echoed 64-bit cookie, an `info1` field containing the done bit and data length, followed by TLV data.
- `ATH12K_HTT_STATS_COOKIE_MSB`, `ATH12K_HTT_STATS_COOKIE_LSB`, and `ATH12K_HTT_STATS_MAGIC_VALUE` define the cookie layout. The driver encodes a magic value in the upper 32 bits and the target pdev id in the lower 32 bits.
- `struct htt_ext_stats_cfg_params` carries the four firmware config words (`cfg0` through `cfg3`) sent by `ath12k_dp_tx_htt_h2t_ext_stats_req()`.

## TLV Dispatch Coverage

The chunk begins mid-switch in `ath12k_dbg_htt_ext_stats_parse()`. The tags covered here include latency profile counters and stats, UL OFDMA and UL MU-MIMO trigger/user stats, RX FSE stats, TXBF rate and OFDMA NDPA/NDP/BRP/steering stats, DLPAGER stats, PHY stats/counters/reset/TPC stats, common SoC TXRX stats, per-rate stats, AST entries, puncture stats, DMAC reset stats, scheduler algorithm OFDMA stats, BE OFDMA TX rate stats, MBSSID control-frame stats, legacy TX/RX pdev rate stats, histogram stats, RX rate extension stats, TDMA stats, MLO scheduler and IPC stats, RTT responder/initiator/hardware/TBR stats, TX HWQ common stats, and channel-switch timing stats.

Every recognized tag is handled by a dedicated formatter that receives the raw TLV body, the TLV length, and the active `debug_htt_stats_req`. The formatter is expected to validate its own minimum structure length before reading fields, convert little-endian firmware counters to CPU order, and append text to `stats_req->buf`. Unrecognized tags are ignored by the `default` case. The parse callback always returns success, so bad or unsupported tags do not abort the whole upload unless the lower-level TLV iterator detects malformed framing.

## Request And Response Control Flow

The normal dump flow starts with userspace selecting a stats type:

1. Userspace writes `"<type> [cfg0 cfg1 cfg2 cfg3]"` to `htt_stats_type`.
2. `ath12k_write_htt_stats_type()` copies at most 32 bytes from userspace, parses the stats type and optional parameters with `sscanf()`, rejects the reset pseudo-type and values greater than or equal to `ATH12K_DBG_HTT_NUM_EXT_STATS`, then stores the type/config under the `wiphy` lock.
3. Userspace opens `htt_stats`.
4. `ath12k_open_htt_stats()` rejects the reset pseudo-type, takes the `wiphy` lock, requires `ah->state == ATH12K_HW_STATE_ON`, rejects concurrent dumps with `-EAGAIN` when `ar->debug.htt_stats.stats_req` is already set, allocates the request plus the 512 KiB buffer, copies the selected type/config into the request, and marks `override_cfg_param` if any config word is nonzero.
5. `ath12k_debugfs_htt_stats_req()` initializes the completion, records the target pdev id, clears `done`, builds a cookie from magic plus pdev id, copies optional config words into `htt_ext_stats_cfg_params`, sends the HTT H2T extended-stats request, and waits up to three seconds.
6. Firmware replies via the HTT receive path. `ath12k_dp_htt_htc_t2h_msg_handler()` dispatches `HTT_T2H_MSG_TYPE_EXT_STATS_CONF` to `ath12k_debugfs_htt_ext_stats_handler()`.
7. The handler validates the cookie magic, resolves `pdev_id` to `struct ath12k` under RCU, obtains the active `stats_req`, sets `stats_req->done` from `ATH12K_HTT_T2H_EXT_STATS_INFO1_DONE` under `ar->data_lock`, checks the indicated payload length against the SKB length, and parses the TLV data with `ath12k_dp_htt_tlv_iter()`.
8. If the done bit was set, the handler calls `complete(&stats_req->htt_stats_rcvd)`, allowing the opener to finish. Userspace can then read `htt_stats`, which returns the formatted buffer through `simple_read_from_buffer()`.
9. Closing the file frees the request and clears `ar->debug.htt_stats.stats_req` under the `wiphy` lock.

Multi-segment firmware uploads are handled by the same request object. Non-final segments append parsed text and leave the waiter blocked. The segment with the done bit appends its TLVs and completes the request. Timeout handling in `ath12k_debugfs_htt_stats_req()` sets `done = true` under `data_lock` and returns `-ETIMEDOUT` if no done segment was observed before the three-second deadline.

## Reset Control Flow

`htt_stats_reset` is a separate write-only command path. Userspace writes one stats type. `ath12k_write_htt_stats_reset()` parses it with `kstrtou32_from_user()`, rejects out-of-range values and the reset pseudo-type itself, then builds a reset request for firmware stats type `ATH12K_DBG_HTT_EXT_STATS_RESET`.

The reset bitmap is distributed across `cfg1`, `cfg2`, or `cfg3` depending on `(type >> 5) + 1`, with `cfg0` set to `HTT_STAT_DEFAULT_RESET_START_OFFSET`. The helper macros `ATH12K_HTT_STATS_RESET_BITMAP32_BIT()` and `ATH12K_HTT_STATS_RESET_BITMAP64_BIT()` mask the bit position for the relevant config word. The command is sent with cookie `0ULL` because this path does not wait for a parsed stats response. On successful send, `ar->debug.htt_stats.reset` records the requested type under the `wiphy` lock.

## State And Persistence Behavior

The persistent debugfs configuration lives in `ar->debug.htt_stats`, which is embedded in `struct ath12k_debug`. `type`, `cfg_param[4]`, and `reset` survive across debugfs file opens while the radio remains registered. `stats_req` is transient and non-NULL only while one `htt_stats` file instance is open and has an active/completed request object.

Each `struct debug_htt_stats_req` owns its completion and formatted output buffer. Its lifetime is bound to the open `htt_stats` file: allocation and request submission happen in `.open`, `file->private_data` points to the request for `.read`, and `.release` frees the request. The code deliberately permits only one active request per `struct ath12k`; another opener gets `-EAGAIN`.

The firmware counters themselves are not persisted by this code. The dump path reads firmware state into a temporary host buffer, while the reset path asks firmware to clear selected counter categories. No state is written to disk. The debugfs files are recreated per pdev during ath12k debugfs setup and disappear with the debugfs pdev directory.

Locking is split by purpose:

- `wiphy_lock()` serializes user-visible debugfs configuration changes, open/release request ownership, and reset command submission with other cfg80211/mac80211 radio operations.
- `rcu_read_lock()` protects lookup of `struct ath12k` from a pdev id in the asynchronous HTT event handler.
- `ar->data_lock` protects `stats_req->done` updates shared between the event handler and the request wait/timeout path.
- The text buffer itself is not separately locked. It relies on the single active request model and on completion ordering: userspace receives a readable file only after `.open` has returned from the synchronous request function.

## Dependencies And Integration Points

This chunk depends on the ath12k debugfs framework for per-pdev directory creation and on `CONFIG_ATH12K_DEBUGFS` for the external handler declaration. `ath12k_debugfs_htt_stats_register()` is called from the broader debugfs registration path after `ar->debug.debugfs_pdev` exists.

It integrates with the HTT data-path control channel in both directions. Requests are sent through `ath12k_dp_tx_htt_h2t_ext_stats_req()`, which allocates an HTC SKB, fills `HTT_H2T_MSG_TYPE_EXT_STATS_CFG`, sets a pdev mask based on `ath12k_mac_get_target_pdev_id(ar)`, copies the four config words and cookie, and sends it on the HTT endpoint. Responses arrive in `ath12k_dp_htt_htc_t2h_msg_handler()` and are routed to this file's handler on `HTT_T2H_MSG_TYPE_EXT_STATS_CONF`.

The pdev mapping dependency is important. The request cookie encodes the target pdev id returned by `ath12k_mac_get_target_pdev_id(ar)`, while the response handler uses the cookie's low bits with `ath12k_mac_get_ar_by_pdev_id(ab, pdev_id)` to recover the radio object. If firmware echoes an incorrect cookie or pdev id, the handler logs a warning and drops the response.

The TLV parser depends on `ath12k_dp_htt_tlv_iter()` for safe HTT TLV framing and on a large set of formatter functions earlier in `debugfs_htt_stats.c`. Those formatters depend on TLV structure definitions in `debugfs_htt_stats.h` and related HTT definitions in `dp_htt.h`. This final dispatcher section is the integration point that makes newly added formatter functions reachable from firmware tags.

The code uses standard kernel user-buffer and debugfs helpers: `copy_from_user()`, `kstrtou32_from_user()`, `simple_read_from_buffer()`, `simple_open`, `default_llseek`, and `debugfs_create_file()`. It also relies on kernel completion, bitfield, endian, SKB, allocation, and warning APIs.

## Risks And Edge Cases

Cookie validation prevents unrelated HTT messages from completing a debugfs request, but the handler does not validate that the response stats type matches `stats_req->type`. It trusts firmware and the echoed cookie/pdev mapping. A stale or reused cookie would be mitigated by the magic plus single active request per pdev, but the cookie is deterministic for a pdev rather than per-open unique.

The length check uses `if (len > skb->len)`, where `len` is the payload length from `info1` and `skb->len` includes the fixed message header. That is conservative enough to catch huge values but does not by itself prove that `msg->data + len` is inside the SKB after accounting for `sizeof(*msg)`. Correctness depends on the HTT receive path and TLV iterator not reading beyond valid data. This is a useful audit point for malformed firmware messages.

The request object can be timed out while a late firmware segment is still in flight. On timeout, `ath12k_debugfs_htt_stats_req()` marks `done = true`, frees the request in the open error path, and clears `ar->debug.htt_stats.stats_req` under the `wiphy` lock. A later event handler first fetches `ar->debug.htt_stats.stats_req` and drops the response if it is NULL, which avoids use-after-free as long as the pointer is cleared before late processing observes it. The mixed `wiphy_lock`, RCU, and `data_lock` model is worth preserving carefully if this path is refactored.

`ath12k_write_htt_stats_type()` accepts at most 32 bytes and parses with `sscanf()` into an enum object and four unsigned ints. The `num_args > 5` check is defensive but unreachable for this format. Negative textual input is not accepted as a valid unsigned parse in the intended way, but type-size differences between enum and `%u` are always a point to review in kernel code. The function rejects reset and out-of-range types but does not validate whether a specific stats type supports the supplied config words.

`override_cfg_param` is false when all four config words are zero. This means a user cannot explicitly send all-zero override config; all-zero is treated the same as no override. That appears intentional for default stats behavior, but it matters for any future stats type where zero-valued config fields have a distinct semantic.

The formatter dispatch silently ignores unrecognized tags. This is good for forward compatibility with firmware that emits extra TLVs, but it also means missing host support for a tag produces no debugfs-visible error beyond absent output.

Output truncation is bounded by `ATH12K_HTT_STATS_BUF_SIZE`, but the many formatter functions generally keep incrementing `stats_req->buf_len` by `scnprintf()` return values. If `buf_len - len` underflows after logical length exceeds the buffer, later appends can become risky depending on the exact types and helper usage in the formatter. This chunk's read path clamps the readable length to the buffer size, but buffer-write safety relies on the formatter pattern across the whole file.

The reset path sends a firmware command while holding the `wiphy` lock and does not wait for a completion. It records `reset` only after a successful send. There is no user-visible confirmation that firmware actually applied the reset beyond the send result and later counter observations.

## Test Signals

Useful validation for this chunk includes:

- Debugfs smoke tests that write a valid stats type to `htt_stats_type`, open/read `htt_stats`, and confirm the output contains expected TLV headings for a live device.
- Negative input tests for `htt_stats_type`: oversized writes, empty/non-numeric input, reset type `0`, values greater than or equal to `ATH12K_DBG_HTT_NUM_EXT_STATS`, and valid type plus one to four config words.
- Concurrency tests opening `htt_stats` twice on the same pdev. The second open should return `-EAGAIN` while the first request object is active.
- Firmware timeout tests or fault injection for dropped `EXT_STATS_CONF` events. The open path should return `-ETIMEDOUT`, free the request, clear `ar->debug.htt_stats.stats_req`, and tolerate a late response.
- Response validation tests for bad cookie magic, unknown pdev id, malformed TLV length, and unknown TLV tags. Expected signals are warnings for invalid cookie/pdev/parse errors and no kernel crash.
- Multi-segment response tests where one or more non-done segments append output and only the done segment completes the waiter.
- Reset tests writing several stats type values around 31/32 and 63/64 boundaries to verify the correct reset bitmap word (`cfg1`, `cfg2`, or `cfg3`) and bit position are sent.
- Lockdep-enabled tests around debugfs read/reset during interface down, hardware state transitions, and radio removal. The open path should reject non-ON hardware with `-ENETDOWN`, and the event handler should not dereference missing `ar` or request state.
- Buffer pressure tests with verbose stats types to verify output is clamped to 512 KiB, formatting remains readable, and no sanitizer reports appear from formatter append paths.
- Build coverage with `CONFIG_ATH12K_DEBUGFS` enabled and disabled. When disabled, the header provides an inline no-op response handler, so the HTT receive path should still compile.

For the research pipeline, the key artifact signal is this source-tree-aligned chunk document at `Docs/researches/chunks/subset-b-004743_research.md`. It intentionally covers only `debugfs_htt_stats.c` lines 5977-6441; the later merge lane should reconcile it with earlier chunks that define the individual TLV formatters and most HTT TLV structures.

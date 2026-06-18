# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_tx.c

Purpose: Implements host-to-firmware HIF request construction, synchronous command sending, and high-level request helpers for configuration, reset, scan, join, keys, EDCA, PM, AP start, beacon transmit, link mapping, and IE update.

Important APIs and functions: `wfx_init_hif_cmd()` initializes command serialization. `wfx_cmd_send()` is the central synchronous/asynchronous send path. Public wrappers include `wfx_hif_shutdown()`, `wfx_hif_configuration()`, `wfx_hif_reset()`, `wfx_hif_read_mib()`, `wfx_hif_write_mib()`, `wfx_hif_scan_uniq()`, `wfx_hif_scan()`, `wfx_hif_stop_scan()`, `wfx_hif_join()`, `wfx_hif_set_bss_params()`, `wfx_hif_add_key()`, `wfx_hif_remove_key()`, `wfx_hif_set_edca_queue_params()`, `wfx_hif_set_pm()`, `wfx_hif_start()`, `wfx_hif_beacon_transmit()`, `wfx_hif_map_link()`, and `wfx_hif_update_ie_beacon()`.

Control flow and integration: Each wrapper allocates a `wfx_hif_msg`, fills the common header with `wfx_fill_header()`, populates a packed command body, calls `wfx_cmd_send()`, then frees the request. `wfx_cmd_send()` serializes with `hif_cmd.lock`, publishes `buf_send`/reply buffer, completes `hif_cmd.ready` for BH TX, optionally polls IRQ during boot, waits for `hif_cmd.done`, logs slow/missing replies, freezes the chip on timeout, and formats HIF/MIB names for diagnostics.

State and persistence: Uses `wdev->hif_cmd` lock/completions/buffers/return code and `wdev->chip_frozen`. Firmware state changed by wrappers includes PDS configuration, reset, scan state, BSS/join state, key table, EDCA/PM/AP/link/IE state.

Dependencies: Depends on BH scheduling, HWIO control for shutdown fallback, HIF command/general layouts, mac80211 channel/BSS/scan/queue types, debug name helpers, and station API-version checks.

Risks and test signals: Risks include command timeout deadlocks, no-reply shutdown ordering, reply buffer size mismatch returning `-EIO`, MIB read copying variable lengths, API-version-specific add-key interface ID, old queue ID mapping, scan bounds, and signed/unsigned status handling. Tests should cover command serialization, boot polling, timeout/freeze path, all request wrappers, scan passive/active timing, join without BSS/SSID, EDCA queue mapping for old/new APIs, PM idle conversion, and shutdown during release.

Test signals: Source read size: 537 lines, 15924 bytes.

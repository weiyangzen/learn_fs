# sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/wsm.c

Purpose: Implements the CW1200 WSM host-interface command, confirmation, indication, and TX-buffer plumbing. It serializes firmware commands, marshals/unmarshals WSM byte streams, dispatches firmware indications, and selects TX frames or commands for the bus bottom half.

Important APIs, types, and functions: Command APIs include `wsm_configuration`, `wsm_reset`, `wsm_read_mib`, `wsm_write_mib`, `wsm_scan`, `wsm_join`, `wsm_set_bss_params`, `wsm_add_key`, `wsm_set_edca_params`, `wsm_switch_channel`, `wsm_set_pm`, `wsm_start`, `wsm_map_link`, and `wsm_update_ie`. Transport functions include `wsm_cmd_send`, `wsm_handle_rx`, `wsm_get_tx`, `wsm_txed`, `wsm_lock_tx`, `wsm_flush_tx`, and WSM buffer helpers.

Control flow: Command helpers fill `priv->wsm_cmd_buf` using checked `WSM_PUT*` macros, serialize with `wsm_cmd_mux`, publish `priv->wsm_cmd` under spinlock, wake the BH, and wait on `wsm_cmd_wq`. `wsm_handle_rx()` strips link ID bits, dispatches TX confirms, command responses, or indications by WSM ID, runs command-specific confirm parsers, stores `priv->wsm_cmd.ret`, and wakes waiters. Indications update firmware caps/startup readiness, deliver RX frames to `cw1200_rx_cb`, enqueue generic events, signal scan/join/channel/PM completion, and handle suspend/resume. TX selection prioritizes pending commands, then AP multicast, sleeping-station constraints, EDCA scoring, bursting, and special firmware workarounds.

State and persistence: In-memory state includes `priv->wsm_cmd`, `wsm_cmd_buf`, firmware capability fields, `firmware_ready`, TX lock counter, channel/PM wait states, event queue, and BH error flags. Device-side state is changed through WSM/MIB commands but is not persisted by this file.

Dependencies and integration points: Integrates with CW1200 BH, queue, STA, scan, join, PM, and debug code; Linux wait queues, mutexes, spinlocks, workqueues, skbs, and mac80211 frame helpers; and firmware WSM message IDs from `wsm.h`.

Risks: Firmware command timeout kills the BH thread and sets fatal state; lost or repeated responses are guarded but still fragile. Buffer macros rely on `goto underflow/nomem` in each function. `wsm_flush_tx()` can declare fatal BH error if firmware keeps frames too long. Some message IDs are literal constants, making spec drift harder to audit. `wsm_cmd_send()` busy-spins under a spinlock until `done` instead of sleeping.

Test signals: Validate startup indication, command timeout path, MIB read/write, scan/join/channel-switch/PM indications, multi-TX confirm buffer release, TX lock/flush behavior, event queue processing, and malformed WSM underflow handling.

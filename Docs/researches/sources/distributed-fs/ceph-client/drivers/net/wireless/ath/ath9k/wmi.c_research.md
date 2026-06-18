# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/wmi.c

## Purpose
`wmi.c` implements the WMI control channel for ath9k_htc USB devices. It sends serialized commands over an HTC endpoint, waits for matching responses, queues asynchronous firmware events, and dispatches events such as SWBA, fatal reset, and TX status.

## Important APIs, types, and functions
`ath9k_init_wmi()` allocates `struct wmi`, initializes queues, locks, completions, pending event lists, and the tasklet. `ath9k_wmi_connect()` binds WMI callbacks to `WMI_CONTROL_SVC` through HTC. `ath9k_wmi_cmd()` builds an SKB with HTC/WMI headroom, serializes command issue under `op_mutex`, waits on `cmd_wait`, and handles timeout by invalidating `last_seq_id`. `ath9k_wmi_ctrl_rx()` distinguishes events from responses, validates sequence numbers, and schedules the tasklet. `ath9k_wmi_event_tasklet()` drains queued events and dispatches them. `ath9k_stop_wmi()`, `ath9k_destroy_wmi()`, and `ath9k_wmi_event_drain()` stop and clean up state.

## Control flow and integration
Command flow is synchronous: allocate SKB, reserve header room, copy payload, lock operations, reject stopped WMI, push `wmi_cmd_hdr`, increment `tx_seq_id`, record response buffer and sequence, send via HTC, and wait for completion. RX flow is asynchronous from HTC callbacks. Event IDs have bit `0x1000` and are queued for tasklet context; normal responses must match `last_seq_id` before copying response bytes and completing the waiter.

## State and persistence behavior
Persistent WMI state includes `stopped`, HTC endpoint ID, sequence counters, response buffer pointers, event SKB queue, tasklet, locks, and pending TX event list. State lasts for the lifetime of the ath9k_htc private structure and is torn down at device stop/destroy.

## Dependencies
The file depends on `htc.h`, the HTC service layer, ath9k_htc reset/TX/SWBA handlers, Linux SKB queues, tasklets, completions, spinlocks, and mutexes. It uses command IDs and event structs from `wmi.h`.

## Risks
Risks include response timeout races, stale `cmd_rsp_buf`/length if firmware sends malformed responses, sequence wrap or mismatch dropping valid responses, event queue growth if tasklets are blocked, and locking mistakes between HTC callback context and command waiters. Event handling also deliberately ignores events before `priv->initialized`, which must align with probe ordering.

## Test signals
Signals include successful firmware version and register commands, timeout behavior on unplug, correct fatal-event reset work scheduling, TX status delivery under load, no SKB leaks after event drain, and no command execution after `ath9k_stop_wmi()`.

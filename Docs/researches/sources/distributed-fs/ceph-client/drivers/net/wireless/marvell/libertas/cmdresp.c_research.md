## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/cmdresp.c

Purpose: this file handles firmware command responses and asynchronous firmware events for Libertas.

Important functions: `lbs_process_command_response()` validates that a response matches `priv->cur_cmd` by sequence and command ID, handles firmware defer/error/PS special cases, invokes the command callback, completes the command, and clears the timeout. `lbs_process_event()` maps firmware event IDs to driver actions. `lbs_mac_event_disconnected()` reports disconnect, stops queues/carrier, frees current TX skb, resets link state, and exits power save if needed.

Control flow: bus code stores responses in `resp_buf` and notifies the main thread, which calls this response processor. For normal successful commands, the callback runs outside `driver_lock` but under `priv->lock`, then completion returns the node to the free queue or wakes a synchronous waiter. PS mode responses update `psstate`/`needtowakeup` inline. Events handle deauth/disassoc/link lost, PS sleep/awake, host/deep sleep wake, MIC failures, MIB/init notifications, RSSI/SNR threshold events, and mesh autostart.

State and persistence: it mutates `connect_status`, `tx_pending_len`, `currenttxskb`, `psstate`, `needtowakeup`, `is_deep_sleep`, `is_host_sleep_activated`, command timer state, and command queue state. No persistent storage is used.

Dependencies and integration: depends on cfg80211 notification helpers, command completion from `cmd.c`, netdev queue/carrier APIs, firmware event constants, wait queues, and bus/main-thread delivery of responses/events.

Risks and tests: mismatched sequence/command responses leave errors and can stall command progress. Firmware result `0x0004` intentionally lets commands time out and resubmit, so timeout handling must be tested. The disconnect path sleeps for supplicant compatibility. Test signals include invalid response injection, PS enter/exit events, host/deep sleep wake events, MIC failure reporting, link-loss notifications, and command callback execution.

# sources/distributed-fs/ceph-client/samples/connector/cn_test.c

Purpose: kernel-side connector/netlink test module that registers connector callbacks and periodically sends messages to user-space listeners.

Important APIs/functions: uses `struct cb_id`, `struct cn_msg`, `cn_add_callback`, `cn_del_callback`, `cn_netlink_send`, `timer_setup`, `mod_timer`, and `timer_delete_sync`. `cn_test_callback` logs received connector messages; `cn_test_timer_func` allocates a `cn_msg`, fills a counter string, sends it, and re-arms the timer.

Control flow: init registers two callbacks for adjacent connector IDs, starts a one-second timer, and logs the final ID. The timer repeatedly sends `counter = N` messages. Exit deletes the timer synchronously and unregisters both callbacks.

State and persistence: global connector ID, timer object, timer counter, and a legacy `nls` socket pointer. State is volatile and reset on module load.

Dependencies and integration: depends on the connector subsystem and netlink. Pairs with `samples/connector/ucon.c`, which subscribes and optionally sends test messages.

Risks: timer callback allocates with `GFP_ATOMIC`, so allocation failure silently drops a tick. The disabled notification example shows raw netlink skb construction and should remain example-only. Callback registration/unregistration depends on restoring `cn_test_id.val` correctly during unwind.

Test signals: load `cn_test.ko`, run `ucon`, observe one-second connector messages, run `ucon -s` to send bursts, and inspect kernel logs for callback output and clean unregister on unload.

# sources/distributed-fs/ceph-client/security/integrity/ima/ima_queue_keys.c

Purpose: Defers asymmetric key measurements until a custom IMA policy is loaded or a timeout proves none will be loaded.

Important APIs/types/functions: Provides `ima_init_key_queue()`, `ima_queue_key()`, `ima_process_queued_keys()`, and `ima_should_queue_key()`. Uses `struct ima_key_entry` from IMA headers, `ima_keys_lock`, `ima_keys`, delayed work `ima_keys_delayed_work`, and `timer_expired`.

Control flow: At init, a delayed worker is scheduled for five minutes. `ima_queue_key()` copies the key payload and keyring description, then enqueues the entry only while `ima_process_keys` is false. `ima_update_policy()` later calls `ima_process_queued_keys()`, which atomically flips processing mode, cancels the timeout if it has not fired, measures queued keys with `process_buffer_measurement(... KEY_CHECK ...)`, then frees all entries. If the timer fires first, queued keys are discarded without measurement.

State and persistence: Queued keys live only in memory. Once `ima_process_keys` becomes true, it never returns to queueing mode, so future keys are measured immediately by the normal key measurement path.

Dependencies and integration: Integrated with IMA policy loading, keyring notifications, asymmetric key payloads, workqueues, user namespace idmaps, and integrity audit for allocation failures.

Risks and test signals: Main risks are missed measurements when policy loads close to timeout, allocation failure audit correctness, list lifetime during concurrent queue/process calls, and copying untrusted payload lengths. Tests should simulate policy load before and after timeout, concurrent key arrivals, and OOM cleanup.

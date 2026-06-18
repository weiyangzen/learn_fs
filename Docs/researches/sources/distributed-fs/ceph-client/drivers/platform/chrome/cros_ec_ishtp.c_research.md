# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_ishtp.c

Purpose: ISH-TP transport driver for ChromeOS EC firmware running on Intel Integrated Sensor Hub.

Important APIs, types, and functions: ISH message `struct header` distinguishes `CROS_EC_COMMAND` responses from `CROS_MKBP_EVENT` notifications. `struct response_info` coordinates command response wait state. `struct ishtp_cl_data` stores ISH client, response state, reset/event work, and core EC device. `ish_send()` sends a tokenized command and waits for response. `process_recv()` parses incoming packets. `cros_ec_pkt_xfer_ish()` adapts core EC v3 packets to ISH framing. Probe/reset/remove manage ISH client lifecycle.

Control flow: probe takes a write lock on global `init_lock`, allocates and connects an ISH client, registers the receive callback, initializes work and waitqueue, releases the lock, then creates/registers a core EC device using packet transfer only. Command transfer takes a read lock unless reset/init is active, prepares EC request after ISH header, sends through `ish_send()`, validates response and checksum, and returns data length. Receive callback drains RX buffers: command responses validate token/status, copy into waiting buffer, set `received`, and wake the sender; MKBP events timestamp and schedule work to call `cros_ec_irq_thread()`. Reset work takes write lock, destroys/re-establishes the ISH connection, and refreshes EC private pointers.

State and persistence: `init_lock` globally serializes init/reset against send/receive. `next_token` in `ish_send()` is static across devices. Response state is single outstanding command per client. Work items bridge asynchronous ISH notifications to the core EC event path.

Dependencies and integration points: Intel ISH client interface, Chrome EC core/protocol helpers, waitqueues, workqueues, PM ops, and ISH GUID matching. No separate IRQ is assigned; MKBP channel drives event handling.

Risks and edge cases: `wait_event_interruptible_timeout()` return value is ignored except via `received`, so interrupted waits become timeout-like if no response arrived. Static token is global, which is acceptable for serialized commands but not per-client isolated. Global `init_lock` serializes all instances. Receive path has several error labels that set shared response error even for malformed async packets. PM calls core suspend/resume on the EC device.

Test signals: ISH connection establishment, host command round trips, token mismatch drop, timeout handling, MKBP event delivery, reset recovery, suspend/resume, and module remove cancelling work before unregistering EC.

# sources/distributed-fs/ceph-client/include/media/cec.h

Purpose: Main kernel CEC core interface for HDMI Consumer Electronics Control adapters, filehandles, message/event queues, transmit completion, received-message injection, EDID physical-address parsing, and connector metadata.

Important APIs/types/functions: Key types are `cec_devnode`, `cec_data`, `cec_fh`, `cec_adap_ops`, and `cec_adapter`. Driver-facing APIs include `cec_allocate_adapter`, register/unregister/delete, `cec_s_log_addrs`, `cec_s_phys_addr`, `cec_s_conn_info`, `cec_transmit_msg`, `cec_transmit_done_ts`, `cec_transmit_attempt_done_ts`, `cec_received_msg_ts`, pin event queueing helpers, and EDID helpers. Inline helpers manage device references, driver data, logical-address tests, sink tests, registration state, and invalidation.

Control flow: Adapter drivers allocate and register an adapter with low-level ops. Userspace opens `/dev/cecX`; `cec_fh` tracks initiator/follower/monitor modes and queues events/messages. Transmits enter adapter queues, the core invokes `adap_transmit`, and drivers complete with timestamped done callbacks. Received messages are timestamped into the core and optionally passed to high-level callbacks.

State and persistence: `cec_adapter` holds mutex-protected adapter state, transmit and wait queues, kthreads, logical/physical addresses, monitor/follower counters, remote-control integration, connector info, debug counters, notifier/pin pointers, and device-node state. Nothing is persisted across driver removal.

Dependencies and integration: Depends on Linux device/cdev/fs/kthread/timer infrastructure, `linux/cec-funcs.h`, rc-core, optional notifier and pin frameworks, DRM connector info, and EDID parsing.

Risks and test signals: Risks include open/unregister races, queue overflow, wrong lock order, aborted transmit handling when physical address changes, disabled-core stubs, EDID bounds parsing, and CEC timing/retry compliance. Test registration lifetime, simultaneous filehandles, monitor/follower exclusivity, transmit completion statuses, queue limits, HPD/5V pin events, and EDID SPA extraction.

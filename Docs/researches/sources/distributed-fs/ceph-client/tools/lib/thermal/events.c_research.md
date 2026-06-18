# sources/distributed-fs/ceph-client/tools/lib/thermal/events.c

Purpose: Subscribes to thermal generic-netlink event multicast group, dispatches thermal events to user-provided callbacks, and exposes the event socket fd.

Important APIs/types/functions: Public APIs are `thermal_events_init()`, `thermal_events_exit()`, `thermal_events_handle()`, and `thermal_events_fd()`. Internal `thermal_events_ops_init()` populates the `enabled_ops` command table from callback presence. `handle_thermal_event()` parses a netlink event and calls the matching callback.

Control flow: Init records which callbacks are non-NULL, connects a netlink socket, and subscribes to `THERMAL_GENL_EVENT_GROUP_NAME`. Handle installs a valid-message callback and calls `nl_recvmsgs()`. The message handler parses attributes, skips disabled event types, and switches on `genlhdr->cmd` to invoke the corresponding user callback with extracted attributes.

State and persistence: Static `enabled_ops` is process-global, not per-handler. `struct thermal_handler` stores event socket/callback. Event handling is runtime-only.

Dependencies/integration: Depends on libnl, Linux thermal event constants, public `thermal_events_ops`, and private netlink helpers.

Risks: `enabled_ops` being global means multiple handlers with different ops can interfere. `handle_thermal_event()` assumes enabled callbacks are non-NULL and required attrs exist; malformed messages can dereference NULL attrs. `THERMAL_GENL_ATTR_GOV_NAME` is used for governor events while policy elsewhere uses `THERMAL_GENL_ATTR_TZ_GOV_NAME`, which may indicate an attribute-name mismatch depending on UAPI definitions. Exit returns error before disconnecting if unsubscribe fails.

Test signals: Simulate every event type, disabled callbacks, missing attrs, multiple handlers, subscription failure, fd retrieval, and unsubscribe/disconnect behavior.

# sources/distributed-fs/ceph-client/include/linux/firmware/xlnx-event-manager.h

## Purpose
This header defines the AMD/Xilinx firmware event manager client API for subscribing to platform management callbacks.

## APIs, types, and control flow
`event_cb_func_t` receives a pointer to up to `CB_MAX_PAYLOAD_SIZE` 32-bit payload words plus caller data. `xlnx_register_event(cb_type, node_id, event, wake, cb_fun, data)` subscribes a callback to a PM callback type, node id, event id, and wake behavior. `xlnx_unregister_event()` removes the matching subscription. The callback id type comes from `xlnx-zynqmp.h`, and constants include subsystem restart and ACPU node ids.

## State and dependencies
Subscription state is owned by the event-manager implementation and keyed by callback type/node/event/function/data tuple. With `CONFIG_XLNX_EVENT_MANAGER` unreachable, both calls return `-ENODEV`. It depends on the ZynqMP firmware definitions and firmware callback delivery.

## Integration, risks, and tests
Users include restart, error, power, and device event consumers that must react to firmware notifications. Risks are unregister tuple mismatches, callback lifetime after module removal, wake flag misuse, and payload length assumptions. Tests should cover disabled stubs, duplicate registration policy, callback dispatch with sample payloads, unregister during callback or module teardown, and wake-capable event delivery.

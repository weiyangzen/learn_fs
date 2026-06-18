<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_kvp.c -->
# sources/distributed-fs/ceph-client/drivers/hv/hv_kvp.c

## Purpose

`hv_kvp.c` implements the Hyper-V Key Value Pair integration component. It negotiates the KVP protocol with the host, forwards host key/value and IP configuration requests to a userspace daemon, converts between UTF-16 host strings and UTF-8 userspace strings, handles daemon registration, and sends serialized responses back to the host.

## Important APIs, Types, and Functions

- `kvp_transaction` stores the single active host transaction: state, receive length, current `hv_kvp_msg`, channel, and request ID.
- `hv_kvp_onchannelcallback()` is the VMBus receive path for host KVP messages.
- `kvp_on_msg()` processes daemon writes through `hv_utils_transport`.
- `kvp_send_key()` converts and sends host requests to userspace.
- `kvp_respond_to_host()` converts daemon responses back to host format and sends the VMBus response.
- `kvp_handle_handshake()`, `kvp_register()`, and `kvp_register_done()` manage daemon registration and version compatibility.
- `process_ib_ipinfo()` and `process_ob_ipinfo()` translate inbound and outbound IP information structures.
- `hv_kvp_init()`, `hv_kvp_init_transport()`, `hv_kvp_pre_suspend()`, `hv_kvp_pre_resume()`, and `hv_kvp_deinit()` integrate with `hv_util.c`.

## Control Flow

`hv_kvp_init()` receives the shared utility receive buffer and channel, sets a larger maximum packet size, and marks the device waiting for daemon registration. `hv_kvp_init_transport()` creates the userspace transport. Host callbacks are ignored during early daemon negotiation except for scheduling a delayed host-handshake poll to avoid losing failover IP messages. Once ready, `hv_kvp_onchannelcallback()` receives a packet, handles IC negotiation directly, or stores a KVP exchange in `kvp_transaction`, marks `HVUTIL_HOSTMSG_RECEIVED`, schedules `kvp_sendkey_work`, and arms a timeout.

`kvp_send_key()` builds a daemon message according to operation type, translating keys, values, and IP fields. `kvp_on_msg()` receives the daemon reply, derives the error code according to daemon protocol version, cancels the timeout, responds to the host, and polls the VMBus channel again. Timeout and reset paths fail the host transaction and reset the state machine.

## State and Persistence Behavior

The implementation intentionally keeps only one outstanding transaction because the Hyper-V IC protocol is request/response. `dm_reg_value` records daemon registration protocol. `recv_buffer` points into the utility service buffer owned by `hv_util.c`; `hvt` owns the transport. Delayed work items persist across transactions and are cancelled on suspend or deinit. On suspend the tasklet is disabled, work is cancelled, and state is forced to ready so resume negotiation can proceed even if userspace writes arrive out of order.

## Dependencies and Integration Points

This file depends on VMBus utility service wiring in `hv_util.c`, negotiation helper `vmbus_prep_negotiate_resp()`, structures from `<linux/hyperv.h>`, connector/misc transport from `hv_utils_transport.c`, and the userspace KVP daemon using `/dev/vmbus/hv_kvp` or legacy connector IDs.

## Risks and Edge Cases

The global transaction model depends on host serialization and driver-side state checks. Buffer-size validation is present for IC headers, but KVP union fields require operation-specific care. String conversion must preserve NUL room and report failures. If userspace is absent or slow, host transactions fail after timeout. Reset/open races with the transport intentionally fail pending host requests.

## Test Signals

Test host IC negotiation, daemon registration versions, daemon absence and timeout, GET/SET/DELETE/ENUMERATE operations, IP GET/SET conversions, UTF-16/UTF-8 conversion failures, transport reset during active requests, suspend/resume ordering, and channel polling after completed transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_kvp.c -->

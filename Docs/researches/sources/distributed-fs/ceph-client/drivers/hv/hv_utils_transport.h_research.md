<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_utils_transport.h -->
# sources/distributed-fs/ceph-client/drivers/hv/hv_utils_transport.h

## Purpose

`hv_utils_transport.h` declares the shared userspace transport contract for Hyper-V utility services such as KVP and VSS. It defines the transport mode state machine, the transport object layout, and init/send/destroy APIs.

## Important APIs, Types, and Functions

- `enum hvutil_transport_mode` defines `HVUTIL_TRANSPORT_INIT`, `HVUTIL_TRANSPORT_NETLINK`, `HVUTIL_TRANSPORT_CHARDEV`, and `HVUTIL_TRANSPORT_DESTROY`.
- `struct hvutil_transport` embeds miscdevice and file operations state, connector ID, list node, callbacks, pending outbound message, waitqueue, mutex, and release completion.
- `hvutil_transport_init()` creates a named transport with connector IDs and service callbacks.
- `hvutil_transport_send()` sends one kernel-originated message to userspace and can run an `on_read` callback.
- `hvutil_transport_destroy()` tears down connector/misc resources and synchronizes with open character-device users.

## Control Flow

Service code includes this header, creates a transport during its utility-service init path, sends requests to userspace with `hvutil_transport_send()`, receives daemon replies through the `on_msg` callback supplied at init, and destroys the transport during service deinit. The mode enum tells the implementation whether communication is unregistered, connector-based, character-device-based, or being destroyed.

## State and Persistence Behavior

The header exposes implementation state because `hv_utils_transport.c` embeds the `file_operations` in the transport and uses `container_of()` from file operations. Service users should treat fields as owned by the transport implementation and interact through the three exported functions plus callbacks.

## Dependencies and Integration Points

It depends on Linux connector and miscdevice headers. The interface is consumed by `hv_kvp.c` and `hv_snapshot.c` and indirectly by `hv_util.c`.

## Risks and Edge Cases

Because the full struct is visible, accidental external mutation could break locking, mode transitions, or pending-message ownership. The callback contract is important: `on_msg` must validate user input and `on_reset` must make service state consistent after daemon disconnect or transport mode switch.

## Test Signals

Compile users of the header after signature changes, test all mode transitions through the C implementation, and verify KVP/VSS reset and daemon reply paths still conform to the callback contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_utils_transport.h -->

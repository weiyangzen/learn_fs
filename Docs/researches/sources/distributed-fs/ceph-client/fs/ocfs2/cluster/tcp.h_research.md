# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/tcp.h

## Purpose

`tcp.h` is the public O2CB network transport interface used by OCFS2 cluster components. It defines the wire header `struct o2net_msg`, payload limits, default timing constants, link-down classification, exported send/handler APIs, connection lifecycle hooks, heartbeat callback registration, module init/exit hooks, and optional debugfs tracking hooks.

## Important APIs, Types, and Functions

`struct o2net_msg` is the fixed header on the wire. It carries a magic value, payload length, message type, system status, handler/user status, domain key, message number, and flexible payload buffer. `O2NET_MAX_PAYLOAD_BYTES` caps payloads to one page minus the header, and DLM message structures size themselves against that limit.

`o2net_msg_handler_func` is the inbound handler signature: it receives a full message buffer, total length, registered private data, and optional post-handler return data. `o2net_post_msg_handler_func` runs after the status response is sent.

The main caller APIs are `o2net_send_message()` for a single contiguous payload and `o2net_send_message_vec()` for kvec payloads. Handler lifecycle uses `o2net_register_handler()` and `o2net_unregister_handler_list()`, where an unregister list lets a subsystem remove all handlers it registered for a domain. `o2net_fill_node_map()` reports currently connected peers.

Cluster lifecycle APIs are `o2net_register_hb_callbacks()`, `o2net_unregister_hb_callbacks()`, `o2net_start_listening()`, `o2net_stop_listening()`, `o2net_disconnect_node()`, `o2net_num_connected_peers()`, `o2net_init()`, and `o2net_exit()`.

`o2net_link_down()` is an inline classifier used by DLM and transport users to treat socket state or errors such as `-ECONNREFUSED`, `-ENOTCONN`, `-ECONNRESET`, and `-EPIPE` as link-down conditions.

## Control Flow

Callers register message handlers before sending or accepting domain traffic. A sender calls `o2net_send_message*()`, which constructs an `o2net_msg`, waits for a valid node connection, sends header plus payload, and waits for a status frame keyed by `msg_num`. The remote transport dispatches the registered handler based on `msg_type` and `key`, then sends a status frame using the same header identity.

Node manager calls the listening APIs as the local cluster node is configured or torn down. Heartbeat callback registration wires `tcp.c` into heartbeat up/down events so peer sockets are established and destroyed as nodes join or leave.

## State and Persistence Behavior

The header itself stores no state. It defines the wire-visible state contract: magic values are private to `tcp_internal.h`, but this header fixes the public header layout, status fields, payload size, and timing defaults. Runtime state lives in `tcp.c`.

## Dependencies and Integration Points

The header bridges Linux socket/kvec types with OCFS2 cluster code. It is included by DLM files such as `dlmast.c` and by node/heartbeat/lifecycle code. It conditionally exposes debugfs hooks when `CONFIG_DEBUG_FS` is enabled and compiles them into empty inline stubs otherwise.

## Risks and Edge Cases

`struct o2net_msg` is a wire ABI. Field size/order changes would break inter-node compatibility. `O2NET_MAX_PAYLOAD_BYTES` is a hard constraint for all cluster messages; any DLM structure that grows past it will fail registration or send validation. `o2net_link_down()` mixes socket state and errno classification; adding or removing errors changes DLM failure semantics.

## Test Signals

Build coverage should include both `CONFIG_DEBUG_FS=y` and `n`. Runtime signals include successful handler registration/unregistration, oversized handler registration rejection, oversized send rejection, correct status propagation, DLM behavior after link-down errors, and node map consistency with active cluster peers.

# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/tcp_internal.h

## Purpose

`tcp_internal.h` is the private implementation header for `tcp.c`. It defines transport magic values, the O2NET protocol version, handshake layout, per-node connection state, per-socket receive/send state, registered handler records, system error values, send waiters, and optional debugfs send tracking.

## Important APIs, Types, and Functions

Magic constants identify normal messages, status responses, keepalive requests, and keepalive responses. `O2NET_QUORUM_DELAY_MS` delays quorum decisions until heartbeat has had time to declare truly dead nodes. `O2NET_PROTOCOL_VERSION` is currently `11` and documents historical protocol/locking semantic changes.

`struct o2net_handshake` is exchanged before a connection becomes valid. It contains protocol version, connector ID, heartbeat timeout, idle timeout, keepalive delay, and reconnect delay. The timeout fields intentionally force cluster-wide timing agreement.

`struct o2net_node` holds per-peer mutable state: `nn_lock`, current socket container, valid bit, persistent error, idle-timeout flag, transmit wait queue, status waiter IDR/list, delayed connect work, connect expiry work, and delayed still-up quorum work.

`struct o2net_sock_container` owns a refcounted socket, peer node pointer, receive/connect/shutdown work, idle timer, keepalive delayed work, handshake state, receive page and offset, original socket callbacks, current message identity for stats/debug, optional debugfs timestamps, optional stats counters, and `sc_send_lock`.

`struct o2net_msg_handler` stores one registered handler in the transport rb-tree. `struct o2net_status_wait` is a pending synchronous send completion. `struct o2net_send_tracking` is either detailed debugfs state or a dummy structure depending on configuration.

## Control Flow

The types in this header encode the control flow of `tcp.c`: peer heartbeats manipulate `o2net_node`; socket callbacks queue work on `o2net_sock_container`; inbound normal messages look up `o2net_msg_handler`; outbound calls wait on `o2net_status_wait`; and debugfs/stat code samples `o2net_send_tracking` and `o2net_sock_container` timing fields.

Handshake is a gate between socket existence and transmit validity. `nn_sc` can point at an `sc` before `nn_sc_valid` is set, but transmitters only proceed after the remote handshake is checked and `o2net_set_nn_state()` marks the connection valid.

## State and Persistence Behavior

All state is in-memory cluster runtime state. The important durability property is not persistence but cluster consistency: mismatched protocol versions or timing values prevent a connection from being considered valid. Pending waiters are transient and are completed either by status response or forced death on shutdown.

## Dependencies and Integration Points

This header depends on `tcp.h` for the public message header and handler types, node manager for `O2NM_MAX_NODES`, heartbeat constants for quorum delay, Linux IDR/list/workqueue/timer/kref/socket types, and optional debugfs/stats configuration. DLM indirectly depends on many of these limits through `O2NET_MAX_PAYLOAD_BYTES` and protocol behavior.

## Risks and Edge Cases

Refcounted socket lifetime is subtle because every queued work item must hold an `sc` reference. `nn_status_idr` IDs become wire-visible `msg_num` values, so waiter removal must be synchronized with response processing and shutdown completion. The one-page receive buffer constrains payload size and makes handler lifetime rules strict: inbound payload memory is invalid after the handler returns.

Protocol-version comments note that O2NET version once represented both transport and filesystem locking semantics. Tests must ensure that filesystem/DLM protocol negotiation remains separate from the transport version after version 11.

## Test Signals

Review signals include structure-size/layout changes, additions to `enum o2net_system_error` without translation updates, work item additions without refcount rules, and handshake field changes without `tcp.c` validation. Runtime signals are handshake rejection on timing mismatch, pending waiter completion on disconnect, debugfs send/socket tracking under `CONFIG_DEBUG_FS`, and stats updates under `CONFIG_OCFS2_FS_STATS`.

# sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd_connection.c

## Purpose
This file implements EFALND connection establishment, lookup, refresh, deactivation, timeout scanning, and connection-manager daemon behavior.

## Important APIs, Types, And Functions
Public functions are `kefalnd_lookup_or_init_conn()`, `kefalnd_lookup_conn()`, `kefalnd_handle_conn_establishment()`, `kefalnd_deactivate_conn()`, `kefalnd_destroy_conn()`, `kefalnd_cm_daemon()`, `kefalnd_add_ni_to_cm_daemon()`, and `kefalnd_del_ni_from_cm_daemon()`. Internal helpers send connection probe/probe response/request/request ack messages, select data QPs, create AHs, create connections, initialize peer data QPs, refresh responder connections after epoch changes, and clean up timed-out TXs.

## Control Flow
Initiator lookup first searches the per-NI connection hash; on miss it creates a connection and calls `kefalnd_establish_conn()`. Small NIDs perform TCP metadata discovery through `kefalnd_find_remote_peer_ni()` before creating an address handle; large NIDs extract GID and CM QP data directly. Non-loopback initiators send an EFA probe, process probe response/version negotiation, send a connection request with data QPs, and become active after request ack. Responders are created on incoming probes, validate protocol support, record peer epoch/caps, send probe response, process connection request data QPs, become active, and send request ack. Active connection TX queues are posted when the state changes to active.

## State, Persistence, And Dependencies
Connections are stored in `efa_ni->conns` under `conn_lock`, keyed by XOR-derived NID hash. Each connection owns state, AH, peer QP array, remote epoch/caps, pending/active/abort TX lists, type, and optional peer-NI reference. Cleanup candidates are moved to `efa_ni->cleanup_conns`; the CM daemon scans every second and performs idle scans every fifth iteration. There is no persistence beyond kernel memory, but epochs are used to detect peer restart/stale connections.

## Integration Points
The file relies on message layout from `efalnd_proto.h`, TX posting and completion helpers from `efalnd.c`, peer metadata from `efalnd_peerni.c`, LNet timeout/tunable values, RDMA address-handle creation, and large/small NID helpers from `efalnd.h`.

## Risks
Connection state transitions happen under a mix of NI rwlock and per-connection spinlock, so lock ordering is critical. The hash key is not a full equality key; lookup also compares full NID, but deactivating connections are reinserted with hash key zero for daemon cleanup. Protocol downgrade is only handled on `-EPROTONOSUPPORT`; other probe failures destroy the connection. Timeout cleanup manipulates TX refs to avoid deadlock, which is fragile under concurrent completions. `RESP_CONN_EXTRA_TIME` means responder connections live longer than initiators and must be tested for stale cleanup.

## Test Signals
Tests should cover initiator and responder handshakes, loopback connection activation, small-NID TCP metadata discovery, large-NID direct metadata, protocol downgrade/no-overlap failure, epoch refresh replacing responder connections, pending TX posting after activation, idle timeout cleanup, TX timeout abort, concurrent lookup/create races, and module shutdown draining daemon lists.

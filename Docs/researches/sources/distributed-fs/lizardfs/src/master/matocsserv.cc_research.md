# sources/distributed-fs/lizardfs/src/master/matocsserv.cc

## Purpose

`matocsserv.cc` implements the master-to-chunkserver service. It owns the listening socket for `MATOCS_LISTEN_HOST`/`MATOCS_LISTEN_PORT`, accepts chunkserver connections only while this metadata server is master, tracks connected chunkservers, ingests their registration/space/chunk-status packets, and emits chunk operation packets requested by the chunk subsystem. The file was read as a complete 1851-line implementation.

## Important APIs, Types, and Functions

The central private type is `matocsserventry`, which stores socket state, poll position, timers, protocol input/output queues, advertised chunkserver address/version/label/space counters/load factor, operation counters, and the associated `csdbentry`. Publicly exported functions include placement/state queries (`matocsserv_getservers_sorted`, `matocsserv_getservers_for_new_chunk`, `matocsserv_getservers_lessrepl`, `matocsserv_getspace`, `matocsserv_getlocation`, counter getters), chunk operation senders (`matocsserv_send_createchunk`, `matocsserv_send_deletechunk`, `matocsserv_send_replicatechunk`, `matocsserv_send_liz_replicatechunk`, `matocsserv_send_setchunkversion`, `matocsserv_send_duplicatechunk`, `matocsserv_send_truncatechunk`, `matocsserv_send_duptruncchunk`), registration/status handlers, and event-loop hooks (`matocsserv_init`, `matocsserv_reload`, `matocsserv_desc`, `matocsserv_serve`, `matocsserv_term`). The local replication database uses `repsrc`, `repdst`, `rephash`, and free lists to count in-flight read/write replication pressure per chunkserver.

## Control Flow

Initialization reads config, opens a nonblocking listening socket, initializes replication tracking, and registers reload/destruct/poll callbacks. Poll descriptor creation adds the listener and every connected chunkserver, adding `POLLOUT` when output packets are queued. Service flow accepts new sockets only if `metadataserver::isMaster()`; each accepted entry starts with wildcard label, zeroed space, default timeout, and an unresolved `csdb` pointer. Reads accumulate `InputPacket` data until a full packet arrives, dispatch through `matocsserv_gotpacket`, and reset the parser. Writes drain queued `OutputPacket`s. Idle connections receive NOPs and stale reads time out. Killed entries are removed after notifying replication tracking, chunk state (`chunk_server_disconnected`), and chunkserver DB.

Incoming packet dispatch covers legacy MooseFS and LizardFS packet variants. Registration has old single-packet forms, versioned 1-4 forms, legacy version-5 phased packets, and LizardFS typed packets for host/chunks/space/label. Chunk reports update chunk metadata through `chunk_server_has_chunk`, `chunk_damaged`, and `chunk_lost`. Operation status packets are deserialized according to peer version and packet version, then forwarded to `chunk_got_*_status` callbacks.

## State and Persistence Behavior

The service keeps only runtime state: linked-list connection records, per-connection output queues, in-flight replication hash entries, and socket/config globals. Durable metadata changes happen indirectly in the chunk subsystem when chunkserver inventories and operation statuses update chunk placement. Space, label, and load state influence future placement but are refreshed from chunkserver packets and lost on process restart. The `csdb` integration preserves cross-connection chunkserver identity while the master is running.

## Dependencies and Integration Points

Key dependencies are event loop registration, socket helpers, `InputPacket`/`OutputPacket`, protocol namespaces `matocs` and `cstoma`, LizardFS version gates, `slice_traits`/`Goal` for standard/XOR/EC chunk parts, `master/chunks.h`, `chunkserver_db`, `filesystem` goal definitions, `GetServersForNewChunk`, media labels, and metadata-server personality. It is a high-impact integration point for chunk creation, deletion, replication, truncation, duplicate/duptrunc operations, EC compatibility, label-aware placement, avoiding same-IP placement, and chunkserver UI/status exports.

## Risks and Edge Cases

Protocol compatibility branches are dense and version-sensitive; wrong packet version handling can corrupt chunk type interpretation, especially around XOR/EC parts. Several malformed packets kill the connection, so boundary-size tests matter. Replication counters rely on begin/end/disconnect symmetry; missed status or duplicate operations can skew placement pressure. Placement depends on space values, load factor penalty, labels, history, and random shuffling, which makes deterministic regression testing harder. The service rejects localhost-advertised chunkservers and duplicate `csdb` connections. Output queues are unbounded per connection aside from operation flow control. Some state is manually allocated/free-listed, so disconnect cleanup and error paths are memory-risk areas.

## Test Signals

Useful signals include packet round-trip and malformed packet tests for legacy, XOR, and EC variants; integration tests where chunkservers register in phased and LizardFS packet modes; placement tests for labels, same-IP avoidance, load factor, full servers, and minimum version gates; replication counter tests for success, failure, duplicate, and disconnect paths; event-loop smoke tests for timeout/NOP/reload behavior; and cluster tests that verify chunk metadata reacts correctly to create/delete/replicate/truncate statuses.

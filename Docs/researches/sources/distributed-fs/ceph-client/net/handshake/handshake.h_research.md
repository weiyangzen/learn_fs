<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/handshake.h -->
# sources/distributed-fs/ceph-client/net/handshake/handshake.h

## Purpose
Internal header for the generic handshake service, defining per-net state, request lifetime structures, protocol callbacks, flag bits, and cross-file function declarations.

## APIs, Types, and Functions
Defines `struct handshake_net`, `struct handshake_req`, `struct handshake_proto`, flag enums for network, request, and protocol state, and declarations for alert, netlink, and request helpers. Key fields include `hn_pending`, `hn_pending_max`, `hn_requests`, `hr_list`, `hr_rhash`, `hr_flags`, `hr_proto`, `hr_sk`, `hr_odestruct`, and flexible private storage `hr_priv`.

## Control Flow, State, and Persistence
No executable logic is present, but the header encodes lifecycle invariants. A `handshake_req` is owned by a protocol, maps one-to-one to a socket through the rhashtable, may sit on a per-net pending list before userspace accepts it, stores the original socket destructor for restoration/chaining, and carries protocol-private data at the end. Protocols provide accept, done, and optional destroy callbacks plus a handler class and notification flag.

## Dependencies and Integration
Shared by `alert.c`, `netlink.c`, `request.c`, `tlshd.c`, `trace.c`, and tests. It bridges internal implementation with exported public handshake APIs in `include/net/handshake.h`.

## Risks and Test Signals
Risks include flag misuse causing double completion, callback contracts not being honored by protocol implementations, private size overflow, and inconsistent list/hash lifetime. Test signals are allocation validation, hash lookup, single completion semantics, socket destructor chaining, per-net draining, and protocol-private data access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/handshake.h -->

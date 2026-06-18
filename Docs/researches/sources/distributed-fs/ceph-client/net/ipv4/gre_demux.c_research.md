# sources/distributed-fs/ceph-client/net/ipv4/gre_demux.c

## Purpose
`gre_demux.c` registers IPv4 GRE as an inet protocol and demultiplexes GRE packets to version-specific GRE protocol handlers. It also exports the common GRE header parser used by tunnel implementations.

## Important APIs, Types, And Functions
`gre_proto[GREPROTO_MAX]` stores RCU-protected version handlers. Exported APIs are `gre_add_protocol`, `gre_del_protocol`, and `gre_parse_header`. Runtime callbacks are `gre_rcv` and `gre_err`, installed through `net_gre_protocol` with `inet_add_protocol(IPPROTO_GRE)`.

## Control Flow
Modules register a `struct gre_protocol` for a GRE version with `gre_add_protocol`; cmpxchg prevents duplicate registration. Removal uses cmpxchg and then `synchronize_rcu` before returning. Receive checks that enough packet data exists, extracts the low 7 bits of the GRE version byte, looks up the handler under RCU, and either delegates or drops while updating no-handler/drop stats. Error handling similarly extracts the GRE version from the embedded packet and invokes the registered `err_handler`.

`gre_parse_header` validates base header presence, rejects unsupported version/routing flags, converts GRE flags to tunnel flags, calculates full header length, validates checksum when present, extracts optional key and sequence fields, handles WCCP protocol quirks, stores final header length, and for ERSPAN derives the session id into `tpi->key`.

## State And Persistence
The only persistent state is the global RCU handler array. It is module-wide rather than per-netns. Registration lasts until the owning GRE tunnel module removes its protocol.

## Dependencies And Integration Points
The file integrates with inet protocol dispatch, GRE tunnel modules, ERSPAN helpers, skb checksum helpers, route/ICMP error handling, netdevice stats, and module init/exit. It exports parser functionality to other GRE users.

## Risks
Header parsing is sensitive to short packets and option length calculations. A handler registration race could send packets to the wrong module if RCU synchronization were missing. WCCP and ERSPAN special cases can alter protocol/key interpretation and need compatibility coverage. Error path version extraction assumes enough embedded header data for the calling context.

## Test Signals
Exercise GRE version registration conflicts, deregistration under traffic, receive with no handler, malformed short headers, checksum pass/fail, GRE key/sequence parsing, WCCP v1/v2 adjustment, ERSPAN key derivation, and ICMP error callback routing.

# sources/distributed-fs/ceph-client/net/ipv4/protocol.c

## Purpose
Owns IPv4 protocol and offload dispatch tables. Provides registration helpers for transport protocols and offload implementations by IP protocol number.

## Important APIs, types, and functions
Global exported arrays are `inet_protos[MAX_INET_PROTOS]` and `inet_offloads[MAX_INET_PROTOS]`. Exported functions are `inet_add_protocol()`, `inet_del_protocol()`, `inet_add_offload()`, and `inet_del_offload()`.

## Control flow
Add functions use `cmpxchg()` to install a handler only into an empty slot, returning zero or `-1`. Delete functions clear the slot only if it matches the supplied pointer, then call `synchronize_net()` so in-flight readers finish before callers free handler code/data.

## State and persistence
The dispatch arrays are global kernel state. There is no per-net state. Handler pointers are RCU-style published and remain valid until after deletion synchronization.

## Dependencies and integration points
Integrates with IPv4 receive dispatch and protocol/offload modules such as TCP, UDP, ICMP, raw, GRE, and GRO/offload handlers. Depends on atomic compare-exchange and network RCU synchronization.

## Risks
The API returns `-1` rather than errno. Deletion with the wrong pointer leaves stale registrations. Removal synchronization is required for module unload safety.

## Test signals
Test duplicate registration, deletion with matching/nonmatching pointers, module unload under traffic, offload registration collisions, and receive behavior before/after registration.

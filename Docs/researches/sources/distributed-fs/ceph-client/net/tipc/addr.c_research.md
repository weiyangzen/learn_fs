# sources/distributed-fs/ceph-client/net/tipc/addr.c

## Purpose
This file implements TIPC address and node identity helper routines used by core, netlink, discovery, and socket paths.

## Important APIs, Types, And Functions
Functions are `tipc_in_scope()`, `tipc_set_node_id()`, `tipc_set_node_addr()`, and `tipc_nodeid2string()`. They operate on `struct tipc_net` fields declared in `core.h`: `node_id`, `node_id_string`, `node_addr`, `trial_addr`, `addr_trial_end`, `legacy_addr_format`, and `net_id`.

## Control Flow
Scope checking treats empty or exact domains as matching, rejects non-exact domains in non-legacy format, and in legacy format accepts cluster or zone masks. Node ID setting copies a 16-byte ID, renders it to a printable string, derives a trial address via `hash128to32()`, and logs identity. Node address setting stores the numeric address, synthesizes an ID from the address if no ID exists, updates trial address/end time, and logs. ID string rendering preserves already printable IDs and otherwise converts bytes to hex while stripping trailing zeroes.

## State And Persistence
All state is per network namespace in `struct tipc_net` and in memory only. Identity persists for the lifetime of the namespace or until reconfigured.

## Dependencies And Integration Points
The file depends on `addr.h`, `core.h`, TIPC address masks, jiffies, logging, and `hash128to32()`. It integrates with bearer autoconfiguration and net initialization.

## Risks And Test Signals
Risks include legacy address matching accepting unintended domains, printable ID detection ambiguity, and hash-derived trial address collisions. Test signals include scope unit tests for legacy and modern formats, node ID string conversion for binary and printable IDs, bearer autoconfiguration from L2 addresses, and netlink-visible node identity updates.

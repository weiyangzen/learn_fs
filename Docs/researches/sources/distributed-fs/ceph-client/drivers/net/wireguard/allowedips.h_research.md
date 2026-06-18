# sources/distributed-fs/ceph-client/drivers/net/wireguard/allowedips.h

## Purpose
`allowedips.h` declares WireGuard's allowed-IPs trie structures and public operations for initialization, mutation, lookup, readback, and slab-cache lifecycle.

## Important APIs, Types, And Functions
`struct allowedips_node` contains an RCU peer pointer, two RCU child pointers, prefix metadata (`cidr`, bit offsets, bit length, aligned bits buffer), a packed parent pointer/bit, and a union used as either peer-list entry or RCU callback. `struct allowedips` contains IPv4 and IPv6 roots plus a sequence counter and is explicitly aligned because low pointer bits are packed elsewhere. Function declarations cover insert/remove for v4/v6, remove by peer, node readback, destination/source lookup returning strong peer references, debug selftest, and slab init/uninit.

## Control Flow
The header does not implement control flow, but its API establishes the contract: callers initialize a table, mutate it under a mutex, use lookups in packet paths, and free the table while holding the same lock. Readback expects aligned IP output storage.

## State And Persistence
The declared structures are in-memory only. The sequence field lets callers detect route-table changes. Node lifetime is RCU-managed after removal.

## Dependencies And Integration Points
The header includes mutex, IPv4, and IPv6 kernel headers and forward-declares `struct wg_peer`. It is used by WireGuard peer, netlink, send, and receive paths to enforce allowed IP routing and anti-spoofing.

## Risks
The packed parent pointer design means structure alignment is not incidental; changes to `struct allowedips` or allocation alignment must preserve low-bit availability. The union of list and RCU head requires nodes not be on peer lists once scheduled for RCU free. API users must observe the documented strong-reference return from lookups and release peers accordingly.

## Test Signals
Compile with DEBUG to expose `wg_allowedips_selftest()`, verify structure alignment on supported architectures, run netlink add/remove peer allowed-IP tests, and use KASAN/KCSAN/RCU debugging around remove/free paths.

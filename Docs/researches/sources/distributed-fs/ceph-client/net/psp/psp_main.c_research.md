# sources/distributed-fs/ceph-client/net/psp/psp_main.c

## Purpose
`psp_main.c` implements the core PSP device registry, driver-facing device create/unregister APIs, PSP key size helper, packet encapsulation, packet receive decapsulation, and subsystem initialization. PSP here is UDP-encapsulated TCP protection metadata with driver-managed crypto/key operations.

## Important APIs, types, and functions
Global registry state is `DEFINE_XARRAY_ALLOC1(psp_devs)` and `psp_devs_lock`. Driver APIs include `psp_dev_create()`, `psp_dev_unregister()`, and the internal finalizer `psp_dev_free()`. Visibility checking is `psp_dev_check_access()`. `psp_key_size()` maps PSP versions to AES-GCM/GMAC key sizes.

Packet transmit helpers are `psp_dev_encapsulate()` and private `psp_write_headers()`. Receive helper is `psp_dev_rcv()`. Initialization is `psp_init()`, which initializes the global mutex and registers the generated generic netlink family.

## Control flow and state
`psp_dev_create()` validates mandatory driver capability/operation callbacks, allocates and initializes `struct psp_dev`, assigns a cyclic 16-bit id in `psp_devs`, locks the instance, notifies netlink listeners of device add, publishes `netdev->psp_dev` with RCU, and returns with a refcount of one. `psp_dev_unregister()` takes global then instance locks, notifies delete, stores NULL in the xarray to prevent id reuse while references remain, moves active/previous associations to stale, deletes TX keys for stale associations, clears the netdev RCU pointer, nulls ops/private data to mark unregistered, unlocks, and drops the device reference. `psp_dev_free()` erases the id and frees via RCU after the final put.

`psp_dev_encapsulate()` grows headroom by `PSP_ENCAP_HLEN`, moves the Ethernet/IP header earlier, changes IPv4/IPv6 next protocol to UDP, updates lengths and IPv4 checksum, marks inner TCP metadata, sets encapsulation, and writes UDP/PSP headers. `psp_write_headers()` chooses a UDP source port from the socket hash and local port range when a socket is present, otherwise uses `udp_flow_src_port()`, then writes destination port, UDP length, and fixed PSP header fields.

`psp_dev_rcv()` validates Ethernet/VLAN plus IPv4/IPv6 plus UDP PSP default port, validates linear header availability, computes full PSP header length from `hdrlen`, adds `SKB_EXT_PSP`, records SPI/dev id/generation/version, updates outer IP next header and length to the protected inner protocol, moves L2/L3 headers to remove UDP+PSP headers, pulls the skb, and optionally strips the trailing ICV.

## State and persistence behavior
Device registry state is in-memory, global, xarray-backed, and RCU/refcount protected. PSP device registered/unregistered state is represented by `psd->ops` under `psd->lock` and `netdev->psp_dev` RCU pointer. Associations are list-based under the device lock. Packet metadata persists only in skb extensions for received packets.

## Dependencies and integration points
The file integrates with netdevice `psp_dev` pointers, generic netlink family from `psp-nl-gen.c`, PSP UAPI/public structs from `net/psp.h`, UDP/IP helpers, socket port range/hash logic, skb extensions, xarray, RCU, and driver callback interfaces for configuration, key rotation, SPI allocation, TX key add/delete, and stats.

## Risks and edge cases
Key risks are device lifetime and id reuse during unregister, lock ordering, encapsulation headroom/header movement bugs, IPv4/IPv6 length/checksum correctness, unsupported protocols, malformed PSP header lengths, CHECKSUM_COMPLETE limitations, and `pskb_trim()` failure handling on ICV strip. Receive accepts only already-authenticated packets by contract, so callers must enforce authentication before `psp_dev_rcv()`.

## Test signals
Test driver registration validation, cyclic id allocation, netlink add/delete notifications, unregister with active associations, refcount/RCU lifetime under concurrent netlink operations, `psp_key_size()` for all versions, IPv4 and IPv6 encapsulation byte layout, UDP source port stability per TCP flow, receive decapsulation with VLAN, optional PSP header length, ICV stripping, malformed protocol/port/header cases, and skb extension contents.

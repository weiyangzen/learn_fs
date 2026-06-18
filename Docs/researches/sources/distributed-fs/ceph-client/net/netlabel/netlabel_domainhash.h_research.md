# sources/distributed-fs/ceph-client/net/netlabel/netlabel_domainhash.h

## Purpose
Internal data model and API for NetLabel domain hash mappings.

## Important APIs, Types, And Functions
Defines `NETLBL_DOMHSH_BITSIZE`, address selector containers `netlbl_domaddr_map`, `netlbl_domaddr4_map`, `netlbl_domaddr6_map`, generic mapping union `netlbl_dommap_def`, and top-level `netlbl_dom_map`. Declares initialization, add/remove, default remove, IPv4/IPv6 selector removal, direct and address-specific lookups, and `netlbl_domhsh_walk()`.

## Control Flow
Callers allocate and populate `netlbl_dom_map` and optional selector lists, then transfer ownership to `netlbl_domhsh_add()`. Lookup callers are expected to hold RCU read protection. Remove APIs select whole-domain or family/address-specific paths.

## State And Persistence Behavior
The structs define ownership-sensitive persistent state: `domain` strings, DOI pointers, selector lists, `valid` flags, RCU heads, and list links. The header exposes that entries are RCU-managed and that selector definitions embed address-list nodes.

## Dependencies And Integration Points
Includes RCU/list primitives and `netlabel_addrlist.h`. It is shared by NetLabel KAPI, management netlink, CIPSO/CALIPSO DOI cleanup, and unlabeled default setup.

## Risks And Test Signals
Risks include callers misunderstanding ownership transfer, missing RCU read locks, and conditional IPv6 declaration drift. Test signals are sparse/RCU annotations, compile coverage with IPv6 toggled, and KAPI/management add-remove round trips.

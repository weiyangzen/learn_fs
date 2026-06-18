# sources/distributed-fs/ceph-client/net/netlabel/netlabel_kapi.c

## Purpose
Kernel-facing NetLabel API. It provides configuration helpers for LSMs/protocol engines, category bitmap utilities, socket/request/sk_buff labeling operations, cache management, audit entry points, and subsystem initialization.

## Important APIs, Types, And Functions
Configuration APIs include `netlbl_cfg_map_del()`, unlabeled map/static add/remove, CIPSO/CALIPSO DOI add/remove/map add. Category helpers include `netlbl_catmap_walk()`, `walkrng()`, `getlong()`, `setbit()`, `setrng()`, `setlong()`. Bitmap helpers are `netlbl_bitmap_walk()` and `netlbl_bitmap_setbit()`. Runtime APIs include `netlbl_enabled()`, socket/request/connection/sk_buff set/get/delete operations, `netlbl_skbuff_err()`, cache invalidate/add, and `netlbl_audit_start()`. `netlbl_init()` wires the subsystem at `subsys_initcall`.

## Control Flow
Config map helpers allocate domain entries or selector maps, take DOI references, and transfer ownership to the domain hash. Socket and packet label setters look up the domain and destination address under RCU, then dispatch to CIPSOv4, CALIPSO, or unlabeled deletion/no-op behavior. Receive-side `netlbl_skbuff_getattr()` tries packet-provided labels first and falls back to static unlabeled mappings. Init builds the domain hash, unlabeled hash, netlink families, and default unlabeled allow policy, panicking on failure.

## State And Persistence Behavior
Persistent state lives mostly outside this file: domain hash mappings, DOI registries, protocol caches, and unlabeled static maps. Locally, category maps are caller-owned linked bitmap chunks. `netlbl_enabled()` reflects global `netlabel_mgmt_protocount`.

## Dependencies And Integration Points
Integrates LSM callers with `net/cipso_ipv4.h`, CALIPSO wrappers, Generic Netlink setup, unlabeled fallback, address-list helpers, audit, RCU, and socket/sk_buff internals. Several exported symbols are used by security modules and protocol engines.

## Risks And Test Signals
Risks include GFP_ATOMIC allocation failures, incorrect address-family dispatch, missing socket locks, catmap range overflow, protocol count drift, and init-time panic on netlink or default-config failure. Test signals should cover config API round trips, IPv4/IPv6 address selectors, catmap sparse/range operations, lockdep for socket paths, receive fallback to unlabeled, cache add only when `NETLBL_SECATTR_CACHE` is set, and boot init logs.

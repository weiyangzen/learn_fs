# sources/distributed-fs/ceph-client/include/linux/ceph/osdmap.h

## Purpose

`osdmap.h` declares the in-kernel representation and mapping helpers for Ceph OSD maps. OSD maps describe cluster membership, pool settings, CRUSH placement, temporary/upmap overrides, OSD addresses, and epoch-based changes.

## Important APIs, Types, and Functions

Key types are `ceph_pg`, `ceph_spg`, `ceph_pg_pool_info`, `ceph_object_locator`, `ceph_object_id`, `workspace_manager`, `ceph_pg_mapping`, `ceph_osdmap`, `ceph_osds`, `crush_loc`, and `crush_loc_node`. APIs include PG/SPG comparison, object locator and object id lifecycle helpers, map allocation/decode/incremental-apply/destroy, OSD state helpers, PG decode, PG split and interval-change checks, object-to-PG mapping, PG-to-acting/up OSD mapping, CRUSH location parsing/comparison, and pool lookup helpers.

## Control Flow

Monitor-delivered maps are decoded as full maps or incremental updates. OSD client request targeting calls object locator to PG mapping, then CRUSH/upmap/temp mapping to up/acting sets and primary selection. Map change helpers decide whether a request is in a new interval and must be resent.

## State and Persistence Behavior

`ceph_osdmap` stores FSID, epoch, timestamps, flags, OSD state/weight/address arrays, pool RB tree, temp/upmap RB trees, primary affinity, CRUSH map, and workspace manager. Object locators may own `ceph_string` namespace refs, and object ids may use inline or allocated name storage.

## Dependencies and Integration Points

It depends on RB trees, Ceph decode helpers, Ceph types, and CRUSH. It integrates with monitor map handling and OSD client targeting/resend logic.

## Risks and Edge Cases

Map decoding is untrusted input and must validate bounds and versions. Object ids can contain embedded NULs and must use length, not C-string assumptions. Pool type controls OSD shifting; unknown types `BUG()`. Incremental maps must preserve epoch monotonicity and free replaced dynamic state.

## Test Signals

Decode full and incremental maps, fuzz truncated map data, test object id inline/external transitions, namespace ref lifecycle, CRUSH/upmap/temp mapping, PG split detection, interval-change decisions, pool lookup, and CRUSH location parsing.

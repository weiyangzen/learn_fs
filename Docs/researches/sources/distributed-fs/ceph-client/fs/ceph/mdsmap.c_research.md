<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/mdsmap.c -->
# sources/distributed-fs/ceph-client/fs/ceph/mdsmap.c

## Purpose
`mdsmap.c` decodes CephFS MDS map messages into the kernel client's compact `ceph_mdsmap` representation. It also provides helper behavior for choosing an available MDS, destroying decoded maps, and determining whether the metadata cluster is usable for mounting and request routing.

## Important APIs, types, and functions
The main exported functions are `ceph_mdsmap_get_random_mds`, `ceph_mdsmap_decode`, `ceph_mdsmap_destroy`, and `ceph_mdsmap_is_cluster_available`. Internal helpers include `__mdsmap_get_random_mds`, `__decode_and_drop_compat_set`, and macros that skip unused scalar, set, and map encodings while still validating bounds.

`ceph_mdsmap_decode` fills fields such as map epochs, root rank, session timeout/autoclose, max file size, max xattr size, max MDS count, number of active MDS ranks, possible max rank, per-rank `ceph_mds_info`, data pools, CAS pool, enabled/damaged/laggy status, filesystem name, and export targets.

## Control flow
Map decoding starts by reading the MDS map version and optional length wrapper, then fixed legacy fields. It allocates `m_info` based on the larger of actual active ranks and configured max MDS ranks so transient replacement states can still address higher ranks. For each encoded MDS info item, it decodes global id, rank, incarnation, state, address or address vector, laggy timestamp, and export targets. Only valid positive-state ranks within range are copied into the map.

After active MDS info, the decoder reads data pool ids and skips many server-side fields the kernel client does not need. It still tracks the `in` set to count laggy active ranks and may expand `m_info` to the size of that set. Later encoding versions provide enabled state, filesystem name validation against the mount namespace, damaged ranks, required-client-feature fields to skip, and max xattr size. On success the decode cursor is advanced to the map end; on corruption it logs a hex dump, destroys partial allocations, and returns an error pointer.

Random MDS selection counts ranks with positive state and, on the first pass, excludes laggy ranks. If none are usable, it retries while ignoring laggy status. Cluster availability requires the map to be enabled, not damaged, not entirely laggy, and to contain at least one active rank.

## State and persistence behavior
Decoded maps are heap objects swapped into `mdsc->mdsmap` by `mds_client.c`. They persist until superseded by a newer map or mount teardown, then `ceph_mdsmap_destroy` frees export-target arrays, MDS info, data pools, filesystem name, and the map itself. No map is persisted locally; monitor subscriptions provide fresh maps.

## Dependencies and integration points
This file depends on Ceph decode helpers, messenger address decoding, random number helpers, slab allocation, MDS state string helpers, mount namespace matching, and client logging. It is used by request routing, session opening, metrics sending, cap renewal, reconnect, mount availability checks, and MDS map update handling in `mds_client.c`.

## Risks and test signals
Risks include protocol-version drift, bounds-check mistakes in skipped fields, integer overflow in allocation or skip lengths, accepting invalid ranks or states, filesystem name mismatches causing mount failure, laggy-rank availability edge cases, and export-target decoding errors that would break reconnect during migration/failover. Test signals include decoding old and new map versions, msgr1 and msgr2 address vectors, maps with active ranks above `m_max_mds`, laggy-only maps, damaged maps, disabled filesystems, wrong fs names, empty data-pool lists, export-target reconnect scenarios, and truncated/corrupt map payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/mdsmap.c -->

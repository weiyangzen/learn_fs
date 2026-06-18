# sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_internal.h

## Purpose
`nodemap_internal.h` is the private contract shared by the nodemap implementation files in `ptlrpc`. It defines internal constants and data structures for NID ranges, ID maps, fileset records, alternate filesets, and declares the cross-file APIs used by handler, range, idmap, member, lproc, fileset-alt, and storage code.

## Important APIs, types, and declarations
Important constants are `DEFAULT_NODEMAP`, `NODEMAP_NOBODY_UID/GID/PROJID`, and `NODEMAP_FILESET_PRIM_ID`. External globals are `proc_lustre_nodemap_root`, `nodemap_active`, `active_config_lock`, and `active_config`.

Important structures are `struct lu_nid_range` for regular/ban NID ranges and dynamic subtrees, `struct lu_idmap` for bidirectional ID mapping nodes, `struct lu_nodemap_fileset_info` for IAM fileset persistence payloads, and `struct lu_fileset_alt` for alternate fileset rbtrees. Inline helpers split/compose nodemap index IDs, compare range inclusion, and detect the default nodemap.

The declarations expose lifecycle/config functions, lookup, debugfs registration, range and ban-range operations, idmap operations, alternate fileset helpers, member add/delete/reclassify/revoke, handler helper functions, MGS/loading predicates, and all persistence-layer `nodemap_idx_*()` entry points.

## Control flow and behavior
The header establishes ownership boundaries: handler owns high-level policy, range owns interval-tree operations, idmap owns ID rbtrees, member owns live export membership and revocation, lproc owns debugfs presentation, and storage owns IAM persistence. The `nodemap_lookup` macro still aliases `nodemap_lookup_locked()` for compatibility, so callers must still reason about `active_config_lock`.

## State and persistence
The header does not store state directly, but it defines runtime and persistent identity fields: range IDs, index type bits, fileset fragment metadata, and persistence APIs for nodemap records, roles, offsets, filesets, capabilities, ranges, ID maps, activation, and index reads.

## Dependencies and integration points
It depends on libcfs hash support, Lustre nodemap/disk definitions, Linux rbtrees, LNet NID types, procfs/debugfs types, and Lustre export/config structures through included or transitive headers. All researched nodemap implementation files include it.

## Risks and edge cases
Changing these structures can break multiple files at once. `START()` and `LAST()` convert to NID4, so large-NID paths must avoid them unless already checked. The `nodemap_lookup` macro can obscure lock requirements and should be reviewed carefully in new call sites.

## Test signals
Build coverage detects declaration drift. Runtime signals should cover range insertion/search, large-NID matching, idmap lookup, fileset IAM operations, dynamic inheritance, debugfs registration/removal, config replacement, and lockdep coverage for functions with documented lock requirements.

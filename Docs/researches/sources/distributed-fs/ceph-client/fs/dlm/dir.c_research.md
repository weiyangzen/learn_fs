# sources/distributed-fs/ceph-client/fs/dlm/dir.c

## Purpose
`dir.c` implements the DLM resource directory: mapping a resource-name hash to a directory node, recovering directory records after membership changes, and serving batched lists of resource names mastered by the local node. The directory lets non-master nodes discover the current master node for a resource without broadcasting every lookup.

## Important APIs and Functions
- `dlm_hash2nodeid()` maps a jhash value to a node id using `ls_total_weight` and `ls_node_array`; single-node lockspaces short-circuit to `dlm_our_nodeid()`.
- `dlm_dir_nodeid()` returns `r->res_dir_nodeid`.
- `dlm_recover_dir_nodeid()` recomputes directory ownership for each RSB in a recovery root list.
- `dlm_recover_directory()` queries every other member for master resource names, then calls `dlm_master_lookup(..., DLM_LU_RECOVER_DIR, ...)` to rebuild local directory records.
- `dlm_copy_master_names()` services remote `DLM_RCOM_NAMES` requests by copying name-length/name records for resources mastered locally and whose directory node is the requester.
- The private `struct dlm_dir_dump` tracks a multi-message dump cursor and sanity information while a requester pages through names.

## Control Flow
Normal resource lookup starts outside this file in `lock.c`: a name is hashed, `dlm_hash2nodeid()` selects the directory node, and a lookup message is sent if the local RSB does not already know the master. During recovery, `dlm_recover_directory()` loops over members, asks each for names after the last returned name, parses `__be16` length prefixes from `ls_recover_buf`, and terminates on either zero-length end-of-buffer or `0xFFFF` end-of-node sentinel. Each received name is reconciled through `dlm_master_lookup()` using the sender as the asserted master.

`dlm_copy_master_names()` walks `ls_masters_list` under `ls_masters_lock`. For a fresh dump it allocates a `dlm_dir_dump` context, records the current recovery sequence, and starts at the head of the masters list. For a continuation it finds the previous RSB by name and resumes after its `res_masters_list` entry. It emits records until the output buffer lacks room for another name plus a terminator, then writes a zero-length marker; at end of list it writes `0xFFFF`, logs counts, removes the dump context, and frees it.

## State and Persistence Behavior
Directory state is kept in each RSB (`res_dir_nodeid`, `res_master_nodeid`, `res_masters_list`) and in the lockspace dump list (`ls_dir_dump_list`). It is not persistent across module unload or lockspace destruction. During recovery the directory is reconstructed from live peer state, using `ls_recover_seq` to detect stale continuation requests. The dump context is per requester node and is dropped/replaced if the same node starts another dump before finishing.

## Dependencies and Integration Points
`dir.c` depends on membership (`member.h`), recovery communication (`rcom.h`), low/mid communication state, config, recovery status helpers, and `lock.c` master lookup/search functions. It is called by recovery orchestration to rebuild directory ownership and by RCOM handlers to fill `DLM_RCOM_NAMES_REPLY` payloads.

## Risks
- Directory recovery trusts remote name dumps enough to create or update local directory records, so length validation and sentinel parsing are essential. The code checks buffer bounds and `DLM_RESNAME_MAXLEN`.
- `find_rsb_root()` falls back from rhashtable lookup to `ls_masters_list`; this covers recovery races but means stale list membership would affect dump continuation.
- Multi-message dump cursors are keyed only by requester node; overlapping dumps from the same node intentionally drop the older context.
- The weighted node array must be correctly built by membership code. A bad `ls_total_weight`/`ls_node_array` relationship would misplace directory ownership.

## Test Signals
- Unit-style recovery tests should verify hash-to-node stability for single-node and weighted multi-node lockspaces.
- Recovery tests can force resource masters on several nodes and confirm `dlm_recover_directory()` adds missing directory records and logs mismatched masters.
- RCOM name dump tests should cover exact-buffer-fit, continuation, zero-length block terminator, and `0xFFFF` final terminator behavior.
- Fault tests should inject oversized or truncated name records and expect `-EINVAL` recovery failure rather than out-of-bounds parsing.

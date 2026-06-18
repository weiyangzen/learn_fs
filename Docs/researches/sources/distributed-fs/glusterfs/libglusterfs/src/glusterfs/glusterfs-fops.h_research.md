# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/glusterfs-fops.h

## Purpose
Defines stable enums and small protocol structures for GlusterFS filesystem operations, translator events, lock commands/types, lease commands/types, xattrop operations, seek modes, upcall flags, and dictionary data types.

## APIs, Types, and Functions
`glusterfs_fop_t` enumerates all FOP IDs from `GF_FOP_NULL` through `GF_FOP_COPY_FILE_RANGE` and `GF_FOP_MAXVALUE`. `glusterfs_event_t` enumerates parent/child, poll, cleanup, transport, graph, auth, defrag, barrier, upcall, scrub, ping, and signal events. Other enums include `gf_op_type_t`, `glusterfs_lk_cmds_t`, `glusterfs_lk_types_t`, `gf_lease_types_t`, `gf_lease_cmds_t`, `glusterfs_lk_recovery_cmds_t`, `gf_lk_domain_t`, `entrylk_cmd`, `entrylk_type`, `gf_xattrop_flags_t`, `gf_seek_what_t`, `gf_upcall_flags_t`, and `gf_dict_data_type_t`. `gf_lease` stores lease command/type/id/flags, and `gf_lkowner_t` stores lock-owner bytes.

## Control Flow, State, and Persistence
These numeric values are protocol and logging contracts. They drive dispatch tables, FOP arrays, RPC encoding, default operation tables, and translator event switching. The structures are transient request payloads but their sizes and values affect wire compatibility.

## Dependencies and Integration
Depends on `compat.h`. Included by `glusterfs.h`, dict typing, defaults, xlator interfaces, and protocol code.

## Risks and Test Signals
Risks include renumbering enums, missing `GF_FOP_MAXVALUE` updates, array-size mismatches, lease-id length assumptions, and incompatible dict data type changes. Test signals include RPC compatibility tests, `gf_fop_list` length checks, translator dispatch compile coverage, lock/lease round trips, and rolling-upgrade tests for new FOPs.

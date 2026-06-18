# sources/distributed-fs/lustre-release/lustre/ptlrpc/nodemap_lproc.c

## Purpose
`nodemap_lproc.c` exposes nodemap runtime state through Lustre debugfs/ldebugfs files. It creates the global `nodemap` debugfs directory, per-nodemap directories, read-only views for ranges, ID maps, exports, properties, RBAC/capabilities, filesets, and a few write handlers for activation, legacy fileset setting, and SELinux policy.

## Important APIs, types, and functions
File-level state is `nodemap_pde_list` and `nodemap_root`. Public entry points are `nodemap_procfs_init()`, `nodemap_procfs_exit()`, `lprocfs_nodemap_register()`, and `lprocfs_nodemap_remove()`.

Show/open handlers print idmaps, offsets, capabilities, ranges, ban ranges, filesets, SELinux policy, exports, active flag, ID, squash IDs, trusted/admin/map-mode/RBAC/audit/encryption/raise/read-only/deny-mount/parent/GSS flags. Write handlers are `nodemap_active_seq_write()`, `nodemap_fileset_seq_write()`, and `nodemap_sepol_seq_write()`. Variable tables choose normal versus default-nodemap visible files.

## Control flow and behavior
Initialization creates `debugfs_lustre_root/nodemap` and adds the module-level `active` file. Per-nodemap registration allocates `struct nodemap_pde`, creates a child directory, stores the nodemap name as stable private data, adds ldebugfs vars, links the PDE, and stores it in `nodemap->nm_pde_data`. Name-based private data allows config reload to replace nodemap structs without rewriting debugfs entries.

Most show handlers lookup the current nodemap by name, print scalar or JSON-like data, and release the reference. Range handlers hold `active_config_lock` plus tree read locks; idmap/fileset handlers take their nodemap locks; exports take `nm_member_list_lock`. Write handlers parse bounded user input and call handler APIs.

## State and persistence
This file presents state but owns only debugfs metadata. Persistent changes happen indirectly via `nodemap_activate()`, `nodemap_set_fileset_prim_lproc()`, or `nodemap_set_sepol()`. PDEs are freed on per-nodemap removal or module exit and are transferred across config replacement by handler code.

## Dependencies and integration points
Dependencies include debugfs, ldebugfs, seq_file, nodemap lookup/setters, member/range/idmap/fileset structures, libcfs capability formatting, and OBD export data. Member code creates per-nodemap `md_stats` and `dt_stats` under these debugfs directories.

## Risks and edge cases
Output is JSON-like rather than strict JSON. Some scalar reads rely on ref lifetime rather than property-specific locks. `nodemap_procfs_init()` shadows `rc` in the failure branch, so root creation failure may be reported as success. Fileset and sepol write handlers bypass some normal permission gates for compatibility and need explicit coverage.

## Test signals
Test init/register/remove/exit, config replacement preserving entries, default versus normal file lists, empty/populated views, active write parsing, fileset write limits and invalid paths, sepol validation, failure injection around debugfs creation, and lockdep races with mutation/deletion.

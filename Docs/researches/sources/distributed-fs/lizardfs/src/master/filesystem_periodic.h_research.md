# sources/distributed-fs/lizardfs/src/master/filesystem_periodic.h

## Purpose
`filesystem_periodic.h` declares the public hooks for master periodic filesystem maintenance and reporting.

## Important APIs
`fs_get_defective_nodes_info` returns paginated defective file information filtered by requested flags. `fs_read_periodic_config_file` loads periodic scan configuration. `fs_periodic_master_init` registers maintenance callbacks. `fs_test_getdata` returns scan timing, file/chunk counters, and a report string. `fsnodes_periodic_remove` removes an inode from the defective-node map when a node is deleted.

## Control flow and integration
The header exposes only the reporting/config/init/remove surface; the actual scanning and checksum work stays private in the `.cc` file. It depends on `DefectiveFileInfo` and is included by lifecycle code, node removal, and status/report handlers.

## State and persistence behavior
The declared functions operate on static in-memory periodic scan state. They do not persist data directly, but `fs_periodic_master_init` starts maintenance paths that can mutate metadata through trash purge and async tasks.

## Risks and test signals
Callers depend on stable pagination semantics for defective nodes and stable report counters. Tests should call `fs_get_defective_nodes_info` with different flag masks and entry indexes, confirm `fsnodes_periodic_remove` clears stale entries, and verify init registers all expected event-loop callbacks in master builds.

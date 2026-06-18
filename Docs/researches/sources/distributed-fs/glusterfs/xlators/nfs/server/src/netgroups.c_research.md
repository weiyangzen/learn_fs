<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/netgroups.c -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/netgroups.c

## Purpose

`netgroups.c` parses a Gluster NFS netgroups file into dictionary-backed netgroup and host structures for export authorization. It supports nested netgroup references, host triples in `(host,user,domain)` form, lookup by netgroup name, debug printing, and cleanup of a graph where multiple dictionaries may reference the same netgroup entry. Source read: complete 1161-line file.

## Important APIs, Types, and Functions

External APIs are `ng_file_parse`, `ng_file_get_netgroup`, `ng_file_deinit`, `ng_file_print`, and `ngh_dict_get`. The main internal builders are `_ng_init_parsers`, `_netgroups_file_init`, `_netgroup_entry_init`, `_netgroup_host_init`, `_parse_ng_line`, `_parse_ng_host`, `_ng_handle_host_part`, and `_ng_setup_netgroup_entry`. Cleanup is handled by `_netgroup_entry_deinit`, `_netgroup_host_deinit`, and dict walkers such as `__ngf_free_walk`, `__nge_free_walk`, and `__ngh_free_walk`.

## Control Flow

`ng_file_parse` opens the target file, allocates a `netgroups_file`, initializes regex parsers from `netgroups.h`, then reads lines with `getline`. Comment lines beginning with `#` are skipped. Each non-comment line is passed to `_parse_ng_line`, which treats the first match as the parent netgroup and subsequent matches as either host triples or child netgroup names. Host triples are validated for two commas and no spaces, then split by `ng_host_parser`. Child netgroups are inserted into both the global file dictionary and the parent's `netgroup_ngs` dictionary, enabling direct lookup by name while preserving nested membership structure.

## State and Persistence Behavior

The parsed state is in memory only: `netgroups_file.filename`, `ng_file_dict`, and nested `dict_t` instances for each entry. The parser globals `ng_file_parser` and `ng_host_parser` are initialized during parse and deinitialized before returning. Cleanup uses a temporary global `__deleted_entries` dictionary to prevent double-free when the same `netgroup_entry` is referenced from multiple dictionaries.

## Dependencies and Integration Points

This file depends on Gluster `dict_t`, parser utilities, memory types, and NFS logging messages. It is consumed by `mount3-auth.c`, which loads netgroups into `mnt3_auth_params` and checks whether export hosts are members of authorized netgroups.

## Risks and Edge Cases

The accepted regexes are intentionally narrow and may reject otherwise valid netgroup syntax. Host parsing allows only three regex matches and stores empty user/domain as null when the regex finds no token. Lines with malformed host entries are skipped or logged depending on error severity. The global parser and `__deleted_entries` state make concurrent parsing/deinit unsafe unless externally serialized. Deep or cyclic netgroup membership handling is not resolved here; this file only builds references.

## Test Signals

Good tests parse empty files, comment-only files, direct host entries, nested netgroups, duplicate netgroup references, malformed host triples, missing files, and files with parent-only lines. Cleanup tests should run under ASAN/valgrind to catch double-free or leaks in shared-entry graphs. Auth integration tests should verify `mount3-auth.c` can find hosts through parsed nested groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/netgroups.c -->

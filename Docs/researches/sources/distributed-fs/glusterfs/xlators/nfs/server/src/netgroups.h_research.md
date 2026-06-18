<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/netgroups.h -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/netgroups.h

## Purpose

`netgroups.h` declares the in-memory representation and parser API for NFS export netgroups. It is the contract between the netgroups parser and mount authorization code. Source read: complete 53-line file.

## Important APIs, Types, and Functions

The header defines log domain `GF_NG`, parser regexes `NG_FILE_PARSE_REGEX` and `NG_HOST_PARSE_REGEX`, and structs `netgroup_host`, `netgroup_entry`, and `netgroups_file`. Public APIs are `ng_file_parse`, `ng_file_get_netgroup`, and `ng_file_deinit`; `netgroups.c` also exposes print and host-dict lookup helpers not declared here.

## Control Flow

No executable flow is present. The types describe a two-level dictionary model: a netgroups file maps names to entries, and each entry may map child netgroups and hosts.

## State and Persistence Behavior

The header defines heap-owned strings for filenames, netgroup names, hostnames, users, and domains. Persistence is external: files are parsed from disk by `ng_file_parse`, but the structures are in-memory snapshots that must be released with `ng_file_deinit`.

## Dependencies and Integration Points

It includes NFS memory types, Gluster dictionaries, and `nfs.h`. It integrates with `mount3-auth.c` via `struct netgroups_file` and `struct netgroup_entry`.

## Risks and Edge Cases

The regex macros constrain accepted syntax. Callers must treat returned pointers as owned by the parsed file and avoid freeing nested entries directly. API users must call `ng_file_deinit` to avoid leaking dictionaries and strings.

## Test Signals

Compile coverage with `netgroups.c` and `mount3-auth.c`, plus parser tests that assert struct fields and dictionary contents for representative netgroups files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/netgroups.h -->

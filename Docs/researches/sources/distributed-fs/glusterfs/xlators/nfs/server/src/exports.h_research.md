# sources/distributed-fs/glusterfs/xlators/nfs/server/src/exports.h

## Purpose
Declares the exports-file parser data model and lookup API for Gluster's NFS mount authorization.

## APIs, Types, and Functions
Defines parser regex patterns for netgroups, hostnames, and options; length limits for netgroups, FQDNs, security options, UIDs, and directories; and logging domain `GF_EXP`. Core types are `struct export_options` (`rw`, `nosuid`, `root`, `anon_uid`, `sec_type`), `struct export_item` (name, options, refcount), `struct export_dir` (directory name plus netgroup and host dicts), and `struct exports_file` (filename plus export dict and UUID map). Public functions include `exp_file_parse()`, `exp_file_deinit()`, `exp_file_get_dir()`, `exp_dir_get_host()`, `exp_dir_get_netgroup()`, and `exp_file_dir_from_uuid()`.

## Control Flow, State, and Persistence
The header defines in-memory parser state only. An `exports_file` instance persists until deinitialized or atomically replaced by mount auth reload logic. `exports_map` supports file-handle mount UUID lookup, while `exports_dict` supports mount path lookup.

## Dependencies and Integration
Depends on NFS memory types, Gluster dict API, and `nfs.h`. It forward-declares `struct mount3_state` and `mnt3_mntpath_to_export()` to avoid a header cycle with `mount3.h`. It integrates with `exports.c`, `mount3-auth.c`, and `auth-cache.c`.

## Risks and Test Signals
Risks include cross-header coupling with `mount3.h`, parser regex changes affecting accepted exports syntax, and struct ownership expectations around refcounted `export_item` values. Test signals are compile coverage for mount auth and auth cache users, exports parser tests around constants and patterns, and reload/deinit tests proving ownership is balanced.

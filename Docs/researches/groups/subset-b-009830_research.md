# Research: subset-b-009830

Grouped research for Samba VFS modules under `sources/user-network-fs/samba/source3/modules`. Each section is source-tree aligned and bounded by reconciliation markers for per-file extraction.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_fruit.c -->
# sources/user-network-fs/samba/source3/modules/vfs_fruit.c

## Purpose
`vfs_fruit.c` implements Samba's `fruit` VFS module for macOS SMB, AppleDouble, and Netatalk interoperability. It recognizes the Apple special streams `AFP_AfpInfo` and `AFP_Resource`, maps them to configurable storage backends, negotiates the SMB2 AAPL create context, exposes macOS readdir attributes, coordinates optional Netatalk share-mode locks, and adds Time Machine and OS X copyfile behavior. The module expects to sit in a VFS stack with `catia` and `streams_xattr` when private-character mapping and stream storage are needed.

## Important APIs, Types, And Functions
The main configuration carrier is `struct fruit_config_data`, populated from `fruit:*` and `readdir_attr:*` smb.conf parameters in `init_fruit_config()`. Important enums select backend behavior: `fruit_rsrc` chooses resource-fork storage as normal stream, AppleDouble sidecar file, or Netatalk xattr; `fruit_meta` chooses metadata as stream or Netatalk xattr; `fruit_locking` enables Netatalk lock synchronization; `fruit_encoding` selects private Unicode or native ASCII mapping through catia.

Per-open state lives in `struct fio`, an FSP extension linking the Samba `files_struct` to module config, AppleDouble backend FSPs, fake descriptors, stream type, and deferred open flags. `fruit_get_complete_fio()` filters out internal AppleDouble opens so recursive backend operations pass through to lower modules.

Core VFS entry points are registered in `vfs_fruit_fns`: connect, disk free, fchmod, unlinkat, renameat, openat, close, pread/pwrite and async variants, fsync, stat/lstat/fstatat/fstat, streaminfo, fntimes, ftruncate, fallocate, create_file, freaddir_attr, server-side offload read/write, fs_file_id, and NT ACL get/set. `vfs_fruit_init()` registers the module as `fruit` and creates a debug class.

## Control Flow
On connect, `fruit_connect()` calls the next module, initializes config, adjusts share parameters, optionally appends veto patterns for AppleDouble and `.localized`, injects `catia:mappings` for native encoding, and enables durable handles while disabling kernel oplocks/share modes/posix locking for Time Machine shares.

Create/open flow starts in `fruit_create_file()`, which handles AAPL negotiation via `check_aapl()`, optionally converts legacy AppleDouble files before Apple stream opens, calls the lower `create_file`, rejects empty named-stream opens for AAPL clients, and applies Netatalk byte-range lock compatibility for base-file opens. `fruit_openat()` dispatches only named Apple streams specially: `AFP_AfpInfo` goes to metadata handlers, `AFP_Resource` goes to resource handlers, and all other files/streams are delegated.

Metadata stream handling differs by backend. `FRUIT_META_STREAM` opens a lower ADS when present, otherwise returns a fake fd for create-on-first-write. `FRUIT_META_NETATALK` always exposes a fake fd and reads/writes AppleDouble metadata in `AFPINFO_EA_NETATALK`. Reads normalize macOS behavior by ignoring most offsets and returning an `AFP_INFO_SIZE` packed blob. Writes validate or repair AFPInfo, copy only FinderInfo-relevant content, and mark all-zero FinderInfo writes delete-on-close to match macOS semantics.

Resource fork handling similarly dispatches by backend. `FRUIT_RSRC_STREAM` delegates to lower stream storage. `FRUIT_RSRC_XATTR` uses Solaris `attropen()` when available. `FRUIT_RSRC_ADFILE` opens a hidden `._` AppleDouble sidecar through `adouble_open_from_base_fsp()`, returns a fake fd to upper layers, and redirects resource reads/writes/truncates to the `ADEID_RFORK` offset inside the AppleDouble file while maintaining AppleDouble entry length.

Stream enumeration first asks the lower stack, then filters or synthesizes Apple streams. Metadata streaminfo removes raw Netatalk xattrs and only exposes `AFP_AfpInfo` when FinderInfo is non-empty or the lower stream is valid. Resource streaminfo hides zero-length resource streams and synthesizes `AFP_Resource` from AppleDouble sidecars when the resource fork length is non-zero.

## State And Persistence
Persistent data is stored in multiple filesystem locations depending on configuration: `AFP_AfpInfo` as a lower ADS or Netatalk xattr, `AFP_Resource` as a lower ADS, Netatalk xattr, or AppleDouble `._*` file. The module also mutates share runtime parameters on connect, changes veto-file patterns, may convert/delete AppleDouble files through `ad_convert()`, may update AppleDouble creation dates in `fruit_fntimes()`, and may chmod files after MS NFS ACL mode requests.

Runtime state includes per-share `fruit_config_data`, per-FSP `fio`, fake descriptors for virtual streams, internal AppleDouble FSP references, and global `global_fruit_config.nego_aapl`, which records that an AAPL create context was negotiated. Offload copyfile support uses a static `fruit_offload_ctx` token database context. Time Machine disk accounting is computed on demand by scanning sparsebundle directories and is not persisted by this module.

## Dependencies And Integration Points
This module depends heavily on Samba VFS APIs, `files_struct`, `smb_filename`, talloc, tevent, NTSTATUS helpers, security descriptor helpers, byte-range locks, `adouble` parsing/writing, macOS stream constants from `MacExtensions.h`, `util_macstreams`, `hash_inode()`, `string_replace` mappings, and offload token helpers. It integrates with lower VFS modules through `SMB_VFS_NEXT_*`, with `streams_xattr` for named streams, with `catia` for macOS character mapping, and with Netatalk-compatible xattrs and AppleDouble sidecars.

SMB protocol integration centers on SMB2 AAPL create blobs, AAPL readdir attributes, OS X copyfile over copychunk/offload operations, durable handles for Time Machine, and optional MS NFS-style virtual ACEs for Unix mode/uid/gid transport. Test discovery shows Samba selftests and torture suites for `vfs_fruit`, metadata stream/netatalk modes, stream depot, xattr, Time Machine, zero file IDs, AFPInfo validation, and AppleDouble cleanup behavior.

## Risks
The module has many backend-dependent paths, so behavior can diverge between stream, xattr, and AppleDouble configurations. Fake fds and recursive AppleDouble opens require careful FSP-extension lifetime handling; a missed `fio` detach or backend close can produce stale descriptors. `global_fruit_config.nego_aapl` is process-global, so its semantics are broader than one share or one client. Time Machine sizing scans and parses sparsebundles with regex and directory counts, which can be expensive and race with clients creating bundles. AppleDouble conversion and deletion options can modify sidecar files during normal stream operations. ACL handling intentionally injects and strips virtual MS NFS ACEs, which can surprise consumers expecting exact descriptor round-trips. Several compatibility choices intentionally mimic macOS quirks, including AFPInfo offset behavior, all-zero metadata deletion, zero-length resource fork hiding, and zero file IDs.

## Test Signals
High-value tests are the Samba `source4/torture/vfs/fruit.c` suites and selftest entries for metadata netatalk, metadata stream, stream depot, xattr, Time Machine max size, zero file ID, AFPInfo validation enabled/disabled, delete-empty AppleDouble files, and intentionally blank resource forks. Additional signals should cover AAPL negotiation and readdir attributes, FinderInfo persistence across backends, empty and non-empty resource fork open/delete/stat/streaminfo behavior, rename/chmod/unlink propagation to AppleDouble sidecars, Netatalk lock conflict behavior, copyfile copying named streams, Time Machine sparsebundle disk-free calculation, and ACL mode chmod through MS NFS virtual ACEs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_fruit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_full_audit.c -->
# sources/user-network-fs/samba/source3/modules/vfs_full_audit.c

## Purpose
`vfs_full_audit.c` implements Samba's `full_audit` VFS module, a parseable audit logger for VFS operations. It wraps a broad set of disk, directory, file, stream, ACL, xattr, async, durable-handle, snapshot, DFS, compression, and offload operations, forwards each call to the next VFS module, and logs selected success or failure events to syslog or Samba debug output.

## Important APIs, Types, And Functions
`vfs_op_type` enumerates every auditable operation and must stay in lockstep with `vfs_op_names[]`; `init_bitmap()` panics if this table and enum drift. `struct vfs_full_audit_private_data` stores success/failure bitmaps, syslog facility, priority, whether security descriptors should be SDDL-logged, and whether logging goes to syslog.

Configuration helpers are `audit_syslog_facility()`, `audit_syslog_priority()`, `audit_prefix()`, `log_success()`, `log_failure()`, `errmsg_unix()`, and `errmsg_ntstatus()`. `do_log()` is the central sink: it fetches private data, checks the operation bitmap, expands the configured prefix, formats `ok` or `fail (reason)`, and emits `prefix|operation|status|payload`.

`smb_full_audit_connect()` initializes private data after the lower connect succeeds, opens syslog as `smbd_audit` when enabled, parses `full_audit:success` and `full_audit:failure`, stores the handle data, and logs connect. `vfs_full_audit_fns` registers wrappers for all implemented VFS slots, and `vfs_full_audit_init()` calls `smb_vfs_assert_all_fns()` before registering the module as `full_audit`.

## Control Flow
Most wrappers follow a common pattern: call the corresponding `SMB_VFS_NEXT_*` operation, derive failure text from `errno` or `NTSTATUS`, format the relevant path or operation arguments, call `do_log()`, then return the original result. Path helpers normalize `smb_filename` and `files_struct` values into full SMB paths using a temporary talloc context.

Async wrappers split logging across send and recv phases. `pread`, `pwrite`, `fsync`, `get_dos_attributes`, and `getxattrat` allocate small tevent state structs, log send success or allocation failure, forward to the lower async operation, store the recv result in their completion callback, and log final recv success or failure when the caller receives the request.

Operations with multiple path inputs construct full source/destination names before delegation where possible, such as rename, link, symlink, mkdir, unlink, DFS path operations, and readlink. ACL set can optionally encode the submitted security descriptor with `sddl_encode()` when `full_audit:log_secdesc = true`.

## State And Persistence
The module does not persist audit state in the repository or filesystem. Per-share runtime state is held in the VFS handle as bitmaps and logging options. Its durable output is external logging: syslog by default, or Samba `DEBUG(1)` output when `full_audit:syslog = false`. The temporary global `tmp_do_log_ctx` is used only while formatting log arguments and is freed after each `do_log()` call.

The module intentionally preserves wrapped operation semantics. It generally restores `errno` where post-call logging or path cleanup could disturb the caller-visible error, for example in rename paths. Failed configuration during connect disconnects the lower VFS handle and fails the share connect.

## Dependencies And Integration Points
This file depends on Samba VFS interfaces, loadparm parameter APIs, talloc, bitmap utilities, syslog constants, tevent, NTSTATUS helpers, security descriptor SDDL encoding, file-id formatting, path substitution from `source3/lib/substitute.h`, and many Samba file/ACL/xattr structures. Configuration keys are `full_audit:prefix`, `full_audit:success`, `full_audit:failure`, `full_audit:facility`, `full_audit:priority`, `full_audit:log_secdesc`, and `full_audit:syslog`.

The module is designed to be loaded in a share's `vfs objects` list. It integrates with all lower VFS modules through `SMB_VFS_NEXT_*` calls and with system logging through `openlog()` and `syslog()` when built with syslog support.

## Risks
The enum/name table must remain exactly synchronized or configuration parsing can panic at runtime. Audit selection defaults are security-sensitive: the code uses `"none"` as the local default list passed to `init_bitmap()`, while comments describe success defaulting to no logging and failure defaulting to everything, so effective behavior depends on the loadparm defaults that feed the string lists. Logging can leak filenames, usernames, client IPs, xattr names, and optionally complete security descriptors. Full auditing of high-frequency operations like `readdir`, `pread`, `pwrite`, `getxattrat`, and lock checks can create high syslog volume and noticeable overhead. Some wrappers treat operations without clear failure semantics as success, and some payloads are intentionally terse, so logs are useful for tracing but not a complete semantic record of every parameter.

## Test Signals
Relevant Samba selftests include `samba3.test_vfs_full_audit`, blackbox tests for bad success/failure operation names, and `samba.vfstest.full_audit_segfault`. Good coverage should verify success/failure bitmap parsing for `all`, `none`, negated operations, and invalid names; prefix macro expansion; syslog-disabled debug logging; facility/priority fallback; path formatting for relative names; async send/recv logging; SDDL inclusion when `log_secdesc` is enabled; and that wrapped operations preserve return values and `errno`/`NTSTATUS`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_full_audit.c -->

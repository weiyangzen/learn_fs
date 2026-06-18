<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mount/fuse/src/fuse-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/mount/fuse/src/fuse-mem-types.h

## Purpose
Defines the FUSE mount translator's memory-accounting type range. The enum gives GlusterFS allocator call sites stable type identifiers for FUSE-specific objects so memory accounting can distinguish iovecs, bridge state, FD contexts, graph-switch helpers, gid lists, invalidation nodes, threads, timed messages, and interrupt records from common allocator classes.

## APIs, Types, and Functions
The only exported type is `enum gf_fuse_mem_types_`. It starts at `gf_common_mt_end + 1` and ends at `gf_fuse_mt_end`, matching Gluster's convention that each component owns a contiguous memory type block. Important values include `gf_fuse_mt_fuse_private_t`, `gf_fuse_mt_fuse_state_t`, `gf_fuse_mt_fd_ctx_t`, `gf_fuse_mt_graph_switch_args_t`, `gf_fuse_mt_gids_t`, and `gf_fuse_mt_interrupt_record_t`.

## Control Flow, State, and Persistence
There is no executable control flow. The enum is compile-time state consumed by allocation macros. Persistence is indirect: when memory accounting is enabled, allocations tagged with these identifiers are accumulated in GlusterFS runtime accounting data and logs.

## Dependencies and Integration
Depends on `<glusterfs/mem-types.h>` for `gf_common_mt_end`. It integrates with FUSE translator sources that call `GF_MALLOC`, `GF_CALLOC`, or related macros using FUSE memory type constants.

## Risks and Test Signals
Risks are mostly maintenance risks: enum values must stay after the common range, and new FUSE allocation classes need matching type additions before use. Test signals include successful FUSE translator builds with memory accounting enabled, leak/accounting reports showing these buckets, and compile failures if a type is renamed or removed while still referenced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mount/fuse/src/fuse-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mount/fuse/src/fuse-resolve.c -->
# sources/distributed-fs/glusterfs/xlators/mount/fuse/src/fuse-resolve.c

## Purpose
Implements the FUSE bridge resolver that converts FUSE inode numbers, parent/name pairs, GFIDs, and open file descriptors into current Gluster `loc_t` and `fd_t` objects before resuming a filesystem operation. It also handles graph-switch FD migration so operations continue on the active subvolume instead of stale graph state.

## APIs, Types, and Functions
Public entry points include `fuse_resolve_and_resume()`, `fuse_resolve_continue()`, `fuse_resolve_entry_init()`, `fuse_resolve_inode_init()`, `fuse_resolve_fd_init()`, `fuse_gfid_set()`, and `fuse_migrate_fd_task()`. Lookup callbacks `fuse_resolve_entry_cbk()` and `fuse_resolve_gfid_cbk()` link resolved inodes into the inode table and mark new links with `LOOKUP_NOT_NEEDED`. Resolver paths include `fuse_resolve_parent_simple()`, `fuse_resolve_parent()`, `fuse_resolve_inode_simple()`, `fuse_resolve_inode()`, `fuse_resolve_gfid()`, and `fuse_resolve_fd()`. `FUSE_FD_GET_ACTIVE_FD` protects active-FD selection with the base FD lock.

## Control Flow, State, and Persistence
Resolution starts in `fuse_resolve_and_resume()`, which optionally inserts `"gfid-req"` into `state->xdata`, records the resume function, and calls `fuse_resolve_all()`. `fuse_resolve_all()` walks at most two resolver slots, `state->resolve` and `state->resolve2`, switching `state->resolve_now` and `state->loc_now` before invoking `fuse_resolve()`. `fuse_resolve()` prefers FD resolution, then parent/name resolution, then GFID/inode resolution, and finally advances to the next slot. Parent and inode fast paths reuse hints from the current inode table when `inode_needs_lookup()` is false. Misses fall back to asynchronous `lookup` FOPs by GFID or parent/name, and callbacks resume the state machine. FD resolution checks `fuse_fd_ctx_t`, compares the active FD's subvolume against `state->active_subvol`, launches `synctask_new()` for `fuse_migrate_fd_task()` when needed, and reports `EBADF` if migration failed. Persistent state is in inode-table links, inode context flags, FD context `activefd` and `migration_failed`, loc fields, and the request state's xdata.

## Dependencies and Integration
Depends on `fuse-bridge.h`, Gluster inode/fd/loc APIs, FOP stack macros, `dict_t`, `synctask_new()`, UUID helpers, and graph/subvolume state. It integrates directly with the FUSE request handling path: callers initialize one or two resolves, then the resolver resumes the original FOP through `fuse_fop_resume()`.

## Risks and Test Signals
Key risks are stale inode hints across graph switches, incorrect `inode_ref`/`inode_unref` balance, missed `loc_wipe()` cleanup after asynchronous lookup, FD migration races around `activefd`, and ambiguous root parent/name lookups that intentionally force a conservative lookup. FD migration failure maps to `EBADF`, which can surface as user-visible operation failure during graph changes. Test signals include graph-switch tests with open FDs, parent/name lookups after readdirplus, missing-entry lookups under root, two-loc operations such as rename/link, GFID-request creation, and fault injection for failed lookup or failed synctask creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mount/fuse/src/fuse-resolve.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mount/fuse/utils/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/mount/fuse/utils/Makefile.am

## Purpose
Selects the installed FUSE mount helper script for the target platform.

## APIs, Types, and Functions
The automake variables are `utildir = @mountutildir@`, `util_SCRIPTS`, and `CLEANFILES`. Under `GF_LINUX_HOST_OS`, `util_SCRIPTS` installs `mount.glusterfs`; otherwise it installs `mount_glusterfs`.

## Control Flow, State, and Persistence
There is no runtime control flow. During configure/build, automake expands the conditional and installs exactly one helper into the configured mount utility directory. `CLEANFILES` is empty here.

## Dependencies and Integration
Depends on configure-time substitution of `@mountutildir@` and the `GF_LINUX_HOST_OS` automake conditional. It integrates with system mount helper discovery, where Linux expects `mount.glusterfs` and non-Linux platforms use the underscore variant.

## Risks and Test Signals
Risks include installing the wrong helper if host OS detection is wrong, or missing generated helper substitutions if packaging rules do not process the `.in` templates. Test signals are `make install` output on Linux and BSD/Darwin targets, package file lists containing the expected helper name, and mount invocations resolving the installed script.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mount/fuse/utils/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mount/fuse/utils/mount.glusterfs.in -->
# sources/distributed-fs/glusterfs/xlators/mount/fuse/utils/mount.glusterfs.in

## Purpose
Linux and NetBSD mount helper template for `mount -t glusterfs`. It parses mount arguments and `-o` options, validates server/volume and mountpoint inputs, prevents recursive brick mounts, updates `updatedb` pruning, translates mount options into `glusterfs` daemon arguments, and executes the daemon against the requested mount point.

## APIs, Types, and Functions
Shell functions are `warn()`, `_init()`, `is_valid_hostname()`, `parse_backup_volfile_servers()`, `parse_volfile_servers()`, `start_glusterfs()`, `print_usage()`, `check_recursive_mount()`, `with_options()`, `without_options()`, `parse_options()`, `update_updatedb()`, and `main()`. Option variables cover log level/file, transport, volume ID/name, volfile server and backups, timeout/cache controls, FUSE mount options, subdir mounts, ACL/SELinux/read-only flags, root-squash inversion, HA/halo xlator options, FUSE interrupt handling, copy-file-range handling, and process naming.

## Control Flow, State, and Persistence
`_init()` sets command paths, platform-specific `stat` commands, `/proc/mounts`, and `/etc/updatedb.conf`. `main()` parses Linux positional arguments first, processes `getopts`, detects whether the first argument is a local volfile or `server:volume[/subdir]`, extracts volume and optional subdir information, rejects invalid mountpoint or misplaced `-o`, checks for an existing `fuse.glusterfs` mount, marks snapshot volumes read-only, calls `check_recursive_mount()`, updates `updatedb.conf`, then calls `start_glusterfs()`. `parse_options()` splits comma-separated mount options into `with_options()` or `without_options()`. `start_glusterfs()` builds `cmd_line` by appending validated options, expands server lists including IPv6 backup syntax, adds volfile or volfile-server arguments, appends mount point, executes the command, and verifies the mountpoint can be statted after daemonization. Persistent effects are a GlusterFS FUSE mount, possible `/etc/updatedb.conf` modification, and daemon logs at the requested log file.

## Dependencies and Integration
Depends on generated configure substitutions such as `@sbindir@`, `@prefix@`, `@exec_prefix@`, and `@GLUSTERD_WORKDIR@`; shell utilities `sed`, `awk`, `grep`, `stat`, `uname`, `getfattr`, `umount`, and `mv`; the `glusterfs` binary; and Linux/NetBSD mount helper conventions. It integrates with glusterd brick metadata to reject mounting over bricks or brick parents and with FUSE daemon options consumed by the mount translator.

## Risks and Test Signals
Risks include fragile comma splitting for option values containing commas, shell word-splitting and quoting hazards in server names, mountpoints, SELinux contexts, xlator options, and log paths, duplicate `--fuse-mountopts` emission, and reliance on `getfattr` for part of recursive mount detection. The recursive brick loop also depends on local brick paths being listable. Test signals include Linux helper invocation through `/sbin/mount.glusterfs`, IPv4/IPv6 and backup-volfile-server parsing, snapshot read-only behavior, subdir mount extraction, invalid option rejection, duplicate mount exit code 32, recursive brick rejection, and successful daemon stat verification after mount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mount/fuse/utils/mount.glusterfs.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mount/fuse/utils/mount_glusterfs.in -->
# sources/distributed-fs/glusterfs/xlators/mount/fuse/utils/mount_glusterfs.in

## Purpose
BSD/Darwin-oriented mount helper template for GlusterFS FUSE mounts. It performs a smaller option translation and argument parsing flow than the Linux helper, then starts the `glusterfs` daemon with volfile-server or local-volfile settings.

## APIs, Types, and Functions
Functions are `warn()`, `_init()`, `is_valid_hostname()`, `parse_backup_volfile_servers()`, `parse_volfile_servers()`, `start_glusterfs()`, `print_usage()`, `with_options()`, `without_options()`, `parse_options()`, and `main()`. Supported options include log level/file, transport, direct I/O, mac compatibility, volume ID/name, volfile check, server port, timeouts, background queue, backup volfile servers, fetch attempts, congestion threshold, xlator option, FUSE mount options, readdirp, root-squash inversion, process name, read-only, ACL, SELinux, WORM, fopen keep-cache, ino32, memory accounting, aux GFID mount, and Darwin capability support.

## Control Flow, State, and Persistence
`_init()` sets log constants, command path, Darwin `stat` commands, and platform aliases. `main()` handles the OSX convention where `-o` may be the first argument, then parses `getopts`, handles FreeBSD positional arguments under preprocessor guards, resolves local volfile versus `server:volume`, validates server and mountpoint presence, rejects `-o` in positional slots, and calls `start_glusterfs()`. `start_glusterfs()` uppercases log levels, appends selected daemon options, expands primary and backup volfile servers, adds transport/server-port/volume ID, appends mount point, and executes the resulting command. State persists as the mounted FUSE filesystem and daemon process.

## Dependencies and Integration
Depends on configure substitutions for install paths, `uname`, `sed`, `awk`, `grep`, platform `stat`, and the `glusterfs` binary. The template includes C preprocessor conditionals for FreeBSD handling, so it integrates with the build system before installation. It complements `mount.glusterfs.in` through `Makefile.am` host selection.

## Risks and Test Signals
Risks include reduced validation compared with the Linux helper, no recursive brick check, shell word-splitting hazards, simplistic `server:volume` parsing, and platform-specific option order differences. `xlator-option` supports only one stored value, unlike the Linux helper's accumulated `xlator_options`. Test signals are Darwin and FreeBSD helper invocation paths, OSX first-argument `-o` handling, backup server parsing, local volfile mounting, invalid mountpoint rejection, and daemon command construction for mac-compat/capability options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/mount/fuse/utils/mount_glusterfs.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/nfs/Makefile.am

## Purpose
Top-level automake entry for the GlusterFS NFS translator subtree.

## APIs, Types, and Functions
The file defines `SUBDIRS = server` and an empty `CLEANFILES`.

## Control Flow, State, and Persistence
Build traversal descends into `xlators/nfs/server`. There is no runtime state.

## Dependencies and Integration
Depends on automake's recursive make behavior. It integrates the NFS server translator subtree into the broader `xlators` build.

## Risks and Test Signals
Risk is limited to build coverage: omitting `server` would silently exclude the NFS translator subtree. Test signals are recursive make logs entering `xlators/nfs/server`, generated distribution files including the subtree, and configured builds reaching `server/src`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/Makefile.am

## Purpose
Intermediate automake entry for the GlusterFS NFS server translator.

## APIs, Types, and Functions
The file defines `SUBDIRS = src` and an empty `CLEANFILES`.

## Control Flow, State, and Persistence
Build traversal descends into `xlators/nfs/server/src`, where the loadable translator module is defined. There is no runtime state.

## Dependencies and Integration
Depends on automake recursive make. It integrates the server source directory into the NFS subtree build.

## Risks and Test Signals
Risk is limited to build-system wiring. Test signals are recursive make logs entering `xlators/nfs/server/src` and package generation including the server source artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/Makefile.am

## Purpose
Builds the GlusterFS NFS server translator module `server.la` and declares its source, header, include, link, and distribution settings.

## APIs, Types, and Functions
When `WITH_SERVER` is enabled, `xlator_LTLIBRARIES = server.la`. `server_la_SOURCES` includes NFS core, common helpers, FOPs, inode handling, generic helpers, MOUNTv3, NFSv3 file handles and helpers, NLM, callback services, ACLv3, netgroups, exports, mount authorization, and auth cache sources. `server_la_LIBADD` links libglusterfs, libgfapi, gfrpc, and gfxdr. `noinst_HEADERS` lists internal headers, and `EXTRA_DIST` ships `nfsserver.sym`.

## Control Flow, State, and Persistence
There is no runtime control flow. At build time, libtool creates a module with `-module`, exports symbols constrained by `nfsserver.sym`, and installs it under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/nfs`. Preprocessor flags define `LIBDIR` for auth modules and `DATADIR` for runtime data paths.

## Dependencies and Integration
Depends on the GlusterFS core library, gfapi, RPC library, XDR library, generated RPC/XDR headers, `CONTRIBDIR` rbtree headers, and configure variables such as `GF_CPPFLAGS`, `GF_CFLAGS`, and `GF_XLATOR_LDFLAGS`. It integrates the NFS translator into Gluster's loadable xlator plugin layout.

## Risks and Test Signals
Risks include source list drift when adding/removing NFS server files, missing headers in distribution tarballs, symbol export mismatches, and conditional server builds accidentally disabling NFS artifacts. Test signals are `WITH_SERVER` and non-`WITH_SERVER` build variants, module load tests, symbol checks against `nfsserver.sym`, and link failures catching missing library dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/acl3.c -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/acl3.c

## Purpose
Implements the NFS ACL version 3 RPC program for Gluster's NFS server. It handles NULL, GETACL, and SETACL procedures, resolves NFS file handles to Gluster locations, translates ACL wire entries to and from POSIX ACL xattr buffers, and submits XDR-encoded RPC replies.

## APIs, Types, and Functions
Important exported functions are `acl3svc_init()`, `acl3svc_null()`, `acl3svc_getacl()`, `acl3svc_setacl()`, `acl3_getacl_reply()`, and `acl3_setacl_reply()`. Internal flow uses `acl3svc_submit_reply()`, callbacks `acl3_stat_cbk()`, `acl3_default_getacl_cbk()`, `acl3_getacl_cbk()`, `acl3_setacl_cbk()`, resume functions `acl3_getacl_resume()` and `acl3_setacl_resume()`, and conversion helpers `acl3_nfs_acl_to_xattr()` and `acl3_nfs_acl_from_xattr()`. The file defines validation macros for NFSv3 state, Gluster file handles, file-handle-to-volume mapping, subvolume start state, resolved file handles, and call-state initialization. `acl3svc_actors` and `acl3prog` register the RPC program.

## Control Flow, State, and Persistence
GETACL decodes `getaclargs`, validates the mask and file handle, maps the handle to a volume, creates `nfs3_call_state_t`, resolves the file handle asynchronously, stats the resolved object, fills NFS attributes, then reads default ACL xattrs for directories and access ACL xattrs for all objects before replying. SETACL allocates max-size ACL arrays, decodes `setaclargs`, validates masks and handles, converts user and default ACL entries into `cs->aclxattr` and `cs->daclxattr`, resolves the file handle, builds a dict containing `POSIX_ACL_ACCESS_XATTR` and/or `POSIX_ACL_DEFAULT_XATTR`, calls `nfs_setxattr()`, then replies from callback. `acl3svc_init()` creates an ACL listener on `GF_ACL3_PORT`, honors insecure port settings, and uses a static `acl3_inited` boolean to make setup one-shot. Persistent effects are POSIX ACL xattrs on backend files and RPC listener registration.

## Dependencies and Integration
Depends on NFSv3 state/call-state helpers, Gluster RPC service APIs, XDR serializers/deserializers, iobuf/iobref pools, file-handle resolution, `nfs_getxattr()`, `nfs_setxattr()`, `nfs_stat()`, POSIX ACL xattr structures, endian conversion, and NFS message logging. It integrates as an auxiliary RPC program beside the main NFSv3 service.

## Risks and Test Signals
Risks include ACL count bounds, endian conversion correctness, default ACL flag masking, Solaris mask-bit compatibility, reply cleanup on asynchronous error paths, listener one-shot behavior across reloads, and possible null `cs` cleanup on early SETACL failures. Test signals include GETACL on files and directories with and without ACL xattrs, SETACL round trips for access and default ACLs, invalid masks returning `NFS3ERR_INVAL`, bad handles returning `NFS3ERR_BADHANDLE` or stale mapping, backend xattr ENODATA handling as success, and listener creation with insecure-port options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/acl3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/acl3.h -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/acl3.h

## Purpose
Declares constants and the initialization entry point for the NFS ACLv3 RPC program.

## APIs, Types, and Functions
Defines procedure numbers `ACL3_NULL`, `ACL3_GETACL`, `ACL3_SETACL`, and `ACL3_PROC_COUNT`; listener port `GF_ACL3_PORT`; logging domain `GF_ACL`; ACL mask bits `NFS_ACL`, `NFS_ACLCNT`, `NFS_DFACL`, `NFS_DFACLCNT`; NFS default ACL tag bit `NFS_ACL_DEFAULT`; and maximum ACL entry count `NFS_ACL_MAX_ENTRIES`. It declares `rpcsvc_program_t *acl3svc_init(xlator_t *nfsx)`.

## Control Flow, State, and Persistence
The header has no runtime flow. Its constants control ACL RPC dispatch sizing, valid mask validation, ACL translation bounds, and listener configuration in `acl3.c`.

## Dependencies and Integration
Depends on `<glusterfs/glusterfs-acl.h>` for POSIX ACL definitions and on types visible through included NFS/RPC headers in consumers. It integrates with `acl3.c` and the NFS server build.

## Risks and Test Signals
Risks include mismatch between `ACL3_PROC_COUNT` and the actor table, changing `GF_ACL3_PORT` breaking clients or firewall rules, and `NFS_ACL_MAX_ENTRIES` diverging from allocated call-state buffers. Test signals are compile-time actor table builds, ACL GET/SET calls using the defined masks, and interoperability with NFS ACL clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/acl3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/auth-cache.c -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/auth-cache.c

## Purpose
Implements a TTL-based authorization cache for NFS file handles. It records that a host has been authorized for a file handle and keeps the matched `export_item` so later NFS operations can avoid reparsing or rewalking exports and netgroups until the entry expires.

## APIs, Types, and Functions
Public functions are `auth_cache_init()`, `cache_nfs_fh()`, `is_nfs_fh_cached()`, `is_nfs_fh_cached_and_writeable()`, and `auth_cache_purge()`. Internal pieces include `enum auth_cache_lookup_results`, `struct auth_cache_entry`, `make_hashkey()`, `auth_cache_entry_init()`, `auth_cache_entry_free()`, `auth_cache_add()`, `_auth_cache_expired()`, `auth_cache_get()`, `auth_cache_lookup()`, and `auth_cache_entry_purge()`.

## Control Flow, State, and Persistence
`make_hashkey()` builds a key from file-handle `exportid`, `mountid`, and host address. `cache_nfs_fh()` first looks up the entry, then creates a refcounted `auth_cache_entry`, timestamps it with `gf_time()`, takes a reference to the authorized `export_item`, wraps it in a `data_t`, and inserts it under the cache lock. `auth_cache_lookup()` generates the same key, calls `auth_cache_get()`, returns the cached timestamp and `opts->rw` flag on hit, and releases the entry reference. Expired entries are removed from the dict. `auth_cache_purge()` swaps in a new dict under lock, then walks and releases entries from the old dict. State is in `struct auth_cache`: a lock, dict, TTL seconds, and per-entry references to export options.

## Dependencies and Integration
Depends on Gluster `dict_t`, locks, refcount helpers, `data_t`, UUID formatting, `gf_time()`, NFSv3 file-handle layout, export parsing structures, and NFS logging. It integrates with mount authorization and NFS FOP authorization checks that cache successful host/file-handle decisions.

## Risks and Test Signals
Risks include the file's own FIXME around dangerous `entry_data` use, manual `GF_FREE(lookup_res)` on expiry instead of normal refcount release, potential stale authorization until TTL expiry after exports changes, host string normalization mismatches, and lock/refcount interaction during purge and lookup. Test signals include cache hit/miss/expiry cases, writeable versus read-only export checks, purge while lookups are active, exports reload invalidation behavior, and sanitizer or valgrind runs around expired-entry removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/auth-cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/auth-cache.h -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/auth-cache.h

## Purpose
Declares the NFS authorization cache interface and cache container type.

## APIs, Types, and Functions
`struct auth_cache` contains `gf_lock_t lock`, `dict_t *cache_dict`, and `time_t ttl_sec`. The public API is `auth_cache_init()`, `cache_nfs_fh()`, `is_nfs_fh_cached_and_writeable()`, `is_nfs_fh_cached()`, and `auth_cache_purge()`.

## Control Flow, State, and Persistence
The header has no executable flow. It defines the state shared by cache implementation and users: an in-memory dictionary protected by a Gluster lock and governed by TTL. No on-disk persistence is implied.

## Dependencies and Integration
Depends on `nfs-mem-types.h`, `exports.h`, `<glusterfs/dict.h>`, and `nfs3.h`. It integrates with NFS server authorization paths that use `struct nfs3_fh`, host addresses, and parsed `struct export_item` objects.

## Risks and Test Signals
Risks include callers treating cache checks as authoritative after export configuration changes, passing unstable `host_addr` formatting, or using the cache without periodic purge/reload. Test signals are compile coverage for all cache users, write-permission checks through `is_nfs_fh_cached_and_writeable()`, and reload paths invoking `auth_cache_purge()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/auth-cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/exports.c -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/exports.c

## Purpose
Parses an NFS exports file into lookup dictionaries used by Gluster's mount authorization path. It recognizes export directories, host entries, netgroup entries, and per-entry options, and builds both directory-name and UUID-like maps so later file-handle authorization can find the export originally mounted by a client.

## APIs, Types, and Functions
External functions are `exp_file_parse()`, `exp_file_deinit()`, `exp_file_get_dir()`, `exp_dir_get_host()`, `exp_dir_get_netgroup()`, and `exp_file_dir_from_uuid()`. Internal helpers initialize/deinitialize parsers and objects, print exports, destroy dict contents, parse options (`__exp_line_opt_parse()` and `__exp_line_opt_key_value_parse()`), parse host/netgroup strings (`__exp_line_ng_host_str_parse()`), parse netgroups and hosts from a line, parse directory names, parse full lines, and insert export dirs with `_exp_file_insert()`. `enum gf_exp_parse_status` distinguishes success, not found, parse failure, mount-state mismatch, and ignored lines.

## Control Flow, State, and Persistence
`exp_file_parse()` opens the file, initializes regex parsers, reads lines with `getline()`, strips newlines, and calls `_exp_line_parse()`. `_exp_line_parse()` ignores comments/blank/leading-space lines, extracts the directory token, optionally validates it against `mount3_state`, parses netgroup and host items, and returns a populated `struct export_dir`. Parsed dirs are inserted into `exports_dict` by directory name and into `exports_map` by a UUID string whose first bytes contain `SuperFastHash()` of the directory with leading slashes removed. Host lookup first tries the exact host and then wildcard `"*"`. Directory lookup normalizes missing leading slash. Persistent state is the in-memory `struct exports_file` graph of dicts, refcounted `export_item` values, option strings, and the hash map used by NFS file-handle mount IDs.

## Dependencies and Integration
Depends on Gluster dict/data/refcount APIs, `SuperFastHash`, parser utilities, mount3 export lookup, NFS logging, and memory types. It integrates with `mount3-auth.c` for host/netgroup authorization and with file-handle paths that need `exp_file_dir_from_uuid()`.

## Risks and Test Signals
Risks include regex grammar limitations, comments or whitespace semantics that ignore leading-space lines, option parser accepting only `root`, `ro`, `rw`, `nosuid`, `anonuid`, and `sec`, hash collisions in the UUID-like exports map, double destruction hazards because `exports_dict` and `exports_map` can reference the same `export_dir` data, and inconsistent refcount handling for dict-held `export_item` values. Test signals include parsing mixed host/netgroup lines, wildcard host fallback, trailing slash normalization, mount-state filtering, invalid option rejection, exports-map lookup from generated mount IDs, reload/deinit under sanitizer, and long directory/FQDN boundary cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/exports.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/exports.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/exports.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/mount3-auth.c -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/mount3-auth.c

## Purpose
Implements host authorization for NFS MOUNTv3 and subsequent NFS file operations. It loads parsed exports and netgroups files, checks whether a host is allowed for a directory or mounted file handle, resolves netgroup membership recursively, handles subnet entries, and enforces read-only versus read-write export options.

## APIs, Types, and Functions
Public functions are `mnt3_auth_params_init()`, `mnt3_auth_params_deinit()`, `mnt3_auth_set_exports_auth()`, `mnt3_auth_set_netgroups_auth()`, `mnt3_auth_host()`, and `check_rw_access()`. Internal structures and helpers include `struct _mnt3_subnet_match_s`, `_mnt3_auth_subnet_match()`, `_mnt3_auth_check_host_in_export()`, `struct ng_auth_search`, `__netgroup_dict_search()`, `__export_dir_lookup_netgroup()`, `_mnt3_auth_setup_search_params()`, and `_mnt3_auth_check_host_in_netgroup()`.

## Control Flow, State, and Persistence
Initialization allocates `struct mnt3_auth_params` and binds it to a `mount3_state`. Export and netgroup setters parse files, atomically replace `expfile` or `ngfile` with `__sync_lock_test_and_set()`, and deinitialize old files. `mnt3_auth_host()` first searches the exports file: for FOPs with a file handle it maps `fh->mountid` through `exp_file_dir_from_uuid()`, while mount requests use the requested directory. It then looks for exact host entries, CIDR subnet entries, and finally netgroup membership. Netgroup search walks exported netgroup names, loads corresponding netgroup entries, searches direct hosts and nested netgroups, and returns the export item that supplied options. If the operation is a write, `check_rw_access()` returns `-EROFS` unless the matched item is `rw`; otherwise authorization succeeds with 0. Deinit atomically clears `ms->auth_params` before freeing files so later FOPs are denied rather than using torn-down state.

## Dependencies and Integration
Depends on parsed exports, parsed netgroups, mount3 state, Gluster memory allocation, dict walking, `gf_is_ip_in_net()` for CIDR matching, and NFS logging. It integrates with MOUNTv3 request handling and NFS FOP authorization, and supplies the `export_item` later cached by `auth-cache.c`.

## Risks and Test Signals
Risks include atomic pointer replacement without broader reader lifetime protection, recursive netgroup cycles or deep nesting, subnet matching only for entries containing `/`, exact host string matching without DNS normalization, stale auth cache entries after reload, and the header declaration `mnt3_auth_fop_options_verify()` having no implementation in this file. Test signals include exact host, wildcard, subnet, and netgroup authorization; write attempts against read-only exports returning `-EROFS`; reload while operations run; null or missing auth files denying access; file-handle based authorization after mount; and nested netgroup search behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/mount3-auth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/mount3-auth.h -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/mount3-auth.h

## Purpose
Declares the mount authorization parameter object and public authorization API for Gluster's NFS MOUNTv3/NFS FOP paths.

## APIs, Types, and Functions
Defines logging domain `GF_MNT_AUTH` and `struct mnt3_auth_params`, which holds pointers to a netgroups file, exports file, and owning `mount3_state`. Declares `mnt3_auth_params_init()`, `mnt3_auth_set_netgroups_auth()`, `mnt3_auth_set_exports_auth()`, `mnt3_auth_host()`, `mnt3_auth_params_deinit()`, and `mnt3_auth_fop_options_verify()`.

## Control Flow, State, and Persistence
The header has no executable flow. It defines the in-memory authorization state that persists under `mount3_state` until reloaded or deinitialized. `mnt3_auth_host()` can optionally return the matched `export_item` through `save_item` for cache integration.

## Dependencies and Integration
Depends on NFS memory types, netgroups, exports, `mount3.h`, and `nfs.h`. It integrates mount3 request handling, exports parsing, netgroups parsing, and NFS file-handle authorization.

## Risks and Test Signals
Risks include header-level coupling across mount3, exports, and netgroups, and the declared `mnt3_auth_fop_options_verify()` lacking a corresponding implementation in the researched source set. Test signals are compile/link coverage for all declared functions, auth reload tests, and FOP authorization paths using `mnt3_auth_host()` with and without saved export items.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/mount3-auth.h -->

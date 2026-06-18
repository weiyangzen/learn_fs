# Research Group subset-b-009728

Grouped research for nfs-utils export, support/include, junction, and misc files. Each section is source-tree aligned and bounded by reconciliation markers for per-file extraction.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/export/cache_flush.c -->
# sources/user-network-fs/nfs-utils/support/export/cache_flush.c

## Purpose
Flushes knfsd and sunrpc authentication/export caches after export state changes. It prefers generic netlink cache-flush commands and falls back to the historical `/proc/net/rpc/*/flush` files.

## Important APIs, Types, and Functions
`cache_flush()` is the public entry point. Helpers include `nl_send_flush()`, `cache_nl_flush()`, and `cache_proc_flush()`. It uses `NFSD_CMD_CACHE_FLUSH`, `SUNRPC_CMD_CACHE_FLUSH`, `NFSD_FAMILY_NAME`, and `SUNRPC_FAMILY_NAME`.

## Control Flow
`cache_flush()` tries netlink unless global `no_netlink` is set. `cache_nl_flush()` opens a genetlink socket, enables `NETLINK_EXT_ACK`, resolves and flushes the sunrpc family first, then flushes nfsd if available. On failure it writes a future timestamp to procfs flush files in dependency order.

## State and Persistence Behavior
No repository state is persisted. Effects are kernel cache invalidations through netlink or procfs. The only process state consulted is `no_netlink`; procfs writes use current time plus one second for old kernels.

## Dependencies and Integration Points
Depends on libnl generic netlink, generated or system nfsd/sunrpc netlink UAPI headers, `nfslib.h`, `xlog.h`, and `compat.h`. It integrates with exportfs/mountd paths that need kernel cache invalidation after export table updates.

## Risks and Edge Cases
Ordering is significant because filehandle cache entries reference export cache entries. Netlink family absence triggers fallback or partial success. Procfs paths may be missing when nfsd is not running; write failures are warning-only. Timestamp semantics differ across kernel versions.

## Test Signals
Exercise netlink success, missing sunrpc/nfsd families, `no_netlink` fallback, absent procfs cache files, and short write/error handling. Integration signals are export changes becoming visible to knfsd without stale auth/export results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/export/cache_flush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/export/client.c -->
# sources/user-network-fs/nfs-utils/support/export/client.c

## Purpose
Maintains the in-memory client table used by export matching. It classifies export host identifiers as FQDNs, subnetworks, wildcards, netgroups, anonymous clients, or GSS principals, then resolves and matches callers against those records.

## Important APIs, Types, and Functions
Public functions are `client_lookup()`, `client_dup()`, `client_gettype()`, `client_check()`, `client_release()`, `client_freeall()`, `client_resolve()`, `client_compose()`, and `client_member()`. Core helpers initialize address lists, parse IPv4/IPv6 netmasks, test wildcard/netgroup membership, and maintain sorted comma-separated names.

## Control Flow
`client_lookup()` classifies the host string, resolves FQDNs when needed, searches `clientlist[type]`, allocates a new `nfs_client` when absent, and populates addresses. `client_check()` dispatches by type: exact address comparison for FQDNs, mask matching for subnetworks, reverse DNS plus aliases for wildcards, `innetgr()` variants for netgroups, and unconditional match for anonymous clients.

## State and Persistence Behavior
`clientlist[MCL_MAXTYPES]` is a process-global linked-list table. Each `nfs_client` owns a hostname string, address union array, exported flag, and reference count incremented by exports. State is freed by `client_freeall()` after export teardown.

## Dependencies and Integration Points
Depends on `sockaddr.h` address helpers, host resolution functions from `hostname.c`, `wildmat()`, libc resolver APIs, optional IPv6 and netgroup support, and `exportfs.h` structures. It is consumed by `export.c`, auth/cache matching, and etab rebuilds.

## Risks and Edge Cases
DNS and netgroup lookups can block or fail. Netmask parsing has family-specific rules and IPv6 code depends on compile flags. `client_member()` only matches comma-delimited exact names. The fallback netgroup IP check treats the first sockaddr as IPv4-shaped for `inet_ntop`, so mixed-family handling deserves care.

## Test Signals
Test identifier classification, IPv4 prefix and dotted masks, IPv6 prefix and explicit masks, wildcard aliases, netgroup present/absent builds, anonymous and GSS behavior, duplicate lookup reuse, and sorted `client_compose()` output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/export/client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/export/export.c -->
# sources/user-network-fs/nfs-utils/support/export/export.c

## Purpose
Maintains the in-core export list parsed from `/etc/exports`, `/etc/exports.d`, and etab state. It binds parsed `exportent` records to cached clients and indexes them by client type and path hash.

## Important APIs, Types, and Functions
Important APIs include `export_read()`, `export_d_read()`, `export_create()`, `export_lookup()`, `export_find()`, `export_freeall()`, `exportent_realpath()`, `exportent_release()`, and `export_test()`. Internal helpers duplicate exports, insert into `exportlist`, compute simple path hashes, and warn about duplicate export entries.

## Control Flow
`export_read()` iterates `getexportent()`, looks for an existing host/path export, creates new records, warns on duplicates, and rejects manual numeric fsid assignments when any `reexport=` option is present. `export_find()` searches all client classes for a caller/path match and duplicates non-FQDN exports into FQDN-specific exports. `export_test()` writes a test line to the nfsd export cache channel.

## State and Persistence Behavior
`exportlist[MCL_MAXTYPES]` is the process-global export index with linked-list heads and hash buckets. Each `nfs_export` owns a duplicated `exportent`, flags for xtab/export status, and a counted client reference. Real paths are lazily cached in `e_realpath` and released by `exportent_release()`.

## Dependencies and Integration Points
Depends on `nfslib.h` export parser APIs, `exportfs.h` client/export types, `nfsd_path` rootdir helpers, `xmalloc`, logging, and reexport policy. It integrates with `xtab.c`, `v4root.c`, auth/cache upcall processing, and exportfs CLI operations.

## Risks and Edge Cases
The path hash is simple and collision handling depends on linked-list bucket boundaries. Duplicate exports with incompatible flags are ignored after logging. Reexport/fsid validation is global after parsing. `export_test()` relies on procfs cache channels and buffer sizing.

## Test Signals
Use parser tests for duplicate exports, exports.d filtering and version sorting, chroot rootdir realpath handling, reexport with manual fsid rejection, wildcard-to-FQDN duplication, hash collisions, and kernel export test success/failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/export/export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/export/export.h -->
# sources/user-network-fs/nfs-utils/support/export/export.h

## Purpose
Declares the mountd/exportd support surface for authentication, cache upcall processing, NFSv4 client monitoring, export cache updates, and client match helpers.

## Important APIs, Types, and Functions
Exports `auth_reload()`, `auth_authenticate()`, cache loop functions, `v4clients_*()` functions, `cache_get_filehandle()`, `cache_export()`, worker controls, client match helpers, and inline `is_ipaddr_client()`.

## Control Flow
The header defines contracts only. Runtime flow is implemented in auth/cache/v4clients modules: callers set fd bits, process ready descriptors, export cache answers, and match caller domains or `$`-prefixed IP-address pseudo-clients.

## State and Persistence Behavior
No state is stored here. Declared modules own their descriptors, workers, and caches.

## Dependencies and Integration Points
Includes `nfslib.h` and `exportfs.h`. It is shared by mountd/exportd support code and hides implementation modules behind one internal header.

## Risks and Edge Cases
Because this is an internal aggregate header, prototype drift can create build or ABI mismatches across support/export modules. `is_ipaddr_client()` assumes non-NULL, non-empty strings.

## Test Signals
Build all export support objects together and compile auth/cache/v4clients users. Add unit checks for `$` client-domain classification if callers begin accepting untrusted empty strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/export/export.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/export/fsloc.c -->
# sources/user-network-fs/nfs-utils/support/export/fsloc.c

## Purpose
Parses export `refer=` and `replicas=` location data into the `servers` structure expected by nfsd export cache writers.

## Important APIs, Types, and Functions
Public APIs are `replicas_lookup()` and `release_replicas()`. Helpers include `method_list()`, `parse_list()`, debug-only `method_stub()`, and `replicas_print()`.

## Control Flow
`replicas_lookup()` dispatches on `FSLOC_NONE`, `FSLOC_REFER`, `FSLOC_REPLICA`, and debug stub methods. List data is split on unescaped colons while respecting bracketed IPv6 literals, then each `path@host[+host]` entry becomes a `mount_point`; plus signs in host lists are translated to colon separators for kernel output.

## State and Persistence Behavior
The returned `servers` object owns heap-allocated `mount_point`, host, and path strings and records whether data is referral or replica. `release_replicas()` frees the whole tree. No persistent storage is used.

## Dependencies and Integration Points
Depends on `fsloc.h`, `exportfs.h`, allocation/string routines, and `xlog`. Export cache serialization consumes the returned structures when writing `fs_locations` information to nfsd.

## Risks and Edge Cases
Malformed entries are logged and skipped, so partial lists may be accepted. The parser is bounded by `FSLOC_MAX_LIST`. IPv6 bracket handling only protects list splitting, not full address validation.

## Test Signals
Test referral and replica lists, multiple hosts with plus separators, bracketed IPv6 addresses, missing `@`, relative paths, overlong lists, and release behavior under partial allocation failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/export/fsloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/export/hostname.c -->
# sources/user-network-fs/nfs-utils/support/export/hostname.c

## Purpose
Centralizes hostname and numeric address conversion for export client matching, including strict presentation parsing and reliable reverse/forward lookup checks.

## Important APIs, Types, and Functions
Public functions are `host_ntop()`, `host_pton()`, `host_addrinfo()`, `host_canonname()`, `host_reliable_addrinfo()`, and `host_numeric_addrinfo()`.

## Control Flow
`host_pton()` first uses strict `inet_pton()` for IPv4 validation before `getaddrinfo(AI_NUMERICHOST)` to avoid accepting partial IPv4 strings. `host_addrinfo()` resolves names with canonical names. `host_reliable_addrinfo()` reverse-resolves an address, resolves that hostname forward, verifies the original address is present, then returns numeric addrinfo for the original sockaddr.

## State and Persistence Behavior
All returned names and addrinfo lists are heap-owned by callers. There is no global cache. Logging records resolver failures at parse/general debug levels.

## Dependencies and Integration Points
Depends on `sockaddr.h`, libc resolver APIs, optional `getnameinfo()`, `inet_ntop()`, `inet_pton()`, and `nfs_compare_sockaddr()`. Used heavily by `client.c` and auth matching.

## Risks and Edge Cases
DNS behavior can be slow or environment-dependent. Fallback code supports only IPv4. `host_pton()` deliberately rejects some strings `getaddrinfo()` would accept, which can surprise callers expecting legacy abbreviated IPv4.

## Test Signals
Test numeric IPv4/IPv6 conversion, invalid partial IPv4 such as `10.4`, reverse lookup failure, forward/reverse mismatch, unsupported families, and builds with and without `getnameinfo()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/export/hostname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/export/v4clients.c -->
# sources/user-network-fs/nfs-utils/support/export/v4clients.c

## Purpose
Monitors `/proc/fs/nfsd/clients` with inotify and logs NFSv4 client attach/detach events, including transitions from unconfirmed to confirmed client state.

## Important APIs, Types, and Functions
Public functions are `v4clients_init()`, `v4clients_set_fds()`, and `v4clients_process()`. Internal state uses `struct ent`, `tsearch()` tree management, `read_info()`, `add_id()`, `del_id()`, and `check_id()`.

## Control Flow
Initialization verifies the procfs clients directory, opens a nonblocking inotify fd, and watches for create/delete events. Processing reads inotify events, parses numeric client ids from names, adds/removes tree entries, and watches each client `info` file for modifications while unconfirmed. `read_info()` extracts clientid, address, minor version, and status lines.

## State and Persistence Behavior
Process-global state includes `clients_fd`, a search tree of `struct ent` records, per-client info-file watch ids, and `have_unconfirmed`. State is not persisted beyond log messages and kernel procfs watches.

## Dependencies and Integration Points
Depends on Linux inotify, `/proc/fs/nfsd/clients`, `search.h`, and `export.h` logging. It integrates with mountd/exportd select loops through fd-set helpers.

## Risks and Edge Cases
Only numeric event names are accepted. Lost inotify events, disappearing info files, and unexpected procfs formats can drop logs. Tree entries are keyed by client directory number, not clientid content.

## Test Signals
Test no-procfs behavior, inotify setup failure, create/delete/modify events, unconfirmed-to-confirmed attach logging, confirmed detach logging, malformed info files, and nonnumeric event names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/export/v4clients.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/export/v4root.c -->
# sources/user-network-fs/nfs-utils/support/export/v4root.c

## Purpose
Synthesizes NFSv4 pseudo-root exports for parent directories so NFSv4 clients can traverse to real exported paths even when those parents are not explicitly exported.

## Important APIs, Types, and Functions
Important functions include `v4root_set()`, `v4root_add_parents()`, `pseudofs_update()`, `v4root_create()`, `v4root_support()`, and `set_pseudofs_security()`. It uses a static `pseudo_root` template export.

## Control Flow
`v4root_set()` exits unless pseudo roots are needed and kernel features advertise `NFSEXP_V4ROOT`. It walks all exports, forces `/` to fsid 0 when needed, and creates or updates pseudo exports for each path prefix. Non-root pseudo exports may get deterministic UUIDs from a fixed seed when kernel export testing without fsid fails.

## State and Persistence Behavior
Creates new entries in the global export list through `export_create()`. `v4root_needed` is set by etab reads. Pseudo exports are in-memory until normal etab/cache write paths persist or communicate them.

## Dependencies and Integration Points
Depends on `exportfs.h`, `nfslib.h`, `misc.h`, `v4root.h`, `pseudoflavors.h`, libuuid, kernel export feature probing, and `/etc/krb5.keytab` presence for security flavor filtering.

## Risks and Edge Cases
Error handling is limited in the main walk. Security flavor choices depend on local keytab existence. Deterministic UUID generation strips hyphens and relies on fixed seed behavior. Existing non-V4ROOT exports block pseudo replacement.

## Test Signals
Test kernel feature absent/present, export of `/` without fsid, nested path parent creation, existing pseudo update, krb5 keytab gating, export_test failure UUID generation, and repeated `v4root_set()` idempotence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/export/v4root.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/export/xtab.c -->
# sources/user-network-fs/nfs-utils/support/export/xtab.c

## Purpose
Reads and writes the etab export-state file and manages paths under the nfs-utils state directory. It preserves mountd/exportfs shared state with locking and atomic replacement.

## Important APIs, Types, and Functions
Public APIs are `xtab_export_read()`, `xtab_export_write()`, `state_setup_basedir()`, `setup_state_path_names()`, and `free_state_path_names()`. Internal helpers are `xtab_read()`, `xtab_write()`, `cond_rename()`, and `state_make_pathname()`.

## Control Flow
`xtab_read()` locks etab for reading, parses export entries, creates or updates in-core exports, marks `m_xtabent` and `m_mayexport`, and disables dynamic v4root generation when fsid 0 is present. `xtab_write()` writes marked exports to a temp file using canonical client hostnames, then renames only if content differs.

## State and Persistence Behavior
Persists export state in `etab.statefn`, `etab.tmpfn`, and `etab.lockfn`, all derived from `state_base_dirname`. `v4root_needed` is process-global. File replacement intentionally changes inode when content changes for auth reload detection.

## Dependencies and Integration Points
Depends on `nfslib.h` parser/writer functions, `xio` locks, `exportfs.h`, `v4root.h`, `misc.h` path helpers, and state directory macros. Used by mountd/exportfs state synchronization.

## Risks and Edge Cases
Parser cleanup manually frees selected fields after `getexportent()`. `cond_rename()` ignores some open/read errors. State setup runs before logging and reports to stderr. Content-identical writes unlink temp files and do not refresh inode.

## Test Signals
Test read/write locking, fsid 0 v4root detection, malformed entries, temp rename with identical and changed files, missing state dir, long path names, and auth reload behavior tied to etab inode replacement.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/export/xtab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/Makefile.am -->
# sources/user-network-fs/nfs-utils/support/include/Makefile.am

## Purpose
Automake metadata that defines which private headers or support sources are built in this directory and marks generated `Makefile.in` for maintainer cleanup.

## Important APIs, Types, and Functions
No C APIs are defined. The meaningful variables are `SUBDIRS`, `noinst_HEADERS`, `noinst_LIBRARIES`, `noinst_LTLIBRARIES`, and per-library source lists.

## Control Flow
During autoreconf/automake, this file is expanded into a makefile fragment. Recursive subdirectories are entered first when `SUBDIRS` is set, and listed headers/sources are packaged into private build artifacts.

## State and Persistence Behavior
No runtime state exists. Build artifacts such as `Makefile.in`, static libraries, or libtool archives are generated outside this source file.

## Dependencies and Integration Points
Integrates with the nfs-utils autotools build. Correctness is visible through generated make rules and successful compilation of dependent support libraries.

## Risks and Edge Cases
The main risk is drift between source files and the Automake lists, which can omit headers from distribution or omit sources from a support library.

## Test Signals
Run autoreconf/automake, `make distcheck` or a clean build, and verify all listed headers and support sources are included in generated makefiles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/cld.h -->
# sources/user-network-fs/nfs-utils/support/include/cld.h

## Purpose
Defines the packed nfsdcld upcall ABI used for NFSv4 client tracking and reclaim decisions.

## Important APIs, Types, and Functions
`CLD_UPCALL_VERSION`, `NFS4_OPAQUE_LIMIT`, `enum cld_command`, `struct cld_name`, `struct cld_princhash`, `struct cld_clntinfo`, `struct cld_msg`, `struct cld_msg_v2`, and `struct cld_msg_hdr`.

## Control Flow
Kernel/userspace messages carry a version, command, status, xid, and command-specific union payload. Version 2 can include client name plus Kerberos principal hash.

## State and Persistence Behavior
No code executes here; the packed struct layout is the persistent wire/shared-memory contract between nfsd and nfsdcld.

## Dependencies and Integration Points
Depends on fixed-width integer types from consumers. Integrated by nfsdcld and kernel upcall handling.

## Risks and Edge Cases
Packed layout, signed status width, and opaque length limits must remain ABI-compatible. Version negotiation is required before using v2-only fields.

## Test Signals
Compile-time size/layout checks and integration tests for create/remove/check/grace/version upcalls across v1/v2 peers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/cld.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/compat.h -->
# sources/user-network-fs/nfs-utils/support/include/compat.h

## Purpose
Provides small compatibility definitions missing from older system headers.

## Important APIs, Types, and Functions
Defines `NETLINK_EXT_ACK` as 11 when absent.

## Control Flow
Included before code calls `setsockopt(..., NETLINK_EXT_ACK, ...)` so older build hosts still compile.

## State and Persistence Behavior
No runtime state. It only affects preprocessing.

## Dependencies and Integration Points
Depends on `<linux/netlink.h>` and is used by netlink support such as cache flushing.

## Risks and Edge Cases
If a platform uses a different value, the fallback would be wrong; this mirrors Linux UAPI.

## Test Signals
Build against old and new kernel headers and verify netlink extended ACK setup compiles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/conffile.h -->
# sources/user-network-fs/nfs-utils/support/include/conffile.h

## Purpose
Declares a section/key configuration parser interface used by nfs-utils daemons and support helpers.

## Important APIs, Types, and Functions
`struct conf_list_node`, `struct conf_list`, `conf_begin/end`, getters for strings, bools, numbers, sections, lists, addresses, mutation/write helpers, `conf_cleanup()`, `modified_by`, and inline `upper2lower()`.

## Control Flow
Callers initialize a config file, query section/key values through typed getters, optionally write/remove entries, report state, and cleanup. List results use TAILQ-backed nodes.

## State and Persistence Behavior
Parser state is owned by the implementation. Returned strings/lists generally require caller cleanup via documented functions. Config files are persistent external state.

## Dependencies and Integration Points
Depends on BSD queue macros, stdio, ctype, fixed-width types, and socket address declarations. Used by `nfsd_path.c` for `exports.rootdir` and other daemon config consumers.

## Risks and Edge Cases
Ownership rules vary by getter, and config changes can affect chroot/rootdir behavior globally. `upper2lower()` stops on `tolower(*str) == 0`, so input must be NUL-terminated.

## Test Signals
Test typed lookup defaults, missing sections, list cleanup, address parsing, writes/removes, base64 decode, and mixed-case normalization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/conffile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/exportfs.h -->
# sources/user-network-fs/nfs-utils/support/include/exportfs.h

## Purpose
Defines the central export/client data model and function declarations shared by exportfs, mountd, auth, cache, and pseudo-root code.

## Important APIs, Types, and Functions
Key types are `nfs_client`, `nfs_export`, `exp_hash_entry`, `exp_hash_table`, `export_features`, and client class enums. Inline helpers get/set AF_INET/AF_INET6 address slots. It declares client, export, xtab, secinfo, hostname, feature, realpath, and export-test APIs.

## Control Flow
Implementation modules parse export entries into `nfs_export`, associate them with `nfs_client`, hash by path, match callers by addrinfo, and persist/read etab state. Inline address helpers hide union field access.

## State and Persistence Behavior
`exportlist` and `clientlist` are extern process-global tables. Export entries own dynamically allocated option fields and cached real paths; etab paths persist state on disk.

## Dependencies and Integration Points
Depends on `nfslib.h`, `sockaddr.h`, and libc networking headers. This is the primary integration header for support/export modules.

## Risks and Edge Cases
ABI and ownership expectations are implicit. Address setters silently ignore unsupported families. Bitfield state in `nfs_export` must stay consistent with etab/cache operations.

## Test Signals
Build all export modules, test client/export lifecycle, address helpers with IPv4/IPv6, etab read/write, feature probing, and duplicate/free paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/exportfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/fsloc.h -->
# sources/user-network-fs/nfs-utils/support/include/fsloc.h

## Purpose
Declares the simple NFSv4 fs_locations representation used by export option parsing.

## Important APIs, Types, and Functions
`FSLOC_MAX_LIST`, `struct mount_point`, `struct servers`, `replicas_lookup()`, and `release_replicas()`.

## Control Flow
Callers pass a method and location string to `replicas_lookup()`, then serialize returned mount points to kernel export cache data and release them.

## State and Persistence Behavior
Returned structures own heap strings and are not persisted directly. Export options remain the durable source.

## Dependencies and Integration Points
Implemented by `support/export/fsloc.c` and consumed by export cache writers.

## Risks and Edge Cases
Fixed maximum list size can truncate large location sets. `h_referral` is an int flag whose meaning must be preserved.

## Test Signals
Test refer/replica method parsing, empty/invalid data, maximum list size, and release cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/fsloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/ha-callout.h -->
# sources/user-network-fs/nfs-utils/support/include/ha-callout.h

## Purpose
Implements inline high-availability callout execution for mountd/statd event hooks.

## Important APIs, Types, and Functions
Defines global `ha_callout_prog` and inline `ha_callout(event,arg1,arg2,arg3)`, which forks and execs the configured script.

## Control Flow
If no program is configured the call returns. Otherwise it formats `arg3`, temporarily restores default `SIGCHLD`, forks, execs the script with event arguments, waits, restores the signal action, and logs the exit status.

## State and Persistence Behavior
No persistent state beyond external script effects. It temporarily mutates process `SIGCHLD` handling and waits for one child.

## Dependencies and Integration Points
Depends on fork/exec/wait/sigaction and `xlog`. Integrated by daemons that support HA event scripts.

## Risks and Edge Cases
Inline code in a header pulls process-control behavior into all users. `WEXITSTATUS` is used without checking normal exit. Script path and arguments are trusted process configuration.

## Test Signals
Test disabled mode, fork/exec failure, negative and nonnegative arg3, SIGCHLD restoration, and script exit logging.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/ha-callout.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/junction.h -->
# sources/user-network-fs/nfs-utils/support/include/junction.h

## Purpose
Public libjunction interface for managing FedFS/NFS junctions and NFS fileset location data stored on local filesystems.

## Important APIs, Types, and Functions
Defines `FedFsStatus`, `struct nfs_fsloc`, allocation/free helpers, junction CRUD/predicate APIs, cache flush, path conversion helpers, and status display helpers.

## Control Flow
Callers construct linked `nfs_fsloc` records, call `nfs_add_junction()` to serialize them into a directory xattr, query via `nfs_get_locations()`, and remove via `nfs_delete_junction()`. Status values are FedFS protocol-style rather than errno.

## State and Persistence Behavior
Location records own hostname/rootpath strings. Junctions persist as trusted xattrs and mode-bit changes on directories; helper functions allocate caller-owned structures.

## Dependencies and Integration Points
Implemented by `support/junction/*.c`, using libxml2, xattrs, and procfs cache flushing. Used by tools and export cache junction discovery.

## Risks and Edge Cases
Requires CAP_SYS_ADMIN for trusted xattrs. Struct fields mirror NFSv4 fs_locations semantics and must remain compatible with XML serialization.

## Test Signals
Test allocation/free, path conversion, add/get/delete junction round trips, status display, and permission/error mappings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/junction.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/lockd_netlink.h -->
# sources/user-network-fs/nfs-utils/support/include/lockd_netlink.h

## Purpose
Generated Linux UAPI mirror for lockd generic netlink commands.

## Important APIs, Types, and Functions
Defines `LOCKD_FAMILY_NAME`, version, server attributes, and server set/get commands.

## Control Flow
Consumers use these constants to build or parse generic netlink messages for lockd server configuration.

## State and Persistence Behavior
No runtime state; the header is an ABI constant set.

## Dependencies and Integration Points
Generated from kernel `lockd.yaml` and used by nfs-utils netlink tooling when system headers are unavailable.

## Risks and Edge Cases
Must track kernel UAPI. Manual edits risk command or attribute mismatch.

## Test Signals
Compile against bundled and system headers and test lockd netlink get/set message construction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/lockd_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/misc.h -->
# sources/user-network-fs/nfs-utils/support/include/misc.h

## Purpose
Collects small shared support declarations for random keys, state path helpers, mountpoint checks, and RPC procfs buffer sizing.

## Important APIs, Types, and Functions
Declares `randomkey()`, `weakrandomkey()`, `generic_make_pathname()`, `generic_setup_basedir()`, `check_is_mountpoint()`, `is_mountpoint()`, and `RPC_CHAN_BUF_SIZE`.

## Control Flow
Implementations allocate state paths, validate base directories, generate keys, and determine mountpoints by stat comparisons.

## State and Persistence Behavior
No state is stored here. Implementations may inspect filesystem state and return heap path strings.

## Dependencies and Integration Points
Used by export state setup, mountpoint checks, and procfs cache readers.

## Risks and Edge Cases
Weak random keys are explicitly not strong. Mountpoint checks rely on stat behavior and symlink/lstat choice.

## Test Signals
Test path length limits, base directory validation, mountpoint detection, and randomkey length/error behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/misc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nfs/Makefile.am -->
# sources/user-network-fs/nfs-utils/support/include/nfs/Makefile.am

## Purpose
Automake metadata that defines which private headers or support sources are built in this directory and marks generated `Makefile.in` for maintainer cleanup.

## Important APIs, Types, and Functions
No C APIs are defined. The meaningful variables are `SUBDIRS`, `noinst_HEADERS`, `noinst_LIBRARIES`, `noinst_LTLIBRARIES`, and per-library source lists.

## Control Flow
During autoreconf/automake, this file is expanded into a makefile fragment. Recursive subdirectories are entered first when `SUBDIRS` is set, and listed headers/sources are packaged into private build artifacts.

## State and Persistence Behavior
No runtime state exists. Build artifacts such as `Makefile.in`, static libraries, or libtool archives are generated outside this source file.

## Dependencies and Integration Points
Integrates with the nfs-utils autotools build. Correctness is visible through generated make rules and successful compilation of dependent support libraries.

## Risks and Edge Cases
The main risk is drift between source files and the Automake lists, which can omit headers from distribution or omit sources from a support library.

## Test Signals
Run autoreconf/automake, `make distcheck` or a clean build, and verify all listed headers and support sources are included in generated makefiles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nfs/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nfs/debug.h -->
# sources/user-network-fs/nfs-utils/support/include/nfs/debug.h

## Purpose
Defines legacy debug bit masks for sunrpc, nfsd, lockd, and NFS client debug controls.

## Important APIs, Types, and Functions
Macros include `RPCDBG_*`, `NFSDDBG_*`, `NLMDBG_*`, `NFSDBG_*`, `CTL_SUNRPC`, and debug sysctl enum values.

## Control Flow
Consumers OR, set, or display bit flags for kernel debug facilities; no control flow is implemented here.

## State and Persistence Behavior
No runtime state. Values are ABI/configuration constants.

## Dependencies and Integration Points
Included by utilities that read or change kernel debug flags.

## Risks and Edge Cases
Values must match kernel expectations. Some sysctl paths are legacy and may be absent on modern kernels.

## Test Signals
Compile debug utilities and test setting/listing each debug facility against kernels with and without legacy sysctl support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nfs/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nfs/export.h -->
# sources/user-network-fs/nfs-utils/support/include/nfs/export.h

## Purpose
Defines nfsd export limits and `NFSEXP_*` flag values shared by user-space export code and kernel cache protocols.

## Important APIs, Types, and Functions
Provides client/path size limits, export option flag masks, old-kernel feature masks, transport security flags, and `NFSEXP_XPRTSEC_*` helpers.

## Control Flow
Export parsers, feature probes, pseudo-root code, and cache writers set/test these bits when building export entries and kernel upcall responses.

## State and Persistence Behavior
No state. Flags become persistent when written to etab or sent to kernel caches.

## Dependencies and Integration Points
Included through `nfs/nfs.h` and `nfslib.h`. Must align with Linux nfsd export flags.

## Risks and Edge Cases
Flag drift breaks export semantics. Reserved or old-feature masks need care when supporting older kernels.

## Test Signals
Test option parsing to flags, kernel feature filtering, transport security serialization, and old-kernel compatibility paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nfs/export.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nfs/nfs.h -->
# sources/user-network-fs/nfs-utils/support/include/nfs/nfs.h

## Purpose
Defines generic NFS protocol limits, version/protocol bit helpers, and length-tagged NFS filehandle storage.

## Important APIs, Types, and Functions
`struct nfs_fh_len`, `NFS3_FHSIZE`, version/minor constants, and `NFSCTL_*` macros for protocol/version bitsets.

## Control Flow
Callers manipulate integer bitsets to enable/disable NFS versions, minor versions, UDP/TCP, and defaults. Filehandle users carry size plus bytes.

## State and Persistence Behavior
No state. Bitsets are caller-owned and may persist in daemon configuration or kernel setup commands.

## Dependencies and Integration Points
Includes Linux types, RPC NFSv2 protocol declarations, and export flags. Used across mountd/nfsdctl/export support.

## Risks and Edge Cases
Macros mutate arguments, so side effects in macro arguments are unsafe. Minor-version default comments must match bit values.

## Test Signals
Test bitset set/unset/is-set operations, default masks, any-protocol checks, and filehandle size bounds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nfs/nfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nfs_mntent.h -->
# sources/user-network-fs/nfs-utils/support/include/nfs_mntent.h

## Purpose
Declares a mount-table parser/writer wrapper derived from util-linux mount entry handling.

## Important APIs, Types, and Functions
Defines `mntFILE` with FILE pointer, pathname, line number, and error counters, plus `nfs_setmntent()`, `nfs_endmntent()`, `nfs_addmntent()`, `my_getmntent()`, and `nfs_getmntent()`.

## Control Flow
Callers open a mount table through `nfs_setmntent()`, iterate or add entries, track parse errors, and close with `nfs_endmntent()`.

## State and Persistence Behavior
Parser state is stored in `mntFILE`. Persistent state is the mounted/fstab file being read or written.

## Dependencies and Integration Points
Depends on `<mntent.h>` and support implementation files. Used by mount utilities.

## Risks and Edge Cases
Error thresholds and soft-error handling are implementation-defined. Callers must not mix raw FILE operations with wrapper state.

## Test Signals
Test malformed mount entries, write/add paths, line/error counters, and close cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nfs_mntent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nfs_paths.h -->
# sources/user-network-fs/nfs-utils/support/include/nfs_paths.h

## Purpose
Defines fallback paths and lock/temp names for the mounted filesystem table.

## Important APIs, Types, and Functions
Defines `_PATH_MOUNTED`, `MOUNTED_LOCK`, and `MOUNTED_TEMP`.

## Control Flow
Mount helpers use these names when updating mounted table state.

## State and Persistence Behavior
No runtime state. Constants refer to persistent files.

## Dependencies and Integration Points
Included by mount support code where system path macros may be absent.

## Risks and Edge Cases
Defaulting `_PATH_MOUNTED` to `/etc/fstab` is unusual for mounted-state updates and depends on surrounding code expectations.

## Test Signals
Build mount utilities and verify configured path macros override these fallbacks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nfs_paths.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nfs_ucred.h -->
# sources/user-network-fs/nfs-utils/support/include/nfs_ucred.h

## Purpose
Declares credential helpers used to execute filesystem operations under NFS request credentials and export squash policy.

## Important APIs, Types, and Functions
`struct nfs_ucred`, `nfs_ucred_get()`, group squash/reload helpers, `nfs_ucred_swap_effective()`, and inline free/init/free-groups helpers.

## Control Flow
Callers derive credentials from RPC requests and export options, adjust supplemental groups, swap process effective credentials around sensitive operations, then restore and free.

## State and Persistence Behavior
Credential objects own a heap group array. Effective uid/gid/group state is process-global while swapped, so callers must restore carefully.

## Dependencies and Integration Points
Used by `nfsd_path.c` openat wrappers and auth/export code. Depends on RPC request and `exportent` types.

## Risks and Edge Cases
Credential swapping can affect all threads if not serialized. Ownership of saved credentials must be followed exactly.

## Test Signals
Test squash rules, group reload, swap/restore on success and failure, and `nfsd_cred_openat()` permission behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nfs_ucred.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nfsd_netlink.h -->
# sources/user-network-fs/nfs-utils/support/include/nfsd_netlink.h

## Purpose
Generated Linux nfsd generic netlink UAPI mirror for server control, cache notifications, export/expkey requests, fs_locations, security flavors, and unlock commands.

## Important APIs, Types, and Functions
Defines family/version, cache types, export flags, xprtsec modes, many `NFSD_A_*` attribute enums, and `NFSD_CMD_*` commands.

## Control Flow
Netlink clients use these constants to subscribe to nfsd cache notifications, retrieve pending export/expkey requests, set responses, configure server threads/protocols/sockets, and flush caches.

## State and Persistence Behavior
No state. It encodes a kernel userspace ABI.

## Dependencies and Integration Points
Used by export cache netlink code, cache flushing, and nfsd control tools when system UAPI headers are unavailable.

## Risks and Edge Cases
Must remain synchronized with kernel `nfsd.yaml`. Attribute nesting and flag numeric alignment with `NFSEXP_*` are critical.

## Test Signals
Build with bundled/system UAPI switches and run netlink export cache, cache flush, and nfsdctl command tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nfsd_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nfsd_path.h -->
# sources/user-network-fs/nfs-utils/support/include/nfsd_path.h

## Purpose
Declares chroot/rootdir-aware filesystem wrappers used by nfsd export support.

## Important APIs, Types, and Functions
APIs include `nfsd_path_init()`, rootdir get/strip/prepend helpers, stat/lstat/statfs/realpath, credential-aware `openat`, read/write wrappers, `nfsd_name_to_handle_at()`, and inline `nfsd_openat()`.

## Control Flow
When `exports.rootdir` is configured, implementation uses a worker chrooted into that rootdir to run filesystem calls. Otherwise wrappers call system APIs directly.

## State and Persistence Behavior
The implementation owns a process-global workqueue. Filesystem effects and file descriptors are caller-visible; rootdir configuration persists in config file state.

## Dependencies and Integration Points
Used by export realpath, cache channel writes, filehandle lookup, and export path validation. Depends on `nfs_ucred` and workqueue support.

## Risks and Edge Cases
Chrooted workers and credential swaps are sensitive to threading and errno propagation. `strip_root()` returns interior pointers or NULL.

## Test Signals
Test rootdir unset/set, stat/lstat/statfs/realpath under chroot, credential open failures, read/write errno, and name_to_handle_at fallback.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nfsd_path.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nfsdnl.h -->
# sources/user-network-fs/nfs-utils/support/include/nfsdnl.h

## Purpose
Declares a helper for sending simple string-attribute commands to the nfsd generic netlink family.

## Important APIs, Types, and Functions
`nfsd_nl_cmd_str(cmd, attr, value)` is real when `HAVE_NFSD_NETLINK` is enabled and an inline `-ENOSYS` stub otherwise.

## Control Flow
Callers issue one nfsd netlink command carrying one string attribute, wait for ACK, and receive 0 or negative errno.

## State and Persistence Behavior
No state in the header. The implementation opens and closes netlink sockets per command.

## Dependencies and Integration Points
Used by nfsdctl/exportfs-style control code. Depends on nfsd netlink command and attribute constants.

## Risks and Edge Cases
Callers must handle `-ENOSYS` when netlink support is absent and negative errno when the family or command is unsupported.

## Test Signals
Build both netlink-enabled and disabled configurations and test command success, unknown family/attr, and ACK error paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nfsdnl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nfslib.h -->
# sources/user-network-fs/nfs-utils/support/include/nfslib.h

## Purpose
Primary shared support header for nfs-utils, including export entry structures, state path names, qword cache encoding helpers, daemon setup, RPC sockets, and utility prototypes.

## Important APIs, Types, and Functions
Defines `struct state_paths`, `struct sec_entry`, `struct xprtsec_entry`, `struct exportent`, `struct rmtabent`, SEC/XPRTSEC counts, path macros, parser/writer APIs, rmtab APIs, cache qword helpers, daemon helpers, socket helpers, `atomicio()`, and inline `nfs_freeaddrinfo()`.

## Control Flow
Export and rmtab users open parser state, iterate entries, write updates, and close. Cache code qword-encodes strings and integers for procfs channels. Daemons initialize, signal readiness, and create RPC sockets through declared helpers.

## State and Persistence Behavior
Persistent state includes exports, etab, rmtab, and daemon-managed files. `exportent` owns many heap option fields and cached real path data that must be released by export code.

## Dependencies and Integration Points
This header ties together rpcsvc NFS protocol, export flags, uuid, logging, mountd/exportfs parsers, statd state, and generic utility code.

## Risks and Edge Cases
It is broad and ownership-heavy. `exportent` option arrays/strings require disciplined duplication and release. Constants define protocol-visible limits.

## Test Signals
Full nfs-utils build, exports/rmtab parser round trips, qword encoding/decoding tests, daemon socket tests, and memory leak checks around `exportent` duplication/free.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nfslib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nfsrpc.h -->
# sources/user-network-fs/nfs-utils/support/include/nfsrpc.h

## Purpose
Declares RPC client utility functions for NFS, mount, lockd, statd, rpcbind, and portmap interactions.

## Important APIs, Types, and Functions
Defines program constants, `NFSPROTO_RDMA`, `nfs_clear_rpc_createerr()`, RPC client constructors, netid/protocol conversion, universal address helpers, port lookup/ping APIs, statd probe, and `nfs_authsys_create()`.

## Control Flow
Callers resolve program names, acquire privileged or ephemeral RPC clients, map service tuples to ports through rpcbind/portmap, ping remote services, and create AUTH_SYS handles.

## State and Persistence Behavior
No state except libc/libtirpc `rpc_createerr`, cleared by inline helper. Network queries observe remote rpcbind/statd state.

## Dependencies and Integration Points
Depends on libtirpc/SunRPC headers and socket address data. Used by mount, statd, lockd, and NFS service discovery code.

## Risks and Edge Cases
RPC timeouts, privileged port binding, IPv6/universal address formatting, and RDMA pseudo-protocol handling are portability risks.

## Test Signals
Test tcp/udp/rdma netid conversion, rpcbind and portmap lookups, ping timeouts, privileged client binding, and statd probe behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nfsrpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nls.h -->
# sources/user-network-fs/nfs-utils/support/include/nls.h

## Purpose
Provides gettext/no-gettext translation macros for nfs-utils command output.

## Important APIs, Types, and Functions
Defines `LOCALEDIR`, `_()`, and `N_()` depending on `ENABLE_NLS`, and stubs `bindtextdomain()`/`textdomain()` when NLS is disabled.

## Control Flow
Translatable strings are wrapped at compile time. With NLS enabled they call gettext; otherwise strings are returned unchanged.

## State and Persistence Behavior
No project state. Runtime gettext may read locale catalogs.

## Dependencies and Integration Points
Used by command-line tools that need optional localization.

## Risks and Edge Cases
Macro stubs can hide missing gettext initialization in non-NLS builds. `LOCALEDIR` fallback must match installation layout.

## Test Signals
Build with and without `ENABLE_NLS`, run output smoke tests under different locales, and verify catalog lookup paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nsm.h -->
# sources/user-network-fs/nfs-utils/support/include/nsm.h

## Purpose
Declares Network Status Monitor support for rpc.statd state files, monitor/notify lists, and NSM RPC packet helpers.

## Important APIs, Types, and Functions
Defines `nsm_populate_t`, path/state/list management APIs, host insert/delete helpers, private-data hex conversion, NSM transmit/receive functions, and `NSM_MAXMSGSIZE`.

## Control Flow
Statd setup initializes pathnames and privileges, loads monitor/notify lists through callbacks, updates kernel state, and uses XDR helpers to send/parse rpcbind, notify, and NLM call messages.

## State and Persistence Behavior
Persistent state is statd monitor/notify directories and kernel NSM state. RPC functions operate on sockets and XDR streams.

## Dependencies and Integration Points
Depends on sockets, netdb, time, `sm_inter.h`, and RPC/XDR types. Integrated by rpc.statd file and RPC implementations.

## Risks and Edge Cases
State file migration, privilege dropping, IPv4/IPv6 rpcbind differences, and XDR bounds are key risks.

## Test Signals
Test state path setup, monitor insertion/deletion, notify list loading, private hex conversion, rpcbind getport/getaddr parsing, and malformed XDR replies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/nsm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/pseudoflavors.h -->
# sources/user-network-fs/nfs-utils/support/include/pseudoflavors.h

## Purpose
Defines RPCSEC_GSS pseudoflavor numbers and the security flavor lookup table contract.

## Important APIs, Types, and Functions
`RPC_AUTH_GSS_KRB5*` constants, `struct flav_info`, extern `flav_map[]`, and `flav_map_size`.

## Control Flow
Export option parsing and pseudo-root security setup iterate `flav_map`, check flavor numbers and krb5 requirements, then add secinfo entries.

## State and Persistence Behavior
No state here besides extern table declarations. Security choices can persist in export entries and kernel cache replies.

## Dependencies and Integration Points
Used by `v4root.c`, export option parsing, and secinfo serialization.

## Risks and Edge Cases
Numbers must match kernel/RPCSEC_GSS assignments. `need_krb5` behavior depends on local keytab checks in consumers.

## Test Signals
Test flavor parsing, secinfo output for krb5/krb5i/krb5p, and pseudo-root behavior with and without keytab.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/pseudoflavors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/rpcmisc.h -->
# sources/user-network-fs/nfs-utils/support/include/rpcmisc.h

## Purpose
Declares shared RPC server registration and dispatch helpers.

## Important APIs, Types, and Functions
Defines `rpcsvc_fn_t`, `struct rpc_dentry`, `struct rpc_dtable`, `dtable_ent()` macro, service create/unregister/init/dispatch functions, globals for rpcbind/service state, and caller sockaddr helpers.

## Control Flow
Daemons build dispatch tables from XDR and service functions, register RPC programs/transports, and dispatch incoming requests through `rpc_dispatch()` by procedure number.

## State and Persistence Behavior
Global `_rpcpmstart`, `_rpcprotobits`, and `_rpcsvcdirty` track RPC service setup. Server registration persists in rpcbind/portmap until unregistered.

## Dependencies and Integration Points
Depends on libtirpc/SunRPC server headers. Used by statd, mountd, and other RPC daemons.

## Risks and Edge Cases
Procedure table sizes and XDR function casts must match generated RPC code. Caller sockaddr helpers expose transport-owned storage.

## Test Signals
Test service registration/unregistration, dispatch of known and unknown procedures, XDR decode failures, and caller address extraction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/rpcmisc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/rpcsvc/Makefile.am -->
# sources/user-network-fs/nfs-utils/support/include/rpcsvc/Makefile.am

## Purpose
Automake metadata that defines which private headers or support sources are built in this directory and marks generated `Makefile.in` for maintainer cleanup.

## Important APIs, Types, and Functions
No C APIs are defined. The meaningful variables are `SUBDIRS`, `noinst_HEADERS`, `noinst_LIBRARIES`, `noinst_LTLIBRARIES`, and per-library source lists.

## Control Flow
During autoreconf/automake, this file is expanded into a makefile fragment. Recursive subdirectories are entered first when `SUBDIRS` is set, and listed headers/sources are packaged into private build artifacts.

## State and Persistence Behavior
No runtime state exists. Build artifacts such as `Makefile.in`, static libraries, or libtool archives are generated outside this source file.

## Dependencies and Integration Points
Integrates with the nfs-utils autotools build. Correctness is visible through generated make rules and successful compilation of dependent support libraries.

## Risks and Edge Cases
The main risk is drift between source files and the Automake lists, which can omit headers from distribution or omit sources from a support library.

## Test Signals
Run autoreconf/automake, `make distcheck` or a clean build, and verify all listed headers and support sources are included in generated makefiles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/rpcsvc/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/rpcsvc/nfs_prot.h -->
# sources/user-network-fs/nfs-utils/support/include/rpcsvc/nfs_prot.h

## Purpose
Rpcgen-generated NFSv2 protocol header containing constants, XDR type declarations, and client/server stubs for program 100003 version 2.

## Important APIs, Types, and Functions
Defines NFS status and file type enums, filehandle, attributes, argument/result structs for NFSv2 procedures, XDR prototypes, `NFS_PROGRAM`, `NFS_VERSION`, and `nfsproc_*_2` client/server prototypes.

## Control Flow
RPC clients and servers marshal data through the declared `xdr_*` functions and call/implement the procedure stubs for NULL, GETATTR, SETATTR, LOOKUP, READ, WRITE, CREATE, REMOVE, RENAME, LINK, SYMLINK, MKDIR, RMDIR, READDIR, and STATFS.

## State and Persistence Behavior
No runtime state in the header. Structures define the wire format and must remain compatible with generated XDR implementation.

## Dependencies and Integration Points
Included by `nfslib.h` and RPC modules. Depends on `<rpc/rpc.h>` and rpcgen conventions.

## Risks and Edge Cases
Manual edits to generated layouts break wire compatibility. `struct entry` name conflicts with libc `search.h`, as seen in `v4clients.c` workaround.

## Test Signals
Compile generated XDR sources, run NFSv2 RPC marshalling tests, and verify procedure table integration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/rpcsvc/nfs_prot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/sockaddr.h -->
# sources/user-network-fs/nfs-utils/support/include/sockaddr.h

## Purpose
Provides alias-safe socket address storage and inline helpers for address length, ports, equality, and loopback checks.

## Important APIs, Types, and Functions
`union nfs_sockaddr`, size macros, `nfs_sockaddr_length()`, `nfs_get_port()`, `nfs_set_port()`, `nfs_is_v4_loopback()`, `nfs_compare_sockaddr()`, and family-specific helpers.

## Control Flow
Callers store IPv4/IPv6 addresses in the union, query the family-specific length, get/set network-order ports, and compare addresses while respecting IPv6 link-local scope ids.

## State and Persistence Behavior
No state. It manipulates caller-owned sockaddr buffers.

## Dependencies and Integration Points
Used throughout client matching, hostname resolution, RPC helper code, and local-address checks.

## Risks and Edge Cases
The union is intentionally smaller than `sockaddr_storage` and unsuitable for AF_LOCAL. IPv6 helpers compile to no-ops/false when disabled.

## Test Signals
Test IPv4 and IPv6 length/port/equality, link-local scope mismatch, unsupported family handling, and no-IPv6 builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/sockaddr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/sunrpc_netlink.h -->
# sources/user-network-fs/nfs-utils/support/include/sunrpc_netlink.h

## Purpose
Generated Linux sunrpc cache generic netlink UAPI mirror for IP map, UNIX GID, cache notification, request subscription, and cache flush operations.

## Important APIs, Types, and Functions
Defines `SUNRPC_FAMILY_NAME`, cache types, `SUNRPC_A_*` attribute enums, `SUNRPC_CMD_*` commands, and multicast group names.

## Control Flow
Export/cache daemons use these constants to watch pending sunrpc cache requests, answer IP/GID mappings, receive notifications, or flush caches.

## State and Persistence Behavior
No runtime state. Constants describe kernel ABI.

## Dependencies and Integration Points
Used by export cache netlink processing and `cache_flush.c` fallback selection when system headers are unavailable.

## Risks and Edge Cases
Must track kernel `sunrpc_cache.yaml`; attribute mismatches break cache upcall handling.

## Test Signals
Build with bundled/system UAPI headers and test IP map, UNIX GID, notification, and flush netlink paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/sunrpc_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/sys/Makefile.am -->
# sources/user-network-fs/nfs-utils/support/include/sys/Makefile.am

## Purpose
Automake metadata that defines which private headers or support sources are built in this directory and marks generated `Makefile.in` for maintainer cleanup.

## Important APIs, Types, and Functions
No C APIs are defined. The meaningful variables are `SUBDIRS`, `noinst_HEADERS`, `noinst_LIBRARIES`, `noinst_LTLIBRARIES`, and per-library source lists.

## Control Flow
During autoreconf/automake, this file is expanded into a makefile fragment. Recursive subdirectories are entered first when `SUBDIRS` is set, and listed headers/sources are packaged into private build artifacts.

## State and Persistence Behavior
No runtime state exists. Build artifacts such as `Makefile.in`, static libraries, or libtool archives are generated outside this source file.

## Dependencies and Integration Points
Integrates with the nfs-utils autotools build. Correctness is visible through generated make rules and successful compilation of dependent support libraries.

## Risks and Edge Cases
The main risk is drift between source files and the Automake lists, which can omit headers from distribution or omit sources from a support library.

## Test Signals
Run autoreconf/automake, `make distcheck` or a clean build, and verify all listed headers and support sources are included in generated makefiles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/sys/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/sys/fs/Makefile.am -->
# sources/user-network-fs/nfs-utils/support/include/sys/fs/Makefile.am

## Purpose
Automake metadata that defines which private headers or support sources are built in this directory and marks generated `Makefile.in` for maintainer cleanup.

## Important APIs, Types, and Functions
No C APIs are defined. The meaningful variables are `SUBDIRS`, `noinst_HEADERS`, `noinst_LIBRARIES`, `noinst_LTLIBRARIES`, and per-library source lists.

## Control Flow
During autoreconf/automake, this file is expanded into a makefile fragment. Recursive subdirectories are entered first when `SUBDIRS` is set, and listed headers/sources are packaged into private build artifacts.

## State and Persistence Behavior
No runtime state exists. Build artifacts such as `Makefile.in`, static libraries, or libtool archives are generated outside this source file.

## Dependencies and Integration Points
Integrates with the nfs-utils autotools build. Correctness is visible through generated make rules and successful compilation of dependent support libraries.

## Risks and Edge Cases
The main risk is drift between source files and the Automake lists, which can omit headers from distribution or omit sources from a support library.

## Test Signals
Run autoreconf/automake, `make distcheck` or a clean build, and verify all listed headers and support sources are included in generated makefiles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/sys/fs/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/sys/fs/ext2fs.h -->
# sources/user-network-fs/nfs-utils/support/include/sys/fs/ext2fs.h

## Purpose
Provides compatibility ext2 filesystem ioctl and mount flag constants for platforms lacking this header.

## Important APIs, Types, and Functions
`EXT2_IOC_*`, filesystem state flags, mount option flags, helper macros `clear_opt`, `set_opt`, `test_opt`, and default mount-count/check intervals.

## Control Flow
Consumers use constants in ioctl or option manipulation code; no executable flow is present here.

## State and Persistence Behavior
No state. Values represent filesystem/kernel ABI constants.

## Dependencies and Integration Points
Included by filesystem/mount support code when ext2 flag definitions are needed.

## Risks and Edge Cases
Macros assume an ext2-style superblock layout for `test_opt`. Kernel header drift can make compatibility constants stale.

## Test Signals
Compile mount/filesystem utilities on systems without native ext2 headers and test ioctl flag get/set where supported.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/sys/fs/ext2fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/tcpwrapper.h -->
# sources/user-network-fs/nfs-utils/support/include/tcpwrapper.h

## Purpose
Declares TCP wrapper/local-address access checks used by RPC daemons.

## Important APIs, Types, and Functions
`from_local()` tests whether a sockaddr belongs to the local host. `check_default()` checks access policy for a service/program and caller address.

## Control Flow
Callers typically allow local callers or consult hosts.allow/hosts.deny style policy through the implementation.

## State and Persistence Behavior
Implementation may cache local interface addresses and access decisions. Policy files are external persistent state.

## Dependencies and Integration Points
Used by mountd/statd RPC access paths. Depends on socket headers and `from_local.c`/`tcpwrapper.c` implementations.

## Risks and Edge Cases
Policy evaluation depends on system tcp_wrappers availability and current interface list. Address-family handling must match callers.

## Test Signals
Test local/remote address detection, policy allow/deny files, IPv4/IPv6 callers, and interface address cache refresh.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/tcpwrapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/v4root.h -->
# sources/user-network-fs/nfs-utils/support/include/v4root.h

## Purpose
Declares dynamic NFSv4 pseudo-root support.

## Important APIs, Types, and Functions
Extern `v4root_needed` and `v4root_set()`.

## Control Flow
After etab/export parsing, callers invoke `v4root_set()` when pseudo-root generation may be needed.

## State and Persistence Behavior
`v4root_needed` is global process state set by etab reading. Generated pseudo exports enter the export list.

## Dependencies and Integration Points
Implemented by `support/export/v4root.c` and used by `xtab.c`/export setup.

## Risks and Edge Cases
Global flag ordering matters; calling before export list population has no effect.

## Test Signals
Test etab fsid0 detection and pseudo-root creation paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/v4root.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/version.h -->
# sources/user-network-fs/nfs-utils/support/include/version.h

## Purpose
Provides inline Linux kernel version-code calculation for compatibility decisions.

## Important APIs, Types, and Functions
`MAKE_VERSION(p,q,r)` and `linux_version_code()`.

## Control Flow
`linux_version_code()` calls `uname()`, parses leading release numbers with `sscanf`, and returns a packed version or `UINT_MAX` on failure/unparseable future formats.

## State and Persistence Behavior
No persistent state. It reads current kernel release at call time.

## Dependencies and Integration Points
Used by mount/support code that gates behavior on kernel version.

## Risks and Edge Cases
`UINT_MAX` intentionally disables backward-compat paths, but unparseable releases may hide needed workarounds. Vendor suffixes after numbers are tolerated.

## Test Signals
Test parse of common releases, partial `major.minor`, uname failure injection, and future nonnumeric strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/workqueue.h -->
# sources/user-network-fs/nfs-utils/support/include/workqueue.h

## Purpose
Declares a tiny synchronous worker queue abstraction used to run operations in a configured chroot.

## Important APIs, Types, and Functions
`struct xthread_workqueue`, `xthread_workqueue_alloc()`, `xthread_workqueue_shutdown()`, `xthread_work_run_sync()`, and `xthread_workqueue_chroot()`.

## Control Flow
Callers allocate a worker, optionally ask it to chroot, run function/data jobs synchronously, and shut it down.

## State and Persistence Behavior
Implementation owns worker thread state and queue synchronization. Chroot changes affect the worker thread environment.

## Dependencies and Integration Points
Used by `nfsd_path.c` to run filesystem calls under `exports.rootdir`.

## Risks and Edge Cases
Threading availability and chroot failure behavior are implementation-sensitive. Synchronous calls can deadlock if invoked reentrantly from the worker.

## Test Signals
Test allocation/shutdown, synchronous execution ordering, chroot setup, failure paths, and no-thread fallback builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/workqueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/xcommon.h -->
# sources/user-network-fs/nfs-utils/support/include/xcommon.h

## Purpose
Declares common mount/support helpers, checked allocation wrappers, string concatenation helpers, error reporting, and exit status flags.

## Important APIs, Types, and Functions
`canonicalize()`, `nfs_error()`, `xmalloc()`, `xrealloc()`, `xfree()`, `xstrdup()`, `xstrndup()`, `xstrconcat*()`, `die()`, `at_die`, `streq`, format attributes, and `EX_*` status bits.

## Control Flow
Callers use checked allocation and fatal error helpers throughout nfs-utils support and mount code. Exit status bits are ORed to report mount outcomes.

## State and Persistence Behavior
No direct state except `at_die` callback. Allocation helpers may exit rather than return NULL, shaping caller control flow.

## Dependencies and Integration Points
Included by `xmalloc.h` and many support files. Depends on config feature macros and system major/minor headers.

## Risks and Edge Cases
Duplicate `die` declarations are intentional but noisy. Functions that exit on allocation failure must not be used where recovery is required.

## Test Signals
Build with format attributes enabled/disabled, test allocation wrappers, string concat helpers, and exit-status combinations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/xcommon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/xio.h -->
# sources/user-network-fs/nfs-utils/support/include/xio.h

## Purpose
Declares simple file/token parsing and advisory lock helpers.

## Important APIs, Types, and Functions
`XFILE`, `xfopen()`, `xflock()`, `xfunlock()`, `xfclose()`, `xgettok()`, `xgetc()`, `xungetc()`, `xskip()`, and `xskipcomment()`.

## Control Flow
Callers open an `XFILE`, consume tokens/chars with line tracking and comment skipping, and use lock helpers around shared state files.

## State and Persistence Behavior
`XFILE` owns a FILE pointer and line counter. Lock helpers operate on external lock files.

## Dependencies and Integration Points
Used by export/rmtab parsers and etab locking.

## Risks and Edge Cases
Parsing helpers have fixed token buffer contracts; lock acquisition failures must be handled by callers.

## Test Signals
Test token parsing, line counts, comments, pushback, lock read/write modes, and close/unlock cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/xio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/xlog.h -->
# sources/user-network-fs/nfs-utils/support/include/xlog.h

## Purpose
Declares nfs-utils logging facilities, severity/debug facility masks, and printf-checked logging functions.

## Important APIs, Types, and Functions
`L_*` severities, `D_*` debug masks, `struct xlog_debugfac`, `export_errno`, `xlog_open()`, stderr/syslog toggles, config helpers, `xlog_enabled()`, `xlog()`, `xlog_warn()`, `xlog_err()`, `xlog_errno()`, and backend hook.

## Control Flow
Programs open logging, enable/disable facilities by numeric or string names, and emit severity/debug messages. Fatal severity exits in the implementation.

## State and Persistence Behavior
Implementation owns logging destination and enabled-facility process state. Messages persist to stderr/syslog depending on configuration.

## Dependencies and Integration Points
Used by nearly every support module. Format attributes catch mismatched printf arguments.

## Risks and Edge Cases
Mixing `D_` and `L_` values is documented as unsupported. Global logging state is process-wide.

## Test Signals
Test facility toggles, stderr/syslog routing, fatal behavior, errno formatting, and format warnings in builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/xlog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/xmalloc.h -->
# sources/user-network-fs/nfs-utils/support/include/xmalloc.h

## Purpose
Compatibility wrapper that exposes checked allocation declarations from `xcommon.h`.

## Important APIs, Types, and Functions
Includes `xcommon.h`; no independent API.

## Control Flow
Including this file gives callers `xmalloc`, `xstrdup`, and related helpers.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Used by older code that expects an `xmalloc.h` header.

## Risks and Edge Cases
Any include-cycle or guard issue is inherited from `xcommon.h`.

## Test Signals
Compile sources that include `xmalloc.h` directly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/xmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/xstat.h -->
# sources/user-network-fs/nfs-utils/support/include/xstat.h

## Purpose
Declares stat wrappers that can use newer statx/no-sync behavior when available.

## Important APIs, Types, and Functions
`xlstat()` and `xstat()`.

## Control Flow
Callers request lstat/stat semantics through wrappers; implementation may choose statx or traditional syscalls.

## State and Persistence Behavior
No state in the header. Filesystem metadata is read from the live filesystem.

## Dependencies and Integration Points
Used by misc and export path code.

## Risks and Edge Cases
Wrapper semantics must match lstat/stat closely, especially symlink behavior and errno.

## Test Signals
Test symlink and regular file metadata, missing paths, statx-enabled and fallback builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/include/xstat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/junction/Makefile.am -->
# sources/user-network-fs/nfs-utils/support/junction/Makefile.am

## Purpose
Automake metadata that defines which private headers or support sources are built in this directory and marks generated `Makefile.in` for maintainer cleanup.

## Important APIs, Types, and Functions
No C APIs are defined. The meaningful variables are `SUBDIRS`, `noinst_HEADERS`, `noinst_LIBRARIES`, `noinst_LTLIBRARIES`, and per-library source lists.

## Control Flow
During autoreconf/automake, this file is expanded into a makefile fragment. Recursive subdirectories are entered first when `SUBDIRS` is set, and listed headers/sources are packaged into private build artifacts.

## State and Persistence Behavior
No runtime state exists. Build artifacts such as `Makefile.in`, static libraries, or libtool archives are generated outside this source file.

## Dependencies and Integration Points
Integrates with the nfs-utils autotools build. Correctness is visible through generated make rules and successful compilation of dependent support libraries.

## Risks and Edge Cases
The main risk is drift between source files and the Automake lists, which can omit headers from distribution or omit sources from a support library.

## Test Signals
Run autoreconf/automake, `make distcheck` or a clean build, and verify all listed headers and support sources are included in generated makefiles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/junction/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/junction/display.c -->
# sources/user-network-fs/nfs-utils/support/junction/display.c

## Purpose
Maps FedFS status codes to readable text and prints status messages for libjunction callers.

## Important APIs, Types, and Functions
`nsdb_display_fedfsstatus()` and `nsdb_print_fedfsstatus()`.

## Control Flow
Display uses a switch over all known `FedFsStatus` values and returns a static string. Print reports success to stdout and errors to stderr.

## State and Persistence Behavior
No state or persistence beyond output streams.

## Dependencies and Integration Points
Depends on `junction.h` status enum and stdio. Used by junction command-line tools for diagnostics.

## Risks and Edge Cases
New enum values need switch updates. Output streams are fixed by status and not caller-configurable.

## Test Signals
Test every known status, unknown status fallback, stdout success, and stderr error output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/junction/display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/junction/export-cache.c -->
# sources/user-network-fs/nfs-utils/support/junction/export-cache.c

## Purpose
Flushes kernel NFSD export-related caches for junction updates using procfs cache flush files.

## Important APIs, Types, and Functions
`junction_flush_exports_cache()` and helper `junction_write_time()`.

## Control Flow
The flush function formats current time and writes it to auth.unix.ip, auth.unix.gid, nfsd.fh, and nfsd.export flush files in dependency order. It stops and returns a FedFS status on the first failed open/write.

## State and Persistence Behavior
No internal state. Effects are kernel cache invalidation attempts through `/proc/net/rpc` files.

## Dependencies and Integration Points
Depends on procfs rpc cache files, `junction.h` statuses, and `xlog`. Complements the broader export cache flush code.

## Risks and Edge Cases
Missing proc files return no-cache-update, while write failure returns unknown-cache. Unlike `cache_flush.c`, this path has no netlink mode.

## Test Signals
Test all proc files present, first file missing, later write failure, time failure injection, and ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/junction/export-cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/junction/junction-internal.h -->
# sources/user-network-fs/nfs-utils/support/junction/junction-internal.h

## Purpose
Private libjunction declarations for trusted xattr names, XML tag names, filesystem helpers, and XML helper functions.

## Important APIs, Types, and Functions
Defines `JUNCTION_XATTR_NAME_MODE`, `JUNCTION_XATTR_NAME_NFS`, XML root/fileset/savedmode names, and prototypes for path, xattr, mode, and XML parse/write helpers.

## Control Flow
Implementation files include this header to share internal routines. Public callers use `junction.h` instead.

## State and Persistence Behavior
No state. Constants name persistent trusted xattrs and XML elements.

## Dependencies and Integration Points
Depends on libxml2 tree/xpath/parser headers and `FedFsStatus` from public declarations.

## Risks and Edge Cases
Changing xattr or XML names breaks existing on-disk junctions. Private prototypes must remain aligned with implementation files.

## Test Signals
Build libjunction and run add/get/delete junction round trips against existing xattr names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/junction/junction-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/junction/junction.c -->
# sources/user-network-fs/nfs-utils/support/junction/junction.c

## Purpose
Implements low-level local filesystem operations for junction directories: open/stat, sticky-bit marker handling, trusted xattr access, and saved-mode restore.

## Important APIs, Types, and Functions
Functions include `junction_open_path()`, `junction_is_directory()`, `junction_is_sticky_bit_set()`, `junction_set_sticky_bit()`, xattr present/read/get/set/remove helpers, `junction_get_mode()`, `junction_save_mode()`, and `junction_restore_mode()`.

## Control Flow
Operations open directories with `O_DIRECTORY`, inspect via `fstatat(AT_EMPTY_PATH)`, use no-execute plus sticky bit as a junction marker, store original mode as a trusted xattr, and read/write/remove trusted xattrs by fd.

## State and Persistence Behavior
Persistent state is directory mode bits plus trusted xattrs `trusted.junction.mode` and `trusted.junction.nfs`. Heap buffers returned by read/get helpers are caller-owned.

## Dependencies and Integration Points
Depends on Linux xattr APIs, libjunction internal constants, and `xlog`. Used by NFS junction add/delete/query code and XML helpers.

## Risks and Edge Cases
Trusted xattrs require CAP_SYS_ADMIN. `junction_set_sticky_bit()` clears all permission bits before setting sticky, making restore correctness critical. Error mapping is coarse for xattr set/remove failures.

## Test Signals
Test directory/non-directory paths, permission failures, xattr absent/present, binary and string xattr reads, save/restore mode, read-only filesystem errors, and cleanup after partial add failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/junction/junction.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/junction/locations.c -->
# sources/user-network-fs/nfs-utils/support/junction/locations.c

## Purpose
Provides memory-management helpers for `struct nfs_fsloc` and NUL-terminated string arrays.

## Important APIs, Types, and Functions
`nfs_free_string_array()`, `nfs_dup_string_array()`, `nfs_free_location()`, `nfs_free_locations()`, and `nfs_new_location()`.

## Control Flow
Duplication counts strings, allocates a NULL-terminated copy, and rolls back on failure. Free functions walk arrays or linked location lists and free owned fields.

## State and Persistence Behavior
Location and array ownership is heap-based and caller-managed. No persistent state.

## Dependencies and Integration Points
Used by NFS junction XML parse/build code and public libjunction callers.

## Risks and Edge Cases
Free helpers assume non-NULL location pointers where documented. Partial allocation rollback must avoid leaks.

## Test Signals
Test NULL arrays, empty arrays, multi-string duplication, allocation failure paths, single and linked location cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/junction/locations.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/junction/nfs.c -->
# sources/user-network-fs/nfs-utils/support/junction/nfs.c

## Purpose
Implements NFS junction creation, deletion, validation, XML serialization, and XML parsing for NFSv4 fs_locations data stored in a directory trusted xattr.

## Important APIs, Types, and Functions
Public APIs are `nfs_add_junction()`, `nfs_delete_junction()`, `nfs_get_locations()`, `nfs_is_prejunction()`, and `nfs_is_junction()`. Many helpers convert each `nfs_fsloc` field to/from XML children and attributes under `/junction/fileset/location`.

## Control Flow
Adding a junction verifies the path is a directory that is not already marked, builds an XML document with saved mode and fileset locations, writes it to `trusted.junction.nfs`, then saves mode and marks sticky/no-execute. Deletion verifies a junction, restores mode, and removes NFS xattr. Querying parses the XML through XPath and constructs linked `nfs_fsloc` results.

## State and Persistence Behavior
Persistent state is XML in `trusted.junction.nfs` plus saved mode/sticky-bit state handled by `junction.c`. Parsed locations are heap-owned by callers. No separate database exists.

## Dependencies and Integration Points
Depends on libxml2, NFSv2 `NFS_PORT`, public/private junction headers, and xattr helpers. Export cache code can discover basic junctions and convert locations into export referrals.

## Risks and Edge Cases
All location XML children are effectively required. Repeated/extraneous elements are ignored. `nfs_parse_nodeset()` appends incorrectly by overwriting `result->nfl_next` instead of tracking the tail, so more than two locations may be lost. One class attribute is parsed twice for `writever`.

## Test Signals
Test add/get/delete round trips, multiple locations, zero-component root paths, missing/invalid XML fields, non-junction directories, pre-existing sticky/xattr markers, mode restore, and malformed port/u8/int attributes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/junction/nfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/junction/path.c -->
# sources/user-network-fs/nfs-utils/support/junction/path.c

## Purpose
Converts between FedFS/NSDB pathname component arrays and local POSIX path strings.

## Important APIs, Types, and Functions
`nsdb_free_string_array()`, `nsdb_path_array_to_posix()`, `nsdb_posix_to_path_array()`, plus helpers for normalization, component counting, zero-component allocation, XDR quad length, and UTF-8 validation placeholder.

## Control Flow
Array-to-POSIX validates each component, joins with slashes, normalizes duplicate/trailing slashes, and returns `/` for zero components. POSIX-to-array normalizes the input, counts components and encoded length, allocates a NULL-terminated array, and duplicates each component.

## State and Persistence Behavior
Returned path strings and arrays are heap-owned by callers. No persistent state.

## Dependencies and Integration Points
Used by libjunction public pathname conversion APIs and NFS location handling.

## Risks and Edge Cases
UTF-8 validation is a stub that always returns true. Component length checks mix NAME_MAX and 255 limits. Empty string normalization returns server fault rather than bad name.

## Test Signals
Test root path, repeated slashes, trailing slashes, empty input, too-long components, embedded slash in components, non-ASCII/invalid UTF-8 once implemented, and cleanup on allocation failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/junction/path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/junction/xml.c -->
# sources/user-network-fs/nfs-utils/support/junction/xml.c

## Purpose
Provides libxml2 helper functions for junction XML attribute/content conversion and xattr-backed XML parse/write.

## Important APIs, Types, and Functions
Includes `junction_xml_is_empty()`, node name/find helpers, bool/u8/int attribute getters/setters, int content getters/setters, `junction_xml_parse()`, and `junction_xml_write()`.

## Control Flow
Parse opens the junction directory, reads the xattr into memory, and calls `xmlReadMemory()`. Write opens the directory, dumps the XML document as formatted UTF-8 memory, and stores it as a trusted xattr. Attribute helpers convert strings with strict numeric bounds.

## State and Persistence Behavior
Persistent state is the XML document stored in a trusted xattr. Temporary XML docs/buffers are caller or function owned and freed after use.

## Dependencies and Integration Points
Depends on libxml2 and `junction.c` xattr helpers. Used by `nfs.c` for NFS junction serialization.

## Risks and Edge Cases
XML parser uses default libxml flags, so parser hardening should be reviewed for untrusted xattr content. Logging line in parse read formats buffer oddly. Numeric conversion rejects trailing characters.

## Test Signals
Test bool/int/u8 parse success/failure, missing attributes, XML xattr round trips, malformed XML, large xattrs, and write failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/junction/xml.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/misc/Makefile.am -->
# sources/user-network-fs/nfs-utils/support/misc/Makefile.am

## Purpose
Automake metadata that defines which private headers or support sources are built in this directory and marks generated `Makefile.in` for maintainer cleanup.

## Important APIs, Types, and Functions
No C APIs are defined. The meaningful variables are `SUBDIRS`, `noinst_HEADERS`, `noinst_LIBRARIES`, `noinst_LTLIBRARIES`, and per-library source lists.

## Control Flow
During autoreconf/automake, this file is expanded into a makefile fragment. Recursive subdirectories are entered first when `SUBDIRS` is set, and listed headers/sources are packaged into private build artifacts.

## State and Persistence Behavior
No runtime state exists. Build artifacts such as `Makefile.in`, static libraries, or libtool archives are generated outside this source file.

## Dependencies and Integration Points
Integrates with the nfs-utils autotools build. Correctness is visible through generated make rules and successful compilation of dependent support libraries.

## Risks and Edge Cases
The main risk is drift between source files and the Automake lists, which can omit headers from distribution or omit sources from a support library.

## Test Signals
Run autoreconf/automake, `make distcheck` or a clean build, and verify all listed headers and support sources are included in generated makefiles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/misc/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/misc/file.c -->
# sources/user-network-fs/nfs-utils/support/misc/file.c

## Purpose
Implements generic state pathname construction and base-directory validation shared by nfs-utils state-file users.

## Important APIs, Types, and Functions
`generic_make_pathname()` and `generic_setup_basedir()`.

## Control Flow
Path construction joins base and leaf with one slash after checking `PATH_MAX` and `snprintf()` bounds. Base setup validates length, `lstat()` existence, dirname usability, logs the selected directory, and copies it into the caller buffer.

## State and Persistence Behavior
Returned pathnames are heap-owned by callers. Base directory buffers are caller-owned process configuration; underlying directories are persistent filesystem state.

## Dependencies and Integration Points
Used by `xtab.c` and NSM/statd path setup helpers. Depends on `misc.h`, `xlog`, libc path/stat functions.

## Risks and Edge Cases
`generic_setup_basedir()` assumes `parentdir` is non-NULL. It checks existence but not directory type or permissions. Error messages omit trailing newlines in some cases.

## Test Signals
Test long paths, NULL/empty handling by callers, nonexistent paths, relative `.` dirname rejection, normal state directory setup, and allocation failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/misc/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/misc/from_local.c -->
# sources/user-network-fs/nfs-utils/support/misc/from_local.c

## Purpose
Determines whether a sockaddr belongs to a local network interface for tcpwrapper/access-control decisions.

## Important APIs, Types, and Functions
`from_local()` is the public API. With `getifaddrs()` it caches the interface list for one-second granularity; fallback code uses ioctl `SIOCGIFCONF` and stores IPv4 addresses in a growable static array.

## Control Flow
On each call, the getifaddrs path refreshes cached addresses when `time()` changes, then compares active interface addresses with `nfs_compare_sockaddr()`. The fallback discovers active IPv4 interfaces once and compares raw IPv4 addresses.

## State and Persistence Behavior
Static cache state includes interface list/time or fallback address arrays. No persistent files are modified.

## Dependencies and Integration Points
Depends on `sockaddr.h`, interface APIs, ioctl fallback, and `xlog`. Declared by `tcpwrapper.h` and used by RPC access checks.

## Risks and Edge Cases
Cache refresh frequency can miss rapid interface changes. Fallback supports only IPv4. `ifa_addr` NULL handling is not explicit before comparison. Time failure reuses cache when possible.

## Test Signals
Test local loopback/interface addresses, remote addresses, interface down/up changes, IPv6 with getifaddrs, fallback IPv4 builds, and getifaddrs/ioctl failure handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/misc/from_local.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/misc/mountpoint.c -->
# sources/user-network-fs/nfs-utils/support/misc/mountpoint.c

## Purpose
Implements mountpoint detection by comparing a path with its parent.

## Important APIs, Types, and Functions
`check_is_mountpoint(path, mystat)` and macro wrapper `is_mountpoint()` from `misc.h`.

## Control Flow
It builds `path/..`, stats both with `mystat` or `lstat`, and returns true when device differs or inode is equal, matching common mountpoint/root detection.

## State and Persistence Behavior
No persistent state. It allocates a temporary string and reads filesystem metadata.

## Dependencies and Integration Points
Uses `xmalloc` and `misc.h`; consumed by export/cache path checks.

## Risks and Edge Cases
Trailing slashes and unusual paths depend on stat behavior. If either stat fails, result is false. Caller can choose stat vs lstat semantics.

## Test Signals
Test root directory, ordinary directory, actual mountpoint, symlink with stat/lstat handlers, missing path, and allocation cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/misc/mountpoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/misc/nfsd_path.c -->
# sources/user-network-fs/nfs-utils/support/misc/nfsd_path.c

## Purpose
Implements `exports.rootdir` aware wrappers for filesystem operations, optionally offloading work to a chrooted worker queue and applying NFS user credentials for open calls.

## Important APIs, Types, and Functions
Functions include rootdir strip/prepend/get/init, stat/lstat/statfs/realpath wrappers, `nfsd_cred_openat()`, read/write wrappers, and `nfsd_name_to_handle_at()` with ENOSYS fallback.

## Control Flow
Initialization reads `exports.rootdir` from config and creates a worker queue chrooted there. Wrapper calls package arguments into small task structs and run them on the worker when present; otherwise they call libc/syscalls directly. Credential open swaps effective credentials around `openat()` and restores them.

## State and Persistence Behavior
Global `nfsd_wq` owns optional worker state. Configured rootdir comes from persistent config. File descriptors, errno, metadata, and read/write side effects are visible to callers.

## Dependencies and Integration Points
Depends on `conffile.h`, `workqueue.h`, `nfs_ucred.h`, `xstat.h`, `nfslib.h`, and system stat/open/read/write/name_to_handle APIs. Used by export realpath, export tests, and cache/filehandle code.

## Risks and Edge Cases
Workqueue setup failure silently falls back to host namespace operations. `nfsd_path_statfs()` casts `struct statfs *` through `struct stat *` function types. Credential swapping must be serialized to avoid thread-wide side effects. `nfsd_path_strip_root()` returns an interior pointer.

## Test Signals
Test rootdir unset, rootdir `/`, duplicate slash/dot stripping, chrooted stat/open/read/write, credential open success/failure/restore, realpath stripping/prepending, statfs behavior, and name_to_handle_at fallback.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/misc/nfsd_path.c -->

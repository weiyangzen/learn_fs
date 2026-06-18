# subset-b-009735 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdctl/nfsdctl.c -->
## sources/user-network-fs/nfs-utils/utils/nfsdctl/nfsdctl.c

Purpose: Implements `nfsdctl`, an administrative CLI and interactive shell for controlling kernel nfsd and lockd through generic netlink. It exposes `status`, `threads`, `version`, `listener`, `pool-mode`, `nlm`, and `autostart`.

Important APIs/types/functions: Local state uses `struct nfs_version`, `struct server_socket`, `nfsd_versions`, and `nfsd_sockets`. Netlink helpers include `netlink_sock_alloc`, `netlink_msg_alloc`, family setup, policy probing, shared callbacks, and parsers for status, version, listener, thread, pool, and lockd attributes. Command handlers are dispatched through `parse_command` and `func[]`.

Control flow: `main` reads `nfs.conf`, parses global options, opens netlink, queries policy support, then runs one command or a readline loop. Set commands fetch current kernel state, mutate local arrays, serialize nested netlink attributes, and wait for ACK/finish callbacks.

State and persistence: Persistent configuration comes from `/etc/nfs.conf`; runtime truth is kernel nfsd/lockd state. `autostart` applies configured versions, listeners, lockd ports, thread counts, scope, lease/grace times, dynamic min threads, and optional filehandle key hash.

Dependencies and integration: Uses libnl/genl, generated `nfsd_netlink.h` and `lockd_netlink.h`, readline, uuid, `nfslib`, `conffile`, `xlog`, module autoload via `modprobe`, and kernel support advertised by netlink policy.

Risks and test signals: Risk is high around kernel-version compatibility, listener parsing, global fixed arrays, netlink attr bounds, IPv6 availability, and privileged execution. Useful tests exercise unsupported attributes, invalid listener/version syntax, no-listener thread starts, `autostart` from representative configs, and mocked netlink replies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdctl/nfsdctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdctl/nfsdctl.h -->
## sources/user-network-fs/nfs-utils/utils/nfsdctl/nfsdctl.h

Purpose: Provides generated NFSv4 compound operation numbers used by `nfsdctl.c` to label server RPC status data.

Important APIs/types/functions: Defines `enum nfs_opnum4`, covering core NFSv4.0 operations, NFSv4.1 session/pNFS operations, NFSv4.2 operations, xattr operations, and `OP_ILLEGAL`.

Control flow: No executable flow; consumers index operation-name tables with enum constants received from kernel netlink status attributes.

State and persistence: No state or persistence. Its correctness depends on staying synchronized with `Documentation/netlink/specs/nfsd.yaml` and kernel UAPI expectations.

Dependencies and integration: Included by `nfsdctl.c`; paired with generated or system nfsd netlink headers. The SPDX line allows GPL syscall-note or BSD-3-Clause use.

Risks and test signals: Drift between enum values and kernel attributes would mislabel RPC operations. Tests should compare values against the generated kernel header/spec and check bounds for sparse/unknown op numbers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdctl/nfsdctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsidmap/Makefile.am -->
## sources/user-network-fs/nfs-utils/utils/nfsidmap/Makefile.am

Purpose: Automake rules for building and distributing the `nfsidmap` helper and its man page/config sample.

Important APIs/types/functions: Declares `sbin_PROGRAMS = nfsidmap`, `nfsidmap_SOURCES = nfsidmap.c`, include path for `support/nfsidmap`, and link dependencies on keyutils, `libnfs`, and `libnfsidmap`.

Control flow: Build-system only; automake emits compile/link/install targets.

State and persistence: Installs no runtime state itself. `EXTRA_DIST` ships `id_resolver.conf` and `nfsidmap.man`.

Dependencies and integration: Integrates kernel keyring support through `-lkeyutils` and nfs-utils support libraries.

Risks and test signals: Build failures would show as missing keyutils or support library symbols. Validate with `make nfsidmap`, distribution tarball checks, and install path checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsidmap/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsidmap/id_resolver.conf -->
## sources/user-network-fs/nfs-utils/utils/nfsidmap/id_resolver.conf

Purpose: Sample request-key rule connecting kernel id-resolver key requests to `/usr/sbin/nfsidmap`.

Important APIs/types/functions: The rule matches `create id_resolver * *` and invokes `nfsidmap -t 600 %k %d`, passing key serial and description with a 600 second timeout.

Control flow: The kernel key request mechanism calls this rule when NFS id mapping needs a userspace resolver.

State and persistence: Resolved values are instantiated in the keyring and expire according to the timeout.

Dependencies and integration: Requires Linux keyutils/request-key configuration and the installed `nfsidmap` binary path to match.

Risks and test signals: Wrong binary path or timeout prevents uid/gid/name resolution. Test with a mounted NFSv4 filesystem, `request-key`, and keyring inspection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsidmap/id_resolver.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsidmap/nfsidmap.c -->
## sources/user-network-fs/nfs-utils/utils/nfsidmap/nfsidmap.c

Purpose: Userspace NFSv4 id-mapping helper that resolves `name@domain` to uid/gid and uid/gid to names, then instantiates Linux keyring entries for kernel upcalls.

Important APIs/types/functions: Key operations include `keyring_clear`, `list_keyring`, `id_lookup`, `name_lookup`, and `key_invalidate`. It uses `nfs4_init_name_mapping`, owner/id conversion APIs from `libnfsidmap`, `keyctl_instantiate`, `keyctl_set_timeout`, and `/proc/keys` scanning fallback helpers.

Control flow: `main` parses clear/list/display/invalidate/upcall modes, requires root, initializes idmap config, then either handles admin actions or parses key/description pairs from request-key. Descriptions are split into type/value and dispatched to uid, gid, user, or group lookup.

State and persistence: Uses the `.id_resolver` keyring as cache, `/etc/idmapd.conf` for mapping rules, and `/proc/keys` for discovery/invalidation. On full keyring errors it clears the resolver ring and retries.

Dependencies and integration: Integrates with Linux keyutils, request-key, nfs-utils logging/config helpers, and libnfsidmap.

Risks and test signals: Risks include root-only operation, parsing `/proc/keys`, `atoi` for ids, keyring quota races, and silent unknown description types. Tests should cover all mapping directions, expired keys, invalidation masks, keyring-full retry, non-root rejection, and malformed descriptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsidmap/nfsidmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsref/Makefile.am -->
## sources/user-network-fs/nfs-utils/utils/nfsref/Makefile.am

Purpose: Automake rules for the `nfsref` junction/referral management utility.

Important APIs/types/functions: Builds `nfsref` from `add.c`, `lookup.c`, `nfsref.c`, and `remove.c`, installs `nfsref.h` as a local header, and links against `support/nfs`, `support/junction`, libxml2, and libcap.

Control flow: Build-system only; automake emits targets for compile, link, install, and maintainer cleanup.

State and persistence: No runtime state. It declares the `nfsref.man` man page and generated `Makefile.in` cleanup.

Dependencies and integration: The junction library provides xattr/XML referral primitives; libcap likely supports privileged metadata operations.

Risks and test signals: Link failures or missing junction symbols are the main risk. Validate with build, install, and packaging checks that `nfsref.man` ships.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsref/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsref/add.c -->
## sources/user-network-fs/nfs-utils/utils/nfsref/add.c

Purpose: Implements `nfsref add`, creating a local NFS basic junction and storing one or more fileset locations.

Important APIs/types/functions: `nfsref_add_help`, `nfsref_add_build_fsloc`, `nfsref_add_build_fsloc_list`, `nfsref_add_nfs_basic`, and `nfsref_add`. It populates `struct nfs_fsloc` defaults, converts POSIX export paths with `nsdb_posix_to_path_array`, and writes metadata with `nfs_add_junction`.

Control flow: Public `nfsref_add` ensures the junction path exists as a directory, selects the requested type, builds a linked list of server/export pairs, writes junction metadata, frees locations, and reports success/failure.

State and persistence: Persists referral metadata on the junction filesystem object through the junction support library. Default FSL fields encode conservative NFSv4 location behavior.

Dependencies and integration: Uses uuid headers, `junction.h`, `xlog`, and shared `nfsref.h`; called from `nfsref.c` after root/type/argument validation.

Risks and test signals: The list builder appends only through `result->nfl_next`, so more than two locations deserve tests. Also test odd argument counts, existing junction metadata, allocation failures, path conversion errors, and export-cache flush by the caller.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsref/add.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsref/lookup.c -->
## sources/user-network-fs/nfs-utils/utils/nfsref/lookup.c

Purpose: Implements `nfsref lookup`, reading and displaying NFS basic junction metadata from a local path.

Important APIs/types/functions: `nfsref_lookup_help`, `nfsref_lookup_display_nfs_location`, `nfsref_lookup_nfs_basic`, `nfsref_lookup_unspecified`, and `nfsref_lookup`. It converts path arrays back to POSIX paths and prints all FSL flags/classes/ranking fields.

Control flow: Public lookup dispatches by junction type. Unspecified mode probes with `nfs_is_junction`; basic mode validates, calls `nfs_get_locations`, prints every linked location, and frees the list.

State and persistence: Reads persisted junction metadata but does not mutate it.

Dependencies and integration: Relies on `junction.h`, `rpcsvc/nfs_prot.h`, and `xlog`; invoked by the `nfsref` front end.

Risks and test signals: Output is human-readable and not structured, so downstream parsing is brittle. Tests should cover non-junction paths, corrupt rootpath arrays, multiple locations, and unsupported `nfs-fedfs` type handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsref/lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsref/nfsref.c -->
## sources/user-network-fs/nfs-utils/utils/nfsref/nfsref.c

Purpose: Main command dispatcher for `nfsref`, managing root checks, global options, junction type selection, and subcommand routing.

Important APIs/types/functions: Defines option tables for `--debug`, `--help`, and `--type`; `nfsref_usage`; and `main`. Supported subcommands are `add`, `remove`, and `lookup`.

Control flow: `main` initializes locale, umask, logging, parses options, rejects non-root execution except help, chooses the subcommand, and calls the corresponding implementation. Successful add/remove operations flush the exports cache.

State and persistence: Does not store state directly; operations invoked by it mutate junction metadata and export cache state.

Dependencies and integration: Uses `junction_flush_exports_cache`, `xlog`, and declarations in `nfsref.h`.

Risks and test signals: Option parsing permits help before root enforcement, but subcommand argument boundaries need coverage. Tests should validate `-t nfs-basic`, rejected type strings, missing parameters, root permission checks, and cache flush calls after mutations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsref/nfsref.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsref/nfsref.h -->
## sources/user-network-fs/nfs-utils/utils/nfsref/nfsref.h

Purpose: Shared declarations for the `nfsref` utility implementation files.

Important APIs/types/functions: Defines `enum nfsref_type` with unspecified, NFS basic, and NFS FedFS values, plus prototypes for add/remove/lookup handlers and help functions.

Control flow: No executable flow; it stabilizes the front-end-to-subcommand contract.

State and persistence: No state. Type values determine which persistence backend a subcommand attempts to use.

Dependencies and integration: Included by all `nfsref` C files and built as a no-install local header.

Risks and test signals: FedFS type is declared but not implemented in the researched command paths, so tests should verify graceful rejection rather than accidental partial behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsref/nfsref.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsref/remove.c -->
## sources/user-network-fs/nfs-utils/utils/nfsref/remove.c

Purpose: Implements `nfsref remove`, deleting junction metadata from a filesystem object.

Important APIs/types/functions: `nfsref_remove_help`, `nfsref_remove_nfs_basic`, `nfsref_remove_unspecified`, and `nfsref_remove`. Core metadata deletion is delegated to `nfs_delete_junction`.

Control flow: Public dispatch selects unspecified or NFS basic deletion. Basic mode treats `FEDFS_ERR_NOTJUNCT` as a failure. Unspecified mode attempts deletion and reports success even if the path was not an NFS basic junction, except for other errors.

State and persistence: Mutates local junction metadata and relies on caller `nfsref.c` to flush the exports cache on success.

Dependencies and integration: Uses `junction.h`, `xlog`, and shared type declarations.

Risks and test signals: The unspecified success path for `FEDFS_ERR_NOTJUNCT` is surprising and should be characterized. Tests should cover existing junctions, absent metadata, permission errors, unsupported type, and export-cache flush integration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsref/remove.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsstat/Makefile.am -->
## sources/user-network-fs/nfs-utils/utils/nfsstat/Makefile.am

Purpose: Automake rules for building `nfsstat`, the NFS statistics reporting utility.

Important APIs/types/functions: Declares `nfsstat.c` as the only source, applies libnl CFLAGS, and links export, nfs, misc, libnl3, and libnl-genl libraries.

Control flow: Build-only. Automake emits compile, link, install, distribution, and maintainer cleanup rules.

State and persistence: No runtime state; ships `nfsstat.man`.

Dependencies and integration: The libnl dependencies match `nfsstat.c` server-stat netlink support, while support libraries cover shared nfs-utils helpers.

Risks and test signals: Missing libnl causes build failure; packaging tests should verify the man page and program are installed together.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsstat/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsstat/nfsstat.c -->
## sources/user-network-fs/nfs-utils/utils/nfsstat/nfsstat.c

Purpose: Implements `nfsstat`, reporting NFS client/server RPC, network, cache, filehandle, I/O, and per-procedure counters.

Important APIs/types/functions: Uses global counter arrays and `statinfo` descriptors. Main helpers include `parse_raw_statfile`, `parse_pretty_statfile`, `get_stats_netlink`, `stats_nl_handler`, `diff_stats`, `print_*` functions, and `mounts`. Option flags select client/server, versions, categories, list format, `--since`, and interval mode.

Control flow: `main` parses options, decides default client/server/category/version sets, reads current or baseline stats, optionally waits for SIGINT or loops at a sleep interval, diffs counters, and prints normal or list output. Server stats prefer generic netlink `NFSD_CMD_SERVER_STATS_GET`, falling back to `/proc/net/rpc/nfsd`; client stats use `/proc/net/rpc/nfs`.

State and persistence: Runtime state is process-local counters. Persistent inputs are `/proc/net/rpc/nfsd`, `/proc/net/rpc/nfs`, `/proc/mounts`, and optional saved pretty/raw stats file for `--since`.

Dependencies and integration: Uses libnl/genl and nfsd netlink UAPI, plus procfs formats emitted by kernel NFS client/server. Output compatibility is maintained for older kernel stat layouts.

Risks and test signals: Counter widths truncate u64 netlink counts to unsigned int in several places, proc pretty parsing is format-sensitive, interval update math is easy to regress, and server-only category warnings are non-fatal. Tests should feed fixture raw/pretty files, mocked netlink attributes, wraparound counters, mount listings, and SIGINT interval flow.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsstat/nfsstat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/showmount/Makefile.am -->
## sources/user-network-fs/nfs-utils/utils/showmount/Makefile.am

Purpose: Automake rules for building `showmount`.

Important APIs/types/functions: Builds `showmount.c`, links export/nfs/misc support libraries and libtirpc, and adds the export support include path.

Control flow: Build-only.

State and persistence: No runtime state; distributes `showmount.man`.

Dependencies and integration: Depends on RPC/TI-RPC and nfs-utils support libraries used by `showmount.c`.

Risks and test signals: Validate with builds against libtirpc and install/distribution checks for binary plus man page.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/showmount/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/showmount/showmount.c -->
## sources/user-network-fs/nfs-utils/utils/showmount/showmount.c

Purpose: Implements `showmount`, querying a remote mountd service for exports or active mount entries.

Important APIs/types/functions: `nfs_get_mount_client` creates a TCP or UDP RPC client using mount program aliases. `dump_cmp` sorts output. `main` handles `-a`, `-d`, `-e`, `--no-headers`, version fallback, RPC calls, and formatting.

Control flow: Options choose exactly one mode: host list default, all host:directory pairs, directories, or exports. It chooses localhost by default, creates an authenticated mount RPC client, tries mount protocol versions in order on version mismatch, calls `MOUNTPROC_EXPORT` or `MOUNTPROC_DUMP`, sorts dump entries, suppresses duplicates, and prints.

State and persistence: Stateless client. Reads no local persistent data beyond hostname and RPC database; remote mountd provides all data.

Dependencies and integration: Uses RPC mount protocol XDR types from `mount.h`, `nfsrpc.h` authentication helpers, and libtirpc/SunRPC.

Risks and test signals: Remote RPC failures exit directly, memory for `-a` strings is not freed before exit, and output depends on mountd v1/v2/v3 compatibility. Tests should mock mountd responses for exports, duplicates, version mismatch, no headers, invalid mode combinations, and unreachable hosts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/showmount/showmount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/Makefile.am -->
## sources/user-network-fs/nfs-utils/utils/statd/Makefile.am

Purpose: Automake rules for `rpc.statd`, `sm-notify`, generated RPC simulation files, scripts, and man pages.

Important APIs/types/functions: Builds `statd` from callback, monitor, notification-list, RPC call, daemon, service-loop, and helper sources; builds `sm-notify` from `sm-notify.c`; installs `start-statd`; generates RPC files from `sim_sm_inter.x` when configured; renames installed `statd` with `rpc.`/kernel prefixes.

Control flow: Build and install hooks transform daemon names and create man-page symlinks.

State and persistence: No runtime state in this file, but it wires programs that use NSM state directories and pid files.

Dependencies and integration: Links `support/nsm`, `support/nfs`, `support/misc`, libwrap, libnsl, libcap, and libtirpc.

Risks and test signals: Install hooks are custom and can diverge from automake expectations. Validate generated RPC file creation, prefixed binary install/uninstall, man links, and clean targets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/callback.c -->
## sources/user-network-fs/nfs-utils/utils/statd/callback.c

Purpose: Services incoming NSM `SM_NOTIFY` calls and schedules local lockd callbacks when monitored peers reboot.

Important APIs/types/functions: Exports `sm_notify_1_svc`. It uses `statd_present_address`, `statd_matchhostname`, `ha_callout`, `nlist_clone`, and global lists `rtnl` and `notify`.

Control flow: On `SM_NOTIFY`, it records sender address, invokes HA callout, exits early if no hosts are monitored, scans runtime monitored entries for changed state and hostname/address match, updates entry state, clones it, and inserts the clone into the pending notify/callback queue.

State and persistence: Mutates in-memory `rtnl` entry state and queues callback work in `notify`. Persistent monitor files are not removed here; lockd continues monitoring until unmonitor.

Dependencies and integration: Runs under RPC dispatch from `statd.c`; callback queue is processed by `svc_run.c` and `rmtcall.c`.

Risks and test signals: DNS matching can block or misidentify peers; remote `mon_name` trust is limited. Tests should cover IP and hostname matches, unchanged states, empty monitor list, HA callout invocation, and cloned callback queue entries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/callback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/hostname.c -->
## sources/user-network-fs/nfs-utils/utils/statd/hostname.c

Purpose: Provides hostname/address canonicalization and equivalence checks for statd monitor matching.

Important APIs/types/functions: `statd_present_address`, `statd_canonical_name`, `statd_matchhostname`, and internal `get_addrinfo`, `get_nameinfo`, `statd_canonical_list`.

Control flow: Presentation addresses are converted with getnameinfo when available; canonical name resolution distinguishes numeric hosts from names; matching first checks case-insensitive string equality, then canonical names, then address-list intersection.

State and persistence: No state; DNS and resolver configuration are external state.

Dependencies and integration: Uses nfs-utils sockaddr helpers, `getaddrinfo`/`getnameinfo`, IPv6 build flags, and `xlog`. Called by monitor registration, unmonitor, notify handling, and list search.

Risks and test signals: DNS latency blocks the single-threaded daemon, reverse/forward mismatch affects correctness, wildcard/netgroup comments are not explicitly enforced here, and IPv6 fallback behavior differs by build. Tests should cover numeric IPv4/IPv6, no reverse DNS, canonical aliases, same-address different names, resolver failures, and scope IDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/hostname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/misc.c -->
## sources/user-network-fs/nfs-utils/utils/statd/misc.c

Purpose: Small allocation helpers for statd.

Important APIs/types/functions: `xmalloc` and `xstrdup` wrap allocation and log fatal errors with `xlog_err` on failure.

Control flow: `xmalloc(0)` returns NULL; otherwise allocation failure terminates via logging behavior. `xstrdup` similarly assumes non-NULL input.

State and persistence: No state.

Dependencies and integration: Used by notification-list and simulator code for fail-fast allocation semantics.

Risks and test signals: Callers do not consistently handle NULL because these helpers are intended to abort on memory exhaustion. Unit tests can cover zero-size allocation and successful duplication; fault injection should confirm expected fatal logging path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/monitor.c -->
## sources/user-network-fs/nfs-utils/utils/statd/monitor.c

Purpose: Implements NSM monitor registration and deregistration RPC procedures used by local lockd.

Important APIs/types/functions: Exports `sm_mon_1_svc`, `sm_unmon_1_svc`, `sm_unmon_all_1_svc`, `load_state`, and global `rtnl`. Uses `caller_is_localhost`, `nlist_*`, `nsm_insert_monitored_host`, `nsm_delete_monitored_host`, `nsm_load_monitor_list`, `statd_canonical_name`, and HA callouts.

Control flow: `SM_MON` rejects non-loopback callers and non-lockd callbacks, sanitizes `my_name`, rejects dangerous hostnames, canonicalizes monitored host, handles duplicates or cookie changes, persists a monitor record, and inserts/updates runtime list. `SM_UNMON` and `SM_UNMON_ALL` validate local caller, find matching runtime records, delete persistent records, call HA hooks, and remove list nodes.

State and persistence: Maintains runtime monitor list and stable NSM monitor records. Uses `MY_STATE` for responses.

Dependencies and integration: Tied to kernel lockd callback program/procedure numbers, nsm support library, custom hostname matching, and RPC dispatch.

Risks and test signals: Security depends on loopback checks and hostname sanitation. DNS failure prevents monitoring. Duplicate-cookie update behavior and `free(clnt)` on failure need coverage. Tests should simulate local/non-local RPC callers, bad program/proc, malicious hostnames, duplicate monitors, persistent insert/delete failures, and reload from state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/monitor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/notlist.c -->
## sources/user-network-fs/nfs-utils/utils/statd/notlist.c

Purpose: Implements doubly linked-list management for monitored hosts and pending notification/callback work.

Important APIs/types/functions: `nlist_new`, `nlist_insert`, `nlist_insert_timer`, `nlist_remove`, `nlist_clone`, `nlist_free`, `nlist_kill`, and `nlist_gethost`.

Control flow: Entries are allocated with default retry count `MAX_TRIES`; normal insert prepends; timer insert keeps ascending `when`; remove unlinks without freeing; clone copies callback identity and cookie; kill drains the list.

State and persistence: Manages in-memory lists only. Persistent NSM records are handled elsewhere.

Dependencies and integration: Uses `notify_list` macros from `notlist.h`, `xmalloc`, `xstrdup`, and `statd_matchhostname`. Shared by monitor, callback, rmtcall, and service-loop code.

Risks and test signals: Pointer ownership is delicate: `nlist_free` frees inner fields but not the entry itself, while `nlist_kill` frees both. Tests should cover head/middle/tail removal, append timer insertion, clone cookie fields, hostname search, and memory ownership under sanitizers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/notlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/notlist.h -->
## sources/user-network-fs/nfs-utils/utils/statd/notlist.h

Purpose: Declares statd notification-list data structures, globals, functions, and accessor macros.

Important APIs/types/functions: `struct notify_list` embeds `mon`, callback port, retry count, state, DNS name, linked-list pointers, XID, and timeout. Declares global `rtnl` and `notify`, list functions, and `NL_*` macros for nested NSM fields.

Control flow: No executable flow; macros define how all list users read/write monitor identity and scheduling fields.

State and persistence: Defines in-memory state only. `rtnl` mirrors monitored records; `notify` tracks pending RPC work.

Dependencies and integration: Includes `netinet/in.h` and depends on NSM types/macros from `statd.h`.

Risks and test signals: Macro-heavy access can obscure ownership and type errors. Tests should compile all users and validate field preservation through clone/insert/remove workflows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/notlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/rmtcall.c -->
## sources/user-network-fs/nfs-utils/utils/statd/rmtcall.c

Purpose: Sends asynchronous local callbacks to lockd after peer reboot notifications and processes replies on a reserved UDP socket.

Important APIs/types/functions: `statd_get_socket`, `recv_rply`, `process_entry`, `process_reply`, and `process_notify_list`. It uses `nsm_xmit_getport`, `nsm_recv_getport`, `nsm_xmit_nlmcall`, and `nsm_parse_reply`.

Control flow: A privileged loopback UDP socket is created before dropping privileges. Pending entries first discover the local lockd port if needed, then send the callback RPC. Replies are matched by XID, update callback port, reschedule entries, or free successful/failed entries. Timeouts reinsert entries by `NL_WHEN` until retries are exhausted.

State and persistence: Uses static `sockfd` and the global `notify` list. No persistent state.

Dependencies and integration: Integrated with `svc_run.c` select loop and `callback.c`/`monitor.c` queue producers; depends on reserved ports accepted by lockd.

Risks and test signals: Only loopback replies are trusted, but XID collisions and retry exhaustion need coverage. Tests should exercise reserved-port binding, service port discovery, successful callback, no registered service, timeout rescheduling, and failure after `MAX_TRIES`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/rmtcall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/simu.c -->
## sources/user-network-fs/nfs-utils/utils/statd/simu.c

Purpose: Implements the `SM_SIMU_CRASH` RPC service for test/simulation builds.

Important APIs/types/functions: `sm_simu_crash_1_svc` validates caller address/port, calls `my_svc_exit`, and clears the runtime monitor list.

Control flow: The procedure accepts only IPv4 loopback callers from privileged ports. Accepted calls stop the custom service loop and kill the runtime notify list.

State and persistence: Mutates only in-memory runtime list and service-loop stop flag. It does not retire NSM state files.

Dependencies and integration: Built for simulation support, depends on `nfs_getrpccaller`, `nfs_is_v4_loopback`, `nfs_get_port`, and `notlist`.

Risks and test signals: Security relies on loopback plus privileged-port checks. Tests should cover non-local callers, unprivileged local port rejection, list cleanup, and service-loop exit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/simu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/simulate.c -->
## sources/user-network-fs/nfs-utils/utils/statd/simulate.c

Purpose: Optional simulator CLI for exercising statd NSM procedures and receiving simulated callbacks.

Important APIs/types/functions: `simulator` dispatches to `simulate_mon`, `simulate_unmon`, `simulate_unmon_all`, `simulate_stat`, `simulate_crash`, and `daemon_simulator`; callback service `sim_sm_mon_1_svc` logs received status.

Control flow: Depending on argument count and command, it creates UDP RPC clients to target statd, sends NSM calls, and for `mon` registers a temporary simulator RPC service to wait for callback.

State and persistence: Uses a computed `sim_port` and rpcbind registration. No persistent state.

Dependencies and integration: Requires `SIMULATIONS`, generated `sim_sm_inter` RPC stubs, rpcbind, and statd service stubs.

Risks and test signals: It contains developer-era rough edges and abrupt fatal logging. Test only in simulation builds; verify pmap registration cleanup, monitor callback receipt, and all command argument forms.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/simulate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/sm-notify.c -->
## sources/user-network-fs/nfs-utils/utils/statd/sm-notify.c

Purpose: Sends `SM_NOTIFY` RPCs to peers recorded in NSM state after local reboot/startup, with retry scheduling and optional lockd grace-period lift.

Important APIs/types/functions: `struct nsm_host`, `smn_lookup`, `smn_verify_my_name`, `smn_alloc_host`, `smn_create_socket`, `notify`, `notify_host`, `recv_reply`, `recv_rpcbind_reply`, `recv_notify_reply`, `insert_host`, `find_host`, and `record_pid`.

Control flow: `main` reads config/options, prevents duplicate default runs via `/run/sm-notify.pid`, verifies source name/address, retires monitored hosts into notify list, obtains NSM state, optionally daemonizes, creates a nonblocking reserved UDP socket, drops privileges, and enters `notify`. The loop sends due hosts in batches, first rpcbind lookup if needed, then SM_NOTIFY, backs off exponentially, rotates addresses after repeated retries, and removes hosts after successful qualified and unqualified notifications.

State and persistence: Reads and mutates NSM monitor/notify records through `support/nsm`; updates kernel NSM state; writes pid file; may write `Y` to `/proc/fs/lockd/nlm_end_grace`.

Dependencies and integration: Uses resolver APIs, nfs-utils config/logging, low-level RPC encode/decode from `nfsrpc`, and lockd grace-period integration.

Risks and test signals: DNS failures, stale rpcbind ports, IPv6 dual-stack behavior, pid-file semantics, and retry timeout caps are important. Tests should use fake NSM records, mocked rpcbind/notify replies, multiple addrinfo records, `--no-update-state`, source bind options, duplicate run detection, and grace-period file absence/presence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/sm-notify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/start-statd -->
## sources/user-network-fs/nfs-utils/utils/statd/start-statd

Purpose: Shell helper used by NFS mount tooling to start `rpc.statd` if locking is requested and the daemon appears absent.

Important APIs/types/functions: Uses `/run/rpc.statd.lock` with `flock`, checks `/run/rpc.statd.pid` and `kill -0`, tries `systemctl start rpc-statd.service`, adds a runtime dependency to `remote-fs.target`, and falls back to `exec rpc.statd --no-notify`.

Control flow: Serialize invocations, exit if an existing pid is alive, prefer systemd, otherwise launch daemon directly from `/`.

State and persistence: Reads pid and lock files under `/run`; systemd runtime wants are transient.

Dependencies and integration: Invoked by mounting path; depends on systemd when available, otherwise installed `rpc.statd` in PATH.

Risks and test signals: Pid-file parsing assumes numeric content and root privileges. Tests should cover concurrent invocation, stale pid file, systemd success/failure, and fallback exec arguments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/start-statd -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/stat.c -->
## sources/user-network-fs/nfs-utils/utils/statd/stat.c

Purpose: Implements the NSM `SM_STAT` procedure.

Important APIs/types/functions: `sm_stat_1_svc` resolves the requested monitor name via `statd_canonical_name` and returns `STAT_SUCC` or `STAT_FAIL` plus local `MY_STATE`.

Control flow: On request, log caller name, attempt canonical resolution, set result status accordingly, free the resolved name, set state, and return a static response.

State and persistence: Reads local NSM state from global `MY_STATE`; no persistent mutation.

Dependencies and integration: Used by RPC dispatch; relies on DNS/canonicalization helper.

Risks and test signals: Resolver availability controls success and can block. Tests should cover resolvable host, unresolved host, numeric address, and returned state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/statd.c -->
## sources/user-network-fs/nfs-utils/utils/statd/statd.c

Purpose: Main daemon for Linux NSM `rpc.statd`, handling configuration, daemonization, RPC listener setup, notification startup, state loading, privilege dropping, and service loop execution.

Important APIs/types/functions: Defines globals `run_mode`, `ha_callout_prog`, `SM_stat_chge`, ports, and option table. Key functions include `statd_unregister`, signal handlers, `create_pidfile`, `truncate_pidfile`, `run_sm_notify`, `set_nlm_port`, `read_statd_conf`, and `main`.

Control flow: Startup reads config/env, parses options, rejects duplicate statd, validates ports, optionally delegates notify-only mode to `sm-notify`, limits file descriptors, sets lockd ports via procfs, daemonizes, registers signals, writes pid file, runs `sm-notify` unless disabled, creates reserved callback socket, loads persistent monitor state, obtains NSM state, unregisters stale RPC registrations, drops privileges, creates RPC listeners, announces readiness, then repeatedly runs `my_svc_run`.

State and persistence: Uses `/run/rpc.statd.pid`, NSM state directory, kernel NSM state, `/proc/sys/fs/nfs/nlm_*port`, and rpcbind registrations. Runtime globals control modes and local name/state.

Dependencies and integration: Integrates with config file, `support/nsm`, nfs-utils daemon helpers, libtirpc RPC service creation, tcp_wrappers when enabled, lockd procfs controls, and `sm-notify`.

Risks and test signals: Startup ordering is security-sensitive: reserved socket before privilege drop, unregister before listener creation, and pid handling. Tests should cover config/CLI precedence, duplicate daemon detection, no-notify env, port validation, privilege drop failure, listener creation failure, signal cleanup, and `sm-notify` fork path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/statd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/statd.h -->
## sources/user-network-fs/nfs-utils/utils/statd/statd.h

Purpose: Shared statd declarations, constants, global state accessors, and mode flags.

Important APIs/types/functions: Includes RPC `sm_inter.h`, defines `STAT_FAIL`/`STAT_SUCC`, declares hostname helpers, service loop, notification processors, socket/state helpers, allocation helpers, and exports `SM_stat_chge` through `MY_NAME` and `MY_STATE`. Defines timeout constants and mode flags.

Control flow: No executable flow; establishes contracts across statd compilation units.

State and persistence: Exposes global NSM local name/state and run mode. Persistent state is handled by declared helpers.

Dependencies and integration: Included by all statd sources; depends on generated NSM RPC headers and nfs-utils logging/system abstractions.

Risks and test signals: Global macros make hidden coupling easy. Compile-time tests and integration tests should ensure every source sees consistent mode/timeout/state definitions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/statd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/svc_run.c -->
## sources/user-network-fs/nfs-utils/utils/statd/svc_run.c

Purpose: Custom RPC service loop for statd that multiplexes RPC listener fds with the local notification reply socket and timeout queue.

Important APIs/types/functions: Global `notify`, static `svc_stop`, `my_svc_exit`, and `my_svc_run`.

Control flow: The loop processes due notification entries, builds the RPC fd set, adds the notify socket, selects with a timeout based on the next notification, handles transient errors, processes notify replies first, then dispatches RPC requests via `svc_getreqset`.

State and persistence: Manages in-memory stop flag and global pending notify list only.

Dependencies and integration: Called from `statd.c`; uses `process_notify_list` and `process_reply` from `rmtcall.c`, plus SunRPC `svc_fdset`.

Risks and test signals: Timeout calculations depend on a valid `now`, and fd-set size is constrained by `FD_SETSIZE`. Tests should cover empty queue blocking, due queue processing, reply socket events, RPC-only events, EINTR handling, and `my_svc_exit`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/svc_run.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/system.h -->
## sources/user-network-fs/nfs-utils/utils/statd/system.h

Purpose: Compatibility definitions for fd-set types used by statd service-loop code.

Important APIs/types/functions: Defines `FD_SET_TYPE` and `SVC_FDSET` as either `fd_set`/`svc_fdset` or legacy `int`/`svc_fds`.

Control flow: Preprocessor-only compatibility layer.

State and persistence: No state.

Dependencies and integration: Included by `statd.h`; shields users from SunRPC implementation differences.

Risks and test signals: Build portability depends on correct branch selection. Compile tests should cover modern and legacy RPC headers if supported.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/statd/system.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/.claude/settings.local.json -->
## sources/user-network-fs/pyfuse3/.claude/settings.local.json

Purpose: Local Claude tool permission settings for the pyfuse3 repository.

Important APIs/types/functions: JSON grants selected Bash and Serena MCP file operations.

Control flow: Configuration-only; no executable code.

State and persistence: Persists local tool permissions under `.claude`.

Dependencies and integration: Consumed by Claude tooling, not by pyfuse3 runtime/build.

Risks and test signals: Risk is accidental broad tool permission drift. Validate as JSON and keep out of packaging/runtime assumptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/.claude/settings.local.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/.github/workflows/codespell.yml -->
## sources/user-network-fs/pyfuse3/.github/workflows/codespell.yml

Purpose: GitHub Actions workflow for spelling checks.

Important APIs/types/functions: Runs on pushes and pull requests to `main`, grants read-only contents permission, checks out code, then runs `codespell-project/actions-codespell@v2`. The file notes configuration is in `pyproject.toml`.

Control flow: Single job on Ubuntu latest with checkout then codespell action.

State and persistence: No persistent state beyond CI results.

Dependencies and integration: Integrates repository spelling policy with GitHub Actions.

Risks and test signals: If `pyproject.toml` config drifts or action version changes behavior, false positives can block PRs. Test by running codespell locally or in CI.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/.github/workflows/codespell.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/.github/workflows/test.yml -->
## sources/user-network-fs/pyfuse3/.github/workflows/test.yml

Purpose: GitHub Actions CI workflow for pyfuse3 build, lint, type checking, tests, and docs.

Important APIs/types/functions: Matrix covers Python 3.10 through 3.14 on Ubuntu 24.04, installs uv, Linux FUSE/build dependencies, runs `uv sync --locked`, ruff check/format diff, mypy, pyright, pytest, and sphinx with warnings as errors.

Control flow: Triggered on push; fail-fast matrix stops after first failed lane.

State and persistence: Uses uv cache from setup action and CI artifacts/logs only.

Dependencies and integration: Requires libattr, libfuse3, fuse3, pkg-config, gcc, uv, and the repository lockfile.

Risks and test signals: FUSE tests may require CI kernel/user permissions, Python 3.14 compatibility is an active signal, and docs warnings fail builds. Local reproduction should use the same uv commands and apt packages.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/.github/workflows/test.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/.readthedocs.yaml -->
## sources/user-network-fs/pyfuse3/.readthedocs.yaml

Purpose: Read the Docs build configuration for pyfuse3 documentation.

Important APIs/types/functions: Uses config version 2, Ubuntu 22.04, Python 3.11, fetches additional git history after checkout, installs build-essential/pkg-config/libfuse3-dev, installs the project with pip, and points Sphinx to `rst/conf.py`.

Control flow: RTD creates environment, runs post-checkout git fetch, installs apt packages, installs package, then builds Sphinx docs.

State and persistence: No runtime state; RTD build cache/logs only.

Dependencies and integration: Aligns docs build with native extension/FUSE library requirements and setuptools-scm style versioning needs.

Risks and test signals: Missing git history or libfuse3 breaks docs import/versioning. Test with Read the Docs build or local equivalent using Python 3.11.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/.readthedocs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/MANIFEST.in -->
## sources/user-network-fs/pyfuse3/MANIFEST.in

Purpose: Source distribution manifest for pyfuse3.

Important APIs/types/functions: Includes changes/license, grafts docs, headers, examples, rst, util, and tests, prunes test cache and `.github`, excludes manifest/git/RTD metadata, recursively includes source `.pyx`, `.pyi`, `.py`, `.pxi`, `.pxd`, `.c`, `.h`, and excludes `.pyc`.

Control flow: Packaging configuration only; consumed during sdist generation.

State and persistence: Affects package artifact contents.

Dependencies and integration: Integrates Python packaging with Cython/C headers and docs/test distribution.

Risks and test signals: Missing generated C/header files can break offline builds; over-including tests/docs increases sdist size. Validate with `python -m build --sdist` and inspect archive contents.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/MANIFEST.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/examples/hello.py -->
## sources/user-network-fs/pyfuse3/examples/hello.py

Purpose: Minimal Trio-based pyfuse3 filesystem example exposing a single read-only file `message`.

Important APIs/types/functions: `TestFs` implements `getattr`, `lookup`, `opendir`, `readdir`, `open`, and `read`; `init_logging`, `parse_args`, and `main` handle CLI and pyfuse3 lifecycle.

Control flow: `main` parses mountpoint/debug options, initializes `TestFs`, sets FUSE options, calls `pyfuse3.init`, runs `trio.run(pyfuse3.main)`, and closes on normal or exceptional exit. Filesystem methods map root and one file inode to static attributes/data.

State and persistence: In-memory only: fixed inode/name/data and deterministic timestamps. No underlying filesystem writes.

Dependencies and integration: Demonstrates `pyfuse3.Operations` with Trio, FUSE entry attributes, file handles, and `readdir_reply`.

Risks and test signals: It rejects writes and unknown names; exceptions close without unmount. Tests can mount in a temp mountpoint, read `/message`, list root, try write/open errors, and run with debug options.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/examples/hello.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/examples/hello_asyncio.py -->
## sources/user-network-fs/pyfuse3/examples/hello_asyncio.py

Purpose: Asyncio variant of the minimal pyfuse3 single-file example, also showing termination via xattr.

Important APIs/types/functions: Enables `pyfuse3.asyncio`, implements the same `TestFs` methods as `hello.py`, plus `setxattr` accepting `command=terminate` on the root inode to call `pyfuse3.terminate`.

Control flow: `main` initializes FUSE and runs `asyncio.run(pyfuse3.main())`. Filesystem operations serve static root/file metadata and content; unsupported xattrs return `ENOTSUP`, invalid command values return `EINVAL`.

State and persistence: In-memory only with static file content and timestamps.

Dependencies and integration: Demonstrates pyfuse3 asyncio integration, FUSE xattr handling, and graceful event-loop termination.

Risks and test signals: The terminate control path is intentionally exposed through xattr and should be used only for example/test mounts. Tests should cover reading `message`, read-only open enforcement, xattr terminate, and cleanup after exceptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/examples/hello_asyncio.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/examples/passthroughfs.py -->
## sources/user-network-fs/pyfuse3/examples/passthroughfs.py

Purpose: Trio-based pyfuse3 passthrough filesystem that mirrors and mutates an underlying directory tree.

Important APIs/types/functions: `Operations` maps FUSE inode ids to paths and file descriptors. It implements lookup, getattr, forget, readlink, directory ops, unlink/rmdir, symlink, rename, hardlink, setattr, mknod, mkdir, statfs, open/create, read/write, and release. Helpers include `_inode_to_path`, `_add_path`, `_getattr`, and `_forget_path`.

Control flow: `main` parses source/mountpoint/debug/writeback options, creates operations, initializes FUSE, runs `trio.run(pyfuse3.main)`, and closes. FUSE calls translate inode/fh operations to Python `os.*` calls, converting `OSError.errno` to `FUSEError`. Lookup/readdir add path mappings; forget and deletion remove them; open/create maintain fd/inode/open-count maps.

State and persistence: Persistent state is the underlying source directory. In-memory state tracks inode-to-path mapping, lookup counts, open fd maps, and hardlink path sets. Attribute and entry timeouts are zero, reducing cache staleness.

Dependencies and integration: Demonstrates broad pyfuse3 API coverage, Trio, native POSIX filesystem calls, FUSE request context uid/gid/umask, and optional writeback-cache configuration storage.

Risks and test signals: The file documents known risks: possible tree escape, weak behavior when underlying files are renamed/deleted externally, slow full-directory reads, non-POSIX readdir offsets for hardlinks, and simplified block/generation attributes. Tests should mount a temp tree and exercise create/read/write/truncate/chmod/chown/timestamps/link/symlink/rename/unlink/rmdir/statfs/readdir/forget, plus external mutation behavior and hardlink directory ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/examples/passthroughfs.py -->

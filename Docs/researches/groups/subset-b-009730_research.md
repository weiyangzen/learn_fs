<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/libtest.c -->
# sources/user-network-fs/nfs-utils/support/nfsidmap/libtest.c

Purpose: `libtest.c` is a small manual exerciser for libnfsidmap translation paths. It reads the normal idmap configuration through `nfs4_init_name_mapping(NULL)` and tries principal-to-id, name-to-id, group-list, and id-to-name conversions.

Important APIs and control flow: `main` expects `<user@nfsv4domain> <k5princ@REALM>`, enables debug logging with `nfs4_set_debug(3, NULL)`, initializes mapping, calls `nfs4_gss_princ_to_ids`, `nfs4_name_to_uid`, `nfs4_name_to_gid`, `nfs4_gss_princ_to_grouplist`, `nfs4_uid_to_name`, and `nfs4_gid_to_name`, and exits early after failures when `QUIT_ON_ERROR` is enabled.

State, dependencies, and integration: State is local stack buffers plus a global `conf_path` pointing at `/etc/idmapd.conf`, though initialization is delegated to the library. It depends on installed `nfsidmap.h` and links with `-lnfsidmap`.

Risks and test signals: The file uses old-style `main` without an explicit return type and fixed 32-byte owner output buffers. Useful tests are interactive runs with NSS, static, regex, and GSS principal mappings, including too-small output buffers and missing realm/domain configuration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/libtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/nfsidmap.h -->
# sources/user-network-fs/nfs-utils/support/nfsidmap/nfsidmap.h

Purpose: `nfsidmap.h` is the public libnfsidmap interface for NFSv4 owner/group string mapping, numeric UID/GID mapping, GSS principal mapping, group-list lookup, and debug logging.

Important APIs and types: It defines `NFS4_MAX_DOMAIN_LEN`, `extra_mapping_types`, `extra_mapping_params`, `nfs4_idmap_log_function_t`, and the exported `nfs4_*` functions. The API separates plain `name@domain` mapping from NFSv4 owner/group-owner helpers and has `_ex` variants for extra mapping parameters such as X.509 certificate content.

State, dependencies, and integration: The header depends on system `uid_t`, `gid_t`, and `size_t` types supplied by including code. It is consumed by `libnfsidmap.c`, bundled plugins, idmapd, tests, and ACL/userland NFSv4 callers.

Risks and test signals: There are no include guards in this snapshot, so repeated inclusion relies on build context. ABI stability matters for all prototypes and enum values. Tests should compile standalone consumers and exercise initialization/termination, default-domain lookup, numeric string fallback behavior, GSS group-list sizing, and logging callbacks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/nfsidmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/nfsidmap_common.c -->
# sources/user-network-fs/nfs-utils/support/nfsidmap/nfsidmap_common.c

Purpose: `nfsidmap_common.c` provides shared helpers for libnfsidmap plugins: local realm list derivation, no-strip/reformat policy parsing, and NSS buffer sizing.

Important APIs and control flow: `get_local_realms` returns cached `General/Local-Realms`; if absent it allocates a one-entry list containing the upper-case default NFSv4 domain. `free_local_realms` clears that cache. `get_nostrip` parses `General/No-Strip` into `IDTYPE_USER`/`IDTYPE_GROUP` flags and optionally sets `reformat_group` from `General/Reformat-Group`. `get_pwnam_buflen` and `get_grnam_buflen` use `sysconf` with a 16 KiB fallback.

State, dependencies, and integration: Static globals cache local realms, no-strip, and group reformat policy. It depends on `conffile.h`, `nfsidmap_private.h`, and `nfs4_get_default_domain`; plugins must initialize configuration first.

Risks and test signals: Allocation failure in the default realm path can leak the partially allocated list. Cached policy is not reset except process/plugin teardown. Tests should cover absent/present `Local-Realms`, all `No-Strip` variants, `Reformat-Group`, and sysconf fallback.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/nfsidmap_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/nfsidmap_plugin.h -->
# sources/user-network-fs/nfs-utils/support/nfsidmap/nfsidmap_plugin.h

Purpose: `nfsidmap_plugin.h` is the private ABI contract used by libnfsidmap translation plugins.

Important APIs and types: `struct trans_func` names a plugin and provides callbacks for initialization, GSS principal-to-ids, name-to-uid/gid, uid/gid-to-name, and GSS group-list lookup. It exports `idmap_verbosity`, `idmap_log_func`, `nfsidmap_conf_path`, `nfsidmap_config_get`, and the plugin entry point `libnfsidmap_plugin_init`. `IDMAP_LOG` centralizes verbosity-based logging, and `UNUSED` helps keep callback signatures uniform.

State, dependencies, and integration: Runtime state is owned by libnfsidmap and each plugin; this header only binds them. Bundled plugins `nss`, `regex`, `static`, and `umich_ldap` each return a `trans_func`.

Risks and test signals: This ABI is pointer-table based, so signature drift breaks dynamically loaded plugins. Callbacks return negative errno-style values by convention. Tests should compile all plugins, load them through libnfsidmap, and verify missing callbacks or failed init are handled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/nfsidmap_plugin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/nfsidmap_private.h -->
# sources/user-network-fs/nfs-utils/support/nfsidmap/nfsidmap_private.h

Purpose: `nfsidmap_private.h` exposes helper declarations and private structures shared only between libnfsidmap and bundled plugins.

Important APIs and types: It declares common-helper functions from `nfsidmap_common.c`, `idtypes` flags for user/group paths, `libnfsidmap_plugin_init_t`, and `struct mapping_plugin`, which holds a dynamic-library handle and returned `struct trans_func *`.

State, dependencies, and integration: It includes `conffile.h` and is included by plugin implementations and the core library. Durable state is not stored here, but the `mapping_plugin` layout mirrors dynamic plugin loading state in libnfsidmap.

Risks and test signals: The header has no guard in this snapshot and is not suitable for external consumers despite containing ABI-sensitive structures. Tests should build all bundled plugins and libnfsidmap together, verify callback dispatch through `mapping_plugin`, and cover plugin unload cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/nfsidmap_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/nss.c -->
# sources/user-network-fs/nfs-utils/support/nfsidmap/nss.c

Purpose: `nss.c` implements the `nsswitch` idmap plugin, translating NFSv4 owner strings and Kerberos principals through local libc NSS passwd/group databases.

Important APIs and control flow: `nss_uid_to_name` and `nss_gid_to_name` call `getpwuid_r`/`getgrgid_r` and format `local@domain` through `write_name`. `nss_name_to_uid` strips the default domain, then uses `getpwnam_r`. Group lookup supports `No-Strip` and optional `Reformat-Group`, with `_nss_name_to_gid` trying domain-stripped, raw, or `DOMAIN\name` formats. `nss_gss_princ_to_ids` validates `krb5`, checks principal realm against `Local-Realms`, then maps the local principal name; `nss_gss_princ_to_grouplist` calls `getgrouplist`.

State, dependencies, and integration: The plugin initializes `idmapd.conf`, caches the default domain in a static buffer, uses shared policy helpers, and returns `nss_trans` from `libnfsidmap_plugin_init`.

Risks and test signals: Realm comparison is case-sensitive, buffers grow on `ERANGE` in some paths but not all, and `nss_gss_princ_to_grouplist` returns the initialized `ret` on success unless `getgrouplist` fails. Tests should cover realm rejection, domain stripping, group reformatting, large NSS records, and group-list size handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/nss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/regex.c -->
# sources/user-network-fs/nfs-utils/support/nfsidmap/regex.c

Purpose: `regex.c` implements a configurable regex-based idmap plugin that extracts local account/group names from remote NFSv4 names and formats local names back into remote names.

Important APIs and control flow: `regex_init` reads `Regex/User-Regex`, `Group-Regex`, prefix/suffix options, optional `Group-Name-Prefix`, and optional prefix-exclusion regex. `regex_getpwnam` and `regex_getgrnam` run `regexec`, use the first captured submatch as the local name, optionally remove group prefixes, then call `getpwnam_r`/`getgrnam_r`. ID/name callbacks wrap those helpers, `write_name` composes reverse mappings, and principal callbacks accept `krb5` or `spkm3`.

State, dependencies, and integration: Compiled regexes and string pointers are global plugin state sourced from libnfsidmap configuration. It depends on POSIX regex, NSS, and shared buffer-size helpers.

Risks and test signals: `regex_init` returns success even after missing or failed regex compilation in the error path, which can leave uninitialized regex state. Reverse formatting uses repeated `strcat`, and input names are not escaped because regexes intentionally control parsing. Tests should cover missing config, bad regexes, capture selection, prefix exclusion, reverse output length, and group-list overflow.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/regex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/static.c -->
# sources/user-network-fs/nfs-utils/support/nfsidmap/static.c

Purpose: `static.c` implements a static idmap plugin where principals or NFSv4 names are explicitly mapped to local passwd/group names in the `[Static]` section of idmapd configuration.

Important APIs and control flow: `static_getpwnam` and `static_getgrnam` look up `Static/<principal>` and resolve the configured local user or group through NSS. Principal/name callbacks return UID/GID from those helpers. `static_init` reads all static tags, resolves each as both user and group, and caches reverse UID/GID-to-principal lookups in 256-bucket LIST hash tables.

State, dependencies, and integration: Persistent plugin state is the in-memory `uid_mappings` and `gid_mappings` tables. Config and NSS remain the source of truth. The plugin exposes `static_trans` to libnfsidmap.

Risks and test signals: Reverse callbacks use `strcpy` and ignore the output `len`. Mapping nodes are never freed during plugin lifetime, and hash collisions are linear. Tests should cover duplicate UID/GID mappings, missing local accounts, reverse mapping buffer limits, and both `krb5`/`spkm3` principal paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/static.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/umich_ldap.c -->
# sources/user-network-fs/nfs-utils/support/nfsidmap/umich_ldap.c

Purpose: `umich_ldap.c` implements the `umich_ldap` idmap plugin, mapping NFSv4 names, numeric IDs, and GSS principals through an LDAP schema with configurable object classes and attribute names.

Important APIs and control flow: `umichldap_init` reads `UMICH_SCHEMA` options for server, base DNs, TLS, referrals, SASL, timeout, canonicalization, and attribute mappings. `ldap_init_and_bind` creates a per-request LDAP handle, sets protocol/referral/TLS/SASL options, and binds. `umich_name_to_ids`, `umich_id_to_name`, and `umich_gss_princ_to_grouplist` issue LDAP searches, validate one-result cases, convert `uidNumber`/`gidNumber`, and fill output buffers. Public callbacks are collected in `umichldap_trans`.

State, dependencies, and integration: Global `ldap_info` and `ldap_map` store configuration. The code integrates OpenLDAP, optional Cyrus SASL/GSSAPI, `nfslib` address helpers, and libnfsidmap plugin dispatch.

Risks and test signals: This snapshot contains duplicated tokens around `sasl_interact_cb`, `umich_name_to_ids`, and `umichldap_name_to_uid` that would fail compilation as shown. LDAP filters interpolate unescaped external names/principals, and each lookup opens/binds a new connection. Tests should include build coverage, LDAP fixtures for user/group/principal/group-list mapping, TLS/SASL options, oversized filters, malicious filter characters, and group-list size negotiation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nfsidmap/umich_ldap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nsm/Makefile.am -->
# sources/user-network-fs/nfs-utils/support/nsm/Makefile.am

Purpose: `support/nsm/Makefile.am` builds the internal NSM support library used by statd and tests.

Important build APIs and control flow: It defines generated RPC files from `sm_inter.x`, builds `libnsm.a` from generated files plus `file.c` and `rpc.c`, and handles either an in-tree rpcgen or an external `@RPCGEN_PATH@`. Rules generate client, service, XDR, and header outputs, and a `sm_inter.h` rule appends an `sm_prog_1` prototype and links it into `support/include`.

State, dependencies, and integration: Generated sources are build-state artifacts and are removed via `CLEANFILES`. The library links conceptually into rpc.statd, sm-notify, and NSM tests.

Risks and test signals: Generated-file ordering depends on `BUILT_SOURCES` and rpcgen availability. The header rule mutates generated output after rpcgen. Tests should run `make distcheck`, clean rebuilds with in-tree and system rpcgen, and verify `support/include/sm_inter.h` exists.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nsm/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nsm/file.c -->
# sources/user-network-fs/nfs-utils/support/nsm/file.c

Purpose: `file.c` owns NSM/statd durable state: state number files, monitored-host records, notify-backup records, privilege dropping, and monitor record load/delete/retire operations.

Important APIs and control flow: Path helpers validate hostnames and construct paths under `nsm_base_dirname`. `nsm_get_state` reads and optionally advances the odd NSM state number via atomic write, and `nsm_update_kernel_state` posts it to `/proc/sys/fs/nfs/nsm_local_state`. `nsm_insert_monitored_host`, `nsm_load_monitor_list`, `nsm_load_notify_list`, `nsm_delete_monitored_host`, and `nsm_delete_notified_host` serialize or parse text records containing callback address, RPC tuple, private cookie, mon_name, and my_name. `nsm_drop_privileges` changes to the state directory owner and preserves only bind-service capability when possible.

State, dependencies, and integration: Durable files live in `sm`, `sm.bak`, and `state`; updates use temp-file rename. It depends on libcap/prctl, `generic_*` path helpers, xlog, NSM XDR structs, and statd monitor callbacks.

Risks and test signals: Records only encode IPv4 callback addresses, append/delete rewrites are not locked, malformed records can abort a load, and privilege logic depends on directory ownership. Tests should cover atomic state updates, reboot retirement, multi-record host files, bad hostnames, corrupted lines, non-root state directories, and kernel-state write failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nsm/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nsm/rpc.c -->
# sources/user-network-fs/nfs-utils/support/nsm/rpc.c

Purpose: `rpc.c` constructs and parses the UDP ONC RPC messages statd needs without relying on a separate RPC client handle per program/version.

Important APIs and control flow: `nsm_next_xid`, `nsm_init_rpc_header`, and `nsm_init_xdrmem` prepare AUTH_NULL RPC messages. `nsm_xmit_getport` sends PMAP v2 queries for IPv4, `nsm_xmit_getaddr` sends RPCB v3 `GETADDR` for IPv6 when libtirpc is available, and `nsm_xmit_rpcbind` selects by address family. `nsm_xmit_notify` sends `SM_NOTIFY`; `nsm_xmit_nlmcall` sends the NLM callback requested by monitor records. Reply parsing is split into `nsm_parse_reply`, `nsm_recv_getport`, `nsm_recv_getaddr`, and `nsm_recv_rpcbind`.

State, dependencies, and integration: Static XID state is process-local. It uses XDR memory streams, rpcbind/pmap protocol definitions, `nfs_sockaddr2universal`, `nfs_universal2port`, and statd scheduling code.

Risks and test signals: XIDs are predictable and not synchronized across threads, only UDP is supported, PMAP is IPv4-only, and sendto short writes fail the call. Tests should cover XDR encode/decode, IPv4/IPv6 rpcbind, bad replies, unregistered programs, and malformed universal addresses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/nsm/rpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/reexport/Makefile.am -->
# sources/user-network-fs/nfs-utils/support/reexport/Makefile.am

Purpose: `support/reexport/Makefile.am` builds the reexport support library and the `fsidd` helper daemon.

Important build APIs and control flow: It defines `libreexport.la` from `reexport.c`, `reexport.h`, and `reexport_backend.h`, and `fsidd` from `fsidd.c` plus `backend_sqlite.c`. `libreexport_la_CPPFLAGS` points at support headers, while `fsidd_LDADD` links SQLite, libevent, and support libraries.

State, dependencies, and integration: Build artifacts feed export parsing/mountd code through `libreexport.la`, while the installed daemon backs the AF_UNIX fsid service.

Risks and test signals: Runtime reexport support depends on both sqlite and libevent availability, and service/library version skew can break the text socket protocol. Tests should build with/without reexport dependencies, verify `fsidd` linkage, and run integration lookups against the library client.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/reexport/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/reexport/backend_sqlite.c -->
# sources/user-network-fs/nfs-utils/support/reexport/backend_sqlite.c

Purpose: `backend_sqlite.c` implements the sqlite-backed reexport database that maps export paths to stable numeric fsid values.

Important APIs and control flow: `sqlite_plug_init` seeds a small PRNG for lock backoff, opens the configured database, and creates `fsidnums(num INTEGER PRIMARY KEY, path TEXT UNIQUE)`. `get_fsidnum_by_path` and `sqlite_plug_path_by_fsidnum` run prepared SELECTs. `new_fsidnum_by_path` inserts the smallest free positive fsid via an SQL self-join/UNION query with `RETURNING`, handling unique races by rechecking. `sqlite_plug_fsidnum_by_path` combines lookup and optional creation.

State, dependencies, and integration: Static `sqlite3 *db` and `init_done` hold plugin state. The backend is exported as `sqlite_plug_ops` for `fsidd`.

Risks and test signals: `sqlite_plug_destroy` closes the DB but does not reset `init_done`, `new_fsidnum_by_path` may not mark success after the constraint recheck, and backoff is randomized but unbounded by total time. Tests should cover concurrent creation races, locked DBs, path uniqueness, fsid reuse gaps, database config override, and init/destroy/reinit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/reexport/backend_sqlite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/reexport/fsidd.c -->
# sources/user-network-fs/nfs-utils/support/reexport/fsidd.c

Purpose: `fsidd.c` is the AF_UNIX service daemon that serializes access to the reexport fsid database and exposes a small text command protocol.

Important APIs and control flow: `main` reads `nfs.conf`, initializes the backend, binds a `SOCK_SEQPACKET` socket from `reexport/fsidd_socket`, creates a libevent base, and accepts clients. `client_cb` handles `get_fsidnum`, `get_or_create_fsidnum`, `get_path`, and `version`, returning `+ result` or `- reason`. `srv_cb` accepts clients as nonblocking and installs persistent read events.

State, dependencies, and integration: Global `evbase` and `dbbackend` own process state. The default socket is an abstract namespace path from `FSID_SOCKET_NAME`. It integrates with `reexport.c` clients and `fsidd.service`.

Risks and test signals: `accept4` errors are not checked before `event_new`, request paths are trusted as raw text without newline/protocol escaping, and some server errors return empty success. Tests should cover concurrent clients, abstract and filesystem sockets, bad commands, malformed fsids, backend failure, long paths near `PATH_MAX`, and daemon restart while clients reconnect.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/reexport/fsidd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/reexport/reexport.c -->
# sources/user-network-fs/nfs-utils/support/reexport/reexport.c

Purpose: `reexport.c` is the client-side helper used while parsing exports to obtain stable fsid numbers from `fsidd` and apply reexport policy to `struct exportent`.

Important APIs and control flow: `reexpdb_init` retries the `fsidd` connection, `do_fsidd_cmd` writes one socket request and parses one reply, and wrappers implement path-to-fsid, fsid-to-path, and reconnect behavior. `reexpdb_uncover_subvolume` uses fsid lookup followed by `nfsd_path_statfs` to trigger automounts. `reexpdb_apply_reexport_settings` skips non-reexports, UUID fsids, and v4 roots, then enforces or allocates numeric fsids depending on `e_reexport`.

State, dependencies, and integration: Static `fsidd_srv` caches the socket. It depends on `nfs.conf`, `nfsd_path`, export flags, and the fsidd text protocol.

Risks and test signals: Failed `connect` leaks the just-created socket, replies are capped at 1023 bytes, command strings cannot encode paths containing protocol separators safely, and reconnection closes on parse failures. Tests should cover daemon absence/restart, auto fsid allocation, configured fsid mismatch, v4 root skip, UUID skip, and very long paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/reexport/reexport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/reexport/reexport.h -->
# sources/user-network-fs/nfs-utils/support/reexport/reexport.h

Purpose: `reexport.h` declares reexport modes and the public helper functions that export parsing/mountd code use.

Important APIs and types: It defines `REEXP_NONE`, `REEXP_AUTO_FSIDNUM`, `REEXP_PREDEFINED_FSIDNUM`, and `REEXP_DB`, plus `reexpdb_init`, `reexpdb_destroy`, `reexpdb_fsidnum_by_path`, `reexpdb_uncover_subvolume`, and `reexpdb_apply_reexport_settings`. `FSID_SOCKET_NAME` sets the default abstract Unix socket.

State, dependencies, and integration: The header includes `exportfs.h` for `struct exportent` and coordinates with `fsidd.service`, `fsidd.c`, and `reexport.c`.

Risks and test signals: Mode values are ABI/config semantics for export options. The abstract socket default starts with `@`, which both client and daemon translate into a NUL-prefixed Unix path. Tests should compile consumers, parse each reexport mode, and verify socket override compatibility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/reexport/reexport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/reexport/reexport_backend.h -->
# sources/user-network-fs/nfs-utils/support/reexport/reexport_backend.h

Purpose: `reexport_backend.h` defines the backend plugin interface used by `fsidd` to store and retrieve reexport path/fsid mappings.

Important APIs and types: `struct reexpdb_backend_plugin` contains `fsidnum_by_path`, `path_by_fsidnum`, `initdb`, and `destroydb` callbacks. It declares the sqlite implementation `sqlite_plug_ops`.

State, dependencies, and integration: The header itself owns no state. `fsidd.c` uses a `struct reexpdb_backend_plugin *` initialized to `&sqlite_plug_ops`, making sqlite the built-in backend.

Risks and test signals: There is no version field or capability negotiation, so new backends must preserve callback semantics exactly. Tests should compile with sqlite backend, add a mock backend in unit tests, and validate found/not-found/error separation in callback outputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/support/reexport/reexport_backend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/60-nfs.rules -->
# sources/user-network-fs/nfs-utils/systemd/60-nfs.rules

Purpose: `60-nfs.rules` applies NFS-related sysctl settings when relevant kernel modules are added.

Important APIs and control flow: udev rules match `ACTION=="add"`, `SUBSYSTEM=="module"`, and module names `sunrpc`, `rpcrdma`, `lockd`, `nfsv4`, and `nfs`. Each rule runs `/sbin/sysctl -q --pattern ... --system` with a regex narrowed to the sysctl namespace supported by that module.

State, dependencies, and integration: It has no persistent state of its own; it causes sysctl state to be loaded from the system configuration stack. It integrates with udev and systemd module loading.

Risks and test signals: The comment says "systctl", but behavior is clear. Incorrect regexes could miss module-specific knobs or apply too broad a set. Tests should load modules in a test VM/container with udev monitoring and confirm expected sysctl patterns are applied without failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/60-nfs.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/Makefile.am -->
# sources/user-network-fs/nfs-utils/systemd/Makefile.am

Purpose: `systemd/Makefile.am` installs NFS systemd units, udev rules, man pages, and system generators according to configure-time feature flags.

Important build APIs and control flow: `unit_files` starts with common server/client units and conditionally adds idmapd, v4 server, blkmapd, GSS, svcgssd, and nfsdcld units. It builds `nfsroot-generator`, `nfs-server-generator`, and `rpc-pipefs-generator` from common `systemd.c/systemd.h` plus generator sources. Under `INSTALL_SYSTEMD`, `install-data-hook` copies unit files and `60-nfs.rules` to target directories and renames the pipefs mount template to the configured mount unit.

State, dependencies, and integration: It links generators against support libraries for NFS, export parsing, misc, and reexport.

Risks and test signals: Conditional unit lists must stay aligned with configured daemons. Install hooks use plain `cp`, so packaging paths and template substitution matter. Tests should run feature-matrix builds and inspect installed unit/generator names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/auth-rpcgss-module.service -->
# sources/user-network-fs/nfs-utils/systemd/auth-rpcgss-module.service

Purpose: This unit loads the `auth_rpcgss` kernel module before GSS-related NFS services test kernel GSS proxy support.

Important APIs and control flow: It is a `DefaultDependencies=no` oneshot service ordered before `gssproxy.service`, `rpc-svcgssd.service`, and `rpc-gssd.service`, wants gssproxy and rpc.gssd, and runs `/sbin/modprobe -q auth_rpcgss`. It only runs when `/etc/krb5.keytab` exists and not inside a container.

State, dependencies, and integration: `RemainAfterExit=yes` leaves service state active after modprobe. It integrates with NFS client/server GSS units and kernel RPCSEC_GSS support.

Risks and test signals: Built-in kernel support makes modprobe fail harmlessly only if dependent units tolerate it. Keytab-based activation may skip environments using alternative credentials. Tests should verify ordering with gssproxy/rpc.gssd and behavior with module built-in, absent keytab, and containers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/auth-rpcgss-module.service -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/fsidd.service -->
# sources/user-network-fs/nfs-utils/systemd/fsidd.service

Purpose: `fsidd.service` starts the reexport fsid daemon required by reexport-aware mountd/server configuration.

Important APIs and control flow: The unit starts after `local-fs.target`, before `nfs-mountd.service` and `nfs-server.service`, and executes `/usr/sbin/fsidd`. Its install section is `RequiredBy=nfs-mountd.service nfs-server.service`, making those services pull it in when enabled.

State, dependencies, and integration: Runtime state is the sqlite reexport DB and AF_UNIX socket managed by `fsidd`. The unit provides ordering for `reexport.c` clients that connect during export processing.

Risks and test signals: There is no explicit `Type`, restart policy, or dependency on the database directory. Tests should enable nfs-server/mountd and verify fsidd starts early, socket is available, and failure propagates to reexport users as expected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/fsidd.service -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/nfs-blkmap.service -->
# sources/user-network-fs/nfs-utils/systemd/nfs-blkmap.service

Purpose: This service runs `blkmapd`, the pNFS block layout mapping daemon.

Important APIs and control flow: It disables default dependencies, conflicts with shutdown unmount, requires and starts after `rpc_pipefs.target`, is `PartOf=nfs-utils.service`, and runs as a forking service with `/run/blkmapd.pid`.

State, dependencies, and integration: It depends on rpc_pipefs being mounted and participates in the broader NFS client service group. The daemon persists runtime state in its own pidfile and kernel/rpc_pipefs interactions.

Risks and test signals: Forking/pidfile assumptions must match daemon behavior. Missing rpc_pipefs blocks service startup. Tests should start/stop with `nfs-client.target`, restart `nfs-utils.service`, and verify clean shutdown ordering before unmount.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/nfs-blkmap.service -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/nfs-idmapd.service -->
# sources/user-network-fs/nfs-utils/systemd/nfs-idmapd.service

Purpose: This unit runs `rpc.idmapd`, the NFSv4 ID-name mapping daemon.

Important APIs and control flow: It requires `rpc_pipefs.target`, starts after rpc_pipefs, local filesystems, and network-online, wants network-online, and is `PartOf=nfs-server.service`. It runs `/usr/sbin/rpc.idmapd` as a forking service.

State, dependencies, and integration: The daemon uses rpc_pipefs and idmap configuration/cache state. The unit is pulled into server workflows through `nfs-server.service` wants.

Risks and test signals: Being only `PartOf=nfs-server.service` means client-only activation depends on other targets not shown in this file. Tests should verify NFSv4 server startup pulls idmapd, rpc_pipefs ordering, restart propagation, and daemon failure behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/nfs-idmapd.service -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/nfs-mountd.service -->
# sources/user-network-fs/nfs-utils/systemd/nfs-mountd.service

Purpose: This unit runs `rpc.mountd`, the NFS mount daemon used by the NFS server.

Important APIs and control flow: It has no default dependencies, requires `proc-fs-nfsd.mount`, wants network-online, starts after nfsd procfs, network/local filesystems, and rpcbind socket, and `BindsTo=nfs-server.service`. It runs `/usr/sbin/rpc.mountd` as a forking service.

State, dependencies, and integration: mountd depends on kernel nfsd state and export configuration. `BindsTo` ties its lifetime to `nfs-server.service`.

Risks and test signals: rpcbind ordering is `After` only, while `nfs-server.service` wants rpcbind.socket. Reexport configs may also require fsidd ordering. Tests should cover server start/stop, export reload, rpcbind unavailable, and shutdown ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/nfs-mountd.service -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/nfs-server-generator.c -->
# sources/user-network-fs/nfs-utils/systemd/nfs-server-generator.c

Purpose: `nfs-server-generator.c` emits a drop-in for `nfs-server.service` that orders it with exported filesystems and loopback NFS mounts.

Important APIs and control flow: `main` validates the generator argument layout, disables syslog, reads `/etc/exports` and `/etc/exports.d`, creates `nfs-server.service.d/order-with-mounts.conf`, and writes `[Unit]` dependency lines. For exported paths it emits `RequiresMountsFor` unless the export has an explicit mountpoint or a covering fstab entry with `noauto`. For fstab `nfs`/`nfs4` mounts it emits `Before=<escaped>.mount`.

State, dependencies, and integration: It reads exports, `/etc/fstab`, and uses `systemd_escape`. Generated files live in the systemd generator output directory for one boot transaction.

Risks and test signals: `is_unique` stores export path pointers without freeing, fstab prefix matching can be broad, and paths with quotes are only partially handled. Tests should run generator fixtures for spaces, duplicate exports, `noauto`, loopback mounts, and empty exports.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/nfs-server-generator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/nfs-server.service -->
# sources/user-network-fs/nfs-utils/systemd/nfs-server.service

Purpose: `nfs-server.service` orchestrates full NFS server startup and shutdown.

Important APIs and control flow: It requires network target, `proc-fs-nfsd.mount`, and `nfs-mountd.service`; wants rpcbind, network-online, statd, idmapd, statd-notify, nfsdcld, auth-rpcgss, and svcgssd. Startup refreshes exports, then runs `nfsdctl autostart` or falls back to `rpc.nfsd`; shutdown sets nfsd threads to zero or falls back to `rpc.nfsd 0`, then unexports and flushes exportfs state.

State, dependencies, and integration: It leaves oneshot state active and is installed for `multi-user.target`. Kernel nfsd state, export tables, rpcbind, GSS services, and client tracking are integration points.

Risks and test signals: Several dependencies are wants, so missing helpers may not fail the server unit. Shell fallback behavior must be tested with and without `nfsdctl`. Tests should cover start, reload, stop, partial dependency failures, and export cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/nfs-server.service -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/nfs-utils.service -->
# sources/user-network-fs/nfs-utils/systemd/nfs-utils.service

Purpose: `nfs-utils.service` is a grouping/restart unit for NFS server and client daemons.

Important APIs and control flow: It is a oneshot service that runs `/bin/true` and remains active. Units declaring `PartOf=nfs-utils.service` restart when this service is restarted, making it a service-style replacement for a restartable target.

State, dependencies, and integration: It owns no daemon state. Integration is through systemd `PartOf` relationships from units such as rpc.statd, rpc.gssd, blkmapd, and others.

Risks and test signals: It should not be stopped in normal operation, and only units that declare `PartOf` participate. Tests should restart it and verify expected daemons restart while unrelated units do not.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/nfs-utils.service -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/nfsdcld.service -->
# sources/user-network-fs/nfs-utils/systemd/nfsdcld.service

Purpose: This unit runs `nfsdcld`, the NFSv4 client tracking daemon for server-side lease recovery.

Important APIs and control flow: It disables default dependencies, conflicts with unmount, requires rpc_pipefs and `proc-fs-nfsd.mount`, starts after those plus `systemd-remount-fs.service`, and runs `/usr/sbin/nfsdcld` as a forking service.

State, dependencies, and integration: nfsdcld persists client tracking data and communicates through kernel nfsd/rpc_pipefs interfaces. It is wanted by server units.

Risks and test signals: The unit has no install section here, so activation depends on wants from server services. Tests should validate server startup pulls it in, client tracking database availability, restart behavior, and shutdown before unmount.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/nfsdcld.service -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/nfsroot-generator.c -->
# sources/user-network-fs/nfs-utils/systemd/nfsroot-generator.c

Purpose: `nfsroot-generator.c` creates an initrd `sysroot.mount` unit for NFS root filesystems described on the kernel command line.

Important APIs and control flow: `get_nfsroot_info_from_cmdline` parses `/proc/cmdline` forms `root=/dev/nfs nfsroot=...` and dracut-style `root=nfs[4]:...`, deriving server from `ip=` when omitted and splitting path/options. `generate_sysroot_mount_unit` writes `sysroot.mount` with `_netdev`, `nofail`, `x-systemd.after=network-online.target`, and any provided options. `main` only emits units in initrd.

State, dependencies, and integration: It uses transient systemd generator output and depends on `/proc/cmdline`, initrd detection via `systemd_in_initrd`, and `systemd_escape` helpers.

Risks and test signals: Parsing is in-place and assumes `root` is non-null before `strcmp(root, "/dev/nfs")`; malformed cmdlines can return errors. Tests should cover both documented syntaxes, omitted server with `ip=`, option separators, non-initrd no-op, and malformed inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/nfsroot-generator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/nfsv4-exportd.service -->
# sources/user-network-fs/nfs-utils/systemd/nfsv4-exportd.service

Purpose: This unit runs `nfsv4.exportd`, the NFSv4-only mount/export daemon.

Important APIs and control flow: It requires `proc-fs-nfsd.mount`, wants network-online, starts after nfsd procfs, network-online, and local filesystems, and `BindsTo=nfsv4-server.service`. It runs `/usr/sbin/nfsv4.exportd` as a forking service.

State, dependencies, and integration: It is tied to `nfsv4-server.service` and kernel nfsd procfs, serving export information for an NFSv4-only server mode.

Risks and test signals: There is no install section here, so the v4 server unit is the activation path. Tests should start/stop `nfsv4-server.service`, verify export daemon binding, and exercise network-online delays.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/nfsv4-exportd.service -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/nfsv4-server.service -->
# sources/user-network-fs/nfs-utils/systemd/nfsv4-server.service

Purpose: `nfsv4-server.service` starts an NFSv4-only server stack.

Important APIs and control flow: It requires network target, `proc-fs-nfsd.mount`, and `nfsv4-exportd.service`; wants network-online, idmapd, nfsdcld, and auth-rpcgss. Startup refreshes exports and runs `rpc.nfsd -N 3`, disabling NFSv3; shutdown runs `rpc.nfsd 0` and flushes export state.

State, dependencies, and integration: It remains active as a oneshot and installs into `multi-user.target`. It integrates with kernel nfsd, exportfs, id mapping, client tracking, and GSS support.

Risks and test signals: GSS services are ordered after but only auth-rpcgss is wanted here. Tests should verify NFSv3 disabled, NFSv4 exports active, idmapd/nfsdcld ordering, stop cleanup, and coexistence conflict expectations with full `nfs-server.service`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/nfsv4-server.service -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/rpc-gssd.service.in -->
# sources/user-network-fs/nfs-utils/systemd/rpc-gssd.service.in

Purpose: This template unit runs `rpc.gssd`, the RPC security service for NFS client and server Kerberos/GSS use.

Important APIs and control flow: It has no default dependencies, conflicts with unmount, requires and starts after `rpc_pipefs.target`, checks for `@_sysconfdir@/krb5.keytab`, is `PartOf=nfs-utils.service`, and starts `/usr/sbin/rpc.gssd` as a forking service.

State, dependencies, and integration: Template substitution supplies the sysconfdir. Runtime state lives in rpc_pipefs and Kerberos credential/keytab infrastructure.

Risks and test signals: Keytab condition suppresses the service for keyless or gssproxy-only setups. Tests should verify substitution, rpc_pipefs ordering, restart via nfs-utils, and behavior with missing keytab.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/rpc-gssd.service.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/rpc-pipefs-generator.c -->
# sources/user-network-fs/nfs-utils/systemd/rpc-pipefs-generator.c

Purpose: `rpc-pipefs-generator.c` creates runtime systemd units when the configured rpc_pipefs mount path differs from the default.

Important APIs and control flow: `main` reads `NFS_CONFFILE`, exits when `general/pipefs-directory` is absent or equals the default, rejects paths already mounted by a non-rpc_pipefs filesystem, and calls `generate_target`. `generate_target` escapes the path to a mount unit name, writes that mount unit with `What=sunrpc`, `Type=rpc_pipefs`, then writes `rpc_pipefs.target` requiring and ordering after it.

State, dependencies, and integration: Generated files are transient systemd generator output. It depends on nfs.conf, `/etc/mtab`, and `systemd_escape`.

Risks and test signals: `is_non_pipefs_mountpoint` uses string comparisons that can misread unusual mtab entries, and generated directories are minimally checked. Tests should cover default no-op, custom path, path escaping, already-mounted wrong type, and generator argument validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/rpc-pipefs-generator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/rpc-statd-notify.service -->
# sources/user-network-fs/nfs-utils/systemd/rpc-statd-notify.service

Purpose: This unit runs `sm-notify` to tell NFS peers that the local system restarted.

Important APIs and control flow: It disables default dependencies, starts after local filesystems, network-online, name service lookup, and `nfs-server.service`, is `PartOf=nfs-utils.service`, and runs `-/usr/sbin/sm-notify` as a forking service with `RemainAfterExit=yes`. The leading dash makes failures non-fatal to systemd.

State, dependencies, and integration: It consumes NSM notify records and works with rpc.statd state. Ordering after nfs-server ensures clients are not notified before the server is available.

Risks and test signals: Failure is ignored, which can hide notification problems. Tests should simulate pending `sm.bak` records, network unavailable, server-enabled ordering, and restart idempotence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/rpc-statd-notify.service -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/rpc-statd.service -->
# sources/user-network-fs/nfs-utils/systemd/rpc-statd.service

Purpose: This unit runs `rpc.statd`, the NFSv2/v3 status monitor used for lock recovery.

Important APIs and control flow: It disables default dependencies, conflicts with unmount, requires name service lookup and rpcbind socket, wants network-online and statd-notify, starts after network, lookup, rpcbind service/socket, and is `PartOf=nfs-utils.service`. It sets `RPC_STATD_NO_NOTIFY=1`, runs as a forking service with `/run/rpc.statd.pid`.

State, dependencies, and integration: statd uses the NSM on-disk database and rpcbind registration. Notification is delegated to `rpc-statd-notify.service`.

Risks and test signals: Both `rpcbind.service` and socket ordering are present, but only socket is required. Tests should verify rpcbind activation, pidfile handling, no-notify environment behavior, restart propagation, and shutdown before unmount.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/rpc-statd.service -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/rpc-svcgssd.service -->
# sources/user-network-fs/nfs-utils/systemd/rpc-svcgssd.service

Purpose: This unit runs the legacy server-side RPCSEC_GSS daemon when gssproxy support is unavailable.

Important APIs and control flow: It starts after local filesystems and gssproxy, is `PartOf` both nfs-server and nfs-utils, and has OR-style `ConditionPathExists` checks requiring no gssproxy pid and no `/proc/net/rpc/use-gss-proxy`, plus a keytab. It runs `/usr/sbin/rpc.svcgssd` as a forking service.

State, dependencies, and integration: It integrates with Kerberos keytab state, gssproxy detection, and server GSS service startup.

Risks and test signals: Systemd `ConditionPathExists=|` semantics are subtle, so packaging changes can accidentally start both gssproxy and svcgssd or neither. Tests should cover gssproxy available/unavailable, missing keytab, restart via server/nfs-utils, and kernel support detection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/rpc-svcgssd.service -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/rpc_pipefs.target.in -->
# sources/user-network-fs/nfs-utils/systemd/rpc_pipefs.target.in

Purpose: This template target groups the configured rpc_pipefs mount unit.

Important APIs and control flow: The unit simply `Requires=@_rpc_pipefsmount@` and starts `After=@_rpc_pipefsmount@`, making consumers depend on a target rather than hard-coding the concrete mount unit name.

State, dependencies, and integration: Template substitution supplies the configured mount unit. It is used by rpc.gssd, idmapd, blkmapd, nfsdcld, and generated pipefs units.

Risks and test signals: If substitution does not match the installed mount unit name, all dependent daemons can fail to order correctly. Tests should inspect installed unit files for consistent `_rpc_pipefsmount` replacement and verify target activation mounts rpc_pipefs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/rpc_pipefs.target.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/systemd.c -->
# sources/user-network-fs/nfs-utils/systemd/systemd.c

Purpose: `systemd.c` provides helper functions shared by nfs-utils systemd generators.

Important APIs and control flow: `systemd_escape` implements systemd path-to-unit escaping: trim leading/trailing slash behavior, collapse slash runs to `-`, encode root as `-`, leave ASCII alnum, `:`, `.`, and `_`, and encode other bytes as `\xNN`. `systemd_len` computes allocation size, and `hexify` writes escape sequences. `systemd_in_initrd` checks `/etc/initrd-release`.

State, dependencies, and integration: It allocates returned unit names for callers to free and uses only libc/system calls. Generators for nfs-server, nfsroot, and rpc-pipefs depend on it.

Risks and test signals: `systemd_escape` does not check `malloc` before writing through `result`, and the allowed-character set must stay aligned with systemd. Tests should cover root, duplicate slashes, leading dots, spaces, non-ASCII bytes, colons, suffix appending, and malloc failure handling if injectable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/systemd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/systemd.h -->
# sources/user-network-fs/nfs-utils/systemd/systemd.h

Purpose: `systemd.h` declares the shared systemd generator helper API.

Important APIs and types: It exposes `char *systemd_escape(char *path, char *suffix)` and `int systemd_in_initrd(void)`.

State, dependencies, and integration: The header owns no state. Callers must free the string returned by `systemd_escape`. It is included by the systemd generator sources.

Risks and test signals: There is no include guard in this snapshot. Tests should compile all generator sources together and validate callers free returned names on all paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/systemd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/var-lib-nfs-rpc_pipefs.mount.in -->
# sources/user-network-fs/nfs-utils/systemd/var-lib-nfs-rpc_pipefs.mount.in

Purpose: This mount template defines the default rpc_pipefs mount unit.

Important APIs and control flow: The unit is `DefaultDependencies=no`, starts after `systemd-tmpfiles-setup.service`, conflicts with unmount, and mounts `What=sunrpc` at `@_statedir@/rpc_pipefs` with `Type=rpc_pipefs`.

State, dependencies, and integration: Template substitution supplies the configured state directory. The installed mount unit is required by `rpc_pipefs.target` and services that use rpc_pipefs.

Risks and test signals: Wrong state-dir substitution or unit filename mismatch breaks dependent NFS daemons. Tests should validate template substitution, mount activation, shutdown ordering, and compatibility with custom pipefs-directory generated by `rpc-pipefs-generator`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/systemd/var-lib-nfs-rpc_pipefs.mount.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tests/Makefile.am -->
# sources/user-network-fs/nfs-utils/tests/Makefile.am

Purpose: `tests/Makefile.am` wires top-level nfs-utils tests and the `statdb_dump` helper into automake.

Important build APIs and control flow: It builds `statdb_dump` from `statdb_dump.c`, links support NFS, NSM, misc, and optional cap libraries, descends into `nsm_client`, and declares `t0001-statd-basic-mon-unmon.sh` as the test. `EXTRA_DIST` packages `test-lib.sh` and tests.

State, dependencies, and integration: Test binaries depend on built support libraries, generated NSM code, and system capabilities for statd integration.

Risks and test signals: `t0002-nfsconf.sh` and `tests/nfsconf` fixtures are present but not listed in `TESTS` in this snapshot. Tests should run `make check`, ensure linked libraries are current, and confirm distributed test fixtures are complete.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tests/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tests/nfsconf/01-errors.conf -->
# sources/user-network-fs/nfs-utils/tests/nfsconf/01-errors.conf

Purpose: `01-errors.conf` is a negative fixture for the nfs.conf parser.

Important content and control flow: It contains malformed sections, unterminated quotes, missing keys/values, invalid bracket syntax, duplicate-looking assignments, and environment-variable-like data. The file is intended to drive parser diagnostics rather than daemon behavior.

State, dependencies, and integration: There is no runtime state; it is consumed by nfsconf tests or manual parser checks alongside valid fixtures.

Risks and test signals: The fixture is only valuable if the test harness asserts specific failures and recovery behavior. Tests should verify the parser rejects bad section syntax, handles partial assignments predictably, and continues or aborts according to documented error policy.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tests/nfsconf/01-errors.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tests/nfsconf/02-valid.conf -->
# sources/user-network-fs/nfs-utils/tests/nfsconf/02-valid.conf

Purpose: `02-valid.conf` is a positive nfs.conf parser fixture covering sections, subsection labels, quoting, whitespace, variable expansion, duplicate sections, and includes.

Important content and control flow: It defines `[environment]`, `[section_one]`, and repeated `[section_two "..."]` blocks. Values include `$three`, quoted strings with extra whitespace, keys containing spaces, and an `include = "02-valid.sub"` directive.

State, dependencies, and integration: Test state comes from parser output and the included subfile. It integrates with `t0002-nfsconf.sh` or nfsconf tooling.

Risks and test signals: If include files are missing from distribution or `srcdir`, tests become path-sensitive. Assertions should verify expansion, trimming, duplicate section merge/override behavior, subsection selection, and include resolution.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tests/nfsconf/02-valid.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tests/nsm_client/Makefile.am -->
# sources/user-network-fs/nfs-utils/tests/nsm_client/Makefile.am

Purpose: `tests/nsm_client/Makefile.am` builds the synthetic NSM client and lockd simulator used by statd tests.

Important build APIs and control flow: It generates `nlm_sm_inter` client, service, XDR, and header files from `nlm_sm_inter.x` using in-tree or system rpcgen, builds `nsm_client` from generated files plus `nsm_client.c`, and links support NFS, NSM, libcap, and tirpc.

State, dependencies, and integration: Generated files are build artifacts listed in `BUILT_SOURCES` and `CLEANFILES`. The binary is used by shell tests to issue SM_MON/UNMON/NOTIFY and emulate NLM callbacks.

Risks and test signals: rpcgen path selection and generated header freshness are common failure points. Tests should cover clean tree builds, dist builds, and execution of generated client/server RPC stubs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tests/nsm_client/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tests/nsm_client/nsm_client.c -->
# sources/user-network-fs/nfs-utils/tests/nsm_client/nsm_client.c

Purpose: `nsm_client.c` is a synthetic command-line NSM client plus NLM notification server for exercising rpc.statd behavior.

Important APIs and control flow: `main` parses host/name/program/version options and dispatches `daemon`, `crash`, `stat`, `notify`, `unmon_all`, `unmon`, or `mon`. `nsm_client_get_rpcclient` resolves the statd host, asks rpcbind for `SM_PROG/SM_VERS`, and creates a UDP RPC client. Command helpers call generated NSM stubs. `daemon_simulator` registers NLM callback services, and `nlm_sm_notify_3_svc`/`nlm_sm_notify_4_svc` print received reboot notifications.

State, dependencies, and integration: It depends on generated `nlm_sm_inter` files, libtirpc/SunRPC, nfs-utils RPC helpers, and statd running locally or remotely.

Risks and test signals: The getopt switch lacks `break` statements, so one option falls through and can unintentionally set later fields. Some argument-count checks are too low for commands that read two extra args. Tests should cover each command, option parsing, invalid cookies, rpcbind failures, and daemon callback receipt.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tests/nsm_client/nsm_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tests/statdb_dump.c -->
# sources/user-network-fs/nfs-utils/tests/statdb_dump.c

Purpose: `statdb_dump.c` dumps statd NSM monitor/notify database records in a stable text format for tests.

Important APIs and control flow: A callback passed to `nsm_load_monitor_list` or `nsm_load_notify_list` formats host, timestamp, address, program/version/procedure, cookie hex, mon_name, and my_name. `main` sets up pathnames from arguments and selects monitor or notify database dumping.

State, dependencies, and integration: It reads statd state directories through `support/nsm/file.c` APIs. Static buffers hold cookie and address formatting. It integrates with shell tests that compare statd side effects.

Risks and test signals: Output stability depends on timestamp and address formatting. Tests should cover empty DBs, malformed records, IPv4 address formatting, cookie conversion, monitor versus notify directory selection, and non-default state directories.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tests/statdb_dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tests/t0001-statd-basic-mon-unmon.sh -->
# sources/user-network-fs/nfs-utils/tests/t0001-statd-basic-mon-unmon.sh

Purpose: This shell test exercises basic rpc.statd monitor and unmonitor behavior using the synthetic `nsm_client`.

Important APIs and control flow: It sources `test-lib.sh`, checks root and `/dev/log`, sets up temporary state, starts statd, issues monitor/unmonitor requests, dumps the stat database with `statdb_dump`, and validates expected record creation/deletion through shell assertions.

State, dependencies, and integration: It manipulates a temporary statd state directory, starts system daemons/binaries from the build tree, and depends on rpcbind/logging environment.

Risks and test signals: It likely requires root privileges and a working syslog socket, so CI may skip or fail outside privileged environments. Tests should verify cleanup traps, non-default state path isolation, statd lifecycle, and expected DB contents after each operation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tests/t0001-statd-basic-mon-unmon.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tests/t0002-nfsconf.sh -->
# sources/user-network-fs/nfs-utils/tests/t0002-nfsconf.sh

Purpose: This shell test is intended to validate nfs.conf parser behavior against the nfsconf fixtures.

Important APIs and control flow: It sources the shared test library, points parser commands at fixture files under `tests/nfsconf`, and checks behavior for valid and invalid configuration files. The fixture pairing suggests assertions around parser dump/get/isset semantics and error handling.

State, dependencies, and integration: It depends on the built nfsconf tooling and `srcdir` fixture discovery. It does not manage daemon state.

Risks and test signals: The top-level `Makefile.am` does not list this script in `TESTS` in the inspected snapshot, so it may not run by default. Validation should add it to the test suite if intended, then assert valid include/expansion behavior and deliberate error diagnostics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tests/t0002-nfsconf.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tests/test-lib.sh -->
# sources/user-network-fs/nfs-utils/tests/test-lib.sh

Purpose: `test-lib.sh` is shared shell infrastructure for nfs-utils tests.

Important APIs and control flow: It resolves and validates `srcdir`, extends `PATH` with the test and `nsm_client` directories, and provides environment checks such as `check_root` and `check_dev_log`. It also supplies common setup/cleanup helpers used by statd tests.

State, dependencies, and integration: It exports PATH changes and interacts with root privileges, `/dev/log`, and temporary test directories. Test scripts source it before invoking helper binaries.

Risks and test signals: Hard environment requirements can make tests fragile in containers or unprivileged CI. Tests should verify skip/fail behavior is explicit, cleanup runs on failure, and build-tree versus source-tree paths work.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tests/test-lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/Makefile.am -->
# sources/user-network-fs/nfs-utils/tools/Makefile.am

Purpose: `tools/Makefile.am` defines the nfs-utils tools subdirectory traversal.

Important build APIs and control flow: It conditionally adds `rpcgen`, `nfsdclddb`, and `nfsrahead` to `OPTDIRS`, always adds `nfsconf`, and sets `SUBDIRS` to locktest, rpcdebug, nlmtest, mountstats, nfs-iostat, rpcctl, nfsdclnts, and optional directories.

State, dependencies, and integration: No runtime state; it coordinates build/install of command-line utilities and test tools.

Risks and test signals: Optional directory ordering matters when generated tools such as rpcgen are needed by later builds. Tests should run configure feature combinations and verify all expected tools are distributed, built, and installed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/locktest/Makefile.am -->
# sources/user-network-fs/nfs-utils/tools/locktest/Makefile.am

Purpose: `tools/locktest/Makefile.am` builds the simple `testlk` lock exerciser.

Important build APIs and control flow: It declares `noinst_PROGRAMS = testlk`, builds it from `testlk.c`, and marks `Makefile.in` as maintainer-clean.

State, dependencies, and integration: The program is not installed; it is available in the build tree for manual or test use around advisory locking/NLM behavior.

Risks and test signals: Because it is `noinst`, downstream packages may not ship it. Tests should confirm it builds on platforms with POSIX `fcntl` locks and is available to any lock-related test harness expecting it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/locktest/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/locktest/testlk.c -->
# sources/user-network-fs/nfs-utils/tools/locktest/testlk.c

Purpose: `testlk.c` is a small manual tool for setting or querying POSIX byte-range locks on a file.

Important APIs and control flow: `main` parses `-r`, `-w`, `-b`, and `-t` to select read lock, write lock, blocking write lock, or `F_GETLK`; opens the target file read/write; fills `struct flock`; calls `fcntl`; prints success or conflicting lock details; and pauses after setting a lock so the lock remains held.

State, dependencies, and integration: Runtime state is the open file descriptor and kernel lock held by the process. It depends on `fcntl` locking and getopt.

Risks and test signals: The usage string omits option descriptions, `atoi` silently accepts bad ranges, and the process pauses indefinitely after lock acquisition. Tests should cover read/write/blocking/query modes, conflict reporting, invalid files, and signal cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/locktest/testlk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/mountstats/Makefile.am -->
# sources/user-network-fs/nfs-utils/tools/mountstats/Makefile.am

Purpose: `tools/mountstats/Makefile.am` packages and installs the Python `mountstats` utility and its man page.

Important build APIs and control flow: It lists `mountstats.py` as `PYTHON_FILES`, includes `mountstats.man`, makes the Python file part of `EXTRA_DIST`, and installs it executable as `$(sbindir)/mountstats` in `install-data-hook`.

State, dependencies, and integration: No build-time compilation occurs; install behavior copies the script directly. Runtime integration is with `/proc/self/mountstats`.

Risks and test signals: Install hooks must preserve executable mode and shebang compatibility. Tests should run `make install DESTDIR=...`, verify path/mode/manpage, and execute the installed script with a fixture file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/mountstats/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/mountstats/mountstats.py -->
# sources/user-network-fs/nfs-utils/tools/mountstats/mountstats.py

Purpose: `mountstats.py` parses `/proc/self/mountstats` and displays NFS mount statistics in detailed, raw, nfsstat-like, transport, or iostat-like forms.

Important APIs and control flow: Counter name arrays define NFS events, byte counters, UDP/TCP/RDMA transport counters, and NFSv3/v4 operation names. `DeviceData` parses one mount's NFS and RPC sections, formats reports, computes diffs, accumulates per-version stats, and prints iostat summaries. Top-level commands `mountstats_command`, `nfsstat_command`, and `iostat_command` parse a stats file, filter NFS mountpoints, optionally diff against `--since`, and print selected views. `ICMAction` disambiguates iostat interval/count from mountpoint arguments.

State, dependencies, and integration: State lives in Python dictionaries per mount. The default input is `/proc/self/mountstats`; command-line subcommands use argparse and file handles.

Risks and test signals: Kernel mountstats formats vary; missing fields are padded in some paths but can still raise `KeyError`. `Nfsv4ops` contains duplicate `LAYOUTSTATS`. Integer interval parsing rejects iostat intervals when `--file`/`--since` is used. Tests should use fixture files for v3/v4, TCP/UDP/RDMA, nconnect accumulation, missing counters, diffs after remount, and each subcommand/default dispatch path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/mountstats/mountstats.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfs-iostat/Makefile.am -->
# sources/user-network-fs/nfs-utils/tools/nfs-iostat/Makefile.am

Purpose: `tools/nfs-iostat/Makefile.am` packages and installs the Python NFS iostat utility.

Important build APIs and control flow: It lists `nfs-iostat.py` as the Python source, `nfsiostat.man` as the man page, includes both in distribution, and installs the script executable as `$(sbindir)/nfsiostat`.

State, dependencies, and integration: There is no compilation state. Runtime behavior belongs to the installed Python script, which is expected to inspect NFS mount statistics.

Risks and test signals: The installed command name differs from the source directory and script name, so packaging checks must verify `nfsiostat` exists and is executable. Tests should install to DESTDIR, inspect file mode/man page, and run a fixture-based smoke test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfs-iostat/Makefile.am -->

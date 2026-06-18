# Research Group subset-b-009733

This grouped report covers the requested nfs-utils gssd, idmapd, and mount helper files. Each section is bounded by reconciliation markers and titled with the original source path.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/svcgssd.c -->
# sources/user-network-fs/nfs-utils/utils/gssd/svcgssd.c

Purpose: `svcgssd.c` is the main program for the server-side RPCSEC_GSS daemon. It initializes configuration, logging, GSS credentials, libevent, NFSv4 idmapping, and a procfs channel reader for `/proc/net/rpc/auth.rpcsec.init/channel`.

Important APIs and functions: `main()` parses `-f`, `-i`, `-v`, `-r`, `-n`, and `-p`, reads `svcgssd` settings from `NFS_CONFFILE`, calls `gssd_check_mechs()`, `gssd_acquire_cred()`, `nfs4_init_name_mapping()`, and dispatches libevent. `svcgssd_nullrpc_cb()` reads a kernel null-init request and passes it to `handle_nullreq()`. `svcgssd_nullrpc_open()`, `svcgssd_nullrpc_close()`, and `svcgssd_wait_cb()` manage delayed availability of the kernel proc channel. `sig_die()` and `sig_hup()` implement shutdown and ignored reload behavior.

Control flow: startup reads config, applies debug levels, daemonizes, acquires either machine credentials, a configured principal, or nameless credentials, then opens or waits for the nullrpc channel. Once libevent is running, readable channel data is converted from newline-terminated kernel text into a mutable string for `svcgssd_proc.c`.

State and persistence: process-global state tracks signal receipt, event base, channel fd, and event handles. Persistent external state is in kernel procfs RPCSEC_GSS caches plus Kerberos credentials acquired by gssd helpers. Shutdown frees events, name mapping, enctype caches, and GSS state.

Dependencies and integration: integrates with libevent, libtirpc/authgss debug APIs, libnfsidmap, nfs-utils config/logging helpers, GSSAPI, and kernel `/proc/net/rpc/auth.rpcsec.init/channel`.

Risks: procfs channel failures leave the daemon waiting; double signal forces exit; credential acquisition failures are fatal. Test signals include option parsing, config precedence, missing channel wait/reopen, signal-triggered event-loop exit, foreground/background daemon readiness, and credential acquisition paths for `-n`, `-p`, and default hostbased `nfs`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/svcgssd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/svcgssd.h -->
# sources/user-network-fs/nfs-utils/utils/gssd/svcgssd.h

Purpose: this header defines the minimal shared server gssd interface.

Important APIs and types: it includes GSSAPI and queue/type headers, declares `void handle_nullreq(char *cp);`, and defines `GSSD_SERVICE_NAME` as `"nfs"`. The function is implemented in `svcgssd_proc.c` and invoked by the event callback in `svcgssd.c`.

Control flow and integration: the header couples the daemon entrypoint to the null RPC processor without exposing internal credential or downcall structures. `GSSD_SERVICE_NAME` is used when `svcgssd` acquires default hostbased service credentials.

State and persistence: no state is owned here; it exposes a contract around mutable text input from the kernel init channel.

Dependencies: GSSAPI is included because the surrounding server gssd code shares GSS type vocabulary, though this header itself exports only a char-pointer request handler and a service-name macro.

Risks: the interface does not describe buffer ownership or syntax, so callers must already know the qword-encoded kernel channel format. Test signals are compile coverage for both `svcgssd.c` and `svcgssd_proc.c`, plus malformed null request tests that verify the handler tolerates bad input.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/svcgssd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/svcgssd_krb5.c -->
# sources/user-network-fs/nfs-utils/utils/gssd/svcgssd_krb5.c

Purpose: this file restricts Kerberos encryption types used by server gssd to those supported by the kernel, falling back to version-based defaults when the kernel does not expose a list.

Important APIs and functions: `svcgssd_limit_krb5_enctypes()` is called before accepting a security context. `svcgssd_free_enctypes()` releases global parsed/cached enctype arrays. Internal helpers `parse_enctypes()` and `get_kernel_supported_enctypes()` parse `/proc/fs/nfsd/supported_krb5_enctypes`.

Control flow: when `HAVE_SET_ALLOWABLE_ENCTYPES` is available, the code chooses default old or new kernel enctype lists based on `linux_version_code()`, reads the procfs enctype list, and calls `gss_set_allowable_enctypes(&min_stat, gssd_creds, &krb5oid, ...)`. If the kernel list is unchanged, parsing is skipped via `cached_enctypes`.

State and persistence: global `parsed_num_enctypes`, `parsed_enctypes`, and `cached_enctypes` cache the last kernel string. External state is read-only procfs capability data and the global GSS credential handle.

Dependencies and integration: depends on MIT/Heimdal Kerberos enctype constants, GSSAPI Kerberos OID definitions, nfs-utils `gss_util`, logging, and version helpers. It is integrated from `handle_nullreq()`.

Risks: parsing is permissive and uses `atoi`, so malformed comma content can become zero entries after the first digit. A failed proc read silently falls back to defaults. Test signals include kernel list parsing, cache reuse, fallback lists for old/new kernel version codes, and failure propagation from `gss_set_allowable_enctypes()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/svcgssd_krb5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/svcgssd_krb5.h -->
# sources/user-network-fs/nfs-utils/utils/gssd/svcgssd_krb5.h

Purpose: this header exposes the server gssd Kerberos enctype limiter lifecycle.

Important APIs: `int svcgssd_limit_krb5_enctypes(void);` applies kernel/default enctype restrictions to the current acquired GSS credential, and `void svcgssd_free_enctypes(void);` clears cached parsed enctype data.

Control flow and integration: `svcgssd_proc.c` calls the limiter before `gss_accept_sec_context()`, while `svcgssd.c` calls the free routine during process shutdown. The header intentionally hides the procfs file name and caching details.

State and persistence: no state is declared here; the implementation owns process-global caches and reads kernel procfs capability state.

Dependencies: consumers include this after GSS credential setup code, but the header itself has no includes beyond its guard.

Risks and tests: callers must treat nonzero return from `svcgssd_limit_krb5_enctypes()` as fatal for the current upcall. Compile tests should cover configurations with and without `HAVE_SET_ALLOWABLE_ENCTYPES`; behavior tests should ensure shutdown can call `svcgssd_free_enctypes()` safely even if no parse succeeded.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/svcgssd_krb5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/svcgssd_mech2file.c -->
# sources/user-network-fs/nfs-utils/utils/gssd/svcgssd_mech2file.c

Purpose: maps a GSS mechanism OID to the short kernel/cache mechanism name used by server gssd.

Important APIs and data: `char *mech2file(gss_OID mech)` scans the static `m2f` table. The only configured mapping is the Kerberos V5 OID to `"krb5"`. `g_OID_equal` compares length and bytes.

Control flow: `do_svc_downcall()` and `get_ids()` call this to convert the accepted mechanism into the name used in procfs downcalls and nfsidmap calls. Unknown mechanisms return `NULL`, causing request failure paths in callers.

State and persistence: no mutable state. The returned pointer refers to static storage in `m2f`.

Dependencies and integration: depends on GSSAPI OID layout and the kernel/server idmapping convention that Kerberos is addressed as `krb5`.

Risks: adding a new mechanism requires updating this static table and ensuring all downstream idmapping/downcall formats support it. The exported prototype is local rather than in a header, so mismatches can compile unnoticed on permissive compilers. Test signals include known krb5 OID mapping, unknown OID rejection, and null/empty OID robustness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/svcgssd_mech2file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/svcgssd_proc.c -->
# sources/user-network-fs/nfs-utils/utils/gssd/svcgssd_proc.c

Purpose: this file handles server-side RPCSEC_GSS init upcalls from the kernel, accepts GSS security contexts, maps client principals to local credentials, serializes completed contexts, and writes init/context responses back to kernel procfs channels.

Important APIs and types: `handle_nullreq()` is the external entrypoint. `do_svc_downcall()` writes context cache data to `/proc/net/rpc/auth.rpcsec.context/channel`. `send_response()` writes accept status and output token data to `/proc/net/rpc/auth.rpcsec.init/channel`. `get_ids()` converts a GSS name to uid/gid via `nfs4_gss_princ_to_ids()`, and `add_supplementary_groups()` fills auxiliary groups. `struct svc_cred` stores uid, gid, and up to `NGROUPS`.

Control flow: the handler qword-decodes input handle/token. A non-empty handle restores an in-progress `gss_ctx_id_t`; otherwise a fresh accept starts. It applies Kerberos enctype limits, calls `gss_accept_sec_context()`, returns continuation state when needed, or on completion maps identity, gets hostbased client name, creates a short kernel handle, serializes context material, downcalls the credential/context tuple, and sends the null reply. Error paths delete partial contexts and send failure status with null buffers.

State and persistence: static `handle_seq` issues process-local context handles. Kernel context/init caches persist accepted contexts and short-lived init replies. Dynamic GSS buffers, context tokens, names, and hostbased names are freed per request.

Dependencies and integration: integrates GSSAPI, kernel procfs RPC cache channels, `context.h` serialization, nfsidmap principal mapping, qword encoders, Kerberos enctype limiter, and mechanism-to-file mapping.

Risks: handle reuse after daemon restart is acknowledged; fixed-size token/handle buffers bound request sizes; failed downcalls are logged but do not prevent response send. Test signals include continuation and completion handshakes, malformed qword fields, unmapped principals mapping to anonymous uid/gid, group list truncation, enctype limiter failure, context serialization failure, and procfs write failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/svcgssd_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/write_bytes.h -->
# sources/user-network-fs/nfs-utils/utils/gssd/write_bytes.h

Purpose: provides inline serialization/deserialization helpers for bounded byte buffers and simple XDR-like 32-bit-aligned GSS buffers.

Important APIs: `write_bytes()`, `WRITE_BYTES`, `write_buffer()`, and `write_oid()` append native-endian length-prefixed values to a caller-managed buffer. `get_bytes()` and `get_buffer()` parse native-endian fields and allocate GSS buffers. `xdr_get_u32()`, `xdr_get_buffer()`, `xdr_write_u32()`, and `xdr_write_buffer()` handle network-byte-order 32-bit fields and padded XDR buffers.

Control flow: every helper advances the caller's pointer only after bounds checks pass. Reads and writes validate `end` boundaries and pointer wraparound. Buffer getters allocate exact payload length and copy payload into newly owned memory.

State and persistence: no global state; persistence is in caller-provided serialized buffers and allocated result buffers that callers must release.

Dependencies and integration: used by GSS context/channel serialization code; depends on GSSAPI buffer/OID layouts, `malloc`, `memcpy`, and byte-order conversion.

Risks: native-endian helpers are not portable wire formats; zero-length buffers currently attempt `malloc(0)` and can be treated as failure depending on libc behavior. `xdr_write_buffer()` writes padded bytes from `arg->value`, so callers must ensure padding bytes are readable. Test signals include boundary overflow checks, malformed lengths, zero-length buffers, XDR padding behavior, and pointer advancement after failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/write_bytes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/idmapd/Makefile.am -->
# sources/user-network-fs/nfs-utils/utils/idmapd/Makefile.am

Purpose: automake definition for building and installing the `idmapd` daemon and its manual page links.

Important build APIs: `sbin_PROGRAMS = idmapd`; sources are `idmapd.c`, `nfs_idmap.h`, and `queue.h`. `AM_CPPFLAGS` includes the support nfsidmap headers. `idmapd_LDADD` links libnfs, libnfsidmap, and libevent.

Control flow: install hooks rename the built binary with `$(RPCPREFIX)$(KPREFIX)` and create prefixed man-page symlinks; uninstall hooks remove those renamed artifacts. The comments document why `program_transform_name` is not used.

State and persistence: affects installed filesystem layout under `$(sbindir)` and `$(man8dir)` rather than runtime state.

Dependencies and integration: ties the daemon to nfs-utils support libraries and libevent. Prefix variables allow distributions to install as `rpc.idmapd` or kernel-prefixed variants.

Risks: custom install hooks can diverge from automake expectations and must match packaging scripts. Test signals include `make install DESTDIR=...`, prefixed binary rename, man symlink creation/removal, and builds with different `RPCPREFIX`/`KPREFIX` values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/idmapd/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/idmapd/idmapd.c -->
# sources/user-network-fs/nfs-utils/utils/idmapd/idmapd.c

Purpose: `idmapd.c` implements the NFSv4 ID mapping daemon for client rpc_pipefs upcalls and server nfsd procfs cache upcalls, converting between numeric ids and NFSv4 owner/group names.

Important APIs and types: `struct idmap_client` tracks each client channel fd, directory fd, path, libevent handle, and TAILQ membership. `main()` parses config/CLI, initializes nfsidmap, opens nfsd channels, watches rpc_pipefs with inotify, and runs libevent. `nfscb()` handles binary `struct idmap_msg` client messages. `nfsdcb()` handles text server cache upcalls. `idtonameres()` and `nametoidres()` call libnfsidmap conversion APIs. `addfield()`/`getfield()` escape/unescape procfs fields.

Control flow: startup loads `/etc/nfs.conf` and idmapd config, sets nobody user/group, daemonizes, initializes name mapping, then optionally opens server channels and/or scans client pipefs. Inotify/SIGUSR events rescan `clnt*` directories and add or remove client idmap channel events. Server callbacks parse auth/type/name-or-id, convert, and write cache records with expiry.

State and persistence: process globals store verbosity, cache expiry, pipefs path, nobody ids, event base, and inotify fd. Persistent external state lives in kernel nfsd cache channels, client rpc_pipefs idmap pipes, `/proc/sys/fs/nfs/idmap_cache_timeout`, and libnfsidmap configuration.

Dependencies and integration: libevent, inotify, nfsidmap, nfs-utils config/logging, passwd/group databases, `/proc/net/rpc/nfs4.*` caches, and rpc_pipefs.

Risks: malformed server upcalls can be dropped; `imconv()` has a fragile null-termination check; long or escaped fields depend on fixed `IDMAP_MAXMSGSZ`. Test signals include client-only/server-only modes, cache flush and timeout writes, inotify rescan, disappeared clients, user/group conversion success/failure, nobody fallback, and unprivileged config errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/idmapd/idmapd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/idmapd/nfs_idmap.h -->
# sources/user-network-fs/nfs-utils/utils/idmapd/nfs_idmap.h

Purpose: defines the fixed kernel/userspace binary message format for client-side idmapping.

Important APIs and types: `struct idmap_msg` contains `im_type`, `im_conv`, `im_name[IDMAP_NAMESZ]`, `im_id`, and `im_status`. Constants define user/group types, id-to-name/name-to-id conversions, status bits, name size, and max message size.

Control flow and integration: `idmapd.c` reads and writes exactly this struct on client rpc_pipefs `idmap` files in `nfscb()`. The same constants drive conversion dispatch and result status handling.

State and persistence: no state; it is an ABI-style header mirrored from Linux NFS idmap expectations.

Dependencies: uses fixed-width integer typedefs expected from system headers included by the consumer.

Risks: field size/order is a compatibility contract with the kernel; changes would break binary pipefs communication. `IDMAP_NAMESZ` constrains owner/group string lengths. Test signals include struct size compatibility, round-trip binary reads/writes, lookup failure status handling, and bounds around 127-character names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/idmapd/nfs_idmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/idmapd/queue.h -->
# sources/user-network-fs/nfs-utils/utils/idmapd/queue.h

Purpose: local copy of BSD queue macros used by idmapd for intrusive lists, especially `TAILQ` client tracking.

Important APIs and types: the header defines `SLIST`, `LIST`, `SIMPLEQ`, `TAILQ`, and `CIRCLEQ` head/entry/access/manipulation macros. `idmapd.c` uses `TAILQ_HEAD`, `TAILQ_ENTRY`, `TAILQ_INIT`, `TAILQ_FOREACH`, `TAILQ_INSERT_TAIL`, `TAILQ_REMOVE`, `TAILQ_FIRST`, and `TAILQ_NEXT`.

Control flow: macros perform pointer manipulation inline in callers. Tail queues provide O(1) insertion/removal and forward traversal for active idmap clients.

State and persistence: no standalone state; list membership is embedded in consumer structs. Persistence is in process memory only.

Dependencies and integration: avoids dependency on platform `<sys/queue.h>` semantics by shipping an older BSD-compatible implementation.

Risks: macros are type-unsafe and evaluate arguments in pointer-heavy contexts; misuse can corrupt list links. The circular queue `CIRCLEQ_REPLACE` macros reference `head` inconsistently with pointer-style usage, but idmapd does not use them. Test signals are compile coverage and dynamic add/remove/rescan client behavior that exercises the TAILQ subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/idmapd/queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/Makefile.am -->
# sources/user-network-fs/nfs-utils/utils/mount/Makefile.am

Purpose: automake recipe for the NFS mount/umount helper and associated man pages/config files.

Important build APIs: `sbin_PROGRAMS = mount.nfs`; `mount_common` collects shared mount sources, option parsers, protocol code, headers, and utilities. `MOUNT_CONFIG` adds `configfile.c` and the `nfsmount.conf` man page. `CONFIG_LIBMOUNT` switches between `mount_libmount.c` and legacy `mount.c`, `fstab.c`, and `nfsumount.c`.

Control flow: install hook creates symlinks `mount.nfs4`, `umount.nfs`, and `umount.nfs4`, and sets setuid permissions on `mount.nfs`. Uninstall removes symlinks. Man hooks remove generated link names.

State and persistence: affects installed helper names, permissions, and manual/config distribution files.

Dependencies and integration: links nfs-utils support libraries, export/reexport/misc libraries, libtirpc, pthread, and optionally libmount.

Risks: setuid install behavior is security-sensitive and packaging may override it. Build variants produce materially different mtab/utab code paths. Test signals include both `CONFIG_LIBMOUNT` paths, `MOUNT_CONFIG` on/off, install symlink layout, and helper invocation through all four names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/configfile.c -->
# sources/user-network-fs/nfs-utils/utils/mount/configfile.c

Purpose: converts `/etc/nfsmount.conf` entries into effective mount options layered with CLI/fstab options.

Important APIs and data: `conf_get_mntopts(spec, mount_point, mount_opts)` is exported via `mount_config.h`. `conf_parse_mntopts()` adds options from `MountPoint`, `Server`, and global sections. `mountopts_alias()` maps human option names like `background` to `bg`; `mountopts_convert()` expands `k`, `m`, and `g` size suffixes. `default_value()` populates global default version/protocol settings used by network probing.

Control flow: existing options are parsed first and take precedence. The code then applies mountpoint-specific, server-specific, and global options, skipping duplicates, inverses, conflicting `fg`/`bg`, and extra version keys. Boolean false is transformed to `no<opt>` or inverted aliases.

State and persistence: global `config_default_vers`, `config_default_proto`, external `config_default_family`, and file-scope `strict` are mutated during parse. Persistent input is the configured mount options file.

Dependencies and integration: uses nfs-utils conffile, option-list helpers, network protocol/version parsers, and xlog.

Risks: size conversion uses a static buffer and `strtol` into unsigned arithmetic; default option parsing depends on string prefixes. Test signals include precedence order, false/true handling, case-insensitive aliases, version de-duplication, defaultproto/defaultvers side effects, and suffix conversion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/configfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/error.c -->
# sources/user-network-fs/nfs-utils/utils/mount/error.c

Purpose: centralizes NFS mount/umount error presentation and maps NFS protocol status values to local errno text.

Important APIs: `rpc_mount_errors()`, `sys_mount_errors()`, `mount_error()`, `umount_error()`, and `nfs_strerror()`. Internal `rpc_strerror()` formats `rpc_createerr`.

Control flow: foreground errors go to stderr through `nfs_error`/`fprintf`; background mount errors go to syslog. `mount_error()` switches on errno and provides more specific messages for access denied, bad options, unsupported protocol, busy mountpoints, RPC mount failures, and RDMA routing hints. `nfs_strerror()` scans `nfs_errtbl` for NFSv2/v3 status mappings.

State and persistence: a static `errbuf` is reused for formatted messages; syslog is opened once per background path. No durable state is written.

Dependencies and integration: depends on libtirpc `rpc_createerr`, nls gettext wrappers, mount option parser tables, and NFS protocol status constants.

Risks: static buffer is not thread-safe, though helpers are single-process/single-thread. Some foreground `sys_mount_errors()` non-timeout paths intentionally do not append detailed text. Test signals include each errno branch, RPC timeout retry/give-up variants, background syslog path, unknown NFS status, and RDMA-specific `EPROTO`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/error.h -->
# sources/user-network-fs/nfs-utils/utils/mount/error.h

Purpose: declares common error-reporting functions for mount and umount helpers.

Important APIs: exports `nfs_strerror()`, `mount_error()`, `rpc_mount_errors()`, `sys_mount_errors()`, and `umount_error()`. It includes `parse_opt.h` because `mount_error()` accepts `struct mount_options *` for option-sensitive diagnostics.

Control flow and integration: consumed by `mount.c`, `mount_libmount.c`, `nfsmount.c`, `nfs4mount.c`, `nfsumount.c`, and network helper code to keep user-visible diagnostics consistent.

State and persistence: no state; all behavior lives in `error.c`.

Dependencies: callers must provide global `progname` as required by the implementation.

Risks and tests: signature changes affect many mount paths. Test signals are compile coverage across libmount and legacy builds, plus branch tests in `error.c` that verify callers pass the expected source, target, errno, and options values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/error.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/fstab.c -->
# sources/user-network-fs/nfs-utils/utils/mount/fstab.c

Purpose: legacy mount-table and fstab support for builds without libmount, including reading `/etc/mtab`, `/proc/mounts`, `/etc/fstab`, and updating `/etc/mtab` safely.

Important APIs: `mtab_is_a_symlink()`, `mtab_is_writable()`, `mtab_does_not_exist()`, `reset_mtab_info()`, `getmntdirbackward()`, `getprocmntdirbackward()`, `getmntdevbackward()`, `getfsfile()`, `getfsspec()`, `lock_mtab()`, `unlock_mtab()`, and `update_mtab()`.

Control flow: file contents are lazily read into circular doubly-linked `struct mntentchn` chains. Lookups scan backward for most recent mount entries or forward through fstab. `lock_mtab()` creates a pid-specific link target and uses hard-link creation plus `fcntl` locks and signal handlers to serialize writers. `update_mtab()` rereads mtab under lock, removes or updates an entry, writes a temp file, fixes mode/ownership, and renames.

State and persistence: cached flags describe mtab existence/symlink status; global linked lists cache mtab/proc/fstab entries. Persistent output is `/etc/mtab` and its lock/temp files, unless mtab is absent, unwritable, or symlinked.

Dependencies and integration: uses nfs mount-entry wrappers, nfs path constants, xcommon allocation/error helpers, and legacy mount/umount flows.

Risks: signal handling in setuid helpers is delicate; stale lock files and mtab symlinks need careful handling. Test signals include concurrent updates, remount entry replacement, umount deletion of last matching entry, missing `/etc/mtab` fallback to `/proc/mounts`, and fstab lookups.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/fstab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/fstab.h -->
# sources/user-network-fs/nfs-utils/utils/mount/fstab.h

Purpose: exposes legacy mtab/fstab lookup and update interfaces.

Important APIs and types: defines `_PATH_FSTAB` fallback, `struct mntentchn` linked-list node, mtab state queries, backward mount/proc lookups, fstab file/spec lookups, and mtab lock/update routines.

Control flow and integration: legacy `mount.c` uses fstab checks for non-root mounts and mtab updates after mount. `nfsumount.c` uses mount/proc lookups and deletion/remount updates. The header is excluded from libmount builds.

State and persistence: declares access to implementation-owned in-memory mount lists and persistent `/etc/mtab` mutation routines.

Dependencies: includes `nfs_mntent.h` for mount-entry file wrappers and `struct mntent`.

Risks and tests: consumers must not free returned list nodes. Because `update_mtab()` can mutate system files, tests should use isolated mount table paths or mocks. Compile tests should cover non-libmount builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/fstab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/mount.c -->
# sources/user-network-fs/nfs-utils/utils/mount/mount.c

Purpose: legacy frontend for `mount.nfs`, `mount.nfs4`, `umount.nfs`, and `umount.nfs4` when libmount is not used.

Important APIs and data: global `progname`, `nfs_mount_data_version`, `nomtab`, `verbose`, `sloppy`, and `string`. `opt_map` translates generic mount options to `MS_*` flags. `main()` dispatches to `nfsumount()` for umount names or mounts via `try_mount()`. `parse_opts()`, `parse_opt()`, `fix_opts_string()`, `init_mntent()`, `add_mtab()`, and `create_mtab()` handle option and mtab mechanics.

Control flow: CLI options are collected, non-root requests are validated against fstab and setuid status, mountpoint is canonicalized, config-file options are layered, generic flags are split from NFS-specific options, and `nfsmount_string()`, `nfs4mount()`, or `nfsmount()` performs the actual mount. Background mounts fork and retry in the child after returning success to the parent.

State and persistence: updates `/etc/mtab` through `fstab.c` unless fake/no-mtab. Adds user/users metadata for unprivileged mounts.

Dependencies and integration: uses legacy fstab/mtab code, configfile glue, NFSv2/v3, NFSv4, string mount, error handling, and utility helpers.

Risks: setuid path and user mount validation are security-sensitive. Option parsing must preserve quoted commas. Test signals include user/fstab enforcement, `-o` concatenation, `mount.nfs4` type selection, fake/no-mtab behavior, background `EX_BG`, and mtab creation/update.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/mount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/mount_config.h -->
# sources/user-network-fs/nfs-utils/utils/mount/mount_config.h

Purpose: compile-time abstraction for optional mount configuration file support.

Important APIs: when `MOUNT_CONFIG` is defined, `mount_config_init(program)` opens xlog and reads `MOUNTOPTS_CONFFILE` (default `/etc/nfsmount.conf`), while `mount_config_opts(spec, mount_point, mount_opts)` calls `conf_get_mntopts()`. Without `MOUNT_CONFIG`, both are no-op/pass-through inline functions.

Control flow and integration: `mount.c` and `mount_libmount.c` call these unconditionally, allowing the same frontend code to build with or without config-file support.

State and persistence: the enabled path reads global config into conffile state and may indirectly update global default protocol/version state in `configfile.c`.

Dependencies: enabled path depends on `conffile.h` and `xlog.h`; disabled path has no runtime dependencies.

Risks and tests: behavior changes substantially with the compile flag. Test signals include config-enabled and config-disabled builds, default file path override, and preserving caller option strings when disabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/mount_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/mount_constants.h -->
# sources/user-network-fs/nfs-utils/utils/mount/mount_constants.h

Purpose: supplies mount flag definitions not guaranteed by older system headers and defines NFS helper-specific pseudo flags.

Important APIs/data: fallback definitions include `MS_DIRSYNC`, `MS_ACTION_MASK`, `MS_NOATIME`, `MS_NODIRATIME`, `MS_BIND`, `MS_MOVE`, `MS_REC`, `MS_VERBOSE`, `MS_RELATIME`, and `MS_MGC_VAL/MS_MGC_MSK`. It defines `MS_DUMMY`, `MS_USERS`, `MS_USER`, and `MS_NOMTAB`.

Control flow and integration: `mount.c` option parsing sets these flags, and mount/umount code masks helper-only `MS_USER/MS_USERS` before calling `mount(2)`.

State and persistence: no state; constants affect generated mtab options and syscall flags.

Dependencies: included by legacy mount, umount, and NFS protocol code to normalize build environments.

Risks and tests: incorrect flag values can cause wrong kernel behavior or mtab output. Test signals include builds on older headers, generic option parsing, masking pseudo flags before syscall, and remount/no-mtab option handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/mount_constants.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/mount_libmount.c -->
# sources/user-network-fs/nfs-utils/utils/mount/mount_libmount.c

Purpose: libmount-based frontend for NFS mount and umount helpers, replacing local mtab/fstab handling with libmount context management.

Important APIs: `main()` creates a `libmnt_context` and dispatches by program name. `mount_main()` parses helper options via `mnt_context_helper_setopt()`, applies fstab and nfsmount.conf options, prepares the mount, runs `try_mount()`, and finalizes. `umount_main()` prepares unmount, retrieves stored NFS options, optionally sends MNT `UMNT`, performs `umount(2)`, and finalizes. `store_mount_options()` and `retrieve_mount_options()` bridge fs-specific NFS options through mtab or `/dev/.mount/utab`.

Control flow: libmount owns canonicalization, permission checks, option separation, and table updates. Actual NFS work still delegates to `nfsmount_string()`, `nfs4mount()`, or `nfsmount()`. Background mounts daemonize and re-enter `try_mount()`.

State and persistence: globals mirror legacy frontend flags for shared lower layers. Persistent state is maintained by libmount in mtab/utab, with fs attributes used on non-mtab systems.

Dependencies and integration: libmount, mount config glue, NFS protocol mount implementations, string options, error utilities.

Risks: option storage/retrieval must preserve fs-specific NFS options or unmount advisory calls lose server data. Test signals include mount and umount helper modes, restricted user mounts through libmount, utab attribute storage, NFSv4 detection, lazy unmount skip, and background behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/mount_libmount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/network.c -->
# sources/user-network-fs/nfs-utils/utils/mount/network.c

Purpose: common network, rpcbind, protocol/version parsing, callback address, statd, and advisory unmount helpers for NFS mount/umount.

Important APIs: address conversion `nfs_lookup()`, `nfs_gethostbyname()`, `nfs_string_to_sockaddr()`, `nfs_present_sockaddr()`, and `nfs_callback_address()`. Probing functions `probe_bothports()` and `nfs_probe_bothports()` fill NFS and mountd `pmap` tuples. Option parsers include `nfs_nfs_version()`, `nfs_nfs_protocol()`, `nfs_nfs_proto_family()`, `nfs_mount_proto_family()`, and `nfs_options2pmap()`. RPC helpers include `mnt_openclnt()`, `mnt_closeclnt()`, `clnt_ping()`, `nfs_advise_umount()`, `nfs_call_umount()`, `nfs_umount_do_umnt()`, and `start_statd()`.

Control flow: mount code resolves hosts, parses requested versions/transports/ports, probes rpcbind and NULL RPC calls in ordered protocol/version lists, then supplies discovered endpoints to mount RPCs. Unmount code reconstructs endpoint data from stored options, skips UMNT for NFSv4, resolves mountd, and sends advisory UMNT.

State and persistence: global default family/protocol can be influenced by config. External state includes DNS, local interfaces, rpcbind, remote NFS/mountd services, rpc.statd, and stored mount options.

Dependencies and integration: libtirpc, rpcbind/nfsrpc helpers, parse_opt, conffile, nfslib, network interfaces, and Linux IPv6 preferences.

Risks: network probing has many fallback/error paths; NFSv4-vs-v3 detection uses EAGAIN signaling; address-family defaults depend on build-time IPv6 support. Test signals include IPv4/IPv6 lookup, proto/version parse errors, fixed and discovered pmap combinations, timeout handling, statd start, local address matching, and NFSv4 UMNT skip.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/network.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/network.h -->
# sources/user-network-fs/nfs-utils/utils/mount/network.h

Purpose: declares shared network/protocol interfaces for NFS mount and unmount code.

Important APIs and types: `clnt_addr_t` pairs hostname pointer, IPv4 sockaddr, and RPC `pmap`. Constants define mount RPC send/receive buffer sizes and common timeouts. It declares probing, lookup, presentation, callback address, ping, local address checks, option-to-version/protocol parsing, statd startup, mountd client lifecycle, UMNT calls, and `nfs_umount_do_umnt()`.

Control flow and integration: `nfsmount.c`, `nfs4mount.c`, `nfsumount.c`, `mount_libmount.c`, `error.c`, and `configfile.c` use this contract. The header exposes both legacy IPv4 `clnt_addr_t` and sockaddr-generic APIs.

State and persistence: declares `extern const char *nfs_transport_opttbl[]`; no mutable state is owned in the header.

Dependencies: includes `rpc/pmap_prot.h`; some declarations depend on `dirpath` and `CLIENT` types supplied by RPC/NFS includes in consumers.

Risks and tests: APIs mix legacy and newer address handling, so callers must use matching sockaddr lengths. Test signals are compile coverage across all mount code and behavior tests for option parsing/probing through the exported functions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/network.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/nfs4_mount.h -->
# sources/user-network-fs/nfs-utils/utils/mount/nfs4_mount.h

Purpose: defines the legacy userspace-to-kernel data structure for NFSv4 mounts and declares `nfs4mount()`.

Important APIs and types: `struct nfs_string` is a length/data pair. `struct nfs4_mount_data` contains versioned fields for flags, transfer/cache parameters, client address, mount path, hostname, server sockaddr, transport protocol, and auth flavor array. Flag constants include soft, intr, nocto, noac, strictlock, unshared, and mask.

Control flow and integration: `nfs4mount.c` fills this structure and passes it to `mount(2)` for filesystem type `nfs4` in legacy binary mount-data mode.

State and persistence: no state here; field order is a kernel ABI compatibility contract.

Dependencies: uses `struct sockaddr` and is included alongside networking headers.

Risks and tests: comments warn not to reorder fields; changing layout breaks kernel compatibility. Test signals include compile-time structure availability, version value, flag translation from options, and mount syscall data population.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/nfs4_mount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/nfs4mount.c -->
# sources/user-network-fs/nfs-utils/utils/mount/nfs4mount.c

Purpose: performs legacy binary-data NFSv4 mounts.

Important APIs: `nfs4mount(spec, node, flags, extra_opts, fake, running_bg)` parses `host:dir`, resolves IPv4 server/client addresses, parses NFSv4-specific options, pings server NFS program v4, fills `struct nfs4_mount_data`, and calls `mount(2)`. Helpers include `parse_sec()`, `parse_devname()`, `fill_ipv4_sockaddr()`, and `get_my_ipv4addr()`.

Control flow: mount options populate rsize/wsize/timeouts/cache flags/proto/port/clientaddr/security flavors. If `bg` is requested and the foreground attempt should background, the function returns `EX_BG`. Otherwise it retries until timeout, accepting only supported RPC responses. Successful probe can update clientaddr based on the chosen local route.

State and persistence: uses static buffers and mount data for one process. It appends `addr=<server-ip>` to options for mtab/umount use unless already running in background.

Dependencies and integration: uses `network.c` `clnt_ping`, pseudoflavor map, error helpers, kernel NFSv4 mount ABI, and global `progname`, `verbose`, `sloppy`.

Risks: IPv4-only parsing in this legacy path; `strtok` mutates option strings; support daemon lock checks are disabled. Test signals include sec flavor parsing, unsupported options with/without sloppy, retry/background behavior, clientaddr override, fake mount, and mount syscall failure reporting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/nfs4mount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/nfs_mount.h -->
# sources/user-network-fs/nfs-utils/utils/mount/nfs_mount.h

Purpose: defines legacy NFSv2/v3 userspace-to-kernel mount data structures and mount frontend prototypes.

Important APIs and types: constants include `NFS_MOUNT_VERSION` and `NFS_MAX_CONTEXT_LEN`. File handle structs `nfs2_fh` and `nfs3_fh` are used within the mount data ABI. The header declares `nfsmount()` and `nfsumount()`.

Control flow and integration: `nfsmount.c` fills the ABI structure based on MOUNT protocol results and option parsing; `mount.c` and `mount_libmount.c` call `nfsmount()` for legacy NFS mounts and dispatch to `nfsumount()` in non-libmount umount mode.

State and persistence: no state; structure layout/defines are compatibility contracts with older kernel mount interfaces.

Dependencies: includes IPv4 networking headers because mount data contains addresses.

Risks and tests: ABI changes are risky across kernel versions. Test signals include builds against old headers, selecting correct mount data version through `discover_nfs_mount_data_version()`, and NFSv2/v3 file handle copy behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/nfs_mount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/nfsmount.c -->
# sources/user-network-fs/nfs-utils/utils/mount/nfsmount.c

Purpose: performs legacy binary-data NFSv2/v3 mounts using the MOUNT RPC protocol to retrieve file handles before calling `mount(2)`.

Important APIs: `nfsmount()` is the exported mount path. `parse_options()` handles rsize/wsize/timeouts/cache flags, mountd/NFS program/version/port/proto options, security flavor, SELinux context, and locking/cache flags. `nfs_call_mount()` probes both NFS and mountd, opens a mountd client, and calls `MOUNTPROC_MNT` or `MOUNTPROC3_MNT`. Inline `nfs2_mount()`/`nfs3_mount()` wrap RPC calls.

Control flow: `nfsmount()` parses `host:dir`, resolves host, initializes defaults and pmap requests, checks compatibility, loops through retry/background behavior, calls MOUNT, validates returned status and security flavor support, copies file handles into kernel mount data, starts statd if remote locking is required, appends `addr=`, then calls `mount(2)` unless fake.

State and persistence: static `struct nfs_mount_data` and buffers are reused per process; mtab options are returned via `extra_opts`. Remote state includes MOUNT rmtab registration, undone via UMNT on security flavor mismatch.

Dependencies and integration: libtirpc, network probing/statd helpers, error mapping, Linux version detection, global frontend flags.

Risks: legacy path is IPv4-oriented and mutates option strings; MOUNT retry loops can take minutes; security flavor negotiation must match server-provided flavor list. Test signals include mount v2/v3 success, RPC status mapping, bg retry/exponential wait for missing mountpoint, bad option/sloppy behavior, nolock/statd behavior, and mount syscall failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/nfsmount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/nfsmount.conf -->
# sources/user-network-fs/nfs-utils/utils/mount/nfsmount.conf

Purpose: sample/default NFS mount configuration file consumed by `configfile.c` when mount config support is enabled.

Important content: documents section forms `[MountPoint "..."]`, `[Server "..."]`, and `[NFSMount_Global_Options]`. It lists commented options for default and mandatory protocol version, network protocol, retries, cache attribute times, ACLs, background/foreground behavior, hard/soft, locking, READDIRPLUS, read/write sizes, sloppy parsing, sharecache, timeo, mountd host/port/protocol/version, server port, RPCGSS security flavors, interrupt behavior, lookupcache, and noatime.

Control flow and integration: no executable code; options here map through aliases and parsing in `configfile.c`, then through protocol/version parsers in `network.c` and option parsers in `nfsmount.c`/`nfs4mount.c` or string mount paths.

State and persistence: if installed as `/etc/nfsmount.conf`, uncommented settings persistently alter mount defaults system-wide.

Dependencies: syntax depends on nfs-utils conffile section/tag handling.

Risks and tests: examples must stay aligned with parser-supported names and case behavior. Test signals include installing a config with each documented option, verifying mount option output, and ensuring commented defaults do not alter behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/nfsmount.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/nfsumount.c -->
# sources/user-network-fs/nfs-utils/utils/mount/nfsumount.c

Purpose: legacy umount helper for NFS filesystems when libmount is not used.

Important APIs and data: `nfsumount(argc, argv)` parses `-f`, `-v`, `-n`, `-r`, `-l`, and `-h`. Internal `del_mtab()` performs `umount`, `umount2(MNT_FORCE)`, or `umount2(MNT_DETACH)` and updates mtab. `try_remount()` remounts busy filesystems read-only for `-r`. `nfs_umount_is_vers4()` checks `/proc/mounts` to decide whether an advisory MOUNT `UMNT` call is needed.

Control flow: input may be a mountpoint or `host:dir`; mtab is searched backward. Non-root users may unmount only entries with `users` or matching `user=<name>`. For mounted legacy NFS and non-lazy unmounts, `nfs_umount23()` sends advisory server cleanup before local umount. Successful or already-gone unmounts remove mtab entries.

State and persistence: globals track force/lazy/remount plus shared verbose/nomtab. Persistent state is `/etc/mtab` updates and remote mountd rmtab advisory cleanup.

Dependencies and integration: uses `fstab.c`, parse_opt, parse_dev, network unmount helpers, mount constants, and error reporting.

Risks: unmount behavior must not report failure solely because advisory UMNT failed. User permission checks rely on mtab contents. Test signals include force/lazy/read-only remount, NFSv4 skip, non-root user/users permissions, missing mtab entry behavior, and mtab deletion on `EINVAL`/`ENOENT`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/nfsumount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/parse_dev.c -->
# sources/user-network-fs/nfs-utils/utils/mount/parse_dev.c

Purpose: parses an NFS device string into server hostname/address and export pathname.

Important APIs: `nfs_parse_devname(devname, hostname, pathname)` is exported. Internal parsers handle standard `host:path`, bracketed IPv6 `[addr]:path`, and reject `nfs://` URLs with a clear error.

Control flow: the public parser duplicates the input because parsing is destructive. Standard parsing splits at the first colon and truncates unsupported replicated-host lists at the first comma with a warning. Bracket parsing requires a closing `]` followed by `:`. Both paths enforce hostname and pathname length limits and allocate requested output strings.

State and persistence: no persistent state; output strings are caller-owned heap allocations.

Dependencies and integration: uses nfs-utils `nfs_error`, gettext wrappers, and global `progname`. Included where string mount/unmount parsing needs robust host/path extraction.

Risks: the simple-host parser contains an unusual `else` attachment before path parsing but effectively continues for no-comma cases; replicated mounts and NFS URLs are intentionally unsupported. Test signals include null input, missing colon, overlong host/path, replicated host warnings, bracketed IPv6 success/missing-brace failure, and allocation cleanup on partial failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/parse_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/parse_dev.h -->
# sources/user-network-fs/nfs-utils/utils/mount/parse_dev.h

Purpose: declares the NFS device-name parser.

Important API: `int nfs_parse_devname(const char *, char **, char **);` returns success/failure and optionally allocates hostname and pathname output strings.

Control flow and integration: consumers include this to split `host:dir` or `[IPv6]:dir` syntax before address resolution or unmount advisory processing.

State and persistence: no state; callers own and must free allocated output values from the implementation.

Dependencies: no includes are required by the prototype.

Risks and tests: the header gives no ownership note, so callers must learn allocation behavior from implementation. Test signals are compile coverage and parser tests for all supported/unsupported device forms.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/parse_dev.h -->

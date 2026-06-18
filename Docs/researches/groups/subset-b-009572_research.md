<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/man/es/davfs2.conf.5.po.in -->
# Research: sources/user-network-fs/davfs2/man/es/davfs2.conf.5.po.in

Purpose: Spanish gettext/po4a translation catalog for the generated `davfs2.conf(5)` manual. It mirrors the English configuration manual and is configured by `man/es/meson.build` into `davfs2.conf.5` under `es/man5`.

Important data and APIs: this is PO-format documentation data, not executable code. The API surface is the set of `msgid` keys extracted from `davfs2.conf.5.in` and translated `msgstr` payloads. It preserves substitution tokens such as `@CONFIGFILE@`, `@PROGRAM_NAME@`, `@PACKAGE@`, `@SYS_CONF_DIR@`, `@CERTS_DIR@`, and groff/po4a markup like `B<>`, `I<>`, `E<gt>`, and `\\(rs`.

Control flow and integration: `po4a.conf` declares Spanish as an available language and maps `davfs2.conf.5.in` to `es/davfs2.conf.5.in`; Meson then runs `configure_file()` over `davfs2.conf.5.in.po`/PO-derived material using `mandata`. The resulting manpage is installed only when `nls` and `man` are enabled. Runtime code does not read this file; it affects packaging and operator-facing documentation.

State and persistence: the file persists translation state, including metadata (`POT-Creation-Date: 2026-03-12`, `PO-Revision-Date: 2007-04-26`) and fuzzy flags. Several newer option descriptions are untranslated or fuzzy, especially TLS certificate options, cookie/redirect/SharePoint options, memory minimization, and debugging descriptions.

Dependencies: PO syntax must remain valid for po4a/gettext tooling. It depends on placeholder names matching the configured manpage template and on UTF-8 encoding.

Risks: stale or fuzzy translations can misdocument security-sensitive options such as `trust_ca_cert`, `trust_server_cert`, `secrets`, `ask_auth`, and debug flags that may expose confidential data. Placeholder corruption would break configured output. The file contains old Spanish text that sometimes no longer matches current English semantics.

Test signals: run `po4a po4a.conf`, Meson `subdir('man')`, and package manpage generation with NLS enabled. Review warnings for fuzzy/untranslated entries and inspect the rendered Spanish manpage with `man -l` or groff linting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/man/es/davfs2.conf.5.po.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/man/es/meson.build -->
# Research: sources/user-network-fs/davfs2/man/es/meson.build

Purpose: Meson fragment for installing the Spanish translated `davfs2.conf(5)` manpage.

Important APIs: uses `configure_file(input: 'davfs2.conf.5.in.po', output: 'davfs2.conf.5', configuration: mandata, install_dir: mandir + '/es/man5')`. It consumes `mandata` from the parent `man/meson.build`, so all substitution variables are shared with the English manpages.

Control flow and integration: the parent `man/meson.build` enters this subdirectory only when `enable_nls` is true. `run_command('po4a', 'po4a.conf')` in the parent is expected to have generated or refreshed translated inputs before this configure step.

State and persistence: no local state beyond the generated configured manpage under the build directory and the installed Spanish manpage.

Dependencies: depends on parent-scope `mandata`, `mandir`, and Meson configured-file semantics. It also implicitly depends on po4a-generated Spanish material having the expected filename.

Risks: this installs only `davfs2.conf.5`; Spanish translations for `mount.davfs.8` and `umount.davfs.8` are not configured here. If the po4a output name differs from `davfs2.conf.5.in.po`, Meson configuration fails. The input extension is unusual for a configured manpage and should be checked against po4a outputs.

Test signals: configure with `-Dnls=true -Dman=true`, verify `meson install` places `davfs2.conf.5` under `$mandir/es/man5`, and confirm substituted tokens are resolved.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/man/es/meson.build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/man/meson.build -->
# Research: sources/user-network-fs/davfs2/man/meson.build

Purpose: top-level manpage generation for davfs2. It builds configured English `davfs2.conf(5)`, `mount.davfs(8)`, and `umount.davfs(8)` pages and orchestrates po4a translations.

Important APIs: creates `mandata = configuration_data()` and fills it from project config and Meson options: package names, daemon user/group, system config/run/cache directories, config/secrets filenames, cert directory names, and bug-report URL. Calls `configure_file()` for three manpage templates and `run_command('po4a', 'po4a.conf', check:true)`. If NLS is enabled, enters `de` and `es` subdirectories.

Control flow and integration: invoked from root `meson.build` only when `get_option('man') == true`. It relies on root Meson variables such as `cdata`, `davfs2_sysconfdir`, `davfs2_localstatedir`, `mandir`, and `enable_nls`.

State and persistence: output manpages are build artifacts installed into `man5` and `man8`. Translation generation mutates/generated translated manpage sources in the build flow according to po4a.

Dependencies: Meson, po4a, gettext/NLS gating, and parent configuration values. It must stay aligned with options documented in `mount_davfs.c` and defaults in `defaults.h`.

Risks: `run_command('po4a', ...)` is unconditional inside the man build, so `-Dman=true` requires po4a even without NLS installation. Documentation substitution errors can misrepresent default paths and security policy. Translation subdirs only run under NLS, so non-NLS builds produce English-only manuals.

Test signals: Meson configure/build with `-Dman=true`, verify po4a availability failure behavior, install-tree layout, and rendered manpage placeholders.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/man/meson.build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/man/mount.davfs.8.in -->
# Research: sources/user-network-fs/davfs2/man/mount.davfs.8.in

Purpose: source manual for `mount.davfs(8)`, the user-visible mount helper for exposing WebDAV resources as a local FUSE filesystem.

Important content/API surface: documents command forms via `mount -t davfs` and direct `mount.davfs`, mount options (`conf`, modes, uid/gid, `[no]user`, `username`, network and security flags), daemon privilege drop, WebDAV URL semantics, cache behavior, locks/lost-update handling, credentials and certificate file locations, environment variables (`DAVFS_PASSWORD`, proxy variables), and examples.

Control flow and integration: this file is configured by `man/meson.build` with `mandata`, replacing tokens such as `@PROGRAM_NAME@`, `@PACKAGE@`, `@SYS_CONF_DIR@`, `@SECRETSFILE@`, and `@SYS_CACHE_DIR@`. It is also an input to po4a, although Spanish translation is not configured for this page in `man/es/meson.build`.

State and persistence behavior described: explains in-memory directory metadata, on-disk file cache, delayed upload, permanent cache directories, PID files under `@SYS_RUN@`, lost+found backup files, secrets files, user config templates, and the fact that local ownership/permission changes are cached locally rather than represented on the server except execute bit metadata.

Dependencies/integration: must match implementation in `mount_davfs.c`, `cache.c`, `webdav.c`, `kernel_interface.c`, and defaults in `defaults.h`/Meson options. It documents FUSE kernel version 7 support and umount helper expectations.

Risks: incorrect docs here affect security-critical operator choices around user mounts, secrets readability, TLS certificate trust, and cache recovery. Some typos remain, but the behavioral content matches the cache and lock model observed in `cache.c`.

Test signals: generated manpage should render cleanly with configured values. Behavioral tests should compare documented options with parser support and verify examples for fstab escaping, credentials lookup, and unmount synchronization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/man/mount.davfs.8.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/man/po4a.conf -->
# Research: sources/user-network-fs/davfs2/man/po4a.conf

Purpose: po4a configuration that manages translation extraction and generated translated manpage sources for davfs2 manuals.

Important directives: `[po4a_langs] de es`, `[po4a_paths] $master.pot $lang:$lang/$master.po`, and three `[type:man]` mappings for `davfs2.conf.5.in`, `mount.davfs.8.in`, and `umount.davfs.8.in`. German has translator addenda and UTF-8 options for all three pages. Spanish is mapped only for `davfs2.conf.5.in` with `opt_es:"-k 60 -L UTF-8"`.

Control flow and integration: `man/meson.build` runs `po4a po4a.conf` before entering language subdirs. Generated/updated language files are then consumed by language-specific Meson fragments.

State and persistence: po4a uses POT/PO files as durable translation state and may regenerate translated manpage intermediates. Translation coverage differs per language and per page.

Dependencies: requires po4a with manpage support and stable relative paths from `man/`. Addendum paths must exist for German. Encoding flags must match the PO files.

Risks: the `-k 60` Spanish threshold can produce partially translated output. Spanish coverage is limited to `davfs2.conf.5.in`; mount and umount remain untranslated for Spanish despite language being listed. Build reproducibility depends on po4a version behavior because the root Meson file requires `po4a --version`.

Test signals: run `po4a po4a.conf` from `man/`, check generated files for all listed mappings, and inspect fuzzy/untranslated thresholds in CI.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/man/po4a.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/man/umount.davfs.8.in -->
# Research: sources/user-network-fs/davfs2/man/umount.davfs.8.in

Purpose: source manual for `umount.davfs(8)`, the helper called by `umount(8)` to wait for davfs2 cache synchronization before unmount completion.

Important content/API surface: documents `umount dir` and root-only direct helper invocation, `-h`/`-V`, ignored compatibility flags (`-f -l -n -r -v -t`), lookup of PID files under `@SYS_RUN@`, and fallback `umount -i` if the daemon reports serious errors.

Control flow and integration: configured by `man/meson.build` into `man8`. It references `mount.davfs(8)`, `umount(8)`, `davfs2.conf(5)`, and `fstab(5)`. The behavior described corresponds to the daemon/cache shutdown path in `cache.c` and the helper source `umount_davfs.c` included by `src/meson.build`.

State and persistence behavior described: emphasizes that local cached dirty files may take seconds to hours to write back to the WebDAV server; the helper blocks so `umount` returns only after synchronization, mirroring local filesystem expectations.

Dependencies: relies on PID-file conventions, daemon cooperation, and cache close logic. `_netdev` mount option is recommended so the OS treats the mount as network-backed.

Risks: lazy/forced unmount bypasses normal synchronization guarantees. If docs and helper behavior diverge, users may assume writes are durable when dirty cache data remains local.

Test signals: generated manpage rendering, helper CLI option compatibility, integration tests that dirty a cached file then invoke `umount` and confirm the helper waits for upload or returns an error.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/man/umount.davfs.8.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/meson.build -->
# Research: sources/user-network-fs/davfs2/meson.build

Purpose: root Meson build definition for davfs2 1.8.0. It configures compile-time constants, dependency checks, subdirectories, optional NLS/man/docs, and install paths.

Important APIs: `project('davfs2','c', version:'1.8.0')`, `_GNU_SOURCE` project argument, OS gate for Linux/FreeBSD, `configuration_data()` for `config.h`, `dependency('neon', required:true)`, `find_library('intl')`, header/function probes, `run_command('po4a','--version', check:true)`, `subdir('src')`, `subdir('etc')`, optional `po` and `man`, and optional `install_data()` for docs.

Control flow and integration: build options from `meson_options.txt` set system/user names, cache/state/cert directories, doc/man/NLS behavior. `config.h` exports path and package constants consumed by C files and man generation. NLS is enabled only when option `nls` is true and `msgfmt` is found.

State and persistence: no runtime state, but it fixes installed paths and default runtime directories into binaries. Documentation install destination is computed from `docdir` or `datadir/doc/davfs2`.

Dependencies: C compiler, Meson >=0.58, neon, po4a, optional gettext/msgfmt/libintl, POSIX/GNU headers and functions. For Meson >=1.3, required functions are asserted.

Risks: `prefix / get_option('datadir')` can double-prefix if `datadir` is already absolute or Meson semantics change; path composition deserves install-tree testing. Requiring po4a at root blocks builds even when man generation is disabled. Function checks are conditional on Meson version, so older Meson may skip required-function enforcement.

Test signals: configure/build on Linux and FreeBSD; `meson configure` option matrix for `man`, `doc`, `nls`; inspect generated `config.h`; run installed binaries against expected default paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/meson.build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/meson_options.txt -->
# Research: sources/user-network-fs/davfs2/meson_options.txt

Purpose: declares project-specific Meson options controlling documentation, installation paths, runtime users/groups, cache/state/cert directories, and NLS.

Important options: `man`, `doc`, `docdir`, `cachedir`, `statedir`, `certdir`, `dav_user`, `dav_group`, and `nls`. Defaults install man/docs, use `/var/cache/davfs2` and `/var/run`, relative cert directory `certs`, daemon user/group `davfs2`, and enable NLS if tooling is available.

Control flow and integration: consumed by root `meson.build`, `man/meson.build`, `etc` generation, and C `config.h` substitution. `dav_user`/`dav_group` affect privilege drop docs and runtime defaults; `cachedir`/`statedir` affect persistent cache and PID-file locations.

State and persistence: option values are persisted in Meson build configuration and compiled into generated files.

Dependencies: Meson option parser. Downstream packagers may override options to match distro policy.

Risks: changing path options changes binary/documentation behavior and can break existing systemd/tmpfiles, permissions, or package scripts. `certdir` is documented as relative to sysconfdir; absolute values may produce confusing paths. `statedir` default `/var/run` may differ from modern `/run` policy.

Test signals: option override matrix, install-tree inspection, and runtime smoke tests verifying cache, state, cert, and config paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/meson_options.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/po/POTFILES.in -->
# Research: sources/user-network-fs/davfs2/po/POTFILES.in

Purpose: gettext source manifest listing C files that contain translatable strings for davfs2 Native Language Support.

Important entries: `src/cache.c`, `src/dav_fuse.c`, `src/kernel_interface.c`, `src/mount_davfs.c`, `src/umount_davfs.c`, and `src/webdav.c`.

Control flow and integration: consumed by gettext tooling via Meson `i18n.gettext()` in `po/meson.build`. It ensures `_()` strings in runtime sources are extracted into the `davfs2` text domain.

State and persistence: not runtime state; it persists the extraction scope for translators.

Dependencies: paths must match source files included in `src/meson.build`. Files using `_()` but absent here would ship untranslated messages.

Risks: build or translation drift if new translatable C files are added without updating this manifest. Because cache and WebDAV errors are operator-facing, missing translations reduce diagnostic quality.

Test signals: `meson compile davfs2-pot`/gettext extraction, compare `_(` occurrences against manifest coverage, and verify installed `.mo` files when NLS is enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/po/POTFILES.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/po/meson.build -->
# Research: sources/user-network-fs/davfs2/po/meson.build

Purpose: Meson NLS build fragment for generating gettext catalogs for davfs2.

Important APIs: `i18n = import('i18n')` and `i18n.gettext(meson.project_name(), preset: 'glib')`. It sets `po_dir = meson.current_source_dir()`, though that variable is not used in this fragment.

Control flow and integration: entered from root `meson.build` only when `enable_nls` is true, which requires option `nls=true` and a found `msgfmt`. The domain name is the Meson project name, `davfs2`.

State and persistence: produces build/install translation artifacts, usually `.gmo`/`.mo`, derived from PO files and `POTFILES.in`.

Dependencies: Meson i18n module, gettext/msgfmt, valid PO files, and a complete `POTFILES.in`.

Risks: `preset: 'glib'` assumes GLib gettext conventions; this should be intentional because the C code uses plain gettext macros. If no LINGUAS/PO files are present or stale, installed catalogs may be incomplete.

Test signals: NLS-enabled Meson build, gettext target execution, installed locale file inspection, and runtime smoke test with `LANG=...` to confirm translated diagnostics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/po/meson.build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/src/cache.c -->
# Research: sources/user-network-fs/davfs2/src/cache.c

Purpose: core davfs2 directory/file cache and FUSE upcall implementation target. It translates filesystem operations into WebDAV operations while maintaining an in-memory `dav_node` tree, on-disk cache files, dirty-file upload scheduling, lock refresh/release, local backup recovery, and a persistent XML cache index.

Important APIs: public functions implement the cache contract in `cache.h`: `dav_init_cache`, `dav_close_cache`, `dav_register_kernel_interface`, `dav_tidy_cache`, and upcalls `dav_access`, `dav_close`, `dav_create`, `dav_getattr`, `dav_lookup`, `dav_mkdir`, `dav_open`, `dav_read`, `dav_remove`, `dav_rename`, `dav_rmdir`, `dav_root`, `dav_setattr`, `dav_statfs`, `dav_sync`, `dav_write`.

Control flow: initialization sets globals from `dav_args`, creates the hash table and root, selects a per-mount cache directory, parses `index`, creates backup directory if missing, cleans orphaned cache files, then tries `PROPFIND` on root with retry tolerance. Kernel requests arrive through `dav_fuse.c`; each validates node existence/permissions, updates directories/files if refresh windows expired, invokes `webdav.c` helpers (`dav_get_collection`, `dav_get_file`, `dav_put`, `dav_lock`, `dav_unlock`, `dav_move`, `dav_delete`, `dav_quota`), and updates local node/cache state. `dav_tidy_cache` is called during idle loop to refresh locks, upload closed dirty files, release locks, resize cache, and optionally minimize memory.

State and persistence: global state includes `root`, `backup`, node hash `table`, `changed` queue, retry intervals, default uid/gid/modes, cache directory, cache size counters, and directory entry writer callback. Persistent state is the cache directory: file content cache, directory-list cache files, `lost+found` backups, and XML `index` written on close. Dirty or created files are retried with increasing delay and moved to backup/remove path after hard failures or too many attempts.

Important private helpers: `new_node`, `add_node`, `update_directory`, `update_node`, `update_cache_file`, `create_cache_file`, `create_dir_cache_file`, `write_dir`, `move_dir`, `move_reg`, `move_no_remote`, `remove_node`, `backup_node`, `clean_tree`, `resize_cache`, `parse_index`, `write_node`, and XML callbacks.

Dependencies/integration: depends on neon allocation/XML APIs, POSIX file APIs, user/group database, `defaults.h`, `mount_davfs.h` args, `webdav.h`, `util.h`, and the FUSE directory-entry callback registered by `dav_fuse.c`.

Risks: uses pointer values as inode/node IDs, so process-local validity and alignment/hash assumptions matter. The code is single-thread oriented; concurrent access would need external serialization. Upload failures and lock loss are data-integrity sensitive. XML index parsing deletes invalid trees, and cache backup behavior must be reliable. Some loops increment byte counters even after `write()` returns negative, which deserves review in adjacent FUSE writer code. Permission semantics are local-only and may diverge from remote server state.

Test signals: WebDAV integration tests for create/open/write/close/upload, delayed upload, lock refresh, remote conflict/lost update, rename over open files, cache eviction, XML index restart recovery, orphaned cache backup, user/group permission checks, quota/statfs, and unmount with dirty data.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/src/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/src/cache.h -->
# Research: sources/user-network-fs/davfs2/src/cache.h

Purpose: public cache-layer interface and data model shared between the WebDAV cache implementation and kernel interface.

Important types: `dav_handle` tracks open local cache file descriptors with access flags and requester pid/pgid/uid. `dav_node` represents files/directories with parent/child/tree links, hash-table link, server path, display name, local cache path, ETag, open handles, size, atime/mtime/ctime/server mtime, update time, lock expiration, directory nlink count, remote-exists/dirty flags, mode, uid, and gid. `dav_node_list_item` supports changed/upload scheduling. `dav_stat` backs statfs output. `dav_write_dir_entry_fn` is the kernel-specific callback for serializing directory entries.

Control flow and integration: `dav_fuse.c` uses `dav_node *` as FUSE node IDs and calls these APIs for every filesystem request. `cache.c` owns all mutation. `dav_register_kernel_interface` lets the kernel layer provide directory-entry serialization and receive preferred block size.

State and persistence: declares structures that store both volatile in-memory state and references to persistent cache files. Fields such as `cache_path`, `etag`, `smtime`, `lock_expire`, `remote_exists`, and `dirty` are serialized by `cache.c` into the XML cache index.

Dependencies: requires POSIX types (`mode_t`, `uid_t`, `gid_t`, `pid_t`, `off_t`) and `dav_args` from `mount_davfs.h`.

Risks: public exposure of full `dav_node` internals couples kernel translation tightly to cache representation. Pointer-based inode identity makes stale pointers dangerous after node invalidation. Callers must respect documented permission and lifetime rules.

Test signals: compile-time ABI checks across source files, FUSE operations using node pointers through lookup/open/release, cache index round-trip preserving all required fields, and close/removal behavior for invalidated open nodes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/src/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/src/dav_fuse.c -->
# Research: sources/user-network-fs/davfs2/src/dav_fuse.c

Purpose: FUSE kernel protocol v7 message loop and translation layer. It reads binary FUSE requests from `/dev/fuse`, maps them to `dav_*` cache calls, and writes binary replies.

Important APIs/functions: public `dav_fuse_loop()`. Static handlers include `fuse_access`, `fuse_create`, `fuse_getattr`, `fuse_init`, `fuse_lookup`, `fuse_mkdir`, `fuse_mknod`, `fuse_open`, `fuse_read`, `fuse_release`, `fuse_rename`, `fuse_setattr`, `fuse_stat`, `fuse_write`, plus helpers `write_dir_entry` and `set_attr`.

Control flow: `dav_fuse_loop` allocates a shared buffer, registers `write_dir_entry` with cache, then uses `select()` on the FUSE device. Timeouts trigger `dav_tidy_cache`; FUSE opcodes dispatch to handlers or return `ENOSYS` for unsupported operations. The loop maps FUSE root node ID 1 to the real `dav_node *` root captured during `FUSE_INIT`. On termination request, it forks `/bin/umount -il` on Linux or `/sbin/umount -v` on FreeBSD.

State and persistence: state is process-local: `buf_size`, `buf`, translated root pointer, debug flag, and idle-loop timing. Persistence is delegated to `cache.c`.

Dependencies/integration: depends on `fuse_kernel.h` structures, `cache.h` public API, `kernel_interface.h`, POSIX `select/read/write`, and syslog/gettext. `write_dir_entry` emits `struct fuse_dirent` records for directory cache files.

Risks: FUSE message parsing is manual and buffer-size-sensitive. Node IDs are raw pointers, so stale or forged IDs rely on cache validation. `fuse_read` returns `len + header` even if `dav_read` set an error, so negative/uninitialized `len` paths deserve review. Write loops add `w` even when `write()` fails, which can corrupt counters. Unsupported xattrs/symlinks/links are explicit functional gaps.

Test signals: FUSE protocol smoke tests for lookup/getattr/open/read/write/release/readdir/create/rename/setattr/statfs, malformed size requests, unmount signal path, idle cache tidy behavior, and unsupported opcode error mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/src/dav_fuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/src/defaults.h -->
# Research: sources/user-network-fs/davfs2/src/defaults.h

Purpose: central defaults and constants for davfs2 runtime, cache, HTTP/WebDAV behavior, mount flags, directory/file modes, paths, and debug bitmasks.

Important constants: filesystem type `davfs`; enforced mount flags `DAV_MOPTS` and user mount flags `DAV_USER_MOPTS`; default modes; XML namespace; utab, device, mounts, cache, index, backup directory names; cache sizing/table/refresh/delay defaults; HTTP/proxy/auth/lock/etag/cookie/precheck/compression/timeout/retry/upload/lock-refresh defaults; debug masks `DAV_DBG_CONFIG`, `DAV_DBG_KERNEL`, `DAV_DBG_CACHE`, `DAV_DBG_SECRETS`.

Control flow and integration: values are consumed by option parsing, `cache.c`, `kernel_interface.c`, WebDAV setup, manpage defaults, and generated config templates. FreeBSD compatibility maps Linux mount flag names to BSD equivalents.

State and persistence: constants influence persistent cache location/naming and XML namespace but hold no state themselves.

Dependencies: POSIX mode/mount macros, `config.h` platform detection, and build-time path constants from Meson.

Risks: defaults encode security posture. `nosuid` and `nodev` are always enforced; changing them has security impact. Cache timing defaults influence freshness and lost-update risk. Retry/upload defaults determine how long dirty files remain local before backup/removal. `DAV_IF_MATCH_BUG` comment/default mismatch should be verified.

Test signals: option default tests, generated config/manpage consistency checks, mount flag enforcement tests, cache refresh/upload timing tests, and platform builds for Linux/FreeBSD macro compatibility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/src/defaults.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/src/fuse_kernel.h -->
# Research: sources/user-network-fs/davfs2/src/fuse_kernel.h

Purpose: vendored FUSE 2.5.3 kernel ABI definitions for FUSE protocol version 7.5, trimmed to the structures/opcodes davfs2 uses.

Important APIs/types: fixed-width aliases `__u64`, `__u32`, `__s32`; constants `FUSE_KERNEL_VERSION`, `FUSE_KERNEL_MINOR_VERSION`, `FUSE_ROOT_ID`, device major/minor, `FUSE_MIN_READ_BUFFER`; structs for attributes, statfs, request/response headers, lookup/create/open/read/write/release/setattr/init/access payloads, and directory entries; opcode enum including lookup, getattr, setattr, mkdir, unlink, rename, open, read, write, statfs, release, fsync, init, opendir/readdir, access, create.

Control flow and integration: `dav_fuse.c` casts the shared I/O buffer to these structs and uses enum values to dispatch kernel requests. `kernel_interface.c` uses `FUSE_MIN_READ_BUFFER` to size the device buffer and mount `max_read`.

State and persistence: no state; defines wire layout. Padding is part of ABI correctness.

Dependencies: must match Linux/FreeBSD FUSE kernel expectations for protocol 7.5. It intentionally removes include guards and external includes from original upstream file, relying on including C files to provide integer types.

Risks: ABI drift with modern FUSE kernels can cause subtle protocol bugs. The local comment notes a 2025 read buffer increase to 64 KiB, so buffer expectations changed from the original. Manual struct definitions need alignment/padding care across 32/64-bit builds.

Test signals: mount/read/write/readdir tests on current Linux and FreeBSD FUSE, protocol init negotiation, static size/offset assertions if added, and comparison with kernel FUSE headers for used structs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/src/fuse_kernel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/src/kernel_interface.c -->
# Research: sources/user-network-fs/davfs2/src/kernel_interface.c

Purpose: privileged setup of the FUSE kernel interface. It opens `/dev/fuse`, loads the kernel module if necessary, sizes buffers, mounts the FUSE filesystem, and restores the original effective UID.

Important APIs/functions: public `dav_init_kernel_interface(int *dev, size_t *buf_size, const char *url, const char *mpoint, const dav_args *args)`. FreeBSD-only helpers `add_iovec_opt` and `free_iovec` build `nmount()` iovec options.

Control flow: temporarily `seteuid(0)`, open `/dev/fuse` nonblocking, fork `modprobe fuse` on Linux or `kldload fusefs` on FreeBSD if open fails, retry after a short wait, enforce buffer size at least `FUSE_MIN_READ_BUFFER + 4096`, then mount. Linux builds a mount data string with fd, rootmode, user_id, group_id, `allow_other`, and `max_read`; FreeBSD uses `nmount` with iovec options. On success, restores original euid.

State and persistence: returns an open FUSE device fd and updated buffer size. Kernel mount table state is changed by `mount()`/`nmount()`.

Dependencies/integration: called by mount helper after parsing `dav_args`; pairs with `dav_fuse_loop` for ongoing request handling. Depends on root privileges, `/dev/fuse`, module loaders, system mount APIs, and `defaults.h` device path.

Risks: mount data includes `allow_other`, making local permission handling in `cache.c` critical. Privilege switching failures abort. Module-loading paths are hard-coded. Errors call `ERR`, so this function terminates the program on many failures. Mount options and root mode must match security documentation.

Test signals: root and unprivileged mount flows, missing `/dev/fuse` with module loading, FreeBSD/Linux mount path tests, buffer-size negotiation, euid restoration on success/failure, and mount option inspection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/src/kernel_interface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/src/kernel_interface.h -->
# Research: sources/user-network-fs/davfs2/src/kernel_interface.h

Purpose: public interface between mount/cache setup and the kernel-specific FUSE loop.

Important APIs: `dav_is_mounted_fn` callback type; `dav_init_kernel_interface()` to open/mount the kernel filesystem and update device/buffer data; `dav_fuse_loop()` to process FUSE requests until unmount/termination.

Control flow and integration: `mount_davfs.c` should call `dav_init_kernel_interface` during mount setup, initialize the cache, and then enter `dav_fuse_loop` with the device fd, mountpoint, buffer size, idle time, mount-status callback, run flag, and debug mask.

State and persistence: header declares no state. Implementations create kernel mount state and cache persistence indirectly.

Dependencies: `dav_args` from `mount_davfs.h`, POSIX size/time/int types, and the FUSE/cache implementation files.

Risks: function comments still mention fallback between fuse/coda, but the current implementation is FUSE-focused; stale comments can mislead maintainers. The callback contract for `is_mounted` is important for clean shutdown.

Test signals: compile/link tests across mount helper, integration tests that mount, serve requests, detect unmount, and exit the loop cleanly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/src/kernel_interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/src/meson.build -->
# Research: sources/user-network-fs/davfs2/src/meson.build

Purpose: builds and installs the two davfs2 executables: `mount.davfs` and `umount.davfs`.

Important APIs: `mount_davfs_sources` includes `mount_davfs.c`, `dav_fuse.c`, `cache.c`, `webdav.c`, and `kernel_interface.c`; `umount_davfs_sources` includes `umount_davfs.c`. Two `executable()` calls use `config_inc`, dependencies `[neon_dep, intl_dep]`, `install: true`, and `install_dir: davfs2_sbindir`.

Control flow and integration: root `meson.build` enters this directory after configuring `config.h` and dependencies. `mount.davfs` links the full runtime stack; `umount.davfs` is standalone but still receives the same include dir and dependencies.

State and persistence: build artifact definitions only. Installed binaries are placed under configured sbindir.

Dependencies: parent variables `config_inc`, `neon_dep`, `intl_dep`, and `davfs2_sbindir`; source files must match NLS `POTFILES.in`.

Risks: linking `umount.davfs` against `neon_dep` is likely unnecessary but harmless; if neon is unavailable the whole project fails because mount helper needs it. Source-list drift can break translation extraction or miss new runtime modules.

Test signals: Meson compile/install, ldd/link dependency inspection, executable smoke tests for `--help`/`--version`, and package file-list checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/src/meson.build -->

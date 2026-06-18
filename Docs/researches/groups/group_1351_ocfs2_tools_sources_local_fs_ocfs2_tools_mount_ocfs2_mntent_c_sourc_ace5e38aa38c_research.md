# Group Research: group_1351_ocfs2_tools_sources_local_fs_ocfs2_tools_mount_ocfs2_mntent_c_sourc_ace5e38aa38c

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/local-fs/ocfs2-tools`, which is included in subset A. Every listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/mntent.c -->
# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/mntent.c

Private replacement for libc `mntent` routines used by `mount.ocfs2` mtab/fstab handling. It implements escaping/unescaping for spaces, tabs, newlines, and backslashes using octal `\040`-style sequences.

Exports `my_setmntent`, `my_endmntent`, `my_addmntent`, and `my_getmntent`. `my_setmntent` opens the target file with temporary restrictive `umask(077)`, stores file metadata in `mntFILE`, and records open errors. `my_addmntent` appends a fully escaped mount entry. `my_getmntent` reads nonblank/noncomment lines into static storage, parses fields, tolerates missing final newline, and skips up to `ERR_MAX` malformed lines.

Dependencies include `mntent.h`, `sundries.h` allocation helpers, and `nls.h` no-op translation macros. Important integration: `update_mtab_entry()` in `mount.ocfs2.c` uses this file to append `/etc/mtab` records.

Risks/quirks: returned `struct my_mntent` is static, while its string fields are newly allocated on each parse and are not freed by this parser. Line length is fixed at 4096 bytes. It uses legacy `index()`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/mntent.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/mntent.h -->
# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/mntent.h

Header for the private mtab/fstab parser in `mntent.c`. It defines `struct my_mntent`, `ERR_MAX`, and `mntFILE`.

The public surface is `my_setmntent`, `my_endmntent`, `my_addmntent`, and `my_getmntent`. This mirrors libc-style mount entry operations but with local structures and slightly different prototypes.

Integration is limited to the `mount.ocfs2` support code, especially mtab update paths.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/mntent.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/mount.ocfs2.8.in -->
# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/mount.ocfs2.8.in

Manpage template for `mount.ocfs2`. It documents the helper as the OCFS2 filesystem mounter, normally invoked by `mount(8)`, with syntax `mount.ocfs2 [-vn] [-o options] device dir`.

It lists OCFS2-relevant options including `_netdev`, atime modes, ACL/xattr toggles, commit interval, data ordering, error handling, `localflocks`, coherency, reservation levels, `inode64`, `nocluster`, interruptible IO, and read-only/read-write selection.

Operational notes explain that clustered mounts require the cluster stack to be online, can wait for DLM domain join, and that unmount may involve lock-resource migration. It also advises using `_netdev` in `/etc/fstab` and points failures to `dmesg` and cluster configuration/firewall checks.

This file is documentation only but matches the implementation’s automatic `_netdev` behavior and `nocluster` warning path.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/mount.ocfs2.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/mount.ocfs2.c -->
# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/mount.ocfs2.c

Main implementation of the OCFS2 mount helper. It parses `-v`, `-n`, `-o`, and `-t`, validates the target filesystem type, opens the OCFS2 device read-only through libocfs2, determines whether the volume should be clustered, initializes the cluster stack, joins the heartbeat/DLM group when required, performs `mount(2)`, finalizes group join, adjusts local heartbeat IO priority, and updates mtab.

Key state: global `verbose`, `mount_quiet`, `nocluster_opt`, `progname`, and private `nomtab`. `struct mount_options` carries device, mountpoint, raw options, mount flags, kernel extra options, and requested type.

Important functions:
`read_options()` handles CLI parsing. `process_options()` validates device, mountpoint, type, and delegates `-o` parsing to `parse_opts()`. `add_mount_options()` injects OCFS2-specific kernel options such as `heartbeat=none`, `cluster_stack=...`, `heartbeat=global`, or `heartbeat=local`. `update_mtab_entry()` canonicalizes source/target and writes `/etc/mtab` through the private mntent/fstab helpers. `change_local_hb_io_priority()` invokes `hb_ctl -P -d <device>` for local heartbeat on classic o2cb.

Integration points: libocfs2 superblock helpers, libo2cb stack/heartbeat group APIs, `opts.c`, `sundries.c`, private mtab helpers, and kernel `mount(2)`.

Risks/quirks: after `mount()` fails it stores positive `errno` in `ret` but compares `ret == -EROFS`, so the special read-only error branch appears unreachable. `run_hb_ctl()` uses `WEXITSTATUS` without checking `WIFEXITED`. `add_mount_options()` replaces `*optstr` without freeing the prior string, which is acceptable for this short-lived process but is a leak.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/mount.ocfs2.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/mount.ocfs2.h -->
# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/mount.ocfs2.h

Umbrella header for the `mount.ocfs2` program. It enables large-file/GNU feature macros and includes system mount, filesystem, process, and device headers.

It pulls together local helper headers: `fstab.h`, `nls.h`, `paths.h`, `realpath.h`, `sundries.h`, `xmalloc.h`, `mntent.h`, `mount_constants.h`, and `opts.h`, plus libocfs2 headers.

This file has no include guard, so it is intended as a single translation-unit convenience header rather than a broadly reusable public header.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/mount.ocfs2.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/mount_constants.h -->
# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/mount_constants.h

Compatibility header defining Linux mount flag constants when the platform headers do not provide them. It covers basic flags such as `MS_RDONLY`, `MS_NOSUID`, `MS_NODEV`, remount/action flags, atime flags, bind/move/recursive flags, and magic mount flag values.

This supports the util-linux-derived option parser in `opts.c` and the final `mount(2)` flag computation in `mount.ocfs2.c`.

No executable logic. Main risk is historical compatibility drift if modern kernels add semantics not reflected here.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/mount_constants.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/nls.h -->
# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/nls.h

Small no-op native language support shim copied from util-linux style code. It undefines `bindtextdomain` and `textdomain`, then defines `_()` and `N_()` as identity macros.

Used by mtab parsing and support helpers to keep translatable-message call sites compiling without real gettext integration.

No runtime behavior beyond macro substitution.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/nls.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/opts.c -->
# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/opts.c

Mount option parser adapted from util-linux. It maps `-o` options to mount flags and separates kernel/filesystem-specific extra options.

`opt_map` handles standard and pseudo mount options such as `ro`, `rw`, `noexec`, `nosuid`, `nodev`, `sync`, `remount`, `bind`, `_netdev`, `user`, `owner`, `loop`, atime options, and comments. `string_opt_map` captures options with values such as `loop=`, `vfs=`, `offset=`, `encryption=`, `speed=`, and `comment=`. `parse_string_opt()` also recognizes `nocluster` and sets the global `nocluster_opt`.

`parse_opts()` tokenizes the comma-separated option string, updates `flags`, and builds `extra_opts` for unknown/kernel OCFS2 options. `fix_opts_string()` reconstructs an mtab-friendly canonical option string, starting with `ro` or `rw`, then adding non-skipped recognized flags, remembered string options, extra options, and optional `user=`.

Integration: `mount.ocfs2.c` uses this before calling `mount(2)` and after mounting to create the mtab option string.

Risks/quirks: length accounting relies on the original options length plus 20 and silently omits text if space would run out. Static string option globals make parsing non-reentrant.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/opts.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/opts.h -->
# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/opts.h

Header defining private pseudo mount flags used by the util-linux-derived option parser. It defines flags such as `MS_NOAUTO`, `MS_USERS`, `MS_USER`, `MS_OWNER`, `MS_GROUP`, `MS_PAMCONSOLE`, `MS_NETDEV`, `MS_COMMENT`, and `MS_LOOP`.

It also defines masks for options not passed to the kernel (`MS_NOSYS`), not written to mtab (`MS_NOMTAB`), ordinary-user security defaults (`MS_SECURE`), and owner-mounted device defaults (`MS_OWNERSECURE`).

Exports `parse_opts()` and `fix_opts_string()`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/opts.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/paths.h -->
# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/paths.h

Path constants for `mount.ocfs2` support code. It includes `<mntent.h>`, defines `_PATH_FSTAB` as `/etc/fstab`, and derives mtab lock/temp paths from `_PATH_MOUNTED` when available or falls back to `/etc/mtab~` and `/etc/mtab.tmp`.

Also defines `LOCK_TIMEOUT` as 10 seconds. Used by fstab/mtab update code outside this group and by the mtab routines called from `mount.ocfs2.c`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/paths.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/realpath.c -->
# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/realpath.c

Local canonical-path resolver derived from older libc/util-linux code. `myrealpath()` resolves relative paths against `getcwd`, collapses repeated slashes, `.` and `..`, follows symlinks with `readlink`, and writes into a caller-provided buffer.

It is used by `sundries.c` `canonicalize()` before writing mtab entries. The resolver can restart on absolute symlink targets or splice relative symlink targets into the remaining path.

Risks/quirks: `readlinks` is incremented for each component before `readlink`, so very deep non-symlink paths can hit `MAX_READLINKS` and return `ELOOP`. It uses a single temporary `buf` for rewritten path tails and requires the caller to supply sufficient buffer size.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/realpath.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/realpath.h -->
# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/realpath.h

Single-prototype header for `myrealpath(const char *path, char *resolved_path, int m)`.

Used by `sundries.c` to canonicalize paths without relying on libc `realpath`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/realpath.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/sundries.c -->
# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/sundries.c

Utility functions adapted from util-linux mount code. Provides string allocation/concatenation helpers, signal masking, nonfatal error output, filesystem type matching, option matching, and path canonicalization.

Key exports: `xstrndup`, `xstrconcat2`, `xstrconcat3`, `xstrconcat4`, `block_signals`, `error`, `matching_type`, `matching_opts`, and `canonicalize`. `canonicalize()` preserves special pseudo devices `none`, `proc`, and `devpts`, otherwise uses `myrealpath()` and maps `/dev/dm-N` to `/dev/mapper/<name>` by reading `/sys/block/<dm-N>/dm/name`.

Integration: `mount.ocfs2.c` uses signal blocking and canonicalization around cluster join and mtab updates. `mntent.c` uses allocation helpers via `sundries.h`.

Risks/quirks: `xstrconcat3/4` free their first argument, which is intentional but easy to misuse. `canonicalize_dm_name()` uses `strdup()` directly rather than fatal allocation wrappers.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/sundries.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/sundries.h -->
# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/sundries.h

Header for mount support utilities. It declares global mount state (`nocluster_opt`, `mount_quiet`, `verbose`, `sloppy`), the `streq` macro, support function prototypes, optional NFS mount prototype, and util-linux style exit status bit constants.

Used throughout the `mount.ocfs2` helper modules.

Notable: it declares `xmalloc` and `xstrdup` even though those are implemented in `xmalloc.c`, while other string helpers are in `sundries.c`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/sundries.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/xmalloc.c -->
# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/xmalloc.c

Fatal allocation helper implementation. Defines global callback `at_die`, `die()`, `xmalloc()`, `xrealloc()`, and `xstrdup()`.

`die()` prints a formatted message, calls `at_die` if set, then exits with the provided code. `xmalloc()` returns `NULL` for size zero, otherwise exits on allocation failure. `xrealloc()` and `xstrdup()` also exit on allocation failure; `xstrdup(NULL)` returns `NULL`.

Used by private mount support code to simplify allocation error handling.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/xmalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/xmalloc.h -->
# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/xmalloc.h

Header for fatal allocation helpers. Declares `xmalloc`, `xrealloc`, `xstrdup`, `die`, and the `at_die` callback pointer.

Used by `mount.ocfs2` helper code and included indirectly through the umbrella mount header.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mount.ocfs2/xmalloc.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mounted.ocfs2/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/mounted.ocfs2/Makefile

Build recipe for `mounted.ocfs2`. It builds one source file, `mounted.c`, into the root sbin program `mounted.ocfs2`.

Links against `libocfs2`, `libo2dlm`, `libo2cb`, `libtools-internal`, `com_err`, UUID, AIO, and optional `dlm_lt`/`cmap` libraries depending on configured stack support.

Also installs/builds the `mounted.ocfs2.8` manpage and includes common top-level make preamble/postamble.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mounted.ocfs2/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mounted.ocfs2/mounted.c -->
# File Research: sources/local-fs/ocfs2-tools/mounted.ocfs2/mounted.c

Implementation of `mounted.ocfs2`, an OCFS2 volume detection utility. It can scan a specified device or all entries from `/proc/partitions`.

Two modes: quick detect (`-d`, default) reads likely superblock offsets directly and prints device, stack, cluster, global-heartbeat flag, UUID, and label. Full detect (`-f`) calls `ocfs2_check_heartbeats()` to populate mounted/heartbeat state and prints nodes that appear to have mounted each volume.

Important helpers: `build_partition_list()` enumerates devices, maps `dm-N` to `/dev/mapper` when possible, filters tiny devices, and removes whole-disk entries when partitions are found. `populate_sb_info()` copies label/UUID and cluster stack metadata from the superblock. `print_full_detect()` resolves node numbers to names through o2cb cluster APIs.

Integration: uses libocfs2 device/superblock routines, libo2cb node/cluster listing, kernel-list linked lists, and tools-internal verbose logging.

Risks/quirks: full detect can report stale mount state because it reads heartbeat/slot information without cluster locks; the manpage explicitly documents this. Device filtering is Linux-specific and tied to `/proc/partitions` and `/sys/dev/block`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mounted.ocfs2/mounted.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/mounted.ocfs2/mounted.ocfs2.8.in -->
# File Research: sources/local-fs/ocfs2-tools/mounted.ocfs2/mounted.ocfs2.8.in

Manpage template for `mounted.ocfs2`. Documents quick mode `-d`, full mode `-f`, and optional device argument.

Explains quick output as OCFS2 volumes with labels, UUIDs, cluster stack, cluster name, and global-heartbeat flag. Explains full output as volumes plus nodes that may have mounted them.

Important warning: full detect data can be stale after unclean unmount because slot recovery may not have run yet. Examples show quick and full tabular output.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/mounted.ocfs2/mounted.ocfs2.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb.pc.in -->
# File Research: sources/local-fs/ocfs2-tools/o2cb.pc.in

Pkg-config template for the `o2cb` library. It fills prefix paths and version at configure time, declares `Requires: com_err`, links with `-lo2cb`, and exposes include flags.

Used by downstream consumers needing libo2cb cluster-base APIs.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb.pc.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/Makefile

Build recipe for two programs: legacy `o2cb_ctl` and command-oriented `o2cb`.

Shared config/parser sources are `o2cb_config.c`, `jconfig.c`, and `jiterator.c`. `o2cb_ctl` adds `o2cb_ctl.c`. `o2cb` adds `o2cbtool.c` and operation modules for cluster, node, heartbeat, listing, registration, heartbeat start/stop, disk scanning, status, and utilities.

Links against libo2cb, GLib, libocfs2, libo2dlm, libtools-internal, com_err, and optional cluster stack libraries. Static linking is enabled unless `OCFS2_DYNAMIC_CTL` is set.

Also builds manpages `o2cb_ctl.8`, `o2cb.8`, and `ocfs2.cluster.conf.5`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/jconfig.c -->
# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/jconfig.c

Generic GLib-based parser and serializer for stanza-style config files. It parses files or memory buffers into `JConfig`, containing ordered stanza names and a hash table from stanza name to lists of `JConfigStanza`; each stanza has an attribute hash table.

Parser format: stanza lines begin at column 0 as `name:`, attributes are indented as `key = value`, blank lines close current stanza, `#` comments are skipped, and attribute values support continuation lines ending in backslash.

Public API includes context creation/configuration, file/memory parsing, stanza iteration, stanza lookup by name and optional match filters, attribute get/set/delete, config dump to file or memory, and free routines.

Integration: `o2cb_config.c` uses this as the storage layer for `/etc/ocfs2/cluster.conf`. `o2cb_ctl.c` and `o2cbtool` interact with the typed wrapper, not usually with `jconfig` directly.

Risks/quirks: serializer iterates GLib hash tables, so attribute/stanza output order can be nondeterministic except for the separately tracked stanza-name list not used by dump. `j_config_parse_to_eol()` contains an assignment in `if ((token = G_TOKEN_CHAR) && ...)`, a legacy bug that effectively ignores the actual token type. `j_config_delete_stanza()` appears to test the old list pointer instead of `new_elem` when checking whether the list is empty.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/jconfig.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/jconfig.h -->
# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/jconfig.h

Public API for the generic configuration parser. It forward-declares `JConfigStanza`, `JConfig`, and `JConfigCtxt`, defines `JConfigMatch` for attribute-value filtering, and declares parse, iterate, mutate, dump, and free functions.

It depends on GLib types and `JIterator` being visible to consumers. Used by `o2cb_config.c`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/jconfig.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/jiterator.c -->
# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/jiterator.c

Opaque iterator abstraction over arbitrary contexts, with a built-in adapter for GLib `GList`.

`j_iterator_new()` stores context and function callbacks. `j_iterator_new_from_list()` copies a `GList`, wraps it in a header element, and iterates without owning item data. `j_iterator_has_more()`, `j_iterator_get_next()`, and `j_iterator_free()` drive the callback interface.

Integration: used heavily by `jconfig`, `o2cb_config`, and `o2cb` operation modules to avoid exposing GLib lists directly.

Quirk: `j_iterator_free()` assumes `notify_func` is non-null.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/jiterator.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/jiterator.h -->
# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/jiterator.h

Header for the opaque iterator abstraction. Defines `JIterator`, callback type `JIteratorFunc`, and declares construction, list-adapter construction, `has_more`, `get_next`, and free functions.

Used by the generic config parser and typed O2CB config model.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/jiterator.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cb.8.in -->
# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cb.8.in

Manpage template for the command-oriented `o2cb` utility. It documents global options `--config-file`, `--verbose`, `--help`, and `--version`.

Commands covered: add/remove cluster, add/remove node, add/remove heartbeat, heartbeat-mode, list clusters/nodes/heartbeats, register/unregister cluster, start/stop heartbeat, and cluster-status.

This manpage maps closely to `o2cbtool.c` dispatch and the `op_*.c` modules. It documents the default config file as `/etc/ocfs2/cluster.conf`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cb.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cb_config.c -->
# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cb_config.c

Typed configuration model for O2CB cluster config. It maps generic `JConfig` stanzas into `O2CBConfig`, `O2CBCluster`, `O2CBNode`, and `O2CBHeartbeat` objects.

Load path: `o2cb_config_load()` parses `/etc/ocfs2/cluster.conf` or an empty config if missing, then `o2cb_config_fill()` reads `cluster` stanzas and associated `node`/`heartbeat` stanzas. It validates node numbers, IPv4 strings, ports, node count, heartbeat mode, and required attributes.

Store path: `o2cb_config_store()` builds a new `JConfig`, stores cluster, heartbeat, and node stanzas, dumps to memory, then writes via `write_file()`, which creates `/etc/ocfs2`, writes a temp file from `mkstemp`, chmods it, closes it, and renames it over the target.

Public API supports add/remove/get clusters, cluster name and heartbeat mode accessors, heartbeat add/remove/get/list, node add/delete/get/list, and node property accessors/mutators.

Risks/quirks: `o2cb_config_fill_cluster()` has `if (!match.value && !*match.value)`, which should likely be `||` to avoid dereferencing null. `o2cb_node_set_ipv4()` replaces `n_addr` without freeing the old value. Store order is based on in-memory list order for typed objects but attribute order is inherited from `jconfig` hash iteration.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cb_config.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cb_config.h -->
# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cb_config.h

Public typed API for O2CB cluster configuration management. It declares opaque config, cluster, node, and heartbeat types.

Functions cover loading/storing/freeing configs, cluster add/remove/list/lookup/name/hb-mode operations, heartbeat region operations, node list/lookup/add/delete, and node property accessors/mutators.

Used by both `o2cb_ctl.c` and the newer `o2cbtool` command modules.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cb_config.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cb_ctl.8.in -->
# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cb_ctl.8.in

Manpage template for legacy `o2cb_ctl`, described as a direct control program for the O2CB service and not recommended for normal users.

Documents object/attribute operations: create `-C`, delete `-D`, info `-I`, change `-H`, install/remove live config with `-i`/`-u`, object selection with `-n`, type selection with `-t`, attributes with `-a`, and compact/verbose info with `-o`/`-z`.

Examples show adding a node offline or online, querying attributes, and changing an IP address. Implementation is only partial in `o2cb_ctl.c`: delete and node changes are not supported there.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cb_ctl.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cb_ctl.c -->
# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cb_ctl.c

Legacy object/attribute interface for O2CB config. It parses short options for create/delete/info/change, loads `/etc/ocfs2/cluster.conf`, manipulates typed config objects, optionally applies running cluster changes through libo2cb, and writes config on changes.

Supported operations: create cluster, create node, info cluster/node, change cluster name, and bring a cluster online/offline through the `online` attribute. Delete is explicitly not supported. Node changes are explicitly not supported.

Important functions: `parse_options()`, `validate_attrs()`, `load_config()`, `write_config()`, `find_objects_for_type()`, `find_type_for_objects()`, `run_info_*()`, `online_cluster()`, `offline_cluster()`, `run_change_*()`, and `run_create_*()`.

Integration: uses `o2cb_config` for persistent state and libo2cb for live configfs cluster/node operations. Local-node detection compares configured node name to `gethostname()` up to a dot boundary.

Risks/quirks: `attr_boolean()` returns `-EINVAL` from a `gboolean` function, which is truthy and can make invalid boolean values look like true to callers. Online change modifies live cluster state before config persistence, and a FIXME notes this ordering.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cb_ctl.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cb_scandisk.c -->
# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cb_scandisk.c

Disk scanning support for global heartbeat operations. It scans block devices, identifies OCFS2 heartbeat regions by UUID, and fills `o2cb_device` descriptors with region and cluster descriptions.

`fill_desc()` opens a candidate device with `OCFS2_FLAG_HEARTBEAT_DEV_OK`, fills heartbeat and cluster descriptors, and duplicates selected region strings. `filter_devices()` accepts sysfs-backed disk nodes without holders and asks for a rescan if device paths are missing. `add_to_list()` favors mapper, EMC power, SCSI, loop, xvd, virtio, rbd, drbd, and nbd paths. `o2cb_scandisk()` retries with increasing sleep if udev paths are not ready.

Integration: `op_start.c` uses this to map configured heartbeat UUIDs to live devices before calling `o2cb_start_heartbeat()`.

Risks/quirks: comments note descriptor allocations are not fully freed. `free_scan_context()` frees `hb_devices` nodes but not `hb_path`, so scan context leaks paths in-process. Device path filtering is Linux/storage-stack-specific.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cb_scandisk.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cb_scandisk.h -->
# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cb_scandisk.h

Header for heartbeat device scanning. It includes filesystem, directory, sysmacros, scandisk, libo2cb, and kernel-list dependencies.

Defines `struct o2cb_device`, including UUID, found/heartbeat-started flags, region descriptor, and cluster descriptor. Exports `o2cb_scandisk(struct list_head *hbdevs)`.

Used by `op_start.c`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cb_scandisk.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cbtool.c -->
# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cbtool.c

Main program for the newer `o2cb` command utility. It defines the command table mapping command names to operation functions, parses global options, loads the selected config file, dispatches the command, prints command usage on failure, and stores the config if the command marked it modified.

Global options include `--config-file`, `--help`, `--verbose`, and `--version`. `o2cbtool_init_cluster_stack()` initializes libo2cb and verifies that the active cluster stack is `o2cb`.

Integration: command implementations live in `op_cluster.c`, `op_node.c`, `op_heartbeat.c`, `op_lists.c`, `op_register.c`, `op_start.c`, and `op_status.c`.

Quirk: `--version` exits with status 1 after printing version, likely unintentional.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cbtool.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cbtool.h -->
# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cbtool.h

Shared header for the `o2cb` command modules. It includes C/POSIX networking, getopt, signal, GLib, typed config, libo2cb, libocfs2, and tools-internal helpers.

Defines defaults for config file and IP port, the `struct o2cb_command` dispatch context, long-option enum values, command prototypes, signal blocking helper, stack initialization helper, and utility functions for registered cluster and active heartbeat checks.

This is the common contract connecting `o2cbtool.c` and all `op_*.c` modules.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cbtool.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cbutils.c -->
# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cbutils.c

Small utility module for live O2CB state checks.

`is_cluster_registered()` lists nodes in a cluster and returns true if any registered node is marked local. `is_heartbeat_active()` lists active heartbeat regions and returns true if at least one exists.

Used by `op_start.c` and `op_status.c` to validate cluster online/heartbeat state before starting heartbeat or reporting status.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/o2cbutils.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/ocfs2.cluster.conf.5.in -->
# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/ocfs2.cluster.conf.5.in

Manpage template for `/etc/ocfs2/cluster.conf`. It documents the O2CB cluster configuration file and its three stanza types: `cluster`, `node`, and `heartbeat`.

Cluster stanza fields: `node_count`, `heartbeat_mode`, and `name`; cluster names are limited to up to 16 alphanumeric characters. Node stanza fields: `ip_port`, `ip_address`, `number`, `name`, and `cluster`. Heartbeat stanza fields: `region` and `cluster`.

It emphasizes that all nodes in the cluster should share the same file and recommends using `o2cb(8)` rather than manual editing. The example aligns with `o2cbtool` command behavior.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/ocfs2.cluster.conf.5.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/op_cluster.c -->
# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/op_cluster.c

Implements `o2cb add-cluster` and `o2cb remove-cluster`.

`o2cbtool_validate_clustername()` strips whitespace, enforces non-empty names, checks maximum `OCFS2_CLUSTER_NAME_LEN`, and permits only alphanumeric characters. `o2cbtool_add_cluster()` validates and adds the cluster to the in-memory config. `o2cbtool_remove_cluster()` removes an existing cluster from the config.

These operations only modify the config model and mark the command modified; persistence is handled by `o2cbtool.c`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/op_cluster.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/op_heartbeat.c -->
# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/op_heartbeat.c

Implements heartbeat-region config commands for `o2cb`.

`get_region()` treats a non-block-device argument as a region UUID string; for block devices it opens the OCFS2 filesystem with heartbeat-device allowance and uses `fs->uuid_str`. `o2cbtool_add_heartbeat()` adds a region to a cluster. `o2cbtool_remove_heartbeat()` removes a region. `o2cbtool_heartbeat_mode()` sets cluster heartbeat mode to `global` or `local`.

Integration: persistent model changes are stored later by `o2cbtool.c`; actual starting/stopping live heartbeat is in `op_start.c`.

Risks/quirks: uses `gchar *region = '\0'` style initialization, effectively null pointer but visually odd. Device-to-UUID conversion requires the device to be readable as OCFS2.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/op_heartbeat.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/op_lists.c -->
# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/op_lists.c

Implements `o2cb list-clusters`, `list-cluster`, `list-nodes`, and `list-heartbeats`.

`list_parse_options()` handles `--oneline` and cluster argument parsing. `show_heartbeats()`, `show_nodes()`, and `show_cluster()` print either stanza-style output or compact one-line output. `o2cbtool_list_objects()` selects which objects to print based on command name. `o2cbtool_list_clusters()` iterates all clusters and prints names.

Uses typed config iterators and verbose output channel `VL_OUT`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/op_lists.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/op_node.c -->
# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/op_node.c

Implements `o2cb add-node` and `o2cb remove-node`.

`add_node_parse_options()` handles `--ip`, `--port`, and `--number`, then extracts cluster and node names. `validate_ip_address()` validates supplied IPv4 or resolves the node name with `getaddrinfo()`. `validate_nodenum()` chooses the first unused node number or validates the supplied number against `O2NM_MAX_NODES`. `o2cbtool_add_node()` applies all validations and appends the node to the cluster config. `o2cbtool_remove_node()` deletes a node by name.

Risks/quirks: allocated `ip` is not freed before return, but the process is short-lived. Port parsing accepts any `strtol` result without explicit range validation here; the typed config layer stores it as `guint`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/op_node.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/op_register.c -->
# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/op_register.c

Implements live configfs registration and unregistration for configured clusters.

Registration flow: block signals, validate cluster exists/name, initialize and verify o2cb stack, create cluster if needed, register heartbeat mode, unregister stale/changed nodes, and add configured nodes with local-node marking based on hostname.

Unregistration flow: verify active cluster matches requested cluster, verify no active heartbeat regions remain, unregister all nodes, and remove the cluster.

Important helpers: `compare_node_attributes()` compares live configfs node IP/port/number with config, `unregister_nodes()` removes stale or all nodes, `register_nodes()` adds configured nodes, and `register_heartbeat_mode()` writes heartbeat mode while tolerating local-heartbeat mode on older stacks.

Integration: uses libo2cb configfs APIs and `o2cb_config` typed objects. Signal blocking prevents interruption during live config changes.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/op_register.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/op_start.c -->
# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/op_start.c

Implements `o2cb start-heartbeat` and `o2cb stop-heartbeat` for global heartbeat mode.

Start flow: verify cluster exists, stack is o2cb, cluster is registered, global heartbeat mode is enabled, build configured heartbeat device descriptors, scan disks to match UUIDs to devices, start heartbeat on each found region, then stop heartbeat on live regions removed from config.

Stop flow: verify stack and active cluster, ensure global heartbeat mode, list active regions, and stop all or only stale regions depending on caller.

Important helpers: `get_region_descs()`, `start_heartbeat()`, `start_global_heartbeat()`, `_fake_default_cluster_desc()`, `_fake_region_desc()`, and `stop_global_heartbeat()`.

Integration: depends on `o2cb_scandisk.c` to map configured region UUIDs to devices and libo2cb heartbeat APIs for start/stop. Uses signal blocking around live heartbeat changes and rollback stopping in `free_region_descs()` when start fails.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/op_start.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/op_status.c -->
# File Research: sources/local-fs/ocfs2-tools/o2cb_ctl/op_status.c

Implements `o2cb cluster-status [clustername]`.

It initializes the o2cb stack, gets the active cluster name from libo2cb, optionally compares it to the requested name, checks that the cluster is registered, checks heartbeat mode, and for global heartbeat requires at least one active heartbeat region. It prints online/offline and returns 0 for online, 1 otherwise.

Risk: `get_active_clustername()` writes `name[namelen] = '\0'`; callers pass a buffer sized `OCFS2_CLUSTER_NAME_LEN + 1` with `namelen` set to `OCFS2_CLUSTER_NAME_LEN`, so this is safe for current usage but relies on that convention.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2cb_ctl/op_status.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2dlm.pc.in -->
# File Research: sources/local-fs/ocfs2-tools/o2dlm.pc.in

Pkg-config template for the `o2dlm` library. It substitutes install paths and version, requires `com_err`, links with `-lo2dlm` plus configured dynamic loading libraries, and exposes include flags.

Used by external consumers of OCFS2 DLM APIs.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2dlm.pc.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2image/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/o2image/Makefile

Build recipe for the `o2image` metadata imaging tool. It compiles `o2image.c` into root sbin program `o2image`, builds `o2image.8`, and includes common top-level make rules.

Links primarily against `libocfs2`, GLib, com_err, and AIO. It defines `VERSION` for the C source and includes OCFS2 headers plus local directory includes.

Although this group does not include `o2image.c`, the Makefile shows the tool is standalone and only needs libocfs2 for core imaging logic.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2image/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/o2image/o2image.8.in -->
# File Research: sources/local-fs/ocfs2-tools/o2image/o2image.8.in

Manpage template for `o2image`, which copies or restores OCFS2 filesystem metadata.

Documents default packed metadata image creation, raw/sparse output with `-r`, restore mode with `-I`, and interactive size confirmation with `-i`. It emphasizes that file data is not copied, only metadata blocks such as inodes and directory/file names.

The restore option is explicitly warned as dangerous because it can overwrite and corrupt an existing volume. Debugfs understands both packed and raw image formats.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/o2image/o2image.8.in -->
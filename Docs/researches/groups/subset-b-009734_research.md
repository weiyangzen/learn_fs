# subset-b-009734 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/parse_opt.c -->
# sources/user-network-fs/nfs-utils/utils/mount/parse_opt.c

## Purpose

`parse_opt.c` implements the text mount-option list used by `mount.nfs` and `umount.nfs`. It turns comma-delimited option strings into a mutable doubly linked list, preserving option order so callers can model Linux mount parsing rules where the rightmost duplicate wins.

## Important APIs, types, and functions

The private `struct mount_option` stores `keyword`, optional `value`, and list links. `struct mount_options` stores `head`, `tail`, and `count`. Public operations include `po_split`, `po_dup`, `po_replace`, `po_join`, insertion/appending, `po_contains`, `po_contains_prefix`, `po_get`, `po_get_numeric`, `po_rightmost`, `po_remove_all`, and `po_destroy`.

## Control flow

`po_split` creates an empty list, tokenizes on commas with `token.c`, converts each token into `keyword[=value]`, and appends it. Mutators add or delete nodes while keeping head/tail/count correct. Lookup helpers scan either from the head for existence or from the tail for effective values. `po_join` first computes the exact output length, then concatenates each option back into a comma string.

## State and persistence behavior

All state is heap memory owned by a `struct mount_options` handle. `po_replace` transfers list node ownership from source to target and empties the source. The module performs no persistent I/O; its output string is later passed to `mount(2)` or written into mtab-style records by higher layers.

## Dependencies and integration points

It depends on `token.c` for quote-aware tokenization and is used heavily by `stropts.c`, `utils.c`, and network option helpers. It exposes an opaque handle in `parse_opt.h`, allowing mount code to rewrite options without string surgery.

## Risks and edge cases

Quoted commas are handled only at token boundaries; `option_create` itself splits on the first `=` without quote awareness. `po_get_numeric` with `strtol` accepts numeric prefixes because it checks `endptr != option` but not `*endptr == '\0'`. Allocation failures unwind through destroy paths, but callers must honor `PO_FAILED` and `NULL` returns.

## Test signals

Useful tests should cover empty and NULL strings, duplicate rightmost selection, quoted comma tokens, missing values, values with additional `=`, removal of all duplicates, numeric bad values, `po_replace` ownership transfer, and round-trip `po_split`/`po_join`.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/parse_opt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/parse_opt.h -->
# sources/user-network-fs/nfs-utils/utils/mount/parse_opt.h

## Purpose

`parse_opt.h` is the public interface for the mount-option list abstraction. It hides the linked-list representation and gives mount code a small API for parsing, querying, editing, and serializing option strings.

## Important APIs, types, and functions

The header defines `po_return_t` (`PO_FAILED`, `PO_SUCCEEDED`) and `po_found_t` (`PO_NOT_FOUND`, `PO_FOUND`, `PO_BAD_VALUE`). It forward-declares `struct mount_options` and declares all list lifecycle, lookup, mutation, and serialization functions implemented in `parse_opt.c`.

## Control flow

There is no executable control flow. The API contract implies a parse-edit-join lifecycle: obtain a handle with `po_split`, modify with insert/append/remove/replace, query with contains/get/rightmost, serialize with `po_join`, then release with `po_destroy`.

## State and persistence behavior

The opaque handle represents heap state managed by the implementation. The header itself stores no state and performs no persistence. Callers are responsible for freeing joined strings as documented by `po_join` behavior.

## Dependencies and integration points

The header is included by `stropts.c`, `utils.c`, and other mount helpers. Because the representation is opaque, callers cannot depend on list internals and must use the exported functions for all option manipulation.

## Risks and edge cases

The API uses mutable `char *` for many input strings even when functions do not modify the caller buffer, which can invite casts from const data. `po_get` returns an interior pointer owned by the option list, so callers must not free or retain it beyond list lifetime.

## Test signals

Compile tests should ensure all mount users include this header without requiring private structs. API tests should verify that returned `po_found_t` values distinguish absent options from bad numeric options.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/parse_opt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/stropts.c -->
# sources/user-network-fs/nfs-utils/utils/mount/stropts.c

## Purpose

`stropts.c` is the text-option mount path for `mount.nfs`. It validates user options, resolves server addresses, negotiates NFS version and transport choices, constructs final kernel mount option strings, and drives foreground/background retry behavior.

## Important APIs, types, and functions

The private `struct nfsmount_info` carries the requested spec, mountpoint, type, parsed options, extra mtab options, version, flags, fake mode, and background-child state. Public entry is `nfsmount_string`. Key helpers include `nfs_validate_options`, `nfs_set_version`, `nfs_append_addr_option`, `nfs_append_clientaddr_option`, `nfs_fix_mounthost_option`, `nfs_rewrite_pmap_mount_options`, `nfs_try_mount_v4`, `nfs_try_mount_v3v2`, `nfs_autonegotiate`, `nfsmount_fg`, `nfsmount_bg`, and `nfs_remount`.

## Control flow

`nfsmount_string` parses `extra_opts`, initializes `nfsmount_info`, and calls `nfsmount_start`. Validation parses `server:path` except on remount, chooses protocol family, strips user-supplied `addr`, determines version, and handles `sloppy`. Non-remount mounts choose foreground or background from rightmost `bg`/`fg`. The first attempt resolves addresses if needed, appends `addr=`, then either tries NFSv4 directly/autonegotiates or probes v2/v3 through rpcbind. V4 mounts add `clientaddr=` and format version/minor options. V3/V2 mounts rewrite protocol, port, mount protocol, mount version, and mount port from portmapper probes before calling `mount(2)`.

## State and persistence behavior

The module keeps mount attempt state in memory. It mutates the caller's `extra_opts` string to describe successful mounts for mtab, but deliberately records user-specified options before v3/v2 negotiation so unmount can renegotiate stale ports. It starts `rpc.statd` when locking is enabled and may fork background retry children through callers that honor `EX_BG`.

## Dependencies and integration points

It depends on NFS network helpers, rpcbind probing, config defaults, `parse_dev`, `parse_opt`, `mount(2)`, `getaddrinfo`, `nfs_error` reporting, and kernel-version checks from `version.h`. It integrates with `mount.nfs` command parsing through `stropts.h` and with `umount.nfs` via the mtab options it preserves.

## Risks and edge cases

Autonegotiation relies on errno classification from kernel mount attempts and rpcbind failures; misclassified failures can stop fallback too early or hide the true error. Static counters in `nfs_is_permanent_error` are process-global, so repeated attempts share history. User-provided `clientaddr` mismatch only warns, not fails. V4 rejects mountd-specific options by forcing fallback. Background retries can run for a long time by default. RDMA skips version/transport negotiation.

## Test signals

Tests should cover explicit v4 minor versions, default v4.2 fallback to v4.1/v4.0/v3, v3 rpcbind rewrites, remount bypass, `bg` retry classification, `retry=` parsing, `sloppy` handling on old/new kernels, lock/statd failures, clientaddr validation, mounthost/mountaddr combinations, RDMA no-negotiation behavior, and fake mounts.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/stropts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/stropts.h -->
# sources/user-network-fs/nfs-utils/utils/mount/stropts.h

## Purpose

`stropts.h` exposes the text-option NFS mount entry point used by the command-line mount frontend.

## Important APIs, types, and functions

It declares `nfsmount_string(const char *spec, const char *node, char *type, int flags, char **extra_opts, int fake, int child)`, returning a mount command exit code.

## Control flow

The header has no executable logic. Its declaration transfers control to `stropts.c`, which owns parsing, validation, negotiation, retries, and the final `mount(2)` call.

## State and persistence behavior

The function contract includes an in/out `extra_opts` pointer. Implementations may replace this string with options appropriate for mtab or caller persistence.

## Dependencies and integration points

It is included by `mount.nfs` frontend code. The API exposes only primitive C types, keeping callers insulated from `struct nfsmount_info` and the option-list internals.

## Risks and edge cases

Callers must pass a valid mutable `char **extra_opts`; on success the pointed-to string may be freed and replaced. Misunderstanding `fake` or `child` changes whether mounts are executed or retried as a daemon.

## Test signals

Build coverage should ensure the mount frontend calls this interface with correct argument ownership. Integration tests should verify that `extra_opts` changes are visible to the caller.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/stropts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/token.c -->
# sources/user-network-fs/nfs-utils/utils/mount/token.c

## Purpose

`token.c` provides a small reentrant tokenizer for mount option parsing. It avoids `strtok`, does not modify the input string, and treats delimiters inside double quotes as literal characters.

## Important APIs, types, and functions

`struct tokenizer_state` stores the current position, delimiter, and error code. `init_tokenizer` allocates state, `next_token` returns a newly allocated token, `tokenizer_error` exposes parse/allocation errors, and `end_tokenizer` frees state. Private helpers skip leading delimiters and find the next delimiter while tracking quote state.

## Control flow

Each `next_token` call skips delimiter runs, stops at string end, scans until an unquoted delimiter, and returns `strndup` of the token. If the input ends inside an open quote, it records `EINVAL`; if allocation fails, it records `ENOMEM`. On no-token or error, it nulls `pos` and returns `NULL`.

## State and persistence behavior

The tokenizer state is heap-allocated and advances monotonically through the caller-provided string. Returned tokens are independent heap strings owned by the caller. The module performs no I/O or persistence.

## Dependencies and integration points

It is used by `parse_opt.c` to split comma-delimited mount options such as SELinux contexts containing quoted commas. The opaque state is declared in `token.h`.

## Risks and edge cases

Quotes are toggled by every double quote; there is no escape handling. Empty tokens from repeated delimiters are skipped. A trailing open quote stops tokenization with `EINVAL`, which callers must check after the loop.

## Test signals

Tests should cover repeated delimiters, leading/trailing delimiters, quoted delimiters, unmatched quotes, allocation-failure behavior where practical, and nested independent tokenizers.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/token.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/token.h -->
# sources/user-network-fs/nfs-utils/utils/mount/token.h

## Purpose

`token.h` declares the tokenizer interface used by the mount option parser.

## Important APIs, types, and functions

It forward-declares `struct tokenizer_state` and declares `init_tokenizer`, `next_token`, `tokenizer_error`, and `end_tokenizer`.

## Control flow

There is no executable logic. The intended lifecycle is initialize, repeatedly call `next_token`, inspect `tokenizer_error`, then free with `end_tokenizer`.

## State and persistence behavior

State is opaque and owned by the tokenizer implementation. Returned tokens are heap strings, while the input string remains unmodified.

## Dependencies and integration points

`parse_opt.c` includes this header to obtain quote-aware comma splitting. The header has no external library dependencies beyond C declarations.

## Risks and edge cases

Callers must free each returned token and must not assume `NULL` means success without checking `tokenizer_error`.

## Test signals

API tests should verify proper lifecycle use and that the header can be included independently by C files needing tokenizer declarations.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/token.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/utils.c -->
# sources/user-network-fs/nfs-utils/utils/mount/utils.c

## Purpose

`utils.c` contains miscellaneous shared helpers for `mount.nfs` and `umount.nfs`: kernel mount-data version selection, verbose mount printing, usage text, mountpoint validation, and NFSv2/v3 unmount setup.

## Important APIs, types, and functions

`discover_nfs_mount_data_version` maps the running kernel release to legacy binary `nfs_mount_data` versions and indicates when string options are supported. `print_one`, `mount_usage`, and `umount_usage` handle user output. `chk_mountpoint` validates the local target. `nfs_umount23` parses the device name and option string, then invokes `nfs_umount_do_umnt`.

## Control flow

Version discovery reads `linux_version_code` and applies historical kernel thresholds. `chk_mountpoint` stats the mountpoint, requires a directory, and for non-root users checks execute permission. `nfs_umount23` parses `hostname:path`, splits mtab options with `po_split`, calls the network unmount helper, and frees all temporary allocations.

## State and persistence behavior

The file has no durable state. It reads kernel version and filesystem metadata, emits messages, and passes parsed options to the unmount RPC path. It relies on globals `verbose` and `progname` for output behavior.

## Dependencies and integration points

It depends on `version.h`, `parse_opt`, `parse_dev`, mount error reporting, network unmount helpers, NLS, and support headers for NFS mount constants. It is linked into the mount/umount utilities.

## Risks and edge cases

Kernel-version parsing failures return `UINT_MAX`, which suppresses old compatibility paths and treats the kernel as future/new. `nfs_umount23` tolerates option parse failure only by returning an error before RPC unmount. Access checks differ for real/effective root.

## Test signals

Tests should cover kernel threshold mappings, malformed kernel releases, non-directory mountpoints, permission failures for non-root users, malformed NFS device names, empty option strings, and option parsing failures on quoted strings.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/utils.h -->
# sources/user-network-fs/nfs-utils/utils/mount/utils.h

## Purpose

`utils.h` declares the shared mount/umount helper API.

## Important APIs, types, and functions

It includes `parse_opt.h` and declares `discover_nfs_mount_data_version`, `print_one`, usage printers, `chk_mountpoint`, and `nfs_umount23`.

## Control flow

No executable flow exists. The declarations support the command-line frontends and unmount path.

## State and persistence behavior

The header exposes functions that operate on process globals and parsed options, but contains no state itself.

## Dependencies and integration points

By including `parse_opt.h`, it makes the option-list type available to users of the utility helpers. It is part of the internal mount utility interface rather than a public library ABI.

## Risks and edge cases

The prototypes use mutable `char *` for some output strings, so callers must follow the implementation's ownership expectations. Header-level coupling to `parse_opt.h` can force rebuilds when the option API changes.

## Test signals

Compile tests should cover inclusion from both mount and umount translation units. ABI checks should ensure return-code conventions remain consistent with callers.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/version.h -->
# sources/user-network-fs/nfs-utils/utils/mount/version.h

## Purpose

`version.h` provides inline helpers for converting Linux kernel release strings into integer version codes used by compatibility decisions in mount utilities.

## Important APIs, types, and functions

`MAKE_VERSION(p, q, r)` packs major, minor, and patch into the traditional `major*65536 + minor*256 + patch` format. `linux_version_code` calls `uname`, parses the leading numeric release components with `sscanf`, and returns a packed code or `UINT_MAX` on failure.

## Control flow

`linux_version_code` obtains `struct utsname`, initializes minor/patch defaults to zero, parses at least the major version, and returns the packed result. Failure paths deliberately return `UINT_MAX` so future or unparseable kernels do not trigger old compatibility branches.

## State and persistence behavior

The helper has no persistent state. It reads the current kernel release via `uname` each time it is called.

## Dependencies and integration points

It depends on `<sys/utsname.h>`, `<limits.h>`, and `<stdio.h>`. `stropts.c`, `utils.c`, and `nfssvc.c` use it for kernel feature decisions.

## Risks and edge cases

Distribution release suffixes are accepted if the numeric prefix parses, but unusual releases that do not start with an integer are treated as very new. Very large components can overflow the packed format. Repeated calls do not cache results.

## Test signals

Tests can wrap or simulate `uname` parsing for releases like `2.6.32`, `5.15.0-custom`, major-only strings, invalid strings, and very large numeric components.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mountd/Makefile.am -->
# sources/user-network-fs/nfs-utils/utils/mountd/Makefile.am

## Purpose

`mountd/Makefile.am` defines the automake build and install behavior for the `rpc.mountd` service.

## Important APIs, types, and functions

It builds `mountd` from `mountd.c`, `mount_dispatch.c`, `rmtab.c`, `svc_run.c`, and `mountd.h`. It links export, NFS, misc, reexport, optional junction, BSD, tcp-wrappers, NSL, blkid, uuid, tirpc, pthread, and netlink libraries. Install hooks rename the binary to include `rpc.` and optional kernel prefix and create `rpc.mountd.8` manpage links.

## Control flow

Automake processes the file into build rules. Conditional `CONFIG_JUNCTION` adds junction support. Custom install/uninstall hooks rename executables and manage manpage symlinks after standard automake targets.

## State and persistence behavior

No runtime state is managed. Installation mutates files under `sbindir` and `man8dir`.

## Dependencies and integration points

The target includes support/export headers and links to the same support libraries that implement export authentication, cache upcalls, and reexport behavior consumed by `mountd.c`.

## Risks and edge cases

The rename hooks assume installed program names and manpage suffix transformations match automake behavior. Packaging systems that use staged installs must preserve `DESTDIR` behavior. Optional library ordering matters for systems with static or strict linkers.

## Test signals

Build tests should cover junction enabled/disabled, install and uninstall into a `DESTDIR`, prefixed binary names, manpage symlink creation, and link success with/without tcp-wrapper and netlink libraries.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mountd/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mountd/mount_dispatch.c -->
# sources/user-network-fs/nfs-utils/utils/mountd/mount_dispatch.c

## Purpose

`mount_dispatch.c` defines the RPC dispatch tables for the MOUNT protocol versions served by `rpc.mountd` and forwards accepted requests to the generic RPC dispatcher.

## Important APIs, types, and functions

It declares static `rpc_dentry` arrays for MNTv1, MNTv2, and MNTv3. The arrays map procedure numbers to service functions such as `mount_null`, `mount_mnt`, `mount_dump`, `mount_umnt`, `mount_export`, and v2 `mount_pathconf`. Public function `mount_dispatch` performs optional tcp-wrapper authorization and calls `rpc_dispatch`.

## Control flow

Incoming RPC requests enter `mount_dispatch`. If tcp-wrapper support is compiled in, the caller address is checked for service `mountd`; failed clients receive `AUTH_FAILED`. Accepted requests are dispatched by version/procedure lookup using the table array.

## State and persistence behavior

The file has only static dispatch metadata. It does not mutate persistent state; invoked service handlers in `mountd.c` and `rmtab.c` may update rmtab or export caches.

## Dependencies and integration points

It depends on `mountd.h`, `rpcmisc.h`, tirpc/SunRPC types, and optional `tcpwrapper.h`. It is registered as the dispatch callback when `mountd.c` creates listeners for MOUNTPROG versions.

## Risks and edge cases

Incorrect table sizes or procedure/type mappings would decode RPC arguments incorrectly. Tcp-wrapper failures occur before service-level authentication, so wrapper configuration can block otherwise valid exports. MNTv3 omits EXPORTALL and PATHCONF compared to earlier versions.

## Test signals

Tests should send NULL, MNT, DUMP, UMNT, UMNTALL, EXPORT, EXPORTALL, and PATHCONF calls for supported versions, plus invalid procedure/version calls and tcp-wrapper denial where compiled.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mountd/mount_dispatch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mountd/mountd.c -->
# sources/user-network-fs/nfs-utils/utils/mountd/mountd.c

## Purpose

`mountd.c` implements the `rpc.mountd` daemon: it authenticates NFS mount protocol requests, returns export root file handles, lists exports and mounts, manages daemon configuration, creates RPC listeners, and runs worker processes for kernel export cache upcalls.

## Important APIs, types, and functions

Service handlers include `mount_null_1_svc`, `mount_mnt_1_svc`, `mount_mnt_3_svc`, `mount_dump_1_svc`, `mount_umnt_1_svc`, `mount_umntall_1_svc`, `mount_export_1_svc`, `mount_exportall_1_svc`, and `mount_pathconf_2_svc`. Core helpers are `get_rootfh`, `set_authflavors`, `get_exportlist`, `read_mountd_conf`, `killer`, and `main`. Globals control reverse DNS, gid management, netlink, root credential application, cache address mode, HA callouts, thread count, port, descriptors, and enabled NFS versions.

## Control flow

Startup reads `nfs.conf`, parses command-line overrides, sets state paths for `etab` and `rmtab`, adjusts file descriptor limits, unregisters stale RPC registrations, creates MOUNT v1/v2/v3 listeners as configured, daemonizes if requested, opens cache channels, forks cache workers, initializes nfsd path and v4 client support, and enters `my_svc_run`. MNT requests resolve and authenticate the requested path, verify mountpoint constraints, optionally perform subpath lookup under client credentials, cache the export in the kernel, fetch a filehandle, add an rmtab entry, and return success. Export-list requests build a cached RPC export list from authenticated export structures.

## State and persistence behavior

Runtime state includes export cache state, worker processes, listener registrations, and static cached export lists keyed by auth reload counter. Persistent files include `etab` and `rmtab` under the configured state directory. Signal cleanup unregisters RPC services, removes lock files, and frees state path names.

## Dependencies and integration points

It depends on export authentication (`auth_reload`, `auth_authenticate`), kernel export cache helpers (`cache_export`, `cache_get_filehandle`, `cache_open`, `cache_fork_workers`), `nfsd_path` wrappers, credential helpers, config parsing, rpcmisc listener creation, and `rmtab.c`. It integrates with clients through MOUNT RPC and with the kernel nfsd export cache through support library channels.

## Risks and edge cases

Path handling is security-sensitive: symlink resolution, export path races, subpath credential checks, mountpoint enforcement, and crossmount checks all affect access. `get_exportlist` caches static RPC list memory and relies on auth reload counters. Multiworker signal handling kills process groups and waits for cache workers. Listener creation can silently produce no v2/v3 listeners except for a warning. Applying root credentials changes lookup semantics for subpaths.

## Test signals

Integration tests should cover authenticated/denied MNT v1/v3, filehandle sizes, subpath lookup with and without managed gids, crossmount denial, unmounted export rejection, PATHCONF authorization, export list pruning, rmtab add/remove, daemon foreground/background modes, version enable/disable flags, no-listener warnings, and signal cleanup.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mountd/mountd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mountd/mountd.h -->
# sources/user-network-fs/nfs-utils/utils/mountd/mountd.h

## Purpose

`mountd.h` declares the RPC service handlers and shared helper interfaces used across the `rpc.mountd` implementation.

## Important APIs, types, and functions

It includes RPC, NFS library, exportfs, and mount protocol headers. It defines `union mountd_arguments` and `union mountd_results` for dispatch storage. It declares mount service procedures, `mount_dispatch`, auth hooks, and rmtab list operations.

## Control flow

The header has no executable logic. Its declarations connect `mount_dispatch.c` table entries to `mountd.c` service handlers and `rmtab.c` state functions.

## State and persistence behavior

The header exposes functions that mutate export auth/cache and rmtab state, but it stores no state itself. Callers use the declared rmtab functions to update persistent mount records.

## Dependencies and integration points

It is the internal interface between the dispatch table, daemon implementation, and rmtab persistence module. It also establishes the argument/result union types expected by `rpc_dispatch`.

## Risks and edge cases

Any mismatch between union fields and dispatch table XDR types can corrupt request decoding. Because auth functions are declared here but implemented elsewhere, changes in export authentication contracts must be synchronized.

## Test signals

Build tests should compile all mountd translation units against this header. RPC dispatch tests should validate that each declared service handler matches its expected argument/result type.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mountd/mountd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mountd/rmtab.c -->
# sources/user-network-fs/nfs-utils/utils/mountd/rmtab.c

## Purpose

`rmtab.c` manages `rpc.mountd`'s remote mount table, recording which clients have mounted which exported paths and providing the MOUNT DUMP response list.

## Important APIs, types, and functions

Public functions are `mountlist_add`, `mountlist_del`, `mountlist_del_all`, and `mountlist_list`. Private `slink_safe_rename` preserves a symlinked rmtab path by renaming the temp file to the symlink target. `mountlist_freeall` releases cached RPC mountlist nodes.

## Control flow

Adds take an append lock, scan existing entries, increment count for duplicates, or append a new entry. Deletes take a write lock, stream existing entries to a temp file while decrementing/removing matches, and rename the temp file into place. UMNTALL canonicalizes the caller hostname, authenticates each path before removing it, and rewrites the table. Listing caches an in-memory mountlist until rmtab mtime changes.

## State and persistence behavior

Persistent state is the configured `rmtab.statefn` text file with client/path/count entries, guarded by `rmtab.lockfn` and rewritten through `rmtab.tmpfn`. HA callouts fire on mount and unmount count changes. The DUMP response list is cached statically in process memory.

## Dependencies and integration points

It depends on support `xio` rmtab helpers, file locks, host canonicalization, export authentication for UMNTALL, `ha-callout`, and `mountd.h`. `mountd.c` calls it after successful MNT and authenticated UMNT operations.

## Risks and edge cases

The symlink-safe rename follows only the destination symlink and trusts its target path. Cached mountlist invalidation uses mtime only. Reverse DNS during listing can fail and falls back to stored client text. If temp-file rewrite or rename fails, rmtab can become stale. Lock acquisition failures silently skip updates.

## Test signals

Tests should cover duplicate mount count increments, decrement-to-zero removal, symlinked rmtab paths, failed rename handling, UMNTALL auth filtering, reverse-resolve on/off, mtime cache reuse, allocation failures while listing, and HA callout arguments.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mountd/rmtab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mountd/svc_run.c -->
# sources/user-network-fs/nfs-utils/utils/mountd/svc_run.c

## Purpose

`svc_run.c` provides `rpc.mountd`'s custom RPC event loop, extending the usual `svc_run` behavior to process kernel export-cache file descriptors as well as RPC transports.

## Important APIs, types, and functions

Public function `my_svc_run` loops forever. On some 64-bit glibc builds, private `my_svc_getreqset` replaces buggy old `svc_getreqset` behavior by iterating fd masks and calling `svc_getreq_common`.

## Control flow

Each loop copies `svc_fdset`, passes it to `cache_process`, and, if selected RPC descriptors remain, dispatches them through `svc_getreqset`. A negative select/cache result logs an error and returns to the caller.

## State and persistence behavior

The loop operates on global SunRPC `svc_fdset` and kernel export cache descriptors managed elsewhere. It does not persist data directly.

## Dependencies and integration points

It depends on tirpc/SunRPC globals, `cache_process` from export support code, and `xlog`. `mountd.c` calls `my_svc_run` after listener and cache-worker initialization.

## Risks and edge cases

The loop exits on select errors, which causes `mountd.c` to log unexpected termination and exit. FD set size is capped at `FD_SETSIZE` in the compatibility path. Any cache processing bug can starve RPC dispatch or terminate the daemon.

## Test signals

Tests should exercise cache-only activity, RPC-only activity, mixed readiness, select error handling, high fd values near `FD_SETSIZE`, and the glibc compatibility path where available.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mountd/svc_run.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsd/Makefile.am -->
# sources/user-network-fs/nfs-utils/utils/nfsd/Makefile.am

## Purpose

`nfsd/Makefile.am` defines the automake build and install rules for the `rpc.nfsd` user-level control program.

## Important APIs, types, and functions

It builds `nfsd` from `nfsd.c` and `nfssvc.c`, installs `nfsd.man`, includes `nfssvc.h` as a non-installed header, and links against the support NFS library plus tirpc. Install hooks rename the binary with `rpc.` and optional kernel prefix and create matching manpage symlinks.

## Control flow

Automake generates normal build targets, then custom install/uninstall hooks rename executables and manage manpage links under `DESTDIR`.

## State and persistence behavior

No runtime state exists in the Makefile. Install rules mutate the target filesystem's sbin and man directories.

## Dependencies and integration points

The build links to `../../support/nfs/libnfs.la`, which provides NFS control macros and library helpers used by `nfsd.c` and `nfssvc.c`.

## Risks and edge cases

As with `mountd`, the install hooks assume automake naming behavior. Manpage symlink targets are derived by replacing `man` suffix with `8`, which depends on local file naming conventions.

## Test signals

Build and packaging tests should cover `make install DESTDIR=...`, uninstall, prefixed binary names, manpage links, and link success with tirpc enabled.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsd/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsd/nfsd.c -->
# sources/user-network-fs/nfs-utils/utils/nfsd/nfsd.c

## Purpose

`nfsd.c` is the command-line front end for starting, stopping, and configuring kernel NFS server threads. The kernel performs NFS serving; this program configures versions, protocols, sockets, RDMA, grace/lease times, scope, and thread count.

## Important APIs, types, and functions

`main` owns all behavior. `read_nfsd_conf` initializes config and debug settings. The option parser handles host, scope, version enable/disable, TCP/UDP, port, RDMA, grace time, lease time, syslog, and debug. It calls `nfssvc_get_minormask`, `nfssvc_mount_nfsdfs`, `nfssvc_inuse`, `nfssvc_setvers`, `nfssvc_set_time`, `nfssvc_set_sockets`, `nfssvc_set_rdmaport`, and `nfssvc_threads`.

## Control flow

Startup reads defaults from `nfs.conf`, folds in command-line options, validates requested version/protocol combinations, changes into `NFS_STATEDIR`, ensures nfsdfs is mounted, and checks whether nfsd sockets are already configured. For a fresh start it writes version and timeout settings first, optionally unshares UTS namespace and sets hostname scope, opens requested TCP/UDP sockets per host and hands them to the kernel, optionally requests RDMA, then closes inherited fds and writes the desired thread count. If thread count is zero, it skips socket setup and only changes thread count.

## State and persistence behavior

Persistent server state lives in the kernel and procfs/nfsdfs files, not in this process. The program may alter the UTS namespace hostname for NFSv4 scope when `--scope` is used. It switches logging to syslog before closing standard descriptors.

## Dependencies and integration points

It depends on config parsing, support NFS control bit macros, `nfssvc.c`, `xlog`, `basename`, sockets, and Linux `unshare(CLONE_NEWUTS)`. It integrates directly with `/proc/fs/nfsd` through `nfssvc.c`.

## Risks and edge cases

Version/minor-version bit logic is subtle, especially force-setting v4.0 on newer kernels. NFSv4 requires TCP and is rejected without it. Existing nfsd sockets prevent reconfiguration beyond thread count. Host list reallocation has precedence-sensitive sizing code. Closing all fds before spawning threads protects the kernel but makes late stderr diagnostics unavailable.

## Test signals

Tests should cover config and CLI precedence, enabling/disabling v3/v4 minors, all-versions-disabled rejection, v4-without-TCP rejection, `nrservs=0`, existing nfsd in-use path, invalid ports and times, host lists, RDMA option forms, scope setup failures, and socket failure propagation.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsd/nfsd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsd/nfssvc.c -->
# sources/user-network-fs/nfs-utils/utils/nfsd/nfssvc.c

## Purpose

`nfssvc.c` contains the low-level procfs/nfsdfs operations that let `rpc.nfsd` configure the kernel NFS server.

## Important APIs, types, and functions

Public functions include `nfssvc_mount_nfsdfs`, `nfssvc_inuse`, `nfssvc_set_sockets`, `nfssvc_set_rdmaport`, `nfssvc_set_time`, `nfssvc_get_minormask`, `nfssvc_setvers`, `nfssvc_threads`, and `nfssvc_setfh_key` as declared in the header. Private `nfssvc_setfds` creates sockets and writes their fd numbers to `/proc/fs/nfsd/portlist`; `nfssvc_print_vers` formats version tokens.

## Control flow

`nfssvc_mount_nfsdfs` checks for the `threads` file and attempts a `mount -t nfsd` if missing. `nfssvc_inuse` reads `portlist` to determine whether sockets are already configured. Socket setup resolves host/port, creates TCP/UDP IPv4/IPv6 sockets, sets IPv6-only and reuseaddr options where needed, binds/listens, then writes each fd number to `portlist` for kernel adoption. Version setup writes plus/minus version tokens to `versions`. Thread setup writes the requested count to `threads`.

## State and persistence behavior

State is kernel-owned and exposed via `/proc/fs/nfsd`. The module writes sockets, RDMA port requests, grace/lease times, lockd grace period, supported versions, and thread counts. A static scratch `buf[128]` is reused across operations.

## Dependencies and integration points

It depends on Linux nfsdfs paths, socket APIs, `getaddrinfo`, support NFS macros, `version.h`, and `xlog`. `nfsd.c` is its primary caller.

## Risks and edge cases

`nfssvc_get_minormask` reads into a 128-byte buffer and then writes `ptr[size] = '\0'`; if `read` returns the full buffer length, this is an out-of-bounds write. Socket setup returns success if at least one socket was handed off, even if later addresses fail. The fallback `system("/bin/mount ...")` ignores direct return status. Version formatting depends on kernel version for v4.0 syntax.

## Test signals

Tests should cover nfsdfs absent/present, portlist read states, IPv4/IPv6 socket handoff, partial address failures, service-name fallback from `nfs` to `2049`, RDMA port names and numbers, version-string formatting around Linux 4.11, minor mask parsing at buffer boundaries, grace/lease writes, and thread-file fallback.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsd/nfssvc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsd/nfssvc.h -->
# sources/user-network-fs/nfs-utils/utils/nfsd/nfssvc.h

## Purpose

`nfssvc.h` declares the internal service-control interface used by `rpc.nfsd`.

## Important APIs, types, and functions

It declares functions for mounting nfsdfs, checking active sockets, setting sockets and RDMA port, setting grace/lease times, configuring NFS major/minor versions, changing kernel thread count, reading minor-version masks, and setting a filehandle key.

## Control flow

No executable flow exists. `nfsd.c` calls these functions in a strict order: mount nfsdfs, check in-use status, set versions/timeouts, set sockets/RDMA, then set threads.

## State and persistence behavior

The declared functions mutate kernel nfsd procfs state. The header itself holds no state.

## Dependencies and integration points

It is the boundary between argument/config parsing in `nfsd.c` and procfs writes in `nfssvc.c`.

## Risks and edge cases

The header declares `nfssvc_setfh_key`, but this work-item source set does not include an implementation in `nfssvc.c`, so link coverage elsewhere is required. Callers must understand which functions return errno-style values and which only log.

## Test signals

Compile/link tests should ensure all declared functions are defined in the complete build. Unit tests should verify caller handling of return values.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsd/nfssvc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/Makefile.am -->
# sources/user-network-fs/nfs-utils/utils/nfsdcld/Makefile.am

## Purpose

`nfsdcld/Makefile.am` builds the `nfsdcld` NFSv4 client-tracking daemon.

## Important APIs, types, and functions

It builds `nfsdcld` from `nfsdcld.c`, `sqlite.c`, and `legacy.c`; installs `nfsdcld.man`; defines `_LARGEFILE64_SOURCE`; declares internal headers; and links support NFS, libevent, sqlite, and libcap.

## Control flow

Automake turns these declarations into compile/link/install rules. There are no custom install rename hooks in this file.

## State and persistence behavior

No runtime state is managed by the Makefile. The linked daemon manages SQLite and legacy recovery directories at runtime.

## Dependencies and integration points

The link dependencies reflect runtime behavior: libevent for pipe events, sqlite for persistent tracking, libcap for capability dropping, and support NFS for shared constants/helpers.

## Risks and edge cases

Builds without the expected libevent/sqlite/libcap flags will fail. `_LARGEFILE64_SOURCE` must match any file-offset assumptions in sqlite or system headers.

## Test signals

Build tests should verify daemon linking with and without capability headers and that generated distribution archives include the manpage and internal headers as expected.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/cld-internal.h -->
# sources/user-network-fs/nfs-utils/utils/nfsdcld/cld-internal.h

## Purpose

`cld-internal.h` defines private shared state for the `nfsdcld` daemon and SQLite backend.

## Important APIs, types, and functions

It computes `UPCALL_VERSION` from `CLD_UPCALL_VERSION`. `struct cld_client` stores the cld pipe fd, libevent event pointer, and a union of v1/v2 kernel message formats. It declares global `current_epoch`, `recovery_epoch`, `first_time`, `num_cltrack_records`, and `num_legacy_records`.

## Control flow

No executable flow exists. The data layout lets the event-loop code read either upcall format and lets `sqlite.c` update epoch globals.

## State and persistence behavior

The declared globals mirror SQLite database state and first-time migration status during daemon runtime. Persistent copies live in the SQLite `grace` and `parameters` tables.

## Dependencies and integration points

It depends on `cld.h` message definitions and libevent's `struct event` being visible through including translation units. It is shared by `nfsdcld.c` and `sqlite.c`.

## Risks and edge cases

The message union must stay large enough and aligned for all supported kernel upcall versions. Globals make only one active database/daemon context practical per process.

## Test signals

Compile tests should cover builds with upcall v1 and v2. Runtime tests should verify v1/v2 message sizing and epoch global updates after database startup and grace transitions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/cld-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/legacy.c -->
# sources/user-network-fs/nfs-utils/utils/nfsdcld/legacy.c

## Purpose

`legacy.c` migrates and cleans the older kernel NFSv4 recovery directory format for `nfsdcld` first-time upgrades.

## Important APIs, types, and functions

`legacy_load_clients_from_recdir` reads `/proc/fs/nfsd/nfsv4recoverydir`, opens the directory it names, prefixes each legacy entry with `hash:`, includes the NUL terminator, and inserts it into the current SQLite client table. `legacy_clear_recdir` reads the same proc file and removes each child directory after the first grace completes.

## Control flow

Both functions open the proc file, read a newline-terminated directory path, trim it, and iterate non-dot entries. Loading formats each entry into a bounded buffer and calls `sqlite_insert_client`. Clearing constructs full child paths and calls `rmdir`.

## State and persistence behavior

It reads kernel-advertised legacy recovery directory state and writes migrated records to `nfsdcld` SQLite. Cleanup removes legacy recovery subdirectories best-effort. Record counts are returned by incrementing the caller's integer.

## Dependencies and integration points

It depends on procfs nfsd recovery directory reporting, `sqlite_insert_client`, NFSv4 opaque limits from `cld.h`, and `xlog`. `sqlite_prepare_dbh` invokes migration when the database `first_time` parameter is set; `cld_gracedone` invokes cleanup after the first grace.

## Risks and edge cases

The code skips entries that exceed `NFS4_OPAQUE_LIMIT` after `hash:` prefixing. It assumes legacy entries are direct child directories and uses `rmdir`, so non-empty or non-directory entries remain. Proc-file reads require a newline; missing newline silently aborts.

## Test signals

Tests should cover missing proc file, invalid/no-newline path, empty recovery dir, dot entries, long names, sqlite insert failures, count increments, cleanup failures, and interaction with first-time migration from cltrack records.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/legacy.h -->
# sources/user-network-fs/nfs-utils/utils/nfsdcld/legacy.h

## Purpose

`legacy.h` declares the legacy recovery-directory migration helpers used by `nfsdcld`.

## Important APIs, types, and functions

It declares `legacy_load_clients_from_recdir(int *)` and `legacy_clear_recdir(void)`.

## Control flow

No executable flow exists. Callers use the load helper during first-time database preparation and the clear helper after first grace completion.

## State and persistence behavior

The declared functions read and remove legacy recovery directory state and may insert records into SQLite through `legacy.c`.

## Dependencies and integration points

It is included by `nfsdcld.c` and `sqlite.c`, connecting daemon grace handling and database initialization to legacy on-disk cleanup.

## Risks and edge cases

The header does not describe ownership or error reporting; the implementation logs and returns mostly through side effects, so callers cannot distinguish many failure classes.

## Test signals

Build tests should ensure both daemon and SQLite modules include the header and agree on the count-pointer contract.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/legacy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/nfsdcld.c -->
# sources/user-network-fs/nfs-utils/utils/nfsdcld/nfsdcld.c

## Purpose

`nfsdcld.c` implements the long-running NFSv4 client-tracking daemon that communicates with the kernel over the nfsd cld pipe, persists client IDs in SQLite, sends recovery records during grace, and handles first-time migration from older trackers.

## Important APIs, types, and functions

Key helpers include `cld_set_caps`, `cld_pipe_open`, `cld_inotify_setup`, `cld_pipe_init`, `cld_check_grace_period`, `cld_message_size`, command handlers `cld_create`, `cld_remove`, `cld_check`, `cld_gracedone`, `cld_gracestart`, `cld_get_version`, `cld_not_implemented`, `cld_pipe_read_msg`, and event callback `cldcb`. `main` handles config, daemonization, capability dropping, database setup, pipe event registration, signals, and cleanup.

## Control flow

Startup reads `nfs.conf`, accepts foreground/debug/pipefs/storage options, builds `<pipefs>/nfsd/cld`, daemonizes unless foreground, drops all capabilities, checks storage writability, flags old kernels before 4.20, opens/prepares SQLite, installs inotify for the pipe directory, opens the cld pipe if present, and enters libevent dispatch. Pipe events read a message header and body, switch on command, update SQLite or iterate recovery records, write a downcall response, and re-add the event. If the pipe disappears or writes fail, the daemon reopens it.

## State and persistence behavior

Persistent state is `main.sqlite` under the storage directory, with current/recovery epoch tables and migration parameters. Runtime state includes pipe fd/event, inotify fd/event, signal state, and epoch globals. First-time grace completion can delete old cltrack records and clear legacy recovery directories before marking `first_time=0`.

## Dependencies and integration points

It depends on libevent, inotify, libcap, `cld.h` kernel upcall formats, procfs `v4_end_grace` for old kernels, SQLite backend, legacy migration helpers, config parsing, and `version.h`. It integrates with the kernel through rpc_pipefs and with older tracking mechanisms through migration.

## Risks and edge cases

Message size handling exits fatally on unknown versions. V2 create stores principal hashes, but remove/check use the v1 name field, so kernel message layout compatibility is critical. Old-kernel grace detection reads a single proc byte and synthesizes `sqlite_grace_start`. Many pipe write failures trigger reopen but not command replay. Capability dropping can make storage misownership fatal later.

## Test signals

Tests should cover v1/v2 upcalls, create/remove/check/gracestart/gracedone/getversion, pipe absent then created, pipe reopen after write failure, unsupported command response, old-kernel grace detection, first-time migration cleanup, storage permission warnings, signal shutdown, and recovery iteration with principal hashes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/nfsdcld.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/sqlite.c -->
# sources/user-network-fs/nfs-utils/utils/nfsdcld/sqlite.c

## Purpose

`nfsdcld/sqlite.c` implements the SQLite persistence backend for the daemon's NFSv4 client recovery database. It manages schema creation/upgrades, epoch transitions, client insert/remove/check operations, recovery iteration, and migration from `nfsdcltrack` and legacy recovery directories.

## Important APIs, types, and functions

Public APIs include `sqlite_prepare_dbh`, `sqlite_insert_client`, `sqlite_insert_client_and_princhash`, `sqlite_remove_client`, `sqlite_check_client`, `sqlite_grace_start`, `sqlite_grace_done`, `sqlite_iterate_recovery`, `sqlite_delete_cltrack_records`, `sqlite_first_time_done`, and `sqlite_shutdown`. Schema helpers handle versions 1-4, table-name repair, attached cltrack database copying, and first-time flags.

## Control flow

Preparation opens `<storagedir>/main.sqlite`, creates the directory if needed, sets a busy timeout, detects schema version, initializes or upgrades to v4, loads current/recovery epochs, checks table names under an exclusive transaction, and performs first-time migration. Grace start either advances `current`/`recovery` and creates a new `rec-...` table, or clears the current table when restarting while already in grace. Grace done clears recovery, drops the recovery table, and updates globals. Check queries the recovery table and reinserts reclaimed clients into the current epoch.

## State and persistence behavior

The database has `parameters`, `grace`, and per-epoch `rec-%016"PRIx64"` tables with `id` and optional `princhash` blobs. `current_epoch`, `recovery_epoch`, and `first_time` globals mirror database values. Migration can attach the old cltrack database, copy its `clients` table, load legacy recdir entries, and later delete migrated old records.

## Dependencies and integration points

It depends on sqlite3, config parsing for old cltrack storage location, `cld-internal.h` globals/message buffers, legacy migration, NFS4 opaque limits, and `xlog`. `nfsdcld.c` calls it for every kernel upcall.

## Risks and edge cases

Dynamic SQL uses formatted table names and fixed `PATH_MAX` buffers; bounds checks are present but numerous. `sqlite_iterate_recovery` copies principal hash bytes using `SHA256_DIGEST_SIZE` when any bytes exist, without first ensuring the SQLite blob length is at least that size. Some functions return sqlite codes while callers map them to generic kernel errors. Schema repair only accepts short table names for current or recovery epochs.

## Test signals

Tests should cover new DB init, upgrades from v1/v2/v3, concurrent setup races, first-time cltrack and legacy migration, epoch advance and restart-in-grace, check success/failure, principal hash storage/iteration, table-name repair, busy database handling, attach/detach failures, grace done table drops, and shutdown idempotence.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/sqlite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/sqlite.h -->
# sources/user-network-fs/nfs-utils/utils/nfsdcld/sqlite.h

## Purpose

`nfsdcld/sqlite.h` declares the SQLite backend interface for the client-tracking daemon.

## Important APIs, types, and functions

It forward-declares `struct cld_client` and declares database preparation, client insert/remove/check, insert with Kerberos principal hash, grace start/done, recovery iteration callback, old cltrack cleanup, first-time completion, and shutdown.

## Control flow

No executable flow exists. The intended sequence is prepare database at daemon startup, service create/remove/check/grace commands, optionally iterate recovery clients during `Cld_GraceStart`, then shut down.

## State and persistence behavior

The declared functions operate on a process-global sqlite handle and epoch globals. Persistent state is in `main.sqlite`.

## Dependencies and integration points

The header is included by `nfsdcld.c`, `legacy.c`, and `sqlite.c`. It abstracts SQL details away from pipe command handling.

## Risks and edge cases

Return values mix negative errno-style errors and sqlite result codes depending on function, so callers must preserve existing mapping behavior. The callback form of `sqlite_iterate_recovery` mutates the supplied client message buffer.

## Test signals

API tests should validate return-code mapping and callback behavior for recovery iteration, including empty and multi-record recovery tables.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/sqlite.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcltrack/Makefile.am -->
# sources/user-network-fs/nfs-utils/utils/nfsdcltrack/Makefile.am

## Purpose

`nfsdcltrack/Makefile.am` builds the older `nfsdcltrack` kernel usermode-helper client tracking program.

## Important APIs, types, and functions

It optionally installs under `/sbin` when `CONFIG_SBIN_OVERRIDE` is true because the kernel knows that helper path. It builds `nfsdcltrack` from `nfsdcltrack.c` and `sqlite.c`, installs the manpage, declares `sqlite.h`, defines `_LARGEFILE64_SOURCE`, and links support NFS, sqlite, and libcap.

## Control flow

Automake turns the declarations into build/install rules. There are no custom post-install hooks beyond the conditional `sbindir` override.

## State and persistence behavior

The Makefile has no runtime state. The built helper manages SQLite state at runtime.

## Dependencies and integration points

The `/sbin` override is an integration point with kernel helper invocation. Libraries match helper needs: sqlite for storage and libcap for privilege reduction.

## Risks and edge cases

Installing outside the path expected by older kernels breaks upcalls. Conditional automake syntax is deliberately written to avoid automake disabling the override, so refactors should be cautious.

## Test signals

Build/install tests should verify install location with `CONFIG_SBIN_OVERRIDE` true/false, link dependencies, manpage distribution, and helper availability at the configured kernel path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcltrack/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcltrack/nfsdcltrack.c -->
# sources/user-network-fs/nfs-utils/utils/nfsdcltrack/nfsdcltrack.c

## Purpose

`nfsdcltrack.c` implements the older command-style NFSv4 client tracking helper invoked by the kernel. It decodes hex client IDs, updates an SQLite database, supports reclaim checks and grace completion, and bridges legacy recovery-directory state.

## Important APIs, types, and functions

Commands are described by `struct cltrack_cmd`: `init`, `create`, `remove`, `check`, and `gracedone`. Helpers include `hex_to_bin`, `hex_str_to_bin`, `cltrack_set_caps`, `cltrack_lift_grace_period`, `cltrack_get_grace_start`, `cltrack_reclaims_complete`, `cltrack_client_has_session`, command handlers, legacy check/cleanup helpers, config reading, and `main`.

## Control flow

`main` reads config, parses debug/foreground/storage options, opens logging, drops capabilities, locates the requested command, validates required arguments, and invokes the command handler. `init` prepares SQLite and may lift grace if all reclaims are complete. `create`, `remove`, and `check` decode the hex client ID into a binary blob, then call SQLite. `check` falls back to a legacy recovery directory environment variable if the DB lookup fails. `gracedone` parses a grace start time, deletes unreclaimed records, and cleans legacy directories.

## State and persistence behavior

Persistent state is `main.sqlite` under the configured storage directory, with a `clients` table storing client ID blobs, timestamps, and `has_session`. The helper also writes `Y` to `/proc/fs/nfsd/v4_end_grace` to lift grace when conditions allow. Legacy directory cleanup uses environment-provided paths from the kernel.

## Dependencies and integration points

It depends on kernel-provided command-line arguments and environment variables (`NFSDCLTRACK_GRACE_START`, `NFSDCLTRACK_CLIENT_HAS_SESSION`, legacy paths), SQLite backend, libcap, config parsing, xlog, and procfs end-grace control.

## Risks and edge cases

`hex_str_to_bin` can partially clobber the destination before reporting `-ENOBUFS`. Capability dropping occurs before database access, so storage ownership matters. Invalid or missing grace-start env vars prevent early grace lifting. Legacy check removes recovery directories after inserting records, so failures can leave duplicate recovery sources.

## Test signals

Tests should cover each command, invalid commands returning `-ENOSYS`, missing arguments, odd/non-hex/too-long client IDs, storage permission cases, session and grace env vars, legacy fallback success/failure, grace lifting, unreclaimed pruning, and foreground/syslog behavior.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcltrack/nfsdcltrack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcltrack/sqlite.c -->
# sources/user-network-fs/nfs-utils/utils/nfsdcltrack/sqlite.c

## Purpose

`nfsdcltrack/sqlite.c` provides SQLite storage for the older kernel usermode-helper client tracker.

## Important APIs, types, and functions

Public functions are `sqlite_prepare_dbh`, `sqlite_insert_client`, `sqlite_remove_client`, `sqlite_check_client`, `sqlite_remove_unreclaimed`, and `sqlite_query_reclaiming`. Private helpers create the storage directory, query schema version, initialize schema v2, and upgrade v1 to v2 by adding `has_session`.

## Control flow

Preparation opens `<storagedir>/main.sqlite`, creates the directory if open fails, sets busy timeout, then initializes or upgrades the schema. Inserts use `INSERT OR REPLACE` into `clients`, setting `time` to either zero or current epoch seconds and storing the session flag. Checks verify record existence and update timestamp only for NFSv4.0 clients. Grace completion deletes records with timestamps older than the supplied grace start. Reclaim query counts records that are older than grace start or lack sessions.

## State and persistence behavior

The database has `parameters` and `clients` tables. Client rows contain binary `id`, integer `time`, and integer `has_session`. The sqlite handle and SQL scratch buffer are process-global for the helper invocation.

## Dependencies and integration points

It depends on sqlite3, Linux `PATH_MAX`, xlog, and the command helper in `nfsdcltrack.c`. `nfsdcld/sqlite.c` can later attach this database and migrate its `clients` records.

## Risks and edge cases

Errors can be raw sqlite codes or negative errno values. `sqlite_query_reclaiming` returns sqlite error codes as nonzero counts to callers, which conservatively prevents grace lifting. No explicit shutdown closes `dbh` in this file, relying on process exit. Time is sourced from SQLite `strftime`.

## Test signals

Tests should cover new DB creation, v1 upgrade, unsupported schema rejection, inserts with current/zero time, session vs non-session check timestamp behavior, removal, pruning by grace time, reclaim counts, busy timeout behavior, and storage path errors.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcltrack/sqlite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcltrack/sqlite.h -->
# sources/user-network-fs/nfs-utils/utils/nfsdcltrack/sqlite.h

## Purpose

`nfsdcltrack/sqlite.h` declares the SQLite API for the older `nfsdcltrack` helper.

## Important APIs, types, and functions

It declares preparation, client insert/remove/check, removal of unreclaimed clients by grace time, and query for still-reclaiming clients.

## Control flow

No executable flow exists. Command handlers prepare the database first, then call the appropriate operation for create/remove/check/gracedone/init.

## State and persistence behavior

The declared functions operate on a process-global sqlite handle and persistent `clients` table in the configured storage directory.

## Dependencies and integration points

The header is included by `nfsdcltrack.c` and its SQLite implementation. It uses `bool`, `size_t`, `uint64_t`, and `time_t`, so including translation units must provide the relevant standard headers before or through their include chain.

## Risks and edge cases

The API does not expose a shutdown call; short-lived helper process exit closes resources. Return-code conventions require callers to translate sqlite failures into kernel-facing errors.

## Test signals

Compile tests should verify required type visibility. API tests should cover check behavior with `has_session` true and false and grace-time pruning.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcltrack/sqlite.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdctl/Makefile.am -->
# sources/user-network-fs/nfs-utils/utils/nfsdctl/Makefile.am

## Purpose

`nfsdctl/Makefile.am` defines the build for the newer `nfsdctl` control utility.

## Important APIs, types, and functions

It builds `nfsdctl` from `nfsdctl.c`, declares `nfsdctl.h`, installs `nfsdctl.8`, applies libnl/libgenl/readline CFLAGS, and links support NFS plus libnl, libgenl, and readline libraries.

## Control flow

Automake expands the declarations into normal build and install rules. There are no custom install hooks in this file.

## State and persistence behavior

The Makefile stores no runtime state. The compiled utility likely controls kernel/server state through netlink and interactive readline support, but those sources are outside this work item.

## Dependencies and integration points

The build dependencies indicate integration with generic netlink and optional interactive command handling. The support NFS library provides shared NFS constants/helpers.

## Risks and edge cases

Link ordering and availability of libnl3, libnl-genl3, and readline determine build success. Distribution must include `nfsdctl.8` and keep `nfsdctl.h` in sync with `nfsdctl.c`.

## Test signals

Build tests should cover library detection flags, successful link, manpage installation, and builds in environments without readline if configure supports disabling it.

<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdctl/Makefile.am -->

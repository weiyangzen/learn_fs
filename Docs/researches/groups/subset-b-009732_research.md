# Research: subset-b-009732

Grouped research for nfs-utils blkmapd, exportd/exportfs, and gssd source files. Each section is source-tree aligned and bounded by reconciliation markers for per-file extraction.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/blkmapd/device-discovery.c -->
# sources/user-network-fs/nfs-utils/utils/blkmapd/device-discovery.c

## Purpose
This is the `blkmapd` daemon entry point. It discovers local block devices for pNFS block layout use, watches `rpc_pipefs` for the kernel's `nfs/blocklayout` pipe, receives mount/unmount device requests, and replies with either created device-mapper major/minor numbers or an error status.

## APIs And Control Flow
Key routines are `bl_discover_devices`, `bl_disk_inquiry_process`, `bl_event_helper`, and `main`. Discovery clears `visible_disk_list`, reads `/proc/partitions`, keeps only whole block devices present under `/sys/block`, and calls `bl_add_disk` for `/dev/<name>`. `bl_add_disk` opens the device, determines size, reads SCSI serial/path state through `device-inq.c`, groups paths by serial, and chooses the highest priority path: pseudo, active, then passive. The event loop uses `inotify` for pipefs topology changes and `select` for the pipe itself. Mount requests call `process_deviceinfo`; unmount requests call `dm_device_remove_all`.

## State, Dependencies, And Integration
Persistent process state includes pipe paths, watch descriptors, pipe fd, pidfile fd, and the global `visible_disk_list`. It depends on Linux block ioctls, inotify, syslog, `/proc/partitions`, `/sys/block`, `/dev`, rpc_pipefs, libdevmapper helpers, and nfs-utils config parsing for `pipefs-directory`.

## Risks And Test Signals
Risks include fallback serials based on filenames causing unstable identity, a possible null dereference when serial reading fails but later serial comparison assumes `serial`, pidfile locking in the parent rather than daemon child, fixed pipe message framing with poor resynchronization after short reads, and path priority depending on full rediscovery timing. Test with fake pipefs create/delete events, mount/unmount pipe messages, missing pipe directories, multipath devices, SCSI inquiry failures, and daemon/foreground/pidfile modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/blkmapd/device-discovery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/blkmapd/device-discovery.h -->
# sources/user-network-fs/nfs-utils/utils/blkmapd/device-discovery.h

## Purpose
This header defines the shared block-layout discovery contract used by `blkmapd` source files: decoded block volume structures, disk identity structures, pipe message formats, XDR-style decode helpers, public daemon functions, and logging macros.

## APIs And Types
Important types are `enum blk_vol_type`, `struct bl_volume`, `struct bl_sig`, `struct bl_disk`, `struct bl_disk_path`, `struct bl_serial`, `struct bl_dev_msg`, and `struct bl_pipemsg_hdr`. Volume types model simple devices, slices, concats, stripes, and pseudo devices. Disk offsets and lengths are stored in 512-byte sectors. `BLK_READBUF`, `READ32`, `READ64`, and `READ_SECTOR` are decode macros layered on `blk_overflow`. Public functions connect the modules: `bl_discover_devices`, `process_deviceinfo`, `dm_device_create`, `dm_device_remove_all`, SCSI serial helpers, and `atomicio`.

## State, Dependencies, And Integration
The header exposes `visible_disk_list` as global shared daemon state and assumes networking byte-order helpers, syslog, device major/minor types, and block-device semantics. It is the integration point between discovery, SCSI inquiry, pNFS deviceinfo decoding, and device-mapper creation.

## Risks And Test Signals
Risks include macro-based decode control flow that jumps to `out_err`, flexible-array `struct bl_dev_id` layout assumptions over raw SCSI buffers, sector-alignment rejection in `READ_SECTOR`, and exposing mutable global disk state. Tests should cover malformed short buffers, unaligned 64-bit sector fields, maximum signature component counts, and compile coverage for all modules including this header.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/blkmapd/device-discovery.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/blkmapd/device-inq.c -->
# sources/user-network-fs/nfs-utils/utils/blkmapd/device-inq.c

## Purpose
This file performs SCSI inquiry operations used by `blkmapd` to identify block devices and decide active/passive path state. It converts VPD pages into `struct bl_serial` identities and path states consumed by discovery and deviceinfo matching.

## APIs And Control Flow
`bl_create_scsi_string` allocates a serial object with inline byte storage, and `bl_free_scsi_string` frees it. `bldev_inquire_page` sends an SG_IO INQUIRY command for a standard or EVPD page. `bldev_inquire_pages` first reads a default 255-byte buffer, validates the returned page code, computes the full response length, reallocates up to `MX_ALLOC_LEN`, and retries when needed. `bldev_read_ap_state` reads EMC page `0xc0` and treats low status as passive, otherwise active. `bldev_read_serial` reads VPD page `0x83`, scans designator descriptors, prioritizes NAA/EUI/T10/vendor identifiers, and falls back to the filename when no usable serial is present.

## State, Dependencies, And Integration
There is only static SG timeout state. Dependencies are Linux SCSI SG_IO, SPC VPD page formats, syslog logging macros from `device-discovery.h`, and callers that keep the returned serial until the disk list is released.

## Risks And Test Signals
Risks include signed `char` arithmetic when computing page length, trusting descriptor lengths within one buffer, treating unknown devices as active, and filename fallback causing identity changes across udev naming. Tests should mock SG_IO pages for page `0x83`, page `0xc0`, oversized length rejection, zero-length descriptors, and inquiry failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/blkmapd/device-inq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/blkmapd/device-process.c -->
# sources/user-network-fs/nfs-utils/utils/blkmapd/device-process.c

## Purpose
This file decodes XDR-like pNFS block layout deviceinfo sent by the kernel, maps server-provided signatures to discovered local disks, builds an internal `bl_volume` graph, and asks `dm-device.c` to materialize the final block device.

## APIs And Control Flow
`blk_overflow` bounds-checks decode cursor movement. `decode_blk_signature` reads signature components and points them directly into the input buffer. `verify_sig` opens a candidate disk and requires every component to match at absolute or end-relative offsets. `map_sig_to_device` scans `visible_disk_list` and fills simple volume device and size fields. `decode_blk_volume` handles simple, slice, stripe, and concat volumes; slices read offset/size and one prior volume; stripes validate power-of-two stripe units and equal subvolume sizes; concats sum subvolume sizes. `process_deviceinfo` reads the volume count, allocates the volume array and pointer arena, decodes all volumes in order, verifies complete consumption, calls `dm_device_create`, and returns major/minor.

## State, Dependencies, And Integration
The module depends on `visible_disk_list`, device paths chosen by discovery, network-byte-order fields, Linux major/minor macros, and device-mapper creation. It does not persist state itself; created DM devices are tracked by `dm-device.c`.

## Risks And Test Signals
Risks include raw input pointer aliasing, potentially insufficient pointer-arena sizing if future volume rules change, O(n disks * signatures) scanning, read/lseek assumptions on block devices, and rejecting valid but non page-size stripe units per DM constraints. Tests should fuzz short buffers, invalid indices, negative offsets, unmatched signatures, mixed stripe sizes, and successful simple/slice/concat/stripe mappings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/blkmapd/device-process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/blkmapd/dm-device.c -->
# sources/user-network-fs/nfs-utils/utils/blkmapd/dm-device.c

## Purpose
This file translates decoded pNFS block volume graphs into Linux device-mapper devices and removes them later. It is the backend that turns simple, slice, concat, and stripe layout descriptions into `/dev/mapper/pnfs_vol_N` devices.

## APIs And Control Flow
Internal helpers maintain linked lists of DM target table rows and tracked `dm_tree` objects. `dm_device_create_mapped` creates a DM device, sets its generated name, adds all targets, runs the task, updates nodes, and returns `MKDEV(major, minor)`. `dm_device_remove` finds a mapper device name by dev number before removing it. `dm_device_remove_all` maps a kernel-provided major/minor pair to a tracked DM tree, removes the root, deactivates children, updates nodes, and drops the cached tree. `dm_device_create` walks decoded volumes in order, passing through simple devices and creating linear or striped targets for slices, concats, and stripes. Each created pseudo volume rewrites the current volume to `BLOCK_VOLUME_PSEUDO`.

## State, Dependencies, And Integration
Global state includes `dev_count` for generated names and `bl_tree_head` for removal tracking. It depends on libdevmapper, `/dev/mapper`, Linux device number macros, and the decoded `bl_volume` graph from `device-process.c`.

## Risks And Test Signals
Risks include fixed target parameter buffers, generated-name races with other processes, removal limited to devices tracked in this process, sparse error cleanup, `del_from_bl_dm_tree` predecessor handling, and assumptions that subvolumes are already simple/pseudo. Test with mocked libdevmapper for creation failure, name collision, concat table offsets, stripe parameter formatting, child cleanup, and process restart before unmount.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/blkmapd/dm-device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/exportd/Makefile.am -->
# sources/user-network-fs/nfs-utils/utils/exportd/Makefile.am

## Purpose
This automake file builds and installs the NFSv4 `exportd` daemon and its man page. It wires the program to nfs-utils support libraries and preserves the project convention of installing daemons with an `nfsv4.` prefix plus optional kernel prefix.

## APIs And Build Flow
`sbin_PROGRAMS = exportd` with `exportd_SOURCES = exportd.c`. Link inputs include `libexport.a`, `libnfs.la`, `libmisc.a`, `libreexport.a`, optional junction support, blkid, pthread, uuid, and netlink libraries. `exportd_CPPFLAGS` adds the support/export include path. Hook targets rename the installed binary to `$(NFSPREFIX)$(KPREFIX)exportd` and create/remove `nfsv4.` manpage symlinks.

## State, Dependencies, And Integration
The build depends on configure variables such as `CONFIG_JUNCTION`, `LIBNL3_LIBS`, `LIBNLGENL3_LIBS`, `LIBPTHREAD`, `LIBBLKID`, and `KPREFIX`. It integrates exportd with shared export/cache/nfs support code and packaging install conventions.

## Risks And Test Signals
Risks include manual install hooks diverging from automake transform behavior, missing netlink or uuid libraries surfacing only at link time, and manpage symlink assumptions. Test signals are `make`, `make install DESTDIR=...`, `make uninstall DESTDIR=...`, builds with and without `CONFIG_JUNCTION`, and validation that `nfsv4.exportd` and man links are installed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/exportd/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/exportd/exportd.c -->
# sources/user-network-fs/nfs-utils/utils/exportd/exportd.c

## Purpose
`exportd` is a daemon for servicing NFSv4 export cache upcalls. It reads exportd/mountd configuration, opens kernel cache channels, optionally forks worker processes, initializes v4 client tracking, and processes export cache requests until shutdown.

## APIs And Control Flow
Important functions are `read_exportd_conf`, `set_signals`, `killer`, and `main`. Configuration populates `manage_gids`, `no_netlink`, worker thread count, state directory, cache keying mode, and TTL. Command-line options override config for foreground, debug categories, manage-gids, netlink, cache IP keying, TTL, state path, and thread count. `main` sets state path names for `etab`, daemonizes, clamps worker count to `1..64` outside foreground mode, opens cache channels before forking, delegates process fanout to `cache_fork_workers`, initializes v4 clients, and loops on `cache_process`.

## State, Dependencies, And Integration
Global state is intentionally shared with support libraries: `manage_gids`, `no_netlink`, `use_ipaddr`, `default_ttl`, and `etab` path data. It depends on support/export, support/nfs, support/misc, cache channel files, nfs.conf, daemon lifecycle helpers, and worker management functions.

## Risks And Test Signals
Risks include Linux-specific signal behavior, foreground forcing single worker, command-line/config option mismatches, and cleanup only for lock/state path names on normal signal paths. Test with foreground and daemon modes, multiple `--num-threads` values, invalid TTL, SIGHUP/SIGTERM behavior, no-netlink mode, cache upcall processing, and worker exit handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/exportd/exportd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/exportfs/Makefile.am -->
# sources/user-network-fs/nfs-utils/utils/exportfs/Makefile.am

## Purpose
This automake file builds the `exportfs` administration command and packages its related manual pages for exports, nfsd, and exportfs.

## APIs And Build Flow
It declares `man5_MANS = exports.man`, `man7_MANS = nfsd.man`, `man8_MANS = exportfs.man`, and `sbin_PROGRAMS = exportfs`. `exportfs_SOURCES` is `exportfs.c`. Link dependencies include support/export, support/nfs, support/misc, support/reexport, libwrap, libnsl, pthread, and netlink libraries. `exportfs_CPPFLAGS` adds support/reexport and netlink include flags.

## State, Dependencies, And Integration
The file integrates the command with the export database, reexport support, cache flushing, and optional libnl based kernel interfaces. Configure variables provide all portability decisions and library flags.

## Risks And Test Signals
Risks are mostly build-time: optional netlink flags must match compiled code, libwrap/libnsl availability varies by platform, and manpage lists must stay synchronized with distributed files. Test with `make`, `make distcheck`, netlink enabled/disabled builds, and link checks on systems with and without tcp_wrappers/libnsl.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/exportfs/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/exportfs/exportfs.c -->
# sources/user-network-fs/nfs-utils/utils/exportfs/exportfs.c

## Purpose
`exportfs` is the administrative CLI for listing, exporting, unexporting, reexporting, validating, and flushing NFS exports. It reads `/etc/exports` and exports.d data, updates the etab state file, and notifies kernel/user-space caches.

## APIs And Control Flow
`main` parses `-a`, `-r`, `-u`, `-o`, `-i`, `-f`, `-L`, `-v`, and `-s`, validates incompatible modes, initializes state paths and nfsd paths, serializes writers with `grab_lockfile`, reads configured exports unless ignored, marks all exports or parses explicit `host:/path` arguments, writes etab, flushes caches, and frees export state. `exportfs_parsed` creates or updates an export entry and calls `validate_export`. IPv6 bracket syntax is handled separately. `unexportfs_parsed` clears active flags and, when possible, sends an NFSD netlink unlock-export command if no export remains for a path. `dump` renders current exports in table or exports-file format.

## State, Dependencies, And Integration
State includes the lock fd, `f_unexport_all`, global `no_netlink`, `exportlist`, etab paths, cache channels, DNS resolution, and optional NFSD/SUNRPC generic netlink. It integrates support/export parsing, xtab/etab persistence, reexport options, secinfo/xprtsec display, and kernel export validation.

## Risks And Test Signals
Risks include in-place mutation of argv strings while parsing, DNS dependence for hostname matching, best-effort lock failure logging, time-2038 handling for proc cache probes, netlink/proc fallback differences, and validation warnings that do not fail the command. Test list/export/unexport/reexport modes, IPv6 host syntax, trailing slash unexport, wildcard/netgroup names, invalid options, netlink unlock failures, and concurrent writers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/exportfs/exportfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/Makefile.am -->
# sources/user-network-fs/nfs-utils/utils/gssd/Makefile.am

## Purpose
This automake file builds RPCSEC_GSS user-space daemons: `gssd` and, when configured, `svcgssd`. It defines shared GSS/Kerberos context sources and installs binaries under the `rpc.` prefix convention.

## APIs And Build Flow
`COMMON_SRCS` contains context serializers, GSS utilities, OID/name helpers, and error utilities. `gssd_SOURCES` adds `gssd.c`, `gssd_proc.c`, `krb5_util.c`, public headers, and byte-writing helpers. `svcgssd_SOURCES` adds server-side files when `CONFIG_SVCGSS` is enabled. Link flags include support/nfs, libevent, RPCSEC_GSS, Kerberos, GSSAPI, libtirpc, pthread, and optionally nfsidmap for svcgssd. Install hooks rename binaries to `$(RPCPREFIX)$(KPREFIX)<name>` and create `rpc.` manpage symlinks.

## State, Dependencies, And Integration
The file is the build integration point for conditional MIT/Heimdal/lucid Kerberos support, libevent event handling, rpcsec_gss APIs, and package naming conventions.

## Risks And Test Signals
Risks include compile/link matrix complexity across MIT, Heimdal, libtirpc, libgssglue, and service GSS options. Test with `CONFIG_SVCGSS` both ways, Kerberos implementations with and without lucid support, `make install/uninstall DESTDIR=...`, and runtime link checks for libevent/GSSAPI symbols.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/context.c -->
# sources/user-network-fs/nfs-utils/utils/gssd/context.c

## Purpose
This file is the mechanism dispatcher for serializing established GSS contexts into the kernel format expected by RPCSEC_GSS. It currently accepts only Kerberos V5.

## APIs And Control Flow
`serialize_context_for_kernel` receives a `gss_ctx_id_t`, output buffer, mechanism OID, and optional endtime pointer. It compares the supplied OID with the global Kerberos OID through `g_OID_equal`; Kerberos is delegated to `serialize_krb5_ctx`, while any other mechanism logs an unsupported-mechanism error and returns `-1`.

## State, Dependencies, And Integration
There is no private state. Dependencies are GSSAPI types, `krb5oid` from `gss_oids.c`, the selected `serialize_krb5_ctx` implementation from the conditional context backend, and `printerr` logging. It is called by `gssd_proc.c` after creating an authenticated RPCSEC_GSS context and before writing a downcall to the kernel pipe.

## Risks And Test Signals
Risks are intentionally narrow mechanism support and OID comparison assumptions. Tests should cover successful Kerberos dispatch, unsupported OID failure, null/invalid OID defensive behavior at callers, and builds selecting lucid, MIT-private, or Heimdal serializers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/context.h -->
# sources/user-network-fs/nfs-utils/utils/gssd/context.h

## Purpose
This header defines the GSS context serialization interface shared by gssd, svcgssd, and Kerberos-specific backend files. It also records the kernel v2 Kerberos context flag values.

## APIs And Types
`MAX_CTX_LEN` fixes the temporary serialized buffer size at 4096 bytes. Flags are `KRB5_CTX_FLAG_INITIATOR`, `KRB5_CTX_FLAG_CFX`, and `KRB5_CTX_FLAG_ACCEPTOR_SUBKEY`. Public functions are `serialize_context_for_kernel` for mechanism dispatch and `serialize_krb5_ctx` for backend-specific Kerberos serialization.

## State, Dependencies, And Integration
The header depends on RPC/GSS types and is included by context backends and upcall handling code. Its constants must match the kernel RPCSEC_GSS context import formats for legacy RFC1964 and newer RFC4121/CFX contexts.

## Risks And Test Signals
Risks include the fixed maximum length silently constraining future algorithms or token formats, duplicate flag definitions in `context_lucid.c`, and ABI dependence on kernel expectations. Test by serializing DES, DES3, RC4, AES, initiator/acceptor, and acceptor-subkey contexts and confirming kernel import succeeds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/context_heimdal.c -->
# sources/user-network-fs/nfs-utils/utils/gssd/context_heimdal.c

## Purpose
This is the non-lucid Heimdal-specific Kerberos context serializer. It reaches into Heimdal GSS context internals and emits the legacy kernel `krb5_ctx` wire format for DES-era contexts.

## APIs And Control Flow
The file is compiled only when lucid support is absent and Heimdal is present. `write_heimdal_keyblock` writes an enctype and opaque key buffer. `write_heimdal_enc_key` obtains the local subkey, forces keytype `4` for kernel DES compatibility, derives the encryption key by XORing bytes with `0xf0`, and writes it. `write_heimdal_seq_key` obtains and writes the sequence key. `serialize_krb5_ctx` writes initiator state, fake seed fields, fixed sign/seal algorithms, lifetime/endtime, local sequence number, Kerberos OID, encryption key, and sequence key into a `MAX_CTX_LEN` buffer.

## State, Dependencies, And Integration
There is no persistent module state. It depends on Heimdal private GSS structs, krb5 auth-context accessors, `write_bytes.h`, `krb5oid`, and gssd error helpers. It integrates with `context.c` as the selected `serialize_krb5_ctx`.

## Risks And Test Signals
Risks include private Heimdal structure coupling, DES-only assumptions, hard-coded algorithm values, mutating/forcing key types, and fixed buffer size. Test with Heimdal builds lacking lucid support, DES contexts, non-DES warning paths, expired contexts, and kernel downcall acceptance.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/context_heimdal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/context_lucid.c -->
# sources/user-network-fs/nfs-utils/utils/gssd/context_lucid.c

## Purpose
This is the common Kerberos serializer for GSS libraries that support exported lucid security contexts. It avoids private MIT/Heimdal context layouts and chooses the kernel's legacy or v2 context format based on protocol and enctype.

## APIs And Control Flow
`serialize_krb5_ctx` calls `gss_export_lucid_sec_context` for version 1 lucid data, then dispatches to `prepare_krb5_rfc1964_buffer` when protocol is RFC1964 with DES-like enctypes, or `prepare_krb5_rfc4121_buffer` otherwise. The RFC1964 path emits legacy fields, Kerberos OID, an XOR-derived encryption key, and sequence key. The RFC4121 path emits v2 flags, endtime, 64-bit send sequence, selected enctype, and raw key bytes, preferring acceptor subkey when present. It frees lucid context data through `gss_free_lucid_sec_context`.

## State, Dependencies, And Integration
No persistent state is stored. Dependencies are `gssapi_krb5.h`, gss_util compatibility macros, `krb5oid`, `write_bytes.h`, and `context.h`. This backend is the preferred serializer when configure detects lucid support.

## Risks And Test Signals
Risks include version-1-only lucid support, context export consuming or invalidating the original context, duplicated flag constants, DES key derivation compatibility, and key choice differences for acceptor subkeys. Test with MIT and Heimdal lucid builds, DES/DES3/RC4/AES enctypes, CFX and non-CFX protocols, acceptor subkey cases, and failure to free lucid contexts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/context_lucid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/context_mit.c -->
# sources/user-network-fs/nfs-utils/utils/gssd/context_mit.c

## Purpose
This is the non-lucid MIT Kerberos context serializer. It duplicates private MIT `krb5_gss_ctx_id_rec` layouts so gssd can extract keys, sequence numbers, flags, and lifetimes for kernel downcalls when lucid export APIs are unavailable.

## APIs And Control Flow
The file defines private context structs for older and newer MIT Kerberos versions plus a glue-layer `gss_union_ctx_id_t`. `write_keyblock` serializes an enctype and key contents. `serialize_krb5_ctx` unwraps the Kerberos internal context and branches on encryption type. DES-family enctypes use the legacy kernel format with initiator, seed, sign/seal algorithms, endtime, 32-bit sequence number, mech OID, encryption key, and sequence key. DES3, RC4, and AES use the v2 format with flags, endtime, 64-bit sequence, selected enctype, and either acceptor-subkey or main encryption key bytes.

## State, Dependencies, And Integration
There is no module persistence. It depends on MIT private structure compatibility, `KRB5_VERSION`, GSS glue wrapping, Kerberos enctype constants, `write_bytes.h`, and `context.h`. It is selected only without lucid support.

## Risks And Test Signals
Risks are high because private structure layouts may change, glue-layer assumptions may be wrong without libgssglue, unsupported enctypes fail, and old-format sequence truncation is intentional. Test across MIT Kerberos versions, all listed enctypes, acceptor subkey and initiator flags, unsupported enctypes, and kernel import behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/context_mit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/err_util.c -->
# sources/user-network-fs/nfs-utils/utils/gssd/err_util.c

## Purpose
This file provides small logging and time-formatting utilities shared by gssd code. It abstracts foreground stderr output versus daemon syslog/xlog output and gates messages by verbosity.

## APIs And Control Flow
`initerr` stores the verbosity and foreground flags and opens xlog when running as a daemon. `printerr` returns early when message priority is above the configured verbosity, then writes to stderr in foreground mode or `xlog_backend` otherwise. `get_verbosity` exposes the current verbosity. `sec2time` converts seconds to a static `Hh:Mm:Ss` buffer for diagnostic output.

## State, Dependencies, And Integration
Static state is `verbosity` and `fg`; `sec2time` also uses a static buffer. The module depends on xlog and stdio varargs. It is used throughout context serialization, Kerberos cache handling, gssd daemon setup, and upcall processing.

## Risks And Test Signals
Risks include non-thread-safe `sec2time` output, global logging state shared across worker threads, `printerr` format-string correctness relying on compiler attributes in the header, and daemon logs always using `L_ERROR`. Test foreground/daemon logging, verbosity thresholds, concurrent calls, and formatting warnings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/err_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/err_util.h -->
# sources/user-network-fs/nfs-utils/utils/gssd/err_util.h

## Purpose
This header exposes gssd logging helpers and the diagnostic seconds-to-time formatter.

## APIs And Types
It declares `initerr`, `printerr`, `get_verbosity`, and `sec2time`. `printerr` carries a GCC printf-format attribute so callers get compile-time checking for format strings and arguments.

## State, Dependencies, And Integration
The header has no state but represents the public logging contract implemented in `err_util.c`. It is included by most gssd modules and context backends, so changes affect both client and server GSS daemon builds.

## Risks And Test Signals
Risks include the unconditional `__attribute__` portability assumption and the static-buffer semantics of `sec2time` not being visible in the prototype. Test with compilers that support or reject GCC attributes, format warning builds, and concurrent diagnostic use.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/err_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gss_names.c -->
# sources/user-network-fs/nfs-utils/utils/gssd/gss_names.c

## Purpose
This file converts authenticated GSS client names into hostbased service-name buffers that can be passed back to the kernel with a successful context downcall.

## APIs And Control Flow
`get_krb5_hostbased_name` handles Kerberos principal display strings containing both `@` and `/`; it copies the service/instance portion before the realm and converts the last slash to `@`, producing a hostbased service form. `get_hostbased_client_name` calls `gss_display_name`, rejects very large names, supports Kerberos OIDs through `krb5oid`, and returns an allocated string. `get_hostbased_client_buffer` wraps that string as a `gss_buffer_t`, including a terminating NUL in the length.

## State, Dependencies, And Integration
No persistent state is kept. Dependencies are GSSAPI display-name APIs, nfsidmap/nfslib includes, `krb5oid`, and `printerr`. `gssd_proc.c` calls this after `gss_inquire_context` to include the acceptor/client name in kernel downcalls.

## Risks And Test Signals
Risks include parsing displayed names with `sscanf`, only supporting Kerberos, allocation length equal to source length without extra slack but relying on zeroed memory, and embedding a NUL in the returned buffer length. Test with normal `nfs/server@REALM`, malformed names, huge names, unknown mechanisms, and buffer release by caller.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gss_names.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gss_names.h -->
# sources/user-network-fs/nfs-utils/utils/gssd/gss_names.h

## Purpose
This header declares the GSS-name conversion helpers used by gssd downcall processing.

## APIs And Types
It exports `get_hostbased_client_name`, which returns an allocated hostbased string, and `get_hostbased_client_buffer`, which returns the same data in a `gss_buffer_t` shape suitable for kernel downcall serialization.

## State, Dependencies, And Integration
There is no local state. The declarations require GSS types to be available from including translation units. The functions integrate `gss_names.c` with `gssd_proc.c` and server-side GSS code that needs normalized hostbased identities.

## Risks And Test Signals
Risks include no include guard, implicit dependency on prior GSS headers, and caller responsibility for freeing returned buffer values. Test by compiling all users with strict warnings and exercising successful and failed name conversion paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gss_names.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gss_oids.c -->
# sources/user-network-fs/nfs-utils/utils/gssd/gss_oids.c

## Purpose
This file defines the Kerberos V5 GSS mechanism OID used throughout gssd to recognize, request, and serialize Kerberos RPCSEC_GSS contexts.

## APIs And State
It exports one global object, `gss_OID_desc krb5oid`, with length 9 and the Kerberos V5 OID byte sequence. There is no control flow or dynamic state.

## Dependencies And Integration
The file depends on GSSAPI type definitions. `context.c`, context serializers, `gss_util.c`, `gss_names.c`, and `krb5_util.c` use this OID for comparisons, desired mechanism sets, error display, and context export.

## Risks And Test Signals
Risks are low but central: if the OID bytes are wrong or object linkage is duplicated, every Kerberos mechanism check fails. Test with `gss_indicate_mechs`, OID comparison against the library's Kerberos mechanism, and link tests ensuring exactly one definition.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gss_oids.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gss_oids.h -->
# sources/user-network-fs/nfs-utils/utils/gssd/gss_oids.h

## Purpose
This header exposes the Kerberos mechanism OID and provides a local OID equality macro when the GSS library does not provide one.

## APIs And Types
It declares `extern gss_OID_desc krb5oid`. `g_OID_equal` compares OID length and byte contents using `memcmp`, preserving compatibility with older GSS headers.

## State, Dependencies, And Integration
The header has no state but assumes `gss_OID_desc` and `memcmp` are visible through surrounding includes. It is included in context dispatch, serializers, GSS utilities, name conversion, and Kerberos credential logic.

## Risks And Test Signals
Risks include missing direct includes for GSSAPI/string declarations and macro double-evaluation of arguments if callers pass expressions. Test strict compile modes, equality with Kerberos and non-Kerberos OIDs, null avoidance at callers, and compatibility with headers that already define `g_OID_equal`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gss_oids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gss_util.c -->
# sources/user-network-fs/nfs-utils/utils/gssd/gss_util.c

## Purpose
This file contains general GSSAPI support for gssd: status reporting, acceptor credential acquisition, mechanism availability checks, and global credential cleanup.

## APIs And Control Flow
`display_status_2` converts major and minor GSS status codes into readable diagnostics and treats expired credentials as lower-verbosity noise. `pgsserr` is the public wrapper. `gssd_acquire_cred` imports an optional hostbased server name, acquires acceptor credentials into global `gssd_creds`, reports detailed failures, and releases imported names. `gssd_check_mechs` verifies that the GSS library returns at least one supported mechanism. `gssd_cleanup` releases the global credential handle.

## State, Dependencies, And Integration
Global state is `gssd_creds` and `g_mechOid`. Dependencies include GSSAPI, optional Kerberos name types, error utilities, and gssd globals. Client upcall processing uses the status helpers; server-side code can acquire acceptor creds through this file.

## Risks And Test Signals
Risks include global credential lifetime, limited major-status name mapping, possible null release paths around target names, and diagnostic verbosity hiding important credential-expiry behavior. Test GSS library misconfiguration, no mechanisms, bad service names, expired credentials, and cleanup idempotence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gss_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gss_util.h -->
# sources/user-network-fs/nfs-utils/utils/gssd/gss_util.h

## Purpose
This header declares shared GSS utility functions and compatibility mappings for Kerberos-specific GSS extension APIs.

## APIs And Types
It exports `gssd_creds`, `gssd_acquire_cred`, `pgsserr`, `gssd_check_mechs`, and `gssd_cleanup`. When not using libgssglue, it maps generic lucid-context and allowable-enctype helper names onto `gss_krb5_*` functions from `gssapi_krb5.h`.

## State, Dependencies, And Integration
The header depends on RPC/GSS headers and `write_bytes.h`. It is included by gssd core, upcall processing, context serialization, and Kerberos utilities, making it the compatibility shim between libtirpc/rpcsec_gss code and concrete GSSAPI implementations.

## Risks And Test Signals
Risks include macro compatibility differences between libgssglue and direct Kerberos GSS headers, and exposing a global credential handle without ownership annotations. Test builds with libgssglue and without it, lucid support enabled, allowable-enctype support enabled, and strict warnings for macro signatures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gss_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gssd.c -->
# sources/user-network-fs/nfs-utils/utils/gssd/gssd.c

## Purpose
This is the `rpc.gssd` daemon main loop. It watches `rpc_pipefs` for kernel RPC client directories, opens their `gssd` or legacy `krb5` upcall pipes, dispatches upcalls into worker threads, and manages daemon configuration, signals, and timeout watchdogs.

## APIs And Control Flow
`read_gss_conf` and option parsing set pipefs, keytab, ccache search paths, DNS behavior, gssproxy use, timeouts, and verbosity. `main` normalizes `$HOME`, optionally enables `GSS_USE_PROXY`, builds the ccache search list, initializes logging, daemonizes, checks GSS mechanisms, creates a libevent base, opens pipefs, initializes inotify, registers SIGHUP rescans and pipefs events, starts the watchdog, scans current clients, and enters `event_base_dispatch`. Scanning builds `topdir` and `clnt_info` lists, adds inotify watches, opens client pipes, registers read events, and parses `info` files for server/service/address data. Inotify callbacks incrementally rescan or destroy clients.

## State, Dependencies, And Integration
Major state includes pipefs directory/fd, inotify fd, event base, config globals, `topdir_list`, client reference counts, `active_thread_list`, and mutexes. It depends on libevent, inotify, rpc_pipefs layout, nfs.conf, Kerberos utilities, and upcall handlers in `gssd_proc.c`.

## Risks And Test Signals
Risks include complex lifetime coupling between events, client refs, and worker threads; reliance on `d_type`; DNS fallback behavior; watchdog cancellation safety; global per-process environment changes; and empty pipefs treated as fatal. Test pipefs create/delete/rescan paths, SIGHUP, malformed `info`, RDMA-to-TCP conversion, foreground/daemon modes, gssproxy env setup, timeout clamping, and shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gssd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gssd.h -->
# sources/user-network-fs/nfs-utils/utils/gssd/gssd.h

## Purpose
This header defines the shared daemon configuration, rpc_pipefs client structures, upcall request structures, and public upcall-handling APIs for `rpc.gssd`.

## APIs And Types
It defines default paths and names, upcall timeout bounds, `RPC_CHAN_BUF_SIZE`, auth type constants, and many extern configuration variables. `struct clnt_info` tracks one kernel client directory, its parsed server/service/protocol data, pipe fds/events, watch descriptor, sockaddr, and fallback upcall fields. `struct clnt_upcall_info` packages one worker request. `struct upcall_thread_info` tracks watchdog metadata, deadline, uid, fd, and cancellation flags. Public functions include `handle_krb5_upcall`, `handle_gssd_upcall`, `free_upcall_info`, `gssd_free_client`, and `do_error_downcall`.

## State, Dependencies, And Integration
The header depends on GSSAPI, libevent, pthreads, sys/queue, and nfs-utils state directory macros. It connects `gssd.c`, `gssd_proc.c`, and `krb5_util.c` through shared globals.

## Risks And Test Signals
Risks include many mutable extern globals, reference-counted client lifetimes, legacy and modern pipe paths coexisting, and structs carrying both parsed and fallback service info. Test compile users under strict warnings and runtime paths for legacy `krb5` pipe, modern `gssd` pipe, cancellation flags, and config defaults.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gssd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gssd_proc.c -->
# sources/user-network-fs/nfs-utils/utils/gssd/gssd_proc.c

## Purpose
This file handles actual gssd upcalls. It parses kernel requests, selects user or machine Kerberos credentials, creates RPCSEC_GSS contexts with servers, serializes contexts for the kernel, and writes success or error downcalls.

## APIs And Control Flow
`handle_krb5_upcall` reads a uid from the legacy pipe; `handle_gssd_upcall` parses text fields such as `mech=`, `uid=`, `target=`, `service=`, `srchost=`, and `enctypes=`, then starts a worker. `start_upcall_thread` creates a pthread and records it in the watchdog list. `process_krb5_upcall` chooses user creds via `krb5_not_machine_creds` or machine creds via `krb5_use_machine_creds`, creates an authenticated RPC client, extracts private authgss context data, inquires lifetime/acceptor name, serializes the context with `serialize_context_for_kernel`, and calls `do_downcall`. Error paths call `do_error_downcall`. `create_auth_rpc_client` builds the RPC client, sets allowable enctypes when supported, populates ports, and handles bad-integrity retries.

## State, Dependencies, And Integration
State includes global kernel enctype arrays, active thread tracking, client refs, and authgss private data. Dependencies are libtirpc/rpcsec_gss, GSSAPI, Kerberos utility functions, nfs RPC helpers, pthread cancellation, and kernel pipe downcall formats.

## Risks And Test Signals
Risks include thread cancellation around library calls, direct syscall identity changes, shared enctype globals updated by upcalls, parsing fixed-size text buffers, partial pipe writes, DNS/rpcbind dependence, and service-ticket repair heuristics. Test malformed upcalls, user and machine credential paths, gssproxy/allowable enctype intersections, timeout cancellation, bad integrity retry, NFSv4 port defaults, and kernel downcall binary layout.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/gssd_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/krb5_util.c -->
# sources/user-network-fs/nfs-utils/utils/gssd/krb5_util.c

## Purpose
This file manages Kerberos credential caches, keytab principal selection, machine credential refresh, user credential cache selection, service-ticket cleanup, and encryption-type policy for gssd.

## APIs And Control Flow
User credential flow starts in `gssd_setup_krb5_user_gss_ccache`: expand `%U` directory patterns, scan for `krb5cc` files/dirs, reject wrong owners and expired/corrupt caches, prefer configured realms and newest mtime, and select the cache with `gss_krb5_ccache_name`. Machine credential flow uses `gssd_refresh_krb5_machine_credential_internal`: resolve the keytab, find a principal for `$`, `root`, `nfs`, or `host` service names across target/preferred/default realms, create or find a principal-list entry, choose FILE or MEMORY ccache, and obtain/refresh init creds from the keytab. `gssd_get_krb5_machine_cred_list` refreshes cached principals and returns ccname strings for context creation. Optional enctype logic intersects kernel, config, and library permitted enctypes in library order and applies them with `gss_set_allowable_enctypes`.

## State, Dependencies, And Integration
State includes the global principal list, `ple_lock`, per-principal ccname/endtime/refcount, allowed/kernel/library enctype arrays, and global config from `gssd.c`. Dependencies are Kerberos krb5 APIs, GSSAPI Kerberos extensions, nfs.conf, DNS canonicalization, keytab and ccache files, and gssd logging.

## Risks And Test Signals
Risks include complex lock/refcount behavior, credential cache ownership and expiry edge cases, hostname canonicalization and AD machine-account assumptions, stale machine cache destruction on shutdown, global enctype cache invalidation, and service-ticket removal using fixed `nfs/<name>`. Test user cache selection, preferred realm ordering, FILE vs MEMORY caches, keytab service matching, force renew, expired/corrupt caches, allowed-enctype intersections, bad service ticket removal, and concurrent refresh/list operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/krb5_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/krb5_util.h -->
# sources/user-network-fs/nfs-utils/utils/gssd/krb5_util.h

## Purpose
This header declares the Kerberos utility API used by gssd upcall processing and daemon shutdown. It also hides selected MIT versus Heimdal cleanup differences behind macros.

## APIs And Types
Public functions cover user ccache setup, machine credential list allocation/free, principal destruction, machine credential refresh, Kerberos error strings, default realm lookup, direct user credential acquisition, bad service credential removal, and enctype list formatting. When allowable-enctype support is configured, it also declares `limit_krb5_enctypes`, `get_allowed_enctypes`, and `get_krb5_library_permitted_enctypes`. Compatibility macros map name, realm, and keytab-entry freeing to MIT or Heimdal APIs.

## State, Dependencies, And Integration
The header depends on `krb5.h`, either libtirpc `auth_gss.h` or local OIDs, and compile-time Kerberos feature macros. It is included by `gssd.c` startup and `gssd_proc.c` upcall handling.

## Risks And Test Signals
Risks include compile-time API differences between MIT and Heimdal, optional function declarations only under configure probes, and ownership expectations for returned strings/lists. Test both Kerberos implementations, allowable-enctype enabled/disabled builds, and callers freeing all returned allocations correctly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/gssd/krb5_util.h -->

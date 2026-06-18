# subset-b-005696 Research

Grouped source research for NFS client NFSv4 XDR marshalling, early boot NFS root option preparation, and NFS tracepoint instantiation. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4xdr.c -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs4xdr.c

## Purpose

`sources/distributed-fs/ceph-client/fs/nfs/nfs4xdr.c` is the Linux NFS client-side XDR implementation for NFSv4. It translates VFS/NFS client operation arguments into NFSv4 COMPOUND RPC request streams, decodes server replies back into NFS client result structures, validates operation ordering and reply sizes, and publishes the NFS version 4 RPC procedure table. The source was read as a complete 7,786-line file for this report.

## Important APIs, Types, and Functions

The file centers on `struct compound_hdr`, which tracks COMPOUND status, operation count, tag, expected reply length, and minor version while encoding or decoding. Public integration objects are `nfs4_procedures[]`, `nfs_version4_counts[]`, `nfs_version4`, `nfs41_maxwrite_overhead`, `nfs41_maxread_overhead`, `nfs41_maxgetdevinfo_overhead`, and `nfs4_decode_dirent`.

The generic encoder layer includes `reserve_space`, `encode_string`, `encode_uint32`, `encode_uint64`, `xdr_encode_bitmap4`, `mask_bitmap4`, `encode_compound_hdr`, `encode_op_hdr`, `encode_nops`, `encode_nfs4_stateid`, `encode_nfs4_verifier`, `encode_attrs`, and per-operation helpers such as `encode_open`, `encode_close`, `encode_read`, `encode_write`, `encode_readdir`, `encode_getattr`, `encode_setattr`, `encode_lock`, `encode_layoutget`, `encode_layoutcommit`, `encode_layoutreturn`, `encode_exchange_id`, `encode_create_session`, and `encode_sequence`.

The RPC-facing encoder entry points are named `nfs4_xdr_enc_*` and build full COMPOUND sequences for access, lookup, open, read/write, metadata, ACL, fs_locations, security, lease/session, and pNFS operations. They are wired into `nfs4_procedures[]` through `PROC`, `PROC40`, `PROC41`, and `PROC42`.

The generic decoder layer includes `decode_compound_hdr`, `__decode_op_hdr`, `decode_op_hdr`, `decode_bitmap4`, `decode_attr_*` helpers, `verify_attr_len`, `decode_getfattr_attrs`, `decode_getfattr_generic`, `decode_fsinfo`, `decode_getfh`, `decode_open`, `decode_read`, `decode_write`, `decode_readdir`, `decode_readlink`, `decode_secinfo_common`, `decode_exchange_id`, `decode_create_session`, `decode_sequence`, `decode_getdeviceinfo`, and the pNFS layout decoders. RPC-facing decoders are named `nfs4_xdr_dec_*`.

## Control Flow

Encoding starts in an `nfs4_xdr_enc_*` procedure selected from `nfs4_procedures[]`. The entry point initializes a `compound_hdr`, emits the COMPOUND header, usually emits `OP_SEQUENCE` for NFSv4.1+ sessions, places the current filehandle with `PUTFH` or `PUTROOTFH`, emits one or more operation-specific bodies, prepares reply pages for bulk replies when needed, and finally patches the real operation count with `encode_nops`.

Simple metadata flows are linear. For example LOOKUP encodes `SEQUENCE`, `PUTFH`, `LOOKUP`, `GETFH`, and `GETATTR`; ACCESS optionally appends `GETATTR`; STATFS and PATHCONF request selected attributes through `GETATTR` bitmaps. Mutating directory operations such as RENAME and LINK use `SAVEFH` and `RESTOREFH` to control the current and saved filehandles.

Data paths use page-backed XDR buffers. READ, READLINK, READDIR, GETACL, FS_LOCATIONS, GETDEVICEINFO, and LAYOUTGET call `rpc_prepare_reply_pages` or enter reply pages so large opaque payloads land directly in page vectors. WRITE, SETACL, symlink creation, and layoutcommit can splice caller pages into the send buffer with `xdr_write_pages` and set XDR buffer flags.

Decoding mirrors the compound order. Each `nfs4_xdr_dec_*` routine decodes the COMPOUND header, checks the session sequence where present, verifies each expected operation with `decode_op_hdr`, and only then fills result fields. Attribute decoding is order-sensitive: bitmap bits are consumed by `decode_attr_*` helpers, unexpected earlier bits are treated as malformed XDR, and `verify_attr_len` confirms that the decoded attribute body length matches the server's declared length.

pNFS control flow adds layout-specific handling. `LAYOUTGET` validates that at least one layout is returned, decodes stateid/range/type/length, and reads opaque layout bytes from pages. `GETDEVICEINFO` reads opaque device addresses into pages and validates the layout type and notification bitmap. `LAYOUTRETURN` and `LAYOUTCOMMIT` manage layout stateids and optional size updates.

NFSv4.2 procedures are conditionally included by `#include "nfs42xdr.c"` and conditionally wired into the same table. NFSv4.0-only operations such as RENEW and RELEASE_LOCKOWNER are compiled as real procedures only when `CONFIG_NFS_V4_0` is enabled; otherwise procedure slots become stubs.

## State and Persistence Behavior

This file owns no durable storage. It mutates caller-provided RPC argument/result structures, page arrays, XDR streams, NFS fattr structures, sequence/session state fields, lock/open seqids, and pNFS layout/device buffers. Reply status is propagated into result fields such as `op_status`, `sr_status`, `lr_ret`, `sattr_ret`, and layout-specific `status`.

Protocol state appears in encoded and decoded stateids, clientids, sessionids, sequence numbers, slot ids, verifier values, open/lock owner identifiers, delegations, and pNFS layout state. These are persisted by higher NFS client state managers, not by this file. The static `nfs_version4_counts` array is RPC statistics storage associated with the exported `nfs_version4` table.

Attribute results populate caches through `struct nfs_fattr`, filehandles through `struct nfs_fh`, fsinfo/pathconf/statfs structures, ACL buffers, security flavor pages, and fs_locations structures. Directory entries are not decoded at READDIR RPC completion; `nfs4_decode_dirent` parses cached XDR directory pages later when VFS readdir consumers request entries.

## Dependencies and Integration Points

The file depends on Linux SUNRPC XDR APIs (`xdr_stream`, `xdr_buf`, `rpc_rqst`, `rpc_prepare_reply_pages`), NFS protocol definitions (`linux/nfs.h`, `linux/nfs4.h`, `linux/nfs_fs.h`, `linux/nfs_common.h`), NFSv4 client internals (`nfs4_fs.h`, `internal.h`, `nfs4idmap.h`, `nfs4session.h`, `pnfs.h`, `netns.h`), GSS/security types, and kernel identity mapping helpers.

Important integration points are the RPC procedure table consumed by the NFS client transport layer, idmapping via `nfs_map_uid_to_name`, `nfs_map_gid_to_group`, `nfs_map_name_to_uid`, and `nfs_map_group_to_gid`, tracepoints from `nfs4trace.h` for bad XDR status/operation/filehandle cases, pNFS layout driver callbacks for layoutreturn encoding, and NFSv4.2 XDR code included from `nfs42xdr.c`.

Compile-time configuration affects behavior through `CONFIG_NFS_V4_0`, `CONFIG_NFS_V4_1`, `CONFIG_NFS_V4_2`, `CONFIG_NFS_V4_SECURITY_LABEL`, `DEBUG`, and implementation ID settings. The file also integrates with kernel UTS data for implementation IDs and session AUTH_SYS callback parameters.

## Risks and Edge Cases

XDR length accounting is a primary risk. Encode size macros must stay aligned with the actual helper bodies and with the `p_arglen`/`p_replen` values registered in `nfs4_procedures[]`. Underestimates can corrupt send or receive buffer planning; overestimates can waste space or hide incomplete decode assumptions.

Attribute bitmap ordering is fragile. Many `decode_attr_*` helpers reject earlier unexpected bits, and `verify_attr_len` rejects mismatched attribute lengths. Adding or reordering attributes requires protocol-order review across encoder masks, decoder helpers, and fattr validity flags.

Bulk page handling is security-sensitive. READ, READLINK, READDIR, ACL, deviceinfo, layoutget, and fs_locations replies rely on correct page length, offset, and padding calculations. The code has explicit checks for giant symlinks, cheating servers that report more data than received, invalid filehandle lengths, unsupported notifications, layout type mismatches, and empty layout arrays.

State sequencing is correctness-sensitive. OPEN/CLOSE/LOCK decoders increment sequence ids on non-XDR statuses, `decode_sequence` rejects mismatched session ids, sequence numbers, and slot ids, and pNFS paths lock around layout stateid encoding. Incorrect status propagation can break recovery or replay behavior.

Several paths intentionally tolerate partial or optional data, such as ignored extra layout entries, optional implementation IDs, optional security labels, unsupported ACL attributes, and fallback owner/group mapping to `nobody` during encode. These behaviors should be preserved deliberately because they encode interoperability choices with imperfect servers.

## Test Signals

Useful test signals include kernel build coverage across NFSv4.0, v4.1, v4.2, pNFS, ACL, xattr, and security-label configurations; NFS client xfstests over v4.0/v4.1/v4.2 for open, delegation, locking, rename/link/create, ACL, fs_locations, and read/write/commit flows; pNFS layoutget/getdeviceinfo/layoutcommit/layoutreturn tests with multiple layout types and small maxcount retries; fault injection or packet-level tests for malformed XDR lengths, invalid op numbers, bad filehandle sizes, giant symlink lengths, truncated page payloads, and mismatched session slots; and tracepoint checks for `nfs4_xdr_status`, bad operations, and bad filehandles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4xdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfsroot.c -->
# sources/distributed-fs/ceph-client/fs/nfs/nfsroot.c

## Purpose

`sources/distributed-fs/ceph-client/fs/nfs/nfsroot.c` prepares the device string and text mount options used when the kernel mounts its root filesystem over NFS. It combines early IP autoconfiguration state, DHCP/BOOTP root path data, and the `nfsroot=` kernel command-line option into the `server:/export` and option strings consumed by the normal NFS mount path. The source was read as a complete 316-line file for this report.

## Important APIs, Types, and Functions

The exported entry point is `int __init nfs_root_data(char **root_device, char **root_data)`, which validates the selected server address, calls the internal parser, and returns pointers to the prepared static buffers.

Early-boot setup functions are `nfs_root_setup`, registered with `__setup("nfsroot=", nfs_root_setup)`, and, under `NFS_DEBUG`, `nfs_root_debug`, registered with `__setup("nfsrootdebug", nfs_root_debug)`. Helper functions are `root_nfs_copy`, `root_nfs_cat`, `root_nfs_parse_options`, and the internal `root_nfs_data`.

Important file-level state includes `nfs_root_parms`, `nfs_root_options`, `servaddr`, `nfs_export_path`, and `nfs_root_device`. Defaults are `NFS_ROOT` (`/tftpboot/%s`) and `NFS_DEF_OPTIONS`, which selects an NFS protocol version based on kernel configuration and always includes TCP plus 4096-byte read/write sizes.

## Control Flow

During command-line parsing, `nfs_root_setup` marks `ROOT_DEV` as `Root_NFS`. If the option begins like an absolute path, comma option list, or IPv4 address, it copies the line directly. Otherwise it treats the line as a hostname-like token and interpolates it into the default `/tftpboot/%s` path template. It then calls `root_nfs_parse_addr`, which may remove a leading `server-ip:` component from `nfs_root_parms` and stores the address in the global `root_server_addr`.

At mount-root time, `nfs_root_data` copies `root_server_addr` into `servaddr`, rejects `INADDR_NONE`, invokes `root_nfs_data`, and returns the static device/options buffers to the caller.

`root_nfs_data` starts with a temporary copy of the default root path. If DHCPv4 option 17 populated `root_server_path`, it parses that first. If the kernel command line supplied `nfsroot=`, it parses that next so command-line path/options override DHCP-derived values. It appends mandatory `nolock,addr=<server-ip>` options last so they override earlier text options. Finally it substitutes `utsname()->nodename` into the selected export path template and formats `nfs_root_device` as `<server-ip>:<export-path>`.

`root_nfs_parse_options` splits an incoming string at the first comma. A nonempty, non-`default` first field becomes the export path; the remaining comma-separated text is appended to the global options buffer. `root_nfs_cat` inserts a comma separator when needed and rejects truncation.

## State and Persistence Behavior

All storage is `__initdata` and used only during early boot. `nfs_root_parms` holds the raw or transformed command-line parameter, `nfs_root_options` accumulates defaults plus DHCP/command-line/mandatory options, `servaddr` holds the selected server IPv4 address, `nfs_export_path` holds the final export path after `%s` substitution, and `nfs_root_device` holds the mount device string.

There is no file-backed persistence. Once the root mount data is handed to the NFS mount interface, later NFS mount state is owned by the standard NFS superblock/client code. The temporary allocation in `root_nfs_data` is freed before return.

## Dependencies and Integration Points

The file depends on kernel init command-line parsing (`__setup`), root device selection (`ROOT_DEV`, `Root_NFS`), IP autoconfiguration state from `<net/ipconfig.h>` such as `root_server_addr` and `root_server_path`, NFS mount internals declared by `"internal.h"`, and UTS nodename populated by ipconfig.

It integrates with the generic NFS text mount parser by returning strings rather than building binary mount data locally. It also relies on `root_nfs_parse_addr` to strip a leading server address and on normal NFS mount code to interpret options such as `vers=`, `tcp`, `rsize`, `wsize`, `nolock`, and `addr=`.

## Risks and Edge Cases

Buffer sizing and truncation handling are central. Path and device buffers are bounded by `NFS_MAXPATHLEN + 1`; options are limited to 256 bytes. Helper functions return `-1` on `strscpy`, `strlcat`, or `snprintf` overflow, and user-visible errors distinguish allocation failure, option overflow, and device-name overflow.

The `%s` substitution in the export path is intentionally late so DHCP/ipconfig can set the nodename, but it means path strings are interpreted as `snprintf` format strings. Existing behavior expects `%s` use for nodename substitution; unexpected format tokens would be risky if not constrained by boot-time trusted input assumptions.

Override order matters. DHCP option 17 is parsed before command-line `nfsroot=`, and mandatory `nolock,addr=` is appended last. Changing this order can alter real boot behavior. The special path value `default` preserves the currently selected default path while still allowing options to be appended.

Only IPv4 server formatting is used (`%pI4`, `INET_ADDRSTRLEN`, `__be32`). IPv6 root-over-NFS behavior is outside this code path. A missing server address is fatal even if an export path is available.

## Test Signals

Useful test signals include boot tests with `root=/dev/nfs` and `nfsroot=` variants covering plain path, `server-ip:path`, options-only strings, `default,<opts>`, hostname-token transformation, and DHCP option 17; overflow tests for long export paths and long option strings; confirmation that command-line values override DHCP path/options while `nolock,addr=` remains last; debug boot tests with `nfsrootdebug`; and regression boots across `CONFIG_NFS_V2`, `CONFIG_NFS_V3`, and v4-only builds to confirm default `vers=` selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfsroot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfstrace.c -->
# sources/distributed-fs/ceph-client/fs/nfs/nfstrace.c

## Purpose

`sources/distributed-fs/ceph-client/fs/nfs/nfstrace.c` instantiates selected NFS tracepoints and exports tracepoint symbols for use by GPL modules. It is the C translation unit that defines tracepoint storage by setting `CREATE_TRACE_POINTS` before including `nfstrace.h`. The source was read as a complete 15-line file for this report.

## Important APIs, Types, and Functions

There are no normal functions. The important API surface is the tracepoint symbol export list: `EXPORT_TRACEPOINT_SYMBOL_GPL(nfs_fsync_enter)`, `EXPORT_TRACEPOINT_SYMBOL_GPL(nfs_fsync_exit)`, `EXPORT_TRACEPOINT_SYMBOL_GPL(nfs_xdr_status)`, and `EXPORT_TRACEPOINT_SYMBOL_GPL(nfs_xdr_bad_filehandle)`.

The include order is part of the API: `linux/nfs_fs.h`, `linux/namei.h`, `"internal.h"`, then `#define CREATE_TRACE_POINTS` and `#include "nfstrace.h"`.

## Control Flow

This file has no runtime control flow. At compile time, including `nfstrace.h` with `CREATE_TRACE_POINTS` causes the tracepoint definitions to be emitted in this object file. At runtime, other NFS client code calls the tracepoint hooks declared in the header; ftrace/perf/eBPF or kernel tracing consumers observe events if enabled.

## State and Persistence Behavior

Tracepoint descriptors and static keys are kernel-resident instrumentation state generated by the tracepoint framework. The file owns no protocol state, no NFS cache state, and no persistent data. Event records persist only as long as the active tracing backend retains them.

## Dependencies and Integration Points

The file depends on the Linux tracepoint framework through `nfstrace.h` and on NFS client headers for event field types. The exported GPL tracepoints allow other GPL modules to attach to or reference NFS fsync and XDR status/filehandle events.

It complements NFS XDR and filesystem paths that emit `trace_nfs_*` events. In particular, status and bad-filehandle tracepoints are useful alongside the NFS XDR decode code when diagnosing malformed replies or server-side errors.

## Risks and Edge Cases

The main risk is duplicate or missing tracepoint definition. Exactly one C file should include `nfstrace.h` with `CREATE_TRACE_POINTS`; moving or duplicating this pattern can cause link errors or missing event storage. Export names must stay synchronized with tracepoint declarations in `nfstrace.h` and with external module users.

Because this is instrumentation plumbing, semantic changes in event field layouts are ABI-sensitive for tracing tools and BPF programs even when the kernel build still succeeds.

## Test Signals

Useful test signals include kernel build/link coverage with tracing enabled, checking that `/sys/kernel/tracing/events/nfs/` exposes the expected events, enabling fsync and XDR events while running NFS client workloads, and building any GPL modules that reference the exported tracepoint symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfstrace.c -->

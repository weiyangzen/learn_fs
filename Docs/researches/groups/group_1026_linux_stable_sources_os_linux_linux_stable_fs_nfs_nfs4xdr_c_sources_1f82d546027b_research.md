# Group Research: group_1026_linux_stable_sources_os_linux_linux_stable_fs_nfs_nfs4xdr_c_sources_1f82d546027b

Scope: `Docs/research_subset_a.md` only.  
Files read completely: `nfs4xdr.c` 7786 lines, `nfsroot.c` 316 lines, `nfstrace.c` 15 lines.  
Note: the referenced internal group report path was not present in the checkout, so this report is generated from direct source review.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4xdr.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4xdr.c

## Purpose

`nfs4xdr.c` is the Linux NFS client’s NFSv4 XDR implementation. It serializes NFSv4, NFSv4.1, and conditionally NFSv4.2 client requests into RPC COMPOUND calls, decodes server replies, validates returned XDR structure, and registers the client-side RPC procedure table for NFS version 4.

It is not filesystem policy code by itself; it is the protocol marshalling layer used by the rest of the NFS client.

## Main Responsibilities

- Defines encoded and decoded size estimates for each NFSv4 operation and compound procedure.
- Encodes COMPOUND headers, operation headers, state IDs, verifiers, strings, bitmaps, attributes, file handles, names, ACL buffers, layout payloads, and NFSv4.1 session fields.
- Builds compound requests for client operations including READ, WRITE, COMMIT, OPEN, CLOSE, SETATTR, LOOKUP, CREATE, REMOVE, RENAME, LINK, READDIR, READLINK, FSINFO, PATHCONF, STATFS, ACL, SECINFO, delegation return, server capability discovery, migration/fs_locations, and pNFS operations.
- Decodes compound replies in the same operation order used by each encoder.
- Converts protocol status values through `nfs4_stat_to_errno()` and emits tracepoints for XDR status and malformed operation results.
- Provides `nfs4_decode_dirent()` for decoding cached NFSv4 READDIR entries when VFS directory iteration consumes directory pages.
- Exports the `nfs4_procedures[]` procedure table and `nfs_version4` RPC version descriptor.

## Key Data Structures and Constants

- `struct compound_hdr` tracks compound status, operation count, encoded `nops` pointer, tag, expected reply length, and minor version.
- `nfs_type2fmt[]` maps NFSv4 file types such as `NF4REG`, `NF4DIR`, `NF4LNK`, etc. to Linux inode mode type bits.
- Many `*_maxsz` macros define XDR word budgets for individual operations and compound procedures.
- `nfs41_maxwrite_overhead`, `nfs41_maxread_overhead`, and exported `nfs41_maxgetdevinfo_overhead` compute NFSv4.1 RPC overhead for upper layers.

## Encoding Flow

The generic encode path is built around:

- `encode_compound_hdr()` writes tag, minor version, and a placeholder operation count.
- `encode_op_hdr()` writes an NFS operation number and increments the running operation count and expected reply size.
- `encode_nops()` patches the final operation count into the compound header.
- Helpers encode primitive values: `encode_string()`, `encode_uint32()`, `encode_uint64()`, `encode_nfs4_stateid()`, `encode_nfs4_verifier()`, `xdr_encode_bitmap4()`.

Important operation encoders include:

- File identity/path operations: `encode_putfh()`, `encode_putrootfh()`, `encode_getfh()`, `encode_lookup()`, `encode_lookupp()`.
- Data operations: `encode_read()`, `encode_write()`, `encode_commit()`, `encode_readlink()`, `encode_readdir()`.
- Metadata operations: `encode_getattr()`, `encode_getfattr()`, `encode_fsinfo()`, `encode_fs_locations()`, `encode_setattr()`, `encode_attrs()`.
- Namespace operations: `encode_create()`, `encode_remove()`, `encode_rename()`, `encode_link()`.
- State operations: `encode_open()`, `encode_close()`, `encode_open_confirm()`, `encode_open_downgrade()`, `encode_lock()`, `encode_lockt()`, `encode_locku()`, `encode_delegreturn()`.
- NFSv4.0 client identity: `encode_setclientid()`, `encode_setclientid_confirm()`, `encode_renew()`, `encode_release_lockowner()`.
- NFSv4.1 sessions: `encode_exchange_id()`, `encode_create_session()`, `encode_sequence()`, `encode_bind_conn_to_session()`, `encode_destroy_session()`, `encode_destroy_clientid()`, `encode_reclaim_complete()`.
- pNFS: `encode_getdeviceinfo()`, `encode_layoutget()`, `encode_layoutcommit()`, `encode_layoutreturn()`.
- Stateid maintenance: `encode_test_stateid()`, `encode_free_stateid()`.
- Security negotiation: `encode_secinfo()`, `encode_secinfo_no_name()`.

`encode_attrs()` is central for SETATTR/CREATE/OPEN creation attributes. It constructs an attribute bitmap and packed attribute buffer for size, mode, uid/gid owner strings, access/modify times, security labels, and mode+umask where supported. UID/GID mapping failures fall back to `"nobody"`.

## Compound Request Encoders

Each `nfs4_xdr_enc_*()` function constructs one full compound request. Common pattern:

1. Determine minor version from the session via `nfs4_xdr_minorversion()` when applicable.
2. Encode compound header.
3. Encode `SEQUENCE` for NFSv4.1+ sessioned operations.
4. Encode one or more protocol operations in the precise expected server order.
5. Prepare reply pages for variable-size replies when needed.
6. Patch operation count with `encode_nops()`.

Examples:

- READ: `SEQUENCE`, `PUTFH`, `READ`, then prepares reply pages and marks `XDRBUF_READ`.
- WRITE: `SEQUENCE`, `PUTFH`, `WRITE`, optional GETATTR, and marks send buffer `XDRBUF_WRITE`.
- OPEN: `SEQUENCE`, `PUTFH`, `OPEN`, `GETFH`, optional ACCESS, GETATTR, optional LAYOUTGET.
- CLOSE and OPEN_DOWNGRADE may include LAYOUTRETURN before final state operation.
- FS_LOCATIONS handles both migration and lookup-style discovery paths.
- GETACL and fs_locations arrange page-backed receive buffers before decoding variable data.

## Decoding Flow

The generic decode path is built around:

- `decode_compound_hdr()` reads compound status, tag, and operation count.
- `__decode_op_hdr()` validates the returned operation number and operation status. It maps NFS status to Linux errno and records tracepoints for bad status or wrong operation number.
- `decode_op_hdr()` wraps `__decode_op_hdr()`.
- `decode_bitmap4()`, `decode_attr_bitmap()`, `decode_attr_length()`, and `verify_attr_len()` enforce attribute stream structure.
- State helpers set stateid type while decoding: open, lock, delegation, layout, invalid state IDs.

Attribute decoding is strict. Each decoder checks whether earlier unexpected bitmap bits remain, consumes exactly the attribute it owns, clears the consumed bit, and returns either an attribute-valid flag, zero, or an error. `decode_getfattr_attrs()` composes these into `struct nfs_fattr`.

Decoded attribute categories include:

- Type, mode, fileid, mounted_on_fileid, filehandle, fsid, change attr, size.
- Link count, owner, group, raw device, space used, timestamps, security label.
- Server features such as supported attrs, ACL support, case sensitivity, exclusive create support, open argument support.
- FSINFO values such as lease time, max file size, max read/write, time delta, pNFS layout types, layout block size, clone block size, change attribute type, xattr support.
- FS locations and pathnames for migration/referral support.
- pNFS MDS threshold hints.

## Reply Decoders

The `nfs4_xdr_dec_*()` functions mirror each compound encoder’s operation order. They generally stop on required operation failure and decode optional trailing attributes only when appropriate.

Important reply decoders:

- Data paths: `nfs4_xdr_dec_read()`, `nfs4_xdr_dec_write()`, `nfs4_xdr_dec_commit()`.
- Lookup/create/path operations: `nfs4_xdr_dec_lookup()`, `nfs4_xdr_dec_lookupp()`, `nfs4_xdr_dec_lookup_root()`, `nfs4_xdr_dec_create()`, `nfs4_xdr_dec_remove()`, `nfs4_xdr_dec_rename()`, `nfs4_xdr_dec_link()`.
- State paths: `nfs4_xdr_dec_open()`, `nfs4_xdr_dec_open_noattr()`, `nfs4_xdr_dec_open_confirm()`, `nfs4_xdr_dec_close()`, `nfs4_xdr_dec_open_downgrade()`, lock decoders.
- NFSv4.1: exchange/create/destroy session, bind connection, sequence, reclaim complete, destroy clientid.
- pNFS: getdeviceinfo, layoutget, layoutcommit, layoutreturn.
- Security and migration: SECINFO, SECINFO_NO_NAME, FS_LOCATIONS, FSID_PRESENT.
- ACL: GETACL and SETACL.

The READ/READLINK/LAYOUTGET decoders explicitly check whether the server returned more data than was actually received and reject or clamp as appropriate.

## pNFS and Layout Handling

This file supports pNFS protocol marshalling but delegates layout-specific opaque encoding/decoding to layout drivers and page buffers.

- GETDEVICEINFO reads opaque device addresses into pages and validates layout type and notification bitmap.
- LAYOUTGET validates non-empty layout arrays, decodes returned range, iomode, layout type, and opaque layout length, then reads layout bytes from pages.
- LAYOUTCOMMIT encodes whole-file layout commit information plus optional layoutupdate pages.
- LAYOUTRETURN encodes file-level returns and lets the layout driver append private data when available.

## Directory Entry Decode

`nfs4_decode_dirent()` parses one cached NFSv4 directory entry from an XDR stream. It handles EOF/cookie markers, name, attribute bitmap, attributes, file handle, inode number selection, and dentry type derivation.

It fakes inode number `1` when neither mounted-on-fileid nor fileid is available, avoiding inode zero.

## Procedure Registration

The `PROC`, `PROC40`, `PROC41`, and `PROC42` macros populate `nfs4_procedures[]`. Unsupported version-gated entries become stubs. `CONFIG_NFS_V4_2` includes `nfs42xdr.c`, and the procedure table includes v4.2 operations such as SEEK, ALLOCATE, DEALLOCATE, CLONE, COPY, xattrs, READ_PLUS, and ZERO_RANGE when configured.

`nfs_version4` exposes RPC version number 4, procedure count, procedure table, and per-procedure counters.

## Error Handling and Invariants

- XDR reservation failures in `reserve_space()` are treated as impossible sizing bugs and trigger `BUG_ON`.
- Decode paths distinguish transport/XDR corruption (`-EIO`) from protocol status converted via `nfs4_stat_to_errno()`.
- Attribute lengths are verified against stream position to detect malformed or unexpected attribute payloads.
- Returned operation numbers must match expected operation order.
- NFSv4.1 SEQUENCE replies must match expected session ID, slot ID, and sequence number, otherwise `-EREMOTEIO` is returned.
- File handle lengths are rejected when zero or larger than `NFS4_FHSIZE`.
- ACL and page-backed variable replies guard against page buffer overflow/truncation.

## Dependencies

This file depends heavily on Linux SUNRPC XDR helpers, NFS client state/session structures, NFS idmapping, pNFS interfaces, NFSv4 constants, and trace definitions from `nfs4trace.h`.

## Research Notes

This is a high-risk protocol boundary file: correctness depends on exact encode/decode ordering, size estimates, bitmap consumption, and page-buffer setup. Any change to an operation’s compound composition must update both its size macros and its matching decoder order.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfsroot.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfsroot.c

## Purpose

`nfsroot.c` prepares early-boot NFS root mount data. It turns DHCP/IP autoconfiguration data and the `nfsroot=` kernel command-line parameter into the device string and mount option string consumed by the normal NFS mount path.

It is init-only setup code for mounting the root filesystem over NFS.

## Main Responsibilities

- Registers the `nfsroot=` boot parameter parser.
- Optionally registers `nfsrootdebug` under `NFS_DEBUG`.
- Maintains init-time buffers for:
  - raw `nfsroot=` parameters,
  - NFS mount options,
  - server address,
  - export path,
  - final `server:/path` device string.
- Combines defaults, DHCP option 17 root path, command-line overrides, and mandatory NFS root options.
- Returns prepared mount strings via `nfs_root_data()`.

## Defaults and Configuration

Default export path:

- `NFS_ROOT` is `"/tftpboot/%s"`.
- `%s` is replaced late by `utsname()->nodename`, which IP autoconfiguration has already set.

Default mount options depend on kernel config:

- NFSv2: `vers=2,tcp,rsize=4096,wsize=4096`
- NFSv3: `vers=3,tcp,rsize=4096,wsize=4096`
- Otherwise NFSv4: `vers=4,tcp,rsize=4096,wsize=4096`

Mandatory options appended last:

- `nolock`
- `addr=<server IPv4 address>`

Appending these last makes them override earlier options.

## Boot Parameter Parsing

`nfs_root_setup()` handles:

```text
nfsroot=[<server-ip>:]<root-dir>[,<nfs-options>]
```

Behavior:

- Sets `ROOT_DEV = Root_NFS`.
- If the argument starts with `/`, `,`, or a digit, it is copied directly into `nfs_root_parms`.
- Otherwise it treats the string as a hostname-like token and formats it into the default path pattern.
- Calls `root_nfs_parse_addr()` to extract an optional NFS server IP and remove it from `nfs_root_parms`.
- Stores the extracted address in global `root_server_addr`.

## Option and Path Assembly

`root_nfs_parse_options()` splits an incoming string at the first comma:

- The first field is the export path.
- A non-empty path other than `"default"` replaces the current export path.
- Remaining comma-separated text is appended to `nfs_root_options`.

`root_nfs_data()` performs late assembly:

1. Allocates a temporary path buffer.
2. Starts with default `NFS_ROOT`.
3. Applies DHCPv4 option 17 from `root_server_path`, if present.
4. Applies command-line `nfsroot=` options, if present.
5. Appends mandatory `nolock,addr=<server>`.
6. Substitutes `utsname()->nodename` into the export path.
7. Builds `nfs_root_device` as `<server-ip>:<export-path>`.

## Public Entry Point

`nfs_root_data(char **root_device, char **root_data)`:

- Copies `root_server_addr` into local init data `servaddr`.
- Fails if no server address was discovered.
- Calls internal `root_nfs_data()`.
- On success, returns:
  - `*root_device = nfs_root_device`
  - `*root_data = nfs_root_options`

## Error Handling

The file reports and returns `-1` for:

- Missing server address.
- Temporary buffer allocation failure.
- Mount option string overflow.
- Export/device string overflow.

String copying uses `strscpy()` and `strlcat()` wrappers that detect truncation.

## Dependencies

- IP autoconfiguration globals from `<net/ipconfig.h>`, including `root_server_addr` and `root_server_path`.
- NFS mount internals from `internal.h`.
- `utsname()->nodename` for late `%s` substitution.
- `ROOT_DEV` and `Root_NFS` to select NFS root.

## Research Notes

This file is intentionally small but boot-critical. Its main invariant is precedence: built-in defaults first, DHCP option 17 next, command-line `nfsroot=` after that, and mandatory root-NFS options last.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfsroot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfstrace.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfstrace.c

## Purpose

`nfstrace.c` instantiates and exports selected NFS tracepoints.

## Contents

The file:

- Includes NFS and path lookup headers.
- Includes `internal.h`.
- Defines `CREATE_TRACE_POINTS` before including `nfstrace.h`, causing tracepoint definitions to be emitted here.
- Exports tracepoint symbols for GPL modules:
  - `nfs_fsync_enter`
  - `nfs_fsync_exit`
  - `nfs_xdr_status`
  - `nfs_xdr_bad_filehandle`

## Dependencies

Tracepoint declarations live in `nfstrace.h`. This file provides the single compilation unit that materializes those declarations as tracepoint definitions.

## Research Notes

This is a tracepoint definition/export shim. It contains no runtime logic beyond symbol creation and export.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfstrace.c -->
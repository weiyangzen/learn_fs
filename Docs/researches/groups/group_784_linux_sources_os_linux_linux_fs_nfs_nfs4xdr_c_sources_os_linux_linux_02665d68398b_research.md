# Group Research: group_784_linux_sources_os_linux_linux_fs_nfs_nfs4xdr_c_sources_os_linux_linux_02665d68398b

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`, which is included in subset A. Each listed source file was read completely. These three files are byte-identical to their `sources/os/linux/linux-stable/fs/nfs/` counterparts in this checkout.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4xdr.c -->
# File Research: sources/os/linux/linux/fs/nfs/nfs4xdr.c

## Purpose

`nfs4xdr.c` is the Linux NFS client’s NFSv4 XDR implementation. It serializes NFSv4, NFSv4.1, and conditionally NFSv4.2 client requests into RPC COMPOUND calls, decodes server replies, validates returned XDR structure, and registers the client-side RPC procedure table for NFS version 4.

It is the protocol marshalling layer used by the rest of the NFS client, not the higher-level filesystem policy layer.

## Main Responsibilities

- Defines encoded and decoded size estimates for each NFSv4 operation and compound procedure.
- Encodes COMPOUND headers, operation headers, stateids, verifiers, strings, bitmaps, attributes, file handles, names, ACL buffers, layout payloads, and NFSv4.1 session fields.
- Builds compound requests for READ, WRITE, COMMIT, OPEN, CLOSE, SETATTR, LOOKUP, CREATE, REMOVE, RENAME, LINK, READDIR, READLINK, FSINFO, PATHCONF, STATFS, ACL, SECINFO, delegation return, migration/fs_locations, and pNFS operations.
- Decodes compound replies in the same operation order used by each encoder.
- Converts NFS protocol status values through `nfs4_stat_to_errno()` and emits XDR tracepoints for malformed or failed operation replies.
- Provides `nfs4_decode_dirent()` for decoding cached NFSv4 READDIR entries during VFS directory iteration.
- Exports `nfs4_procedures[]` and `nfs_version4`.

## Key Structures and Constants

- `struct compound_hdr` tracks compound status, operation count, encoded `nops` placeholder, tag data, expected reply length, and minor version.
- `nfs_type2fmt[]` maps NFSv4 wire file types to Linux inode mode type bits.
- Many `*_maxsz` macros define XDR word budgets for individual operations and full compound procedures.
- `nfs41_maxwrite_overhead`, `nfs41_maxread_overhead`, and exported `nfs41_maxgetdevinfo_overhead` describe NFSv4.1 RPC overhead for size negotiation.

## Encoding Model

The core encode pattern is:

1. `encode_compound_hdr()` writes tag, minor version, and a placeholder operation count.
2. `encode_op_hdr()` writes each operation number, increments `nops`, and tracks expected reply words.
3. Operation-specific helpers encode arguments.
4. `encode_nops()` patches the final operation count.

Important operation helpers include filehandle/path helpers, data helpers, metadata helpers, state/open/lock helpers, v4.0 client identity helpers, v4.1 session helpers, security negotiation helpers, and pNFS layout helpers.

`encode_attrs()` is central for SETATTR, CREATE, and OPEN create attributes. It constructs an attribute bitmap and packed attribute buffer for size, mode, owner/group strings, timestamps, security labels, and mode+umask when supported. UID/GID mapping failures fall back to `"nobody"`.

## Compound Encoders

Each `nfs4_xdr_enc_*()` function builds one complete COMPOUND request. Common steps are minor-version selection, optional `SEQUENCE`, one or more protocol operations, reply-page setup for variable replies, and final operation-count patching.

Notable compounds:

- READ: `SEQUENCE`, `PUTFH`, `READ`, reply pages, `XDRBUF_READ`.
- WRITE: `SEQUENCE`, `PUTFH`, `WRITE`, optional `GETATTR`, send pages, `XDRBUF_WRITE`.
- OPEN: `SEQUENCE`, `PUTFH`, `OPEN`, `GETFH`, optional `ACCESS`, `GETATTR`, optional `LAYOUTGET`.
- CLOSE and OPEN_DOWNGRADE may include `LAYOUTRETURN` before final state operation.
- FS_LOCATIONS supports both migration and lookup-style discovery.
- GETACL and FS_LOCATIONS arrange page-backed receive buffers before decoding variable data.

## Decoding Model

The generic decode path is strict:

- `decode_compound_hdr()` reads compound status, tag, and operation count.
- `__decode_op_hdr()` validates returned operation number and maps operation status.
- Attribute decoders consume attributes in bitmap order, clear consumed bits, and reject unexpected earlier bits.
- `verify_attr_len()` ensures the decoded attribute payload length exactly matches the server-declared length.
- Stateid decoders tag decoded stateids as open, lock, delegation, layout, or invalid.

Decoded attribute families include file type, mode, fsid, fileid, mounted-on-fileid, filehandle, change attribute, size, link count, owner/group, raw device, space used, timestamps, security labels, supported capabilities, ACL support, case behavior, FSINFO, fs_locations, pNFS layout types, layout block size, clone block size, change-attribute type, xattr support, and pNFS MDS threshold hints.

## Reply Decoders

The `nfs4_xdr_dec_*()` functions mirror their matching encoder order and stop on required operation failure. Major decoder groups cover:

- Data paths: READ, WRITE, COMMIT.
- Namespace paths: LOOKUP, LOOKUPP, LOOKUP_ROOT, CREATE, REMOVE, RENAME, LINK, SYMLINK.
- State paths: OPEN, OPEN_NOATTR, OPEN_CONFIRM, CLOSE, OPEN_DOWNGRADE, LOCK, LOCKT, LOCKU.
- Metadata paths: GETATTR, SETATTR, ACCESS, FSINFO, PATHCONF, STATFS, SERVER_CAPS.
- NFSv4.0 client identity and renew.
- NFSv4.1 sessions: EXCHANGE_ID, CREATE_SESSION, DESTROY_SESSION, SEQUENCE, RECLAIM_COMPLETE, BIND_CONN_TO_SESSION, DESTROY_CLIENTID.
- pNFS: GETDEVICEINFO, LAYOUTGET, LAYOUTCOMMIT, LAYOUTRETURN.
- Security/migration: SECINFO, SECINFO_NO_NAME, FS_LOCATIONS, FSID_PRESENT.
- ACL: GETACL and SETACL.

READ, READLINK, GETDEVICEINFO, and LAYOUTGET guard against servers claiming more data than was actually received.

## pNFS and NFSv4.2 Integration

This file handles pNFS protocol marshalling while leaving layout-driver opaque payloads to layout-specific callbacks and page buffers.

When `CONFIG_NFS_V4_2` is enabled, it includes `nfs42xdr.c`, adding procedure-table entries for SEEK, ALLOCATE, DEALLOCATE, LAYOUTSTATS, CLONE, COPY, OFFLOAD operations, COPY_NOTIFY, LAYOUTERROR, xattrs, READ_PLUS, and ZERO_RANGE.

## Directory Entry Decode

`nfs4_decode_dirent()` decodes one cached NFSv4 directory entry from an XDR stream. It handles EOF/cookie markers, name, attribute bitmap, attributes, filehandle, inode number selection, and dentry type derivation. If no fileid is available, it uses inode number `1` to avoid inode zero.

## Risk Areas

- Encoder and decoder operation order must remain exact for every COMPOUND.
- Size macros must be kept in sync with operation composition.
- Attribute bitmap consumption and `verify_attr_len()` are protocol integrity checks.
- Reply page setup for READ, READDIR, READLINK, GETACL, FS_LOCATIONS, GETDEVICEINFO, and LAYOUTGET is easy to break.
- NFSv4.1 `SEQUENCE` replies must match session ID, slot ID, and sequence number.
- Filehandle length, ACL length, security label length, and page-buffer truncation handling are malformed-server boundaries.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfs4xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfsroot.c -->
# File Research: sources/os/linux/linux/fs/nfs/nfsroot.c

## Purpose

`nfsroot.c` prepares early-boot NFS root mount data. It combines DHCP/IP autoconfiguration data and the `nfsroot=` kernel command-line parameter into the device string and mount option string consumed by the normal NFS mount path.

This is init-only setup code for mounting the root filesystem over NFS.

## Main Responsibilities

- Registers the `nfsroot=` boot parameter parser.
- Optionally registers `nfsrootdebug` under `NFS_DEBUG`.
- Maintains init-time buffers for raw `nfsroot=` parameters, NFS mount options, server address, export path, and final `server:/path` device string.
- Combines defaults, DHCP option 17 root path, command-line overrides, and mandatory NFS root options.
- Returns prepared strings through `nfs_root_data()`.

## Defaults

Default export path:

- `NFS_ROOT` is `"/tftpboot/%s"`.
- `%s` is replaced late with `utsname()->nodename`, after IP autoconfiguration has set it.

Default mount options depend on kernel config:

- NFSv2: `vers=2,tcp,rsize=4096,wsize=4096`
- NFSv3: `vers=3,tcp,rsize=4096,wsize=4096`
- Otherwise NFSv4: `vers=4,tcp,rsize=4096,wsize=4096`

Mandatory options appended last:

- `nolock`
- `addr=<server IPv4 address>`

Appending mandatory options last lets them override earlier options.

## Boot Parameter Parsing

`nfs_root_setup()` handles:

```text
nfsroot=[<server-ip>:]<root-dir>[,<nfs-options>]
```

Behavior:

- Sets `ROOT_DEV = Root_NFS`.
- If the argument starts with `/`, `,`, or a digit, it copies the string directly into `nfs_root_parms`.
- Otherwise it treats the value as a hostname-like token and formats it into the default path pattern.
- Calls `root_nfs_parse_addr()` to extract an optional server IP and remove it from `nfs_root_parms`.
- Stores the extracted address in global `root_server_addr`.

## Option and Path Assembly

`root_nfs_parse_options()` splits an incoming string at the first comma:

- The first field is the export path.
- A non-empty path other than `"default"` replaces the current export path.
- Remaining comma-separated text is appended to `nfs_root_options`.

`root_nfs_data()` performs late assembly:

1. Starts with the default export path.
2. Applies DHCPv4 option 17 `root_server_path` if present.
3. Applies command-line `nfsroot=` overrides if present.
4. Appends mandatory `nolock,addr=...`.
5. Expands `%s` in the export path using `utsname()->nodename`.
6. Builds the final `nfs_root_device` string as `<IPv4-address>:<export-path>`.

## Error Handling

The file rejects overlong strings and allocation failures with `-1` plus kernel error messages:

- Could not allocate temporary path buffer.
- Mount options string too long.
- Root device name too long.
- No NFS server address.

String copying/appending is guarded by `strscpy()` and `strlcat()` length checks.

## Cross-File Relationships

- Uses IP autoconfiguration globals from `<net/ipconfig.h>`, including `root_server_addr` and `root_server_path`.
- Uses `root_nfs_parse_addr()` from NFS internal root-mount support.
- Produces strings consumed by the regular NFS text-based mount interface.

## Research Notes

The key behavior is precedence: default path/options, then DHCP root path, then command-line `nfsroot=`, then mandatory NFS-root options. The mandatory options are intentionally appended last.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfsroot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfstrace.c -->
# File Research: sources/os/linux/linux/fs/nfs/nfstrace.c

## Purpose

`nfstrace.c` is the tracepoint instantiation unit for generic NFS client trace events. It defines `CREATE_TRACE_POINTS` before including `nfstrace.h`, causing the trace declarations in that header to generate storage and registration code exactly once.

## Behavior

The file includes core NFS and path lookup headers, includes `internal.h`, then materializes tracepoints from `nfstrace.h`.

It exports GPL tracepoint symbols for:

- `nfs_fsync_enter`
- `nfs_fsync_exit`
- `nfs_xdr_status`
- `nfs_xdr_bad_filehandle`

## Cross-File Relationships

- `nfstrace.h` contains the actual trace event definitions.
- NFS source files include `nfstrace.h` to emit these events.
- Other GPL-compatible NFS-related modules can reference the exported tracepoint symbols.

## Research Notes

There is no runtime filesystem logic here beyond tracepoint materialization and symbol export. Its importance is build/linkage: exactly one C file must instantiate the generic NFS tracepoints.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfstrace.c -->
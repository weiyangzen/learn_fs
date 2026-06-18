# Group Research: group_833_linux_sources_os_linux_linux_fs_smb_client_reparse_c_sources_os_linu_8182ba103384

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux`. All listed files were read completely. The requested `sources/os/linux/linux` files are byte-identical to the corresponding `sources/os/linux/linux-stable` files already present in prior research, but this report is written for the requested source tree paths.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/reparse.c -->
# File Research: sources/os/linux/linux/fs/smb/client/reparse.c

This file implements CIFS/SMB reparse-point creation, parsing, and conversion into Linux inode attributes. It is the central implementation behind native Windows symlinks, NFS-style special-file reparse points, WSL/LX reparse tags, and native AF_UNIX socket tags.

Key responsibilities:
- `create_reparse_symlink()` dispatches symlink creation by mount-selected symlink type: native Windows symlink, NFS reparse, or WSL reparse.
- `create_native_symlink()` builds `IO_REPARSE_TAG_SYMLINK` buffers, converts Linux paths into SMB/NT path form when needed, handles `symlinkroot`, and sets `SYMLINK_FLAG_RELATIVE`.
- `detect_directory_symlink_target()` tries to infer whether a symlink target should be a directory symlink, using simple pathname rules first and server opens for relative targets.
- `mknod_reparse()` creates sockets, FIFOs, char/block devices, and symlinks through NFS or WSL reparse formats.
- `parse_reparse_point()` validates and parses returned reparse buffers for NFS, native symlink, WSL symlink, AF_UNIX, LX FIFO/CHR/BLK.
- `cifs_reparse_point_to_fattr()` converts parsed reparse metadata into `struct cifs_fattr` file type, mode, device, uid/gid, and dtype.

Important data paths:
- NFS-style reparse points use `IO_REPARSE_TAG_NFS` plus `NFS_SPECFILE_*` inode type values. Symlink targets are UTF-16 without trailing wide NUL; char/block devices carry two 32-bit major/minor values.
- WSL-style reparse points use `IO_REPARSE_TAG_LX_*`/`IO_REPARSE_TAG_AF_UNIX`, with `$LXUID`, `$LXGID`, `$LXMOD`, and `$LXDEV` EAs built during creation and consumed during fattr conversion.
- Native symlink parsing converts UTF-16 SMB targets to Linux strings, rejects embedded NULs, handles share-root-relative symlinks, and can map common absolute NT `\??\X:\...` paths back under `symlinkroot`.

Validation and error handling:
- The parser checks buffer lengths, even UTF-16 byte counts, NUL codepoints, WSL symlink version 2, mandatory device EAs for WSL char/block tags, and file-type consistency between WSL tag and `$LXMOD`.
- Unsupported tags return `-EOPNOTSUPP` unless they are directory name-surrogate/internal tags that can be represented as junction-like directories.
- Several malformed cases use `smb_EIO*()` trace helpers, making this file relevant for diagnostics of corrupt or malicious server reparse data.

Dependencies:
- Uses common CIFS conversion helpers, `smb2_create_ea_ctx`, SMB2 IOCTL response layout, CIFS mount flags, server operation callbacks, and definitions from `reparse.h` and `../common/smbfsctl.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/reparse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/reparse.h -->
# File Research: sources/os/linux/linux/fs/smb/client/reparse.h

This header exposes CIFS reparse-point helpers and small inline conversions used by both SMB1 and SMB2/3 client paths.

Key contents:
- `REPARSE_SYM_PATH_MAX` defines the native symlink target limit used by `reparse.c`.
- `IO_REPARSE_TAG_INTERNAL` is a CIFS-only sentinel for cases where a reparse point is known from attributes but its data cannot be fetched.
- `reparse_mkdev()` decodes WSL `$LXDEV` major/minor encoding into Linux `dev_t`.
- `wsl_make_kuid()` and `wsl_make_kgid()` convert WSL EA uid/gid values into kernel ids, honoring mount-level uid/gid override flags.
- `reparse_mode_nfs_type()` maps Linux mode file types to NFS reparse inode types.
- `reparse_mode_wsl_tag()` maps Linux mode file types to WSL/LX reparse tags.

Important inode-cache logic:
- `reparse_inode_match()` matches cached reparse inodes by reparse tag and ctime. It deliberately skips strict tag matching when the cached tag is `IO_REPARSE_TAG_INTERNAL`, because the client cannot fetch the reparse data in that mode.
- `cifs_open_data_reparse()` normalizes open-info data so either POSIX info or SMB2 all-info carries `ATTR_REPARSE_POINT` when `data->reparse_point` is set.

Exported interfaces:
- `cifs_reparse_point_to_fattr()`
- `create_reparse_symlink()`
- `mknod_reparse()`
- `smb2_get_reparse_point_buffer()`

Dependencies:
- Includes CIFS global structures, mount context data, Linux uid/gid helpers, and common SMB FSCTL reparse definitions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/reparse.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/rfc1002pdu.h -->
# File Research: sources/os/linux/linux/fs/smb/client/rfc1002pdu.h

This header defines RFC 1001/1002 NetBIOS session-service packet constants and the packed session packet layout used by CIFS/SMB transport code.

Key contents:
- Session packet type constants: session message, request, positive/negative response, retarget response, and keepalive.
- `RFC1002_LENGTH_EXTEND` marks the high-order length bit for payloads over 64 KiB.
- `struct rfc1002_session_packet` models the big-endian NetBIOS session header and its variants:
  - session request called/calling names,
  - retarget response address/port,
  - negative-session-response error code,
  - message trailers that carry SMB/CIFS payloads.
- Negative response codes are defined for not-listening, called-name-not-present, insufficient-resource, and unspecified-error cases.
- `DEFAULT_CIFS_CALLED_NAME` is the default NetBIOS called name string.

Important note:
- Unlike SMB/CIFS packets, these RFC1002 structures are big-endian. Code touching this header must preserve that endian distinction.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/rfc1002pdu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/sess.c -->
# File Research: sources/os/linux/linux/fs/smb/client/sess.c

This file contains generic CIFS session support shared outside the SMB1-only session implementation. Its main areas are SMB3 multichannel session/channel management, NTLMSSP blob construction/parsing, and authentication method selection.

Multichannel responsibilities:
- Tracks whether a session uses a server interface and maps `TCP_Server_Info` channels to session channel indexes.
- Sets and clears per-channel reconnect flags and `in_reconnect` state.
- `cifs_try_adding_channels()` opens secondary channels according to `chan_max`, SMB dialect, server multichannel capability, interface activity, RDMA compatibility, RSS capability, and speed-derived weights.
- `cifs_decrease_secondary_channels()` tears down excess channels, updates interface reference counts and channel counts, marks sockets for reconnect/termination, and trims reconnect bitmasks.
- `cifs_chan_update_iface()` replaces inactive interface bindings and updates the server destination address.

Channel creation:
- `cifs_ses_add_channel()` creates a temporary mount context from the primary session/server, selects the target interface, reuses authentication and dialect settings, creates a TCP session, adds it to `ses->chans`, negotiates protocol, and runs session setup on the new channel.

NTLMSSP responsibilities:
- `decode_ntlmssp_challenge()` validates challenge blobs, checks server flags against signing/encryption requirements, copies the server challenge, and stores target info.
- `build_ntlmssp_negotiate_blob()` and `build_ntlmssp_smb3_negotiate_blob()` build negotiate messages, with the SMB3 variant adding version fields.
- `build_ntlmssp_auth_blob()` builds the authenticate message from the NTLMv2 response, user/domain/workstation strings, and optional key-exchange session key.
- `cifs_security_buffer_from_str()` centralizes UTF-16 security-buffer packing.

Security selection:
- `cifs_select_sectype()` selects RawNTLMSSP, Kerberos/IAKerb, or NTLMv2 depending on negotiated flavor, requested type, server capabilities, and global security flags.

Risk points:
- Multichannel code is lock-sensitive: `chan_lock`, `iface_lock`, and server locks are used with explicit reference-count handoffs.
- NTLMSSP parsing rejects undersized blobs, incorrect signatures/types, unsupported signing requirements, and out-of-bounds target-info offsets.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/sess.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb1debug.c -->
# File Research: sources/os/linux/linux/fs/smb/client/smb1debug.c

This small file provides SMB1-specific debug dumping through `cifs_dump_detail()`.

Behavior:
- Under `CONFIG_CIFS_DEBUG2`, it interprets the buffer as `struct smb_hdr` and logs command, CIFS error, flags, flags2, MID, PID, and word count.
- It then calls the server operation `check_message()` and, if the message validates, logs the calculated SMB size through `calc_smb_size()`.

Dependencies:
- Uses SMB1 protocol declarations from `smb1proto.h`, generic CIFS prototypes, and `cifs_debug.h`.
- The function is installed into `smb1_operations.dump_detail` in `smb1ops.c`.

Notes:
- With `CONFIG_CIFS_DEBUG2` disabled, the function is effectively a no-op.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb1debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb1encrypt.c -->
# File Research: sources/os/linux/linux/fs/smb/client/smb1encrypt.c

This file implements SMB1 signing and signature verification using MD5 over the session key and SMB request data.

Key functions:
- `cifs_calc_signature()` initializes MD5, hashes the server session key, and delegates request-vector hashing to `__cifs_calc_signature()`. It rejects missing inputs and returns `-EOPNOTSUPP` when FIPS mode disables MD5.
- `cifs_sign_rqst()` writes the SMB1 sequence number into the signature field, advances the server sequence counter, computes the signature, and copies the first 8 bytes into the SMB header. Before a session is established it writes the SMB1 dummy signature string.
- `cifs_verify_signature()` skips verification before session establishment and for oplock-release locking requests, preserves the server signature, recomputes the expected signature using the response sequence number, and compares with `crypto_memneq()`.

Important invariants:
- Signing is conditional on the SMB header security-signature flag and not performed while the server needs negotiate.
- The signing path expects the server mutex to be held where noted.
- Sequence-number handling is central: requests consume paired request/response sequence values.

Security relevance:
- SMB1 signing relies on MD5, so this path is incompatible with FIPS mode and is legacy/security-sensitive by design.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb1encrypt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb1maperror.c -->
# File Research: sources/os/linux/linux/fs/smb/client/smb1maperror.c

This file maps SMB1/DOS/NT status errors to Linux `errno` values.

Key structures:
- `mapping_table_ERRDOS[]` and `mapping_table_ERRSRV[]` are generated tables mapping DOS/SRV SMB error codes to POSIX errors.
- `ntstatus_to_dos_map[]` is a generated sorted table mapping NT status codes to DOS class/code pairs.

Lookup logic:
- Uses `__inline_bsearch()` with small comparator helpers to search sorted tables.
- `map_smb_to_linux_error()` returns 0 for success, translates NT status to DOS class/code when `SMBFLG2_ERR_STATUS` is set, then maps DOS or server class codes to POSIX errors.
- Special NT status exceptions override table behavior for `NT_STATUS_NOT_A_REPARSE_POINT` to `-ENODATA` and `NT_STATUS_PRIVILEGE_NOT_HELD` to `-EPERM`.
- Unmapped or hard-error class values fall back to `-EIO` and emit `smb_EIO2()` tracing.

Reconnect behavior:
- `map_and_check_smb_error()` wraps mapping and triggers reconnect when an old-style server error is `ERRSRV/ERRbaduid`, indicating a bad session uid.

Initialization and tests:
- `smb1_init_maperror()` checks that all generated tables are sorted ascending; this is required for binary search correctness.
- Under `CONFIG_SMB1_KUNIT_TESTS`, internal lookup functions and arrays are exported for the KUnit module.

Dependencies:
- Generated include files: `smb1_err_dos_map.c`, `smb1_err_srv_map.c`, and `smb1_mapping_table.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb1maperror.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb1maperror_test.c -->
# File Research: sources/os/linux/linux/fs/smb/client/smb1maperror_test.c

This file is a KUnit test module for SMB1 error-map lookup coverage.

Test strategy:
- Defines a macro that iterates every exported test array entry and searches for that entry by key.
- Compares returned entries field-by-field against the expected table element.
- Covers:
  - `ntstatus_to_dos_map`,
  - `mapping_table_ERRDOS`,
  - `mapping_table_ERRSRV`.

Assertions:
- `KUNIT_ASSERT_NOT_NULL()` verifies each lookup succeeds.
- NT status mapping checks DOS class, DOS code, NT status, and NT error string.
- SMB-to-POSIX mapping checks SMB error code and POSIX code.

Dependencies:
- Requires `CONFIG_SMB1_KUNIT_TESTS`, which causes `smb1maperror.c` to export its otherwise-static tables and search wrappers for this test module.

Value:
- This test ensures binary-search lookup coverage across every generated mapping entry. It complements the runtime sorted-table checks in `smb1_init_maperror()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb1maperror_test.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb1misc.c -->
# File Research: sources/os/linux/linux/fs/smb/client/smb1misc.c

This file provides SMB1 header assembly, oplock-break/dnotify response detection, and SMB packet size calculation.

Key functions:
- `header_assemble()` zeros the SMB header area, fills the SMB protocol signature, command, flags, PID, TID, UID, MID, word count, Unicode/status/signing/DFS/caseless flags, and returns the fixed request length including BCC.
- `is_valid_oplock_break()` recognizes SMB1 NT transact change-notify responses and locking-andx oplock breaks. It validates word count and lock type, locates the relevant session/tree/file by TID and FID, updates inode/file oplock state, queues oplock-break handling, and treats certain invalid-handle/bad-fid races as harmless.
- `smbCalcSize()` computes SMB message size from header size, word count, BCC field, and byte-count payload.

Concurrency and state:
- Oplock handling walks session/tcon/file lists under `cifs_tcp_ses_lock` and `tcon->open_file_lock`.
- It marks `CIFS_INODE_PENDING_OPLOCK_BREAK`, resets oplock epoch, stores the new oplock level, clears cancellation state, and calls `cifs_queue_oplock_break()`.

Dependencies:
- Uses SMB1 PDU structures, error constants, CIFS inode/file state, and server/channel helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb1misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb1ops.c -->
# File Research: sources/os/linux/linux/fs/smb/client/smb1ops.c

This file binds SMB1/CIFS-specific behavior into `struct smb_version_operations` and `struct smb_version_values`. It adapts generic CIFS VFS operations to SMB1 wire commands and legacy server capabilities.

Major responsibilities:
- `reset_cifs_unix_caps()` negotiates CIFS Unix Extensions, preserving reconnect semantics, honoring mount options, and enabling POSIX ACL/path flags on the superblock.
- Cancel paths implement `SMB_COM_NT_CANCEL` and lock-cancel fallback for Windows blocking locks.
- MID, credit, read-offset/length, oplock, negotiate, echo, and path-accessibility helpers provide SMB1-specific operation semantics.
- Read/write size negotiation accounts for Unix large read/write caps, `CAP_LARGE_READ_X`, `CAP_LARGE_WRITE_X`, signing limitations, server `maxBuf`, and hard CIFS limits.
- `cifs_query_path_info()` layers multiple metadata fallbacks: `CIFSSMBQPathInfo()`, `CIFSFindFirst()`, and legacy `SMBQueryInformation()`, with special handling for non-Unicode wildcard paths and non-NT servers.
- SMB1 reparse support is integrated by detecting `ATTR_REPARSE_POINT`, fetching WSL `$LXMOD`/`$LXDEV` EAs when xattrs are enabled, calling `cifs_query_reparse_point`, and exposing `cifs_get_reparse_point_buffer()`.
- `cifs_make_node()` chooses Unix Extensions, SFU emulation, or reparse-point creation for special files.
- `smb_set_file_info()` implements robust attribute/time setting with path-based, filehandle-based, and legacy `SMB_COM_SETATTR` fallbacks.

Operations table:
- `smb1_operations` wires SMB1 implementations for negotiate, session setup, tree connect/disconnect, query/set metadata, reparse operations, open/close/flush, sync/async I/O, directory enumeration, locking, ACLs, symlinks, special-node creation, stats, and network-name-deleted detection.
- `smb1_values` defines SMB1 constants such as protocol id, header sizes, lock types, read response size, capability bits, and signing mode bits.

Risk points:
- Many paths exist for old/non-NT/non-Unicode servers, so behavior is highly capability-dependent.
- Metadata fallback code must preserve semantic differences between NT-style “zero means unchanged” times and legacy servers where zero can be a real timestamp.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb1ops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb1pdu.h -->
# File Research: sources/os/linux/linux/fs/smb/client/smb1pdu.h

This header defines SMB1/CIFS command constants, flags, packed wire structures, information levels, Unix Extensions layouts, and POSIX-extension helper formats.

Major definition groups:
- Protocol and command IDs for classic SMB commands, Transaction2 subcommands, named-pipe transactions, and NT transactions.
- SMB header limits, authentication/key sizes, open/access flags, SMB flags/flags2, file attributes, share access, create disposition/options, impersonation/security flags, and default identifiers.
- Negotiation response layout, security mode bits, and capability bits including Unicode, NT SMBs, DFS, large read/write, Unix Extensions, compression, and extended security.
- Session setup request/response union covering extended-security NTLM, no-security-extension NTLM, and old pre-NTLM/LANMAN formats.
- Tree connect, echo, logoff, close, flush, find-close, open/create, read, write, lock, rename/copy/delete/create-directory/query/setattr packet layouts.
- NT transaction structures for IOCTL/FSCTL, compression IOCTL, security descriptor get/set, change notify, and quota data.
- Transaction2 generic request/response wrappers plus query/set path/file info, find-first/find-next, filesystem info, set filesystem info, and DFS referral structures.
- Data layouts for `FILE_ALL_INFO`, `FILE_STANDARD_INFO`, `FILE_UNIX_BASIC_INFO`, Unix symlink targets, DOS date/time, allocation/EOF/compression info, POSIX ACLs, POSIX open/unlink, internal file ids, file mode, and reparse attribute/tag.
- Directory enumeration records such as `FILE_UNIX_INFO` and `FIND_FILE_STANDARD_INFO`.
- EA list/blob helpers and optional POSIX/xattr/chattr structures under `CONFIG_CIFS_POSIX`.

Important constants:
- `ATTR_REPARSE_POINT` and `OPEN_REPARSE_POINT` connect this header to reparse handling.
- `SMB_FILE_REPARSEPOINT_INFO`, `struct file_attrib_tag`, and NT transaction IOCTL layouts support reparse-point query/create paths.
- CIFS Unix capability flags drive negotiation in `smb1ops.c`.

Implementation note:
- Most structs are `__packed` wire-format declarations. Correct endian annotations and alignment/padding are critical because request builders and response parsers cast network buffers directly to these types.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb1pdu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb1proto.h -->
# File Research: sources/os/linux/linux/fs/smb/client/smb1proto.h

This header declares the SMB1 client API used across the CIFS client when `CONFIG_CIFS_ALLOW_INSECURE_LEGACY` is enabled.

Contents:
- `struct cifs_unix_set_info_args` carries Unix Extension set-info fields: times, mode, uid/gid, and device.
- Prototypes for SMB1 request builders and operations from `cifssmb.c`, including negotiate, tree connect/disconnect, echo, logoff, create/open/read/write/lock/close/flush, rename, hardlink/symlink, reparse-point query/create, compression, ACL, query/set path/file info, directory search, DFS referral, filesystem info, EOF/size updates, Unix info, and EA operations.
- Prototypes for files in this group:
  - `cifs_dump_detail()`
  - `cifs_sign_rqst()`
  - `cifs_verify_signature()`
  - `map_smb_to_linux_error()`
  - `smb1_init_maperror()`
  - `map_and_check_smb_error()`
  - KUnit-only maperror exports
  - `header_assemble()`
  - `is_valid_oplock_break()`
  - `smbCalcSize()`
  - `smb1_operations`
  - `smb1_values`
  - `reset_cifs_unix_caps()`
  - `CIFS_SessSetup()`
  - transport helpers such as `SendReceive*()`, request setup, message checking, and transaction validation.
- Inline helpers for SMB1 MID access/comparison and BCC/byte-area pointer handling.

Important constraints:
- All declarations are gated by `CONFIG_CIFS_ALLOW_INSECURE_LEGACY`, reflecting SMB1’s legacy/insecure status.
- `get_bcc()` and `put_bcc()` use unaligned little-endian helpers because SMB byte-count fields are computed from variable word-count offsets.

Dependency role:
- This is the cross-file contract for the SMB1 implementation; `smb1ops.c` relies on many of these declarations to populate the version operations table.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb1proto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb1session.c -->
# File Research: sources/os/linux/linux/fs/smb/client/smb1session.c

This file implements SMB1 session setup authentication. It builds `SMB_COM_SESSION_SETUP_ANDX` requests for NTLMv2, Kerberos/SPNEGO, and RawNTLMSSP, sends them, parses responses, and establishes the session state.

Core structure:
- `struct sess_data` stores xid, session, server, NLS table, current auth state function, result, request length, buffer type, and three iovecs:
  - fixed SMB request,
  - optional SPNEGO/NTLMSSP security blob,
  - strings and remaining BCC area.

Common helpers:
- `cifs_ssetup_hdr()` fills shared session-setup fields, max buffer/mpx counts, VC number, session key id, flags2, and capability bits.
- Unicode and ASCII helpers encode user, domain, OS, and LAN manager strings.
- Response decoders parse returned server OS, NOS, and domain strings.
- `sess_alloc_buffer()` allocates the fixed SMB buffer and a 2000-byte string buffer.
- `sess_free_buffer()` zeroes/free sensitive buffers.
- `sess_sendreceive()` computes BCC, sends three-vector requests through `SendReceive2()`, and replaces request buffer with the response.
- `sess_establish_session()` copies the auth key into the server session key when signing is enabled, initializes SMB1 sequence numbering, and marks `server->session_estab`.

Authentication flows:
- `sess_auth_ntlmv2()` sends old-style no-extended-security NTLMv2 session setup, embeds the NTLMv2 response after the fixed request, validates response word count 3, stores `Suid`, decodes strings, and establishes the session.
- `sess_auth_kerberos()` is built under `CONFIG_CIFS_UPCALL`; it gets a SPNEGO key from userspace upcall, validates version, stores the session key, sends an extended-security blob, validates response word count 4 and blob length, decodes strings, and establishes the session.
- RawNTLMSSP is a two-step state machine: `sess_auth_rawntlmssp_negotiate()` sends negotiate, accepts `NT_STATUS_MORE_PROCESSING_REQUIRED`, decodes the NTLMSSP challenge, and schedules `sess_auth_rawntlmssp_authenticate()`; authenticate sends the auth blob with the challenge UID, validates response, decodes returned strings, establishes the session, and cleans sensitive state.

Dispatch:
- `select_sec()` calls `cifs_select_sectype()` and chooses NTLMv2, Kerberos, or RawNTLMSSP. Unsupported or unavailable methods return errors.
- `CIFS_SessSetup()` allocates `sess_data`, selects security, runs state functions until completion, and returns the stored result.

Risk points:
- Security blob lengths and word counts are explicitly validated.
- Sensitive auth material is freed with `kfree_sensitive()` or zeroed before release.
- Kerberos requires `CONFIG_CIFS_UPCALL`; otherwise selection fails with `-ENOSYS`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/smb1session.c -->
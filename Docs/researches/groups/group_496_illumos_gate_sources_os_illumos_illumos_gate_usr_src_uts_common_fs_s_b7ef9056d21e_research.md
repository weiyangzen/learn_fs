# Group Research: group_496_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_s_b7ef9056d21e

Scope: `Docs/research_subset_a`, illumos SMB server filesystem/protocol implementation files under `usr/src/uts/common/fs/smbsrv`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_negotiate.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_negotiate.c

Implements SMB2/SMB3 negotiate handling, including the SMB1 negotiate path that returns an SMB2 response, the initial direct SMB2 negotiate request path, common negotiate response construction, and `FSCTL_VALIDATE_NEGOTIATE_INFO`.

Key behavior:
- Advertises tunable server capabilities and transfer sizes through `smb2srv_capabilities`, `smb2_tcp_bufsize`, `smb2_max_rwsize`, `smb2_max_trans`, and `smb2_old_rwsize`.
- Selects the best supported dialect from `0x202`, `0x210`, `0x300`, `0x302`, `0x311`, bounded by server min/max protocol configuration.
- Parses SMB 3.1.1 negotiate contexts for preauth integrity, encryption capabilities, and signing capabilities, rejecting duplicate or malformed contexts.
- Chooses SHA-512 preauth, a configured encryption cipher, and a configured signing algorithm, with compatibility defaults for older dialects.
- Initializes preauth, signing, encryption mechanisms and socket buffer sizes during negotiation.
- Computes SMB 3.1.1 preauth hashes over request and response messages.
- Drops `VALIDATE_NEGOTIATE_INFO` for SMB 3.1.1, unsigned SMB3 non-encrypted validation, mismatched client security mode/capabilities/GUID, or changed selected dialect.

Important dependencies:
- Protocol encode/decode: `smb_mbc_decodef`, `smb_mbc_encodef`, `smb2_encode_header`, `smb2sr_put_error`.
- Crypto setup: `smb31_preauth_init_mech`, `smb31_preauth_sha512_calc`, `smb2_sign_init_mech`, `smb3_encrypt_init_mech`.
- Session state: `smb_session_t` dialect, capabilities, credits, new request dispatch function, preauth/encryption/signing IDs.

Notable details:
- `SMB2_NEGOTIATE_MAX_DIALECTS` is 64 to match Windows behavior.
- SMB 2.x capabilities are returned as server-supported capabilities, while SMB 3.x capabilities are mostly server/client intersection.
- SMB 3.1.1 negotiate context parsing intentionally gathers data for DTrace before validation errors are returned.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_negotiate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_ofile.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_ofile.c

Provides helper routines for SMB2 open-file metadata queries.

Key behavior:
- `smb2_ofile_getattr()` dispatches attribute reads to disk/printer nodes via `smb_node_getattr()` or pipe handles via `smb_opipe_getattr()`.
- `smb2_ofile_getstd()` fills delete-on-close and directory flags for `FileStandardInformation`.
- `smb2_ofile_getname()` obtains share-relative names from disk/printer nodes or pipe names and records Unicode-equivalent name length.

Important dependencies:
- `smb_node_getattr`, `smb_node_getshrpath`, `smb_node_is_dir`.
- `smb_opipe_getattr`, `smb_opipe_getname`.
- `smb_errno2status`.

Notable details:
- Pipe handles are treated as delete-on-close, non-directory objects for standard info.
- Unsupported file types return invalid device/TTY-derived errors.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_ofile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_oplock.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_oplock.c

Implements SMB2 oplock break acknowledgements, oplock break notifications, oplock acquisition, send-break fallback behavior, and durable-handle reconnect state restoration.

Key behavior:
- `smb2_oplock_break_ack()` decodes either oplock break ACK or forwards lease ACKs to `smb2_lease_break_ack()`.
- Converts SMB2 oplock levels to internal `OPLOCK_LEVEL_*` values and validates unsolicited ACKs.
- Updates open-file oplock state under node oplock locks and broadcasts ACK condition variables.
- `smb2_oplock_send_break()` sends asynchronous oplock break notifications, waits for ACKs when required, closes non-durable opens if disconnected, or performs a local ACK fallback.
- `smb2_oplock_acquire()` grants batch/exclusive/shared oplocks when eligible, honors tree settings forcing level-II oplocks, updates durable handle state, and waits asynchronously for break-in-progress cases.
- `smb2_oplock_reconnect()` reconstructs SMB2 oplock or lease state for durable-handle reconnect responses.

Important dependencies:
- Common oplock engine: `smb_oplock_request`, `smb_oplock_ack_break`, `smb_oplock_wait_ack`, `smb_oplock_wait_break`.
- Open/node locking: `node->n_ofile_list`, `node->n_oplock.ol_mutex`.
- Durable handles: `smb2_dh_update_oplock`.
- Transport: `smb_session_send`.

Notable details:
- Lease break handling is deliberately delegated to `smb2_lease.c`.
- If a client cannot receive a required break ACK, the server must locally ACK to clear filesystem-level breaking state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_oplock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_qinfo_file.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_qinfo_file.c

Implements SMB2 file information-class responses for `SMB2_0_INFO_FILE`.

Key behavior:
- `smb2_qinfo_file()` determines which underlying attributes/name/standard info are needed, gathers them, then dispatches by `qi_InfoClass`.
- Supports basic, standard, internal ID, EA size, access, name, normalized name, position, mode, alignment, all-info, alternate name, stream info, pipe info, compression info, network-open info, attribute tags, and file ID information.
- `FileAllInformation` emits the concatenated Windows layout and optionally includes file name data under `smb2_qif_all_get_name`.
- Alternate names are only returned for disk files when short-name support is enabled.
- Stream info delegates to `smb_query_stream_info()`.
- EAs are reported unsupported/no EAs.
- File ID info combines share-root fsid and target file nodeid/fsid.

Important dependencies:
- Helpers from `smb2_ofile.c`.
- Filesystem and stream helpers: `smb_query_shortname`, `smb_query_stream_info`.
- Apple behavior: `smb2_aapl_use_file_ids`, `SMB_SSN_AAPL_CCEXT`.

Notable details:
- The code intentionally mimics Windows behavior, including zeroed `FileNameInformation` inside `FileAllInformation` for newer server behavior.
- Unsupported information classes return `NT_STATUS_INVALID_INFO_CLASS`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_qinfo_file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_qinfo_fs.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_qinfo_fs.c

Implements SMB2 filesystem information-class responses for `SMB2_0_INFO_FILESYSTEM`.

Key behavior:
- Dispatches volume, size, full size, device, attribute, control, object ID, and sector-size information.
- Disk-only classes validate `STYPE_ISDSK`; filesystem attributes can also describe IPC as `"PIPE"`.
- Reports disk filesystem name as `"NTFS"` for compatibility.
- Builds filesystem capabilities from tree flags, including Unicode-on-disk, ACLs, case sensitivity, named streams, quotas, and sparse files.
- Quota control information requires `SMB_TREE_QUOTA`, otherwise returns `NT_STATUS_VOLUME_NOT_UPGRADED`.
- Sector size information derives from `smb_fssize()` but clamps logical sector size with `smb2_max_logical_sector_size` for Hyper-V compatibility.

Important dependencies:
- `smb_fssize`, `smb_tree_has_feature`, tree resource type and flags.
- `smb_mbc_encodef` for wire layouts.

Notable details:
- Object IDs and driver-path/volume-flags classes are not supported.
- Sector-size response reports aligned/no-seek-penalty flags and unknown alignment offsets.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_qinfo_fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_qinfo_quota.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_qinfo_quota.c

Implements optional SMB2 quota query support for `SMB2_0_INFO_QUOTA`.

Key behavior:
- Requires tree quota feature and a disk-backed file handle.
- Decodes quota query flags and SID/start SID lengths from the request.
- Rejects requests containing both SID list and start SID.
- Builds the share root mount path, determines query mode, calculates max quota output, decodes SID input, calls `smb_quota_query()`, and encodes quota entries.
- Treats `NT_STATUS_NO_MORE_ENTRIES` as successful end of enumeration after clearing quota resume state.

Important dependencies:
- Quota subsystem: `smb_quota_max_quota`, `smb_quota_init_sids`, `smb_quota_query`, `smb_quota_encode_quotas`, `smb_quota_free_sids`.
- Tree root path: `smb_node_getmntpath`.

Notable details:
- Unsupported quota-capable trees return `NT_STATUS_INVALID_DEVICE_REQUEST`.
- The implementation mirrors older SMB1 quota transaction behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_qinfo_quota.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_qinfo_sec.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_qinfo_sec.c

Implements SMB2 security descriptor query handling.

Key behavior:
- Requires disk-backed file handles.
- Clears SACL requests when the target tree ACL type is not `ACE_T`.
- Reads the security descriptor with `smb_sd_read()`, computes encoded length, and either returns it or reports the required size.
- On insufficient output buffer, encodes a 4-byte required-size value and returns `NT_STATUS_BUFFER_TOO_SMALL`.

Important dependencies:
- Security descriptor conversion: `smb_sd_read`, `smb_sd_len`, `smb_encode_sd`, `smb_sd_term`.
- Error wrapping in `smb2_query_info.c` handles SMB 3.1.1 error-context specifics.

Notable details:
- Empty/zero-length descriptors are treated as invalid security descriptors.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_qinfo_sec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_query_dir.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_query_dir.c

Implements SMB2 directory enumeration.

Key behavior:
- Decodes query directory requests, optional Unicode pattern, file index, flags, FID, and max output size.
- Supports standard directory formats: directory, full directory, both directory, names, file-id-both, and file-id-full.
- Uses a private pseudo information class for Apple AAPL readdir extensions when enabled.
- Opens or reuses an `smb_odir_t`, handles reopen/restart/index/continuation positioning, and tracks seek position.
- Limits output by `smb2_max_trans`, estimated entry count, `smb2_find_max`, and single-entry requests.
- Reads entries with `smb_odir_read_fileinfo()`, encodes them, and rewinds enumeration if a read entry cannot fit into the output buffer.
- Patches the final `NextEntryOffset` to zero.

Important dependencies:
- Directory abstraction: `smb_odir_openfh`, `smb_odir_reopen`, `smb_odir_resume_at`, `smb_odir_read_fileinfo`.
- Apple extension helpers: `smb2_aapl_get_macinfo`, session AAPL flags.
- Name/shortname encoding via SMB message buffers.

Notable details:
- `SMB2_QDIR_FLAG_SINGLE` maps end-of-search to `NT_STATUS_NO_SUCH_FILE`.
- Apple compact file IDs can be zeroed depending on `smb2_aapl_use_file_ids`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_query_dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_query_info.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_query_info.c

Top-level SMB2 `QUERY_INFO` dispatcher.

Key behavior:
- Decodes fixed request fields, output length, optional input buffer, additional info, flags, and FID.
- Caps output by `smb2_max_trans` and uses `sr->raw_data` as the response payload buffer.
- Looks up the FID and dispatches to file, filesystem, security, or quota query handlers.
- Encodes successful responses with data offset and length.
- Special-cases advisory `NT_STATUS_BUFFER_OVERFLOW`.
- Formats `NT_STATUS_BUFFER_TOO_SMALL` and `NT_STATUS_INFO_LENGTH_MISMATCH` differently for SMB 3.1.1 error context behavior.

Important dependencies:
- `smb2_qinfo_file`, `smb2_qinfo_fs`, `smb2_qinfo_sec`, `smb2_qinfo_quota`.
- `MBC_SHADOW_CHAIN`, `smb2sr_lookup_fid`, `smb2sr_put_error*`.

Notable details:
- Security-descriptor buffer-too-small is expected to carry required-size data.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_query_info.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_read.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_read.c

Implements SMB2 read handling, including optional zero-copy read support.

Key behavior:
- Decodes SMB2 read requests and validates structure size, length, minimum count, offset, FID, channel, and flags.
- Rejects reads larger than `smb2_max_rwsize`; zero-length reads return success with no data.
- For disk files, rejects directory reads, checks byte-range locks, optionally requests VFS zero-copy buffers, and falls back to allocated mbufs.
- For IPC pipes, reads through `smb_opipe_read()`.
- Handles unbuffered reads by translating the request to `FRSYNC` when `smb_allow_unbuffered` allows it.
- Trims mbufs to transferred length, attaches them to `sr->raw_data`, and updates file seek position.
- Fails with `NT_STATUS_END_OF_FILE` if transferred bytes are below `MinCount`.

Important dependencies:
- Filesystem read path: `smb_fsop_read`, `smb_fsop_reqzcbuf`, `smb_fsop_retzcbuf`.
- Buffering: `smb_mbuf_allocate`, `smb_mbuf_alloc_ext`, `MBC_ATTACH_MBUF`.
- Locking: `smb_lock_range_access`.

Notable details:
- `smb_xuio_t` reference counting ensures borrowed VFS zero-copy buffers are returned only after all external mbufs release them.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_read.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_session_setup.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_session_setup.c

Implements SMB2 session setup dispatch.

Key behavior:
- Decodes session setup request fields and security blob.
- Rejects required-encryption configurations when the negotiated dialect/client capabilities cannot support encryption.
- Rejects SMB3 session binding/multi-channel because it is unsupported.
- Delegates authentication to `smb_authenticate_ext()`.
- On success, sets guest/null/encrypt-data session flags and raises session credits.
- Logs off a previous session ID when supplied by the client and different from the current session.
- Encodes response security blob for success or more-processing-required.

Important dependencies:
- Authentication: `smb_authenticate_ext`.
- Credit management: `smb2_ss_adjust_credits`.
- Server/user encryption policy fields.

Notable details:
- Session setup request capabilities are intentionally ignored because negotiate capabilities are authoritative.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_session_setup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_set_info.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_set_info.c

Top-level SMB2 `SET_INFO` dispatcher.

Key behavior:
- Decodes info type/class, input buffer offset/length, additional info, and FID.
- Shadows the input buffer into `sinfo.si_data`.
- Rejects input buffers larger than `smb2_max_trans`.
- Looks up the FID, sets request credentials from the open file, and dispatches to file, filesystem, security, or quota set-info handlers.
- Encodes a minimal success response.

Important dependencies:
- `smb2_setinfo_file`, `smb2_setinfo_fs`, `smb2_setinfo_sec`, `smb2_setinfo_quota`.
- `smb2sr_lookup_fid`, request-scoped buffers.

Notable details:
- No output payload is expected for successful `SET_INFO`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_set_info.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_setinfo_file.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_setinfo_file.c

Implements SMB2 file information set operations.

Key behavior:
- Dispatches file set-info classes for basic info, rename, hard link, disposition, position, full EA, mode, allocation size, EOF, pipe info, valid data length, and short name.
- Restricts most operations to disk/printer handles; pipe handles only accept `FilePipeInformation`.
- Rename and link decode replace flags, root directory, and Unicode target name, reject rootdir-based relative opens, and call common setinfo helpers.
- Position updates `of->f_seek_pos` under the open-file mutex.
- Full EAs are unsupported.
- Mode currently decodes but does not store write-through/sequential/no-buffering mode.
- Valid data length frees/zeroes from EOD to EOF via `smb_fsop_freesp()`.
- Short-name changes are not allowed, even when short names are supported.

Important dependencies:
- Common setters: `smb_set_basic_info`, `smb_set_disposition_info`, `smb_set_alloc_info`, `smb_set_eof_info`, `smb_setinfo_rename`, `smb_setinfo_link`.
- Filesystem operation: `smb_fsop_freesp`.

Notable details:
- Several Windows features are accepted only enough to return compatible no-op or explicit unsupported statuses.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_setinfo_file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_setinfo_fs.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_setinfo_fs.c

Implements SMB2 filesystem set-info dispatch.

Key behavior:
- Supports `FileFsControlInformation` as a successful disk-tree no-op.
- Rejects `FileFsObjectIdInformation` with `NT_STATUS_INVALID_PARAMETER`.
- All other classes return `NT_STATUS_INVALID_INFO_CLASS`.

Important dependencies:
- Tree resource type validation through `STYPE_ISDSK`.

Notable details:
- Object IDs cannot be changed, matching the referenced FSCC behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_setinfo_fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_setinfo_quota.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_setinfo_quota.c

Implements optional SMB2 quota set support.

Key behavior:
- Requires quota-enabled tree, disk-backed file handle, and admin user.
- Resolves share root mount path.
- Decodes quota records from the set-info input buffer.
- Sends quota changes to `smb_quota_set()` and returns its NT status reply.
- Frees quota list, root path, and releases the file reference before returning.

Important dependencies:
- Quota subsystem: `smb_quota_decode_quotas`, `smb_quota_set`, `smb_quota_free_quotas`.
- Authorization: `smb_user_is_admin`.
- `smb_node_getmntpath`.

Notable details:
- Unsupported or non-admin requests fail before calling quota service.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_setinfo_quota.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_setinfo_sec.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_setinfo_sec.c

Implements SMB2 security descriptor set handling.

Key behavior:
- Requires disk-backed file handles and writable media.
- Clears SACL requests on non-`ACE_T` filesystems.
- Returns success for empty effective security-info masks.
- Decodes the incoming security descriptor and validates requested owner/group fields are present.
- Avoids writing security descriptors on system nodes.
- Writes security descriptors through `smb_sd_write()` and releases descriptor resources.

Important dependencies:
- `smb_decode_sd`, `smb_sd_write`, `smb_sd_term`.
- Read-only media check: `SMB_TREE_IS_READONLY`.

Notable details:
- Missing owner/group in a descriptor that claims to set those fields returns `NT_STATUS_INVALID_PARAMETER`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_setinfo_sec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_signing.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_signing.c

Implements SMB2/SMB3 message signing.

Key behavior:
- Initializes per-session signing mechanism based on negotiated signing algorithm: HMAC-SHA256, AES-CMAC, or AES-GMAC.
- Derives per-user signing keys from the session key:
  - SMB2 uses the first 16 bytes, padded/truncated.
  - SMB3 uses KDF labels/contexts.
  - SMB 3.1.1 uses the preauth hash value as KDF context.
- Enables/checks signing flags based on client and server security modes.
- Builds AES-GMAC IVs from message ID, direction, and cancel flag.
- Computes signatures over the SMB2 header plus payload while zeroing the signature field in a temporary header copy.
- Verifies incoming request signatures and writes outgoing reply signatures.

Important dependencies:
- KDF and MAC helpers: `smb3_kdf`, `smb2_mac_uio`, `smb2_sign_init_hmac_param`, `smb3_sign_init_gmac_param`.
- Session/user signing state and keys.

Notable details:
- Commands with zero session ID are not signature-checked.
- If a required crypto mechanism is unavailable, verification fails and replies may be left unsigned, likely causing client disconnect.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_signing.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_tree_connect.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_tree_connect.c

Implements SMB2 tree connect dispatch.

Key behavior:
- Decodes share path and delegates actual share connection to `smb_tree_connect()`.
- For SMB 3.1.1 non-anonymous/non-guest users, drops the connection if the request is neither signed nor encrypted.
- Encodes share type, share flags, share capabilities, and granted tree access.
- Reports encrypted-share flag when tree encryption is enabled.
- Reports DFS and continuous-availability share capabilities from tree flags.

Important dependencies:
- Core share connection: `smb_tree_connect`.
- Tree state: resource type, encryption mode, flags, access mask.

Notable details:
- Reject-unencrypted-access policy is shared with SMB1 in `smb_tree_connect_core`, not fully enforced here.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_tree_connect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_tree_disconn.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_tree_disconn.c

Implements SMB2 tree disconnect.

Key behavior:
- Validates the fixed request structure.
- Disconnects the current tree and cancels outstanding requests for that tree.
- Encodes a minimal successful tree-disconnect response.

Important dependencies:
- `smb_tree_disconnect`, `smb_session_cancel_requests`.

Notable details:
- Dispatch is expected to have already resolved `uid_user` and `tid_tree`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_tree_disconn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_write.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_write.c

Implements SMB2 write handling.

Key behavior:
- Decodes write request fields, skips padding, and shadows write payload into a VDB.
- Rejects writes larger than `smb2_max_rwsize`.
- Looks up FID before DTrace start probe and records read/write parameters.
- Disk/printer writes check byte-range locks, translate unbuffered or write-through flags to `FSYNC`, call `smb_fsop_write()`, break read-cache oplocks, and notify modifications on first write.
- IPC writes use `smb_opipe_write()` unless unbuffered/write-through flags are set.
- Updates open-file seek position and encodes transferred-byte count.

Important dependencies:
- Filesystem write path: `smb_fsop_write`.
- Locking/oplocks: `smb_lock_range_access`, `smb_oplock_break_WRITE`.
- Notifications: `smb_node_notify_modified`.

Notable details:
- `smb_allow_unbuffered` is global and shared with read-side behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_write.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb31_preauth.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb31_preauth.c

Implements SMB 3.1.1 preauth integrity hashing.

Key behavior:
- Locates KCF SHA-512 mechanism and stores it in the SMB session.
- Provides SHA-512 digest init/update/final wrappers over KCF.
- Computes the rolling preauth hash as `SHA512(previous_hash || message_bytes)` over an mbuf chain.
- Frees the session preauth mechanism on teardown.

Important dependencies:
- Kernel crypto framework: `crypto_mech2id`, `crypto_digest_init`, `crypto_digest_update`, `crypto_digest_final`.
- Session fields: `preauth_mech`, `smb31_preauth_hashid`, rolling hash buffers.

Notable details:
- Digest update failure cancels the crypto context.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb31_preauth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb3_encrypt.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb3_encrypt.c

Implements SMB3 encryption/decryption orchestration around SMB3 transform headers.

Key behavior:
- Initializes nonce salt/fixed bytes per user and generates monotonically unique nonces until an overflow guard threshold.
- Initializes AES-CCM or AES-GCM session mechanism from negotiated cipher ID.
- Derives per-user encryption/decryption keys:
  - SMB 3.1.1 uses cipher-specific key size and preauth-hash KDF contexts.
  - Older SMB3 uses AES-128 CCM labels/contexts.
- Decodes and validates SMB3 transform headers.
- Decrypts incoming encrypted requests by authenticating transform header fields, looking up transform session ID, validating key length, and decrypting ciphertext plus signature tag into cleartext.
- Encrypts outgoing replies by generating nonce, encoding transform header, encrypting cleartext into ciphertext, and patching the resulting signature/tag into the transform header.
- Frees session encryption mechanism on teardown.

Important dependencies:
- Crypto backend: `smb3_crypto_init_ccm_param`, `smb3_crypto_init_gcm_param`, `smb3_encrypt_init`, `smb3_decrypt_init`, `smb3_encrypt_uio`, `smb3_decrypt_uio`.
- KDF: `smb3_kdf`.
- Session/user transform lookup: `smb_session_lookup_ssnid`.

Notable details:
- Decrypt errors return distinct negative values for DTrace visibility, and any non-zero result drops the connection.
- Transform header protocol ID is asserted earlier in request dispatch.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb3_encrypt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb3_encrypt_kcf.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb3_encrypt_kcf.c

Kernel KCF backend for SMB3 encryption helpers.

Key behavior:
- Finds AES-CCM and AES-GCM KCF mechanisms.
- Initializes CCM parameters with MAC size, nonce, auth data, and data size.
- Initializes GCM parameters with IV, tag bits, and AAD.
- Stores raw crypto keys in `smb_enc_ctx_t`.
- Encrypts/decrypts whole messages using KCF `crypto_encrypt()` / `crypto_decrypt()` over UIO scatter/gather data.
- Provides a context cleanup wrapper.

Important dependencies:
- Kernel crypto framework: `crypto_mech2id`, `crypto_encrypt`, `crypto_decrypt`, `crypto_cancel_ctx`.
- `smb_kcrypt.h` crypto abstractions.

Notable details:
- This file intentionally contains almost no SMB protocol knowledge beyond shared crypto constants.
- Crypto context templates are marked as future work.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb3_encrypt_kcf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb3_kdf.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb3_kdf.c

Implements SMB3 key derivation using NIST SP800-108 counter-mode KDF with HMAC-SHA256.

Key behavior:
- Builds `counter || label || 0x00 || context || L` with big-endian counter and bit-length.
- Enforces label and context maximum sizes matching SMB3 use cases.
- Uses SMB HMAC mechanism setup and raw MAC helper to generate derived keys.
- Supports 128-bit and 256-bit derived key lengths through caller-supplied `keylen`.

Important dependencies:
- `smb2_hmac_getmech`, `smb2_sign_init_hmac_param`, `smb2_mac_raw`.

Notable details:
- Comments document the SMB 3.0.2 and SMB 3.1.1 labels/contexts for signing, application, encryption, and decryption keys.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb3_kdf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_acl.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_acl.c

Kernel SMB ACL conversion and ACL utility implementation.

Key behavior:
- Allocates/frees SMB wire-format ACL structures and computes wire lengths.
- Validates ACL revision and ACE layout, currently rejecting object-specific ACL revision handling.
- Sorts DACL ACEs into Windows-preferred order using direct/inherited allow/deny groups.
- Converts ZFS `acl_t` ACE ACLs to Windows SMB ACLs using batched ID-to-SID mapping.
- Converts Windows SMB ACLs to ZFS ACLs using batched SID-to-ID mapping, handling well-known owner/group/everyone SIDs.
- Represents null and empty DACLs with synthetic ZFS ACLs.
- Allocates, frees, merges, and splits native filesystem ACLs.
- Implements Windows inheritance rules for new child objects, including creator owner/group handling and default DACL fallback.
- Converts between `vsecattr_t` and `acl_t`.
- Provides ACE type classification, generic-mask-to-file-specific translation, and flag conversion between Windows and ZFS forms.

Important dependencies:
- ID mapping: `smb_idmap_batch_create`, `smb_idmap_batch_getsid`, `smb_idmap_batch_getid`, `smb_idmap_batch_getmappings`.
- SID helpers: `smb_sid_dup`, `smb_sid_free`, `smb_sid_len`, `smb_sid_isvalid`, `smb_sid_tostr`.
- Solaris ACL helpers: `acl_alloc`, `acl_free`, `ace_trivial`, `ksort`, `cmp2acls`.

Notable details:
- Default inherited DACL grants owner and local system full access when no inheritable DACL exists.
- Empty DACL is simulated with owner implicit permissions rather than everyone-deny to avoid problematic deny precedence.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_alloc.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_alloc.c

Implements SMB memory allocation wrappers and request-scoped temporary storage.

Key behavior:
- Adds an internal header before every allocation with magic, size, owning request pointer, and list node.
- Provides global allocation/free/reallocation APIs with optional zeroing.
- Provides request-scoped `smb_srm_*` APIs that automatically link allocations into `sr->sr_storage`.
- `smb_srm_fini()` frees all request-scoped allocations and destroys the storage list.
- Reallocation returns original pointer when shrinking, optionally zeroes truncated bytes, and allocates/copies/frees when growing.

Important dependencies:
- Kernel memory allocator: `kmem_alloc`, `kmem_zalloc`, `kmem_free`.
- illumos list API.

Notable details:
- `smb_free()` asserts the caller-provided request matches the allocation owner.
- Header magic catches invalid frees in debug/assert builds.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_authenticate.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_authenticate.c

Implements SMB authentication support for SMB1 and SMB2 session setup.

Key behavior:
- Old-style SMB1 authentication creates a user, opens an auth socket, sends client info, sends legacy logon request, then imports an auth token.
- Extended-security authentication creates or finds a logging-on user across multi-step session setup, forwards security blobs to userland auth service, handles continue/done/error replies, and imports the final token.
- SMB 3.1.1 updates preauth hash across session setup messages and stores per-user preauth hash values.
- Token import decodes XDR token data, creates credentials, translates privileges, logs on the SMB user, initializes SMB3 encryption keys, and initializes signing for non-anonymous/non-guest users.
- Auth socket communication is cancellable through request state transitions and `smb_authsock_cancel()`.
- Auth socket concurrency is threshold-limited, uses send/receive timeouts, and connects to an AF_UNIX smbd auth service socket.
- Provides send/recv wrappers that require exact message sizes and map failures to RPC/NT statuses.
- Closes auth sockets and releases threshold slots on user cleanup.

Important dependencies:
- Userland auth protocol: `smb_lsa_msg_hdr_t`, `LSA_MTYPE_*`, XDR helpers.
- User/session management: `smb_user_new`, `smb_user_logon`, `smb_user_logoff`, `smb_session_lookup_uid_st`.
- Credential/token helpers: `smb_cred_create`, `smb_token_xdr`, `smb_token_query_privilege`.
- Security setup: `smb2_sign_begin`, `smb_sign_begin`, `smb3_encrypt_begin`, `smb31_preauth_sha512_calc`.

Notable details:
- Authentication service communication errors are expected to be rare but can occur under auth service saturation.
- Guest/anonymous users still get encryption state initialized because Windows may send encrypted requests for them.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_authenticate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_close.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_close.c

Implements SMB1 close and close-and-tree-disconnect commands.

Key behavior:
- Pre-decode functions read FID and optional timestamp and start DTrace probes.
- `smb_com_close()` looks up the open file, converts local timestamp to GMT, closes the ofile, and encodes an empty result.
- `smb_com_close_and_tree_disconnect()` closes the file, disconnects the tree, cancels outstanding tree requests, and encodes an empty result.
- Post handlers end DTrace probes.

Important dependencies:
- SMB1 request decode/encode: `smbsr_decode_vwv`, `smbsr_encode_empty_result`.
- File/tree/session operations: `smbsr_lookup_file`, `smb_ofile_close`, `smb_tree_disconnect`, `smb_session_cancel_requests`.
- Time conversion: `smb_time_local_to_gmt`.

Notable details:
- Failure to set requested timestamp is documented as not requiring a server error, but actual close behavior is delegated to `smb_ofile_close()`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_close.c -->
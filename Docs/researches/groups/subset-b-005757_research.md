# subset-b-005757 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/reparse.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/reparse.c

## Purpose
`reparse.c` implements CIFS/SMB reparse point support for Linux special-file semantics. It creates and parses native Windows symlinks, NFS-style reparse special files, WSL/LX reparse points, and AF_UNIX socket tags, then converts parsed reparse metadata into `struct cifs_fattr` file type, device, uid/gid, and symlink target state.

## Important APIs, types, and functions
The exported entry points are `create_reparse_symlink`, `mknod_reparse`, `parse_reparse_point`, `smb2_parse_native_symlink`, `smb2_get_reparse_point_buffer`, and `cifs_reparse_point_to_fattr`. Creation helpers include `create_native_symlink`, `create_native_socket`, `mknod_nfs`, `mknod_wsl`, `nfs_set_reparse_buf`, `wsl_set_reparse_buf`, `wsl_set_xattrs`, and `ea_create_context`. Parsing helpers include `parse_reparse_nfs`, `parse_reparse_native_symlink`, `parse_reparse_wsl_symlink`, `wsl_to_fattr`, and `posix_reparse_to_fattr`.

## Control flow
Symlink creation dispatches by mount symlink type: native Windows symlink, NFS reparse point, or WSL reparse point. Native symlink creation converts Linux paths to SMB/NT representation, optionally maps absolute `/symlinkroot/<drive>/...` paths into `\??\X:\...`, probes relative targets to decide file-vs-directory symlink type, builds a `reparse_symlink_data_buffer`, and calls the dialect operation `create_reparse_inode`. `mknod_reparse` prefers native AF_UNIX sockets unless disabled, then dispatches to NFS or WSL creation based on `ctx->reparse_type`.

Parsing starts with `parse_reparse_point`, which switches on `ReparseTag`. NFS parsing validates data lengths and UTF-16 symlink target content. Native symlink parsing validates substitute-name bounds, then `smb2_parse_native_symlink` translates NT absolute, share-root-relative, and ordinary relative/POSIX-style targets into Linux paths. WSL symlink parsing accepts only version 2 UTF-8 targets and rejects embedded NUL bytes.

## State and persistence
The durable state is the reparse buffer and, for WSL files, create-time EAs such as `$LXUID`, `$LXGID`, `$LXMOD`, and `$LXDEV` stored on the server. Runtime state is held in transient `cifs_open_info_data`, `kvec` buffers, allocated target strings, and `cifs_fattr`. `cifs_reparse_point_to_fattr` is the main bridge from persisted server tag/data back into Linux inode mode and device metadata.

## Dependencies and integration points
This file depends on CIFS mount context, path conversion helpers, SMB2 create contexts, common reparse tag definitions, NLS conversion, server dialect ops, and `cifs_open_info_data`. It is called from common inode creation and lookup/open paths through `server->ops->create_reparse_inode`, `query_reparse_point`, and `get_reparse_point_buffer`. SMB1 also integrates with these routines through `smb1ops.c`.

## Risks and test signals
Risks include malformed server buffers, UTF-16/UTF-8 length mistakes, embedded NUL targets, absolute NT path conversion gaps, symlinkroot misconfiguration, target type misdetection for unresolved relative symlinks, WSL EA alignment/length errors, and mismatches between reparse tag type and `$LXMOD` file type. Test signals should cover native absolute and relative symlinks, share-root-relative symlink conversion, NFS char/block/fifo/socket/link buffers, WSL symlink/device metadata, missing `$LXDEV` for devices, invalid lengths, unsupported tags, and permission-denied target probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/reparse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/reparse.h -->
# sources/distributed-fs/ceph-client/fs/smb/client/reparse.h

## Purpose
`reparse.h` is the CIFS reparse-point interface header. It declares reparse creation/parsing entry points and provides small conversion helpers used by lookup, inode validation, and metadata translation.

## Important APIs, types, and functions
The header defines `REPARSE_SYM_PATH_MAX` and the internal sentinel `IO_REPARSE_TAG_INTERNAL`. Inline helpers include `reparse_mkdev`, `wsl_make_kuid`, `wsl_make_kgid`, `reparse_mode_nfs_type`, `reparse_mode_wsl_tag`, `reparse_inode_match`, and `cifs_open_data_reparse`. Declarations expose `cifs_reparse_point_to_fattr`, `create_reparse_symlink`, `mknod_reparse`, and `smb2_get_reparse_point_buffer`.

## Control flow
Callers use the mode-to-tag helpers before creating special-file reparse points, use `cifs_open_data_reparse` to normalize open-info attributes, and use `reparse_inode_match` during inode revalidation. The inline uid/gid helpers honor mount overrides before constructing kernel ids from WSL metadata.

## State and persistence
The header itself stores no state. It defines how persisted reparse tag, ctime, and WSL EA values are interpreted. `reparse_inode_match` treats tag plus ctime as the cache coherency signal, except for the internal sentinel used when full reparse data is unavailable.

## Dependencies and integration points
It depends on VFS mode bits, uid/gid types, CIFS mount flags, `cifsglob.h`, `fs_context.h`, and `smbfsctl.h`. It is included by reparse creation/parsing code and SMB1 operations that need to create or inspect reparse-backed inodes.

## Risks and test signals
Risks include stale inode matching if a server changes reparse data without ctime changes, wrong major/minor ordering for WSL devices, invalid uid/gid mapping under user namespaces, and accidentally matching `IO_REPARSE_TAG_INTERNAL` as a real tag. Test signals include inode revalidation after tag/data changes, uid/gid override mounts, WSL device decoding, and open-info paths with both POSIX and all-info layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/reparse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/rfc1002pdu.h -->
# sources/distributed-fs/ceph-client/fs/smb/client/rfc1002pdu.h

## Purpose
`rfc1002pdu.h` defines NetBIOS-over-TCP session service packet types and the packed RFC 1002 session packet layout used around SMB session transport framing.

## Important APIs, types, and functions
The main type is `struct rfc1002_session_packet`, whose header uses big-endian length fields and whose trailer union models session requests, retarget responses, negative responses, and SMB message payloads. Constants define session packet types, the length-extension flag, negative session response error codes, and `DEFAULT_CIFS_CALLED_NAME`.

## Control flow
The file contains no executable code. Transport code includes these definitions when building or interpreting RFC 1002 session requests/responses and message wrappers before the SMB header begins.

## State and persistence
No persistent state exists. The structure describes transient network packets. The important state invariant is that this framing is big-endian, unlike SMB/CIFS message bodies.

## Dependencies and integration points
It integrates with low-level CIFS transport/session setup code and NetBIOS name-based connection paths. It deliberately omits datagram service definitions because the client resolves server names via DNS, IP address, or hosts-style mechanisms.

## Risks and test signals
Risks include endian mistakes in length/retarget fields, mishandling length extension for larger payloads, and treating keepalives or positive responses as carrying SMB trailers. Test signals include RFC 1002 session request/positive/negative/retarget parsing, keepalive handling, and large SMB message length encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/rfc1002pdu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/sess.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/sess.c

## Purpose
`sess.c` contains shared CIFS session helpers used across SMB dialects. It manages SMB3 multichannel session channels and builds/validates NTLMSSP negotiate/challenge/authenticate blobs, then selects the authentication mechanism compatible with server negotiation and mount security settings.

## Important APIs, types, and functions
Multichannel APIs include `is_ses_using_iface`, `cifs_ses_get_chan_index`, `cifs_chan_set_in_reconnect`, `cifs_chan_clear_in_reconnect`, `cifs_chan_set_need_reconnect`, `cifs_chan_clear_need_reconnect`, `cifs_chan_needs_reconnect`, `cifs_chan_is_iface_active`, `cifs_try_adding_channels`, `cifs_decrease_secondary_channels`, and `cifs_chan_update_iface`. `cifs_ses_add_channel` is the internal channel opener. NTLMSSP helpers include `decode_ntlmssp_challenge`, `build_ntlmssp_negotiate_blob`, `build_ntlmssp_smb3_negotiate_blob`, `build_ntlmssp_auth_blob`, and `cifs_select_sectype`.

## Control flow
Channel addition checks max channel count, SMB3 dialect, and server multichannel capability, then iterates advertised interfaces by RDMA compatibility, active state, RSS capability, and speed weight. A new channel builds a temporary fs context, opens a TCP session, attaches it to `ses->chans`, negotiates protocol, and performs session setup under `session_mutex`; failure unwinds channel state and references. Channel decrease terminates secondary channels beyond the new limit and adjusts iface counters/reconnect bitmasks. Channel update replaces inactive interface bindings and updates the server destination address.

NTLMSSP flow builds a negotiate blob with requested flags, validates challenge signature/message type/server flags/key-size support/target info bounds, then builds authenticate data with NTLMv2 response, domain/user/workstation strings, optional key exchange ciphertext, and version information.

## State and persistence
Session state is runtime-only: channel array entries, channel reconnect bitmask, iface list refcounts and weights, server destination addresses, NTLMSSP client/server flags, challenge key, session/auth keys, sequence state, and selected security type. No on-disk persistence exists.

## Dependencies and integration points
The file integrates with TCP session management, server interface discovery, SMB3 multichannel negotiation, `cifs_negotiate_protocol`, `cifs_setup_session`, NTLMSSP crypto helpers, SPNEGO/Kerberos selection policy, NLS conversion, global CIFS security flags, and server dialect operation tables.

## Risks and test signals
Risks include lock ordering between channel and interface locks, reference leaks on failed channel setup, stale reconnect bits, RDMA/non-RDMA channel mixing, weak NTLMSSP downgrade when key exchange is absent, target-info bounds errors, and security selection returning a method unsupported by the negotiated flavor. Test signals include weighted interface distribution, RSS reuse, channel failure unwind, disabling multichannel, inactive iface replacement, NTLMSSP malformed challenges, forced signing without server sign support, anonymous auth, and unspecified security fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/sess.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb1debug.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/smb1debug.c

## Purpose
`smb1debug.c` provides SMB1-specific debug dumping for CIFS packets when deeper debug support is compiled in.

## Important APIs, types, and functions
The single exported function is `cifs_dump_detail(void *buf, size_t buf_len, struct TCP_Server_Info *server)`. Under `CONFIG_CIFS_DEBUG2` it reads `struct smb_hdr` fields and optionally prints the calculated SMB size after running the dialect `check_message` callback.

## Control flow
In debug builds, the function logs command, CIFS error, flags, flags2, MID, PID, and word count. If the server operation's `check_message` accepts the buffer, it logs the buffer pointer and calculated SMB size. In non-debug builds the function is effectively empty.

## State and persistence
There is no state. Output is diagnostic logging only.

## Dependencies and integration points
It depends on `smb1proto.h`, `cifsproto.h`, `cifs_debug.h`, and the server operation callbacks `check_message` and `calc_smb_size`. `smb1ops.c` wires this into `smb1_operations.dump_detail`.

## Risks and test signals
Risks are low but include debug dereference of malformed or too-short buffers and confusion if `server->ops` is incomplete. Test signals are debug builds receiving valid SMB1 PDUs, malformed PDUs, and verifying that non-debug builds compile without runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb1debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb1encrypt.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/smb1encrypt.c

## Purpose
`smb1encrypt.c` implements SMB1 message signing and signature verification using the NTLM/CIFS session key and MD5-based SMB1 signing rules.

## Important APIs, types, and functions
The exported functions are `cifs_sign_rqst` and `cifs_verify_signature`. Internal `cifs_calc_signature` initializes an MD5 context with `server->session_key.response` and delegates request hashing to `__cifs_calc_signature`.

## Control flow
Signing skips packets without the security-signature flag or when negotiation is needed. Before session establishment it writes the dummy `BSRSPYL` signature. After session establishment it writes the current sequence number into the SMB header, advances expected response and next request sequence numbers, calculates the signature, and copies the first eight bytes into the header. Verification ignores pre-session packets and oplock-release lock requests, saves the server signature, writes the expected response sequence into the header, recalculates the signature under the server lock, and compares with `crypto_memneq`.

## State and persistence
The file mutates transient SMB request/response headers and runtime `server->sequence_number`. It consumes the runtime session key established during session setup. No durable state is written.

## Dependencies and integration points
It depends on kernel MD5 helpers, FIPS mode, crypto constant-time comparison, common CIFS signature hashing, SMB1 header structures, and server locking. It is used by SMB1 transport send/receive paths through `smb1_operations`.

## Risks and test signals
Risks include sequence-number drift on send failures or cancel requests, signing disabled in FIPS mode, missing session key material, dummy signature handling during setup, and verification over a mutated response buffer. Test signals include signed and unsigned mounts, FIPS mode, failed sends after sequence increments, session setup dummy signatures, oplock-break responses, and tampered response signatures returning `-EACCES`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb1encrypt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb1maperror.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/smb1maperror.c

## Purpose
`smb1maperror.c` maps SMB1 DOS/SRV class errors and NTSTATUS errors into Linux negative errno values. It also validates generated mapping tables at init time and exposes lookup wrappers to KUnit tests.

## Important APIs, types, and functions
The primary APIs are `map_smb_to_linux_error`, `map_and_check_smb_error`, and `smb1_init_maperror`. Internal binary search helpers are `search_ntstatus_to_dos_map`, `search_mapping_table_ERRDOS`, and `search_mapping_table_ERRSRV`, with comparators for NTSTATUS and SMB error codes. Generated maps are included from `smb1_err_dos_map.c`, `smb1_err_srv_map.c`, and `smb1_mapping_table.c`.

## Control flow
`map_smb_to_linux_error` returns success for zero status. If the header uses NT status, it first maps NTSTATUS to a DOS class/code and logs selected errors; otherwise it reads the legacy DOS error class/code directly. DOS and SRV classes are binary-searched in their mapping tables. Unmapped or hardware-class errors default to `-EIO`, with additional special cases for `NT_STATUS_NOT_A_REPARSE_POINT` and `NT_STATUS_PRIVILEGE_NOT_HELD`. `map_and_check_smb_error` additionally detects legacy `ERRbaduid` and signals reconnect.

## State and persistence
The mapping tables are static read-only state. Runtime side effects are diagnostic logging and reconnect signaling for session identity errors. There is no persisted state.

## Dependencies and integration points
It depends on SMB1 header definitions, Samba-derived mapping data, NT error constants, `__inline_bsearch`, CIFS logging, reconnect signaling, and the SMB1 transport error path. `smb1ops.c` registers `map_smb_to_linux_error` as the dialect `map_error` operation.

## Risks and test signals
Risks include generated tables becoming unsorted, incomplete NTSTATUS coverage collapsing to `-EIO`, special-case status mappings bypassed by DOS fallback, and reconnect not triggered for status-form authentication failures. Test signals include init sortedness checks, KUnit lookup coverage over every table entry, malformed unknown status codes, `ERRbaduid` reconnect behavior, and reparse/privilege special cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb1maperror.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb1maperror_test.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/smb1maperror_test.c

## Purpose
`smb1maperror_test.c` provides KUnit coverage for the SMB1 error mapping table search wrappers exported when `CONFIG_SMB1_KUNIT_TESTS` is enabled.

## Important APIs, types, and functions
The test helpers are `test_cmp_ntstatus_to_dos_err`, `test_cmp_smb_to_posix_error`, and macro-generated cases `check_search_ntstatus_to_dos_map`, `check_search_mapping_table_ERRDOS`, and `check_search_mapping_table_ERRSRV`. The suite is registered as `smb1_maperror`.

## Control flow
Each generated test iterates every exported table entry, searches by the key field, asserts that the result is non-null, and compares all relevant fields with the expected table element. The suite then runs the three table-search cases.

## State and persistence
The test has no persistent state. It reads exported pointers and counts from `smb1maperror.c`.

## Dependencies and integration points
It depends on KUnit, `smb1proto.h` test-only exports, and NT/DOS error definitions. It is gated by the SMB1 KUnit config and is intended to validate binary search correctness for generated mapping tables.

## Risks and test signals
The test catches unsorted or unsearchable table entries but does not directly test `map_smb_to_linux_error` behavior, logging, default `-EIO`, reconnect signaling, or special NTSTATUS overrides. Useful additions would construct SMB headers for zero status, NTSTATUS mapped/unmapped cases, legacy ERRDOS/ERRSRV, `ERRbaduid`, and reparse/privilege special cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb1maperror_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb1misc.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/smb1misc.c

## Purpose
`smb1misc.c` contains SMB1 header assembly, oplock-break/change-notify recognition, and SMB message size calculation.

## Important APIs, types, and functions
The exported functions are `header_assemble`, `is_valid_oplock_break`, and `smbCalcSize`. `header_assemble` initializes an SMB1 header and base request length. `is_valid_oplock_break` parses unsolicited/async SMB1 notifications. `smbCalcSize` computes length from header, word count, and byte count.

## Control flow
Header assembly zeroes a small header area, writes `0xFFSMB`, command, flags, pid, tree/session identifiers, unicode/status/DFS/case/signing flags, MID, and word count. Oplock handling first recognizes NT transact change notify responses, including data-offset validation. It then handles `SMB_COM_LOCKING_ANDX` oplock-release requests, ignores expected invalid-handle/bad-fid responses, finds the matching session/tree/open file by TID and FID, marks the inode for oplock break, updates file oplock fields, and queues break handling.

## State and persistence
The file mutates outgoing SMB headers and runtime inode/open-file state for oplock breaks. It increments tree statistics and sets `CIFS_INODE_PENDING_OPLOCK_BREAK`. No disk state is written.

## Dependencies and integration points
It depends on SMB1 PDU layouts, global CIFS session and tcon lists, open-file lists, inode private state, statistics counters, and oplock worker queuing. `smb1ops.c` exposes these helpers through the dialect operation table.

## Risks and test signals
Risks include malformed notify offsets, races while scanning sessions and open files, stale oplock breaks after close, incorrect MID/TID/UID fields on assembled requests, and byte-count based size errors. Test signals include header assembly with/without tcon/session/server signing, DFS shares, unicode and non-unicode sessions, valid and invalid change notify responses, oplock breaks for open and recently closed files, and `smbCalcSize` on varying word/byte counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb1misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb1ops.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/smb1ops.c

## Purpose
`smb1ops.c` adapts legacy SMB1/CIFS wire operations to the common CIFS client operation interfaces. It negotiates Unix extensions, controls request cancelation, sizes I/O, queries metadata, wraps open/read/write/close/dir/lock/fs operations, handles reparse-backed special files, and publishes `smb1_operations`/`smb1_values`.

## Important APIs, types, and functions
The public symbol is `reset_cifs_unix_caps`; the main exported data are `smb1_operations` and `smb1_values`. Important internal functions include `send_nt_cancel`, `send_lock_cancel`, `cifs_send_cancel`, `cifs_get_next_mid`, `smb1_negotiate_wsize`, `smb1_negotiate_rsize`, `cifs_query_path_info`, `cifs_query_file_info`, `smb_set_file_info`, `cifs_open_file`, `cifs_query_symlink`, `cifs_get_reparse_point_buffer`, `cifs_make_node`, and `cifs_is_network_name_deleted`.

## Control flow
Mount/reconnect capability negotiation queries server Unix capabilities, masks them according to mount options and saved reconnect behavior, sets POSIX ACL/path flags, and sends the negotiated capability mask back to the server. Request cancelation rewrites an existing request as `SMB_COM_NT_CANCEL` or sends a lock-cancel request for Windows blocking locks. MID allocation walks pending requests to avoid 16-bit MID collisions and forces reconnect under extreme queue pressure.

Metadata query first tries NT `QPathInfo`, falls back to `FindFirst`, then to legacy `SMB_COM_QUERY_INFORMATION`, with wildcard handling for non-Unicode servers. For WSL reparse points it opportunistically fetches `$LXMOD` and `$LXDEV` EAs. File info setting prefers existing writable handles, then path set-info, then open-by-path set-info, then legacy setattr for older servers. Node creation chooses Unix extensions, SFU emulation, or reparse points.

## State and persistence
Runtime state includes negotiated `tcon->fsUnixInfo`, mount flags, credits, request MID counters, tcon statistics, cifs inode attributes/oplock state, open FIDs, search handles, and reconnect flags. Persistent server-side effects include file metadata changes, node creation, EAs for WSL reparse data, compression settings, locks, symlinks, hardlinks, and deletes.

## Dependencies and integration points
This file depends on nearly all SMB1 command helpers declared in `smb1proto.h`, common CIFS inode and transport code, reparse support from `reparse.c`, xattr support, DFS upcalls, ACL helpers, mandatory lock helpers, and common dialect interfaces. `smb1_operations` is the central integration point used by the rest of the CIFS client to dispatch dialect-specific behavior.

## Risks and test signals
Risks include capability drift on reconnect, MID exhaustion or collision, legacy server fallbacks changing semantics, wildcard expansion in non-Unicode query fallbacks, WSL EA length/alignment mistakes, read/write size negotiation over server max buffer limits, lock cancel sequence interactions, file attribute updates on non-NT servers, and share-deleted reconnect marking. Test signals include old LANMAN/non-NT servers, Unix extensions on/off, POSIX paths/ACL options, reparse node creation, WSL special-file lookup, signed sessions, blocking lock cancelation, metadata set fallbacks, directory query close behavior, share deletion errors, and operation-table completeness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb1ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb1pdu.h -->
# sources/distributed-fs/ceph-client/fs/smb/client/smb1pdu.h

## Purpose
`smb1pdu.h` is the SMB1/CIFS protocol data-unit definition header. It centralizes command codes, flags, capabilities, info levels, packed request/response structures, Unix extension records, DFS referral records, ACL/xattr formats, and helper constants used by SMB1 command construction and parsing.

## Important APIs, types, and functions
The file defines protocol selectors, SMB command codes, Trans2/NT Transact subcommands, header sizing constants, crypto/session sizes, SMB flags/flags2, create/open/share options, capability bits, search flags, file information levels, Unix extension capability masks, and many packed structures. Key structures include `SMB_NEGOTIATE_RSP`, `SESSION_SETUP_ANDX`, `TCONX_REQ/RSP`, `OPEN_REQ/RSP`, legacy `OPENX_REQ/RSP`, `READ_REQ/RSP`, `WRITE_REQ/RSP`, `LOCK_REQ`, transaction/NT transaction wrappers, query/set path/file info requests, find-first/find-next records, DFS referral records, `FILE_ALL_INFO`, `FILE_UNIX_BASIC_INFO`, POSIX ACL records, EA records, and `xsymlink`.

## Control flow
There is no executable control flow. The header defines the exact wire layouts consumed by SMB1 command helpers, transport validation, session setup, open/read/write, metadata query/set, directory enumeration, DFS referral parsing, ACL/xattr code, and Unix extension paths.

## State and persistence
The structures describe transient SMB requests/responses and durable server metadata such as file attributes, timestamps, allocation size, Unix mode/uid/gid/device fields, POSIX ACL entries, EAs, and symlink payload formats. Endianness annotations and `__packed` layout are critical persistence/interop contracts.

## Dependencies and integration points
It includes the common SMB1 header and is used by `smb1proto.h`, SMB1 command implementation files, session setup, transport, signing, debug, metadata, DFS, ACL, xattr, and reparse paths. Many common CIFS abstractions convert these SMB1 layouts into SMB2-like internal structures such as `smb2_file_all_info` for shared upper-layer code.

## Risks and test signals
Risks include structure packing drift, duplicate capability macro definitions, endian misuse, flexible-array bounds errors, byte-count/offset mismatches, old-server layout quirks, and info-level constants diverging from command implementations. Test signals include compile-time structure layout assumptions, malformed PDU validation, negotiate/session/tcon interop with old and NT-capable servers, large read/write limits, directory enumeration at multiple info levels, Unix extension metadata round trips, DFS referrals, ACL/xattr requests, and reparse tag attribute parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb1pdu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb1proto.h -->
# sources/distributed-fs/ceph-client/fs/smb/client/smb1proto.h

## Purpose
`smb1proto.h` declares the SMB1/CIFS implementation surface used by SMB1 ops, transport, session setup, metadata, ACL, xattr, and tests. It is gated by `CONFIG_CIFS_ALLOW_INSECURE_LEGACY`, reflecting SMB1's legacy/insecure status.

## Important APIs, types, and functions
It defines `struct cifs_unix_set_info_args`, declares SMB1 command helpers such as negotiate, tree connect/disconnect, session logoff/setup, open/read/write/lock/close, query/set path and file info, find-first/next/close, DFS referral, Unix extension operations, reparse query/create, ACL/xattr helpers, signing/verification, map-error functions, misc helpers, and transport send/receive helpers. It also declares `smb1_operations`, `smb1_values`, `CIFS_SessSetup`, and test-only maperror exports. Inline helpers include `get_mid`, `compare_mid`, `BCC`, `pByteArea`, `get_bcc`, and `put_bcc`.

## Control flow
The header has no runtime flow beyond inline packet field access. Build-time gating removes the SMB1 declarations when insecure legacy SMB1 support is disabled. Callers assemble requests through declared command helpers and use inline helpers to locate the byte-count and byte area within variable-length SMB1 packets.

## State and persistence
No state is stored here. The declared APIs mutate server sessions, tree connections, open files, inodes, server-side metadata, locks, ACLs, EAs, reparse data, and transport request queues in their implementation files.

## Dependencies and integration points
The header integrates SMB1 PDU definitions, common SMB2 PDU definitions needed for shared structs, CIFS global structures, KUnit maperror tests, and the common dialect operation model. It is the main include boundary between SMB1 implementation units and common CIFS code.

## Risks and test signals
Risks include prototype drift from implementations, unsafe byte-area pointer arithmetic on malformed packets, unaligned field access, missing declarations under config combinations, and SMB1-only types leaking into common code. Test signals include all SMB1 config combinations, KUnit maperror exports, sparse/build warnings for prototypes, packet byte-count helper tests, and transport send/receive paths using multi-iov requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb1proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb1session.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/smb1session.c

## Purpose
`smb1session.c` implements SMB1 `SESSION_SETUP_ANDX` authentication flows. It supports legacy NTLMv2, Kerberos/SPNEGO when upcalls are enabled, and raw NTLMSSP extended-security negotiate/authenticate sequences.

## Important APIs, types, and functions
The exported entry point is `CIFS_SessSetup`. Internal state is `struct sess_data`, which carries xid, session, server, NLS table, current auth-state function, result, request length, buffer type, and three kvecs. Important helpers include `cifs_ssetup_hdr`, unicode/ascii string encoders, unicode/ascii response decoders, `sess_alloc_buffer`, `sess_free_buffer`, `sess_establish_session`, `sess_sendreceive`, `sess_auth_ntlmv2`, `sess_auth_kerberos`, `_sess_auth_rawntlmssp_assemble_req`, `sess_auth_rawntlmssp_negotiate`, `sess_auth_rawntlmssp_authenticate`, and `select_sec`.

## Control flow
`CIFS_SessSetup` allocates `sess_data`, selects a security flow using shared `cifs_select_sectype`, and runs auth-state callbacks until no next callback remains. NTLMv2 builds a non-extended-security session setup with NTLMv2 response and account/domain/OS strings, sends it, validates word count, records UID, decodes server strings, and establishes the session. Kerberos obtains a SPNEGO key, sends the service ticket blob with extended security, validates the response blob length, decodes strings, and establishes the session. Raw NTLMSSP first sends a negotiate blob and expects `NT_STATUS_MORE_PROCESSING_REQUIRED`, decodes the challenge, then sends an authenticate blob using the challenge UID and establishes the session.

## State and persistence
Runtime state includes session UID (`Suid`), server OS/NOS/domain strings, server/session key material, auth response buffers, NTLMSSP state, session establishment flag, and SMB1 signing sequence number. Sensitive buffers are zeroed or freed with sensitive free helpers. No persistent storage is used.

## Dependencies and integration points
It depends on SMB1 PDU definitions, shared NTLMSSP blob builders/parsers from `sess.c`, NTLMv2 response setup, SPNEGO upcall keys, NLS conversion, SMB1 transport `SendReceive2`, and SMB1 signing/session state. It is registered as `smb1_operations.sess_setup`.

## Risks and test signals
Risks include BCC length and Unicode alignment errors, response word-count mismatches, security blob length overreads, stale UID across raw NTLMSSP phases, sensitive buffer lifetime mistakes, missing Kerberos support when upcalls are disabled, anonymous login edge cases, and session signing key setup failures. Test signals include NTLMv2, Kerberos, raw NTLMSSP two-step auth, guest and anonymous logins, Unicode and ASCII sessions, malformed word counts, malformed blob lengths, wrong SPNEGO upcall version, signing-required sessions, and cleanup after allocation/send failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/smb1session.c -->

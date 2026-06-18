# subset-b-009820 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clidfs.c -->
# sources/user-network-fs/samba/source3/libsmb/clidfs.c

## Purpose

`clidfs.c` implements client-side SMB connection management around DFS-aware path resolution. It is the layer that opens or reuses `cli_state` connections to `\\server\share`, negotiates protocol/session/tree state, follows DFS referrals, handles MSDFS proxy shares, and converts local paths to or from DFS-root full paths when the lower SMB1/SMB2 file APIs need a particular form.

## Important APIs, Types, and Functions

- `cli_cm_open()` is the public connection-manager entry point. It searches the linked list rooted at `referring_cli` for an existing connection to the requested server/share and opens a new connection only when needed.
- `do_connect()` performs the actual connect: `cli_connect_nb()`, SMB negotiate with SMB2 POSIX negotiate context, session setup, optional encryption enablement, optional MSDFS proxy detection, and tree connect.
- `cli_cm_connect()` wraps `do_connect()`, inserts new DFS child connections into the `cli_state` DLIST, and copies requested UNIX extension capabilities to referral targets.
- `cli_dfs_get_referral_ex()` and `cli_dfs_get_referral()` issue DFS referral requests using SMB2 `FSCTL_DFS_GET_REFERRALS` or SMB1 `TRANSACT2_GET_DFS_REFERRAL`, then parse referral version 3 entries into `struct client_dfs_referral`.
- `cli_resolve_path()` is the main DFS resolver. It probes whether a path is ordinary or covered by DFS, opens IPC$ to fetch referrals, reuses or opens target connections, splices unconsumed path components, and recursively follows nested referrals.
- `cli_check_msdfs_proxy()` detects shares that are actually proxy referrals by temporarily switching to IPC$, asking for a referral, and returning a replacement server/share.
- `cli_dfs_target_check()` strips DFS prefixes for APIs such as rename and hardlink where Windows/NetApp expect target-local paths.
- `smb1_dfs_share_path()` converts paths to DFS-root full paths for SMB1 operations against DFS shares.

Supporting helpers include `cli_cm_force_encryption_creds()`, `cli_cm_find()`, `split_dfs_path()`, `clean_path()`, `cli_dfs_make_full_path()`, `cli_dfs_is_already_full_path()`, `cli_conn_have_dfs()`, and `cli_cm_display()`.

## Control Flow

Connection opening starts in `cli_cm_open()`. A cache hit returns an existing `cli_state`; a cache miss requires credentials and calls `cli_cm_connect()`. `do_connect()` resolves/transports to the server, negotiates SMB dialects, configures SMB2 credit defaults, authenticates with credentials or anonymous fallback where allowed, and enforces encryption when requested. Before tree connect it asks `cli_check_msdfs_proxy()` whether the share is a DFS proxy. If so, it closes the current connection and recursively connects to the referred server/share.

DFS path resolution in `cli_resolve_path()` first normalizes repeated leading separators and short-circuits if the current tcon is not a DFS-capable share. For DFS shares it builds a full DFS path from `\\server\share\path`, probes with `cli_qpathinfo_basic()`, and treats success or `OBJECT_NAME_NOT_FOUND` as an ordinary path. `PATH_NOT_COVERED` triggers referral lookup through an IPC$ connection to the DFS root. The resolver splits every returned referral, prefers already-cached target connections, then tries referral targets in order. It recomposes the target path from the unconsumed portion plus any referral extrapath, parses a new mount prefix, and recursively resolves nested DFS targets. On success, if the returned target is itself a DFS share, it returns a full DFS path for that root.

Referral parsing reads the server-returned consumed UCS-2 path length, converts it back to the UNIX charset to compute consumed bytes in the caller's path, then iterates referral records. Only version 3 referrals are materialized; unsupported versions are skipped by `ref_size`.

## State and Persistence Behavior

All persistent state is in memory. `cli_state` objects are talloc-owned and linked by Samba's DLIST macros so a root connection can own child DFS referral connections. `cli_cm_find()` searches both directions from an arbitrary list member. Temporary tree connect state is carefully saved and restored by `cli_state_save_tcon_share()` and `cli_state_restore_tcon_share()` while probing IPC$ for proxy referrals. No files or registry state are written by this module.

Encryption state is negotiated on the connection/session/tcon. SMB2 uses session encryption; SMB1 requires UNIX extensions with `CIFS_UNIX_TRANSPORT_ENCRYPTION_CAP` and may temporarily connect IPC$ to query capabilities. Path conversion state depends on `cli->requested_posix_capabilities`, the current remote name, and `cli->share`.

## Dependencies and Integration Points

This file integrates with Samba client connection/session code (`cli_connect_nb`, `smbXcli_negprot`, `cli_session_setup_creds`, `cli_tree_connect_creds`), credentials (`struct cli_credentials`), DFS RPC/trans2 definitions (`msdfs.h`, `trans2.h`), SMB2 ioctl support, UNIX extension helpers, and path query helpers from the libsmb file/query layers. It is consumed by higher-level client APIs that need a `cli_state` for a path and by SMB1 file operations that must wrap names in DFS syntax.

## Risks and Edge Cases

- `cli_resolve_path()` explicitly does not check for DFS referral loops, so pathological referral graphs can recurse until another failure or resource limit.
- Referral parsing is network-input sensitive. It has bounds checks for record headers, node offsets, and result lengths, but malformed referral sizes remain a high-value fuzz target.
- Path handling mixes DFS backslashes, POSIX slash support, wildcard trimming, and consumed-byte calculations after charset conversion. Multibyte path names and wildcard paths need coverage.
- `cli_check_msdfs_proxy()` temporarily swaps tcons. Any future early return must preserve restore/tdis ordering to avoid leaking or losing tree state.
- Encryption behavior differs sharply between SMB1 and SMB2 and between desired and required settings; fallback semantics are security-sensitive.

## Test Signals

Useful tests include DFS root ordinary-path success, `PATH_NOT_COVERED` referral resolution, nested referral chains, cached referral target reuse, unavailable first referral with later fallback, MSDFS proxy share detection, self-referral rejection, SMB1 DFS path wrapping for file calls, POSIX separator support, wildcard path cleanup, previous DFS full-path input, required encryption failure paths, and malformed referral buffer bounds tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clidfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clidgram.c -->
# sources/user-network-fs/samba/source3/libsmb/clidgram.c

## Purpose

`clidgram.c` implements NetBIOS datagram client support for a specific high-level operation: sending a mailslot-based NetLogon `GETDC` request and parsing the datagram response to discover a domain controller. It bridges Samba client code, nmbd datagram sending, local packet-reader sockets, and NDR-encoded NetLogon payloads.

## Important APIs, Types, and Functions

- `nbt_getdc_send()` starts the asynchronous GetDC request. It validates IPv4, builds a unique return mailslot, locates `nmbd`, prepares the datagram packet, opens a packet reader, and later sends the packet to nmbd.
- `nbt_getdc_recv()` returns the discovered `nt_version`, DC name, and optional `netlogon_samlogon_response`.
- `nbt_getdc()` is the synchronous wrapper with a private tevent context and timeout.
- `cli_prep_mailslot()` builds the NetBIOS datagram plus embedded SMB transaction mailslot payload.
- `prep_getdc_request()` NDR-encodes an `nbt_netlogon_packet` with `LOGON_SAM_LOGON_REQUEST`.
- `parse_getdc_response()` validates the datagram SMB wrapper, NDR-pulls the SMB transaction, parses the NetLogon SAM logon response, maps it to canonical form, validates the returned domain, and extracts the DC name.
- `struct nbt_getdc_state` keeps the async request context, messaging context, nmbd pid, return mailslot, target address/domain/SID/version, outbound packet, and parsed outputs.

## Control Flow

`nbt_getdc_send()` rejects non-IPv4 targets with `NT_STATUS_NOT_SUPPORTED`; the packet format stores an IPv4 address in `packet_struct.ip`. It builds `\\MAILSLOT\\NET\\GETDC...`-style state using `mailslot_name()`, reads nmbd's pidfile, randomizes a datagram id, and calls `prep_getdc_request()`. That helper fills a NetLogon SAM logon request using local NetBIOS name, account information, optional domain SID, requested NT version, and token fields, then passes the encoded blob to `cli_prep_mailslot()`.

`cli_prep_mailslot()` constructs a direct group or unique NetBIOS datagram with source and destination NBT names, lays out an SMB transaction mailslot body, enforces `MAX_DGRAM_SIZE`, copies the caller payload, sets `datasize`, stores destination IPv4 and timestamp, and emits debug diagnostics. After preparation, `nbt_getdc_send()` starts `nb_packet_reader_send()` against nmbd's local datagram socket directory and the private return mailslot.

When the reader is ready, `nbt_getdc_got_reader()` sends the packet to nmbd via `messaging_send_buf(MSG_SEND_PACKET)` and starts `nb_packet_read_send()`. `nbt_getdc_got_response()` receives one packet and calls `parse_getdc_response()`. A valid response completes the tevent request; parse failure maps to `NT_STATUS_INVALID_NETWORK_RESPONSE`.

## State and Persistence Behavior

The module does not persist data itself. It depends on nmbd's pidfile and local socket directory as runtime state. Request state is talloc-scoped to the tevent request; response objects are moved to the caller in `nbt_getdc_recv()`. `nbt_getdc()` uses a stackframe and frees it after polling. Datagram ids are random and masked to 15 bits.

## Dependencies and Integration Points

The file depends on `tevent`, Samba messaging, nmbd packet reader helpers, NetBIOS name/mailslot helpers, NDR-generated NetLogon and datagram parsers, `pull_netlogon_samlogon_response()`, Samba loadparm values such as `lp_netbios_name()`, `lp_pid_directory()`, and `global_nmbd_socket_dir()`, plus pidfile support. The public prototypes are declared in `clidgram.h`.

## Risks and Edge Cases

- IPv6 is unsupported even though the API accepts `sockaddr_storage`.
- The implementation requires a running local `nmbd`; absence of nmbd returns not-supported rather than trying direct UDP.
- `parse_getdc_response()` expects an SMB transaction datagram and validates returned domain equality; cross-domain or alias behavior may fail intentionally.
- Mailslot construction manipulates the SMB buffer by backing up four bytes for the TCP length convention. That area is protected by existing Samba packet layout assumptions and should be regression-tested if packet structures change.
- A single response is read. Retry, multi-response selection, and packet id correlation are delegated to surrounding behavior or not implemented here.

## Test Signals

Tests should cover no-nmbd behavior, IPv6 rejection, datagram size overflow, malformed datagram length/type/command, bad NDR payload, returned-domain mismatch, DC name with one or two leading backslashes, optional samlogon response ownership, timeout behavior in `nbt_getdc()`, and successful end-to-end interaction with a local nmbd packet socket.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clidgram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clidgram.h -->
# sources/user-network-fs/samba/source3/libsmb/clidgram.h

## Purpose

`clidgram.h` is the public header for the NetBIOS datagram GetDC client API implemented by `clidgram.c`. It exposes asynchronous and synchronous entry points for discovering a domain controller through NBT mailslot NetLogon traffic.

## Important APIs and Types

- `nbt_getdc_send()` creates a `tevent_req` for a GetDC request. Callers supply a memory context, tevent context, Samba messaging context, DC socket address, domain name, optional domain SID, account name/flags, and requested NT version.
- `nbt_getdc_recv()` completes the async request and can return the negotiated/returned NT version, DC name, and optional `struct netlogon_samlogon_response`.
- `nbt_getdc()` is the blocking wrapper with an explicit timeout in seconds.
- The header includes `../libcli/netlogon/netlogon.h` so callers see `struct netlogon_samlogon_response`.

## Control Flow and Integration

The header follows Samba's normal async pattern: `*_send()` starts work, a caller polls or chains callbacks on the `tevent_req`, and `*_recv()` transfers outputs. The synchronous helper wraps that flow for callers that are not already in an event loop. Consumers must link with the source3 libsmb datagram implementation and provide a valid `messaging_context`.

## State and Persistence Behavior

The header defines no storage. Ownership semantics are implied by the prototypes: returned strings and response structures are placed under the caller-provided `mem_ctx` in `nbt_getdc_recv()` or `nbt_getdc()`.

## Dependencies and Risks

The API surface hides that the implementation is IPv4-only and nmbd-dependent. Callers passing IPv6 addresses, missing messaging context, or expecting direct network I/O will receive implementation-level failures from `clidgram.c`. Because the optional output pointers can be `NULL`, callers should initialize their own variables and check `NTSTATUS` before using outputs.

## Test Signals

Compile-level tests should ensure the header is self-contained for users needing `struct netlogon_samlogon_response`. API tests should exercise async success, async failure, NULL optional outputs, and the synchronous timeout wrapper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clidgram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clientgen.c -->
# sources/user-network-fs/samba/source3/libsmb/clientgen.c

## Purpose

`clientgen.c` owns generic `cli_state` lifecycle and small connection helpers that are shared by the rest of source3 libsmb. It creates client state with negotiated capability preferences, tears it down safely, manipulates SMB1/SMB2 session and tree identifiers, tracks timeout/backup/case-sensitivity knobs, and implements SMB echo.

## Important APIs, Types, and Functions

- `cli_state_create()` allocates and initializes `struct cli_state`, chooses a client GUID, checks for setuid-root misuse, initializes server identity strings, maps command-line/environment flags into capabilities, creates `smbXcli_conn`, and creates an SMB1 session object.
- `cli_shutdown()` tears down one `cli_state` or an entire DFS-linked list headed by the given state.
- `_cli_shutdown()` closes RPC pipes, tree-disconnects when a tcon is active, disconnects the underlying `smbXcli_conn`, and frees the client state.
- `cli_set_timeout()`, `cli_set_backup_intent()`, `cli_set_case_sensitive()`, `cli_state_server_time()`, and `cli_state_available_size()` expose common connection settings/derived values.
- `cli_state_get_tid()`, `cli_state_set_tid()`, `cli_state_has_tcon()`, `cli_state_get_uid()`, `cli_state_set_uid()`, `cli_setpid()`, `cli_getpid()`, and `cli_state_get_vc_num()` abstract SMB1/SMB2 identifier access.
- `cli_state_save_tcon_share()` and `cli_state_restore_tcon_share()` temporarily detach and restore a tcon/share pair without freeing pipe-parented state.
- `cli_echo_send()`, `cli_echo_recv()`, and `cli_echo()` implement SMB echo for SMB1 and SMB2.

## Control Flow

Creation begins by selecting a client GUID from global override, loadparm value, or `GUID_random()`. It rejects setuid-root execution, allocates `cli_state`, seeds server-domain/OS/type strings, sets default timeout and DOS-error mapping, then interprets environment variables and connection flags for forced DOS errors, ASCII, SPNEGO suppression, oplocks, and level-II oplocks. Signing defaults are resolved through loadparm, with IPC default biased toward required signing. SMB1 capability bits are built from large files, NT SMBs, DFS, large read/write, LWIO, status32, unicode, extended security, and oplocks. SMB2/3 capabilities come from `SMB2_CAP_ALL` and parsed SMB 3.1.1 signing/encryption/QUIC policy. Finally `smbXcli_conn_create()` and `smbXcli_session_create()` attach transport and session objects.

Shutdown closes all open pipes by freeing list nodes, sends `cli_tdis()` if a tree connection exists, disconnects the transport, and frees the state. When the target is the head of a DFS connection list, `cli_shutdown()` iterates and frees subsidiary DFS connections before freeing the head.

Echo dispatches by negotiated protocol. SMB2 ignores the SMB1 echo count/data and calls `smb2cli_echo_send()`, while SMB1 uses `smb1cli_echo_send()`. The synchronous wrapper refuses to run while async calls are in flight on the connection.

## State and Persistence Behavior

This module is entirely in-memory. It initializes and mutates `cli_state` fields such as `timeout`, `backup_intent`, `use_oplocks`, `map_dos_errors`, `smb1.pid`, `smb1.vc_num`, `smb1.session`, `smb1.tcon`, `smb2.tcon`, `share`, and the linked `pipe_list`. It also reads process environment (`CLI_FORCE_DOSERR`, `CLI_FORCE_ASCII`) and Samba configuration. The tcon save/restore helpers deliberately detach raw tcon pointers rather than deep-copying to preserve open pipe parentage.

## Dependencies and Integration Points

The file depends on Samba loadparm, signing/sealing policy, SMBX transport/session/tcon helpers, SMB2 negotiate contexts, NDR GUID support, async SMB helpers, talloc, and tevent. Other libsmb modules rely on these helpers to avoid protocol-specific direct access to tcon ids, encryption state, server time, and connection shutdown.

## Risks and Edge Cases

- Sync helpers must keep rejecting use while async operations are outstanding; violating that can corrupt request sequencing.
- `cli_state_restore_tcon()` frees any replacement tcon before restoring the saved one. Callers must pair save/restore precisely.
- Capability flags in `cli_state_create()` drive negotiation behavior across many clients; environment-controlled force flags are useful tests but risky if assumed unavailable.
- `cli_shutdown()` uses list-head detection; callers holding non-head DFS children need to understand that shutting down the head tears down the whole list.
- IPC signing defaults and encryption algorithms are security-sensitive and tied to current loadparm behavior.

## Test Signals

Tests should verify flag-to-capability mapping, setuid-root rejection, GUID override behavior, signing defaults for IPC/default modes, forced ASCII/DOS env behavior, SMB1 versus SMB2 tcon id getters/setters, tcon save/restore preserving share strings, DFS-list shutdown, encryption-on checks for SMB1/SMB2, echo sync rejection during async calls, and successful SMB1/SMB2 echo paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clientgen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clierror.c -->
# sources/user-network-fs/samba/source3/libsmb/clierror.c

## Purpose

`clierror.c` provides two small client utility functions: mapping SMB/NT status values to local `errno` values and checking whether a `cli_state` is initialized and connected.

## Important APIs and Functions

- `cli_status_to_errno(NTSTATUS status)` converts DOS-class statuses to NTSTATUS first, special-cases `NT_STATUS_STOPPED_ON_SYMLINK` to `EACCES`, then calls `map_errno_from_nt_status()`.
- `cli_state_is_connected(struct cli_state *cli)` returns false for `NULL` or uninitialized clients and otherwise delegates to `smbXcli_conn_is_connected(cli->conn)`.

## Control Flow

`cli_status_to_errno()` starts by detecting DOS-encoded NTSTATUS values with `NT_STATUS_IS_DOS()`, extracting DOS class/code, and translating through `dos_to_ntstatus()`. It preserves legacy Samba behavior for stopped-on-symlink because the status value shape would not map correctly through the generic mapper. It logs the numeric NTSTATUS and resulting errno at notice level before returning.

`cli_state_is_connected()` is a defensive guard: it checks pointer validity, `cli->initialised`, and then the underlying connection state.

## State and Persistence Behavior

No persistent state is modified. The only side effect is logging from `cli_status_to_errno()`.

## Dependencies and Integration Points

This file depends on `source3/include/client.h`, source3 libsmb prototypes, NTSTATUS/DOS status helpers, `map_errno_from_nt_status()`, and `smbXcli_conn_is_connected()`. It is used by callers that need POSIX-style errors or cheap connection liveness checks without knowing `cli_state` internals.

## Risks and Edge Cases

- Error mapping is lossy by nature; callers must retain NTSTATUS where exact protocol diagnostics matter.
- The stopped-on-symlink special case preserves legacy behavior and should not be removed without checking symlink traversal callers.
- `cli_state_is_connected()` assumes initialized clients have a valid `conn` pointer; malformed partially constructed states are not fully protected.

## Test Signals

Tests should include DOS-class status conversion, symlink-stop mapping to `EACCES`, representative NTSTATUS-to-errno mappings, null and uninitialized `cli_state` checks, connected/disconnected underlying `smbXcli_conn` states, and log output stability where diagnostics are asserted.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clierror.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clifile.c -->
# sources/user-network-fs/samba/source3/libsmb/clifile.c

## Purpose

`clifile.c` is the main source3 libsmb client file-operation layer. It exposes asynchronous `*_send`/`*_recv` APIs and synchronous wrappers for path info, file info, POSIX extensions, create/open/close, rename/hardlink/delete, directory operations, locks, attributes, disk size, extended attributes, change notify, query info, flush, shadow copy enumeration, and generic fsctl/ioctl operations. It hides most SMB1 versus SMB2 dispatch differences behind `struct cli_state`.

## Important APIs, Types, and Functional Areas

- Set/query info primitives: `cli_setpathinfo_send/recv`, `cli_setfileinfo_send/recv`, `cli_qpathinfo_send/recv`, `cli_qfileinfo_send/recv`.
- POSIX/UNIX extension operations: symlink/readlink/hardlink, getacl/setacl, stat, chmod/fchmod/chown, POSIX mknod/open/mkdir/unlink/rmdir, and POSIX byte-range locks.
- Rename/link/delete: `cli_rename`, `cli_ntrename`, `cli_hardlink`, `cli_unlink`, `cli_mkdir`, `cli_rmdir`, `cli_nt_delete_on_close`.
- Open/create/close: `cli_ntcreate`, SMB1 `cli_ntcreate1`, `cli_nttrans_create`, `cli_openx`, `cli_open`, `cli_close`, and `cli_ftruncate`.
- Locking: `cli_lockingx`, `cli_locktype`, `cli_lock32`, `cli_unlock`, `cli_posix_lock`, and `cli_posix_unlock`.
- Metadata and space: `cli_getattrE`, `cli_getatr`, `cli_setattrE`, `cli_setatr`, `cli_chkpath`, `cli_dskattr`, and `cli_disk_size`.
- EAs and notifications: `cli_set_ea_path`, `cli_set_ea_fnum`, `cli_get_ea_list_path`, `cli_notify`.
- Server features: `cli_shadow_copy_data` and `cli_fsctl_send/recv`.

Every operation is backed by small state structs allocated under the request, for example `cli_ntcreate_state`, `cli_lockingx_state`, `cli_notify_state`, `cli_qfileinfo_state`, and many operation-specific buffers.

## Control Flow

The dominant pattern is `tevent_req_create()`, protocol/path preparation, lower-level SMB request submission, callback completion, and a `*_recv()` accessor that returns `NTSTATUS` plus moved output buffers. Synchronous wrappers allocate a stackframe, create a private tevent context, reject use when `smbXcli_conn_has_async_calls(cli->conn)` is true, poll the request, call the matching recv function, and free the stackframe.

Protocol dispatch is pervasive. SMB2 paths generally call `cli_smb2_*` helpers directly. SMB1 paths build command words and byte buffers manually (`cli_smb_send`, `cli_smb_req_create`, or `cli_trans_send`). Some operations have SMB1 fallback ladders: `cli_open()` maps POSIX-style open flags to NTCreate parameters, tries `cli_ntcreate()`, treats many unsupported statuses as a signal to fallback to `cli_openx()`, and closes broken directory handles that violate `FILE_NON_DIRECTORY_FILE`.

DFS and previous-version paths are handled at call sites. SMB1 path-based commands against DFS shares call `smb1_dfs_share_path()`. Rename and hardlink targets can call `cli_dfs_target_check()` to strip DFS prefixes where servers expect target-local names. `@GMT` previous-version paths set `FLAGS2_REPARSE_PATH` for non-UNIX info levels and relevant SMB1 commands.

Create/open flows parse server-returned create metadata into `struct smb_create_returns`. SMB2 hardlink opens the source file, sends `FSCC_FILE_LINK_INFORMATION`, then closes the file while preserving the set-info status. Notify sends long-running change-notify requests with timeout temporarily set to zero and supports cancellation by forwarding cancellation to the child request.

## State and Persistence Behavior

The module does not persist data outside the remote SMB server effects requested by the caller. Local state is request-scoped talloc memory: wire buffers, parsed output data, fnums, create-return structures, EA lists, notify changes, shadow-copy names, and fsctl output blobs. Synchronous wrappers use `talloc_stackframe()` for temporary lifetime management.

Remote state changes include creating/deleting/renaming files and directories, modifying ACLs/security descriptors, changing timestamps/attributes/EOF, setting delete-on-close, byte-range locks, flushing data, setting EAs, creating reparse points for special files, and subscribing to notify changes. Some helpers temporarily mutate client timeout (`cli_notify`, `cli_lockingx`) and restore it afterward; `cli_open()` may open then close a handle when detecting broken directory behavior.

## Dependencies and Integration Points

This file integrates with the rest of Samba's client stack: `async_smb`, trans2/nttrans helpers, DFS helpers from `clidfs.c`, SMB2 fnum helpers, security descriptor marshalling, POSIX mode/dev conversion helpers, EA structures, notify structures, reparse point marshalling, and the `smbXcli` protocol abstraction. It is a central dependency for higher-level tools such as smbclient/libsmbclient and for tests that exercise SMB file semantics.

## Risks and Edge Cases

- The file hand-builds many SMB1 wire buffers. Length fields, Unicode termination, and alignment are common risk points.
- Many sync wrappers duplicate the async-in-flight guard; missing that guard in new sync helpers can break request sequencing.
- SMB1/SMB2 behavior is intentionally not identical for every operation, especially POSIX extensions, chmod via NFS mode ACEs, reparse-point special files, and query-info level mappings.
- DFS path conversion must be correct per command. Some SMB1 commands require DFS names for source and destination; SMB2 rename/hardlink target paths may require stripped DFS prefixes.
- Network-response parsers validate minimum lengths for many paths, but EA blobs, notify buffers, shadow copy data, create responses, and referral-adjacent query buffers remain important fuzz targets.
- `cli_lockingx()` changes timeout for blocking locks and restores it only after normal completion; failures before restore are worth auditing.
- `cli_chmod_closed()` currently returns close errors before the saved chmod status, which can mask the chmod result if close fails.

## Test Signals

High-value tests include async and sync variants for each major operation, sync rejection with active async calls, SMB1 and SMB2 protocol dispatch, DFS share path behavior for every SMB1 path command, previous-version `@GMT` flagging, create/open fallback to OpenX, directory-handle correction in `cli_open()`, SMB2 hardlink close-after-error behavior, delete-on-close, set/get attr time-zone conversions, disk-size fallback from full-size-info to core dskattr, EA blob parsing with malformed lengths, POSIX stat 100-byte response validation, notify parsing and cancellation, shadow-copy count-only versus names mode, fsctl SMB1/SMB2 output ownership, and timeout restore around notify and locking.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libsmb/clifile.c -->

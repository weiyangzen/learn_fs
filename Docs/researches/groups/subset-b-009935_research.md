# Research: subset-b-009935

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/connect.c -->
# sources/user-network-fs/samba/source4/libcli/smb_composite/connect.c

Purpose: implements the SMB1 composite "full connect" operation: socket establishment or existing `smbXcli_conn` adoption, protocol negotiation, optional session setup, and optional tree connect. It exposes async `smb_composite_connect_send`/`recv` plus sync `smb_composite_connect`.

Important APIs and types: `enum connect_stage`, `struct connect_state`, `smb_composite_connect_send`, `smb_composite_connect_recv`, `connect_socket`, `connect_send_negprot`, `connect_send_session`, `connect_session_setup`, `connect_session_setup_anon`, and `connect_tcon`. It depends on raw SMB calls, `smbcli_sock_connect_send`, `smb_raw_negotiate_send`, `smb_composite_sesssetup_send`, `smb_raw_tcon_send`, credentials, NBT called/calling names, resolver context, loadparm, and smbX signing helpers.

Control flow: the state machine advances via three callback adapters: raw SMB request, composite subrequest, and tevent subrequest. New sockets move through socket connect to negprot; existing connections skip directly to session setup. Session setup creates a `smbcli_session` and provisional `smbcli_tree`; if credentials are absent the connection completes without authentication. If `service` is present, a TCONX path of `\\called_name\service` is sent.

State and persistence: all state is talloc-owned by the composite context until `recv`, where the output tree is stolen to the caller. It mutates session `vuid`, tree `tid`, `device`, and `fs_type`. Extended-signature tree responses protect the session key. Anonymous fallback resets `vuid` and `gensec` before retrying.

Risks: malformed inputs such as NULL event context or NULL gensec settings produce parameter errors, but called/service strings still drive network paths. Anonymous fallback can change security semantics and should be observable through `anonymous_fallback_done`. Signing/session-key transitions are security critical. Test signals include successful existing-connection reuse, kerberos-over-IP hostname substitution, failed auth with fallback, no-service connections, and extended signature TCON behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/connect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/connect_nego.c -->
# sources/user-network-fs/samba/source4/libcli/smb_composite/connect_nego.c

Purpose: provides a lower-level async helper that connects a TCP/NetBIOS socket and runs SMB dialect negotiation, returning an `smbXcli_conn` without creating a session or tree.

Important APIs and types: `struct smb_connect_nego_state`, `smb_connect_nego_send`, `smb_connect_nego_recv`, `smb_connect_nego_connect_done`, and `smb_connect_nego_nego_done`. It integrates `smbcli_sock_connect_send`, `smbXcli_conn_create`, and `smbXcli_negprot_send` with `tevent_req`.

Control flow: `send` copies options, computes NBT calling/called names, and starts socket connection, optionally to a supplied destination address. On connect completion it builds SMB1 capability flags from client options, creates an `smbXcli_conn` around the donated socket transport, frees the old `smbcli_socket`, and sends negotiate using min/max protocol and credit settings. The final recv moves the connection to the caller.

State and persistence: state is owned by the tevent request; the only persisted output is the moved `smbXcli_conn`. Timeout is derived from `request_timeout * 1000`. The helper has no authentication state and no filesystem side effects.

Risks: capability construction must remain aligned with SMB1 option semantics, especially Unicode, NTSTATUS, SPNEGO, signing, and oplock support. A NULL `called.name` posts a failed request. Test signals include SMB1 and SMB2 dialect negotiation paths, direct-address connections, capability bit selection, timeout behavior, and recv ownership transfer.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/connect_nego.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/fetchfile.c -->
# sources/user-network-fs/samba/source4/libcli/smb_composite/fetchfile.c

Purpose: composes a remote connection and whole-file load into one async operation for fetching a named file from an SMB share.

Important APIs and types: `enum fetchfile_stage`, `struct fetchfile_state`, `smb_composite_fetchfile_send`, `smb_composite_fetchfile_recv`, `fetchfile_connect`, and `fetchfile_read`. It reuses `smb_composite_connect_send` and `smb_composite_loadfile_send`.

Control flow: `send` builds a `smb_composite_connect` from the fetchfile input fields, disables anonymous fallback, copies SMB and session options, then starts a full connect. After connect completion, it creates a `smb_composite_loadfile` with `io->in.filename` and reads the file through the connected tree. On read completion it copies data pointer and size to the outer output.

State and persistence: network connection state and file data are talloc-owned under the composite until `recv`. `recv` steals `io->out.data` to the caller. It does not explicitly disconnect the tree; lifetime follows talloc ownership of the composite and loaded buffer.

Risks: the underlying loadfile cap and read behavior define memory exposure. Fetchfile assumes connect output tree is valid and does not retry authentication. Test signals include connect failure propagation, zero-length and non-empty file reads, data ownership after recv, and preserving input options such as resolver and gensec settings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/fetchfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/fsinfo.c -->
# sources/user-network-fs/samba/source4/libcli/smb_composite/fsinfo.c

Purpose: connects to a remote share and queries filesystem information using raw SMB fsinfo levels.

Important APIs and types: `enum fsinfo_stage`, `struct fsinfo_state`, `smb_composite_fsinfo_send`, `smb_composite_fsinfo_recv`, `fsinfo_connect`, `fsinfo_query`, and raw/composite callback adapters. It uses `smb_composite_connect_send`, `smb_raw_fsinfo_send`, and `smb_raw_fsinfo_recv`.

Control flow: `send` constructs a connect request from fsinfo input and inherited options from an existing `tree` argument, then enters `FSINFO_CONNECT`. On connection completion it allocates `union smb_fsinfo`, sets the requested level, sends the raw query on the newly connected tree, and advances to `FSINFO_QUERY`. Query completion stores the fsinfo union in `io->out`.

State and persistence: the returned `union smb_fsinfo` is allocated under state and stolen to the caller in recv. The file has no durable local storage; network-visible state is limited to opening an SMB session/tree and issuing the fsinfo transaction.

Risks: the `tree` parameter is used as a parent/options source while the operation opens a new tree, so callers need a live tree with valid transport/session options. Error handling maps raw query failures to composite error. Test signals include every supported fsinfo level, invalid credentials, missing event context, and ownership of `out.fsinfo` after recv.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/fsinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/loadfile.c -->
# sources/user-network-fs/samba/source4/libcli/smb_composite/loadfile.c

Purpose: implements an async whole-file read over SMB1 using open, repeated ReadX, and close.

Important APIs and types: `enum loadfile_stage`, `struct loadfile_state`, `smb_composite_loadfile_send`, `smb_composite_loadfile_recv`, `smb_composite_loadfile`, `loadfile_open`, `loadfile_read`, `loadfile_close`, and `setup_close`. It depends on raw open/read/close requests.

Control flow: `send` opens `io->in.fname` with `RAW_OPEN_NTCREATEX`, read-data access, shared read/write, normal attributes, and anonymous impersonation. On open completion it rejects files larger than 100 MB, allocates `io->out.data`, and either closes zero-length files or starts 32 KiB ReadX chunks. Each read advances the offset and output pointer until the expected size is reached, then closes the handle.

State and persistence: the only persistent result is an in-memory buffer and size stolen to the caller in recv. The remote handle should always be closed on normal paths; errors during open/read may leave closure to lower transport/server cleanup.

Risks: no retry logic and no short-read guard except completion by offset plus bytes read; a zero-byte read before expected size could loop if the server reports success with no data. The 100 MB cap is a hard resource policy. Test signals include zero-length files, boundary sizes around 32768 and 100 MB, short read behavior, open denial, and close failure propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/loadfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/savefile.c -->
# sources/user-network-fs/samba/source4/libcli/smb_composite/savefile.c

Purpose: implements an async whole-file write over SMB1 using open/create-if-needed, repeated WriteX, and close.

Important APIs and types: `enum savefile_stage`, `struct savefile_state`, `smb_composite_savefile_send`, `smb_composite_savefile_recv`, `smb_composite_savefile`, `savefile_open`, `savefile_write`, `savefile_close`, and `setup_close`. It uses raw open/write/close requests.

Control flow: `send` opens `io->in.fname` with write-data access, normal attributes, shared read/write, `NTCREATEX_DISP_OPEN_IF`, and anonymous impersonation. After open it closes immediately for size zero. Otherwise it writes chunks sized to `max_xmit - 100`, accumulating `total_written`. A short write or reaching the requested size triggers close; close completion verifies `total_written == io->in.size`.

State and persistence: state tracks the open handle through the raw request structs and stores only `total_written`; remote persistence is the target file contents. There is no explicit truncation before writing, so rewriting a shorter buffer over an existing longer file may leave trailing data unless server disposition semantics are changed elsewhere.

Risks: the lack of truncation is the main data-integrity concern. Partial writes are converted to close then `NT_STATUS_DISK_FULL` if incomplete. Test signals include creating new files, overwriting longer files, zero-byte saves, max_xmit chunking, disk-full simulation, and close error handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/savefile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/sesssetup.c -->
# sources/user-network-fs/samba/source4/libcli/smb_composite/sesssetup.c

Purpose: hides the SMB session setup variants behind one composite API, covering pre-NT1, NT1, and extended-security SPNEGO/GENSEC flows.

Important APIs and types: `struct sesssetup_state`, `smb_composite_sesssetup_send`, `smb_composite_sesssetup_recv`, `smb_composite_sesssetup`, `session_setup_old`, `session_setup_nt1`, `session_setup_spnego_restart`, `session_setup_spnego`, `request_handler`, and the two GENSEC update callbacks. Dependencies include raw sesssetup, credentials, NTLM response generation, GENSEC, SMB signing, and smbX session-key APIs.

Control flow: `send` rejects mandatory encryption above desired, rejects Kerberos-required on legacy/non-SPNEGO protocols, and selects the session setup flavor from negotiated protocol and extended-security capability. Old/NT1 paths build password blobs or NTLM challenge responses and send one SMB request. SPNEGO starts GENSEC, feeds the server negotiate blob, sends one or more SMB sesssetup requests as GENSEC returns more tokens, and handles logon failure retry for kerberos/password fallback.

State and persistence: session `vuid`, `os`, `lanman`, `gensec`, signing state, and session key are mutated. Some response requests are retained for caller-side signing checks until the GENSEC session key is known. The destructor frees outstanding SMB requests.

Risks: this is security-critical. Mutual authentication must continue while GENSEC reports `MORE_PROCESSING_REQUIRED` even if the server returns success. Session key activation, anonymous no-signing, password retry, and kerberos fallback are all sensitive. Test signals include legacy LANMAN rejection with required Kerberos, NTLMv2 without SPNEGO invalid parameter path, multi-leg SPNEGO, failed signing verification, wrong-password retry, anonymous setup, and encryption-required rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/sesssetup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/smb2.c -->
# sources/user-network-fs/samba/source4/libcli/smb_composite/smb2.c

Purpose: supplies SMB2 composite helpers that emulate common SMB1 path operations requiring multiple SMB2 requests: unlink, mkdir, rmdir, and setpathinfo.

Important APIs and types: `smb2_composite_unlink_send`, `smb2_composite_unlink`, `smb2_composite_mkdir_send`, `smb2_composite_mkdir`, `smb2_composite_rmdir_send`, `smb2_composite_rmdir`, `smb2_composite_setpathinfo_send`, `smb2_composite_setpathinfo_recv`, and `smb2_composite_setpathinfo`. Internal state tracks delete/truncate handles and setpathinfo create/set/close status.

Control flow: unlink rejects wildcard patterns, opens the path with delete-on-close and optional write-data access, optionally truncates non-empty files, then closes. mkdir creates a directory and closes the handle. rmdir opens a directory with delete-on-close and closes. setpathinfo opens a path, sets file info by handle, closes, and returns the setinfo status ahead of close status.

State and persistence: remote state changes are actual path deletion, directory creation/deletion, and metadata updates. Handles are carried in state until close. The sync setpathinfo wrapper uses a stack talloc frame and polls the tevent request.

Risks: unlink intentionally ignores truncate errors to avoid handle leaks, so callers may see close/delete status rather than truncation detail. Path normalization strips one leading backslash by incrementing the pointer. Test signals include wildcard rejection, delete-on-close semantics, truncate-if-needed behavior on non-empty files, close-after-setinfo on failure, and correct status priority between setinfo and close.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/smb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/smb_composite.h -->
# sources/user-network-fs/samba/source4/libcli/smb_composite/smb_composite.h

Purpose: declares the public data contracts and function prototypes for SMB composite helpers used by source4 clients.

Important APIs and types: `smb_composite_loadfile`, `smb_composite_fetchfile`, `smb_composite_savefile`, `smb_composite_connect`, `smb_composite_sesssetup`, `smb_composite_fsinfo`, `smb_composite_appendacl`, and SMB2 helper prototypes. It includes raw SMB and SMB2 headers and exposes both async send/recv and sync variants where available.

Control flow: the header itself has no executable flow, but its struct layout defines how callers supply credentials, resolver and gensec settings, SMB/session options, service names, filenames, and output ownership. `smb_composite_connect` explicitly models optional session setup with NULL credentials and optional tree connect with NULL service.

State and persistence: outputs are pointer-heavy talloc objects: loaded data, trees, filesystem info, ACL security descriptors, and session IDs. Callers must respect recv ownership rules implemented in the C files.

Risks: ABI/API coupling is high because composite implementations copy these structs directly. Missing fields in `smb_composite_fsinfo` compared with connect options can force option inheritance from another tree. Test signals are compile coverage of all declarations, struct initialization by downstream callers, and ABI expectations around optional fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/smb_composite.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/util/clilsa.c -->
# sources/user-network-fs/samba/source4/libcli/util/clilsa.c

Purpose: provides convenience LSA RPC helpers over SMB1 and SMB2 file sharing connections for SID/name lookup and account-right management.

Important APIs and types: `struct smblsa_state`, `smblsa_connect`, `smb2lsa_connect`, `smblsa_sid_privileges`, `smb2lsa_sid_privileges`, `smblsa_sid_check_privilege`, `smb2lsa_sid_check_privilege`, `smblsa_lookup_sid`, `smblsa_lookup_name`, `smblsa_sid_add_privileges`, and `smblsa_sid_del_privileges`. It depends on LSARPC NDR stubs, DCERPC over SMB pipes, security descriptors, SID helpers, and smbX signing protection.

Control flow: SMB1 setup connects to IPC$, opens and binds `lsarpc`, then opens an LSA policy handle. SMB2 setup opens the same named pipe over an existing SMB2 tree and calls OpenPolicy2. The public helpers lazy-connect, perform one RPC, validate both transport status and RPC result, and translate outputs such as rights arrays, `DOMAIN\name`, or SID strings.

State and persistence: connection state is cached on `cli->lsa` or `tree->lsa`, including binding handle and policy handle. Privilege add/delete calls persist account-right changes on the remote server.

Risks: cached handles can become stale if the underlying tree/session dies. Lookup validation assumes one domain and one result; malformed server replies return invalid network response. Add/delete require powerful remote access. Test signals include IPC$ connection failure, OpenPolicy result failure, SID parsing errors, lookup response shape validation, SMB2 parity, and add/remove rights round trips.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/util/clilsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/util/pyerrors.h -->
# sources/user-network-fs/samba/source4/libcli/util/pyerrors.h

Purpose: centralizes Python exception conversion macros for Samba C extension code using WERROR, HRESULT, NTSTATUS, and plain strings.

Important APIs and types: `PyErr_FromWERROR`, `PyErr_FromHRESULT`, `PyErr_FromNTSTATUS`, `PyErr_FromString`, `PyErr_SetWERROR`, `PyErr_SetHRESULT`, `PyErr_SetNTSTATUS`, `_and_string` variants, `PyErr_NTSTATUS_IS_ERR_RAISE`, `PyErr_NTSTATUS_NOT_OK_RAISE`, and `PyErr_WERROR_NOT_OK_RAISE`.

Control flow: each setter imports the `samba` Python module, fetches the named exception class, builds a tuple payload of numeric code and message, sets the Python error, and lets callers return NULL through convenience macros.

State and persistence: no local state is stored. The observable effect is Python interpreter exception state. The macros allocate Python objects but do not visibly decref imported module/class temporaries, relying on short-lived extension error paths.

Risks: repeated `PyImport_ImportModule` and `PyObject_GetAttrString` inside macros can leak references or mask import errors. Macros evaluate arguments in C macro context and should not receive expressions with side effects. Test signals include extension-level error conversion for all three status families, custom string overrides, and behavior when importing `samba` fails.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/util/pyerrors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/wbclient/wbclient.c -->
# sources/user-network-fs/samba/source4/libcli/wbclient/wbclient.c

Purpose: adapts Samba internal `id_map` arrays to libwbclient SID/Unix ID conversion APIs.

Important APIs and types: `wbc_sids_to_xids` and `wbc_xids_to_sids`, with `struct id_map`, `struct dom_sid`, `struct unixid`, `struct wbcDomainSid`, and `struct wbcUnixId`. It depends on winbind client environment toggles and libwbclient conversion calls.

Control flow: SID-to-ID allocates temporary arrays, copies internal SIDs into wbc SIDs, temporarily enables winbind if it was disabled by environment, calls `wbcSidsToUnixIds`, restores the previous state, and maps returned ID types back to Samba `ID_TYPE_*`. ID-to-SID validates UID/GID input types, calls `wbcUnixIdsToSids`, duplicates non-null returned SIDs into the caller-owned `ids` array, and marks unmapped null SIDs.

State and persistence: no persistent local state, but winbind process/environment state is toggled around calls. Outputs mutate each `id_map` entry's `xid`, `sid`, and `status`.

Risks: conversion errors collapse to `NT_STATUS_INTERNAL_ERROR`, losing detailed libwbclient diagnostics. In the GID branch, the code initializes `.id.uid` instead of `.id.gid`, which is a suspicious field-selection risk for GID conversions. Test signals include UID, GID, BOTH, NOT_SPECIFIED, unmapped null SID, winbind-off environment restoration, allocation failure, and libwbclient error propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/wbclient/wbclient.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/wbclient/wbclient.h -->
# sources/user-network-fs/samba/source4/libcli/wbclient/wbclient.h

Purpose: declares the legacy winbind client adapter functions for SID/Unix ID mapping.

Important APIs and types: includes `librpc/gen_ndr/idmap.h` and declares `wbc_sids_to_xids(struct id_map *ids, uint32_t count)` and `wbc_xids_to_sids(struct id_map *ids, uint32_t count)`.

Control flow: no executable flow. The header allows callers to pass mutable arrays of `id_map` records and receive updated mapping status and values.

State and persistence: no state in the header. The implementation mutates caller-provided maps and talks to winbind.

Risks: there are no include guards in this header, so repeated inclusion depends on the wider build avoiding duplicate prototype issues. Test signals include successful compilation under repeated includes and consumers using the NDR idmap types consistently.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/wbclient/wbclient.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/wbclient/wscript_build -->
# sources/user-network-fs/samba/source4/libcli/wbclient/wscript_build

Purpose: defines the waf build target for the old source4 winbind client adapter library.

Important APIs and types: `bld.SAMBA_LIBRARY('LIBWBCLIENT_OLD', ...)` builds `wbclient.c` as a private library with public deps `samba-errors events wbclient`, private deps `WB_REQTRANS NDR_WINBIND MESSAGING RPC_NDR_WINBIND`, and a cflag defining `WINBINDD_SOCKET_DIR`.

Control flow: during configure/build, waf interpolates `bld.env.WINBINDD_SOCKET_DIR` into a C preprocessor define and compiles the source into a private Samba library.

State and persistence: build metadata only; it changes which object/library products exist and which socket-dir constant the C code sees.

Risks: dependency drift or a missing environment value can break builds. The target is private, so downstream public consumers should not link it directly. Test signals include waf target generation, correct cflag quoting, and linkage of the wbclient conversion functions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/wbclient/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/wrepl/winsrepl.c -->
# sources/user-network-fs/samba/source4/libcli/wrepl/winsrepl.c

Purpose: implements the low-level WINS replication client transport and core replication requests.

Important APIs and types: `struct wrepl_socket`, `wrepl_socket_init`, `wrepl_socket_is_connected`, `wrepl_socket_donate_stream`, `wrepl_socket_split_stream`, `wrepl_best_ip`, `wrepl_connect_send`/`recv`/sync, `wrepl_request_send`/`recv`/sync, `wrepl_associate`, `wrepl_associate_stop`, `wrepl_pull_table`, and `wrepl_pull_names`. It depends on tevent queues, `tstream`, tsocket addresses, NDR WINSREPL push/pull, loadparm interface selection, and packet framing.

Control flow: operations are serialized on `request_queue`. Connect creates local and remote IPv4 socket addresses and opens a TCP stream to `WINS_REPLICATION_PORT`. Generic request marshals a `wrepl_packet` into a wrapped NDR blob, writes it to the stream, optionally disconnects or completes send-only, otherwise reads a length-prefixed PDU and unmarshals a reply. Higher-level calls build protocol packets for association start/stop, partner-table query, and owner-name pull, then validate reply message and command types.

State and persistence: `wrepl_socket` owns the event context, request timeout, queue, and active stream. Donate/split transfer stream ownership. Pull-name output converts wire names into stable `struct wrepl_name` arrays with owner/address strings. No local durable storage is written, but remote association state is created/stopped.

Risks: event context mismatch currently calls `smb_panic`, so misuse is process-fatal. Any request error frees the stream, affecting queued/future calls. The PDU parser trusts NDR length framing after a 4-byte initial read. Test signals include connect timeout, queue serialization, send-only disconnect, invalid message type handling, multi-address name conversion, stream donate/split with in-use queue, and connection teardown on read/write errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/wrepl/winsrepl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/wrepl/winsrepl.h -->
# sources/user-network-fs/samba/source4/libcli/wrepl/winsrepl.h

Purpose: defines public WINS replication client structures, flag helpers, and includes generated prototypes.

Important APIs and types: forward declarations for `wrepl_request` and `wrepl_socket`, `wrepl_send_ctrl`, `wrepl_associate`, `wrepl_associate_stop`, `wrepl_pull_table`, `wrepl_address`, `wrepl_name`, and `wrepl_pull_names`. Macros decode and construct WINS replication record flags: `WREPL_NAME_TYPE`, `WREPL_NAME_STATE`, `WREPL_NAME_NODE`, `WREPL_NAME_IS_STATIC`, and `WREPL_NAME_FLAGS`.

Control flow: no executable flow. The header shapes inputs and outputs for association setup, stop, table pull, and full name pull. It imports NBT and WINSREPL generated NDR definitions, then includes `winsrepl_proto.h`.

State and persistence: output structs carry association context, partner arrays, and pulled replicated names with version IDs and address lists. Ownership is handled by the implementation's talloc moves.

Risks: flag macros assume bit layout from generated WINSREPL constants; changes in protocol definitions require keeping these masks aligned. Test signals include compile coverage of generated prototypes, flag round-trip tests, and multi-address name representation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/wrepl/winsrepl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/wscript_build -->
# sources/user-network-fs/samba/source4/libcli/wscript_build

Purpose: top-level waf build description for source4 libcli subsystems and libraries relevant to SMB, LSA, WINS replication, resolve, and raw SMB clients.

Important APIs and types: recursive builds for `ldap`, `wbclient`, `smb2`, and `rap`; subsystem targets `LIBSAMBA_TSOCKET`, `LIBCLI_LSA`, `cli_composite`, `LIBCLI_SMB_COMPOSITE`, `LIBCLI_DGRAM`, `LIBCLI_WREPL`, `LIBCLI_RESOLVE`, `LP_RESOLVE`, `LIBCLI_FINDDCS`, `LIBCLI_SMB`; and library target `smbclient-raw`.

Control flow: waf evaluates target declarations, source lists, generated autoprotos, private headers, public deps, and private deps. `LIBCLI_SMB_COMPOSITE` collects loadfile, savefile, connect_nego, connect, sesssetup, fetchfile, appendacl, fsinfo, and smb2 composite sources.

State and persistence: build graph only. It determines generated prototype headers and link relationships. Several runtime modules depend on targets defined here, such as raw SMB depending on composite helpers and WINS replication depending on tstream support.

Risks: cyclic or duplicated deps can cause build instability; `LIBCLI_DGRAM` lists `LIBCLI_RESOLVE` twice. Private header declarations affect install/API visibility. Test signals include full waf configure/build, generated `clilsa.h` and `winsrepl_proto.h`, and link tests for consumers of `LIBCLI_SMB` and `LIBCLI_WREPL`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/composite.h -->
# sources/user-network-fs/samba/source4/libnet/composite.h

Purpose: defines monitor message IDs and the `monitor_msg` structure used by libnet composite operations to report progress.

Important APIs and types: `mon_SamrCreateUser`, `mon_SamrOpenUser`, `mon_SamrQueryUser`, `mon_SamrCloseUser`, `mon_SamrLookupName`, `mon_SamrDeleteUser`, `mon_SamrSetUser`, `mon_SamrConnect`, `mon_SamrOpenDomain`, `mon_LsaOpenPolicy`, `mon_SamrOpenGroup`, `mon_SamrQueryGroup`, network message IDs, masks, and `struct monitor_msg { uint32_t type; void *data; size_t data_size; }`.

Control flow: no executable flow. Composite libnet calls allocate operation-specific message payloads and invoke a caller-supplied monitor callback with these IDs.

State and persistence: monitor messages are transient and generally talloc-owned by the operation state. They do not persist progress beyond the callback.

Risks: IDs are unscoped macros, so collisions or stale payload expectations are possible. `void *data` requires callers to branch correctly on `type`. Test signals include monitor callback coverage for group/user operations and payload size/type consistency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/composite.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/groupinfo.c -->
# sources/user-network-fs/samba/source4/libnet/groupinfo.c

Purpose: implements an async composite SAMR flow for querying group information by group SID or group name.

Important APIs and types: `struct groupinfo_state`, `libnet_rpc_groupinfo_send`, `libnet_rpc_groupinfo_recv`, `libnet_rpc_groupinfo`, and continuation callbacks for lookup, open group, query group info, and close group. It depends on `dcerpc_samr_*_r_send/recv`, SAMR NDR types, policy handles, and libnet monitor messages.

Control flow: `send` validates binding and io. If `io->in.sid` is supplied, it parses the SID and uses the final subauthority as the group RID, then opens the group. Otherwise it calls `samr_LookupNames` for one group name, validates RID/type counts, then opens the group. After open it queries `samr_QueryGroupInfo` at the requested level, steals the returned info union, closes the group handle, and completes. Each major stage can emit a monitor message.

State and persistence: remote state is read-only except opening/closing handles. Output `union samr_GroupInfo` is stolen into caller memory in recv and copied into `io->out.info`.

Risks: SID parsing only uses the last subauthority as RID and does not verify domain SID alignment with `domain_handle`. Monitor payload allocations are not checked uniformly after every field. Test signals include SID and name paths, missing group, invalid lookup response counts, query levels, close failure, and monitor callback contents.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/groupinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/groupinfo.h -->
# sources/user-network-fs/samba/source4/libnet/groupinfo.h

Purpose: declares the input/output contract and monitor payload structures for libnet SAMR group information queries.

Important APIs and types: `struct libnet_rpc_groupinfo` with input `domain_handle`, `groupname`, `sid`, and `level`, and output `union samr_GroupInfo info`; monitor payloads `msg_rpc_open_group`, `msg_rpc_query_group`, and `msg_rpc_close_group`.

Control flow: no executable flow. The struct supports two selection modes, SID or group name, with the implementation choosing SID if present.

State and persistence: no state in the header. Output mirrors the SAMR query level selected by the caller.

Risks: no explicit discriminator identifies which field of `union samr_GroupInfo` is valid, so callers must track the requested level. SID and groupname are both nullable by type, but implementation requires at least one meaningful identifier. Test signals include compile coverage for all query levels and monitor payload consumers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/groupinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/groupman.c -->
# sources/user-network-fs/samba/source4/libnet/groupman.c

Purpose: implements a composite SAMR group creation helper.

Important APIs and types: `struct groupadd_state`, `libnet_rpc_groupadd_send`, `libnet_rpc_groupadd_recv`, `libnet_rpc_groupadd`, and `continue_groupadd_created`. It uses `samr_CreateDomainGroup` over a supplied DCERPC binding handle and domain policy handle.

Control flow: `send` validates the binding and io, creates a composite context, copies the domain handle, allocates an LSA string for the requested group name, sets access mask to zero, points outputs at state-owned `group_handle` and `group_rid`, then sends `dcerpc_samr_CreateDomainGroup_r_send`. The continuation receives transport status, checks `creategroup.out.result`, and completes. `recv` copies the returned group handle into `io->out`.

State and persistence: successful execution persists a new domain group on the remote SAM database and returns an open group policy handle. The returned RID is tracked internally but not exposed by the header.

Risks: access mask zero may depend on server defaults and may not grant useful handle permissions. The monitor function is stored but not used, so callers expecting progress events receive none. Test signals include duplicate group errors, permission failures, returned handle usability, and memory failure during LSA string construction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/groupman.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/groupman.h -->
# sources/user-network-fs/samba/source4/libnet/groupman.h

Purpose: declares the libnet SAMR group-add request structure.

Important APIs and types: `struct libnet_rpc_groupadd`, with input `domain_handle` and `groupname`, and output `group_handle`.

Control flow: no executable flow. The implementation uses the domain handle and group name to create a SAMR domain group.

State and persistence: the output handle represents server-side state opened by group creation. The caller is responsible for later closure through SAMR mechanisms.

Risks: the header does not expose the created RID even though implementation records it, limiting caller verification without extra lookups. Test signals include consumers closing the returned handle and compile coverage for group management functions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/groupman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet.c -->
# sources/user-network-fs/samba/source4/libnet/libnet.c

Purpose: initializes a source4 `libnet_context` with event, loadparm, resolver, and default SAMR state.

Important APIs and types: `libnet_context_init`, `struct libnet_context`, `tevent_context`, `loadparm_context`, `dcerpc_init`, and `lpcfg_resolve_context`.

Control flow: the function requires a non-NULL event context, allocates a zeroed context under the caller memory context, stores event and loadparm pointers, initializes DCERPC globally, derives the resolve context from loadparm, sets `samr.buf_size` to 128, and returns the context.

State and persistence: the returned context persists caller credentials, SAMR/LSA connection fields, resolver context, server address override, and event/loadparm pointers. This function only seeds default fields; connections and handles are opened later by other libnet calls.

Risks: NULL loadparm is not rejected before `lpcfg_resolve_context(lp_ctx)`, so callers must supply a valid loadparm context. `dcerpc_init` is global initialization. Test signals include NULL event rejection, valid context defaults, resolver construction, and subsequent SAMR calls using default buffer size.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet.h -->
# sources/user-network-fs/samba/source4/libnet/libnet.h

Purpose: defines the central source4 libnet context and aggregates libnet operation headers.

Important APIs and types: `struct libnet_context`, including credentials, SAMR connection state, LSA connection state, `resolve_context`, `tevent_context`, `loadparm_context`, and optional `server_address`. It includes operation headers for composite monitoring, user/group management, password, time, RPC, join, site, DC promotion/demotion, samsync, vampire, share, lookup, domain, and generated prototypes.

Control flow: no executable flow. The context layout defines how libnet operations share credentials, already-open pipes, binding handles, domain metadata, policy handles, and runtime contexts.

State and persistence: this is the shared mutable state for libnet clients. SAMR and LSA substructures cache pipes, binding handles, names, SIDs, access masks, and policy handles across operations.

Risks: operations sharing one context must coordinate cached handles and server address overrides. Header aggregation can create broad compile dependencies and hidden coupling. Test signals include initialization defaults, multiple operations sharing SAMR/LSA handles, and consumers compiling with all included headers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/libnet.h -->

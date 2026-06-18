# subset-b-009869 research

Source group:
- sources/user-network-fs/samba/source3/smbd/smb1_lanman.c
- sources/user-network-fs/samba/source3/smbd/smb1_lanman.h
- sources/user-network-fs/samba/source3/smbd/smb1_message.c
- sources/user-network-fs/samba/source3/smbd/smb1_message.h
- sources/user-network-fs/samba/source3/smbd/smb1_negprot.c
- sources/user-network-fs/samba/source3/smbd/smb1_negprot.h
- sources/user-network-fs/samba/source3/smbd/smb1_nttrans.c
- sources/user-network-fs/samba/source3/smbd/smb1_nttrans.h
- sources/user-network-fs/samba/source3/smbd/smb1_oplock.c
- sources/user-network-fs/samba/source3/smbd/smb1_oplock.h

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_lanman.c -->
# sources/user-network-fs/samba/source3/smbd/smb1_lanman.c

## Purpose
`smb1_lanman.c` implements the SMB1 Remote Administration Protocol (RAP/LANMAN) request handlers reached through SMB transaction IPC calls. It translates old LANMAN APIs for share, server, workstation, user, group, session, print queue, print job, password-change, and time-of-day operations into Samba internal services and modern RPC backends (`spoolss`, `srvsvc`, `samr`). The public entry point is `api_reply()`, which dispatches an API id from transaction parameters, enforces selected anonymous-access rules, invokes a handler from `api_commands[]`, and returns transaction parameter/data buffers with RAP-style error codes and converter words.

## Important APIs, types, and functions
The module-local `struct pack_desc` and helpers `getlen()`, `init_package()`, `package()`, `PACKI()`, and `PACKS()` are the core RAP structure packer. They interpret legacy RAP format strings such as `B13BWz`, split fixed fields from string/data regions, track `neededlen`, `usedlen`, `errcode`, and support substructures. `smb_realloc_limit()` allocates or grows reply buffers and zeroes the expanded memory; despite its comment, it does not enforce a hard upper size beyond making allocations at least 4 KiB.

The safe decoding helpers `get_safe_SVAL()`, `get_safe_IVAL()`, `get_safe_ptr()`, `get_safe_str_ptr()` through included headers, `skip_string()`, and `prefix_ok()` are the main protections around variable RAP parameter buffers. `CopyExpanded()`, `CopyAndAdvance()`, and `StrlenExpanded()` write ASCII strings while applying Samba substitution variables for service comments and paths.

Print and spooler handlers include `api_DosPrintQGetInfo()`, `api_DosPrintQEnum()`, `api_RDosPrintJobDel()`, `api_WPrintQueueCtrl()`, `api_PrintJobInfo()`, `api_WPrintJobGetInfo()`, `api_WPrintJobEnumerate()`, `api_WPrintDestGetInfo()`, `api_WPrintDestEnum()`, `api_WPrintDriverEnum()`, `api_WPrintQProcEnum()`, and `api_WPrintPortEnum()`. They validate RAP format strings, open `spoolss` RPC pipes, issue `OpenPrinter`, `EnumPrinters`, `EnumJobs`, `GetPrinter`, `GetPrinterDriver`, `GetJob`, `SetJob`, and `SetPrinter`, then pack old RAP queue/job/destination layouts via `fill_spoolss_printjob_info()`, `fill_printq_info()`, and `fill_printdest_info()`.

Share/server/session/workstation handlers include `api_RNetShareGetInfo()`, `api_RNetShareEnum()`, `api_RNetShareAdd()`, `api_RNetServerEnum2()`, `api_RNetServerEnum3()`, `api_RNetServerGetInfo()`, `api_RNetSessionEnum()`, `api_NetWkstaGetInfo()`, and `api_NetRemoteTOD()`. They combine local loadparm state, usershare/printer reloads, browse-list cache files, and `srvsvc` RPC calls.

User/group/password handlers include `api_RNetGroupEnum()`, `api_RNetGroupGetUsers()`, `api_NetUserGetGroups()`, `api_RNetUserEnum()`, `api_RNetUserGetInfo()`, `api_WWkstaUserLogon()`, `api_WAccessGetUserPerms()`, and `api_SamOEMChangePassword()`. Most are SAMR-backed and return LANMAN-sized fixed names such as 21-byte user or group names.

`api_commands[]` maps RAP ids to handler functions and an `auth_user` flag. `api_TooSmall()` emits `NERR_BufTooSmall` if handler output exceeds caller maxima. `api_Unsupported()` emits `NERR_notsupported` for unknown or rejected variants.

## Control flow
`api_reply()` starts by validating the transaction parameter buffer and extracting the 16-bit RAP command id plus the two format strings immediately following it. It linearly searches `api_commands[]`; if no id matches, it lands on the sentinel `api_Unsupported` handler. For entries marked `auth_user`, `lp_restrict_anonymous()` triggers a session lookup by `vuid` and denies requests below `SECURITY_USER`.

After allocating initial 1 KiB `rdata` and `rparam` buffers, `api_reply()` invokes the selected handler with original request parameter/data buffers, requested max data/parameter return sizes, and mutable reply pointers/lengths. Handlers return `true` when they intentionally produced a RAP response, `false` when the request shape is unsupported. `api_reply()` converts over-large responses into `api_TooSmall()`, converts `false` into `api_Unsupported()`, sends the result through `send_trans_reply()`, and frees temporary buffers.

Most handlers follow the same pattern: parse RAP descriptor strings and scalar fields using bounds-aware helpers, verify the descriptor exactly or by prefix, allocate reply data, gather backend state, pack fixed records and string regions, then write RAP status/count metadata into `rparam`. Print queue APIs often call `init_package()` first to calculate buffer pressure and set `ERRmoredata` or `ERRbuftoosmall`. Server enumeration reads and sorts `SERVER_LIST` cache entries from `cache_path()` before packing records, with `RNetServerEnum3` additionally applying a first-name resume search. SAMR handlers open connect/domain/user handles, perform enumeration or lookup, pack fixed-length names and selected user info fields, and close handles on exit.

## State and persistence behavior
The file itself owns no durable state, but it reads and mutates several shared Samba subsystems. `api_RNetShareEnum()` calls `delete_and_reload_printers()`, `load_registry_shares()`, and `load_usershare_shares()` under root privileges to refresh service/share state before enumeration. `get_session_info()` reads the nmbd-maintained `SERVER_LIST` cache file. Print/job/queue calls modify spooler state through `spoolss` (`SetJob`, `SetPrinter`) and map RAP job ids through the printing RAP id layer. `api_RNetShareAdd()` persists shares through `srvsvc_NetShareAdd`. `api_SamOEMChangePassword()` changes account credentials through SAMR. User/session state is read from `smbXsrv_session_info_lookup()`, SAMR, and SRVSVC.

Reply buffers are transient heap allocations (`SMB_MALLOC`, `SMB_REALLOC`) freed by `api_reply()`. RPC policy handles are transient and generally closed before returning. Some handlers allocate extra temporary buffers when caller return size is zero so `pack_desc` can compute required lengths.

## Dependencies and integration points
This module depends heavily on `smbd` request/connection structures, transaction reply helpers, Samba loadparm substitution, session security, RPC client helpers, generated NDR tables for `samr`, `spoolss`, and `srvsvc`, printer job id mapping, machine/domain SID helpers, passdb/auth state, and network browsing cache files. It is an integration shim between SMB1 transaction IPC and newer server-side services; it does not implement the backing account, share, print, or session databases itself.

## Risks and edge cases
The highest risk area is manual RAP buffer packing. Many records use pointer offsets relative to the reply base, fixed-width ASCII fields, and client-supplied descriptor strings; off-by-one or truncation mistakes can corrupt responses or misreport `neededlen`. The code contains many bounds checks, but also uses legacy allocation and pointer arithmetic, including `mdrcnt + 1024` buffers in several user/workstation paths. Integer-size differences matter because RAP lengths are often 16-bit while backend counts are 32-bit.

Compatibility behavior is intentionally odd in places: unsupported info levels sometimes return specific RAP errors instead of failing the transaction; `RNetGroupGetUsers` returns an informational warning with no data; `WAccessGetUserPerms` returns broad `0x7f` permissions; `RNetServerEnum3` emulates Windows first-name matching; some print driver/proc/port enumerations return static placeholder values. Tests should not simplify these without checking old clients.

Security-sensitive surfaces include anonymous access on selected APIs, share addition, password change, print administration, user/group enumeration, and session enumeration. The `auth_user` gate is per-command and only active when `restrict anonymous` is configured; backend RPC access checks are therefore part of the effective policy. Password-change input is fixed at 532 bytes and passed into `samr_OemChangePasswordUser2`; malformed data must not bypass length checks. Share enumeration reloads state as root, so failures in privilege bracketing or service validation would be high impact.

## Test signals
Useful tests are SMB1 RAP transaction torture cases for every `api_commands[]` id, including anonymous and authenticated sessions with `restrict anonymous` toggled. Buffer-limit tests should vary `mdrcnt`/`mprcnt` around exact fit, zero, and truncation thresholds and verify `ERRmoredata`, `ERRbuftoosmall`, `neededlen`, entry counts, and converter words. Print tests should exercise queue/job enum, get, pause/resume/delete/purge, driver level 52, missing printer/job errors, and spoolss failures. Share tests should cover long share names skipped by RAP, usershare/registry/printer reload visibility, and share add through srvsvc. User/group/session tests should verify SAMR/SRVSVC handle cleanup, domain lookup failures, non-user SID lookup, fixed 21-byte names, and anonymous-denied paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_lanman.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_lanman.h -->
# sources/user-network-fs/samba/source3/smbd/smb1_lanman.h

## Purpose
`smb1_lanman.h` exposes the SMB1 LANMAN/RAP transaction entry point implemented in `smb1_lanman.c`. It is a narrow header used by the SMB1 transaction handling path to hand IPC transaction payloads to the legacy remote API dispatcher.

## Important APIs, types, and functions
The sole declaration is `api_reply(connection_struct *conn, uint64_t vuid, struct smb_request *req, char *data, char *params, int tdscnt, int tpscnt, int mdrcnt, int mprcnt)`. The arguments carry the active connection, virtual user id, request object, input transaction data/parameter buffers and their counts, and caller-advertised maximum data/parameter response sizes.

## Control flow
Callers include this header when they have already parsed an SMB transaction request as a RAP/IPC operation. They pass the raw transaction sections to `api_reply()`, which owns command id decoding, authorization checks, handler dispatch, reply buffer construction, and transaction reply sending.

## State and persistence behavior
The header stores no state. It exposes an API that can read or mutate backing Samba state through its implementation, including shares, print queues, accounts, passwords, and browse/session data depending on the RAP command id.

## Dependencies and integration points
The declaration depends on `connection_struct` and `struct smb_request` being visible from the including smbd headers. It forms the compile-time contract between generic SMB1 transaction code and the LANMAN remote-admin compatibility module.

## Risks and test signals
The main risk is signature drift: every caller must pass input and maximum lengths in the same units expected by `api_reply()`. Tests that cover SMB1 RAP transaction dispatch also cover this header contract. Build coverage should catch prototype mismatches, while runtime tests should verify that malformed counts are rejected by the implementation rather than trusted by callers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_lanman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_message.c -->
# sources/user-network-fs/samba/source3/smbd/smb1_message.c

## Purpose
`smb1_message.c` implements legacy SMB1 winpopup-style messaging commands: `SMBsends`, `SMBsendstrt`, `SMBsendtxt`, and `SMBsendend`. These commands collect sender, recipient, and message text from SMB1 requests and deliver the text by writing it to a temporary file and executing the configured `message command`.

## Important APIs, types, and functions
`struct msg_state` holds `from`, `to`, and accumulated `msg` strings. `msg_deliver()` is the central delivery routine: it verifies that `lp_message_command()` is configured, creates a secure temporary file under `tmpdir()` using `mkstemp()` with group/other permissions masked, converts message data from DOS to UNIX codepage when possible, writes the message while collapsing CRLF to LF-style output, substitutes `%f`, `%t`, `%s`, and standard Samba variables into the configured command, then executes it with `smbrun()`.

The public SMB handlers are `reply_sends()` for one-shot messages, `reply_sendstrt()` to begin a multi-part message, `reply_sendtxt()` to append a fragment, and `reply_sendend()` to deliver and clear the accumulated state.

## Control flow
`reply_sends()` checks that a message command is configured, allocates a temporary `msg_state` on `talloc_tos()`, decodes ASCII `from` and `to` strings from `req->buf + 1`, reads a two-byte message length and clamps it to the remaining request buffer, copies the payload, calls `msg_deliver()`, and returns an empty SMB1 success response.

The multi-part path stores state on `req->xconn->smb1.msg_state`. `reply_sendstrt()` frees any prior state, creates a new `msg_state` under the connection, and decodes sender/recipient. `reply_sendtxt()` validates that state exists and the request has at least a length field, clamps the supplied fragment length, `talloc_realloc()`s the accumulated message buffer, appends bytes, and replies success. `reply_sendend()` validates state, calls `msg_deliver()`, frees the connection message state, and replies success.

Each handler uses SMB profile counters and maps missing configuration to `NT_STATUS_REQUEST_NOT_ACCEPTED`; malformed sequencing or too-short buffers return `NT_STATUS_INVALID_PARAMETER`; allocation failure returns `NT_STATUS_NO_MEMORY`.

## State and persistence behavior
One-shot delivery stores message state only for the current request. Multi-part delivery persists partial message state in `xconn->smb1.msg_state` across SMB requests on the same SMB1 connection until `reply_sendend()` or a new `reply_sendstrt()` frees it. Delivery creates a temporary file and leaves lifecycle behavior to the external message command and system temp cleanup; the code does not unlink the file after `smbrun()`.

## Dependencies and integration points
The module depends on SMB1 request parsing helpers (`srvstr_pull_req_talloc()`, `smbreq_bufrem()`), talloc ownership, loadparm substitution, character conversion (`convert_string_talloc()`), filesystem temp creation, `smbrun()`, profile macros, and the `smbXsrv_connection` SMB1 state block. It is invoked from the SMB1 command dispatch table, not from SMB2.

## Risks and edge cases
The largest security risk is command execution: although sender and recipient are filtered through `alpha_strcpy()`, the configured `message command` receives substituted values and a temp-file path. Administrators must treat it as trusted configuration. The temp file is created with restricted permissions but not explicitly removed. Message accumulation uses talloc buffer size as the current length; repeated `SMBsendtxt` fragments can grow memory until normal request/resource limits intervene. `reply_sends()` and `reply_sendtxt()` clamp payload length to the request buffer, which is important for malformed clients.

Conversion fallback intentionally delivers DOS codepage bytes if conversion fails. CRLF handling skips carriage returns when followed by line feed but writes all other bytes one at a time, so very large messages incur many writes. Multi-part sequencing is strict: `sendtxt` or `sendend` without `sendstrt` returns invalid parameter.

## Test signals
Tests should cover no `message command`, one-shot and multi-part delivery, repeated `sendstrt` state replacement, `sendtxt` before start, short buffers, over-declared message lengths, codepage conversion failure fallback, CRLF normalization, temp-file creation failure, and command substitution of sender, recipient, current user/domain, and temp path. Resource tests should verify accumulated message length behavior under many fragments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_message.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_message.h -->
# sources/user-network-fs/samba/source3/smbd/smb1_message.h

## Purpose
`smb1_message.h` declares the SMB1 winpopup messaging command handlers implemented in `smb1_message.c`.

## Important APIs, types, and functions
It exports four request handlers: `reply_sends(struct smb_request *req)`, `reply_sendstrt(struct smb_request *req)`, `reply_sendtxt(struct smb_request *req)`, and `reply_sendend(struct smb_request *req)`. Each handler consumes a parsed SMB1 request and writes its own SMB1 response or error.

## Control flow
The SMB1 command dispatch layer includes this header and calls the appropriate function for the command code. The one-shot handler delivers immediately, while the start/text/end trio coordinates through per-connection SMB1 message state owned by the implementation.

## State and persistence behavior
The header itself is stateless. Its declared functions can create and clear `xconn->smb1.msg_state`, create temporary message files, and run the configured external message command.

## Dependencies and integration points
The only visible dependency is `struct smb_request`. The functions integrate with the SMB1 dispatcher and the connection-level SMB1 state block.

## Risks and test signals
Prototype mismatch is the primary header-level risk. Runtime coverage should include dispatching all four SMB command codes through the normal SMB1 request path and verifying that the implementation emits expected SMB status codes and preserves connection state only between `sendstrt` and `sendend`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_message.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_negprot.c -->
# sources/user-network-fs/samba/source3/smbd/smb1_negprot.c

## Purpose
`smb1_negprot.c` implements the SMB1 `SMB_COM_NEGOTIATE` reply path. It parses the client's dialect list, infers remote client architecture, applies configured min/max server protocol constraints, selects the best supported dialect, initializes per-connection protocol tables, advertises capabilities/security/signing settings, and can hand off to SMB2 negotiation when the client offers SMB2 dialects.

## Important APIs, types, and functions
`reply_negprot(struct smb_request *req)` is the exported request handler. `get_challenge()` creates or refreshes `xconn->smb1.negprot.auth_context` via `make_auth4_context()` and fills an 8-byte NTLM challenge. `reply_lanman1()` and `reply_lanman2()` build downlevel LANMAN negotiate responses with security mode, max buffer, max mux, raw-mode flags, PID, server time, timezone, and optional challenge. `reply_nt1()` builds the NT1 response, including extended security/SPNEGO, Unicode, UNIX extensions, large file/read/write, DFS, NT status, raw mode, signing, server time, capabilities, challenge or SPNEGO blob, workgroup, and NetBIOS name.

The `supported_protocols[]` table lists dialect strings in preference order, from SMB2 wildcard and SMB2.002 down through NT1 and LANMAN variants, with a reply function and protocol level. Architecture bitmasks (`PROT_*`, `ARCH_*`) encode common dialect-list fingerprints for Windows, OS/2, Samba, CIFSFS, Vista, and OSX detection.

## Control flow
`reply_negprot()` rejects multiple negotiate attempts on the same SMB1 connection, empty dialect buffers, and non-null-terminated dialect lists. It walks `req->buf` from byte 1, converting each dialect to a talloced ASCII string and advancing by `strlen(p) + 2` because each dialect entry includes a buffer-format byte plus a NUL-terminated string. It ORs recognized dialect names into a protocol bitmask, special-casing `Samba` and `POSIX 2`, then maps exact bitmask combinations to `set_remote_arch()`.

The handler reloads services after architecture detection, clamps configured max/min protocol values above SMB2_10 down to the SMB2 wildcard negotiation level, and scans `supported_protocols[]` in preferred order. A dialect is selectable only if its protocol level lies within configured min/max and appears in the client list. If none match, it sends a one-word negotiate response with dialect index `0xffff` and exits the server cleanly.

For a selected dialect, it sets the remote protocol short name, reloads services again, calls the selected reply builder, marks `xconn->smb1.negprot.done`, and enforces mandatory signing for downlevel protocols by terminating the connection if signing is required but the chosen level is below NT1. If async SMB echo handling is enabled and the chosen level is below SMB2.002, it forks the echo handler.

## State and persistence behavior
Negotiation mutates per-connection state: `xconn->smb1.negprot.done`, `encrypted_passwords`, `auth_context`, max receive/session table initialization through `smbXsrv_connection_init_tables()`, common flags2, signing behavior, selected remote architecture/protocol globals, and potentially echo-handler process state. It also triggers service reloads because architecture/protocol choices can affect configuration substitutions.

## Dependencies and integration points
The module depends on authentication (`make_auth4_context`, NTLM challenge generation, SPNEGO), signing helpers, SMB1/SMB2 protocol reply builders (`reply_smb2002`, `reply_smb20ff`), loadparm settings (`server min/max protocol`, encrypted passwords, raw I/O, Unicode, UNIX extensions, DFS, NT status, large read/write, signing), profile macros, service reload logic, and remote architecture/protocol tracking. It sits at the front of all SMB1 session setup because later commands depend on the negotiated protocol tables and capabilities.

## Risks and edge cases
Dialect parsing is security-sensitive because the input is a packed list of variable strings. The code checks final NUL termination and allocation failures, but relies on the SMB request buffer helpers and dialect entry structure. Multiple negotiation attempts intentionally terminate the server connection. No-protocol selection sends the MS-CIFS-required `0xffff` index before clean exit.

Compatibility risks are high: client architecture inference depends on exact dialect-list bitmasks and affects service reload behavior. Capability advertising must stay consistent with configuration and signing: raw mode is disabled when signing is desired, extended security is only advertised when encrypted passwords and client flags allow it, and mandatory signing rejects LANMAN. SMB2 handoff depends on treating all protocols above SMB2_10 as `SMB 2.???` at the SMB1 negotiate stage.

## Test signals
Tests should exercise dialect lists for NT1, LANMAN1/2, Samba, CIFSFS-only, Vista-style SMB2 wildcard, OSX SMB2.002/wildcard, unsupported dialects, non-NUL-terminated buffers, empty buffers, repeated negotiate, configured min/max protocol boundaries, mandatory signing with downlevel dialects, raw-mode suppression under signing, extended-security SPNEGO vs challenge responses, and async echo handler setup. Wire-level assertions should verify dialect index, security word bits, capabilities, challenge/SPNEGO payload, time fields, and `0xffff` no-protocol behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_negprot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_negprot.h -->
# sources/user-network-fs/samba/source3/smbd/smb1_negprot.h

## Purpose
`smb1_negprot.h` declares the SMB1 negotiate-protocol request handler.

## Important APIs, types, and functions
It exports `reply_negprot(struct smb_request *req)`, the handler for SMB1 `SMB_COM_NEGOTIATE`. The function consumes the dialect list in the request and emits the selected dialect response or an error/connection termination.

## Control flow
The SMB1 dispatcher calls `reply_negprot()` before normal SMB1 session setup and tree operations. Once it completes successfully, the connection has protocol tables, security mode, capabilities, and remote architecture/protocol state initialized.

## State and persistence behavior
The header has no state. The implementation behind the declaration mutates `xconn->smb1.negprot`, signing state, auth challenge context, selected protocol metadata, and possibly echo-handler state.

## Dependencies and integration points
The visible dependency is `struct smb_request`. The declared function integrates with the SMB1 command dispatcher and indirectly with SMB2 negotiation when SMB2 dialects are selected from an SMB1 negotiate frame.

## Risks and test signals
Header-level risk is limited to keeping the request-handler signature consistent with the dispatch table. Functional tests should enter through the SMB1 negotiate command rather than calling internals so the declaration, dispatcher binding, and implementation side effects are all covered.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_negprot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_nttrans.c -->
# sources/user-network-fs/samba/source3/smbd/smb1_nttrans.c

## Purpose
`smb1_nttrans.c` implements SMB1 NT transaction handling and several related SMB1 NT command replies. It covers `NT_CREATE_ANDX`, `NT_TRANSACT_CREATE`, notify change, rename, security descriptor query/set, FSCTL dispatch, optional quota query/set, transaction fragment assembly, secondary transaction continuation, and NT cancel. It is the SMB1 bridge from NT-style wire requests to Samba VFS, locking, notify, security, quota, and named-pipe subsystems.

## Important APIs, types, and functions
The exported handlers are `reply_ntcreate_and_X()`, `reply_ntcancel()`, `reply_ntrename()`, `reply_nttrans()`, and `reply_nttranss()`. `send_nt_replies()` is the core NT transaction response splitter; it builds one or more SMB1 NT transaction response packets with total counts, per-packet counts, offsets, displacements, 4-byte data alignment, optional NT error status, sequence number signing offset, encryption flag, and max-send fragmentation.

`nttrans_realloc()` reallocates parameter/data reply buffers with zero fill. `nt_open_pipe()`, `do_ntcreate_pipe_open()`, and `do_nt_transact_create_pipe()` implement named pipe open responses for IPC connections. `set_posix_case_semantics()` and its destructor `restore_case_semantics()` temporarily force POSIX case behavior while converting/opening paths with `FILE_FLAG_POSIX_SEMANTICS`. `get_relative_fid_filename()` resolves root-directory-relative opens.

`reply_ntcreate_and_X()` handles direct SMB NT create-and-X. `call_nt_transact_create()` handles the NT transaction create variant, including security descriptor and EA parsing. Other transaction subhandlers are `call_nt_transact_notify_change()`, `call_nt_transact_rename()`, `call_nt_transact_query_security_desc()`, `call_nt_transact_set_security_desc()`, `call_nt_transact_ioctl()`, and, when compiled with quotas, `call_nt_transact_get_user_quota()` and `call_nt_transact_set_user_quota()`. `handle_nttrans()` dispatches a fully assembled `struct trans_state` by `state->call`.

## Control flow
The create paths parse flags, desired access, file attributes, share access, create disposition/options, root directory FID, allocation size, and path. IPC connections are routed to named-pipe open if pipe support is enabled. Filesystem paths pass through optional POSIX case mode, relative-FID prefixing, GMT snapshot token extraction, DFS stripping, and `filename_convert_dirfsp()`. Both create variants mask ignored create-option bits and remove `FILE_FLAG_POSIX_SEMANTICS` before calling `SMB_VFS_CREATE_FILE()`.

On successful file create, the code computes the returned oplock level from the request flags, fake-oplock setting, and `fsp->oplock_type`; gathers file size, allocation size, DOS attributes, create/access/write/change times with optional DOS resolution; checks EA and stream status for extended responses; and emits either 34/50-word create-and-X or 69/101-byte NT transaction create response parameter data. Sharing violations can be deferred through SMB1 retry machinery; deferred opens do not send immediate errors.

`reply_nttrans()` validates the primary NT transaction word count, extracts total/current parameter and data counts, offsets, setup count, max return sizes, and function code. It denies non-create NT transactions on IPC trees, calls `allow_new_trans()`, allocates a `trans_state`, caps total data/params at 128 MiB each, validates all offsets with `smb_buffer_oob()`, copies primary fragments, copies setup words, and either dispatches immediately or links the state into `conn->pending_trans` and sends an interim empty response. `reply_nttranss()` finds the pending state by MID, forces the reply command back to `SMBnttrans` for Windows compatibility, accepts reduced totals, validates displacement/offset ranges, copies secondary fragments, and dispatches when all bytes have arrived.

`handle_nttrans()` sets the long-name flag for NT1 or newer connections and switches on the NT transaction subcommand. Notify change validates the setup, resolves the FID, creates or reuses per-FSP notify state, replies immediately if changes are pending, otherwise queues the request. NT cancel removes pending change notifies by MID or finishes pending byte-range-lock work. Rename resolves source and destination paths, handles named streams specially, and dispatches to rename, hardlink, or copy internals depending on the rename type.

## State and persistence behavior
The module mutates durable filesystem state through `SMB_VFS_CREATE_FILE()`, rename/copy/hardlink internals, security descriptor setters, FSCTL VFS calls, and optional quota setters. It opens named pipes through `open_np_file()`. It creates temporary transaction assembly state in `conn->pending_trans` until all fragments arrive or an error cancels the state. Notify requests may persist asynchronously in change-notify queues tied to the FSP/request MID. Create responses expose and update open file state through new `files_struct` handles, share-mode/oplock state, and VFS stat metadata.

The temporary POSIX case-semantics object modifies `connection_struct` case fields and relies on talloc destructor cleanup to restore them. Transaction parameter/data buffers are allocated with `SMB_MALLOC` because downstream routines may `SMB_REALLOC()` them; they are freed after dispatch. Quota handlers use temporary talloc contexts and NDR blobs.

## Dependencies and integration points
This file depends on SMB1 packet layout macros, transaction state management, named pipe open code, filename conversion and DFS stripping, snapshot token parsing, VFS create/FSCTL/quota APIs, EA parsing, security descriptor marshalling/unmarshalling, ACL setters, change notify infrastructure, byte-range lock cancellation, oplock constants, share violation deferral, and SMB signing/encryption send paths. It is tightly coupled to `struct smb_request`, `connection_struct`, `files_struct`, and the Samba VFS contract.

## Risks and edge cases
The most critical risks are bounds and integer handling in fragmented NT transactions. The code validates total sizes, current counts, offsets, and displacements, but these paths process attacker-controlled 32-bit lengths and offsets and allocate up to 128 MiB per parameter/data stream. Fragment accounting increments received counts before copy validation in `reply_nttranss()`, with error cleanup if totals are exceeded.

Create handling is security-sensitive because it combines path parsing, DFS/snapshot semantics, relative FIDs, POSIX case behavior, EA lists, initial security descriptors, share modes, oplock requests, and allocation size. The code explicitly checks EA/security descriptor length sums for overflow and data-count mismatch. Named-pipe create responses contain compatibility-specific word counts and access masks. Extended responses must keep wire layout quirks such as 50 words with `smb_wct` set to 42.

Notify and cancel behavior is asynchronous and MID-based; regressions can leak pending requests or send duplicate replies. Security descriptor operations must mask unsupported `SECINFO` flags and enforce write access for setters. IOCTL support deliberately accepts only FSCTLs on open files and delegates function-specific behavior to VFS. Quota operations are root-only (`sec_initial_uid`) and compile-time gated.

## Test signals
Coverage should include NT create-and-X and NT transaction create for files, directories, streams, IPC pipes, relative root FIDs, POSIX pathname/case semantics, DFS referrals, snapshot tokens, EAs, initial security descriptors, all create dispositions, allocation sizes, extended responses, and oplock grant variants. Fragmentation tests should send primary-only, multi-secondary, out-of-order displacement, reduced total, over-total, bad offset, bad setup count, huge total, and duplicate MID transactions. Notify tests should verify immediate vs queued replies, recursive filters, cancel by MID, non-directory rejection, and connection mismatch. Security tests should verify query buffer-too-small, set ACL denied on read-only shares, unsupported SECINFO masking, malformed descriptors, FSCTL rejection for non-FSCTL, and quota access restrictions when quotas are compiled in.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_nttrans.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_nttrans.h -->
# sources/user-network-fs/samba/source3/smbd/smb1_nttrans.h

## Purpose
`smb1_nttrans.h` declares the SMB1 NT create and NT transaction request handlers implemented in `smb1_nttrans.c`.

## Important APIs, types, and functions
The header exports `reply_ntcreate_and_X(struct smb_request *req)`, `reply_ntcancel(struct smb_request *req)`, `reply_ntrename(struct smb_request *req)`, `reply_nttrans(struct smb_request *req)`, and `reply_nttranss(struct smb_request *req)`. These correspond to SMB1 NT create-and-X, cancel, NT rename, primary NT transaction, and secondary NT transaction commands.

## Control flow
The SMB1 dispatcher calls these functions based on command code. The primary/secondary NT transaction pair coordinates through pending transaction state in the implementation; callers do not manage assembly directly. Each function owns response emission or asynchronous deferral.

## State and persistence behavior
The header is stateless. The declared implementation can create/open files and pipes, queue transaction fragments, queue notify requests, cancel pending work, rename/copy/hardlink paths, alter security descriptors, perform FSCTLs, and optionally query/set quotas.

## Dependencies and integration points
The visible dependency is `struct smb_request`. The declarations integrate the SMB1 command dispatch layer with VFS, notify, security, pipe, and transaction subsystems through the implementation.

## Risks and test signals
Header-level risk is keeping dispatcher signatures synchronized. End-to-end SMB1 tests should cover each declared command through normal dispatch so command-code binding, request lifetime, transaction state ownership, and response behavior are verified together.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_nttrans.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_oplock.c -->
# sources/user-network-fs/samba/source3/smbd/smb1_oplock.c

## Purpose
`smb1_oplock.c` builds and sends SMB1 oplock break notifications. It is the SMB1-specific wire-format adapter used when Samba needs to tell a client to release or downgrade an oplock on an open file.

## Important APIs, types, and functions
`new_break_message_smb1(files_struct *fsp, int cmd, char result[SMB1_BREAK_MESSAGE_LENGTH])` initializes an SMB1 `SMBlockingX` oplock break message. It zeroes the SMB header, calls `srv_smb1_set_message(result, 8, 0, true)`, sets command, tree id, PID/UID/MID sentinel values, AndX terminator, target FID, `LOCKING_ANDX_OPLOCK_RELEASE`, and the requested break command/level byte.

`send_break_message_smb1(files_struct *fsp, int level)` selects the sole SMB1 connection from `fsp->conn->sconn->client->connections`, builds the break message, logs it with `show_msg()`, and sends it with `smb1_srv_send()` using the connection encryption state. Send failure is fatal and calls `exit_server_cleanly()`.

## Control flow
The generic oplock/lease break path calls the SMB1 send routine for files opened over SMB1. The code assumes SMB1 has exactly one connection for the client, builds a fixed-size break frame on the stack, and sends it synchronously. No reply is expected from these functions; any client response is handled by separate locking/oplock release paths.

## State and persistence behavior
The module does not persist state itself. It reads `files_struct` fields (`fnum`, connection, tree id, encryption status) and writes a transient network message. The resulting client behavior may later alter oplock/share-mode state elsewhere.

## Dependencies and integration points
It depends on SMB1 packet layout helpers, `files_struct`, `connection_struct`, SMB1 send code, lock/oplock constants, and server-exit behavior. The included lease/share-mode headers reflect its placement in the broader locking subsystem, though this file only formats and sends the SMB1 break message.

## Risks and edge cases
The wire layout is small but exact: incorrect word count, FID, command byte, or sentinel IDs can make clients ignore oplock breaks. The single-connection assumption is explicit for SMB1; using this helper for SMB2/multichannel would be wrong. Send failure terminates the server process cleanly because failing to deliver an oplock break can compromise cache coherency.

## Test signals
Tests should verify the exact SMB1 bytes produced by `new_break_message_smb1()` for representative FIDs/tree ids and break levels, including `SMBlockingX`, `LOCKING_ANDX_OPLOCK_RELEASE`, `0xFFFF` PID/MID, and word count. Integration tests should open an SMB1 file with an oplock, trigger a conflicting open, confirm the break message is sent encrypted when the tree is encrypted, and verify server behavior on simulated send failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_oplock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_oplock.h -->
# sources/user-network-fs/samba/source3/smbd/smb1_oplock.h

## Purpose
`smb1_oplock.h` declares the SMB1 oplock break message size and helper functions used by the locking/oplock subsystem.

## Important APIs, types, and functions
`SMB1_BREAK_MESSAGE_LENGTH` is defined as `smb_size + 8*2`, matching an SMB1 header plus eight parameter words and no byte data. `new_break_message_smb1(files_struct *fsp, int cmd, char result[SMB1_BREAK_MESSAGE_LENGTH])` formats a caller-provided buffer. `send_break_message_smb1(files_struct *fsp, int level)` formats and sends the break to the SMB1 client.

## Control flow
Locking/oplock code includes this header when it needs to produce an SMB1 oplock break. Callers can either build the message for inspection/testing or send it directly.

## State and persistence behavior
The header is stateless. The implementation reads file and connection state and emits a network message; oplock state transitions occur in the broader locking subsystem.

## Dependencies and integration points
The declarations require `files_struct` and SMB packet size macros from surrounding smbd headers. They integrate SMB1 wire formatting with generic oplock break logic.

## Risks and test signals
The macro length must remain consistent with `new_break_message_smb1()`'s `srv_smb1_set_message(..., 8, 0, ...)` call. Compile and unit tests should catch signature drift; byte-layout tests should catch macro or format mismatches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/smbd/smb1_oplock.h -->

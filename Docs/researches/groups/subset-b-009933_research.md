# subset-b-009933 research

Grouped research for Samba raw SMB client interface and implementation files.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/interfaces.h -->
# sources/user-network-fs/samba/source4/libcli/raw/interfaces.h

Purpose: `interfaces.h` is the central typed contract for Samba source4's raw SMB client layer. It defines the request/response unions passed between raw SMB packet builders/parsers, composite client helpers, SMB2 adapters, and NTVFS backends. The file intentionally preserves SMB wire-level distinctions: old SMB commands, AndX forms, trans2/nttrans levels, SMB2-specific structs, Unix extensions, EA/security descriptor payloads, and generic aliases.

Important APIs, types, and functions: Key types include `smb_wire_string`, `smb2_handle`, `smb2_lease_break`, `smb_handle_or_path`, and `smb_handle`. Major unions include `smb_seek`, `smb_unlink`, `smb_mkdir`, `smb_rename`, `smb_tcon`, `smb_sesssetup`, `smb_fileinfo`, `smb_setfileinfo`, `smb_fsinfo`, `smb_setfsinfo`, `smb_open`, `smb_read`, `smb_write`, `smb_lock`, `smb_close`, `smb_lpq`, `smb_ioctl`, `smb_flush`, `smb_notify`, search first/next/close/data unions, `smb_trans2`, `smb_nttrans`, `smb_echo`, and `smb_shadow_copy`. The `SMB_OPEN_OUT_FILE` macro abstracts the per-level location of output handles.

Control flow: This header does not execute control flow; it drives dispatch in implementation files through each union's `generic.level` or equivalent enum. Callers fill an `in` branch and a level, raw send functions encode that branch into SMB, recv functions populate the matching `out` branch, and composite/adapter layers can reuse the same union shapes for SMB1, SMB2, or NTVFS paths.

State and persistence behavior: The definitions are transient request containers. They do not own durable filesystem state, but many fields carry stateful protocol handles, search handles, lock arrays, lease/oplock state, durable handle data, and session/tree identifiers indirectly through caller-owned request structures. `smb_wire_string.private_length` preserves wire lengths for compliance tests while `s` remains the semantic string.

Dependencies and integration points: It includes raw SMB constants, common SMB definitions, GUID/security/lease generated NDR types, and EA/security descriptor structs used by parser helpers. Integration is broad: `rawfile.c`, `rawreadwrite.c`, `rawfileinfo.c`, `rawfsinfo.c`, `rawsearch.c`, SMB2 getinfo/create/ioctl code, NTVFS CIFS passthrough, torture tests, and server-side trans2/nttrans parsers share these layouts.

Risks: Because this is an ABI-like internal contract, changing enum values, field widths, branch names, or handle placement can silently corrupt wire encoding. Several enums intentionally equal SMB info-level constants; reordering or renumbering would break dispatch. Some branches include SMB2 fields in a header mostly used by SMB1 raw code, so implementers must check which implementation actually supports a level. Many `const char *` and blob pointers are caller-owned; lifetime assumptions are external.

Test signals: Good coverage comes from raw torture suites for open, read, write, search, qfileinfo, setfileinfo, ACLs, streams, oplocks, and Unix extensions. Compile-time coverage is also meaningful because most raw modules include this header. Compatibility tests should confirm generic aliases map to the intended specific levels and that wire-string lengths are preserved for compliance cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/interfaces.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/libcliraw.h -->
# sources/user-network-fs/samba/source4/libcli/raw/libcliraw.h

Purpose: `libcliraw.h` is the public/internal umbrella header for source4 raw SMB client operations. It combines raw interface data structures with transport/session/tree/request state and declares the send/recv/sync entry points used by higher-level client, composite, torture, and NTVFS code.

Important APIs, types, and functions: The main state structs are `smbcli_negotiate`, `smbcli_socket`, `smbcli_options`, `smbcli_transport`, `smbcli_session`, `smbcli_tree`, and `smbcli_request`. `smbcli_request_state` tracks request lifecycle. The header exposes request helpers such as `smbcli_request_destroy`, `smbcli_request_simple_recv`, `smbcli_transport_process`, raw operations for open/close/read/write/lock/seek/rename/mkdir/unlink/chkpath/flush, metadata calls (`smb_raw_fileinfo`, `smb_raw_pathinfo`, `smb_raw_fsinfo`, `smb_raw_setfsinfo`), trans2 helpers, change notify, echo, tree/session teardown, oplock handlers, idle handlers, and raw search entry points. `SMBCLI_CHECK_WCT` and `SMBCLI_CHECK_MIN_WCT` are parser guard macros.

Control flow: Callers typically allocate or reuse a tree/session/transport, call a `*_send` function that returns an `smbcli_request`, then call a matching `*_recv` or use the sync wrapper. Request objects move from `INIT` through `RECV` to `DONE` or `ERROR`, with `smbcli_request_destroy` returning the final `NTSTATUS`. Parser functions use word-count macros to reject malformed replies and jump to a common cleanup label.

State and persistence behavior: The structs hold negotiated protocol state, server capabilities, security blobs, signing/options, event context, last transport error, oplock callback state, session IDs, tree IDs, request buffers, async callbacks, and trans2/nttrans substate. No filesystem data is persisted here; it is connection/request state with talloc-managed lifetimes.

Dependencies and integration points: This header includes `smb_common.h`, raw request buffer definitions, NBT NDR types, `interfaces.h`, and SMB2 negotiate-context types. It integrates with `smbXcli` transport/session/tree objects, tevent-driven request processing, client wrappers, composite operations, raw implementations, and torture tests.

Risks: This header exposes low-level internals, so misuse can bypass safer composite abstractions. Request lifetime is subtle because `do_not_free` can suppress cleanup and async callbacks can discard replies if unset. Buffer pointers in `smbcli_request` are invalidated by growth/reallocation. The macros assume a local `failed` label and mutate `req->status`, so they require consistent function structure.

Test signals: Raw torture suites exercise most declared operations. Transport tests should check negotiate state, timeout handling, request destruction status propagation, malformed WCT rejection, oplock callback paths, and async send/recv pairing. Build coverage is important because this header is included throughout raw client code.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/libcliraw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawacl.c -->
# sources/user-network-fs/samba/source4/libcli/raw/rawacl.c

Purpose: `rawacl.c` implements raw SMB1 NT transaction query and set security descriptor operations for file ACLs. It bridges `RAW_FILEINFO_SEC_DESC` and `RAW_SFILEINFO_SEC_DESC` union branches to `NT_TRANSACT_QUERY_SECURITY_DESC` and `NT_TRANSACT_SET_SECURITY_DESC`.

Important APIs, types, and functions: Public-style entry points are `smb_raw_query_secdesc_send`, `smb_raw_query_secdesc_recv`, `smb_raw_query_secdesc`, `smb_raw_set_secdesc_send`, and `smb_raw_set_secdesc`. They use `union smb_fileinfo`, `union smb_setfileinfo`, `struct smb_nttrans`, `struct security_descriptor`, NDR pull/push helpers, `smb_raw_nttrans_send`, `smb_raw_nttrans_recv`, and `smbcli_request_simple_recv`.

Control flow: Query builds an 8-byte parameter block containing file number, padding, and security info flags, asks for up to `0xFFFF` data bytes, sends an NT transaction, validates the returned 4-byte parameter length against returned data, truncates the blob to the reported descriptor size, and NDR-decodes a security descriptor. Set builds the same identifying parameter block, NDR-encodes the input descriptor into the data blob, sends an NT transaction, and the sync wrapper waits for a status-only response.

State and persistence behavior: The code does not persist state locally. It reads or modifies server-side ACL state for an already-open SMB file handle. Output descriptors are talloc-allocated under the caller's memory context. Temporary NDR contexts are freed after request construction.

Dependencies and integration points: It depends on raw NT transaction helpers and generated `ndr_security` routines. It is called directly by `rawfileinfo.c` for `RAW_FILEINFO_SEC_DESC` and by setfileinfo code for security descriptor writes. Torture ACL tests and composite ACL append paths are the main consumers.

Risks: Only SMB1 file-number handles are encoded; SMB2 security descriptor operations are handled elsewhere. Query trusts the returned descriptor length only after checking it fits inside the returned data. Set returns `NULL` if NDR push fails, so sync callers receive the generic unsuccessful status from `smbcli_request_destroy(NULL)`. Security descriptor memory ownership and exact `secinfo_flags` semantics must match callers.

Test signals: `source4/torture/raw/acls.c` and raw session/security tests exercise query/set ACL behavior. Tests should cover owner/group/DACL/SACL flag combinations, malformed or short NT transaction replies, very large descriptors, and server errors from insufficient access.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawacl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawdate.c -->
# sources/user-network-fs/samba/source4/libcli/raw/rawdate.c

Purpose: `rawdate.c` is a thin adapter around Samba DOS date conversion helpers. It ensures raw SMB client packet encoders and parsers consistently use the negotiated server timezone stored in `smbcli_transport`.

Important APIs, types, and functions: The file exports `raw_push_dos_date`, `raw_push_dos_date2`, `raw_push_dos_date3`, `raw_pull_dos_date`, `raw_pull_dos_date2`, and `raw_pull_dos_date3`. These call lower-level `push_dos_date*` and `pull_dos_date*` helpers with `transport->negotiate.server_zone`.

Control flow: Each push function receives a Unix `time_t`, a target buffer, and an offset, then writes the corresponding SMB DOS date layout. Each pull function receives a pointer to wire date bytes and returns a GMT Unix `time_t` adjusted from the server zone. The three variants match SMB wire formats with different word order or 32-bit "Unix-like" DOS timestamp layout.

State and persistence behavior: No state is stored. The only state read is `transport->negotiate.server_zone`, populated during negotiation. The functions mutate caller-provided packet buffers for outgoing requests.

Dependencies and integration points: Raw file open/close, read/write-close, metadata, and search parsers call these helpers for legacy SMB date fields. They depend on negotiate having recorded server time zone accurately. NTTIME fields use separate helpers in `rawrequest.c`; this file is for DOS date formats.

Risks: Timestamp correctness depends on negotiation data and legacy DOS date semantics, including local-time conversion and DST behavior. Using the wrong variant (`date`, `date2`, or `date3`) swaps word order or format and can produce plausible but wrong timestamps. These functions assume valid buffer space at the supplied offset.

Test signals: Raw open, qfileinfo, search, delay-write, and setfileinfo torture tests indirectly validate timestamp round-trips. Targeted tests should compare servers in non-UTC time zones, boundary dates, zero timestamps, and operations that mix DOS time and NTTIME fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawdate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/raweas.c -->
# sources/user-network-fs/samba/source4/libcli/raw/raweas.c

Purpose: `raweas.c` serializes and parses SMB extended attribute lists and EA name lists. It supports both classic trans2 EA list format and chained full-EA formats used by NT transact/SMB2-style payloads.

Important APIs, types, and functions: Size/encode helpers include `ea_list_size`, `ea_list_size_chained`, `ea_put_list`, `ea_put_list_chained`, and `ea_push_name_list`. Parse helpers include `ea_pull_struct`, `ea_pull_list`, `ea_pull_list_chained`, and `ea_pull_name_list`; `ea_pull_name` and `ea_name_list_size` are local helpers. The file operates on `struct ea_struct`, `struct ea_name`, `struct smb_wire_string`, and `DATA_BLOB`.

Control flow: Writers compute the exact wire size, fill length headers, flags, name lengths, value lengths, null-terminated names, value data, and chained next-entry offsets with alignment padding. Parsers validate minimum blob sizes, declared total sizes, per-entry name/value lengths, chained `next_ofs` monotonicity, and allocation success, then talloc arrays for output EAs/names.

State and persistence behavior: No durable state is kept. Output arrays, names, and value blobs are allocated beneath the caller's memory context. Parsed EA values are allocated with one extra zero byte and then length is decremented so binary data remains length-tracked while also being safely inspectable as a C string in tests/debugging.

Dependencies and integration points: `rawfile.c` uses EA writers for trans2 mkdir, trans2 open, and NTTRANS create. `rawfileinfo.c` and `rawsearch.c` use EA parsers for EA query/search levels. Server-side SMB/SMB2 parsers and NTVFS paths also reuse these helpers, so this file is shared client/server utility code within the raw layer.

Risks: The size functions assume EA names are strict ASCII and use `strlen`, so embedded NULs or non-ASCII naming rules are not represented. Chained parsing must avoid integer wrap; the code checks `ofs + next_ofs` and `ofs + 4`, but edge cases around zero offsets and malformed padding deserve coverage. Writers assume caller-provided buffers are preallocated to the computed size.

Test signals: EA-related qfileinfo/search tests, SMB2 create EA tests, and server trans2 parser tests are relevant. Useful cases include empty lists, zero-length values, maximum 8-bit name lengths, malformed declared total length, chained offset loops/overflows, and EA list requests that ask for selected names only.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/raweas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawfile.c -->
# sources/user-network-fs/samba/source4/libcli/raw/rawfile.c

Purpose: `rawfile.c` implements SMB1 raw file namespace, open, close, lock, flush, checkpath, and seek operations. It is the low-level packet builder/parser for many `union smb_open`, `smb_rename`, `smb_mkdir`, `smb_close`, `smb_lock`, `smb_flush`, and `smb_seek` levels.

Important APIs, types, and functions: Key entry points include `smb_raw_rename_send/smb_raw_rename`, `smb_raw_unlink_send/smb_raw_unlink`, `smb_raw_mkdir_send/smb_raw_mkdir`, `smb_raw_rmdir_send/smb_raw_rmdir`, `smb_raw_open_send/smb_raw_open_recv/smb_raw_open`, `smb_raw_close_send/smb_raw_close`, `smb_raw_lock_send/smb_raw_lock`, `smb_raw_chkpath_send/smb_raw_chkpath`, `smb_raw_flush_send/smb_raw_flush`, and `smb_raw_seek_send/smb_raw_seek_recv/smb_raw_seek`. Local helpers handle `TRANSACT2_MKDIR`, `TRANSACT2_OPEN`, and `NT_TRANSACT_CREATE`.

Control flow: Most functions switch on the union's `generic.level`, build the corresponding SMB command with `smbcli_request_setup`, fill VWV fields and data strings/blobs, send, then receive and parse level-specific reply words. Open has the richest flow: old open, OpenX, mknew/create/ctemp/splopen, NTCreateX, trans2 open, NTTRANS create, and chained OpenX/ReadX or NTCreateX/ReadX. Chained opens call `smbcli_chained_request_setup` and `smbcli_chained_advance` to parse the read response after open metadata.

State and persistence behavior: The file creates and destroys transient requests but changes server-side state: rename/unlink/mkdir/rmdir mutate namespace, open returns file handles, close releases handles, locks affect byte-range locking state, flush commits server buffers, and seek returns a server-calculated offset. It relies on `tree->session->transport->negotiate.capabilities` for large-file offsets and date conversion.

Dependencies and integration points: It depends on raw request helpers, trans2/nttrans helpers, EA serialization, NDR security descriptor encoding, DOS date helpers, and raw read parsing for chained reads. Higher-level `clifile`, torture raw tests, NTVFS CIFS passthrough, and client commands integrate with these calls.

Risks: SMB2 levels return `NULL` here, so callers must route SMB2 elsewhere. Many branches assume the matching union branch is initialized correctly. Chained read output buffers must be allocated by the caller before receive. The code has multiple wire-offset constants; mistakes break interoperability. Some allocation failures in helper paths return `NULL` after allocating temporary contexts, and packet growth invalidates local pointers.

Test signals: `source4/torture/raw/open.c`, `unlink.c`, `seek.c`, `oplock.c`, lock tests, and basic namespace tests exercise this file. Important coverage includes large-file offsets with and without `CAP_LARGE_FILES`, chained open-read bounds checks, ctemp returned names, NTTRANS create with EAs/security descriptors, flush-all, and malformed WCT replies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawfileinfo.c -->
# sources/user-network-fs/samba/source4/libcli/raw/rawfileinfo.c

Purpose: `rawfileinfo.c` implements raw SMB file and path metadata query operations. It sends SMBgetatr/getattrE and trans2 QFILEINFO/QPATHINFO requests, and parses classic, NT passthrough, Unix extension, EA, stream, security descriptor, and SMB2-style info blobs into `union smb_fileinfo`.

Important APIs, types, and functions: Major functions are `smbcli_parse_stream_info`, `smb_raw_fileinfo_passthru_parse`, `smb_raw_fileinfo_send`, `smb_raw_fileinfo_recv`, `smb_raw_fileinfo`, `smb_raw_pathinfo_send`, `smb_raw_pathinfo_recv`, and `smb_raw_pathinfo`. Local helpers include `smb_raw_info_backend`, blob send/recv wrappers, `smb_raw_getattr_send/recv`, and `smb_raw_getattrE_send/recv`.

Control flow: Send functions route non-trans2 levels to specialized SMB commands or ACL helpers, reject generic/private levels, optionally encode EA name lists, and send trans2 requests with the requested info level. Receive functions handle the special levels first, then pull a data blob and dispatch through `smb_raw_info_backend`. Passthrough parsing switches by normalized info class and validates exact or minimum blob sizes before extracting times, sizes, attributes, names, streams, EAs, file IDs, access masks, and security descriptors.

State and persistence behavior: Queries do not mutate server filesystem state. They allocate returned strings, EA arrays, stream arrays, and security descriptors under the caller's memory context. Parsing uses `req->session` for negotiated string handling and `req->transport` for DOS date conversion.

Dependencies and integration points: This file depends on trans2 helpers, ACL helpers in `rawacl.c`, EA parsers, raw string/blob helpers, GUID/security NDR parsing, and date helpers. SMB2 getinfo code reuses `smb_raw_fileinfo_passthru_parse`, so the parser supports SMB2 all-information and all-EA variants even though send paths here are SMB1.

Risks: Wire formats differ across servers; the parser accepts some documented deviations, such as 36 vs 40 bytes for basic information and the corrected all-information filename offset. `smbcli_blob_pull_string` return values are not always checked for zero, so malformed names may surface as NULL strings unless size checks catch them. Any wrong size constant or alias mapping can corrupt output silently. `req` may be NULL only on some special paths; code captures session with `req ? req->session : NULL`.

Test signals: Raw qfileinfo, streams, ACLs, Unix info2, delay-write, delete, attr, and SMB2 getinfo tests are direct signals. Tests should cover each info level, path vs handle queries, EA-list requests, stream list malformed next offsets, security descriptor parsing, non-Unicode negotiation, and server-specific short/long passthrough replies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawfileinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawfsinfo.c -->
# sources/user-network-fs/samba/source4/libcli/raw/rawfsinfo.c

Purpose: `rawfsinfo.c` implements raw SMB filesystem information query and set operations. It supports the legacy `SMBdskattr` call, trans2 `TRANSACT2_QFSINFO`, passthrough filesystem info classes, and Unix CIFS setfsinfo.

Important APIs, types, and functions: Entry points are `smb_raw_fsinfo_send`, `smb_raw_fsinfo_passthru_parse`, `smb_raw_fsinfo_recv`, `smb_raw_fsinfo`, and `smb_raw_setfsinfo`. Local helpers include `smb_raw_dskattr_send/recv`, `smb_raw_qfsinfo_send`, `smb_raw_qfsinfo_blob_recv`, `smb_raw_setfsinfo_send`, and `smb_raw_setfsinfo_recv`.

Control flow: Query send dispatches `RAW_QFS_DSKATTR` to `SMBdskattr`, rejects generic levels, or sends trans2 QFSINFO with the enum value as the info level. Receive either parses the dskattr words or receives a data blob and switches by info level. Passthrough parsing extracts volume, size, device, attributes, quota, full-size, object ID, and sector-size fields with strict length checks. Setfsinfo only supports `RAW_SETFS_UNIX_INFO`, encodes version/capability into a 12-byte data blob, and sends `TRANSACT2_SETFSINFO`.

State and persistence behavior: Query paths only populate caller-provided `union smb_fsinfo` output fields. Setfsinfo can alter server-side Unix extension negotiation/capability state for the tree/session. All allocations for returned volume names, filesystem names, and GUID parsing are caller-context scoped.

Dependencies and integration points: It depends on raw trans2 helpers, `smbcli_blob_pull_string`, `smbcli_pull_nttime`, GUID NDR parsing, and the fsinfo union in `interfaces.h`. Client statfs wrappers, torture raw filesystem tests, Unix extension tests, and SMB2 filesystem info adapters use these parsers or level definitions.

Risks: The `RAW_QFS_OBJECTID_INFORMATION` switch block encloses `RAW_QFS_SECTOR_SIZE_INFORMATION` before closing the brace, making sector-size parsing visually nested and easy to modify incorrectly. The Unix info parser stores `capability` with `SVAL` even though the interface field is 64-bit, which may be intentional legacy behavior but deserves scrutiny. Strict exact-size checks may reject nonconforming servers. Generic/SMB2 handle-bearing levels are only partially represented in this SMB1 send path.

Test signals: Raw filesystem info and Unix extension torture tests should cover every query level, volume/attribute strings under Unicode and ASCII, object ID GUID parsing, quota/full-size fields, sector size info, dskattr, unsupported generic levels, and `RAW_SETFS_UNIX_INFO` status behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawfsinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawioctl.c -->
# sources/user-network-fs/samba/source4/libcli/raw/rawioctl.c

Purpose: `rawioctl.c` implements raw SMB1 IOCTL operations through both the legacy `SMBioctl` command and NT transaction `NT_TRANSACT_IOCTL`.

Important APIs, types, and functions: Public entry points are `smb_raw_ioctl_send`, `smb_raw_ioctl_recv`, and `smb_raw_ioctl`. Internal helpers are `smb_raw_smbioctl_send`, `smb_raw_smbioctl_recv`, `smb_raw_ntioctl_send`, and `smb_raw_ntioctl_recv`. The code uses `union smb_ioctl`, `struct smb_nttrans`, `DATA_BLOB`, and raw request/blob helpers.

Control flow: `smb_raw_ioctl_send` switches on `parms->generic.level`. `RAW_IOCTL_IOCTL` builds an `SMBioctl` packet with file number and request code. `RAW_IOCTL_NTIOCTL` builds an NT transaction setup array containing function, file number, fsctl flag, and filter, passes caller input data, and sets `max_data` from the request. SMB2 IOCTL levels return `NULL`. Receive dispatch mirrors send: legacy IOCTL pulls the entire reply data area into a blob, while NT IOCTL receives an NT transaction and steals the returned data blob into the caller's memory context.

State and persistence behavior: Local state is request-scoped only. Server-side effects depend on the IOCTL/FSCTL function: some are pure queries, while others can mutate filesystem/device state. Returned blobs are caller-context allocations for NT IOCTL and direct request-pulled blobs for legacy IOCTL.

Dependencies and integration points: It depends on raw request setup, `smb_raw_nttrans_send/recv`, and blob memory helpers. Higher-level filesystem control operations and tests call it for SMB1; SMB2 IOCTLs must use SMB2-specific implementations matching the SMB2 branches in `interfaces.h`.

Risks: IOCTL payloads are opaque, so this layer cannot validate function-specific input/output structure. Legacy receive does not check WCT before pulling data, relying on generic receive state and buffer info. `smb_raw_ioctl_recv` returns `NT_STATUS_INVALID_LEVEL` for SMB2 levels, but a sync caller that got `NULL` from send still reaches recv. Memory ownership differs between legacy and NT paths.

Test signals: IOCTL/FSCTL torture tests should validate legacy and NT paths, zero-length blobs, large output bounded by `max_data`, server errors, invalid levels, and memory ownership of returned blobs. FSCTL-specific tests should run through higher-level wrappers as well as this raw interface.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawlpq.c -->
# sources/user-network-fs/samba/source4/libcli/raw/rawlpq.c

Purpose: `rawlpq.c` is a placeholder for raw SMB print queue (`SMBsplretq`) support. It declares the send/recv/sync shape for `union smb_lpq` but does not implement packet encoding or parsing.

Important APIs, types, and functions: The file contains `smb_raw_lpq_send`, `smb_raw_lpq_recv`, and `smb_raw_lpq`. `smb_raw_lpq_send` always returns `NULL`; `smb_raw_lpq_recv` always returns `NT_STATUS_NOT_IMPLEMENTED`; the sync wrapper simply calls both.

Control flow: There is no real protocol flow. Any caller of the sync function receives `NT_STATUS_NOT_IMPLEMENTED`. A caller using send directly gets no request object.

State and persistence behavior: No local or server state is touched. The `union smb_lpq` output queue fields defined in `interfaces.h` are never populated by this implementation.

Dependencies and integration points: It includes the raw umbrella header and prototype header to fit the raw module build. Integration is limited to code that might probe or attempt print queue operations; Samba print queue functionality, if present elsewhere, does not use this file as a working raw implementation.

Risks: The API exists but is nonfunctional, so callers may assume print queue support based on declarations and only fail at runtime. Because send returns `NULL`, generic sync patterns that destroy a request would map to unsuccessful statuses, but this recv explicitly returns not implemented. No SMB2 equivalent is handled here.

Test signals: A minimal test should assert `smb_raw_lpq` returns `NT_STATUS_NOT_IMPLEMENTED` and does not dereference the `NULL` request. Any future implementation needs tests for queue entry parsing, maxcount/startidx behavior, user string conversion, and print server interoperability.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawlpq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawnegotiate.c -->
# sources/user-network-fs/samba/source4/libcli/raw/rawnegotiate.c

Purpose: `rawnegotiate.c` manages SMB1 raw client protocol negotiation and populates the raw transport's negotiated capability cache from the lower-level `smbXcli` connection.

Important APIs, types, and functions: Entry points are `smb_raw_negotiate_fill_transport`, `smb_raw_negotiate_send`, `smb_raw_negotiate_recv`, and `smb_raw_negotiate`. The async state is `smb_raw_negotiate_state`. The code delegates network negotiation to `smbXcli_negprot_send/recv` and reads results with `smbXcli_conn_protocol`, `smb1cli_conn_server_security_mode`, `smbXcli_conn_max_requests`, `smb1cli_conn_max_xmit`, capability/session key/security blob/challenge/time helpers, and braw/lockread capability helpers.

Control flow: The async send function clamps `maxprotocol` to `PROTOCOL_NT1`, normalizes `minprotocol`, creates a tevent request, starts `smbXcli_negprot_send`, and registers `smb_raw_negotiate_done`. The callback receives lower-level status, fills `transport->negotiate`, and completes the request. The sync wrapper polls the tevent request and returns the final NT status.

State and persistence behavior: This file mutates `transport->negotiate`: protocol, security mode, max mux/xmit, session key, capabilities, server time/zone, security blob/challenge, and raw read/write/lockread support bits. That state is then used by request encoders for Unicode selection, large reads/writes, timestamps, and authentication/session setup.

Dependencies and integration points: It depends on tevent, `smbXcli_base`, time conversion, and tevent NTSTATUS helpers. It is used during client connect paths (`cliconnect`, composite connect, transport setup) before session/tree operations are attempted.

Risks: `smb_raw_negotiate_fill_transport` assigns `smb1cli_conn_server_writebraw(c)` into `n->readbraw_supported` instead of `n->writebraw_supported`, leaving write-braw state unset and potentially overwriting read-braw capability. The function rejects protocols above NT1 because this raw layer is SMB1-oriented; SMB2 negotiation must use other paths. Security blob ownership is borrowed from the connection, so lifetime depends on `transport->conn`.

Test signals: Basic negotiate torture tests and connection setup tests should assert protocol clamping, extended-security blob vs challenge selection, timezone propagation, and braw/lockread flags. A targeted regression should verify `readbraw_supported` and `writebraw_supported` are filled independently.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawnegotiate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawnotify.c -->
# sources/user-network-fs/samba/source4/libcli/raw/rawnotify.c

Purpose: `rawnotify.c` implements SMB1 raw change notification through `NT_TRANSACT_NOTIFY_CHANGE` and provides a cancellation helper for pending requests.

Important APIs, types, and functions: The main functions are `smb_raw_changenotify_send`, `smb_raw_changenotify_recv`, and `smb_raw_ntcancel`. They operate on `union smb_notify`, `struct smb_nttrans`, `struct notify_changes`, `smbcli_blob_pull_string`, and tevent request cancellation.

Control flow: Send accepts only `RAW_NOTIFY_NTTRANS`, fills a four-word setup array with completion filter, file number, and recursive flag, sets `max_param` to the caller's buffer size, and sends an NT transaction. Receive gets NT transaction params, walks the returned notify records once to count entries while validating 4-byte `next` alignment, allocates the changes array, then walks again to extract action codes and Unicode names. `smb_raw_ntcancel` cancels the first lower-level subrequest if one exists.

State and persistence behavior: Change notify requests may remain pending on the server until a filesystem change, cancellation, or disconnect. Locally the returned changes array and names are allocated under `mem_ctx`. Cancellation mutates the tevent/request state but does not wait for a server response.

Dependencies and integration points: It depends on NT transaction helpers, raw string parsing, and tevent. Higher-level directory watch logic and torture notify tests use this path for SMB1. SMB2 notify has interface definitions but is not implemented in this file.

Risks: The counting loop validates alignment but only checks `nt.out.params.length - ofs > 12`; malformed lengths near boundaries can lead to zero changes or parse failures. In the second loop, `ofs += IVAL(...)` can leave `ofs` unchanged on a zero final record after the last iteration, which is fine only because the loop is count-bounded. Cancellation returning success when no subrequest exists may hide already-completed requests.

Test signals: Notify tests should cover recursive and nonrecursive watches, multiple returned changes, rename pairs, zero-change completions, malformed `next` offsets, cancellation of pending requests, and invalid level rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawnotify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawreadwrite.c -->
# sources/user-network-fs/samba/source4/libcli/raw/rawreadwrite.c

Purpose: `rawreadwrite.c` implements raw SMB1 file read and write operations across old commands, lock/read, readbraw, ReadX, write-unlock, write, write-close, WriteX, and spool write.

Important APIs, types, and functions: Public entry points are `smb_raw_read_send`, `smb_raw_read_recv`, `smb_raw_read`, `smb_raw_write_send`, `smb_raw_write_recv`, and `smb_raw_write`. They operate on `union smb_read`, `union smb_write`, raw request setup/send/receive helpers, `smbcli_raw_pull_data`, and negotiated capabilities such as `CAP_LARGE_FILES` and `CAP_LARGE_READX`.

Control flow: Read send switches by level, builds the appropriate SMB command and word count, encodes file number/count/offset/remaining fields, adds high offset words for large-file capable servers, and optionally sets `FLAGS2_READ_PERMIT_EXECUTE`. Read receive validates WCT, extracts byte counts and offsets, handles large ReadX replies that exceed 64 KiB under `CAP_LARGE_READX`, validates output size against requested min/max, and copies data into caller-provided buffers. Write send builds data blocks or direct WriteX payloads, copies caller data into the request, and sends. Write receive validates reply WCT and extracts written counts, including high bits for WriteX.

State and persistence behavior: Reads do not mutate remote file content, though lockread may combine lock semantics at the server. Writes mutate server-side file data and may update metadata. The file stores no state beyond request lifetime; all read data lands in caller-owned output buffers.

Dependencies and integration points: It depends on `rawrequest.c` for packet buffers and bounds checking, `rawdate.c` for write-close mtime encoding, and negotiate state for large offsets. Raw open chained read logic in `rawfile.c` mirrors the ReadX parser. Torture raw read/write suites and client file wrappers are primary consumers.

Risks: Callers must allocate output buffers large enough for requested read sizes. ReadBraw uses `MAX(parms->readx.in.mincnt, parms->readx.in.maxcnt)` while in the `readbraw` branch, relying on union layout compatibility; that is fragile. Large offset TODO notes that the code does not error when a 64-bit offset is requested without server support. SMB2 levels return `NULL` or internal error here.

Test signals: Raw read/write torture tests should cover all levels, zero-byte operations, large offsets with and without `CAP_LARGE_FILES`, `CAP_LARGE_READX` oversize replies, read-for-execute flags, short replies, write count high bits, write-close mtime, and invalid SMB2 level handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawreadwrite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawrequest.c -->
# sources/user-network-fs/samba/source4/libcli/raw/rawrequest.c

Purpose: `rawrequest.c` is the request buffer and wire helper core for the raw SMB1 client layer. It creates request packets, manages chained requests, sends/receives through the transport, grows packet buffers, appends strings/blobs/data, pulls strings/blobs safely, and converts NTTIME/GUID values.

Important APIs, types, and functions: Key functions include `smb_setup_bufinfo`, `smbcli_request_destroy`, `smbcli_request_setup_transport`, `smbcli_request_setup_session`, `smbcli_request_setup`, `smbcli_chained_request_setup`, `smbcli_chained_advance`, `smbcli_request_send`, `smbcli_request_receive`, `smbcli_request_simple_recv`, `smbcli_request_is_error`, append helpers (`smbcli_req_append_string`, `_string_len`, `_ascii4`, `_blob`, `_bytes`, `_var_block`), pull helpers (`smbcli_req_pull_ascii`, `smbcli_req_pull_string`, `smbcli_req_pull_blob`, `smbcli_raw_pull_data`, blob string variants), and `smbcli_pull/push_nttime` plus GUID helpers.

Control flow: Request setup allocates a talloc request, initializes SMB header fields, VWV/data pointers, flags, IDs, and buffer sizes. Append functions grow allocation/data sections and update BCC. Send delegates to transport; receive pumps the tevent loop until the request leaves `RECV`. Chained setup creates a secondary low-level subrequest and rebuilds the output buffer at the chained offset; chained advance receives the second reply and repopulates `req->in`. Pull helpers use `request_bufinfo` for bounds, Unicode alignment, negotiated string mode, and conversion.

State and persistence behavior: State is per-request: packet buffers, pointers into buffers, status, subrequests, flags2, session/tree/transport links, and async metadata. No durable filesystem state is stored. Talloc ownership is central; request destruction frees all child buffers unless `do_not_free` is set.

Dependencies and integration points: This file underpins nearly every raw SMB1 implementation. It depends on tevent, smbXcli low-level request functions, string conversion, NDR GUID routines, request buffer definitions, and transport helpers. Chained open/read, trans2, nttrans, metadata, search, and IOCTL code all rely on these helpers.

Risks: Buffer growth can reallocate and invalidate external local pointers; the code updates request-owned pointers but callers must not cache old ones. `smbcli_req_pull_ascii` returns converted byte size rather than consumed wire bytes, unlike some parser expectations. Bounds checks are careful about wraparound in `smbcli_req_data_oob`, but many higher-level parsers must still validate offsets before calling. Sync receive can loop indefinitely if transport state never advances except for tevent errors/timeouts.

Test signals: Broad raw torture coverage exercises this file indirectly. Focused tests should cover packet growth, Unicode alignment, ASCII/Unicode string pull/push, chained request setup/advance, malformed offsets, zero-length blobs, request destruction with `NULL` and `do_not_free`, GUID round-trips, and transport errors mapped into request status.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawrequest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawsearch.c -->
# sources/user-network-fs/samba/source4/libcli/raw/rawsearch.c

Purpose: `rawsearch.c` implements raw SMB directory enumeration for old search commands and trans2 findfirst/findnext/findclose. It parses many search data levels and streams entries to a caller callback.

Important APIs, types, and functions: Main entry points are `smb_raw_search_first`, `smb_raw_search_next`, and `smb_raw_search_close`. Shared parser `smb_raw_search_common` handles SMB/SMB2-style directory info records. Local helpers include old search first/next/close, trans2 first/next blob calls, `parse_trans2_search`, `smb_raw_search_backend`, and `smb_raw_t2search_backend`.

Control flow: Old search paths build `SMBsearch`, `SMBffirst`, or `SMBfunique` requests, append ASCII patterns and resume var blocks, then parse fixed 43-byte records. Trans2 paths build `TRANSACT2_FINDFIRST` or `TRANSACT2_FINDNEXT`, optionally encode EA name lists, receive parameter/data blobs synchronously, validate parameter sizes, store returned handle/count/end flags, then parse each data record until count, callback stop, parse error, or zero next offset. Close uses old `SMBfclose` or `SMBfindclose`.

State and persistence behavior: The file does not keep local persistent state; search continuation state is carried by server handles or old resume IDs in caller-provided unions. Server-side directory search handles are opened by findfirst and closed by findclose or exhaustion. Parsed names/EAs are allocated under the caller context and passed to callbacks.

Dependencies and integration points: It depends on raw trans2 helpers, EA name/list helpers, DOS/NT time helpers, raw string/blob parsing, and the callback type from `interfaces.h`. `libcli/clilist.c`, NTVFS CIFS passthrough, nbench, Unix extension tests, and raw search torture tests consume it.

Risks: Search parsing is offset-heavy and level-specific. Some legacy formats use 8-bit name lengths and optional resume keys; incorrect flags shift all fields. The callback may stop early without closing server handles, so callers must manage findclose when needed. SMB2 search level is rejected here even though common parsers support SMB2-like records. Malformed next offsets return invalid-parameter rather than partial results.

Test signals: `source4/torture/raw/search.c`, Unix info2 search tests, chkpath/listing tests, and nbench directory enumeration are key signals. Coverage should include every data level, EA-list search, resume-key flags, ASCII vs Unicode negotiation, callback early termination, malformed next offsets, old search resume IDs, and findclose behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawsearch.c -->

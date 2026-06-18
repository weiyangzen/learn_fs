# subset-b-009978 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/winspool.c -->
# sources/user-network-fs/samba/source4/torture/ndr/winspool.c

Purpose: This file is a narrow NDR regression suite for the generated `winspool` parser. It validates that a captured NDR64 `SyncRegisterForRemoteNotifications` input buffer decodes into the expected remote notification filter structure.

Important APIs, types, and functions: The fixture is `registerforremotenotifications_req_data`. `registerforremotenotifications_req_check()` inspects `struct winspool_SyncRegisterForRemoteNotifications`, `struct winspool_PrintNamedProperty`, and nested `struct spoolss_NotifyOption` values. `ndr_winspool_suite()` registers the test with `torture_suite_add_ndr_pull_fn_test_flags()` using `NDR_IN` and `LIBNDR_FLAG_NDR64`.

Control flow: The suite creates a `winspool` torture suite, feeds the static byte array into the generated pull function, then calls the checker. The checker asserts the notification filter exists, contains four named properties, and that the fourth property carries a two-entry `spoolss_NotifyOption`: one printer notify type with ten printer fields and one job notify type with sixteen job fields.

State and persistence behavior: There is no live server state and no persistence. The only state is the immutable capture vector and decoded transient talloc-backed NDR result.

Dependencies and integration points: The file integrates with Samba's NDR torture harness, generated `librpc/gen_ndr/ndr_winspool.h`, spoolss notify constants, and `torture/ndr/proto.h`. It is exposed through `ndr_winspool_suite()` for the broader NDR torture runner.

Risks: The fixture is intentionally brittle against IDL layout changes, NDR64 alignment changes, property union changes, and notify field enum renumbering. It only exercises one request shape and does not cover output unmarshalling or malformed input.

Test signals: A passing test proves the generated winspool NDR64 pull path maps named properties, property unions, string values, and nested spoolss notify options exactly as expected for this captured request. Failures point to NDR conformance, IDL, or enum mapping regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/winspool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/witness.c -->
# sources/user-network-fs/samba/source4/torture/ndr/witness.c

Purpose: This file is an NDR regression suite for the Witness protocol. It verifies captured input, output, pull-push round trips, and invalid-data handling for Witness interface list, registration, unregistration, and async notification structures.

Important APIs, types, and functions: Static fixtures cover `witness_GetInterfaceList`, `witness_Register`, `witness_UnRegister`, `witness_AsyncNotify`, and a malformed `witness_notifyResponse`. Checker functions validate `struct witness_interfaceList`, context handles, GUIDs, `struct witness_notifyResponse`, `witness_ResourceChange`, and `witness_IPaddrInfoList`. `ndr_witness_suite()` registers pull, pull-push, and invalid-data tests.

Control flow: The suite decodes the interface list output and asserts two interfaces named `NODE2` and `NODE1` with IPv4 addresses and flags. It then decodes Witness Register input and output, matching version, net name, IP address, client computer name, returned GUID context handle, and success status. UnRegister and AsyncNotify input fixtures validate context-handle decoding. AsyncNotify output fixtures validate resource-change and client-move message branches, including a fuzz case with zero addresses. The final invalid-data fixture expects `NDR_ERR_BAD_SWITCH`.

State and persistence behavior: No server state is mutated. The file uses captured byte streams and transient decoded structures only.

Dependencies and integration points: It depends on the generated Witness NDR bindings, Samba's NDR torture framework, GUID parsing, WERROR assertions, and protocol constants such as `WITNESS_NOTIFY_RESOURCE_CHANGE`, `WITNESS_NOTIFY_CLIENT_MOVE`, and `WITNESS_IPADDR_V4`.

Risks: The tests are exact binary compatibility checks, so alignment, union discriminator, conformant-array, string, GUID, IPv4, and IPv6 formatting changes can break them. The file also encodes selected fuzz expectations; parser hardening can regress if the bad-switch fixture starts being accepted.

Test signals: Passing results show that Witness NDR pull, selected pull-push reserialization, context handles, nested notify unions, IP address decoding, and invalid union-switch rejection remain stable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/witness.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ntp/ntp_signd.c -->
# sources/user-network-fs/samba/source4/torture/ntp/ntp_signd.c

Purpose: This file tests Samba's NTP signing daemon protocol over its Unix domain socket and cross-checks the daemon's signature output against Netlogon-derived machine-account credentials.

Important APIs, types, and functions: `struct signd_client_state` stores local/remote socket addresses, a `tstream_context`, send queue, request header/iovecs, reply blob, and status. `test_ntp_signd()` performs the full integration test. `torture_ntp_init()` registers an `ntp` suite with a machine workstation RPC test case against the Netlogon interface.

Control flow: The test obtains the machine workstation name and NT hash, runs `netr_ServerReqChallenge`, initializes Netlogon credential state with AES-capable flags, and authenticates with `netr_ServerAuthenticate3`. It builds an NDR `sign_request` for `SIGN_TO_CLIENT`, connects to `lpcfg_ntp_signd_socket_directory()/socket`, writes a 4-byte length plus NDR request through `tstream_writev_queue_send`, reads a PDU with `tstream_read_pdu_blob_send`, decodes `signed_reply`, and checks protocol version, packet id, success opcode, signed packet length, RID placement, and MD5 signature bytes.

State and persistence behavior: The test creates no files but requires a working machine account, Netlogon secure-channel state, and a live `ntp_signd` Unix socket. It allocates transient talloc memory and mutates the reply blob pointer to skip the length header.

Dependencies and integration points: It depends on tevent, tstream/tsocket, generated Netlogon and ntp_signd NDR, Samba credential helpers, `torture_suite_add_machine_workstation_rpc_iface_tcase()`, and GnuTLS MD5 hashing.

Risks: This is environment-sensitive: missing socket directory, disabled ntp_signd, machine-account setup failure, Netlogon negotiation changes, or crypto behavior changes can fail the test. The manual `reply.data += 4` adjustment is local pointer mutation that assumes the read PDU includes the length header.

Test signals: Success proves the daemon accepts the length-prefixed NDR request, locates the RID/key, signs the packet with the expected machine password hash algorithm, and returns a protocol-conformant reply.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ntp/ntp_signd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rap/printing.c -->
# sources/user-network-fs/samba/source4/torture/rap/printing.c

Purpose: This file builds the RAP printing torture sub-suite. It exercises raw SMB print job creation and RAP print queue, print job, and print destination calls across supported info levels.

Important APIs, types, and functions: `print_printjob()` creates a print job by opening `TORTURE_PRINT_FILE`, writing a small test page, and closing it. Test functions cover `rap_NetPrintQEnum`, `rap_NetPrintQGetInfo`, queue pause/resume, job pause/continue/delete, job enum/getinfo/setinfo, destination enum/getinfo, and the end-to-end `test_rap_print()`. `torture_rap_printing()` registers the `printing` suite.

Control flow: Queue enumeration loops over levels 0 through 5. Queue getinfo first checks that an empty queue name with a zero buffer returns `WERR_INVALID_PARAMETER`, then enumerates level 5 queues and queries each queue at levels 0 through 5. Job helpers enumerate queues, then enumerate or mutate jobs at levels 0 through 2. `test_rap_print()` pauses each queue, opens a second tree connection to that print share, submits a print job, enumerates jobs, validates getinfo, deletes each job, and resumes the queue.

State and persistence behavior: These tests intentionally mutate server print state: they create print jobs, pause/resume queues, set job comments, and delete jobs. Cleanup is mostly explicit via job deletion and queue resume, but interruption could leave queues paused or jobs present.

Dependencies and integration points: The file depends on SMB raw open/write/close APIs, RAP client calls, `torture_second_tcon()`, print share configuration, and `torture_suite_add_1smb_test()`. It is included by the broader RAP suite from `rap.c`.

Risks: It assumes a configured RAP-capable print environment and sufficient privileges to pause queues and delete jobs. Hard-coded job id `400` in `test_netprintjob()` may be server-dependent. Some tests assert transport success but do not always assert RAP status for every job operation.

Test signals: Passing tests show that RAP print queue discovery, per-level marshalling, job lifecycle operations, raw print submission, queue pause/resume, and print destination queries are interoperable with the target server.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rap/printing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rap/rap.c -->
# sources/user-network-fs/samba/source4/torture/rap/rap.c

Purpose: This is the main RAP torture registration file and the home of basic Remote Administration Protocol tests for shares, servers, sessions, remote time-of-day, and raw call scanning.

Important APIs, types, and functions: Basic tests use `rap_NetShareEnum`, `rap_NetServerEnum2`, `rap_WserverGetInfo`, `rap_NetSessionEnum`, `rap_NetSessionGetInfo`, and `rap_NetRemoteTOD`. `torture_rap_scan()` probes call numbers with `new_rap_cli_call()` and `rap_cli_do_call()`. `torture_rap_init()` builds the root `rap` suite and attaches RPC, printing, and SAM sub-suites.

Control flow: Share and server enum tests issue one RAP call and print returned records. Server getinfo checks levels 0 and 1 with success statuses. Session enum queries level 2 and asserts non-empty computer and user names for each record. Session getinfo first enumerates sessions, normalizes each session name to a UNC form if needed, and queries level 2. Remote TOD performs a single success check. The scanner iterates call numbers `0..0xfffe` and reports calls that return `NT_STATUS_INVALID_PARAMETER`, indicating probable RAP handlers.

State and persistence behavior: Basic tests are mostly read-only. They allocate transient RAP request/response structures and print information. `torture_rap_scan()` is exploratory and noisy but does not persist state.

Dependencies and integration points: It depends on `libcli/rap/rap.h`, SMB tree state, torture settings, and sub-suite constructors `torture_rap_rpc()`, `torture_rap_printing()`, and `torture_rap_sam()`. `torture_rap_init()` is the entry point registered with the Samba torture harness.

Risks: The tests assume RAP support and enough server state to return sessions. The server enum test assigns `servertype` twice, leaving only `0x80000000`, which is intentional or legacy but can surprise readers. The scan test is broad and may be slow or noisy.

Test signals: Success indicates basic RAP request marshalling, status handling, share/server/session enumeration, session detail lookup, and remote time query behavior remain functional.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rap/rap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rap/rpc.c -->
# sources/user-network-fs/samba/source4/torture/rap/rpc.c

Purpose: This file checks consistency between RAP server information and the equivalent SRVSVC DCERPC server information.

Important APIs, types, and functions: `test_rpc_netservergetinfo()` opens an SRVSVC RPC pipe, calls `dcerpc_srvsvc_NetSrvGetInfo_r()` at level 101, then compares that with RAP `smbcli_rap_netservergetinfo()` at levels 0 and 1. `torture_rap_rpc()` registers the `rpc` sub-suite.

Control flow: The test obtains a DCERPC binding handle for `ndr_table_srvsvc`, queries `srvsvc_NetSrvGetInfo`, then queries RAP level 0 and level 1. It truncates the RPC server name to the 16-byte RAP name field and compares RAP name, major/minor versions, server type, and comment with RPC output. The pipe is freed at the end.

State and persistence behavior: This is read-only and maintains only transient RPC/RAP response state.

Dependencies and integration points: It depends on RAP client helpers, SRVSVC generated client stubs, `torture_rpc_connection()`, and the same SMB connection used by RAP tests. It is attached to the RAP suite from `rap.c`.

Risks: The comparison depends on RAP's legacy 16-character name semantics and on both RAP and RPC being backed by the same server identity. Differences in comment normalization, server type flags, or unavailable SRVSVC/RAP endpoints can fail the test.

Test signals: Passing results show that legacy RAP server info remains aligned with modern SRVSVC server metadata for the tested levels.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rap/rpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rap/sam.c -->
# sources/user-network-fs/samba/source4/torture/rap/sam.c

Purpose: This file builds the RAP SAM torture sub-suite, covering user password changes, user information retrieval, user creation, and user deletion through legacy RAP calls.

Important APIs, types, and functions: `samr_rand_pass()` generates random passwords. Password tests use `rap_NetUserPasswordSet2` in clear and DES-hash modes, and `rap_NetOEMChangePassword` with RC4-encrypted password buffers. Other tests use `rap_NetUserGetInfo`, `rap_NetUserAdd`, and `rap_NetUserDelete`. `torture_rap_sam()` registers the sub-suite.

Control flow: Password tests create a temporary domain user with `torture_create_testuser_max_pwlen()`, run password-change calls, update the local password only when the RAP status is OK, and leave the domain. OEM password change builds old/new DES hashes, encodes the new password buffer, encrypts it with ARCFOUR keyed by the old hash, and computes the old-password-hash verifier. User getinfo creates a user, queries levels 0, 1, 2, 10, and 11, then removes the user. User add verifies duplicate add returns `WERR_NERR_USEREXISTS`, then deletes. User delete creates a user, deletes it, and verifies the second delete returns `WERR_NERR_USERNOTFOUND`.

State and persistence behavior: The tests mutate domain SAM state by creating, changing, and deleting `torture_rap_user`. Cleanup is explicit through `torture_leave_domain()` or RAP delete, but failures can leave the test user behind or changed.

Dependencies and integration points: The file depends on RAP client calls, Samba torture domain join helpers, random password generation, legacy auth helpers `E_deshash`, `E_old_pw_hash`, `encode_pw_buffer`, GnuTLS ARCFOUR, and domain/workgroup settings.

Risks: It requires privileges to create users and change passwords. It prints generated passwords to output, which is acceptable in torture logs but sensitive in general logs. Password length limits and legacy encryption behavior are fragile across server policy changes.

Test signals: Passing tests show RAP SAM operations, password encoding/encryption paths, duplicate/not-found error mapping, and multi-level user info marshalling operate correctly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/rap/sam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/acls.c -->
# sources/user-network-fs/samba/source4/torture/raw/acls.c

Purpose: This file is a comprehensive SMB1 raw security descriptor and ACL torture suite. It tests DACL set/query behavior, security descriptors supplied at create time, null and empty DACL semantics, creator-owner handling, generic access-bit mapping, owner default rights, ACL inheritance, and dynamic inheritance expectations.

Important APIs, types, and functions: Helpers `verify_sd()` and `verify_attrib()` query `RAW_FILEINFO_SEC_DESC`, `RAW_FILEINFO_STANDARD`, and compare returned descriptors/attributes. Major tests include `test_sd()`, `test_nttrans_create_ext()`, `test_nttrans_create_ext_owner()`, `test_nttrans_create_null_dacl()`, `test_creator_sid()`, `test_generic_bits()`, `test_owner_bits()`, `test_inheritance()`, `test_inheritance_flags()`, and `test_inheritance_dynamic()`. `torture_raw_acls()` registers the suite.

Control flow: The suite repeatedly creates files or directories under `\\testsd`, applies security descriptors through `RAW_SFILEINFO_SEC_DESC` or `RAW_OPEN_NTTRANS_CREATE`, queries descriptors back, and performs access checks by reopening with specific masks. Null DACL tests distinguish a present null DACL, which grants broad access, from an empty DACL, which denies data access. Creator-owner and generic-bit tests construct descriptors with `security_descriptor_dacl_create()` and verify server-side generic-to-specific mapping. Inheritance tests iterate many ACE flag combinations, create child files/directories, and compare inherited ACE trustees, flags, and masks. Dynamic inheritance intentionally expects inherited children not to gain new parent rights after parent ACL changes.

State and persistence behavior: Every test mutates ACLs and filesystem objects under `BASEDIR`. Most paths restore original security descriptors when captured and delete the tree on exit. Some failure paths attempt cleanup but can leave modified ACLs or blocked access if interrupted.

Dependencies and integration points: The file depends on raw SMB open/fileinfo/setfileinfo, security descriptor helpers, global well-known SIDs, LSA privilege checks via `torture_check_privilege()`, SMB2-parity expectations noted in comments, and target conditionals such as `TARGET_IS_WIN7()` and `torture_setting_bool("samba4")`.

Risks: Results vary with filesystem ACL implementation, privileges such as restore and take ownership, Windows version quirks, Samba ACL defaults, and inherited SYSTEM/group ACE behavior. The file includes a disabled `GETSET` test because it does not work against XP or Vista. Cleanup can be complicated when a test successfully denies later access.

Test signals: Passing tests provide strong evidence that SMB1 security descriptor storage, DACL present/null/empty semantics, create-time ACL and owner application, access-mask reporting, generic rights mapping, inheritance flags, creator-owner substitution, and server-specific compatibility behavior remain stable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/acls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/chkpath.c -->
# sources/user-network-fs/samba/source4/torture/raw/chkpath.c

Purpose: This file tests SMB1 `CHKPATH` behavior and compares it with pathinfo, findfirst, and open behavior for path normalization, invalid names, dot segments, bad characters, and DOS/NT status compatibility.

Important APIs, types, and functions: `single_search()` runs a one-result `RAW_SEARCH_TRANS2`. `test_path_ex()` issues `smb_raw_chkpath()` and `RAW_FILEINFO_NAME_INFO` pathinfo, compares expected statuses, and optionally checks normalized returned names. `test_chkpath()` covers many concrete path cases. `test_chkpath_names()` iterates ASCII bytes 0x01 through 0x7f in filenames. `torture_raw_chkpath()` sets up the test tree.

Control flow: The suite creates `\\rawchkpath`, nested `nt\\V S\\VB98`, and a file named `vb6.exe`. It checks existing and missing paths, hidden directory lookup, redundant slashes, parent references, invalid dot-only paths, attempts to traverse through files, wildcard components, root paths, and open/findfirst status parity for selected ambiguous paths. The name loop classifies control characters and reserved characters as invalid while allowing ordinary printable bytes.

State and persistence behavior: It creates and deletes only the `\\rawchkpath` tree and temporary files. No persistent state is intended after `smbcli_deltree()`.

Dependencies and integration points: The test depends on raw SMB `CHKPATH`, pathinfo, search, NT create, `torture_set_file_attribute()`, locale `isprint()`, and torture settings such as `samba4-ntvfs` for known name normalization differences.

Risks: Expected statuses allow both NT and DOS mapped variants, but filesystem and server path parser differences can still cause failures. Slash handling is conditional because Samba FS treats `/` like `\\` outside `samba4-ntvfs`.

Test signals: Passing tests show that path validation, canonical name reporting, reserved-character rejection, dot/parent handling, wildcard rejection, and error-code mapping match Samba's expected SMB1 behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/chkpath.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/close.c -->
# sources/user-network-fs/samba/source4/torture/raw/close.c

Purpose: This file performs focused SMB1 raw close, splclose, flush, and exit tests.

Important APIs, types, and functions: `torture_raw_close()` drives `smb_raw_close()`, `smb_raw_flush()`, `smb_raw_exit()`, `smb_raw_pathinfo()`, `create_complex_file()`, and cleanup helpers. Local macros `REOPEN` and `CHECK_STATUS` simplify repeated create/status checks.

Control flow: The test creates a file, closes it with an explicit future write time, verifies a second close returns invalid handle, then queries all-info to confirm only write time changed. It repeats close with write time zero and verifies the existing write time is preserved. It checks `RAW_CLOSE_SPLCLOSE` on a normal file, flush with a closed handle, flush-all, flush on an open handle, then calls `SMBexit` and verifies the handle is invalid.

State and persistence behavior: It creates `\\torture_close.txt`, mutates file timestamps, and unlinks the file during cleanup. `SMBexit` changes server-side PID/open-handle state for the session.

Dependencies and integration points: It depends on raw close/flush/pathinfo APIs, time conversion helpers, all-info dumping, and raw exit semantics. The function is registered through the broader raw suite via `torture/raw/proto.h`.

Risks: Timestamp precision and server time handling can cause false failures; `basetime` is rounded to an even second to reduce this. Cleanup calls `smbcli_close()` even when `fnum` may already be invalid, which is tolerated in this test style.

Test signals: Passing confirms close-time write timestamp handling, invalid-handle errors after close/exit, splclose error mapping, and flush/flush-all behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/close.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/composite.c -->
# sources/user-network-fs/samba/source4/torture/raw/composite.c

Purpose: This file tests Samba libcli composite SMB helpers under parallel asynchronous load: save/load file, fetch file through a fresh connection, append ACL, and query filesystem object ID.

Important APIs, types, and functions: `loadfile_complete()` increments a shared completion counter. Tests exercise `smb_composite_savefile`, `smb_composite_loadfile_send/recv`, `smb_composite_fetchfile_send/recv`, `smb_composite_appendacl_send/recv`, `smb_composite_appendacl`, and `smb_composite_fsinfo_send/recv`. `torture_raw_composite()` registers four 1-SMB tests.

Control flow: Loadfile saves random data and launches 50 parallel load operations, polling tevent until all callbacks fire, then verifies size and bytes. Fetchfile saves random data, builds a connection description from torture settings and command-line credentials, launches `torture_numops` fetches, and verifies returned data. Appendacl creates 50 empty files, records original ACLs, builds one test ACE, launches parallel append operations, and compares final DACLs with expected ACLs. Fsinfo launches parallel object-ID queries and prints returned GUIDs.

State and persistence behavior: It creates `\\composite`, random test files, and ACL changes, then calls `smb_raw_exit()` and deletes the tree for each test wrapper. It also uses current command-line credentials and share settings to make additional connections.

Dependencies and integration points: Dependencies include tevent, libcli composite APIs, raw SMB, security descriptor helpers, command-line credential access, resolver context, gensec settings, and `torture_numops`.

Risks: These tests are concurrency-sensitive. They assume callbacks always fire; if an async operation stalls the loop waits indefinitely. Fetch/fsinfo depend on host/share settings and credential validity. Appendacl assumes ACL support and stable ACE ordering.

Test signals: Passing shows composite helper APIs preserve data integrity and ACL semantics under parallel use and that async completion, connection setup, and object-ID query paths remain functional.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/composite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/context.c -->
# sources/user-network-fs/samba/source4/torture/raw/context.c

Purpose: This file tests SMB1 context isolation and lifetime behavior for sessions/VUIDs, tree connections/TIDs, process IDs/PIDs, and automatic handle closure.

Important APIs, types, and functions: It uses `smbcli_session_init()`, `smb_composite_sesssetup()`, `smb_composite_sesssetup_send/recv()`, `smbcli_tree_init()`, `smb_raw_tcon()`, `smb_tree_disconnect()`, `smb_raw_ulogoff()`, `smb_raw_exit()`, raw open/write/close, and torture settings. Tests are `test_session()`, `test_tree()`, `test_tree_ulogoff()`, `test_pid_exit_only_sees_open()`, `test_pid_2sess()`, and `test_pid_2tcon()`.

Control flow: Session testing creates secondary security contexts on one transport, validates VUID allocation/failure rules, tests anonymous/non-extended cases, opens a file with one VUID and verifies another VUID cannot use the handle, then logs off and confirms auto-close. It also creates 15 parallel session setups and logs each off. Tree testing creates a second TID, verifies bad device type handling, checks handle isolation by TID, and validates auto-close on tree disconnect. Tree-with-ulogoff demonstrates a TCON can survive a session logoff and be reused with another valid session before disconnect. PID tests show `SMBexit` only closes handles opened under the matching PID and matching VUID/TID scope.

State and persistence behavior: The tests create files under `\\rawcontext`, mutate client-side VUID/TID/PID fields deliberately, and rely on server-side logoff, tree disconnect, and exit to close handles. Cleanup deletes the base directory.

Dependencies and integration points: It depends on raw SMB1 stateful semantics, composite session setup, command-line credentials, GENSEC settings, SMB negotiation capabilities such as `CAP_EXTENDED_SECURITY`, and torture host/share/workgroup configuration.

Risks: These tests depend on subtle SMB1 compatibility behavior and mutate client objects directly. Extended-security and non-extended-security servers legitimately differ. A failure before restoring IDs or deleting the tree can affect the shared connection for following tests.

Test signals: Passing confirms VUID/TID/PID scoping, invalid-handle/error behavior, ulogoff/tdis/exit cleanup semantics, secondary session setup concurrency, and tree reuse semantics match expected SMB1 behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/eas.c -->
# sources/user-network-fs/samba/source4/torture/raw/eas.c

Purpose: This file tests SMB1 extended attribute behavior for setfileinfo EA updates, bad EA name validation, maximum EA size probing, and NTTRANS create with initial EAs.

Important APIs, types, and functions: `check_ea()` wraps `torture_check_ea()`. `test_eas()` drives `RAW_SFILEINFO_EA_SET`. `test_one_eamax()` binary-searches usable EA value length for one EA name. `test_max_eas()` probes aggregate EA capacity using torture options. `test_nttrans_create()` uses `RAW_OPEN_NTTRANS_CREATE` with `struct smb_ea_list`. Entrypoints are `torture_raw_eas()` and `torture_max_eas()`.

Control flow: `test_eas()` creates `ea.txt`, adds two EAs, modifies one, sets a null EA, deletes EAs by setting zero-length values, verifies bad names reject the entire batch, and iterates byte values in a generated EA name to distinguish invalid control/reserved characters from accepted characters. `test_max_eas()` reads options `maxeasize`, `maxeanames`, `maxeastart`, and `maxeadebug`, fills a deterministic blob, then probes per-name maximums and total accepted EA bytes. `test_nttrans_create()` creates a file with three initial EAs, verifies EAs are not applied when opening an existing file, and verifies bad initial EA names fail atomically without creating the file.

State and persistence behavior: It creates files under `\\testeas` and mutates EAs. `torture_raw_eas()` does not delete the tree at the end, while `torture_max_eas()` deletes it unless `maxeadebug` is set, intentionally preserving files for inspection.

Dependencies and integration points: It depends on raw open, setfileinfo, NTTRANS create, EA list structures, `torture_check_ea()`, data blobs, torture option parsing, and server filesystem EA support.

Risks: EA support and limits vary widely by backend filesystem and server configuration. The max-size probe can be expensive with high options. Bad-name behavior must be atomic; partial EA application would indicate a server bug and can pollute later checks.

Test signals: Passing shows EA add/modify/delete semantics, null values, name validation, atomic rejection, initial-create EA handling, and reported capacity behavior are consistent with expected SMB1 EA semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/eas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/ioctl.c -->
# sources/user-network-fs/samba/source4/torture/raw/ioctl.c

Purpose: This file tests selected SMB1 raw IOCTL and NTIOCTL/FSCTL behaviors, including unsupported requests, invalid handles, sparse-file marking, and batch oplock request behavior.

Important APIs, types, and functions: `test_ioctl()` uses `RAW_IOCTL_IOCTL` with request `0xffff`, `IOCTL_QUERY_JOB_INFO`, and a bad handle. `test_fsctl()` uses `RAW_IOCTL_NTIOCTL` for `FSCTL_FIND_FILES_BY_SID`, `FSCTL_SET_SPARSE`, and `FSCTL_REQUEST_BATCH_OPLOCK`. `torture_raw_ioctl()` sets up and tears down `\\rawioctl`.

Control flow: The suite creates `test.dat`, checks legacy IOCTL requests return DOS server error, and verifies a deliberately bad handle also returns the same legacy error. For FSCTLs, it passes random non-SID data to `FSCTL_FIND_FILES_BY_SID` and accepts invalid-parameter, not-implemented, or not-supported. It then marks the file sparse and requires success. It attempts a batch oplock upgrade and logs whether the server supports it. Finally it changes the fnum to a bad handle and requires `NT_STATUS_INVALID_HANDLE`.

State and persistence behavior: It creates and removes `\\rawioctl\\test.dat`. `FSCTL_SET_SPARSE` mutates file metadata before the directory is deleted. `SMBexit` is called before tree deletion.

Dependencies and integration points: The file depends on SMB raw IOCTL wrappers, SMB constants, FSCTL codes, random buffer generation, `create_complex_file()`, and directory setup/deletion helpers.

Risks: Some FSCTL results are intentionally tolerant, but sparse-file support is required by this test. Legacy IOCTL error mapping differs from NTIOCTL error mapping, so changing server error translation can break assertions.

Test signals: Passing shows unsupported IOCTL paths, invalid handle detection, sparse marking, optional batch oplock reporting, and FSCTL invalid-input behavior conform to expected SMB1 raw client semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/raw/ioctl.c -->

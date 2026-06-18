# Group Research: subset-b-009938

This report covers the requested Samba source files under `source4/libnet` and `source4/librpc`. Each section is bounded by reconciliation markers so it can be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/userman.c -->
# sources/user-network-fs/samba/source4/libnet/userman.c

## Purpose

`userman.c` implements composite asynchronous helpers for SAMR-backed user management in source4 libnet: create user, delete user, and modify user. It wraps generated SAMR client calls behind `libnet_rpc_useradd_*`, `libnet_rpc_userdel_*`, and `libnet_rpc_usermod_*` APIs, using Samba's `composite_context` and `tevent_req` callback style so callers can drive the operations either asynchronously or synchronously.

## Important APIs, Types, And Functions

The file defines three private state machines. `struct useradd_state` stores the binding handle, domain handle, `samr_CreateUser` request, output user handle, created RID, and optional monitor callback. `struct userdel_state` stores the SAMR lookup, open, and delete requests plus the handles required to delete a resolved account. `struct usermod_state` stores the lookup/open/query/set requests and a mutable copy of `struct usermod_change`.

Public entry points are `libnet_rpc_useradd_send/recv`, `libnet_rpc_useradd`, `libnet_rpc_userdel_send/recv`, `libnet_rpc_userdel`, `libnet_rpc_usermod_send/recv`, and `libnet_rpc_usermod`. The async send functions allocate a composite context, populate SAMR request structs, submit generated `dcerpc_samr_*_r_send()` calls, and install continuation callbacks. The sync functions are thin wrappers around send/recv.

The user modification core is `usermod_setfields()` and `usermod_change()`. `usermod_setfields()` maps bitmask flags from `userman.h` to SAMR user-info levels such as 7 for account name, 8 for full name, 13 for description, 2 for comment, 10 for home path/drive, 11 for logon script, 12 for profile path, 16 for account flags, and 17 for account expiry. `usermod_change()` decides whether a level can be set directly or must first be queried to preserve unrelated fields.

## Control Flow

User creation is a one-stage state machine. `libnet_rpc_useradd_send()` builds `samr_CreateUser`, sends it, and `continue_useradd_create()` receives transport status, checks `createuser.out.result`, copies the returned policy handle and RID, optionally emits `mon_SamrCreateUser`, then completes the composite context.

User deletion is a three-stage state machine. `libnet_rpc_userdel_send()` sends `samr_LookupNames` for one user name. `continue_userdel_name_found()` validates that returned RID/type counts match the requested count, emits `mon_SamrLookupName`, and sends `samr_OpenUser` with `SEC_FLAG_MAXIMUM_ALLOWED`. `continue_userdel_user_opened()` checks open status, emits `mon_SamrOpenUser`, and sends `samr_DeleteUser`. `continue_userdel_deleted()` checks the delete result, emits `mon_SamrDeleteUser`, and completes.

User modification follows lookup, open, and repeated query/set cycles. `continue_usermod_name_found()` resolves the name and opens the user. `continue_usermod_user_opened()` calls `usermod_change()`. If `usermod_setfields()` returns false for a partially populated level, `usermod_change()` sends `samr_QueryUserInfo`; `continue_usermod_user_queried()` copies the returned union, applies the pending field, and sends `samr_SetUserInfo`. `continue_usermod_user_changed()` clears completed flags, completes when no fields remain, or loops back into `usermod_change()`.

## State And Persistence Behavior

All state is transient and talloc-owned by the composite context. The file does not persist to local storage; persistent changes happen remotely through SAMR on the target account database. Output handles are copied back to caller-owned `io` structs in the recv functions. Monitor callback payloads point to stack-local or state-owned data for the duration of the callback only, so consumers must not retain those pointers.

## Dependencies And Integration Points

The implementation depends on `libcli/composite/composite.h`, `libnet/libnet.h`, generated SAMR RPC stubs from `librpc/gen_ndr/ndr_samr_c.h`, LSA strings, SAMR policy handles, and the monitor message types used elsewhere in libnet. It is compiled into the private `samba-net` library by `source4/libnet/wscript_build`.

## Risks

The send functions have uneven argument validation: useradd rejects null binding or io, while userdel/usermod assume valid `b`, `io`, `username`, and allocation success for some input structures. `usermod_setfields()` mutates `change.fields` with XOR, which works only if bits are known and set once; duplicated or unsupported fields can lead to `NT_STATUS_INVALID_PARAMETER`. Some `struct usermod_change` fields declared in the header are not implemented in `usermod_setfields()` even though constants exist or fields are present. Deletion and modification ask for maximum allowed access, increasing dependency on server ACL behavior. Query-before-set is essential for compound SAMR levels; missing coverage there can reset unrelated account attributes.

## Test Signals

Useful tests are SAMR integration tests that create a temporary domain user, modify each supported field individually and in combinations that share a SAMR info level, then delete the user. Negative tests should cover nonexistent users, lookup count mismatches from mocked RPC replies, denied open/delete/set permissions, invalid field masks, and transport failures from generated SAMR client calls. Monitor callback ordering can be validated for create, lookup/open/delete, and lookup/open/query/set flows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/userman.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/userman.h -->
# sources/user-network-fs/samba/source4/libnet/userman.h

## Purpose

`userman.h` declares the caller-facing IO structures and field masks consumed by `userman.c` for SAMR-backed user add, delete, and modify operations. It also defines monitor payload structures emitted by those operations.

## Important APIs And Types

`struct libnet_rpc_useradd` carries input `domain_handle` and `username`, with output `user_handle`. `struct libnet_rpc_userdel` has the same input and output shape. `struct libnet_rpc_usermod` carries input `domain_handle`, target `username`, and nested `struct usermod_change`.

The `USERMOD_FIELD_*` constants define a bitmask for requested changes. They include account name, full name, description, comment, home directory/drive, logon script, profile path, workstations, logon hours, account expiry, account flags, parameters, country code, and code page. The nested change struct provides strings, several time values, and account flags; not every declared mask has a corresponding value or implementation in `userman.c`.

Monitor payloads include `msg_rpc_create_user` with a RID and `msg_rpc_lookup_name` with RID array pointer and count. Other monitor structures referenced by `userman.c`, such as open-user messages, come from broader libnet headers.

## Control Flow And State

The header is passive. Its structures are filled by callers and copied into per-operation state in `userman.c`. The `fields` bitmask acts as the state cursor for modification: `userman.c` clears bits as fields are successfully mapped into SAMR info levels.

## Dependencies And Integration Points

The only direct include is `librpc/gen_ndr/misc.h` for `policy_handle` and related generated types. Consumers are the libnet RPC user-management functions built into `samba-net`.

## Risks

The header advertises more change masks than the implementation handles, which can surprise callers with `NT_STATUS_INVALID_PARAMETER`. Time fields such as password-change and logon timestamps are present in the struct but are not mapped in the observed `userman.c` code. Callers must keep `username` and string pointers valid until the send function has copied or consumed them.

## Test Signals

Compile-time tests should catch ABI-impacting layout changes. Runtime tests should assert that each documented flag either succeeds with a known SAMR level or returns a clear invalid-parameter error when unsupported.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/userman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/wscript_build -->
# sources/user-network-fs/samba/source4/libnet/wscript_build

## Purpose

This Waf build script defines source4 libnet build targets, including the private `samba-net` library, a join/vampire helper library exposed for Python embedding, and Python extension modules for `samba.net` and `samba.dckeytab`.

## Important Targets

`bld.SAMBA_LIBRARY('samba-net', ...)` compiles many libnet sources including `userman.c` and `groupman.c`, generates `libnet_proto.h`, and depends directly on `INIT_SAMR`. Its public dependencies include credentials, DCE/RPC, SAMR, LSA/SRVSVC/DRSUAPI NDR bindings, resolve/find-dc helpers, NETLOGON ping, schannel, auth, NDR, SMB password parsing, SAM sync, tsocket, and GnuTLS helpers.

`bld.SAMBA_LIBRARY(name, ...)` builds the private, Python-embedded `samba-net-join` library from join and vampire sources when Python builds are enabled. `python_net` builds `samba/net.so` from `py_net.c`, and `python_dckeytab` builds `samba/dckeytab.so` when AD DC support is enabled.

## Control Flow And State

The script is declarative Waf metadata. It derives embedded Python library names with `bld.pyembed_libname()` and uses configuration predicates such as `bld.PYTHON_BUILD_IS_ENABLED()` and `bld.CONFIG_SET('AD_DC_BUILD_IS_ENABLED')` to gate optional artifacts.

## Dependencies And Integration Points

The script is the integration point that pulls `userman.c` into `samba-net`. It also links Python modules to `pyrpc_util`, `pytalloc-util`, `pyldb-util`, provisioning, Kerberos, and database glue as needed.

## Risks

Dependency lists are dense; missing or duplicated dependency names can create build-order or link failures that only appear in selected feature configurations. Because `samba-net` is private, ABI exposure is lower, but Python modules depend on the private libraries being built with Python embedding support.

## Test Signals

Signals include successful Waf configure/build under Python-enabled and Python-disabled configurations, AD DC enabled and disabled builds, and import tests for `samba.net` and `samba.dckeytab` when enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libnet/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/dcerpc.pc.in -->
# sources/user-network-fs/samba/source4/librpc/dcerpc.pc.in

## Purpose

This pkg-config template describes the installed DCE/RPC client library for external or higher-level build consumers.

## Important Fields

It exposes `Name: dcerpc`, description `DCE/RPC client library`, version `@PACKAGE_VERSION@`, and dependencies `ndr samba-util`. Link flags add `@LIB_RPATH@`, `${libdir}`, `-ldcerpc`, and `-ldcerpc-binding`. Cflags add `${includedir}` and `-DHAVE_IMMEDIATE_STRUCTURES=1`.

## Control Flow And State

There is no runtime flow. Configure/build substitution fills prefix, exec prefix, libdir, includedir, version, and RPATH placeholders.

## Dependencies And Integration Points

Consumers that use pkg-config inherit the NDR and Samba utility dependencies and link against the core DCE/RPC client and binding libraries. The `HAVE_IMMEDIATE_STRUCTURES` define affects generated header expectations for immediate struct layout support.

## Risks

Incorrect library names or missing requirements break downstream builds. Public flag changes here are externally visible and should be treated as compatibility-impacting.

## Test Signals

After installation, `pkg-config --libs --cflags dcerpc` should emit usable flags, and a small program including DCE/RPC headers and linking against `dcerpc` should compile.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/dcerpc.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/dcerpc_samr.pc.in -->
# sources/user-network-fs/samba/source4/librpc/dcerpc_samr.pc.in

## Purpose

This pkg-config template describes the installed SAMR-specific DCE/RPC client library.

## Important Fields

It exposes `Name: dcerpc_samr`, description `DCE/RPC client library - SAMR`, version `@PACKAGE_VERSION@`, and requires `dcerpc ndr ndr_standard`. Link flags add `-ldcerpc-samr`; Cflags add the include directory and `HAVE_IMMEDIATE_STRUCTURES`.

## Control Flow And State

The file is build-time metadata only. Template variables are substituted during installation.

## Dependencies And Integration Points

It layers SAMR generated client support on top of the generic DCE/RPC pkg-config module. Code such as `userman.c` depends on SAMR generated stubs internally; external consumers use this file to link against the installed SAMR client library.

## Risks

Because it exposes generated SAMR APIs, dependency drift between `dcerpc-samr`, `ndr_standard`, and installed headers can break consumers. The pkg-config name uses an underscore while the library uses a hyphen, which is intentional but easy to confuse in tooling.

## Test Signals

Installation tests should run `pkg-config --exists dcerpc_samr` and compile a small SAMR client stub user including generated SAMR headers and linking with emitted flags.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/dcerpc_samr.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/idl/irpc.idl -->
# sources/user-network-fs/samba/source4/librpc/idl/irpc.idl

## Purpose

`irpc.idl` defines Samba's internal RPC interface used between source4 services. It models management and notification calls for messaging servers, NBT, KDC checks, SMB server state, Samba termination, directory replication, DNS update, and DNS server reload.

## Important APIs And Types

The interface has UUID `e770c620-0b06-4b5e-8d87-a26e20f28340`, version 1.0, and imports misc, security, NBT, netlogon, and server-id IDL types. Public structs include `irpc_header`, `irpc_name_record`, and `irpc_name_records`. `irpc_header` carries interface UUID, version, call number/id, flags, NTSTATUS, a subcontext-wrapped credential token, and padding.

Management calls include `irpc_uptime`, `nbtd_information`, `nbtd_getdcname`, `nbtd_proxy_wins_challenge`, `nbtd_proxy_wins_release_demand`, `kdc_check_generic_kerberos`, `smbsrv_information`, `samba_terminate`, `dreplsrv_refresh`, `drepl_takeFSMORole`, `drepl_trigger_repl_secret`, `dnsupdate_RODC`, and `dnssrv_reload_dns_zones`.

Key discriminated types include `nbtd_info_level` and `nbtd_info` for NBT statistics, `smbsrv_info_level` and `smbsrv_info` for session/tree-connect listings, and `drepl_role_master` for FSMO role transfers.

## Control Flow And State

IDL does not implement behavior, but it defines request/response wire layout used by generated NDR parsers, clients, servers, and Python bindings. Many calls are administrative messages that trigger state changes in long-running daemons: terminating Samba, refreshing replication caches, taking FSMO roles, triggering secret replication, and reloading DNS zones.

## Dependencies And Integration Points

Generated output is built with `--header --ndr-parser --client --python` by the IDL `wscript_build`, making this interface available to C and Python users. It integrates with Samba's messaging/IRPC subsystem, NBT server, KDC/netlogon stack, SMB server management, drepl service, DNS update task, and internal DNS server.

## Risks

Internal RPC calls often cross daemon boundaries and may have privileged effects. Schema changes affect generated C and Python bindings and must preserve discriminant/value relationships. `irpc_header` embeds security tokens, so parser correctness and credential lifetime matter. Some calls accept strings or DNS name arrays from other components; malformed payloads should be rejected by generated NDR bounds and server-side validation.

## Test Signals

IDL generation should succeed for header, NDR parser, client, and Python outputs. Runtime signals include IRPC tests for uptime, NBT stats, SMB session/tcon reporting, DNS reload, and negative tests for invalid switch levels, malformed name arrays, and unauthorized administrative calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/idl/irpc.idl -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/idl/ntp_signd.idl -->
# sources/user-network-fs/samba/source4/librpc/idl/ntp_signd.idl

## Purpose

`ntp_signd.idl` defines the internal NTP signing protocol structures used to request, produce, and verify signed NTP packets.

## Important APIs And Types

The interface UUID is `0da00951-5b6c-4488-9a89-750cac70920c`, version 1.0. `NTP_SIGND_PROTOCOL_VERSION_0` is the fixed protocol version. `ntp_signd_op` enumerates client/server sign and check operations plus success/failure replies. `sign_request` is a big-endian public struct with protocol version, operation, packet id, little-endian key id, and remaining packet data. `signed_reply` is a big-endian public struct with version, operation, packet id, and remaining signed packet data.

## Control Flow And State

The IDL only defines serialization. Operationally, a client sends a `sign_request` with a packet to sign or verify, and the responder returns `signed_reply` with success/failure semantics encoded in `op` and the signed packet payload.

## Dependencies And Integration Points

The generated NDR parser is built by the IDL Waf script. It relies on `DATA_BLOB` and NDR endian flags from Samba IDL support. It is used by NTP signing components that need byte-accurate packet preservation.

## Risks

The mixed endian annotations are security-sensitive: protocol fields are big-endian except `key_id`, which is explicitly little-endian. Any parser change can break interoperability or signature verification. `NDR_REMAINING` payloads require callers to enforce packet length expectations.

## Test Signals

Tests should round-trip known sign requests/replies, verify `key_id` endian behavior, and reject malformed or truncated remaining payloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/idl/ntp_signd.idl -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/idl/opendb.idl -->
# sources/user-network-fs/samba/source4/librpc/idl/opendb.idl

## Purpose

`opendb.idl` defines NDR-serializable records for Samba's open-file database, used by `ntvfs/common/opendb.c` to store open handles, sharing state, delete-on-close state, oplock state, and pending notifications.

## Important APIs And Types

The interface imports `server_id.idl`. `opendb_entry` records the owning server id, stream id, share access, access mask, opaque file handle and file descriptor pointers, per-entry delete-on-close, level-II oplock allowance, and oplock level. `opendb_pending` records a server id and notification pointer. Public `opendb_file` stores per-path state: delete-on-close, write timestamps, UTF-8 path, entry count and array, pending count and array.

## Control Flow And State

The file is schema only, but it models persistent/shared database state. The database can be loaded by multiple server processes to enforce share modes and track pending open operations. Counts drive variable-length arrays in generated parsers.

## Dependencies And Integration Points

Generated NDR code is consumed by open database code in the NTVFS layer. It depends on server-id serialization and Samba's representation of `NTTIME`, `utf8string`, pointer values, and boolean8 fields.

## Risks

Pointer fields are serialized as opaque identifiers and are process-context-sensitive; misuse across process boundaries can be unsafe unless the owning code treats them as tokens. Count/array consistency is critical. Incorrect delete-on-close or oplock state persistence can cause data-loss or sharing-mode regressions.

## Test Signals

Round-trip tests should serialize open files with multiple entries and pending records. Integration tests should exercise conflicting opens, delete-on-close on one handle versus per-file state, oplock state, and database reload after process handoff.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/idl/opendb.idl -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/idl/sasl_helpers.idl -->
# sources/user-network-fs/samba/source4/librpc/idl/sasl_helpers.idl

## Purpose

`sasl_helpers.idl` defines a packed, big-endian helper structure for saslauthd-style authentication requests.

## Important APIs And Types

The interface UUID is `7512b2f4-5f4f-11e4-bbe6-3c970e8d8226`, version 1.0. Public `saslauthdRequest` is flagged `NDR_NOALIGN | NDR_BIG_ENDIAN | NDR_PAHEX`. It contains length-prefixed UTF-8 authid, password, service, and realm fields. Lengths for authid, service, and realm are computed with `strlen_m()`, while password length is an explicit field followed by raw bytes.

## Control Flow And State

This IDL has no procedures; it is a serialization contract. Generated parsers pack and unpack request blobs for helper code that communicates with SASL authentication services.

## Dependencies And Integration Points

It is generated by the IDL Waf script with header and NDR parser output. It depends on Samba IDL charset and length annotations.

## Risks

Password is a raw byte array and not charset-converted. Length mismatches or embedded NUL expectations can break authentication. The no-align/big-endian/PAHEX combination implies strict wire compatibility requirements.

## Test Signals

Tests should compare generated blobs with known saslauthd request vectors, including non-ASCII UTF-8 identities, empty realm/service, and binary password bytes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/idl/sasl_helpers.idl -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/idl/winsif.idl -->
# sources/user-network-fs/samba/source4/librpc/idl/winsif.idl

## Purpose

`winsif.idl` defines the WINS Administration Interface RPC contract. It models record actions, status/config/statistics queries, replication triggers, scavenging, backup, database range operations, browser-name retrieval, flags, and worker-thread updates.

## Important APIs And Types

The interface UUID is `45f52c28-7f9f-101a-b52b-08002b2efabe`, version 1.0, imports NBT IDL, and uses the NBT helper header. Core types include `winsif_Address`, `winsif_Action`, `winsif_RecordType`, `winsif_NodeType`, `winsif_RecordState`, and `winsif_RecordAction`. `winsif_RecordAction` carries command, optional NBT name, name length, record type, address arrays, version, node type, owner, state, static flag, and expiry.

Status types include address/version maps, replication counters, statistics counters, timestamps, `winsif_Stat`, old fixed-size `winsif_Results`, and newer dynamic `winsif_ResultsNew`. RPC calls span function numbers 0x00 through 0x15, including `winsif_WinsRecordAction`, `winsif_WinsStatus`, `winsif_WinsTrigger`, `winsif_WinsDoStaticInit`, `winsif_WinsDoScavenging`, `winsif_WinsGetDbRecs`, `winsif_WinsTerm`, `winsif_WinsBackup`, `winsif_WinsDelDbRecs`, `winsif_WinsPullRange`, `winsif_WinsSetPriorityClass`, `winsif_WinsResetCounters`, `winsif_WinsWorkerThreadUpdate`, `winsif_WinsGetNameAndAdd`, browser-name calls, `winsif_WinsGetDbRecsByName`, `winsif_WinsStatusWHdl`, and `winsif_WinsDoScanvengingNew`.

## Control Flow And State

The file defines wire layout only. Operationally the calls mutate WINS database records, trigger replication, delete ranges, adjust service priority/threads/flags, run scavenging, and terminate or back up the service. Several calls use `[in,out,ref]` records or results, so server code can update caller-provided structures.

## Dependencies And Integration Points

It integrates with generated NDR code, NBT name types (`wrepl_nbt_name`), WINS replication structures, and WINS service/admin implementations. DOS and UTF16 charset annotations indicate compatibility with legacy Windows admin protocols.

## Risks

This interface exposes powerful administrative state changes. Counted arrays and optional name pointers must be validated carefully. The old `winsif_Results` uses a fixed 25-entry map, while `winsif_ResultsNew` is dynamic; server/client mismatch can truncate status. The function name `WinsDoScanvengingNew` appears misspelled but is part of the IDL contract and should not be casually renamed.

## Test Signals

IDL generation, NDR round trips for records/status results, and interoperability tests against known WINS admin clients are key. Runtime tests should cover insert/query/delete/release actions, static init path encoding, range retrieval, browser names, scavenging requests, and malformed counted arrays.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/idl/winsif.idl -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/idl/winsrepl.idl -->
# sources/user-network-fs/samba/source4/librpc/idl/winsrepl.idl

## Purpose

`winsrepl.idl` defines NDR descriptions for the WINS replication protocol on port 42, even though the protocol is not traditionally IDL/NDR encoded. It gives Samba generated parsers for replication PDUs.

## Important APIs And Types

The interface UUID is `915f5653-bac1-431c-97ee-9ffb34526921`. Public constant `WINS_REPLICATION_PORT` is 42. Types describe IP owner/address pairs, address lists, name types, name states, node types, bitmapped flags, owner/version ranges, replication tables, command discriminants, start/stop association messages, and wrapped packets.

`wrepl_wins_name` combines an NBT name, flags, computed group flag, version id, discriminated address data, and an unknown IPv4 field. `wrepl_replication_cmd` distinguishes table query/reply, send request/reply, update/update2, and inform/inform2. Public `wrepl_packet` is generated-size, big-endian, PAHEX flagged and includes opcode, association context, message type, switched message, and remaining padding. Public `wrepl_wrap` prefixes packet size.

## Control Flow And State

The schema models association startup, association stop, and replication message exchange. State is represented by association context, owner version ranges, command-specific tables or records, and padding retained from the wire.

## Dependencies And Integration Points

It imports `nbt.idl` and uses the NBT helper header. The generated NDR parser is used by WINS replication client/server code and by WINS admin IDL through shared name structures.

## Risks

Several fields encode observed protocol quirks, including opcode bits and nodiscriminant unions. Changing discriminants, endian flags, or computed group flag logic can break wire interoperability. `NDR_REMAINING` padding must be preserved where peers expect noncanonical bytes.

## Test Signals

Round-trip tests should use captured WINS replication packets for start association, table query/reply, send reply with unique/group/multihomed records, and stop association. Tests should verify big-endian wrapping, little-endian address-list substructure, and size calculation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/idl/winsrepl.idl -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/idl/wscript_build -->
# sources/user-network-fs/samba/source4/librpc/idl/wscript_build

## Purpose

This Waf script generates NDR parser/header/client/Python code from selected source4-specific IDL files.

## Important Targets

The first `SAMBA_PIDL_LIST('PIDL', ...)` handles `ntp_signd.idl`, `opendb.idl`, `sasl_helpers.idl`, `winsif.idl`, and `winsrepl.idl` with `--header --ndr-parser`, outputting to `../gen_ndr`. The second handles `irpc.idl` with `--header --ndr-parser --client --python`, also outputting to `../gen_ndr`.

## Control Flow And State

The script computes `topinclude` from the source tree and passes it as PIDL `--includedir`. It is declarative build metadata and has no runtime behavior.

## Dependencies And Integration Points

It is the build link between the IDL contracts in this folder and generated C/Python artifacts consumed by librpc, IRPC, WINS, NTP signing, SASL helper, and opendb code.

## Risks

Adding an IDL to the wrong PIDL list can omit required client or Python bindings. Incorrect include directory calculation breaks imports such as `nbt.idl` and `server_id.idl`.

## Test Signals

Build tests should ensure generated files appear under `source4/librpc/gen_ndr`, and Python import tests should cover IRPC bindings because only `irpc.idl` requests Python generation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/idl/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/ndr/py_auth.c -->
# sources/user-network-fs/samba/source4/librpc/ndr/py_auth.c

## Purpose

`py_auth.c` patches generated Python bindings for `auth_session_info` so Python code can get and set the associated Samba credentials object.

## Important APIs And Types

`PyType_AddGetSet()` injects `PyGetSetDef` descriptors into a type dictionary. `py_auth_session_get_credentials()` extracts `struct auth_session_info` from a pytalloc object and returns `session->credentials` as a Python `samba.credentials.Credentials` NDR-like object via `py_return_ndr_struct()`. `py_auth_session_set_credentials()` converts a Python credentials object with `PyCredentials_AsCliCredentials()` and stores a talloc reference under the session.

`PY_SESSION_INFO_PATCH` is defined as `py_auth_session_info_patch` so generated binding code can invoke the patch.

## Control Flow And State

When the generated module initializes, it calls the patch macro for the generated type. Accessing `.credentials` dynamically wraps or replaces the C pointer. Setting credentials changes in-memory session state only; it does not persist credentials externally.

## Dependencies And Integration Points

It depends on Python C API, pytalloc, auth session structures, credentials Python helpers, and `pyrpc_util`.

## Risks

The getter comment notes this is not a normal IDL structure. Lifetime correctness depends on talloc references and Python wrapper ownership. The setter does not reject null conversion explicitly in this file, so converter error behavior is important.

## Test Signals

Python tests should import the auth binding, read `.credentials`, assign a `samba.credentials.Credentials` instance, and verify reference lifetime after the original Python object is dropped.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/ndr/py_auth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/ndr/py_lsa.c -->
# sources/user-network-fs/samba/source4/librpc/ndr/py_lsa.c

## Purpose

`py_lsa.c` patches generated Python bindings for `lsa_String` to make construction, string conversion, and representation natural in Python.

## Important APIs And Types

`py_lsa_String_init()` accepts optional keyword `str` and talloc-duplicates it into `struct lsa_String.string`. `py_lsa_String_str()` returns the contained string or an empty string when null. `py_lsa_String_repr()` returns `lsaString(None)` for null or a quoted `lsaString('...')` representation. `PY_STRING_PATCH` aliases the patch function for generated module integration.

## Control Flow And State

The patch replaces type slots `tp_init`, `tp_str`, and `tp_repr` at module initialization. Instances store the copied C string in the pytalloc-managed `lsa_String` object.

## Dependencies And Integration Points

It depends on Python C API, pytalloc helpers, and generated `librpc/gen_ndr/lsa.h`. It improves usability of LSA-generated bindings used by many Samba Python tests and tools.

## Risks

`PyArg_ParseTupleAndKeywords(..., "|s")` accepts UTF-8 encoded Python strings through Python's C conversion rules; binary bytes with embedded NULs are not suitable. Representation uses `PyUnicode_FromFormat` with raw string content, so unusual characters rely on Python formatting behavior rather than escaping logic.

## Test Signals

Python tests should construct `lsa.String()`, `lsa.String("name")`, check `str()` and `repr()`, and ensure allocation failure paths propagate `MemoryError`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/ndr/py_lsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/ndr/py_misc.c -->
# sources/user-network-fs/samba/source4/librpc/ndr/py_misc.c

## Purpose

`py_misc.c` patches generated Python bindings for miscellaneous RPC types, primarily `GUID` and `policy_handle`, giving them constructors, comparison, string, and repr behavior.

## Important APIs And Types

`py_GUID_init()` accepts an optional string or bytes object and parses it with `GUID_from_data_blob()`. `py_GUID_str()` and `py_GUID_repr()` format via `GUID_buf_string()`. `py_GUID_richcmp()` delegates ordering/equality to `GUID_compare()`.

`py_policy_handle_init()` accepts optional UUID string and handle type. It parses the UUID with `GUID_from_string()` and writes `handle_type`. `py_policy_handle_str()` and `py_policy_handle_repr()` format handle type and UUID. Patch macros `PY_GUID_PATCH` and `PY_POLICY_HANDLE_PATCH` are consumed by generated binding code.

## Control Flow And State

Type patch functions replace slots during module initialization. Construction mutates the underlying pytalloc C object. Comparisons return `NotImplemented` when the other object is not the expected pytalloc type.

## Dependencies And Integration Points

It depends on Python C API, Samba py3 compatibility, generated `misc.h`, GUID utilities, NTSTATUS-to-Python error helpers, and pytalloc.

## Risks

GUID constructor accepts both bytes and strings; invalid byte lengths or formats must be rejected by `GUID_from_data_blob()`. Ordering semantics expose C `GUID_compare()` behavior to Python, so any change to that function changes Python sorting. `policy_handle` initialization allows default zero UUID/type if no arguments are passed.

## Test Signals

Python tests should construct GUIDs from canonical strings and bytes, compare equal and ordered GUIDs, reject invalid inputs with NTSTATUS-derived exceptions, and format policy handles predictably.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/ndr/py_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/ndr/py_security.c -->
# sources/user-network-fs/samba/source4/librpc/ndr/py_security.c

## Purpose

`py_security.c` patches generated Python bindings for security-related NDR types and the security module. It adds SID usability, security descriptor ACL mutation and SDDL conversion, token helper methods, module privilege helpers, random SID generation, and ACE comparison/SDDL conversion.

## Important APIs And Types

`PyType_AddMethods()` injects methods into generated type dictionaries. `dom_sid` additions include constructor from string, `str`, `repr`, rich comparison via `dom_sid_compare()`, and `.split()` returning domain SID plus RID.

`security_descriptor` additions include a custom `tp_new` using `security_descriptor_initialise(NULL)`, rich equality via `security_descriptor_equal()`, SACL/DACL add/delete helpers, ACE-specific delete helpers, class method `from_sddl()`, and instance method `as_sddl()`. `from_sddl()` supports keyword-only `allow_device_in_sddl` and raises module-specific `security.SDDLValueError` with parse details.

`security_token` additions include a custom constructor with optional `evaluate_claims`, SID membership checks, anonymous/system/admin/authenticated-users checks, privilege checks, and privilege mutation. Module methods include `random_sid`, `privilege_id`, and `privilege_name`. `security_ace` additions include equality and `as_sddl()`.

## Control Flow And State

Most functions are immediate Python method calls mutating in-memory C structures. Descriptor ACL insert/delete helpers call libcli security routines and raise Python errors on NTSTATUS failure. SDDL decode allocates under a temporary talloc context, steals the decoded descriptor to a stable context, and wraps it as a Python object. `py_mod_security_patch()` adds module functions and creates the `SDDLValueError` exception during module initialization.

## Dependencies And Integration Points

The file depends on Python C API, generated conditional ACE support, py3 compatibility, SDDL encode/decode, and libcli security primitives. It is a major integration layer for Samba Python code that manipulates ACLs, SIDs, tokens, privileges, and SDDL strings.

## Risks

Security descriptor mutation is access-control-sensitive; type checks and NTSTATUS propagation must remain strict. `from_sddl()` intentionally includes the original SDDL string in the exception tuple, which is useful for diagnostics but can expose sensitive ACL text to logs if callers print exceptions. `random_sid()` uses `generate_random()` to produce three RID authority components; it is for test/utility use, not a domain SID authority source. `as_sddl()` and ACE encoding require a domain SID argument in some paths and should reject wrong types.

## Test Signals

Python tests should cover SID parse/format/split/compare, descriptor creation, DACL/SACL add/delete by SID and ACE, SDDL round trips including invalid SDDL exception tuple fields, token SID/privilege helper methods, privilege name/id invalid values, random SID format, and ACE equality/SDDL encoding.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/ndr/py_security.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/ndr/py_xattr.c -->
# sources/user-network-fs/samba/source4/librpc/ndr/py_xattr.c

## Purpose

`py_xattr.c` patches generated Python bindings for `xattr_NTACL` with a debug dump method.

## Important APIs And Types

`PyType_AddMethods()` injects methods into a Python type. `ntacl_print_debug_helper()` implements an `ndr_print` callback that formats indented lines to stdout. `py_ntacl_print()` allocates an `ndr_print`, sets the print callback, and invokes `ndr_print_xattr_NTACL(pr, "file", ntacl)`. `PY_NTACL_PATCH` maps to `py_xattr_NTACL_patch`.

## Control Flow And State

Calling `.dump()` on a Python NTACL object prints the NDR representation to stdout and returns `None`. It allocates a temporary talloc context and frees it before returning. It does not mutate the ACL.

## Dependencies And Integration Points

It depends on Python C API, pytalloc, generated xattr NTACL NDR print functions, and Samba's NDR print infrastructure. It is primarily a diagnostic hook for Python tests/tools dealing with NT ACL xattrs.

## Risks

The method writes directly to stdout, which can pollute test output and is not structured logging. `vasprintf()` failures silently skip a line. Dumping ACLs may expose sensitive security descriptor information.

## Test Signals

Tests should call `.dump()` on a minimal and populated NTACL object, capture stdout, and verify no mutation or leaks occur on repeated calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/ndr/py_xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc.c -->
# sources/user-network-fs/samba/source4/librpc/rpc/dcerpc.c

## Purpose

`dcerpc.c` implements the core source4 DCE/RPC client runtime: pipe initialization, binding handles, NCACN bind/alter/auth3 packet handling, request queueing, fragmentation, signing/sealing hooks, response reassembly, timeout/error handling, NDR validation/debugging, and tstream transport IO.

## Important APIs, Types, And Functions

Private `struct rpc_request` tracks queued/pending/done state, pipe pointer, NTSTATUS, call id, payload, PDU flags, fault code, optional special receive handler for bind/alter, object UUID, opnum, request blob, timeout flags, verification-trailer state, and async callback.

`dcerpc_init()` initializes GENSEC. `dcerpc_pipe_init()` allocates a `dcerpc_pipe` and `dcecli_connection`, sets default fragment sizes and timeout, and enables debug printing at high debug levels. `dcerpc_pipe_binding_handle()` creates a generic `dcerpc_binding_handle` backed by `dcerpc_bh_ops`.

Binding-handle operations provide binding lookup, connected state, timeout setting, transport encryption/session key, auth info/session key, raw call send/recv, disconnect, endian/ref/NDR64 flags, debug printing, NDR push/pull failure logging, and optional NDR validation.

Protocol functions include `dcerpc_bind_send/recv`, `dcerpc_auth3()`, `dcerpc_alter_context_send/recv`, and synchronous `dcerpc_alter_context()`. IO functions include `dcerpc_request_send/recv`, `dcerpc_request_prepare_vt()`, `dcerpc_ship_next_request()`, `dcerpc_recv_data()`, `dcerpc_request_recv_data()`, `dcerpc_send_read()`, and `dcerpc_send_request()`.

## Control Flow

Normal RPC calls enter through the binding-handle raw call operation, which creates an `rpc_request` with a new call id and enqueues it. `dcerpc_schedule_io_trigger()` schedules a tevent immediate. `dcerpc_ship_next_request()` moves the first queued request to pending, builds one or more request PDUs respecting negotiated fragment sizes and auth trailer/signature overhead, writes them via the tstream write queue, and starts reads. If authenticated GENSEC does not support async replies, later requests wait for pending requests to drain.

Incoming transport blobs are parsed by `dcerpc_recv_data()` into NCACN packets and dispatched by `dcerpc_request_recv_data()`. Responses are matched by call id, authenticated before request lookup state is trusted, appended across fragments, size-checked against `max_total_response_size`, and completed on the last fragment. Fault packets map DCE/RPC fault codes to NTSTATUS, with severe protocol/security faults killing the connection.

Bind and alter-context requests are special pending `rpc_request` objects with custom receive handlers. `dcerpc_bind_send()` sends a bind with the requested abstract/transfer syntax and a second bind-time-features context. The bind reply handler validates packet type/flags, maps NAK/ACK reasons, negotiates fragment sizes, concurrent multiplexing, header signing, auth trailers, association group id, and binding abstract syntax. Alter-context follows a similar path with one context and fault handling.

## State And Persistence Behavior

All state is in-memory and talloc-owned by the pipe/connection/request. Persistent effects are remote: bind association state on the server and RPC operations sent through this client. `dcecli_connection` tracks call ids, negotiated fragment sizes, flags, security state, pending and queued requests, transport stream/queue/read state, server name, and negotiated bind-time features. Connection death marks the connection dead, shuts down the stream, and completes all queued/pending requests with the same error.

## Dependencies And Integration Points

The file integrates `tevent`, talloc, generated DCERPC NDR types, GENSEC, `dcerpc_pkt_auth`, DCE/RPC utility code, tsocket/tstream, SMB named-pipe tstream helpers, and public binding-handle APIs. Higher-level generated RPC clients use the binding handle created here.

## Risks

This is concurrency- and security-sensitive code. Request queueing must preserve call-id matching and avoid reentrant callbacks; the code defers callbacks for that reason. Fragment sizing must account for object UUIDs, auth trailers, signature sizes, and alignment. Auth verification trailers (`BITMASK1`, `PCONTEXT`, `HEADER2`) are appended for packet-level auth and must be synchronized with server verification state. Connection teardown during callbacks can interact with talloc destructors. Response size limits guard against unbounded reassembly but can reject legitimate large responses if configured too low.

## Test Signals

Key tests include unauthenticated bind and calls, authenticated bind with multi-step GENSEC and auth3, alter-context to another transfer syntax, fragmented request/response round trips, concurrent multiplexing behavior, timeout handling, unmatched call-id responses, fault mapping, NDR validation flags, big-endian/NDR64 modes, packet logging on pull failure, and transport close/error propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc.h -->
# sources/user-network-fs/samba/source4/librpc/rpc/dcerpc.h

## Purpose

`dcerpc.h` is the public source4 DCE/RPC client-side interface header. It defines the visible pipe, connection, and security structures while hiding internals unless `SOURCE4_LIBRPC_INTERNALS` is set, and declares connection, bind, auth, alter-context, endpoint mapping, and secondary-connection APIs.

## Important APIs And Types

`struct dcecli_security` stores auth type/level/context id, temporary auth trailer pointers, GENSEC state, session-key callback, and verification state. `struct dcecli_connection` stores call id, negotiated fragment sizes, flags, security state, event context, IO trigger, packet log dir, dead/free flags, transport stream/queue/read state, server name, pending and queued requests, context id allocation, response size limit, and bind-time features. `struct dcerpc_pipe` stores binding handle, context id, object UUID, abstract and transfer syntaxes, connection pointer, binding, last fault code, per-request timeout, connect-time timeout inhibition flags, and presentation-context verification.

Public functions include `dcerpc_pipe_connect*`, `dcerpc_pipe_init`, SMB open helpers, `dcerpc_bind_auth_none`, `dcerpc_pipe_connect_b*`, `dcerpc_pipe_auth`, `dcerpc_init`, secondary SMB/context/auth helpers, `dcerpc_alter_context`, `dcerpc_bind_auth`, and endpoint mapper helpers.

## Control Flow And State

The header defines the state that `dcerpc.c`, `dcerpc_auth.c`, `dcerpc_connect.c`, and transport-specific files mutate. Without `SOURCE4_LIBRPC_INTERNALS`, internals are wrapped in an `internal` struct to discourage direct external access.

## Dependencies And Integration Points

It includes `data_blob.h`, generated `dcerpc.h`, `libndr.h`, and common RPC definitions. It forward-declares tevent, tstream, credentials, resolve, SMB, ROH, TLS, and socket types to avoid broad public includes.

## Risks

The file explicitly notes that removing public functions or changing signatures requires a shared-library version update. Even fields intended as hidden internals can leak into source4 code compiled with `SOURCE4_LIBRPC_INTERNALS`. Timeout and security state fields are subtle and should be modified only with the owning implementation logic.

## Test Signals

ABI/API tests should compile consumers with and without `SOURCE4_LIBRPC_INTERNALS`, verify exported symbols and signatures, and exercise public connect/auth/bind/alter APIs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc.py -->
# sources/user-network-fs/samba/source4/librpc/rpc/dcerpc.py

## Purpose

`dcerpc.py` is a small Python compatibility/convenience module that re-exports everything from `samba.dcerpc.base`.

## Important APIs And Types

The only executable statement is `from samba.dcerpc.base import *`. Public names are therefore inherited from the base module rather than declared here.

## Control Flow And State

Importing this module imports the base DCE/RPC Python binding module and exposes its symbols in this module's namespace. It has no local state.

## Dependencies And Integration Points

It integrates Python callers expecting this source4 path/module with the generated or compiled `samba.dcerpc.base` binding.

## Risks

Wildcard re-export makes the module's API entirely dependent on `samba.dcerpc.base`. Static analysis cannot determine names from this file alone. Import failures in the base module surface as failures here.

## Test Signals

Python import tests should assert `import samba.dcerpc.rpc.dcerpc` or the package path used by Samba succeeds and that representative base symbols are present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_auth.c -->
# sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_auth.c

## Purpose

`dcerpc_auth.c` implements DCE/RPC bind authentication, both unauthenticated and GENSEC-authenticated. It initializes presentation/transfer syntaxes, creates binding handles, drives GENSEC token exchange through bind/alter/auth3 packets, and finalizes security state on the pipe.

## Important APIs And Functions

`dcerpc_init_syntaxes()` copies the binding object UUID, creates the pipe binding handle, chooses abstract syntax from the NDR table, and selects NDR64 or classic NDR transfer syntax based on connection flags.

Unauthenticated APIs are `dcerpc_bind_auth_none_send/recv` and `_PUBLIC_ dcerpc_bind_auth_none()`, which run `dcerpc_bind_send()` without auth credentials.

Authenticated APIs are `dcerpc_bind_auth_send/recv` and `_PUBLIC_ dcerpc_bind_auth()`. `struct bind_auth_state` stores the pipe, syntaxes, outgoing/incoming `dcerpc_auth` trailers, and whether GENSEC requires more processing. `bind_auth_next_step()`, `bind_auth_next_gensec_done()`, `bind_auth_recv_alter()`, `bind_auth_recv_bindreply()`, and `dcerpc_bind_auth_gensec_done()` implement the multi-step token exchange.

## Control Flow

For authenticated bind, the code starts a GENSEC client, sets credentials, target hostname, optional service, optional target principal from binding options, and starts the mechanism by auth type/level. It sets `auth_context_id` to 1 for compatibility, asks GENSEC for an initial token, and sends a DCE/RPC bind carrying that token. If GENSEC needs more processing, replies are pulled from bind/alter responses, fed back into `gensec_update_send()`, and additional alter-context packets carry subsequent tokens. If GENSEC completes but has a final token, `dcerpc_auth3()` sends it without expecting a reply.

Timeout processing is inhibited while nested `gensec_update()` work is active, so the outer connect timeout can record `timed_out` without destroying the stack mid-update.

## State And Persistence Behavior

State is transient and pipe-owned. Successful authenticated bind leaves `security_state` populated with auth type, level, context id, GENSEC state, and then resets the session-key callback to `dcecli_generic_session_key`. No local persistence occurs; remote association authentication state is established on the server.

## Dependencies And Integration Points

The file depends on GENSEC, credentials, loadparm GENSEC settings, DCE/RPC bind/alter/auth3 functions from `dcerpc.c`, and NDR interface tables generated by PIDL. `dcerpc_connect.c` calls this through `dcerpc_pipe_auth_send()`.

## Risks

GENSEC status handling is security-critical. The comments emphasize that `NT_STATUS_MORE_PROCESSING_REQUIRED` must be honored even if the peer appears to accept the bind, or mutual authentication can be bypassed. Header signing negotiation depends on both GENSEC features and bind ack support. Target service/principal selection affects Kerberos/SPNEGO correctness. Incorrect clearing of `tmp_auth_info` can cause stale credentials to be parsed or sent.

## Test Signals

Tests should cover no-auth bind, NTLM/Kerberos/SPNEGO binds at connect/integrity/privacy levels, schannel forcing `netlogon` service, target principal binding option, multi-step GENSEC alter-context flow, final auth3 token, header signing negotiation, GENSEC failure propagation, and timeout inhibition behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_auth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_connect.c -->
# sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_connect.c

## Purpose

`dcerpc_connect.c` implements high-level DCE/RPC pipe connection orchestration. It parses or accepts bindings, maps endpoints when needed, opens the selected transport, then authenticates/binds the pipe.

## Important APIs, Types, And Functions

`struct dcerpc_pipe_connect` is the transport-open parameter bundle, holding the connection, mutable binding, interface table, credentials, resolve context, NCALRPC directory, and optional existing SMB connection/session/tree data.

Transport-specific open paths include `dcerpc_pipe_connect_ncacn_np_smb_send/recv()` for SMB named pipes, `dcerpc_pipe_connect_ncacn_ip_tcp_send/recv()` for TCP, `dcerpc_pipe_connect_ncacn_http_send/recv()` for RPC over HTTP, `dcerpc_pipe_connect_ncacn_unix_stream_send/recv()` for Unix sockets, and `dcerpc_pipe_connect_ncalrpc_send/recv()` for local RPC.

Top-level public APIs are `dcerpc_pipe_connect_b_send/recv`, `_PUBLIC_ dcerpc_pipe_connect_b()`, `dcerpc_pipe_connect_send/recv`, and `_PUBLIC_ dcerpc_pipe_connect()`.

## Control Flow

`dcerpc_pipe_connect_send()` parses a string binding and delegates to `dcerpc_pipe_connect_b_send()`. The binding-based path allocates a pipe, duplicates the binding, installs a connect timeout, determines the transport, and if no endpoint is present uses endpoint mapper lookup with anonymous credentials for NP/TCP/local and supplied credentials for HTTP. After mapping, `continue_connect()` switches on transport.

For `NCACN_NP`, it negotiates an SMB connection, chooses SMB2 or SMB1 session/tree connect based on negotiated protocol, opens the named pipe endpoint over IPC$, and stores SMBX connection/session/tcon. Binding flags can force SMB1/SMB2 or allow anonymous fallback for schannel/password-change cases. For `NCACN_IP_TCP`, it opens a TCP pipe to the endpoint port and records local/remote addresses back into the binding. For `NCACN_HTTP`, it parses options such as `HttpUseTls`, `RpcProxy`, `HttpProxy`, `HttpConnectOption`, and `HttpAuthOption`, opens ROH, and installs the returned tstream and write queue on the connection. Unix stream and NCALRPC paths require endpoint paths/names and call local open helpers.

After any transport opens, `continue_pipe_connect()` duplicates the binding into the pipe and calls `dcerpc_pipe_auth_send()`. `continue_pipe_auth()` completes the top-level composite with the authenticated pipe.

## State And Persistence Behavior

All client state is in-memory. The code mutates the binding with resolved endpoint, localaddress/host, ncalrpc_dir, and association info. It initializes `packet_log_dir` for high debug levels. Remote state includes SMB sessions/tree connects, TCP/HTTP connections, local socket handles, endpoint mapper lookups, and authenticated DCE/RPC associations.

## Dependencies And Integration Points

The file integrates composite contexts, SMB1/SMB2 clients, SMBX base, DCE/RPC open helpers, credentials, loadparm, name resolution, HTTP/ROH, endpoint mapper utilities, and transport-specific pipe open code. It is the main entry point used by generated RPC clients and tools that start from binding strings.

## Risks

Binding option parsing is broad and user-facing. The HTTP local-proxy check uses string comparison semantics that must be read carefully; incorrect truth tests can unexpectedly enable proxy mode. Endpoint mapper credential choice affects privacy and authentication. SMB fallback to anonymous is intentional for selected flags but risky if applied too broadly. Connect timeout interacts with GENSEC nested updates through inhibition flags. Transport-specific options must be validated to avoid zero ports, null endpoints, or unsupported transports.

## Test Signals

Tests should cover binding parse errors, endpoint mapper fallback, explicit endpoints, SMB1/SMB2 forced and auto negotiation, existing SMB connection reuse, TCP address recording, HTTP/ROH option parsing and auth methods, Unix and NCALRPC endpoints, unsupported transports, connect timeout, and auth bind continuation after transport open.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_connect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_roh.c -->
# sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_roh.c

## Purpose

`dcerpc_roh.c` implements the client-side RPC-over-HTTP transport wrapper for DCE/RPC. It opens paired HTTP channels, performs the ROH/RTS connection sequence, and exposes the result as a `tstream_context` so the generic DCE/RPC engine can read and write NCACN packets without knowing about HTTP channels.

## Important APIs, Types, And Functions

`tstream_roh_ops` provides pending/readv/writev/disconnect operations. `struct tstream_roh_context` stores the `roh_connection`. `struct roh_open_connection_state` carries credentials, resolver output, DCE/RPC connection, TLS params, proxy/server addresses and ports, ROH state, loadparm, and HTTP auth method.

Public open functions are `dcerpc_pipe_open_roh_send()` and `dcerpc_pipe_open_roh_recv()`. Channel helpers include `roh_connect_channel_send/recv()`. The connection sequence uses helpers from companion files: `roh_send_RPC_DATA_IN`, `roh_send_RPC_DATA_OUT`, `roh_send_CONN_A1`, `roh_send_CONN_B1`, `roh_recv_out_channel_response`, `roh_recv_CONN_A3`, and `roh_recv_CONN_C2`.

The tstream adapter maps reads to the default out channel and writes to the default in channel. Disconnect tears down channel-in first, then channel-out.

## Control Flow

`dcerpc_pipe_open_roh_send()` initializes a version-2 ROH connection with random virtual connection and association group cookies, optional TLS parameters, proxy-use flags, and keepalive counters. It resolves the RPC proxy, opens an HTTP connection for the in channel, opens another for the out channel, sends the RPC_IN_DATA HTTP request, sends the RPC_OUT_DATA request, sends RTS CONN/A1 and CONN/B1 PDUs, waits for the out-channel HTTP response, receives CONN/A3, receives CONN/C2, marks the connection opened, and completes.

`dcerpc_pipe_open_roh_recv()` wraps the opened ROH connection in a tstream with `tstream_roh_ops` and returns the send queue from the default in channel's HTTP connection. The DCE/RPC core then uses normal tstream reads/writes.

## State And Persistence Behavior

State is in-memory and tied to the returned tstream. `roh_connection` stores protocol version, connection state, cookies, channel pointers, proxy-use and keepalive values. Each `roh_channel` tracks connection timeout, sent bytes, channel cookie, and HTTP connection. No local persistence occurs.

## Dependencies And Integration Points

The file integrates `tevent`, tsocket internals, TLS params, name resolution, credentials, loadparm, HTTP client helpers, DCE/RPC ROH structs, and generic DCE/RPC connection setup in `dcerpc_connect.c`.

## Risks

ROH setup is order-sensitive: the two HTTP channels and RTS PDUs must be sequenced exactly. The code currently resolves proxy names and uses the first address only; fallback to later addresses is not implemented in the observed flow. TODOs note virtual connection cookie table, proxy discovery, timers, and v1 fallback are incomplete. The returned stream depends on both channels remaining valid; partial disconnect or channel allocation failure must propagate `ENOTCONN`.

## Test Signals

Tests should mock HTTP connections to verify request order, TLS versus non-TLS paths, proxy option handling, failure at each handshake stage, read-from-out/write-to-in stream mapping, sent byte accounting, disconnect order, and behavior when channel pointers are null.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_roh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_roh.h -->
# sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_roh.h

## Purpose

`dcerpc_roh.h` defines the shared data structures, enums, and RTS command constants for Samba's RPC-over-HTTP implementation.

## Important APIs And Types

`struct roh_channel` stores connection timeout, sent byte count, channel cookie, and HTTP connection pointer. `enum roh_protocol_version` currently names `ROH_V1` and `ROH_V2`. `enum roh_connection_state` tracks open-start, out-channel wait, wait A3W, wait C2, and opened. `struct roh_connection` stores protocol version, connection state, virtual connection and association group cookies, default and non-default in/out channels, proxy-use flag, and keepalive counters.

The header also defines command type constants for RTS commands: receive-window size, flow-control ack, connection timeout, cookie, channel lifetime, client keepalive, version, empty, padding, negative/positive ANCE, client address, association group id, destination, and ping.

## Control Flow And State

The header is passive, but its state enum mirrors the connection sequence implemented in `dcerpc_roh.c`. Channel structs are updated by send/write and receive-handshake code.

## Dependencies And Integration Points

It includes generated `misc.h` for GUID and related types and forward-declares tevent queues, tstreams, and TLS params. It is included by ROH transport implementation and channel helper files.

## Risks

The state and command constants encode MS-RPCH semantics. Changing numeric constants or channel struct layout affects all ROH helpers. TODO comments in implementation mean some fields, especially non-default channels and keepalive timers, are not fully exercised.

## Test Signals

Compile tests should ensure all ROH helper files agree on the struct layout. Runtime tests should verify state transitions and command constants used in generated RTS PDUs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_roh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_roh_channel_in.c -->
# sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_roh_channel_in.c

## Purpose

`dcerpc_roh_channel_in.c` implements the inbound-channel pieces of the RPC-over-HTTP opening handshake: sending the long-lived `RPC_IN_DATA` HTTP request and sending RTS `CONN/B1` on that channel.

## Important APIs, Types, And Functions

`struct roh_request_state` stores HTTP request/response pointers for `RPC_IN_DATA`. `roh_send_RPC_DATA_IN_send/recv()` builds and sends the authenticated HTTP request. `struct roh_send_pdu_state` stores the serialized RTS PDU buffer, iovec, bytes-written result, and errno. `roh_send_CONN_B1_send/recv()` constructs and writes the RTS CONN/B1 packet.

## Control Flow

`roh_send_RPC_DATA_IN_send()` constructs URI `/rpc/rpcproxy.dll?<rpc_server>:<rpc_server_port>`, sets request type `HTTP_REQ_RPC_IN_DATA`, HTTP/1.0 version markers, zero body, large `Content-Length` of `1073741824`, and headers such as `Accept: application/rpc`, `User-Agent: MSRPC`, `Host`, keep-alive, no-cache, and pragma. It sends the request through `http_send_auth_request_send()` on `roh->default_channel_in->http_conn` using the selected HTTP auth method.

`roh_send_CONN_B1_send()` builds a DCERPC RTS packet with six commands: version, virtual connection cookie, in-channel cookie, channel lifetime/receive-window value, client keepalive, and association group id. It serializes `ncacn_packet` with little-endian DREP, type `DCERPC_PKT_RTS`, first/last flags, fixed frag length 104, and writes it via the HTTP connection tstream send queue for the default in channel.

## State And Persistence Behavior

The functions mutate only transient request state and write to the existing HTTP in-channel. `CONN/B1` reads cookies from `roh_connection` and channel state; it does not update connection state itself. The broader state transition is handled in `dcerpc_roh.c` after recv functions return success.

## Dependencies And Integration Points

The file depends on tevent, talloc, tsocket, TLS headers, credentials, generated DCERPC NDR types, DCE/RPC ROH structs, and HTTP helpers. It is called by `dcerpc_roh.c` during ROH open sequencing.

## Risks

The large fixed content length and HTTP/1.0/keep-alive behavior are protocol compatibility details; changing them can break RPC proxies. `CONN/B1` uses literal command type numbers rather than the named macros in the header, making accidental mismatch easier. The write completion treats `bytes_written <= 0 && errno != 0` as failure; short positive writes rely on tstream semantics to mean completion.

## Test Signals

Unit tests should inspect the generated HTTP request URI/headers/body, auth method propagation, serialized RTS command count and cookies, fixed fragment length, send queue selection, and error propagation from HTTP auth send and tstream write.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_roh_channel_in.c -->

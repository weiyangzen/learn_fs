# Research Report: subset-b-009614

Grouped research for Impacket DCERPC v5 bindings. Each section preserves the original source path and is bounded for deterministic splitting into per-file research reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/drsuapi.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/drsuapi.py

## Purpose

`drsuapi.py` implements Impacket's client-side NDR model and helper routines for the [MS-DRSR] Directory Replication Service Remote Protocol. It is a protocol binding module: it defines constants, NDR structures, unions, RPC request/response classes, opnum mappings, and convenience helpers for selected DRSUAPI operations. The high-value workflows are binding to the DRS interface, querying domain controller metadata, cracking directory names between formats, requesting replication changes, and decrypting replicated secret attribute payloads.

## Important APIs, Types, And Functions

The module exports `MSRPC_UUID_DRSUAPI` and `DCERPCSessionError`, which formats HRESULT and system errors in DRSR-specific text. It defines large groups of protocol constants for extended operations, DRS extension flags, replication option flags, LDAP connection properties, name cracking special formats, verification modes, and NT4 changelog modes.

The core type surface is the NDR representation of DRS protocol messages. `DRS_EXTENSIONS` and `DRS_EXTENSIONS_INT` describe bind-time capability exchange. `DRS_HANDLE` represents the server context handle. `DRS_MSG_DCINFOREQ`, `DRS_MSG_DCINFOREPLY`, `DS_DOMAIN_CONTROLLER_INFO_*W`, `DRS_MSG_CRACKREQ`, `DRS_MSG_CRACKREPLY`, `DS_NAME_FORMAT`, and `DS_NAME_RESULT*` cover domain controller info and name cracking. Replication state is modeled through `UPTODATE_CURSOR_*`, `UPTODATE_VECTOR_*`, `USN_VECTOR`, `DSNAME`, `PARTIAL_ATTR_VECTOR_V1_EXT`, `SCHEMA_PREFIX_TABLE`, `ATTR*`, `ENTINF`, metadata vectors, `REPLENTINFLIST`, `REPLVALINF_*`, and `DRS_MSG_GETCHGREQ/REPLY` variants.

RPC calls are represented by `DRSBind`, `DRSUnbind`, `DRSGetNCChanges`, `DRSVerifyNames`, `DRSGetNT4ChangeLog`, `DRSCrackNames`, and `DRSDomainControllerInfo`, with `OPNUMS` mapping opnums 0, 1, 3, 12, and 16. The file defines `DRSVerifyNames` and `DRSGetNT4ChangeLog` classes but does not include them in `OPNUMS`, which means generic dispatch via this table will not cover those opnums even though the structures exist.

Helper APIs include `hDRSUnbind`, `hDRSDomainControllerInfo`, `hDRSCrackNames`, `deriveKey`, `removeDESLayer`, `DecryptAttributeValue`, `MakeAttid`, and `OidFromAttid`. `checkNullString` is a small string terminator helper shared in style with other Impacket RPC modules.

## Control Flow

Most control flow is declarative NDR layout. Request helpers allocate an NDRCALL, populate version tags and union arms, then call `dce.request(request)`. `hDRSDomainControllerInfo` forces input version 1, selects `pmsgIn` union tag 1, null-terminates the domain string, and sends opnum 16. `hDRSCrackNames` similarly selects input version 1, fills code page and locale as zero, sets offered and desired formats, appends `LPWSTR` records for every requested name, and sends opnum 12.

Replication change parsing depends on versioned unions. `DRS_MSG_GETCHGREQ` selects request versions 4, 5, 7, 8, or 10 by tag. `DRS_MSG_GETCHGREPLY` selects reply versions 1, 2, 6, 7, or 9. `REPLENTINFLIST.fromString` mutates the `pNextEntInf` field into a typed `PREPLENTINFLIST` before delegating to `NDRSTRUCT.fromString`, which lets Impacket parse a recursive linked list despite NDR pointer limitations. `WCHAR_ARRAY` customizes assignment and retrieval to convert Python strings to UTF-16 code units and back.

The cryptographic helpers have procedural flow. `deriveKey` builds two DES keys from a RID in little-endian byte order and passes them through `transformKey`. `removeDESLayer` decrypts two eight-byte blocks with DES ECB. `DecryptAttributeValue` obtains the DCE session key, unwraps Kerberos `crypto.Key` objects when needed, parses an `ENCRYPTED_PAYLOAD`, derives an RC4 key from MD5(session key + salt), decrypts the payload after the salt, and returns the decrypted bytes after the leading checksum field. `MakeAttid` and `OidFromAttid` convert between LDAP OIDs and DRS `ATTRTYP` values using BER object identifier encoding and the schema prefix table.

## State And Persistence Behavior

The module does not persist local state to disk. Runtime state is carried in NDR instances, DCE context handles, prefix table lists supplied by callers, and server-side DRS handles. `MakeAttid` mutates the caller-provided `prefixTable` by appending a `PrefixTableEntry` when an OID prefix is not already present. `hDRSUnbind` explicitly releases the remote `DRS_HANDLE`; callers are responsible for invoking it after successful `DRSBind`.

Remote effects can be significant. `DRSGetNCChanges` reads replicated directory content and may include secret attributes depending on privileges and flags. `DRSVerifyNames`, `DRSGetNT4ChangeLog`, and domain info calls query remote directory state. The module itself has no durable cache or retry ledger.

## Dependencies And Integration Points

The file depends heavily on Impacket NDR primitives from `impacket.dcerpc.v5.ndr`, Windows type aliases from `dtypes.py`, `impacket.structure.Structure`, UUID helpers, `rpcrt.DCERPCException`, HRESULT/system error tables, Kerberos crypto key objects, `pyasn1` BER encoder/decoder, and `impacket.crypto.transformKey`. Optional `Cryptodome.Cipher.ARC4` and `DES` are required for decryption helpers. The helper functions integrate with any connected and bound `DCERPC_v5` object exposing `request()` and, for decryption, `get_session_key()`.

This module is used by tools that perform Active Directory replication style operations, name format translation, and DCSync-like secret extraction. It also anchors other modules by providing DRS-specific structures such as `DSNAME`, `ATTRTYP`, and schema prefix conversions.

## Risks And Edge Cases

The security blast radius is high: helpers can support extraction of replicated secrets when used with privileged credentials. `DecryptAttributeValue` assumes RC4-style encrypted payloads and leaves checksum validation commented out, so corrupted or tampered plaintext may not be detected locally. Crypto import failure only logs critical warnings; later calls to DES or ARC4 will fail at runtime if the optional dependency is missing.

Parsing risk is concentrated in complex NDR unions and linked lists. `REPLENTINFLIST` explicitly notes it is "cheating" with `pNextEntInf`, and `DRS_MSG_GETCHGREPLY_V6/V9` intentionally model `rgValues` as `DWORD` because the array parsing is unresolved. `VALUE_META_DATA_EXT_V3` repeats the field name `unused1` three times, which can obscure values or overwrite field access depending on `NDRSTRUCT` behavior. `OidFromAttid` mixes list entries and packed byte strings; malformed prefix tables can return `None` or trigger BER decode failures. `checkNullString` indexes `string[-1:]`, so callers must not pass empty strings unless they expect `'' + '\x00'` behavior to work.

## Test Signals

Useful tests should instantiate request helpers and verify union tags, version fields, null termination, and array counts before sending. Round-trip tests for `MakeAttid` and `OidFromAttid` should cover last OID components below 128, above 127, and above 16383. Crypto tests should validate `deriveKey`, `removeDESLayer`, and `DecryptAttributeValue` against known MS-DRSR samples, including Kerberos `crypto.Key` and raw session key paths. Parser tests should include captured DRS replies for V1, compressed V2/V7, V6/V9 object lists, malformed prefix tables, and absent optional pointers. Integration tests require a domain controller or mocked DCE object and should assert that `dce.request()` receives the correct `NDRCALL` class for each helper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/drsuapi.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/dssp.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/dssp.py

## Purpose

`dssp.py` implements Impacket's binding for [MS-DSSP], the Directory Services Setup Remote Protocol. Its focused purpose is to query a Windows machine's primary domain role, upgrade state, or operation state through the `DsRolerGetPrimaryDomainInformation` RPC method.

## Important APIs, Types, And Functions

The module exports `MSRPC_UUID_DSSP`, `DCERPCSessionError`, constants for domain info flags (`DSROLE_PRIMARY_DS_RUNNING`, `DSROLE_PRIMARY_DS_MIXED_MODE`, `DSROLE_PRIMARY_DS_READONLY`, `DSROLE_PRIMARY_DOMAIN_GUID_PRESENT`) and upgrade state (`DSROLE_UPGRADE_IN_PROGRESS`).

The type model centers on DSSP role information. `DSROLE_MACHINE_ROLE` enumerates standalone/member workstation, standalone/member server, backup domain controller, and primary domain controller. `DSROLER_PRIMARY_DOMAIN_INFO_BASIC` carries the machine role, flags, flat DNS/forest names, and domain GUID. `DSROLE_OPERATION_STATE` and `DSROLE_OPERATION_STATE_INFO` describe whether a directory service operation is idle, active, or needs reboot. `DSROLE_SERVER_STATE` and `DSROLE_UPGRADE_STATUS_INFO` represent upgrade status and previous server role. `DSROLE_PRIMARY_DOMAIN_INFO_LEVEL` selects which response form is requested. `DSROLER_PRIMARY_DOMAIN_INFORMATION` is the discriminated NDR union for the returned shape.

The only RPC call class is `DsRolerGetPrimaryDomainInformation` at opnum 0, with `DsRolerGetPrimaryDomainInformationResponse`. `OPNUMS` maps opnum 0 to those classes. `hDsRolerGetPrimaryDomainInformation(dce, infoLevel)` is the single helper.

## Control Flow

Control flow is minimal. The helper creates a request, assigns `InfoLevel`, and delegates to `dce.request()`. The NDR layer handles union selection based on the requested and returned `DSROLE_PRIMARY_DOMAIN_INFO_LEVEL`. Error formatting checks `system_errors.ERROR_MESSAGES` and prints DSSP-specific text.

## State And Persistence Behavior

There is no local persistence or mutable module state. All state is transient in request/response objects and in remote server configuration returned by the RPC endpoint. The call is read-oriented: it queries role and operation information and does not modify the remote machine.

## Dependencies And Integration Points

The module depends on `rpcrt.DCERPCException`, NDR classes, `UINT`, `LPWSTR`, `GUID` from `dtypes.py`, `system_errors`, the local compatibility `Enum`, and UUID conversion helpers. It integrates with a bound DCE connection to the DSSP interface. Consumers are typically enumeration or host profiling tools that need to determine whether a target is a domain controller or domain member.

## Risks And Edge Cases

The main risks are protocol coverage gaps and enum/union correctness. Only opnum 0 is implemented, so any DSSP operations beyond primary domain information are absent. Callers must pass a valid info level; invalid values may fail server-side or fail local union decoding. The union maps only the three documented levels. `DCERPCSessionError` only checks system errors, so non-system HRESULT-style failures may be reported as unknown.

## Test Signals

Unit tests should verify that each `DSROLE_PRIMARY_DOMAIN_INFO_LEVEL` selects the expected union arm and that the helper sends opnum 0 with the requested level. NDR serialization tests should cover null and non-null `LPWSTR` fields in `DSROLER_PRIMARY_DOMAIN_INFO_BASIC`. Integration tests can compare results against local Windows role APIs or known domain controller/member server fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/dssp.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/dtypes.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/dtypes.py

## Purpose

`dtypes.py` is a shared mini implementation of Windows [MS-DTYP] data types for Impacket's DCERPC v5 layer. It maps common Windows scalar, pointer, string, GUID, SID, ACL, and security descriptor shapes onto Impacket NDR primitives. Other RPC modules import this file to avoid redefining fundamental IDL types.

## Important APIs, Types, And Functions

The module defines aliases for basic scalar types such as `DWORD`, `BOOL`, `BYTE`, `CHAR`, `HRESULT`, `INT`, `LONG`, `LONGLONG`, `NTSTATUS`, `UINT`, `ULONG`, `USHORT`, `WORD`, `ACCESS_MASK`, and `SECURITY_INFORMATION`, plus pointer classes including `LPDWORD`, `PBOOL`, `LPBYTE`/`PBYTE`, `PCHAR`, `LPSTR`, `LPWSTR`, `PDOUBLE`, `PFLOAT`, `PHRESULT`, `PINT`, `LPLONG`, `PLONGLONG`, `PLONG64`, `PUINT`, `PULONG`, `PULONGLONG`, `PUSHORT`, `PWORD`, `PGUID`, `PFILETIME`, `PLARGE_INTEGER`, and `PSECURITY_INFORMATION`.

String handling is provided by `WIDESTR`, `STR`, `WSTR`, `LPSTR`, `LPWSTR`, `BSTR`, `LMSTR`, `LPCSTR`, `WCHAR`, and `PWCHAR`. `STR` and `WSTR` maintain NDR conformant string headers and override assignment, retrieval, dumping, and data length behavior. `RPC_UNICODE_STRING` wraps a counted Unicode string and updates `Length` and `MaximumLength` when assigned plain Python data.

Structured Windows types include `GUID`/`UUID`, `FILETIME`, `LUID`, `OBJECT_TYPE_LIST`, `SYSTEMTIME`, `ULARGE_INTEGER`, packet-format `SID`, NDR-format `RPC_SID`, `ACL`, and `SECURITY_DESCRIPTOR`. SID helpers `formatCanonical()` and `fromCanonical()` convert between binary fields and textual `S-...` strings. Access mask and security information constants are exported for use in security-sensitive RPC modules.

## Control Flow

Most behavior is type-level serialization logic. `STR.__setitem__` encodes non-binary values as UTF-8, resets `MaximumCount` and `ActualCount`, and invalidates cached data. `WSTR.__setitem__` encodes values as UTF-16LE and sets counts in 16-bit code units. Their `__getitem__` methods decode back to text, with `STR` falling back to raw bytes if UTF-8 decoding fails. `RPC_UNICODE_STRING.__setitem__` calculates byte lengths before delegating to `NDRSTRUCT`. `SID.fromCanonical` parses dash-separated SID text into revision, identifier authority, and packed little-endian subauthorities; `RPC_SID.fromCanonical` performs the same conversion into NDR array form. `RPC_SID.getData` refreshes `SubAuthorityCount` from the current array before serialization.

## State And Persistence Behavior

There is no disk persistence. State is held in NDR object fields and recalculated during serialization. Several setters intentionally set count fields to `None` or update length fields to force recomputation. SID conversion mutates the target instance. Because this module is imported by many RPC bindings, type behavior changes would have broad runtime effects across the DCERPC stack.

## Dependencies And Integration Points

The file depends on Impacket's NDR base classes and `impacket.structure.Structure`, plus Python `struct.pack/unpack` and `six.binary_type`. It is a core integration point for almost every file in `impacket.dcerpc.v5`, including the DRS, event log, endpoint mapper, certificate services, IP helper, and GKDI modules researched in this group. It also bridges raw packet structures (`SID`) and RPC NDR structures (`RPC_SID`) for callers that need either representation.

## Risks And Edge Cases

Encoding and length calculations are the main correctness risks. `WIDESTR.getDataLen` searches for `b'\x00\x00\x00'`, which is a heuristic for wide null termination and can be fragile with malformed data. `STR` and `WSTR` catch `UnicodeDecodeError` around encode paths where `UnicodeEncodeError` may be more likely in Python 3 edge cases. `SID.formatCanonical` only uses the last byte of `IdentifierAuthority`, which is sufficient for common authorities but not a full 48-bit authority conversion. `RPC_UNICODE_STRING` deliberately hides direct buffer length management; callers needing custom `MaximumLength` must modify nested fields manually. Security descriptor structures model pointers to owner, group, SACL, and DACL but do not validate self-relative versus absolute descriptor semantics.

## Test Signals

Tests should round-trip `STR`, `WSTR`, and `RPC_UNICODE_STRING` with ASCII, non-ASCII, embedded nulls, empty strings, and raw bytes. SID tests should cover canonical conversions for common SIDs and authorities larger than one byte to expose the simplified authority formatting. NDR tests should assert that pointer aliases serialize with expected referents and that `RPC_SID.getData` updates subauthority count. Cross-module integration tests should instantiate representative request structures from modules that import `dtypes.py` and verify stable byte encodings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/dtypes.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/enum.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/enum.py

## Purpose

`enum.py` provides a local Python enumeration implementation compatible with older Python versions and with Impacket's NDR enum classes. It mirrors the standard library `Enum`, `IntEnum`, and `unique` behavior closely enough for protocol modules to define symbolic values without depending on a newer runtime enum module.

## Important APIs, Types, And Functions

The public API is `Enum`, `IntEnum`, and `unique`, exported through `__all__`. Internal helpers include `_RouteClassAttributeToGetattr` for routing class-level `name` and `value` property access, `_is_descriptor`, `_is_dunder`, `_is_sunder`, and `_make_class_unpicklable`. `_EnumDict` tracks member definition order and rejects duplicate member names or reserved sunder names.

`EnumMeta` implements enum class creation, member lookup, iteration, containment, attribute protection, the functional API, mixin resolution, and Python-version-specific `__new__` discovery. The runtime `Enum` class is constructed from `temp_enum_dict`, with methods for value lookup, representation, string conversion, directory listing, formatting, comparison behavior, pickling arguments, hashing, and protected `name` and `value` properties. `IntEnum` is a simple `int, Enum` mixin. `unique` scans `__members__` for aliases and raises on duplicates.

## Control Flow

Class creation starts with `EnumMeta.__prepare__`, which returns `_EnumDict` so member names can be tracked in definition order. `EnumMeta.__new__` identifies the data mixin and first enum base, selects the correct `__new__`, extracts member definitions from the class dictionary, creates the enum class, instantiates members, handles aliases by comparing values, builds `_member_names_`, `_member_map_`, and `_value2member_map_`, adjusts ordering for old Python versions, and restores enum methods where mixin methods would otherwise leak through.

Runtime lookup uses `EnumMeta.__call__`: with only a value it delegates to `Enum.__new__` for by-value lookup; with `names` it creates a new enum class through `_create_`. `Enum.__new__` first unwraps same-class enum values, checks the hash map, falls back to linear search for unhashable values, and raises `ValueError` when no member matches. Attribute access for enum members is handled by `EnumMeta.__getattr__`; class assignment and deletion protect existing members.

## State And Persistence Behavior

Enum class state is stored in `_member_names_`, `_member_map_`, `_member_type_`, and `_value2member_map_`. This is in-memory class metadata only. Pickle support is intentionally disabled for some mixed-in enum classes when the mixin cannot support stable reconstruction. There is no external persistence.

## Dependencies And Integration Points

The module depends only on `sys`. It is imported by protocol modules such as `drsuapi.py` and `dssp.py`, where nested `enumItems(Enum)` classes provide symbolic names for NDR enum numeric values. The implementation must be stable because many NDR enum dumps and constructors rely on `Enum(value).name` behavior.

## Risks And Edge Cases

This is compatibility infrastructure, so subtle divergence from Python's standard `enum` can affect all protocol modules. `_create_` assumes `names` is non-empty when treating list/tuple input and references the loop variable `item` after the loop, which can fail for empty inputs. Duplicate values become aliases by design; callers needing uniqueness must opt into `unique`. For unhashable enum values, value lookup is linear. The file uses float parsing of Python version strings, which is coarse but adequate for the historical branches represented here. Some branches exist for Python versions older than current supported runtimes and are difficult to exercise.

## Test Signals

Tests should cover class syntax, functional API creation, aliases, `unique`, mixed-in `IntEnum`, by-name and by-value lookup, member iteration order, forbidden reassignment/deletion, `name` and `value` property behavior when enum members use those names, and pickling behavior for object and mixin enums. Protocol-level tests should instantiate representative NDR enums and verify that dump output resolves known values to names and unknown values remain numeric.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/enum.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/epm.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/epm.py

## Purpose

`epm.py` implements the DCE/RPC endpoint mapper binding for Impacket. It can query the remote portmapper on TCP 135, enumerate registered endpoints, map an interface UUID/version to a concrete string binding, and parse or print endpoint mapper tower data. It also carries large lookup dictionaries for known endpoint UUIDs and Microsoft protocol identifiers.

## Important APIs, Types, And Functions

The module exports `MSRPC_UUID_PORTMAP`, `DCERPCSessionError`, `KNOWN_UUIDS`, `KNOWN_PROTOCOLS`, endpoint lookup constants (`RPC_C_EP_*`, `RPC_C_VERS_*`, `RPC_NO_MORE_ELEMENTS`), and floor/protocol identifiers for tower parsing. `KNOWN_UUIDS` maps binary UUID/version encodings to service binaries, while `KNOWN_PROTOCOLS` maps string UUIDs to protocol descriptions.

Tower parsing uses `EPMFloor`, `EPMRPCInterface`, `EPMRPCDataRepresentation`, `EPMProtocolIdentifier`, `EPMPipeName`, `EPMHostName`, `EPMHostAddr`, `EPMPortAddr`, and `EPMTower`. RPC structures include `RPC_IF_ID`, `ept_lookup_handle_t`, `twr_t`, `twr_p_t`, `octet_string_t`, `prot_and_addr_t`, `protocol_tower_t`, `ept_entry_t`, `ept_entry_t_array`, and `twr_p_t_array`. RPC calls are `ept_lookup` at opnum 2 and `ept_map` at opnum 3, with response classes.

The primary helper functions are `hept_lookup(destHost, ...)`, `hept_map(destHost, remoteIf, dataRepresentation, protocol, dce=None)`, and `PrintStringBinding(floors)`.

## Control Flow

`hept_lookup` optionally creates its own TCP transport to `ncacn_ip_tcp:<host>[135]`, binds to `MSRPC_UUID_PORTMAP`, and loops issuing `ept_lookup` requests with `max_ents` 500. Each response entry is converted into a dictionary containing the object UUID, annotation bytes, and an `EPMTower` parsed from `tower_octet_string`. The loop continues using the returned context handle until `entry_handle.isNull()` returns true, then disconnects if it created the DCE object.

`hept_map` also optionally creates and binds a DCE connection. It constructs an endpoint mapper tower from the requested interface UUID/version, data representation UUID/version, connection-oriented RPC protocol floor, and transport-specific floors for named pipe, TCP, or HTTP. It sets specific referent IDs for Windows 2003 compatibility, sends `ept_map`, parses the first returned tower, and returns a string binding such as `ncacn_np:host[\pipe]`, `ncacn_ip_tcp:host[port]`, or `ncacn_http:host[port]`.

`EPMTower.fromString` parses the non-standard tower byte encoding by reading the floor count, then selecting parser classes from `EPMFloors` by floor index. `PrintStringBinding` walks floors after the interface/data representation/protocol prefix and builds a human-readable binding from protocol/address floor pairs.

## State And Persistence Behavior

The module has no file persistence. `KNOWN_UUIDS` and `KNOWN_PROTOCOLS` are static in-memory dictionaries. `hept_lookup` accumulates endpoint entries in a local list. `ept_lookup_handle_t` carries server-side enumeration state between calls; that context is returned by the endpoint mapper and becomes null when enumeration is complete. Network connections are opened and closed only when a DCE object is not supplied by the caller.

## Dependencies And Integration Points

Dependencies include `socket`, `struct.unpack`, `six.b`, Impacket UUID helpers, DCERPC transport factory, NDR classes, common dtypes, `Structure`, `rpcrt.DCERPCException`, and `LOG`. It is a foundational discovery module: other tools can use it to resolve dynamic endpoints before binding to protocols such as DRSR, EVEN6, GKDI, ICPR, or service control interfaces. It also integrates with Impacket's string binding and transport stack.

## Risks And Edge Cases

Endpoint mapper data comes from the network and tower parsing is manual. `EPMTower.fromString` indexes `EPMFloors` by floor count position; unexpected tower shapes beyond the six parser slots or uncommon protocols may parse as generic floors or fail. `hept_map` assumes at least one returned tower and indexes `resp['ITowers'][0]`. Unsupported protocols log an error and return `None`. Some constants appear misspelled (`RPC_C_EP_MATH_BY_OBJ`, `RPC_C_VERS_MARJOR_ONLY`) but preserve existing API names. `DCERPCSessionError.__init__` assumes a packet with `status` is present. `PrintStringBinding` uses `ord(floor['ProtocolData'])` in the unknown branch, which is fragile under Python 3 when `ProtocolData` is already a bytes object of length 1.

## Test Signals

Tests should parse known tower byte strings for named pipe, TCP, HTTP, local RPC, NetBIOS, and unknown protocol floors. `hept_map` tests can use a fake DCE object to assert tower construction, referent IDs, protocol-specific floors, and returned string bindings. `hept_lookup` tests should simulate multiple pages and a terminating null context handle. Error tests should cover unsupported protocols, empty `ITowers`, malformed tower data, and endpoint mapper status packets. Integration tests can compare `hept_lookup` output against a Windows host with known endpoints.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/epm.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/even.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/even.py

## Purpose

`even.py` implements the legacy [MS-EVEN] EventLog Remoting Protocol interface. It models RPC calls for opening event logs or backup logs, reading event records, clearing and backing up logs, registering event sources, reporting events, and querying record counts.

## Important APIs, Types, And Functions

The module exports `MSRPC_UUID_EVEN`, `DCERPCSessionError`, event type constants (`EVENTLOG_SUCCESS`, error, warning, information, audit success/failure), read flags (`EVENTLOG_SEQUENTIAL_READ`, `EVENTLOG_SEEK_READ`, `EVENTLOG_FORWARDS_READ`, `EVENTLOG_BACKWARDS_READ`), size limits (`MAX_STRINGS`, `MAX_SINGLE_EVENT`, `MAX_BATCH_BUFF`), and `EVENTLOG_HANDLE_W`.

Important structures include `IELF_HANDLE`, a 20-byte context handle; `EVENTLOGRECORD`, a packet `Structure` for raw event log records; `EVENTLOG_FULL_INFORMATION`; `RPC_CLIENT_ID`; and `RPC_STRING`. RPC call classes cover opnums 0, 1, 2, 4, 5, 7, 8, 9, 10, and 11: `ElfrClearELFW`, `ElfrBackupELFW`, `ElfrCloseEL`, `ElfrNumberOfRecords`, `ElfrOldestRecord`, `ElfrOpenELW`, `ElfrRegisterEventSourceW`, `ElfrOpenBELW`, `ElfrReadELW`, and `ElfrReportEventW`, each with response classes. `OPNUMS` maps these calls for the DCERPC runtime.

Helper functions are `hElfrOpenBELW`, `hElfrOpenELW`, `hElfrCloseEL`, `hElfrRegisterEventSourceW`, `hElfrReadELW`, `hElfrClearELFW`, `hElfrBackupELFW`, `hElfrNumberOfRecords`, and `hElfrOldestRecordNumber`.

## Control Flow

Helpers create request objects, set handles and parameters, then call `dce.request()`. Open helpers set `UNCServerName` to `NULL` and protocol major/minor versions to 1.1. Read helper defaults to seek plus forward reading from offset 0 and requests `MAX_BATCH_BUFF` bytes. Close and count helpers return the response directly.

`EVENTLOGRECORD` parsing is offset-driven. It declares fixed header fields, null-terminated source and computer names, padding, user SID bytes based on `UserSidLength`, string area, event data based on `DataLength`, trailing padding, and the repeated record length. `RPC_STRING.__setitem__` updates counted string lengths before NDR serialization.

## State And Persistence Behavior

Local state is transient, but remote state can be modified. `hElfrClearELFW` clears a remote event log and can optionally write a backup. `hElfrBackupELFW` writes a remote backup file. `hElfrReportEventW` can add events through a registered source. Open calls return server context handles that callers must close with `hElfrCloseEL`. The module does not track handle lifecycle automatically.

## Dependencies And Integration Points

The file depends on Impacket NDR primitives, `dtypes.py` strings and security types, `lsad.PRPC_UNICODE_STRING_ARRAY`, `Structure`, NT error tables, UUID helpers, and `rpcrt.DCERPCException`. It integrates with the `eventlog` named pipe/service endpoint through Impacket's DCERPC transport. Consumers are event log collection, remote administration, and testing tools.

## Risks And Edge Cases

Clear, backup, and report operations have side effects and can require privileges. Handle misuse is easy because helpers accept default empty handles and do not validate that a handle came from a successful open. `EVENTLOGRECORD` is a raw binary parser and can misparse malformed or truncated buffers if offsets and lengths are inconsistent. `RPC_STRING` length uses character count rather than encoded byte count for non-binary values, which is suitable for byte strings but should be checked for unusual text inputs. Errors are formatted from NT status only; other failure spaces may appear unknown.

## Test Signals

Unit tests should serialize each helper request and confirm opnums, version fields, defaults, and handle placement. `EVENTLOGRECORD` tests need captured raw records with and without user SIDs, multiple insertion strings, data payloads, and padding. Integration tests against Windows should open a known log, query count and oldest record, read forward and backward, and close the handle. Side-effect tests for clear, backup, and report should run only in isolated environments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/even.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/even6.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/even6.py

## Purpose

`even6.py` implements an initial binding for [MS-EVEN6], the newer Windows EventLog Remoting Protocol. It supports remote subscriptions, log queries, query iteration and seeking, clearing and exporting logs, opening log handles, closing handles, and listing event channels.

## Important APIs, Types, And Functions

The module exports `MSRPC_UUID_EVEN6`, `DCERPCSessionError`, `checkNullString`, subscription flags (`EvtSubscribeToFutureEvents`, `EvtSubscribeStartAtOldestRecord`, `EvtSubscribeStartAfterBookmark`, tolerance/strict/pull flags), path flags (`EvtQueryChannelName`, `EvtQueryFilePath`), export/query flags, and read direction flags.

Handle and array structures include `handle_t`, `CONTEXT_HANDLE_REMOTE_SUBSCRIPTION`, `CONTEXT_HANDLE_LOG_HANDLE`, `CONTEXT_HANDLE_LOG_QUERY`, `CONTEXT_HANDLE_OPERATION_CONTROL`, pointer wrappers, `EvtRpcQueryChannelInfo`, `RPC_INFO`, string/DWORD/byte array wrappers, `EVENT_DESCRIPTOR`, `BOOKMARK`, and `RESULT_SET`. RPC call classes cover opnums 0, 2, 4, 5, 6, 7, 11, 12, 13, 17, and 19: remote subscription registration and next, controllable operation registration, log query registration, clear/export, query next/seek, close, open log handle, and get channel list.

Helper functions include `hEvtRpcRegisterRemoteSubscription`, `hEvtRpcRemoteSubscriptionNext`, `hEvtRpcRegisterControllableOperation`, `hEvtRpcRegisterLogQuery`, `hEvtRpcClearLog`, `hEvtRpcExportLog`, `hEvtRpcQueryNext`, `hEvtRpcClose`, `hEvtRpcOpenLogHandle`, and `hEvtRpcGetChannelList`.

## Control Flow

Most helpers null-terminate string arguments, set flags and handles, submit the request via `dce.request()`, and return the response. `handle_t` initializes context handles to a null UUID and exposes `isNull()`. `hEvtRpcRegisterLogQuery` defaults the query to `*\x00`; other string helpers call `checkNullString`.

`hEvtRpcQueryNext` is the only helper with non-trivial flow. It prepares a query-next request, sets an initial `status` to `ERROR_MORE_DATA`, performs a request once before the loop, enters a `while status == ERROR_MORE_DATA` loop, and immediately performs another request. It catches `DCERPCException`, re-raises unless the string contains `ERROR_NO_MORE_ITEMS` or `ERROR_TIMEOUT`, then returns the packet. Because `status` is never updated inside the loop and the function returns during the first loop iteration, the loop functions more like a single retry path than a full drain loop.

## State And Persistence Behavior

The module has no local persistence. Remote state is represented by server context handles for subscriptions, log queries, operation controls, and log handles. Some operations have remote side effects: `hEvtRpcClearLog` clears logs, `hEvtRpcExportLog` writes exported logs to server-side paths, and subscriptions/queries allocate server resources until closed. The module does not automatically close handles or manage subscription lifetimes.

## Dependencies And Integration Points

Dependencies are `system_errors`, common dtypes (`WSTR`, `DWORD`, `LPWSTR`, `ULONG`, `LARGE_INTEGER`, `WORD`, `BYTE`, `UUID`), NDR classes, `rpcrt.DCERPCException`, and UUID helpers. This module integrates with the Windows Event Log service over the EVEN6 RPC interface and complements `even.py`, which models the older EventLog protocol. Endpoint discovery can be performed through `epm.py`.

## Risks And Edge Cases

The implementation is explicitly "initial" and has several correctness risks. `OPNUMS` maps opnum 17 to `(EvtRpcOpenLogHandle, EvtRpcOpenLogHandle)` instead of the response class, which can break generic response parsing. `hEvtRpcQueryNext` has questionable retry/error logic and may not handle `ERROR_MORE_DATA` as intended. Several structures omit commented fields (`RESULT_SET` bookmark and subquery data), so parsing may be incomplete for rich responses. `checkNullString` returns `NULL` unchanged but otherwise assumes the input supports slicing and concatenation with `'\x00'`; callers must avoid passing bytes or empty incompatible values. Clear/export operations have administrative side effects.

## Test Signals

Tests should verify all helper request fields, especially string null termination and handle placement. A regression test should catch the opnum 17 response mapping issue. Query tests should simulate normal responses, `ERROR_MORE_DATA`, `ERROR_NO_MORE_ITEMS`, and `ERROR_TIMEOUT` to document or repair `hEvtRpcQueryNext` behavior. Parser tests should use captured `EvtRpcQueryNext` and subscription buffers with multiple events. Integration tests should list channels, open a channel, register a query, fetch events, close the handle, and avoid clear/export except in isolated targets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/even6.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/gkdi.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/gkdi.py

## Purpose

`gkdi.py` implements Impacket's binding for [MS-GKDI], the Group Key Distribution Protocol. It defines structures for group key envelopes and key agreement parameters and provides an RPC helper for `GetKey`, which retrieves group key material for a target security descriptor and key indices.

## Important APIs, Types, And Functions

The module exports `MSRPC_UUID_GKDI`, `DCERPCSessionError`, binary `Structure` parsers for `KDFParameter`, `FFCDHParameter`, `FFCDHKey`, `ECDHKey`, and `GroupKeyEnvelope`, NDR byte array wrappers, `GkdiRpcGetKey`/`GkdiRpcGetKeyResponse`, `OPNUMS`, and `GkdiGetKey`.

`GroupKeyEnvelope` is the most important structure. It parses version, magic, flags, L0/L1/L2 indices, root key GUID, lengths for algorithm names and parameters, private/public key lengths, L1/L2 key lengths, domain and forest lengths, then variable-length KDF algorithm, KDF parameters, security algorithm, security parameters, domain, forest, L1 key, and L2 key fields. Its `dump()` method decodes several fields as UTF-16LE for diagnostics.

`GkdiRpcGetKey` is opnum 0 and sends target security descriptor bytes, optional root key GUID pointer, and L0/L1/L2 key IDs. The response returns output byte count, pointer to output bytes, and an `NTSTATUS`.

## Control Flow

`GkdiGetKey(dce, target_sd, l0=-1, l1=-1, l2=-1, root_key_id=NULL)` creates a `GkdiRpcGetKey` request, sets `cbTargetSD` to `len(target_sd)`, serializes `target_sd` with `target_sd.getData()`, assigns root key and indices, and calls `dce.request()`. Binary structure classes use `impacket.structure.Structure` length expressions to parse variable sections. Dump methods print decoded or raw fields and do not affect protocol flow.

## State And Persistence Behavior

There is no local persistence. The helper reads remote key material according to server-side GKDI state and caller authorization. Parsed envelopes hold key material in memory, including L1 and L2 keys and algorithm parameters. Callers must treat these objects as sensitive and avoid logging dumps in production.

## Dependencies And Integration Points

The module depends on NDR call/pointer/array primitives, common dtypes (`ULONG`, `PGUID`, `LONG`, `NTSTATUS`, `NULL`), `rpcrt.DCERPCException`, HRESULT error messages, `Structure`, and UUID conversion. It integrates with security descriptor types from elsewhere in Impacket because `GkdiGetKey` expects `target_sd` to expose `getData()`. It is relevant to tooling that works with group managed service account or DPAPI-NG style key retrieval workflows.

## Risks And Edge Cases

The most important risk is sensitive key exposure. `GroupKeyEnvelope.dump()` prints key material and domain/forest details, so it should not be used in untrusted logs. `GkdiGetKey` assumes `target_sd` implements both `len()` and `getData()` consistently; mismatches can produce invalid `cbTargetSD`. Structure parsers trust length fields from the remote blob, so malformed envelopes can cause parse errors or excessive memory use. Several fields are named `Unknown*`, signaling incomplete semantic coverage. Error formatting only uses HRESULT tables.

## Test Signals

Unit tests should serialize `GkdiRpcGetKey` for null and non-null root key IDs and verify target security descriptor length/data. Binary parser tests should use sample KDF, FFCDH, ECDH, and group key envelope blobs, including malformed length fields. Integration tests need a domain environment with GKDI support and should validate returned status and envelope parsing without printing key material. Security tests should verify that normal logging paths do not call `dump()` on sensitive structures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/gkdi.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/icpr.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/icpr.py

## Purpose

`icpr.py` implements the [MS-ICPR] ICertPassage Remote Protocol for submitting certificate requests to Microsoft Certificate Services. It wraps the `CertServerRequest` RPC call, prepares request and attribute blobs, interprets disposition codes, and returns the encoded issued certificate bytes when available.

## Important APIs, Types, And Functions

The module exports `MSRPC_UUID_ICPR`, extends Kerberos PKINIT error message mappings for codes 77-81 and 90-93, defines `DCERPCSessionError`, `CERTTRANSBLOB`, `CertServerRequest`, `CertServerRequestResponse`, `translate_error_code`, and `hCertServerRequest`.

`CERTTRANSBLOB` models a counted byte pointer with `cb` and `pb`. `CertServerRequest` is opnum 0 and sends flags, CA authority string, request ID, attributes blob, and certificate request blob. The response returns request ID, disposition, certificate blob, encoded certificate blob, and disposition message. `hCertServerRequest` accepts raw CSR bytes, a list of attribute strings, optional request ID, and CA name.

## Control Flow

At import time the module aliases Kerberos `constants.ERROR_MESSAGES` and adds PKINIT-specific codes if they are not already present. `DCERPCSessionError.__str__` masks error codes to unsigned 32-bit and delegates formatting to `translate_error_code`.

`hCertServerRequest` joins attributes with newline separators, null-terminates and UTF-16LE encodes them, builds `CERTTRANSBLOB` instances for attributes and CSR bytes, constructs a `CertServerRequest` with `dwFlags` 0, null-terminated authority, request ID, and blobs, then sends it through `dce.request()`. It interprets `pdwDisposition`: `3` logs success, `5` logs pending approval, other values are translated as HRESULTs or logged with the server disposition message when unknown. It always logs the request ID and returns the joined bytes from `pctbEncodedCert['pb']`.

## State And Persistence Behavior

The module mutates the process-global Kerberos error message dictionary once at import time. It has no file persistence. Remote state can change because certificate requests may be created, issued, or left pending on the CA. Returned certificates and disposition messages are held in memory. Logging may record request IDs and error details.

## Dependencies And Integration Points

Dependencies include `base64` (imported but not used in the viewed implementation), `typing.List`, Impacket HRESULT errors and logging, common dtypes, NDR classes, Netlogon-style `checkNullString`, `DCERPC_v5` typing, Kerberos constants, and UUID helpers. It integrates with AD CS tooling and any DCE connection bound to the ICPR interface. It also relates to PKINIT workflows because certificate request errors can map to Kerberos authentication constraints.

## Risks And Edge Cases

The helper has direct security implications: it can request certificates from AD CS and may be used in privilege escalation workflows if templates or CA permissions are weak. It does not raise on non-success dispositions; callers receive whatever `pctbEncodedCert` contains, which may be empty for pending or failed requests. Unknown error logging decodes the disposition message as UTF-16LE and can fail if the server returns malformed bytes. `base64` is unused. Global mutation of Kerberos error messages may surprise code expecting the original dictionary. There is a TODO for test cases.

## Test Signals

Unit tests should mock `dce.request()` and cover success disposition 3, pending disposition 5, known HRESULT errors, unknown errors with disposition messages, empty encoded certificate blobs, and malformed disposition message encodings. Serialization tests should verify UTF-16LE newline-separated attributes, CA null termination, CSR byte counts, and request ID propagation. Integration tests require an AD CS environment and should verify issued and pending template paths without logging sensitive CSR material.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/icpr.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/iphlp.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/iphlp.py

## Purpose

`iphlp.py` implements selected MSRPC calls exposed by `iphlpsvc.dll` for IPv6 transition technologies over IPv4 networks. It supports applying transition configuration-change notifications and creating or deleting IPv6-in-IPv4 tunnels.

## Important APIs, Types, And Functions

The module exports three interface UUIDs: `MSRPC_UUID_IPHLP_IP_TRANSITION`, `MSRPC_UUID_IPHLP_TEREDO`, and `MSRPC_UUID_IPHLP_TEREDO_CONSUMER`. It defines `DCERPCSessionError`, notification constants from `NOTIFICATION_ISATAP_CONFIGURATION_CHANGE` through `NOTIFICATION_DA_SITE_MGR_LOCAL_CONFIGURATION_CHANGE_EX`, `BYTE_ARRAY`, and four RPC operations.

RPC call classes are `IpTransitionProtocolApplyConfigChanges` opnum 0, `IpTransitionProtocolApplyConfigChangesEx` opnum 1, `IpTransitionCreatev6Inv4Tunnel` opnum 2, and `IpTransitionDeletev6Inv4Tunnel` opnum 3, each with response classes carrying an `ErrorCode`. `OPNUMS` maps all four. Helpers are `hIpTransitionProtocolApplyConfigChanges`, `hIpTransitionProtocolApplyConfigChangesEx`, `hIpTransitionCreatev6Inv4Tunnel`, and `hIpTransitionDeletev6Inv4Tunnel`.

## Control Flow

Notification helpers build request objects, assign notification number and optional data length/data, and call `dce.request()`. Tunnel creation converts local and remote IPv4 address strings with `socket.inet_aton`, null-terminates the interface name, sets the nested `InterfaceName.MaximumCount` to 256, and sends the request. Tunnel deletion converts a textual tunnel GUID to binary with `uuid.string_to_bin` and sends opnum 3. `checkNullString` returns Impacket `NULL` unchanged and appends a null terminator to other strings when missing.

## State And Persistence Behavior

The module has no local persistence. Remote operations can mutate network configuration: creating or deleting v6-over-v4 tunnels changes server IP helper state, and apply-config notifications can trigger service behavior. The Ex notification path notes that `NOTIFICATION_DA_SITE_MGR_LOCAL_CONFIGURATION_CHANGE_EX` requires no admin, which is important for threat modeling. The module does not track created tunnel GUIDs or rollback state.

## Dependencies And Integration Points

Dependencies include `socket.inet_aton`, Impacket `uuid`, HRESULT errors, UUID conversion, common dtypes (`BYTE`, `ULONG`, `WSTR`, `GUID`, `NULL`), NDR classes, and `rpcrt.DCERPCException`. It integrates with the IP Helper service RPC interfaces and with endpoint discovery through `epm.py`. It is likely consumed by network configuration, testing, or vulnerability research tooling.

## Risks And Edge Cases

The operations can change remote network configuration and may disrupt connectivity. Address conversion raises socket errors for invalid IPv4 strings before any RPC request is sent. `checkNullString` assumes string-like input and can misbehave for bytes. For tunnel creation, forcing `MaximumCount` to 256 is protocol-specific and may hide overly long interface names rather than validating them. Error formatting only uses HRESULT tables. The Teredo UUIDs are declared but no Teredo-specific calls are modeled in this file.

## Test Signals

Unit tests should mock DCE requests and verify opnums, notification fields, data lengths, IPv4 byte order from `inet_aton`, interface null termination, `MaximumCount` adjustment, and GUID conversion. Negative tests should cover invalid addresses, invalid GUIDs, empty interface names, and `NULL` string handling. Integration tests should run only on isolated Windows targets and verify tunnel creation/deletion cleanup and notification error codes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/iphlp.py -->

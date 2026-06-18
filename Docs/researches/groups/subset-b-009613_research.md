# subset-b-009613 Research

Grouped research for Impacket DCOM/WMI/DHCPM protocol binding files. Each source section is wrapped for reconciliation into its source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/dcom/wmi.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/dcom/wmi.py

## Purpose
`wmi.py` is Impacket's partial implementation of the Windows Management Instrumentation remote protocols, primarily `[MS-WMI]` and `[MS-WMIO]`, on top of the DCOM runtime in `dcomrt.py`. It has two major jobs: define the NDR call/response classes for WMI DCOM interfaces, and parse or marshal WMI's custom CIM object binary encoding so callers can treat remote WMI class and instance objects as Python objects with properties and callable methods.

## Important APIs, Types, and Functions
- `DCERPCSessionError` formats WMI HRESULT and `WBEMSTATUS` failures.
- `format_structure()` recursively formats mappings and iterables for readable debugging.
- WMIO/CIM binary parser types include `ENCODED_STRING`, `QUALIFIER`, `QUALIFIER_SET`, `PROPERTY_LOOKUP_TABLE`, `CLASS_PART`, `METHODS_PART`, `CLASS_AND_METHODS_PART`, `INSTANCE_TYPE`, `CLASS_TYPE`, `OBJECT_BLOCK`, `METHOD_SIGNATURE_BLOCK`, and `ENCODING_UNIT`.
- CIM constants and maps include `CIM_TYPE_ENUM`, `CIM_TYPES_REF`, `CIM_TYPE_TO_NAME`, `CIM_NUMBER_TYPES`, `DICTIONARY_REFERENCE`, `DICTIONARY_REFERENCE_TO_VALUE`, `CIM_ARRAY_FLAG`, and `Inherited`.
- WMI DCOM identifiers include `CLSID_WbemLevel1Login`, `CLSID_WbemBackupRestore`, `CLSID_WbemClassObject`, and IIDs for `IWbemLevel1Login`, `IWbemServices`, `IWbemClassObject`, `IEnumWbemClassObject`, `IWbemCallResult`, smart enum, and login helper interfaces.
- RPC call structures cover `IWbemLevel1Login`, `IWbemObjectSink`, the full `IWbemServices` management surface, `IEnumWbemClassObject`, `IWbemCallResult`, `IWbemFetchSmartEnum`, `IWbemWCOSmartEnum`, `IWbemLoginClientID`, `IWbemLoginHelper`, backup/restore, refresher, shutdown, and unsecured apartment methods.
- Public wrapper classes include `IWbemClassObject`, `IWbemServices`, `IEnumWbemClassObject`, `IWbemLevel1Login`, `IWbemCallResult`, `IWbemFetchSmartEnum`, `IWbemWCOSmartEnum`, `IWbemLoginClientID`, and `IWbemLoginHelper`.
- `checkNullString()` appends a NUL terminator for WMI string fields unless the value is the Impacket `NULL` sentinel.

## Control Flow
The module starts with custom binary structure declarations for WMIO object encoding. `ENCODING_UNIT` is the outer parser; it validates the signature and length, then delegates to `OBJECT_BLOCK`. `OBJECT_BLOCK` inspects object flags to decide whether to parse a decoration block, a CIM class (`CLASS_TYPE`), or an instance (`INSTANCE_TYPE`). Class parsing walks class headers, derivation lists, qualifier sets, property lookup tables, method descriptions, and heaps. Instance parsing reuses the embedded current class metadata, unpacks the null/default table, and then resolves each value from the instance heap or inline numeric data.

WMI object construction follows the DCOM object-reference path. `IWbemClassObject.__init__()` wraps an `INTERFACE`, parses its `OBJREF_CUSTOM` object data as an `ENCODING_UNIT`, and either creates Python attributes for instance properties or creates dynamic Python methods for class methods. `createProperties()` recursively wraps embedded object-valued properties and object arrays as nested `IWbemClassObject` instances. `createMethods()` builds callable closures that marshal `__PARAMETERS` instances, call `IWbemServices.ExecMethod()`, and return a parsed output object.

The high-level DCOM wrappers are thin request builders. For example, `IWbemLevel1Login.NTLMLogin()` sends `IWbemLevel1Login_NTLMLogin` and wraps `ppNamespace` as `IWbemServices`; `IWbemServices.ExecQuery()` sends a WQL `IWbemServices_ExecQuery` request and returns `IEnumWbemClassObject`; `IEnumWbemClassObject.Next()` sends `Next` and wraps each returned interface pointer as an `IWbemClassObject`; `IWbemServices.ExecMethod()` marshals optional input parameters and wraps `ppOutParams` as an `IWbemClassObject`.

## State and Persistence Behavior
The module maintains no local persistent storage. Runtime state lives in wrapper instances:
- `IWbemClassObject` stores the parsed `encodingUnit`, a reference to its owning `IWbemServices`, cached method metadata, pending class-name edits, and pending new attributes.
- Parsed object blocks cache `ctParent` and `ctCurrent` dictionaries after `parseObject()`.
- Dynamic WMI properties are written as normal Python attributes on `IWbemClassObject` instances.
- `marshalMe()` mutates or reconstructs object references to reflect edited instance values or class metadata before put or method calls.
Remote state changes happen through WMI operations such as `PutClass`, `PutInstance`, `DeleteClass`, `DeleteInstance`, `ExecMethod`, backup/restore, and refresher calls. Object lifetime, authentication, DCE connections, OID pinging, and IPID/OXID management are delegated to `dcomrt.py`.

## Dependencies and Integration Points
The file depends heavily on Impacket's `Structure` parser for WMIO blobs, NDR primitives and pointers from `impacket.dcerpc.v5.ndr`, DCOM base classes and object-reference structures from `impacket.dcerpc.v5.dcomrt`, Automation `BSTR` from `dcom.oaut`, DCE/RPC error handling, Impacket UUID helpers, `hresult_errors`, and the global Impacket logger. It is intended to be used after a DCOM activation of `CLSID_WbemLevel1Login`, followed by `IWbemLevel1Login.NTLMLogin()` to obtain an `IWbemServices` namespace proxy. Higher-level tools can then query, enumerate instances, spawn class instances, put classes or instances, and execute WMI methods.

## Risks and Edge Cases
- WMIO parsing is offset- and heap-sensitive. A malformed heap reference, length, or null/default table can produce wrong values, parser exceptions, or misleading object metadata.
- Several branches are marked as incomplete, especially propagated method origins, instance property qualifier arrays, object/array marshaling details, and some async/refresher wrappers.
- `CIM_TYPE_ENUM.CIM_ARRAY_BOOLEAN` is assigned the same numeric value as `CIM_ARRAY_UINT64`, which can confuse type-name and pack/unpack expectations.
- `marshalMe()` contains a direct `print()` for instance property values, which can leak data or pollute CLI output.
- Numerous wrapper methods call `resp.dump()`, producing unsolicited debug output in normal use.
- Some methods create wrappers from likely wrong response fields. `IWbemServices.GetObject()` builds `ppcallResult` from `ppObject` data instead of `ppCallResult` when the call-result pointer is present.
- String handling mixes Python `str`, bytes, ASCII encoded strings, and UTF-16 encoded strings. Non-ASCII WMI values and binary strings need coverage.
- `__getattr__()` dynamically turns instance methods into attributes by loading class method definitions and constructing object paths from the first key property; classes with composite keys or key values requiring WMI escaping are fragile.
- Many async and less-common interfaces return raw responses or dumps rather than fully wrapped objects.
- Empty strings are specially marshaled as null/inherited-default in some paths to satisfy known WMI persistence behavior, but that behavior may not match all providers.

## Test Signals
Useful tests should include:
- Golden binary WMIO fixtures for class, instance, decoration, qualifier, method signature, object-valued property, object-array property, and array-valued property parsing.
- Round-trip tests for `IWbemClassObject.SpawnInstance()` and `marshalMe()` with numeric, boolean, string, empty string, null, object, and array values.
- Unit tests for `ENCODED_STRING` ASCII and UTF-16 parsing, `QUALIFIER_SET.getQualifiers()`, `PROPERTY_LOOKUP_TABLE.getProperties()`, and `INSTANCE_TYPE.getValues()` null/default flag behavior.
- Mock DCE tests that assert each `IWbemServices` wrapper populates BSTR, pointer, flag, and NULL fields correctly and wraps the expected response pointer.
- Integration tests against a Windows WMI endpoint for `NTLMLogin`, `ExecQuery`, `Next`, `GetObject`, `ExecMethod`, `PutInstance`, and `DeleteInstance`, including HRESULT failure formatting.
- Regression tests for no unsolicited `print()` or `resp.dump()` output in library paths unless explicit debug mode is enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/dcom/wmi.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/dcomrt.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/dcomrt.py

## Purpose
`dcomrt.py` implements Impacket's core `[MS-DCOM]` runtime support. It defines DCOM wire structures, OBJREF formats, activation property blobs, object exporter calls, remote activation calls, `IRemUnknown` reference-management calls, and connection helpers that activate remote COM classes and keep remote OIDs alive.

## Important APIs, Types, and Functions
- DCOM identifiers include CLSIDs for activation property records and IIDs for `IActivation`, `IRemoteSCMActivator`, `IObjectExporter`, `IRemUnknown`, `IRemUnknown2`, `IUnknown`, and `IClassFactory`.
- Wire structures include `COMVERSION`, `ORPCTHIS`, `ORPCTHAT`, `MInterfacePointer`, `OBJREF`, `STDOBJREF`, `OBJREF_STANDARD`, `OBJREF_HANDLER`, `OBJREF_CUSTOM`, `OBJREF_EXTENDED`, `DUALSTRINGARRAY`, `STRINGBINDING`, `SECURITYBINDING`, `Context`, `ORPC_CONTEXT`, and activation blob structures such as `CustomHeader`, `ACTIVATION_BLOB`, `InstantiationInfoData`, `ActivationContextInfoData`, `ScmRequestInfoData`, `ScmReplyInfoData`, and `PropsOutInfo`.
- RPC call classes include `ResolveOxid`, `SimplePing`, `ComplexPing`, `ServerAlive`, `ResolveOxid2`, `ServerAlive2`, `RemoteActivation`, `RemoteGetClassObject`, `RemoteCreateInstance`, `RemQueryInterface`, `RemAddRef`, and `RemRelease`.
- `DCOMConnection` owns target credentials, the portmap DCE/RPC connection, OID ping sets, a class-level ping timer, `CoCreateInstanceEx()`, `get_dce_rpc()`, and `disconnect()`.
- `CLASS_INSTANCE` stores ORPC headers, resolved string bindings, and negotiated auth type/level for an activated class.
- `INTERFACE` wraps target, IPID, OID, OXID, object references, and per-thread DCE bindings; it parses object references, connects to object endpoints, sends DCOM requests, and disconnects object endpoint transports.
- `IRemUnknown` and `IRemUnknown2` expose `RemQueryInterface`, `RemAddRef`, and `RemRelease`.
- `IObjectExporter`, `IActivation`, and `IRemoteSCMActivator` expose activation, OXID resolution, alive checks, pinging, and class-object/instance activation.

## Control Flow
A `DCOMConnection` is initialized with target and credentials, creates an `ncacn_ip_tcp` transport, applies NTLM or Kerberos settings, sets the requested RPC authentication level, connects to the endpoint mapper/portmap, and stores the DCE connection in class-level `PORTMAPS`. `CoCreateInstanceEx()` uses `IRemoteSCMActivator.RemoteCreateInstance()` to activate a requested CLSID/IID and starts the keepalive ping timer when OXID resolver support is enabled.

Activation calls build ORPC headers and activation-property blobs, request TCP protocol sequence 7, send `RemoteCreateInstance` or `RemoteGetClassObject`, parse the returned custom OBJREF activation blob, extract `ScmReplyInfoData` for OXID bindings and `PropsOutInfo` for interface data, create a `CLASS_INSTANCE`, set auth hints from the server reply, and return an `IRemUnknown2` wrapping the requested interface pointer.

`INTERFACE.process_interface()` parses `OBJREF_*` bytes and, for standard/handler/extended references, records IPID, OID, and OXID. Unless `SORF_NOPING` is set, the OID is added to `DCOMConnection.OID_ADD`. `INTERFACE.connect()` reuses or creates one DCE object-endpoint connection per target/thread/OXID. It selects a TCP string binding from the activation reply, handles FQDN matching and NetBIOS substitution, copies credentials and Kerberos settings from the portmap transport, applies auth level/type from the class instance, connects, binds or alter-contexts to the requested IID, and stores the active binding.

`INTERFACE.request()` injects the stored ORPC header into each `DCOMCALL`, connects or adjusts context for the IID, sends the request using the object endpoint DCE connection, and transforms `RPC_E_DISCONNECTED` failures into a clearer keepalive warning. The ping timer periodically calls `DCOMConnection.pingServer()`, which sends `ComplexPing` when OIDs have been added or deleted and `SimplePing` otherwise.

## State and Persistence Behavior
All state is in process memory:
- `DCOMConnection.PORTMAPS` maps target names to shared portmap DCE objects.
- `DCOMConnection.OID_ADD`, `OID_DEL`, and `OID_SET` track OID lifetime and ping set IDs by target.
- `DCOMConnection.PINGTIMER` is a class-level `threading.Timer` that reschedules itself every 120 seconds.
- `INTERFACE.CONNECTIONS` maps target, thread name, and OXID to object endpoint DCE connections and current IID binding.
- `CLASS_INSTANCE` retains the ORPC header, server string bindings, auth type, and auth level.
No durable persistence is performed. Remote COM object lifetimes are affected by OID pinging and `RemRelease`; `disconnect()` removes local connection/ping state and cancels the timer when no portmaps remain.

## Dependencies and Integration Points
This file depends on Impacket NDR, DCE/RPC transport, type serialization, HRESULT metadata, UUID utilities, socket address parsing, `threading.Timer`, and RPC authentication constants. It is the foundation for higher-level DCOM modules such as `dcom/wmi.py`, which inherit `IRemUnknown` and `INTERFACE` behavior. Integration points include the endpoint mapper, the remote SCM activator, the object exporter, per-object endpoint bindings returned in dual-string arrays, and Kerberos/NTLM credential propagation from the portmap transport to object transports.

## Risks and Edge Cases
- Class-level dictionaries and ping sets are not protected by locks; concurrent activations, releases, and ping timer runs can race.
- `pingServer()` iterates and mutates class-level dictionaries and catches broad exceptions, so failures can hide stale OID state.
- `ComplexPing()` accepts a `sequenceNum` argument but writes `SequenceNum` from `setId`, likely ignoring the supplied sequence number.
- `OBJREF_EXTENDED.__init__()` sets `Signature1` twice and sets `nElms` to the signature value, which looks suspicious and needs protocol validation.
- `INTERFACE.connect()` only accepts TCP tower id 7 and may fail with endpoints that prefer other protocol sequences.
- Target matching for string bindings is heuristic and can fail with unusual DNS suffixes, IPv6 formatting, NetBIOS names, or NAT/forwarded bindings.
- `INTERFACE.CONNECTIONS[self.__target][current_thread().name] = {}` replaces existing per-thread OXID entries when creating a new object connection, which can discard other OXID connections for the same thread.
- Activation helpers mostly support one IID at a time despite protocol fields allowing multiple requested interfaces.
- Some response HRESULT/error fields are not explicitly checked before wrapping returned interface data.
- The runtime assumes NDR32 layouts and Impacket type serialization behavior matching the target DCOM implementation.

## Test Signals
Useful tests should include:
- Golden NDR encode/decode tests for `OBJREF_*`, `DUALSTRINGARRAY`, `ACTIVATION_BLOB`, `ScmReplyInfoData`, and `PropsOutInfo`.
- Mock DCE tests for `RemoteCreateInstance`, `RemoteGetClassObject`, `ResolveOxid`, `ServerAlive2`, `RemQueryInterface`, `RemAddRef`, and `RemRelease` request fields and response wrapping.
- Unit tests for `COMVERSION.set_default_version()`, `CLASS_INSTANCE.get_auth_level()`, `handle_t.isNull()`, and object-reference parsing with and without `SORF_NOPING`.
- Connection-selection tests covering IPv4, IPv6, FQDN, NetBIOS-derived bindings, Kerberos remote host/name propagation, alter-context reuse, and multiple OXIDs in one thread.
- Timer/lifetime tests that simulate OID add/delete sets and verify `ComplexPing`, `SimplePing`, `RemRelease`, and `disconnect()` state cleanup.
- Integration tests against a Windows host for remote activation of a known class, query-interface, method call through a higher-level module, idle keepalive, and clean release/disconnect.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/dcomrt.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/dhcpm.py -->
# sources/user-network-fs/impacket/impacket/dcerpc/v5/dhcpm.py

## Purpose
`dhcpm.py` implements Impacket's `[MS-DHCPM]` DHCP server management RPC bindings. It defines UUIDs, DHCP-specific error constants, NDR structures for DHCP clients, subnets, reservations, option scopes, option data, subnet elements, and call/response classes plus helper functions for common DHCP server enumeration and lookup operations.

## Important APIs, Types, and Functions
- Interface UUIDs are `MSRPC_UUID_DHCPSRV` for `dhcpsrv` and `MSRPC_UUID_DHCPSRV2` for `dhcpsrv2`.
- `DCERPCSessionError` formats DHCPM failures using generic Windows system errors plus module-local DHCP error messages.
- Core aliases include `DHCP_SRV_HANDLE`, `DHCP_IP_ADDRESS`, `DHCP_IP_MASK`, and `DHCP_OPTION_ID`.
- Enumerations include `DHCP_SEARCH_INFO_TYPE`, `QuarantineStatus`, `DHCP_SUBNET_STATE`, `DHCP_OPTION_SCOPE_TYPE`, `DHCP_SUBNET_ELEMENT_TYPE`, and `DHCP_OPTION_DATA_TYPE`.
- Client structures include `DHCP_CLIENT_INFO_V4`, `DHCP_CLIENT_INFO_V5`, `DHCP_CLIENT_INFO_VQ`, `DHCP_CLIENT_INFO_PB`, their pointer and array wrappers, `DHCP_SEARCH_INFO`, `DHCP_CLIENT_SEARCH_UNION`, `DHCP_BINARY_DATA`, `DHCP_CLIENT_UID`, and `DATE_TIME`.
- Subnet and option structures include `DHCP_SUBNET_INFO`, `DHCP_OPTION_SCOPE_INFO`, `DHCP_RESERVED_SCOPE`, `DHCP_BOOTP_IP_RANGE`, `DHCP_IP_RESERVATION_V4`, `DHCP_IP_RANGE`, `DHCP_IP_CLUSTER`, `DHCP_SUBNET_ELEMENT_DATA_V5`, `DHCP_OPTION_DATA_ELEMENT`, `DHCP_OPTION_DATA`, `DHCP_OPTION_VALUE`, `DHCP_OPTION_VALUE_ARRAY`, and `DHCP_ALL_OPTIONS_VALUES`.
- RPC call classes cover `DhcpGetSubnetInfo`, `DhcpEnumSubnets`, `DhcpGetOptionValue`, `DhcpEnumOptionValues`, `DhcpGetClientInfoV4`, `DhcpEnumSubnetClientsV4`, `DhcpEnumSubnetClientsV5`, `DhcpGetOptionValueV5`, `DhcpEnumOptionValuesV5`, `DhcpGetAllOptionValues`, `DhcpEnumSubnetElementsV5`, `DhcpEnumSubnetClientsVQ`, and `DhcpV4GetClientInfo`.
- `OPNUMS` maps opnums 0, 2, 3, 13, 14, 21, 22, 30, 34, 35, 38, 47, and 123 to request/response classes.
- Helper functions beginning with `h` build and submit common requests: `hDhcpGetClientInfoV4`, `hDhcpGetSubnetInfo`, option value helpers, subnet enumeration helpers, client enumeration helpers, and subnet element enumeration.

## Control Flow
Most of the file is declarative NDR schema. Callers bind a DCE/RPC connection to one of the DHCP server UUIDs and then either instantiate request classes directly or use the helper functions. Helpers populate the nullable `ServerIpAddress` with `NULL` to address the bound server, set discriminator fields for unions such as `SearchInfo.SearchInfo.tag` or `ScopeInfo.ScopeInfo.tag`, fill request-specific fields, then call `dce.request(request)`.

Search helpers choose the correct union arm based on `DHCP_SEARCH_INFO_TYPE`: client IP address, hardware address, or client name. Option helpers choose the correct scope union arm based on `DHCP_OPTION_SCOPE_TYPE`: default/global options have no union payload, subnet options use an IPv4 address, reserved options use `DHCP_RESERVED_SCOPE`, and multicast scope options use a wide string. Enumeration helpers initialize resume handles to `NULL`, set `PreferredMaximum`, submit the request, and return the first response or the exception packet when the server reports end-of-data style status that the helper expects.

## State and Persistence Behavior
The module itself keeps no mutable global state beyond constants and class definitions. Helper functions are stateless and do not persist resume handles between calls. Remote DHCP server state is read by all currently implemented helpers; the file defines structures and errors for mutable concepts such as scopes, ranges, clients, reservations, policies, options, and failover, but the provided helper surface is focused on lookup/enumeration. The returned packets can include server-side resume handles, but callers must manage pagination manually if they need to continue past a first partial response.

## Dependencies and Integration Points
The file depends on Impacket's NDR call, structure, pointer, array, enum, and union classes; DHCP uses `dtypes` primitives such as `LPWSTR`, `DWORD`, `LPDWORD`, `BOOL`, `BYTE`, and `WORD`. Error handling uses `system_errors` and `DCERPCException`. UUID generation uses `uuidtup_to_bin`. It integrates with the rest of Impacket through the standard DCE/RPC transport and request machinery: callers bind a transport to `MSRPC_UUID_DHCPSRV` or `MSRPC_UUID_DHCPSRV2`, and `OPNUMS` supports response decoding.

## Risks and Edge Cases
- The helper pagination loops return inside the first iteration, so they do not actually continue while `ERROR_MORE_DATA` or `STATUS_MORE_ENTRIES` is present. Callers expecting full enumeration must handle resume handles themselves.
- Several helpers catch exceptions by matching text such as `ERROR_NO_MORE_ITEMS` or `STATUS_MORE_ENTRIES`; changes in exception formatting can break this behavior.
- `hDhcpEnumSubnetClientsV5()` catches `DCERPCSessionError`, while many other helpers catch `DCERPCException`; inconsistent exception types can miss expected packets.
- Some NDR structures appear suspicious: `DHCP_BOOTP_IP_RANGE` defines `MaxBootpAllowed` twice with different types, causing the first field name to be overwritten in Python structure semantics.
- The `DhcpEnumSubnetClientsV5Response` class omits an explicit `ErrorCode` field unlike the nearby V4/VQ responses, which should be checked against the protocol and decoder behavior.
- Helper defaults often use `SubnetAddress = NULL` or `0`; callers need to know when the server treats this as all subnets versus an invalid scope.
- DHCP IP addresses are raw DWORDs, so callers must provide network/order values consistent with Impacket and protocol expectations.
- Memory ownership/freeing of server-allocated buffers is not modeled; the library relies on decoded response objects rather than explicit RPC free calls.
- The module exposes many DHCP error constants but only a small subset has custom human-readable messages.

## Test Signals
Useful tests should include:
- NDR encode/decode golden tests for each DHCP client info version, option data union arm, option scope union arm, subnet element union arm, and call/response class in `OPNUMS`.
- Unit tests for helper request construction, especially union `tag` values and payload fields for client search and option scope variants.
- Pagination/resume-handle tests with mock DCE responses that include `ERROR_MORE_DATA`, `STATUS_MORE_ENTRIES`, and no-more-items exceptions.
- Error formatting tests for generic `system_errors`, module-local DHCP errors, and unknown errors.
- Regression tests for suspicious structures such as duplicate `MaxBootpAllowed` and `DhcpEnumSubnetClientsV5Response` response shape.
- Integration tests against a Windows DHCP server for subnet enumeration, subnet info lookup, client enumeration across V4/V5/VQ variants, option value lookup, all option values, and subnet element enumeration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/dcerpc/v5/dhcpm.py -->

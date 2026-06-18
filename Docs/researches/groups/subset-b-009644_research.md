# Research: subset-b-009644

This grouped report covers the requested Impacket remote integration test files. Each section is delimited for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/SMB_RPC/test_wmi.py -->
# sources/user-network-fs/impacket/tests/SMB_RPC/test_wmi.py

Purpose: tests Impacket's DCOM/WMI client helpers against a remote Windows host and also verifies offline WMI object-reference parsing. The remote `WMITests` class authenticates with `DCOMConnection`, activates `CLSID_WbemLevel1Login`, logs into `\\<machine>\root\cimv2`, and covers `IWbemLevel1Login` plus selected `IWbemServices` methods. `WMIOfflineTests` decodes compressed/base64 object references into `wmi.IWbemClassObject` without network access.

Important APIs and functions: `_connect_wmi()` centralizes DCOM connection, login, and `IWbemServices` acquisition. Remote tests cover `EstablishPosition`, `RequestChallenge`, `WBEMLogin`, `NTLMLogin`, `OpenNamespace`, `GetObject`, `ExecQuery`, `ExecMethod`, `PutClass`, and `DeleteClass`. Offline helpers are `createIWbemClassObject()` and `assertIWbemClassObjectAttr()`, testing parsed properties from `Win32_CurrentTime` and WMI persistence classes such as `ActiveScriptEventConsumer`, `__IntervalTimerInstruction`, `__EventFilter`, and `__FilterToConsumerBinding`.

Control flow: each remote test creates a DCOM connection, obtains a WMI login interface, calls one operation, then disconnects. Query tests iterate `IEnumWbemClassObject.Next()` until `S_FALSE`. `test_IWbemServices_ExecMethod` creates `notepad.exe`, queries it back by process handle, and terminates it. Class mutation tests create a WMI class, round-trip attributes, and delete the class in `finally`. Offline tests decompress fixtures, instantiate interface wrappers, and assert decoded attributes.

State and persistence behavior: most remote calls are read-only, but `ExecMethod` briefly creates a process, and `PutClass`/`PutClass_update_adds_property` create WMI repository classes. Cleanup is explicit with `Terminate()` or `DeleteClass()` in `finally`, although `test_IWbemServices_PutClass` uses fixed `DummyClass`, which can collide or leave residue if deletion fails. Offline tests are deterministic and have no external state.

Dependencies and integration points: depends on pytest/unittest, `tests.RemoteTestCase` credentials, `impacket.dcerpc.v5.dcom.wmi`, `DCOMConnection`, WMI/DCOM activation permissions, and a reachable Windows WMI service. Offline parsing depends on stable binary object-reference fixtures captured from prior WMI tooling.

Risks: remote tests are environment-sensitive and privilege-sensitive. `test_activation` and `OpenNamespace` are marked xfail. Process creation and WMI repository writes are operationally intrusive. Several exception checks rely on substring matching such as `WBEM_E_NOT_SUPPORTED`, `E_NOTIMPL`, and `WBEM_E_NOT_FOUND`. Offline fixtures encode subtle parser expectations, including booleans and SIDs currently represented as strings.

Test signals: success proves DCOM activation, WMI login, WQL enumeration, class-object parsing, method dispatch, class creation/update/delete, and object-reference decoding. Failure patterns identify WMI/DCOM authentication issues, parser regressions in `IWbemClassObject`, or changed server behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/SMB_RPC/test_wmi.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/__init__.py -->
# sources/user-network-fs/impacket/tests/__init__.py

Purpose: provides the shared remote-test configuration layer used by Impacket integration tests. It stores the remote config path, loads `tests/dcetests.cfg` or a user-specified config, and applies credentials and target identifiers to test instances.

Important APIs and types: module globals include `remote_config_file_path`, `remote_config_section`, `remote_config_params`, and `remote_config_params_names`. Public helpers are `set_remote_config_file_path()`, `get_remote_config_file_path()`, `get_remote_config()`, and `set_transport_config()`. `RemoteTestCase` exposes `set_transport_config()` as a base-class method for unittest-style tests.

Control flow: config path resolution first honors the pytest-set module variable, then `REMOTE_CONFIG`, then defaults to `tests/dcetests.cfg`. `set_transport_config()` reads the `TCPTransport` section and sets `username`, `domain`, `serverName`, `password`, `machine`, and `hashes` on the target object. It splits NTLM hashes into text and binary LM/NT values. Optional branches load machine-account hashes and Kerberos AES keys.

State and persistence behavior: module state is limited to the selected config path. The loaded credentials are copied to test objects or pytest config objects at runtime. No files are written.

Dependencies and integration points: uses `ConfigParser`, environment variables, `binascii.unhexlify`, and `six.moves.configparser`. It is consumed by `conftest.py`, `tests.dcerpc.DCERPCTests`, WMI tests, and many SMB/RPC tests. The expected config schema is documented by `dcetests.cfg.template`.

Risks: missing options raise config parser errors at setup time. Hash parsing assumes `LM:NT` format when `hashes` is non-empty. Secrets are attached as plain object attributes. The default path is relative to the working directory, so running tests outside the repository can silently miss the intended config.

Test signals: healthy remote integration tests demonstrate this module loaded the correct target, domain, username, password/hash, server NetBIOS name, and optional machine-account credentials.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/conftest.py -->
# sources/user-network-fs/impacket/tests/conftest.py

Purpose: integrates the shared remote-test configuration with pytest. It adds a command-line/ini option for the remote configuration file and provides a class-scoped fixture that populates test classes with credential attributes.

Important APIs and functions: `pytest_addoption()` registers `--remote-config` and `remote-config` ini. `pytest_configure()` resolves those settings and, when present, calls `set_remote_config_file_path()` and `set_transport_config(config)`. The `remote` fixture calls `set_transport_config(request.cls)` for class tests.

Control flow: pytest startup parses options, then configuration is applied globally. For tests using `@pytest.mark.usefixtures("remote")` or class fixture injection, the class receives the same attributes expected by `RemoteTestCase` subclasses.

State and persistence behavior: no persistent files are written. It can mutate the pytest `config` object with credential attributes, and fixture execution mutates test classes.

Dependencies and integration points: depends on pytest hook semantics and local helpers from `tests.__init__`. It connects pytest option handling to unittest-style remote tests and complements direct `RemoteTestCase.set_transport_config()` calls in test `setUp()` methods.

Risks: `parser.addini(..., type="pathlist")` may return a list while `set_remote_config_file_path()` expects a file-like path value; callers usually use the command-line option. Applying credentials to pytest `config` can expose secrets to plugins inspecting config attributes. Missing config values fail before remote tests run.

Test signals: pytest collection and remote tests using `--remote-config` should use the specified file rather than the default or `REMOTE_CONFIG`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/conftest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/__init__.py -->
# sources/user-network-fs/impacket/tests/dcerpc/__init__.py

Purpose: defines the base class for DCE/RPC endpoint integration tests. `DCERPCTests` turns remote configuration into a bound DCE/RPC connection using either a formatted string binding or endpoint-mapper resolution.

Important APIs and types: `DCERPCTests` inherits `RemoteTestCase` and defines constants `STRING_BINDING_FORMATTING`, `STRING_BINDING_MAPPER`, `TRANSFER_SYNTAX_NDR`, and `TRANSFER_SYNTAX_NDR64`. Configurable class attributes include `timeout`, `authn`, `authn_level`, `iface_uuid`, `protocol`, `string_binding`, `string_binding_formatting`, `transfer_syntax`, and `machine_account`. The main method is `connect()`.

Control flow: `setUp()` loads credentials, then formats `string_binding` with the test instance or uses `epm.hept_map()` for dynamic endpoint lookup. `connect()` creates a transport via `transport.DCERPCTransportFactory`, applies timeout and credentials when supported, obtains the DCE object, sets authentication level, connects, and binds to `iface_uuid` with optional transfer syntax.

State and persistence behavior: per-test mutable state is the resolved `string_binding` and credential attributes. No persistent files are written. Network handles are returned to callers, which are responsible for cleanup.

Dependencies and integration points: centralizes Impacket transport setup for all `tests/dcerpc/test_*.py` files. It depends on `impacket.dcerpc.v5.transport`, `epm`, and the shared remote config module.

Risks: `connect()` raises `NotImplemented` as an exception object rather than `NotImplementedError`. Tests relying on `string_binding` mutation in `setUp()` may be affected if the same instance reconnects with a changed class attribute. Authentication only applies when the transport has `set_credentials`; callers must handle transports without it. Returned DCE objects are not automatically disconnected.

Test signals: downstream remote tests passing across SMB named pipes, TCP endpoint mapper bindings, NDR, and NDR64 validates this base transport path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_bkrp.py -->
# sources/user-network-fs/impacket/tests/dcerpc/test_bkrp.py

Purpose: validates the BackupKey Remote Protocol client (`bkrp`) over `\PIPE\protected_storage`, including secret wrapping/restoration and backup public-key retrieval.

Important APIs and functions: `BKRPTests` configures `MSRPC_UUID_BKRP`, SMB named-pipe binding, authenticated packet privacy, and a static `data_in` byte string. Tests exercise raw `bkrp.BackuprKey()` requests and helper `bkrp.hBackuprKey()` for `BACKUPKEY_BACKUP_GUID`, `BACKUPKEY_RESTORE_GUID`, `BACKUPKEY_RESTORE_GUID_WIN2K`, and `BACKUPKEY_RETRIEVE_BACKUP_KEY_GUID`. `bkrp.WRAPPED_SECRET` parses wrapped output, and `cryptography.x509.load_der_x509_certificate()` parses returned certificates.

Control flow: backup tests send plaintext, parse the wrapped response, then submit it to a restore action and assert restored bytes equal `data_in`. Retrieval tests request the backup key with `NULL` input and parse the DER certificate. SMB NDR and NDR64 subclasses run the same suite.

State and persistence behavior: the tests do not write remote state. They depend on domain backup-key service state and may expose backup-key certificate material in printed output.

Dependencies and integration points: depends on `cryptography` for certificate parsing, `tests.dcerpc.DCERPCTests`, and authenticated domain access to Protected Storage/DPAPI backup key RPC.

Risks: missing `cryptography` is only printed at import time, so certificate tests can later fail with `NameError`. These tests require privileges/service availability and packet privacy. They validate sensitive DPAPI backup-key paths and should be run only in controlled labs.

Test signals: strong signal for BKRP NDR marshalling, helper wrappers, backup/restore round trips, NDR64 compatibility, and certificate blob parsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_bkrp.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_dcomrt.py -->
# sources/user-network-fs/impacket/tests/dcerpc/test_dcomrt.py

Purpose: exercises Impacket DCOM runtime bindings, activation, object exporter, remote SCM activation, interface querying, and COM Event System helper wrappers.

Important APIs and functions: `DCOMTests` uses TCP DCOM with NTLM packet integrity. It covers `IObjectExporter.ServerAlive`, `ServerAlive2`, `ComplexPing`, `SimplePing`, `ResolveOxid`, `ResolveOxid2`, `IActivation.RemoteActivation`, `IRemoteSCMActivator.RemoteCreateInstance`, and `RemoteGetClassObject`. `DCOMConnectionTests` exercises `DCOMConnection.CoCreateInstanceEx`, `RemQueryInterface`, `RemRelease`, `comev.IEventSystem`, `oaut.IDispatch`, type-info enumeration, and Event System collection enumeration.

Control flow: most tests bind to DCOM TCP, instantiate Event System COM objects, and call one runtime method. `RemoteGetClassObject` uses a `DCOMConnection` directly and releases the interface in `finally`. The `test_comev` path walks type information and enumerates Event Subscription/Event Class collections, releasing interfaces.

State and persistence behavior: tests are mostly read-only COM activation/enumeration. Skipped exploratory tests for VSS, VDS, OAUT, and IE show broader potential but do not run.

Dependencies and integration points: uses `tests.RemoteTestCase`, `tests.dcerpc.DCERPCTests`, `impacket.dcerpc.v5.dcomrt`, and COM helper modules `scmp`, `vds`, `oaut`, and `comev`. Requires remote DCOM firewall/configuration and privileges for COM activation.

Risks: file defines two classes named `DCOMTestsTCPTransport`; the second NDR64 class overwrites the first name in module scope, likely losing the NDR transport class from unittest discovery. Some tests do not always release activated COM interfaces. Event System contents vary by host. DCOM hardening and firewall policy can make failures environmental.

Test signals: validates DCOM endpoint binding, OXID resolution, activation, class factory retrieval, remote unknown lifetime operations, and high-level Event System wrappers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_dcomrt.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_dhcpm.py -->
# sources/user-network-fs/impacket/tests/dcerpc/test_dhcpm.py

Purpose: tests DHCP Server Management Protocol request marshalling and helper functions for DHCP client and option lookup paths.

Important APIs and functions: `DHCPMTests` defines DHCPSRV v1/v2 UUIDs, `\PIPE\dhcpserver`, and packet privacy. Tests cover raw `DhcpGetClientInfoV4`, helper `hDhcpGetClientInfoV4`, raw `DhcpV4GetClientInfo`, `hDhcpEnumSubnetClientsV5`, and `hDhcpGetOptionValueV5`.

Control flow: v1 and v2 tests connect to specific interface UUIDs. Client-info calls build `DHCP_SEARCH_INFO_TYPE.DhcpClientName` searches for `serverName`. Option lookup derives the local subnet by replacing the target host octet with zero and asks for router option 3. Expected DHCP error codes are asserted with `assertRaisesRegex`.

State and persistence behavior: read-only. No DHCP scopes, clients, or options are changed.

Dependencies and integration points: uses endpoint mapper for TCP transport subclasses and skips SMB transports because Windows Server 2008 onward disables that path. It depends on DHCP service availability and `DCERPCTests` authentication.

Risks: success is often expected server-side failure (`ERROR_DHCP_JET_ERROR`, `ERROR_DHCP_INVALID_DHCP_CLIENT`, `ERROR_NO_MORE_ITEMS`, `ERROR_DHCP_SUBNET_NOT_PRESENT`), so different DHCP configuration can change outcomes. NDR64 option-value union handling is marked xfail for a known unimplemented case.

Test signals: proves DHCPM bindability, request union/discriminant encoding, helper parity, endpoint mapping, and expected error unmarshalling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_dhcpm.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_drsuapi.py -->
# sources/user-network-fs/impacket/tests/dcerpc/test_drsuapi.py

Purpose: validates Directory Replication Service Remote Protocol bindings and selected Active Directory replication/name service requests.

Important APIs and functions: `DRSRTests` uses `drsuapi.MSRPC_UUID_DRSUAPI`, `\PIPE\lsass`, and packet privacy. `bind()` builds `DRSBind` with `DRS_EXTENSIONS_INT`, handles replication epoch mismatch by rebinding, then retrieves the NTDS DSA object GUID with `hDRSDomainControllerInfo`. Tests cover raw/helper `DRSDomainControllerInfo`, raw/helper `DRSCrackNames`, `DRSGetNT4ChangeLog`, `DRSVerifyNames`, and xfailed `DRSGetNCChanges` v8/v10 paths. `getMoreData()` loops multi-response NC-change replies.

Control flow: most tests connect, call `bind()`, then issue one DRS request. Name-cracking tests translate Administrator and NTDS Settings names between NT4, UPN, SID, FQDN 1779, unique-id, and role formats. NC-change tests build DSNAME structures, USN vectors, partial attribute sets with schema OIDs, prefix tables, flags such as `DRS_INIT_SYNC`, and secret-replication extended ops.

State and persistence behavior: normal tests are read-only directory queries. Xfailed NC-change tests request replication data and include secret attributes (`unicodePwd`, password history, supplemental credentials), making them sensitive even if expected to fail or require privilege. No directory writes are performed.

Dependencies and integration points: depends on Active Directory domain configuration, LSASS DRSUAPI endpoint, packet privacy, and domain naming assumptions using `self.domain.split('.')`. Runs over SMB named pipe and TCP endpoint-mapped transports, in NDR and NDR64.

Risks: tests can expose sensitive replication behavior; they require domain controller privileges and can fail due to AD version, topology, or hardening. `getMoreData()` appears to assign `uuidInvocIdSrc` incorrectly from the whole V6 response object rather than a GUID field, so the xfailed loop is fragile. Hardcoded names like `DC1-WIN2012` reduce portability.

Test signals: validates DRS extension negotiation, epoch handling, domain controller info levels, name cracking, verify-name marshalling, and partially documents replication request construction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_drsuapi.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_epm.py -->
# sources/user-network-fs/impacket/tests/dcerpc/test_epm.py

Purpose: tests RPC Endpoint Mapper lookup and map operations over SMB and TCP.

Important APIs and functions: `EPMTests` binds to `epm.MSRPC_UUID_PORTMAP`. It covers raw `ept_lookup`, helper `hept_lookup`, raw `ept_map`, and helper `hept_map`. It constructs `EPMTower`, `EPMRPCInterface`, `EPMRPCDataRepresentation`, protocol, port, host, and pipe floor structures.

Control flow: lookup retrieves endpoint entries and parses each tower. Helper lookup filters SAMR, ATSVC, and SCMR interface UUIDs. Map constructs a tower for SAMR-like interface data and requests up to four towers. Helper map resolves SMB and TCP bindings for several known interfaces.

State and persistence behavior: read-only endpoint mapper queries.

Dependencies and integration points: depends on endpoint mapper over `\pipe\epmapper` and TCP port 135. It is also indirectly used by `DCERPCTests` mapper-mode subclasses and RAA endpoint discovery.

Risks: endpoint availability depends on Windows version, firewall, and service state. The raw map test builds some unused floor objects and uses fixed UUIDs, so failures can reflect environment rather than Impacket regressions.

Test signals: verifies tower parsing/serialization, endpoint-map helper behavior, and both SMB/TCP EPM transport compatibility across NDR and NDR64.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_epm.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_even.py -->
# sources/user-network-fs/impacket/tests/dcerpc/test_even.py

Purpose: validates legacy EventLog RPC (`even`) client calls against `\PIPE\eventlog`.

Important APIs and functions: class `RRPTests` in this file binds `even.MSRPC_UUID_EVEN` with packet privacy. It exercises raw and helper calls for `ElfrOpenBELW`, `ElfrOpenELW`, `ElfrRegisterEventSourceW`, `ElfrReadELW`, `ElfrClearELFW`, `ElfrBackupELFW`, raw `ElfrReportEventW`, `hElfrNumberOfRecords`, and `hElfrOldestRecordNumber`.

Control flow: tests open the Security log or a bogus backup log path, then issue read, clear, backup, report, count, and oldest-record requests. Many paths assert expected Windows errors such as missing backup file, invalid backup path, or access denied.

State and persistence behavior: mostly read-only. Clear, backup, and report calls are attempted but expected to fail due to invalid path or access denial, preventing actual log mutation. Handles are not explicitly closed in this suite.

Dependencies and integration points: requires eventlog named pipe, authenticated access, and sufficient rights to read Security log for success paths. Uses Impacket `even` NDR structures and helper functions.

Risks: Security log access is privilege-sensitive. Expected error text can vary. Class name `RRPTests` is misleading and can confuse test reporting.

Test signals: confirms legacy eventlog handle creation, read buffer handling, expected error unmarshalling, and helper parity for NDR/NDR64 named-pipe transports.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_even.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_even6.py -->
# sources/user-network-fs/impacket/tests/dcerpc/test_even6.py

Purpose: tests newer Windows Event Log RPC (`even6`) query/subscription helpers over TCP endpoint-mapped transport.

Important APIs and functions: `EVEN6Tests` binds `even6.MSRPC_UUID_EVEN6`, uses packet privacy, and covers raw/helper `EvtRpcRegisterRemoteSubscription`, `EvtRpcRemoteSubscriptionNext`, `EvtRpcRegisterLogQuery`, `EvtRpcQueryNext`, plus helper `EvtRpcRegisterControllableOperation`, `EvtRpcClearLog`, `EvtRpcExportLog`, and `EvtRpcClose`.

Control flow: subscription tests register a pull subscription on the Security channel with query `*`, fetch up to five records, slice returned event blobs using `EventDataIndices` and `EventDataSizes`, then close the handle. Query tests register a log query and fetch records similarly. Clear/export tests acquire a controllable operation handle, invoke the operation, and close it.

State and persistence behavior: query/subscription paths are read-only. `hEvtRpcClearLog` and `hEvtRpcExportLog` are stateful and potentially destructive/intrusive: they target the Security log and `C:\Security_Log_Exported.evtx`. The source code does not wrap those in expected failure assertions.

Dependencies and integration points: depends on endpoint mapper registration for EVEN6 over TCP, eventlog service, Security log permissions, and Impacket even6 helper structures.

Risks: clear/export operations should be run only in disposable labs. Event availability and permissions vary. Event blobs are assigned to a local variable but not asserted, so tests mainly verify calls do not fail.

Test signals: validates dynamic TCP binding, pull-subscription/query handle lifecycle, packed event buffer index handling, and close helper behavior under NDR/NDR64.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_even6.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_fasp.py -->
# sources/user-network-fs/impacket/tests/dcerpc/test_fasp.py

Purpose: placeholder/skipped tests for a Firewall/Advanced Security Policy (`fasp`) RPC module that is unavailable in the current tree.

Important APIs and functions: `FASPTests` is decorated with `pytest.mark.skip(reason="fasp module unavailable")` and sets `fasp = None`. Intended tests reference `FWOpenPolicyStore`, helper `hFWOpenPolicyStore`, `FWClosePolicyStore`, and `hFWClosePolicyStore` with local store/read access constants.

Control flow: if unskipped and a real module were restored, tests would connect through endpoint mapper over TCP, open a firewall policy store, and close it. Both raw and helper variants are represented.

State and persistence behavior: intended policy-store access is read-only. In current form, no tests execute.

Dependencies and integration points: would depend on `impacket.dcerpc.v5.fasp`, packet privacy, endpoint mapper, and firewall service support. Currently it depends only on pytest skip behavior and base DCE/RPC test scaffolding.

Risks: if the class-level skip is removed without replacing `fasp = None`, tests will fail with attribute errors. The missing UUID and commented `iface_uuid` mean mapper binding is incomplete.

Test signals: current signal is only that pytest properly skips unavailable protocol coverage. It documents an intended future RPC surface.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_fasp.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_lsad.py -->
# sources/user-network-fs/impacket/tests/dcerpc/test_lsad.py

Purpose: broad integration coverage for Local Security Authority Policy (`lsad`) RPC over `\PIPE\lsarpc`, including policy queries, account/privilege management, secret/private-data APIs, security descriptors, forest trust queries, and policy mutation.

Important APIs and functions: `LSADTests.open_policy()` obtains a policy handle with `MAXIMUM_ALLOWED`, `POLICY_CREATE_SECRET`, `DELETE`, and `POLICY_VIEW_LOCAL_INFORMATION`. Tests cover raw/helper `LsarOpenPolicy`, `LsarOpenPolicy2`, `LsarQueryInformationPolicy(2)`, `LsarQueryDomainInformationPolicy`, account enumeration/open/create/delete, privilege add/remove/enumerate/lookup/display, account rights add/remove, secret create/open/set/query/delete, private data retrieve/store, security query/set, forest trust query, and `LsarSetInformationPolicy(2)`.

Control flow: most tests connect, open a policy handle, build an NDR request or helper call, dump responses, and sometimes assert round-trip values. Account mutation tests derive the account domain SID and append RID `9999` for temporary account operations. Secret tests create `MYSECRET`, open it, attempt to set encrypted values, then delete it. Private-data tests copy `DPAPI_SYSTEM` encrypted data into key `BETUS` and then remove it by storing `NULL`. Audit-policy tests read `AuditingMode`, set it to zero, re-read, and restore the old value.

State and persistence behavior: many tests mutate remote LSA state but usually clean up: temporary accounts are deleted, privileges/right changes are removed, secrets are deleted, private data `BETUS` is cleared, and audit policy is restored. If an exception interrupts cleanup outside guarded blocks, residue or policy changes can remain.

Dependencies and integration points: depends on authenticated LSA RPC, administrative or high-privilege rights for many operations, `impacket.dcerpc.v5.lsad` structures, NDR/NDR64 transfer syntax, and Windows/domain policy semantics.

Risks: high operational risk in non-disposable environments. Some operations touch sensitive secrets (`DPAPI_SYSTEM`) and security policy. Cleanup is inconsistent: several tests do not use `finally`. Broad `MAXIMUM_ALLOWED` requests and policy changes can fail due to UAC/LSA protection/domain policy. Some exception handling accepts expected domain-specific status strings.

Test signals: provides extensive marshalling and helper parity coverage for LSAD unions, handles, SIDs, LUID privileges, unicode strings, security descriptors, encrypted secret blobs, mutable policy information, and NDR64 compatibility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_lsad.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_lsat.py -->
# sources/user-network-fs/impacket/tests/dcerpc/test_lsat.py

Purpose: tests LSA Translation (`lsat`) RPC name/SID lookup APIs over `\PIPE\lsarpc`.

Important APIs and functions: `LSATTests.open_policy()` uses `lsad.LsarOpenPolicy2` with lookup access. Tests cover raw/helper `LsarGetUserName`, `LsarLookupNames`, `LsarLookupNames2`, `LsarLookupNames3`, `LsarLookupNames4`, `LsarLookupSids`, `LsarLookupSids2`, and raw `LsarLookupSids3`.

Control flow: name tests build `RPC_UNICODE_STRING` values for Administrator and Guest, set lookup levels/options/client revision, and call raw/helper variants. SID tests first resolve Administrator to a domain SID, then build well-known RID suffixes such as `-500` and `-501`. Bulk SID lookup builds 1000 SIDs to force `STATUS_SOME_NOT_MAPPED`.

State and persistence behavior: read-only translation queries. No remote policy or account data is changed.

Dependencies and integration points: depends on `lsat` and `lsad` modules, LSA policy handle acquisition, domain-local Administrator/Guest names, and authentication. The v3/v4 tests assert access denial where Netlogon authentication would be required.

Risks: localized or renamed built-in accounts can change results. Expected denial strings for Netlogon-required paths can vary. Bulk 1000-SID test creates larger responses and may be slower on constrained domain controllers.

Test signals: verifies LSAT union formats, referenced domain handling, SID construction, helper/raw parity, access-control failures for v3/v4 APIs, and NDR64 behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_lsat.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_mgmt.py -->
# sources/user-network-fs/impacket/tests/dcerpc/test_mgmt.py

Purpose: tests RPC Management interface calls over endpoint mapper transports.

Important APIs and functions: `MGMTTests` binds `mgmt.MSRPC_UUID_MGMT` and covers raw/helper `inq_if_ids`, `inq_stats`, `is_server_listening`, `stop_server_listening`, and `inq_princ_name`.

Control flow: each test connects to either SMB `\pipe\epmapper` or TCP port 135, builds a management request or calls the helper, and dumps the response. Stop-listening tests assert `rpc_s_access_denied`. Some calls disable automatic error checking to inspect returned management status.

State and persistence behavior: read-only except `stop_server_listening`, which would be disruptive but is expected to be denied.

Dependencies and integration points: depends on endpoint mapper service, RPC management interface, Impacket `mgmt` helpers, and the shared DCE/RPC test base.

Risks: management availability and principal-name behavior can differ by transport and security policy. Stop-listening is correctly guarded by expected denial but should not be run with privileges that could actually stop a service.

Test signals: verifies management interface binding, interface-vector parsing, stats arrays, listening status, denial handling, principal-name response handling, and SMB/TCP plus NDR/NDR64 coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_mgmt.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_mimilib.py -->
# sources/user-network-fs/impacket/tests/dcerpc/test_mimilib.py

Purpose: tests Impacket's Mimikatz RPC compatibility helpers (`mimilib`) over TCP, including Diffie-Hellman key exchange, RC4 command encryption, command execution, and unbind.

Important APIs and functions: `MimiKatzTests` binds `mimilib.MSRPC_UUID_MIMIKATZ`, uses mapper TCP, and sets a long timeout. `get_dh_public_key()` builds `MimiDiffeH`, `PUBLICKEYBLOB`, and `MIMI_PUBLICKEY`. `get_handle_key()` calls `hMimiBind`, computes the shared secret, and returns a handle plus the last 16 bytes as key material. Tests cover raw/helper `MimiBind`, raw/helper `MimiCommand`, and raw `MimiUnbind`. Authenticated subclasses add integrity and privacy variants.

Control flow: bind tests send the public key and assert zero error plus RC4 session type. Command tests encrypt `token::whoami` as UTF-16LE with RC4 using reversed key bytes, send it, assert encrypted result length, and decrypt the result locally. Unbind sends the handle from the bind handshake.

State and persistence behavior: command execution depends on a live remote Mimikatz RPC server and may inspect security-token context. The default command is read-only, but the protocol can execute sensitive commands.

Dependencies and integration points: depends on `Cryptodome.Cipher.ARC4`, `mimilib`, endpoint mapper, and a target exposing the Mimikatz RPC interface. Authn subclasses reuse the same test methods with RPC authentication levels.

Risks: highly sensitive security-tool integration. The decrypted command output is not asserted. Importing `Cryptodome` at module import time makes the whole file fail if pycryptodomex is missing. Must only run in authorized lab environments.

Test signals: validates custom protocol structures, DH public-key serialization, shared secret derivation, RC4 command/result framing, handle lifecycle, and behavior under unauthenticated/authenticated RPC levels.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_mimilib.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_nrpc.py -->
# sources/user-network-fs/impacket/tests/dcerpc/test_nrpc.py

Purpose: extensive Netlogon Remote Protocol (`nrpc`) coverage for domain controller discovery, site/trust queries, secure-channel challenge/authentication, logon validation, database sync calls, and control APIs.

Important APIs and functions: `NRPCTests` uses `nrpc.MSRPC_UUID_NRPC`, `authn=True`, and `machine_account=True`. `authenticate()` performs `hNetrServerReqChallenge`, computes a strong session key with the machine account NT hash, computes the client credential, and calls `hNetrServerAuthenticate3`. `update_authenticator()` returns a Netlogon authenticator from the stored credential/session key. Tests cover many raw/helper `Dsr*`, `Netr*`, trust, digest, control, and UAS operations.

Control flow: discovery tests issue unauthenticated/authenticated Netlogon location and site requests. Secure-channel tests explicitly build challenge/authenticate requests for Authenticate, Authenticate2, and Authenticate3. Xfailed privileged tests call `authenticate()` before password, domain info, capability, database sync, forest trust, trust info, and send-to-SAM paths. SamLogon tests encrypt LM/NT OWF password values with RC4 over the session key and submit interactive logon structures.

State and persistence behavior: most operations are read/query or expected access-denied. Password-set and database-sync paths are xfailed and expected to fail; if they unexpectedly ran with privilege they could be sensitive. `DsrDeregisterDnsHostRecords`, service bits, controls, and send-to-SAM are also sensitive but coded to expect denial/not-supported. No cleanup is needed for successful read-only calls.

Dependencies and integration points: depends on machine-account credentials from remote config, Netlogon named pipe or endpoint-mapped TCP, `ntlm` hash functions, optional `Cryptodome.Cipher.ARC4`, and modern domain controller Netlogon hardening behavior.

Risks: many assertions are environment-specific expected errors (`STATUS_DOWNGRADE_DETECTED`, `STATUS_NOT_SUPPORTED`, `rpc_s_access_denied`, `ERROR_NO_SUCH_DOMAIN`). The TODO notes that secure RPC session establishment is incomplete, and Zerologon patching causes xfails. Machine account hash handling is sensitive. Some calls use hardcoded test strings and RIDs.

Test signals: verifies Netlogon structure marshalling, challenge/credential computation, helper parity, domain/site/trust discovery, expected post-hardening failures, encrypted SamLogon payload construction, and transport coverage over SMB and TCP.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_nrpc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_par.py -->
# sources/user-network-fs/impacket/tests/dcerpc/test_par.py

Purpose: tests Print System Asynchronous Remote Protocol (`par`) helper/raw calls over endpoint-mapped TCP.

Important APIs and functions: `PARTests` binds `par.MSRPC_UUID_PAR`, uses packet privacy, and exercises raw/helper `RpcAsyncEnumPrinters`, `RpcAsyncEnumPrinterDrivers`, and `RpcAsyncGetPrinterDriverDirectory`. Raw calls pass `par.MSRPC_UUID_WINSPOOL` as the request UUID where required.

Control flow: enum printers sends a minimal level-0 request. Driver enumeration and driver-directory tests intentionally pass zero buffer and assert `ERROR_INSUFFICIENT_BUFFER`; helper forms perform the helper-managed buffer flow and dump responses.

State and persistence behavior: read-only printer/spooler queries. No printers or drivers are changed.

Dependencies and integration points: depends on spooler service, PAR endpoint mapper registration, Impacket `par` structures, and Windows print subsystem behavior.

Risks: spooler may be disabled or hardened. `ERROR_INSUFFICIENT_BUFFER` is an expected first-call signal; changed server behavior can alter test results. Not-yet-covered add/open/close printer operations would carry more state risk.

Test signals: validates async print RPC marshalling, helper UUID selection, insufficient-buffer error handling, and NDR/NDR64 TCP compatibility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_par.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_raa.py -->
# sources/user-network-fs/impacket/tests/dcerpc/test_raa.py

Purpose: tests Remote Authorization API (`raa`) context creation, compound contexts, access checks, context information queries, and claim/SID modification reachability.

Important APIs and functions: `RAATests` binds `raa.MSRPC_UUID_RAA` over TCP with packet privacy. `get_account_sid()` resolves the configured username to a SID through LSAT/LSAD over `\PIPE\lsarpc` and caches it at class level. `setUp()` uses `epm.hept_lookup()` to find the RAA TCP port from a non-nil object UUID registration. `build_security_descriptor()` constructs a self-relative security descriptor with one allow ACE granting `GENERIC_ALL` to a SID. Tests cover raw/helper `AuthzrInitializeContextFromSid`, `AuthzrFreeContext`, `AuthzrInitializeCompoundContext`, `AuthzrAccessCheck`, `AuthzGetInformationFromContext`, `AuthzrModifyClaims`, and `AuthzrModifySids`.

Control flow: setup resolves account SID and dynamic port before each test. Context tests create one or two authorization contexts, call the target operation, then free all handles. Access-check tests create a context, build an in-memory security descriptor, pass it as `SR_SD`, and free the context. Modify-claims/SIDs tests assert a server-side session error while ensuring the call reaches the server.

State and persistence behavior: remote state is not changed. It creates transient authorization context handles and frees them. Class-level `account_sid` cache persists within the test process.

Dependencies and integration points: integrates EPM, LSAT/LSAD SID lookup, LDAP security descriptor classes, and RAA object UUID request dispatch. Requires RAA registered over TCP and sufficient rights to resolve the user's SID.

Risks: setup skips tests if RAA is not registered or SID resolution fails. Security descriptor construction is low-level and can regress with LDAP type changes. The override calls `super(DCERPCTests, self).setUp()`, which intentionally bypasses `DCERPCTests.setUp()` and may be brittle.

Test signals: validates dynamic object-endpoint lookup, SID resolution, self-relative security descriptor encoding, authorization context lifecycle, compound context handling, access-check replies, and expected errors for modify operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_raa.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_rprn.py -->
# sources/user-network-fs/impacket/tests/dcerpc/test_rprn.py

Purpose: tests Print Spooler Remote Protocol (`rprn`) named-pipe operations for printer enumeration, open/close, driver-directory lookup, and change notification setup.

Important APIs and functions: `RPRNTests` binds `rprn.MSRPC_UUID_RPRN` over `\PIPE\spoolss`. It covers raw/helper `RpcEnumPrinters`, `RpcOpenPrinter`, `RpcGetPrinterDriverDirectory`, `RpcClosePrinter`, `RpcOpenPrinterEx`, and `RpcRemoteFindFirstPrinterChangeNotificationEx`.

Control flow: `RpcEnumPrinters` uses the normal two-step insufficient-buffer pattern: first call expects `ERROR_INSUFFICIENT_BUFFER`, extracts `pcbNeeded`, allocates a dummy buffer, then retries. Open/close tests obtain server handles for `\\<machine>`. `RpcOpenPrinterEx` builds a `SPLCLIENT_CONTAINER` with machine/user/build/architecture fields. Notification tests open the printer and expect `ERROR_INVALID_HANDLE` for remote change notification.

State and persistence behavior: read-only spooler handle and enumeration operations. No printer configuration is changed. Handles are not always closed after open tests.

Dependencies and integration points: depends on spooler service, named-pipe RPC, Impacket `rprn` helpers, and remote config identity. `hexdump()` is used to print returned printer buffers.

Risks: spooler service may be disabled. Change notification behavior can vary and has security-sensitive history, so run only in controlled environments. Some tests request broad access flags before expecting failure.

Test signals: validates spooler NDR structures, buffer sizing, helper/raw parity, client-info union encoding, handle operations, and NDR64 support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_rprn.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_rrp.py -->
# sources/user-network-fs/impacket/tests/dcerpc/test_rrp.py

Purpose: broad Remote Registry Protocol (`rrp`) integration tests covering root-key opens, key/value create/query/delete, enumeration, security, save/restore/load/unload, performance hives, and multi-value queries.

Important APIs and functions: `RRPTests` binds `rrp.MSRPC_UUID_RRP` over `\PIPE\winreg`. `connect_scmr()`, `open_scmanager()`, and `start_rrp_service()` use SCMR over `\pipe\svcctl` to start `RemoteRegistry` before RRP connection. `open_local_machine()` opens HKLM with WOW64 and enumerate rights. Tests cover many raw/helper APIs including `OpenClassesRoot`, `OpenCurrentUser`, `OpenLocalMachine`, `OpenPerformanceData`, `OpenUsers`, `BaseRegCloseKey`, `BaseRegCreateKey`, `BaseRegSetValue`, `BaseRegDeleteValue`, `BaseRegDeleteKey`, `BaseRegEnumKey`, `BaseRegEnumValue`, `BaseRegFlushKey`, `BaseRegGetKeySecurity`, `BaseRegOpenKey`, `BaseRegQueryInfoKey`, `BaseRegQueryValue`, `BaseRegReplaceKey`, `BaseRegRestoreKey`, `BaseRegSaveKey`, `BaseRegSaveKeyEx`, `BaseRegGetVersion`, `OpenCurrentConfig`, `OpenPerformanceText`, `OpenPerformanceNlsText`, `BaseRegQueryMultipleValues`, `BaseRegQueryMultipleValues2`, `BaseRegDeleteKeyEx`, `BaseRegLoadKey`, and `BaseRegUnLoadKey`.

Control flow: setup initializes `rrp_started=False`. `connect()` starts RemoteRegistry once per test via SCMR, then delegates to `DCERPCTests.connect()`. Mutation tests create `BETO` key and `BETO2` value under HKCR, query the value, delete value/key, and assert round-trip data. Save/load tests save hives to files under `%SystemRoot%\System32`, load them under temporary subkeys, unload, and delete files over SMB ADMIN$.

State and persistence behavior: high statefulness. It starts a Windows service, creates/deletes registry keys and values, saves hive files (`BETUSFILE2`, `SEC`) on the remote admin share, loads/unloads a temporary hive key, and opens sensitive keys including `SECURITY` and `SYSTEM\CurrentControlSet\Control\Lsa\JD`. Cleanup exists for most generated artifacts but is not consistently protected by `finally`.

Dependencies and integration points: integrates SCMR service-control RPC, RRP named-pipe RPC, SMB file deletion through the underlying transport, remote admin privileges, RemoteRegistry service, and registry security policy.

Risks: should run only on disposable or dedicated test systems. Failed cleanup can leave registry keys, loaded hives, files in `System32`, or a started RemoteRegistry service. Querying sensitive LSA/SECURITY hives requires high privilege. Some tests use broad `MAXIMUM_ALLOWED`; expected errors for replace/restore depend on file availability.

Test signals: strong coverage for RRP marshalling, helper parity, value encoding/decoding, buffer fields, WOW64 access masks, security descriptors, hive save/load paths, SMB integration for cleanup, and NDR/NDR64 compatibility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_rrp.py -->

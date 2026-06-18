# Research Group subset-b-009643

This grouped report covers Impacket SMB, NetBIOS, NTLM, DCERPC, RPC-over-HTTP, SPNEGO, secretsdump, and embedded SMB server tests under `sources/user-network-fs/impacket/tests/SMB_RPC`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/SMB_RPC/test_ndr.py -->
# sources/user-network-fs/impacket/tests/SMB_RPC/test_ndr.py

## Purpose

`test_ndr.py` is a local golden-packet regression suite for Impacket's DCE/RPC NDR and NDR64 marshalling layer. It feeds captured or hand-built byte streams into generated RPC structures, serializes them back with `getData()`, and checks byte equality or packed length preservation for complex structures whose alignment and referent handling are easy to regress.

## Important APIs, Types, and Functions

The single test class is `NDRTests(unittest.TestCase)`. It defines `NDR64Syntax` with `uuidtup_to_bin(('71710533-BEBA-4937-8319-B5DBEF9CCC36', '1.0'))` and uses that transfer syntax where NDR64 packing matters.

The suite exercises DRSUAPI responses (`DRSCrackNamesResponse`, `DRSDomainControllerInfoResponse`, `DRSGetNCChangesResponse`), SAMR calls (`SamrLookupNamesInDomainResponse`, `SamrLookupIdsInDomain`), LSAT responses (`LsarGetUserNameResponse`, `LsarLookupSids2Response`), RRP registry calls (`BaseRegEnumValueResponse`, `BaseRegGetKeySecurityResponse`, `BaseRegQueryMultipleValues`, `BaseRegQueryValueResponse`, `RVALENT`, `REG_SZ`), SCMR (`RCreateServiceWResponse`), DCOM runtime (`ComplexPing`), SRVS (`NetrShareEnum`), and endpoint mapper types (`ept_lookupResponse`, `ept_map`, `EPMTower`, floor structures). Utility dependencies include `NULL`, `dtypes.ULONG`, `string_to_bin`, and diagnostic `hexdump`.

## Control Flow

Most tests follow the same parse-roundtrip pattern: assign a captured byte literal, instantiate the corresponding RPC object, call `fromString()`, optionally dump the decoded structure, call `getData()`, and assert exact equality or identical length. Exact equality is used where padding and all output bytes are expected to be stable; length equality is used for cases where semantically equivalent repacking may differ in filler bytes or generated referents.

Several tests construct requests from fields rather than only parsing captures. `test_10` builds `srvs.NetrShareEnum` under NDR64 with null server and resume handles. `test_12` builds an endpoint mapper tower from interface, data representation, protocol, port, and IPv4 host floors and stores the tower in `epm.ept_map(isNDR64=True)`. `test_14` creates a `SamrLookupIdsInDomain` request with a domain handle, count, two `ULONG` relative IDs, and an explicit conformant-array maximum count. `test_15` prepares three `RVALENT` registry value descriptors and a value buffer before switching a `BaseRegQueryMultipleValues` request to NDR64 and parsing a captured request.

## State and Persistence Behavior

The file has no persistent external state. State is local to each test's RPC object and nested NDR field containers. The main mutable behavior under test is `fromString()` populating nested fields, `changeTransferSyntax()` switching NDR64 layout rules, and list-like NDR arrays receiving appended entries. The tests print and dump large packets to stdout, which can produce noisy logs but does not affect assertions.

## Dependencies and Integration Points

This test module integrates many generated `impacket.dcerpc.v5` endpoint modules with the shared NDR engine. It is a broad integration signal for conformant varying strings, pointers, arrays, unions, tower floors, security descriptors, SIDs, handles, and NDR64 alignment. It also touches UUID conversion and low-level data-type wrappers that are shared by remote DCERPC clients.

## Risks and Edge Cases

The embedded byte literals are large captures, so maintenance is difficult and failures can be noisy. Some assertions compare only lengths, which can miss byte-level regressions in padding or referent values. The suite relies on captured Windows-like payloads with magic filler bytes, wide strings, SIDs, endpoint towers, OIDs, and registry value lists; a seemingly unrelated change in NDR packing can break many tests at once. There is also a likely typo in `test_15` where `item1['ve_valueptr']` is assigned twice instead of setting `item2['ve_valueptr']`; the later `fromString()` call means the constructed request fields mainly document intent rather than drive final assertions.

## Test Signals

Strong signals are exact round trips for DRSUAPI, SAMR, LSAT, RRP, SCMR, DCOMRT, and endpoint mapper responses. Length-only signals catch gross NDR64 and tower-size regressions but should be supplemented by byte equality where the marshaller is expected to be deterministic. Running this file is useful after changes to `impacket.dcerpc.v5.ndr`, NDR64 transfer syntax handling, conformant arrays, pointer referents, and endpoint mapper tower serialization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/SMB_RPC/test_ndr.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/SMB_RPC/test_nmb.py -->
# sources/user-network-fs/impacket/tests/SMB_RPC/test_nmb.py

## Purpose

`test_nmb.py` validates Impacket NetBIOS name-service helpers locally with mocked packets and remotely against a configured Windows/Samba target. It covers NetBIOS name encode/decode behavior, node-status parsing, name lookups, host address resolution, and name registration request handling.

## Important APIs, Types, and Functions

The file defines `NMBLocalTests` and `NMBRemoteTests`. Local tests use `nmb.encode_name`, `nmb.decode_name`, `nmb.NetBIOS`, `nmb.NAME_SERVICE_PACKET`, `getnetbiosname`, `getnodestatus`, `gethostbyname`, and `name_query_request`. Remote tests inherit `RemoteTestCase`, call `set_transport_config()`, and use live `NetBIOS` calls against `self.machine` and `self.serverName`. `binascii.unhexlify` provides canned packet bytes, and `hexdump` is used for diagnostics.

## Control Flow

Local tests replace `NetBIOS.send` with a `send_hook` that returns `NAME_SERVICE_PACKET(mock)`, so each API consumes deterministic encoded packet bytes without sending UDP traffic. `test_encodedecodename` verifies that a long name is truncated to the NetBIOS 15-character payload. `test_getnetbiosname` parses a mocked node-status response into a server name. `test_getnodestatus` checks individual name table records. `test_gethostbyname` sets the name server and asserts the parsed IPv4 address. `test_name_query_request` directly exercises a name query response.

Remote tests repeat encode/decode and live network operations. They query the configured target's NetBIOS name, node status, host records, and registration behavior. The name registration test tolerates exceptions only when the message indicates a NetBIOS-level response; unrelated exceptions are re-raised.

## State and Persistence Behavior

Local tests keep all state in mock packet data and a `NetBIOS` instance whose `send` method and name server may be modified. Remote tests depend on `RemoteTestCase` state such as `machine`, `serverName`, and transport configuration. No files are written. Remote name registration may interact with the target's NetBIOS name service, but the test uses a throwaway name and catches expected NetBIOS errors.

## Dependencies and Integration Points

The module depends on `pytest.mark.remote`, Python `unittest`, the repository `tests.RemoteTestCase`, and `impacket.nmb`. It is an integration point between the packet structure parser, NetBIOS name encoding rules, and the higher-level query methods used by SMB discovery and connection setup.

## Risks and Edge Cases

The local tests depend on opaque hex captures, so packet-format intent is not obvious from the literals. Remote tests require a reachable target with NetBIOS services enabled, correct `RemoteTestCase` credentials/configuration, and network conditions that allow name service traffic. Encode/decode coverage explicitly checks long-name truncation, but the TODO notes that scope support is not fixed. Some remote tests print values without assertions, so they function more as smoke tests than strict correctness checks.

## Test Signals

Useful local signals are deterministic parsing of node-status and query responses and name truncation behavior. Useful remote signals are successful live lookups and tolerated NetBIOS registration errors. Changes to `impacket.nmb`, NetBIOS packet layouts, or SMB name resolution should run the local tests first and remote tests when a configured SMB/NetBIOS target is available.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/SMB_RPC/test_nmb.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/SMB_RPC/test_ntlm.py -->
# sources/user-network-fs/impacket/tests/SMB_RPC/test_ntlm.py

## Purpose

`test_ntlm.py` is a local protocol-vector suite for Impacket's NTLM implementation. It checks NTLMv1, NTLMv1 with extended session security, NTLMv2, message sealing/signing, authenticate-message packing, AV pair container behavior, and negotiate-message version-field packing.

## Important APIs, Types, and Functions

The only class is `NTLMTests(unittest.TestCase)`. `setUp()` enables `ntlm.TEST_CASE`, fixes deterministic user/domain/password/server/workstation values, session keys, timestamp, client and server challenges, negotiate flags, sequence number, nonce, and UTF-16LE plaintext.

The tests exercise `LMOWFv1`, `NTOWFv1`, `NTOWFv2`, `computeResponseNTLMv1`, `computeResponseNTLMv2`, `KXKEY`, `generateEncryptedSessionKey`, `NTLMAuthChallengeResponse`, `SIGNKEY`, `SEALKEY`, `SEAL`, `AV_PAIRS`, `NTLMAuthNegotiate`, and `VERSION`. `Cryptodome.Cipher.ARC4` is used to reproduce RC4 sealing behavior.

## Control Flow

`test_ntlmv1` disables NTLMv2 and follows Microsoft-style examples: derive LM and NT one-way functions, compute NTLMv1 responses and session base keys, derive key-exchange keys, encrypt a deterministic exported session key, pack an authenticate message, and seal/sign a UTF-16LE plaintext. It then repeats a branch with extended session security and client challenge. Several known-vector assertions are active, while some TODO assertions remain commented out for cases that were not matching expected vectors.

`test_ntlmv2` enables NTLMv2, builds target-info AV bytes for domain and server names, computes NTOWFv2/LMOWFv2, responses, session base key, encrypted session key, authenticate message, signing and sealing keys, sealed payload, and signature. `test_av_pairs_container_protocol` verifies dictionary-like membership and iteration for `AV_PAIRS`. `test_refactor_negotiate_message` packs and parses negotiate messages without and with `os_version`, asserts the version flag behavior, and ensures setting `NTLMSSP_NEGOTIATE_VERSION` without an `os_version` raises.

## State and Persistence Behavior

The test intentionally mutates module globals `ntlm.TEST_CASE` and `ntlm.USE_NTLMv2`, so test isolation depends on `setUp()` resetting the deterministic mode and each method setting NTLMv1/v2 mode explicitly. There is no filesystem or network persistence. RC4 cipher instances are local and stateful for each sealing operation.

## Dependencies and Integration Points

This file sits directly on top of `impacket.ntlm` and indirectly validates behavior consumed by SMB, SPNEGO, DCERPC authentication, and secretsdump. It depends on `six.b` for byte compatibility, `struct` for flag display, and PyCryptodome's ARC4 cipher. The expected values are protocol-vector integration points for cryptographic compatibility.

## Risks and Edge Cases

Because this file manipulates NTLM global flags, failures or future parallelization could leak mode into other tests if not isolated by the runner. Some TODO vectors remain commented, which means those code paths are executed and printed but not fully verified. Deterministic test-case mode suppresses time/random variation and is essential for reproducible NTLMv2 output. The negotiate-message tests protect a subtle refactor risk: emitting the version flag without version bytes creates malformed messages.

## Test Signals

High-value signals are exact known-vector matches for one-way functions, response blobs, session keys, authenticate messages, signing/sealing keys, sealed data, and signatures. The file should be run after changes to NTLM crypto, flag handling, AV pairs, message layout calculations, SPNEGO integration, or SMB/DCERPC authentication code.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/SMB_RPC/test_ntlm.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/SMB_RPC/test_rpch.py -->
# sources/user-network-fs/impacket/tests/SMB_RPC/test_rpch.py

## Purpose

`test_rpch.py` validates RPC over HTTP support. It combines one remote smoke test against `ncacn_http` endpoint mapper with local golden tests for RTS packet parsing and command serialization.

## Important APIs, Types, and Functions

`RPCHTest(RemoteTestCase, unittest.TestCase)` uses `transport.DCERPCTransportFactory`, a `dce` object, `epm.MSRPC_UUID_PORTMAP`, `epm.ept_lookup`, and endpoint mapper constants. `RPCHLocalTest` uses `rpch.RTSHeader`, `rpch.COMMANDS`, and specific RTS command structures such as `Version`, `ReceiveWindowSize`, `Cookie`, `ConnectionTimeout`, `Ack`, `RTSCookie`, and `ChannelLifetime`. `struct.unpack('<L', ...)` decodes command IDs from raw PDU data.

## Control Flow

The remote test builds `ncacn_http:<machine>`, connects without authentication, binds to endpoint mapper, sends an `ept_lookup` request, disconnects, reconnects, and repeats the same request. This primarily checks connection setup and reconnect behavior for RPC over HTTP v1.

Local tests parse captured RTS PDUs. Each test constructs a byte string for a specific scenario, instantiates `RTSHeader`, reads `pduData` and `NumberOfCommands`, then loops over commands by reading the command type and instantiating the matching class from `rpch.COMMANDS`. Assertions check flags, fragment length, pdu data length, and command `getData()` round trips. Scenarios include CONN/A1, CONN/A3, PING, CONN/C2, FlowControlAckWithDestination, CONN/B2 IPv4, and CONN/A2.

## State and Persistence Behavior

The local tests are stateless beyond parsed packet objects and command lists. The remote test depends on `RemoteTestCase` configuration and opens real RPC-over-HTTP connections, but it does not write files or modify persistent target state. The reconnect sequence intentionally creates two connection lifecycles in one test.

## Dependencies and Integration Points

The module depends on `pytest.mark.remote`, `RemoteTestCase`, `impacket.dcerpc.v5.transport`, `epm`, and `rpch`. It integrates the RTS parser with DCE/RPC transport creation and endpoint mapper requests, exercising both low-level command structures and high-level transport behavior.

## Risks and Edge Cases

The local parsing loop trusts the command type lookup and command length calculations; an incorrect command length can desynchronize later commands. Captured RTS packets include channel flags, cookies, receive windows, timeouts, flow-control acknowledgements, and partially noted IPv4 address padding behavior. The remote test requires an RPC over HTTP endpoint to be exposed and may fail in environments where the service is disabled or firewalled.

## Test Signals

Local signals are exact `getData()` matches for selected RTS commands and expected header flags/lengths. Remote signal is successful unauthenticated connect/bind/request/disconnect/reconnect over `ncacn_http`. This file should be run after modifications to `rpch.py`, RTS command definitions, DCE/RPC HTTP transport state, and endpoint mapper transport selection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/SMB_RPC/test_rpch.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/SMB_RPC/test_rpcrt.py -->
# sources/user-network-fs/impacket/tests/SMB_RPC/test_rpcrt.py

## Purpose

`test_rpcrt.py` is a remote integration matrix for Impacket's DCE/RPC runtime engine across TCP and SMB named-pipe transports. It verifies connection setup, credential propagation, NTLM and Kerberos authentication, hash and AES key authentication, transport and DCE fragmentation, packet integrity, packet privacy, anonymous behavior, and large-request fragmentation.

## Important APIs, Types, and Functions

The core class is `RPCRTTests(RemoteTestCase)`, with concrete `RPCRTTestsTCPTransport` and `RPCRTTestsSMBTransport` subclasses marked remote. The central helper `connectDCE()` creates a transport from `self.stringBinding`, sets credentials and Kerberos state when supported, sets transport and DCE fragment sizes, sets remote name/host, obtains a DCE object, optionally propagates credentials to DCE auth, connects, sets auth type and level, and binds to the requested interface.

The suite uses `transport.DCERPCTransportFactory`, `epm.hept_lookup`, `epm.ept_lookup`, endpoint mapper UUIDs, SAMR calls, `NDRCALL`, `RPC_UNICODE_STRING`, and RPC auth constants including `RPC_C_AUTHN_WINNT`, `RPC_C_AUTHN_GSS_NEGOTIATE`, `RPC_C_AUTHN_LEVEL_NONE`, `RPC_C_AUTHN_LEVEL_PKT_INTEGRITY`, and `RPC_C_AUTHN_LEVEL_PKT_PRIVACY`.

## Control Flow

Most tests call `connectDCE()` with a particular credential/auth combination, build an endpoint mapper lookup request, send one or two `dce.request()` calls, optionally dump the response, and disconnect. The matrix covers password, LM/NT hash, Kerberos password, Kerberos hash, AES128, AES256, packet integrity, packet privacy, and fragment-size settings.

`test_bigRequestMustFragment` maps SAMR over TCP, binds with Kerberos packet privacy, sends `SamrConnect`, enumerates domains, then sends an intentionally large `SamrLookupDomainInSamServer` name to force fragmentation. It treats `STATUS_NO_SUCH_DOMAIN` as expected after the transport-level behavior succeeds. Anonymous packet integrity/privacy tests tolerate `STATUS_ACCESS_DENIED` only for SMB named-pipe bindings.

## State and Persistence Behavior

The tests are live remote tests and depend on `RemoteTestCase` fields for target, credentials, hashes, AES keys, server name, and domain. `connectDCE()` mutates transport and DCE authentication state. `test_bigRequestMustFragment` temporarily replaces `self.stringBinding` with a SAMR binding and restores it before continuing. No local files are written, and remote state is limited to reads/queries against endpoint mapper and SAMR.

## Dependencies and Integration Points

This module is one of the strongest integration tests for `impacket.dcerpc.v5.rpcrt`, transport factories, SMB named-pipe transport, TCP transport, SPNEGO/NTLM/Kerberos authentication, fragmentation, sealing/signing, and endpoint-specific NDR calls. It also depends on remote infrastructure that supports the tested protocols and credentials.

## Risks and Edge Cases

The matrix is environment-sensitive: unsupported dialects, missing AES keys, Kerberos/SPN configuration, firewalls, endpoint availability, or target policy can cause failures unrelated to code regressions. Packet privacy/integrity failures may appear only on the second request because sequence numbers and verifier state advance. Fragmentation tests deliberately use tiny fragment sizes and large SAMR names to exercise boundary behavior. Anonymous access behavior differs between TCP and named-pipe transports, and the test encodes that distinction.

## Test Signals

Passing signals indicate that DCE bind, auth negotiation, signing/sealing, request sequencing, fragmentation, and disconnect paths work across `ncacn_ip_tcp` and `ncacn_np`. This file is critical after changes to `rpcrt.py`, transport credential handling, Kerberos/NTLM auth providers, packet privacy/integrity implementation, or DCE fragmentation logic.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/SMB_RPC/test_rpcrt.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/SMB_RPC/test_secretsdump.py -->
# sources/user-network-fs/impacket/tests/SMB_RPC/test_secretsdump.py

## Purpose

`test_secretsdump.py` covers both local parsing edge cases for SAM supplemental credentials and remote end-to-end smoke tests for the `impacket.examples.secretsdump` workflow. It embeds a trimmed `DumpSecrets` driver modeled after the example tool so tests can run VSS, SAM/LSA, and DRSUAPI extraction paths from code.

## Important APIs, Types, and Functions

`DumpSecrets` coordinates `SMBConnection`, `LocalOperations`, `RemoteOperations`, `SAMHashes`, `LSASecrets`, and `NTDSHashes`. It supports password, hashes, Kerberos, AES128, VSS, DRSUAPI-only, single-user, history, output file, resume file, and execution-method options through the `Options` class.

`NTDSHashesUnitTests` directly exercises `samr.unpack_user_properties`, `samr.USER_PROPERTY`, and the private `NTDSHashes.__decryptSupplementalInfo` path by constructing an `NTDSHashes` instance with `object.__new__` and setting private attributes needed for decryption. `SecretsDumpTests` defines remote scenarios for VSS with history, DRSUAPI for one administrator account, and full DRSUAPI.

## Control Flow

`DumpSecrets.dump()` branches between local hive mode and remote mode. Local mode derives the boot key from a SYSTEM hive or supplied bootkey. Remote mode attempts SMB login, creates `RemoteOperations`, configures the execution method, optionally enables the registry, obtains the boot key, and checks LM hash policy. If SAM/LSA processing is allowed, it saves SAM and SECURITY hives, dumps SAM hashes, cached LSA hashes, and LSA secrets, and exports them when an output file is configured. It then chooses an NTDS source: VSS-saved NTDS, local NTDS file, or DRSUAPI remote extraction, constructs `NTDSHashes`, runs `dump()`, handles selected DRSUAPI errors, and always attempts cleanup.

The unit tests build binary supplemental-credential blobs to verify header-only handling, Reserved5 parsing, property-data slicing, padding exclusion, and explicit `struct.error` failures for missing Reserved5 or too-short fixed headers.

## State and Persistence Behavior

Remote tests can create substantial remote and local side effects through `RemoteOperations`, including registry service access, hive saves, NTDS retrieval, resume files, and cleanup calls. `DumpSecrets.cleanup()` calls `finish()` on remote operations and hash dumpers. KeyboardInterrupt handling can prompt about deleting resume-session files. Unit tests avoid normal constructors for `NTDSHashes`, manually populate private dictionaries/callbacks, and validate that no Kerberos keys or cleartext passwords are recorded for header-only supplemental credentials.

## Dependencies and Integration Points

The file integrates `secretsdump` example logic with SMB authentication, remote registry/VSS execution methods, SAMR supplemental credential parsing, SAM/LSA/NTDS hash extraction, and DRSUAPI replication. It relies on `RemoteTestCase` for configured domain-controller-like targets and credentials, and `pytest.mark.remote` for remote selection.

## Risks and Edge Cases

Remote secretsdump tests are high-impact and environment-sensitive. They require privileged credentials, a suitable domain controller or Windows target, working SMB/registry/DRSUAPI/VSS paths, and careful cleanup. Some methods are prefixed `aaaa_` rather than `test_`, so WMI/MMC VSS variants are present but not collected by normal unittest discovery. The wrapper logs many errors instead of failing immediately, so remote smoke tests may miss partial extraction failures unless logs are reviewed. The unit tests cover recently fragile blob boundary cases: Reserved5 must exist even when no credential properties are present, and declared lengths shorter than the fixed header must fail.

## Test Signals

Strong local signals are `unpack_user_properties` accepting valid header-only/property blobs and rejecting malformed lengths. Remote signals are completion of VSS/history and DRSUAPI dump paths without unhandled exceptions and with cleanup. This file should be run after changes to `examples/secretsdump.py`, `samr.unpack_user_properties`, `NTDSHashes` supplemental credential parsing, remote registry operations, or DRSUAPI extraction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/SMB_RPC/test_secretsdump.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/SMB_RPC/test_smb.py -->
# sources/user-network-fs/impacket/tests/SMB_RPC/test_smb.py

## Purpose

`test_smb.py` is a remote SMB client integration suite plus one local regression test. It validates `SMBConnection` behavior across SMB1, NetBIOS-session SMB1, SMB1 Unicode flags, SMB 2.0.2, SMB 2.1, and SMB 3.0 dialect preferences.

## Important APIs, Types, and Functions

`SMBTests(RemoteTestCase)` provides shared remote test methods and `create_connection()`. Concrete classes set `self.dialects`, `self.sessPort`, share/file/directory names, upload file, SMB1 flags, and AES-key transport configuration. The tests exercise `SMBConnection` APIs for negotiation, login, Kerberos login, reconnect, connect/disconnect tree, list path, create/open/close/delete/rename files, read/write, create/delete directories, metadata getters, upload/download callbacks, list shares, session key retrieval, and `queryInfo`.

The local `Test_Issue2099_SessionError_On_Truncated_Response` uses `unittest.mock` to patch `impacket.nmb.NetBIOSTCPSession` and `SMBSessionSetupAndX_Extended_Response_Data.fromString`, constructing minimal SMB negotiate and session-setup responses to assert parse errors become `SessionError`.

## Control Flow

Remote tests create a connection using manual negotiation for SMB1 and direct preferred dialects for SMB2/3. Each test logs in with password, hashes, Kerberos hashes, Kerberos password, or AES as appropriate, performs an SMB operation against the configured administrative share, asserts returned credentials or metadata when applicable, and logs off or closes the connection. File I/O tests create remote files, write 65,535 bytes, read until complete, rename/delete, upload a local `impacket/nt_errors.py`, download to a temporary file, and delete remote artifacts.

The truncated-response regression builds a fake session that returns a valid negotiate packet and a session setup packet whose data parser is forced to raise either `ValueError` or `struct.error`. It asserts `SMBConnection(...).login(...)` raises Impacket's `SessionError` variants rather than exposing raw parser exceptions.

## State and Persistence Behavior

Remote tests mutate the configured share by creating files and directories such as `/TEST` and `/BETO`, then deleting them. They open sockets and explicitly test socket closure with `select`. Reconnect tests preserve stored credentials across logoff/reconnect. The upload/download test creates and deletes a local `impacket/nt_errors.py2` file. The local regression test uses in-memory packet bytes and mocks only, with no network or filesystem dependency.

## Dependencies and Integration Points

The file depends on `RemoteTestCase`, optional `pytest.mark.remote`, `SMBConnection`, `SessionError`, `impacket.smbconnection.smb`, SMB2 dialect constants, `nt_errors`, and `nmb` session ports. It is a broad integration point for SMB negotiation, authentication, file APIs, tree handling, dialect-specific behavior, NetBIOS transport, and error translation.

## Risks and Edge Cases

The remote matrix is sensitive to target OS and dialect support; the file notes Windows 8 limitations when switching SMB2/3 dialects against one machine. Tests operate on administrative shares and require cleanup to avoid stale files. Some methods assume the configured share is writable and that `impacket/nt_errors.py` exists relative to the test working directory. `test_manualNego` calls negotiation on a connection that may already be manually negotiated for SMB1, which makes dialect state important. The local regression protects against malformed server responses producing raw parser exceptions in authentication paths.

## Test Signals

Passing remote tests signal working SMB connection lifecycle, auth variants, dialect selection, file/directory operations, metadata, reconnect credential persistence, and socket closure. The local regression is a targeted signal for issue 2099: truncated session setup responses must raise `SessionError`. Run this file after changes to `smbconnection.py`, `smb.py`, SMB2/3 dialect negotiation, NetBIOS session handling, or file operation wrappers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/SMB_RPC/test_smb.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/SMB_RPC/test_smbserver.py -->
# sources/user-network-fs/impacket/tests/SMB_RPC/test_smbserver.py

## Purpose

`test_smbserver.py` provides local unit and pseudo-functional coverage for Impacket's embedded SMB server. It checks path normalization and file-jail enforcement, then starts `SimpleSMBServer` on localhost and drives it with Impacket's own `SMBConnection` client for authentication, share browsing, file I/O, directory operations, path traversal blocking, Unicode names, SMB1/SMB2 behavior, and server shutdown.

## Important APIs, Types, and Functions

`StoppableMixin` overrides `serve_forever`, `close_request`, and `get_request` so the test server can exit cleanly from a thread. `SMBSERVERForTests` combines the mixin with `SMBSERVER`. `SMBServerUnitTests` covers `normalize_path` and `isInFileJail`.

`SimpleSMBServerFuncTests` defines the shared server/client fixture. It uses `SimpleSMBServer`, `SMBConnection`, `SessionError`, `compute_lmhash`, `compute_nthash`, `assertRaisesRegex`, `assertCountEqual`, `StringIO`, and `BytesIO`. Subclasses toggle `server_smb2_support` and client preferred dialect: `SimpleSMBServer2FuncTestsClientFallBack` enables SMB2 server support while forcing an SMB1 client dialect, and `SimpleSMBServer2FuncTests` enables SMB2 with default client negotiation and adds directory deletion coverage.

## Control Flow

`setUp()` creates a jail directory, a directory inside the jail, unjailed control paths, normal and Unicode files, and initial content. `tearDown()` removes files/directories and stops the server. `get_smbserver()` adds credentials and a share unless requested otherwise, and applies SMB2 support. `start_smbserver()` runs `server.start()` in a daemon thread due to a Python 3.13 multiprocessing issue. `stop_smbserver()` calls server stop methods, clears `must_serve`, sleeps briefly, and joins the thread.

Functional tests start a fresh server, create a client, assert unauthenticated access failures, authenticate, perform the target operation, assert filesystem results or returned SMB metadata, and close the client. Operations include valid and invalid password/hash login, Unicode username login, share listing, tree connect/disconnect, listing files and patterns, put/get/delete/rename files, create/delete directories, open/close file handles, and query info. Path traversal attempts using `..` are expected to fail with `STATUS_OBJECT_PATH_SYNTAX_BAD` and leave unjailed files untouched.

## State and Persistence Behavior

The tests create and delete real local files/directories in the current working directory (`jail_dir`, `unjailed_file`, and related names) and bind a localhost listener on port 1445. Server state includes credentials, shares, dialect support, connection/thread state, and `must_serve`. The fixture attempts cleanup in `tearDown`, but interrupted or failed runs can leave filesystem artifacts or an occupied port. The SMB2 class changes expected directory listing contents because SMB2 responses omit `.` and `..`.

## Dependencies and Integration Points

The file integrates `impacket.smbserver` with `impacket.smbconnection` through real socket traffic on localhost. It also checks lower-level path helper behavior directly. It depends on `six` for Python 2 compatibility helpers and skip behavior, Python threading/select/socket primitives, and the server classes' ability to accept a custom SMB server class.

## Risks and Edge Cases

Port 1445 conflicts can break the suite. Thread shutdown is timing-sensitive and uses a short sleep before join. Filesystem cleanup assumes directories are empty; a failed intermediate operation can affect later teardown. The jail tests are security-critical: traversal via list, put, get, delete, create directory, rename, open, and SMB2 delete directory must not touch unjailed paths. Unicode filename tests are skipped under Python 2. Some server command families remain listed as TODO, so this suite covers important but not exhaustive SMB server behavior.

## Test Signals

Strong signals are correct auth acceptance/rejection, access-denied responses before login, share listing including `IPC$`, file and directory operation success after login, query-info sizes, Unicode name support, clean local server shutdown, and consistent traversal blocking. Run this file after changes to `smbserver.py`, embedded server threading, path normalization/jail logic, SMB1/SMB2 command handlers, or `SMBConnection` client interoperability.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/SMB_RPC/test_smbserver.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/SMB_RPC/test_spnego.py -->
# sources/user-network-fs/impacket/tests/SMB_RPC/test_spnego.py

## Purpose

`test_spnego.py` is a compact local golden-byte suite for SPNEGO token parsing and packing in `impacket.smb`. It verifies `NegTokenInit` and `NegTokenResp` round trips for NTLMSSP negotiation payloads and explicit construction of a request-MIC response.

## Important APIs, Types, and Functions

The file defines one `unittest.TestCase` class named `Test`. `setUp()` stores six DER/ASN.1 SPNEGO byte strings: two `negTokenInit` values, three response values, and one constructed request-MIC response. Test methods use `smb.SPNEGO_NegTokenInit`, `smb.SPNEGO_NegTokenResp`, and `smb.TypesMech['NTLMSSP - Microsoft NTLM Security Support Provider']`.

## Control Flow

Five tests instantiate the appropriate SPNEGO token class, parse a stored byte string with `fromString()`, and assert that `getData()` returns the original bytes. `test_negTokenResp4` constructs a response by assigning `NegState` to `b'\x03'` and `SupportedMech` to the NTLMSSP mechanism OID, then asserts the packed output matches the stored DER bytes.

## State and Persistence Behavior

All state is local to the test instance and token objects. There is no network, filesystem, or global module mutation. The byte fixtures include embedded NTLMSSP negotiate/challenge/authenticate payloads but are treated as opaque SPNEGO token data.

## Dependencies and Integration Points

The suite depends only on `unittest` and `impacket.smb`. It integrates with SMB authentication because the SPNEGO helpers are used around NTLMSSP messages during extended-security negotiation. It also indirectly guards Impacket's ASN.1 length encoding for short and long-form SPNEGO structures.

## Risks and Edge Cases

Coverage is intentionally narrow but sensitive to byte-for-byte encoding. It exercises long-form lengths (`0x81`, `0x82`), optional fields, NTLMSSP mech OIDs, negState values, and response tokens with and without supported mechanism fields. The tests do not validate semantic contents of the nested NTLM messages beyond preserving the outer SPNEGO bytes.

## Test Signals

Passing tests indicate that SPNEGO token parsing is lossless for captured NTLMSSP negotiation flows and that constructing a request-MIC response emits the expected encoding. Run this file after changes to `SPNEGO_NegTokenInit`, `SPNEGO_NegTokenResp`, ASN.1 length handling, mechanism OID mapping, or SMB extended-security negotiation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/SMB_RPC/test_spnego.py -->

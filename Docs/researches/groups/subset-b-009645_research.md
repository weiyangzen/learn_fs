# Research Group: subset-b-009645

This grouped report covers the requested Impacket test files under `sources/user-network-fs/impacket/tests/dcerpc` and `sources/user-network-fs/impacket/tests/dot11`. Each section is source-tree aligned and can be split into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_samr.py -->
# sources/user-network-fs/impacket/tests/dcerpc/test_samr.py

## Purpose
This file is a remote integration test suite for Impacket's SAMR DCE/RPC implementation. It exercises both raw NDR request classes such as `SamrConnect`, `SamrOpenDomain`, `SamrQueryInformationUser2`, and convenience helpers such as `hSamrConnect`, `hSamrOpenUser`, and `hSamrSetInformationUser2`. Coverage spans server connection negotiation, domain lookup/open, user/group/alias enumeration, display information, object creation/deletion, membership management, security descriptors, password policy, and password-change calls.

## Important APIs, Types, and Functions
`SAMRTests` inherits `DCERPCTests`, binds `samr.MSRPC_UUID_SAMR`, requires authentication, and uses NTLM packet privacy. `get_domain_handle()` is the central helper: it connects to the SAM server, enumerates domains, looks up the first domain SID, and opens the domain with broad domain/server access masks. Tests directly instantiate many `impacket.dcerpc.v5.samr` request/structure types, including `RPC_SID`, `SAMPR_GROUP_INFO_BUFFER`, `SAMPR_ALIAS_INFO_BUFFER`, `SAMPR_PSID_ARRAY`, and `SAM_VALIDATE_INPUT_ARG`. Password-change tests also depend on `impacket.crypto` and `impacket.ntlm`.

## Control Flow
Most tests call `self.connect()`, derive a SAM server or domain handle, populate a request object, call `dce.request()`, and dump or assert the response. Paired raw/helper tests validate the same RPC path through low-level request classes and high-level `hSamr*` wrappers. Enumeration tests loop while `STATUS_MORE_ENTRIES` is returned and advance the `EnumerationContext`. Mutating tests usually query old values, set a temporary value, verify it with another query, then restore the previous value. Transport subclasses run the same test body over SMB named pipe and TCP, with NDR and NDR64 variants.

## State and Persistence Behavior
The suite mutates real SAM state on the configured remote target. It creates and deletes temporary users/aliases, changes domain password/logoff/OEM/replication fields, edits group/alias/user comments and names, adjusts group attributes, and performs password change flows. Several operations attempt to restore old values, but not all creation paths use `finally`, so failures may leave accounts, aliases, or modified metadata behind. The Unicode password path creates a random complex password containing non-ASCII characters before expecting a password policy failure.

## Dependencies and Integration Points
The file integrates with the shared DCE/RPC test harness in `tests.dcerpc`, the SAMR RPC definitions in `impacket.dcerpc.v5.samr`, shared DCE/RPC types in `dtypes`, NT status constants in `nt_errors`, NTLM hash helpers, and optional `Cryptodome.Cipher.ARC4`. It assumes a Windows SAM-compatible remote endpoint, Administrator and Guest RIDs, configured credentials on `DCERPCTests`, and sufficient privileges for many mutating operations.

## Risks
These are privileged destructive integration tests, not hermetic unit tests. Risks include persistent account or alias residue on failure, accidental modification of Administrator/user/domain fields, fragile assumptions about built-in RIDs and server names (`BETO`, `Administrator`, `Guest`), environment-specific status codes, and broad access masks that may fail under tighter policies. Some exception checks inspect stringified errors rather than numeric codes, which can be brittle across versions and locales.

## Test Signals
Signals include successful RPC marshalling/unmarshalling, expected `DCERPCSessionError` values such as `STATUS_NO_SUCH_ALIAS`, `STATUS_ACCESS_DENIED`, `STATUS_OBJECT_TYPE_MISMATCH`, `STATUS_INVALID_INFO_CLASS`, `STATUS_PASSWORD_RESTRICTION`, and `rpc_s_access_denied`, equality checks after set/query cycles, and round-trip SID/hash/password buffer behavior. The `pytest.mark.remote` classes signal that these tests require external infrastructure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_samr.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_scmr.py -->
# sources/user-network-fs/impacket/tests/dcerpc/test_scmr.py

## Purpose
This file validates Impacket's Service Control Manager Remote Protocol (`scmr`) implementation against a live Windows service controller. It tests service manager open/query/control calls, service creation/change/delete workflows, service configuration variants, failure-action encoding, enumeration APIs, lock handling, object security, display/key name lookup, and remote service start/stop behavior.

## Important APIs, Types, and Functions
`SCMRTests` binds `scmr.MSRPC_UUID_SCMR` and authenticates. `get_service_handle()` opens `ServicesActive` with service-manager and service permissions. `open_or_create_service()` opens `TESTSVC` or creates it with `hRCreateServiceW`. `changeServiceAndQuery()` wraps `hRChangeServiceConfigW` plus `hRQueryServiceConfigW` and verifies changed fields. `query_service_config2()` implements the standard insufficient-buffer retry pattern for `RQueryServiceConfig2W`; `query_failure_actions()` parses returned binary layout with `struct.unpack`. Tests use `SC_ACTION`, `SC_ACTIONS`, trigger structures, service status/config structures, and `NULL`.

## Control Flow
Tests connect to SCMR, obtain an SCM handle, then either query built-in services such as `PlugPlay`, `RemoteRegistry`, and `CryptSvc`, or create a temporary `TESTSVC`. Configuration tests build an `RChangeServiceConfig2W` request and mutate the discriminated union by setting both `dwInfoLevel` and `Union.tag`. Many calls intentionally first request a zero-sized buffer, capture `ERROR_MORE_DATA` or `ERROR_INSUFFICIENT_BUFFER`, then retry with `pcbBytesNeeded`. Transport subclasses run SMB named-pipe and TCP variants; TCP uses NTLM packet privacy.

## State and Persistence Behavior
The file creates, changes, starts, stops, and deletes real Windows services. `TESTSVC` is normally deleted and handles are closed after configuration tests, and the newer failure-action tests use `finally` for cleanup. Some older flows catch broad exceptions and perform manual deletion, while other service control calls may leave target services stopped or started depending on environmental behavior. `RControlServiceCall` attempts to stop `CryptSvc`, waits, and starts it again.

## Dependencies and Integration Points
Dependencies include `impacket.dcerpc.v5.scmr`, `impacket.crypto.encryptSecret` for service account password encryption on SMB, `impacket.uuid.string_to_bin` for service trigger GUIDs, `impacket.dcerpc.v5.ndr.NULL`, and the shared `DCERPCTests` transport/credential harness. It depends on live Windows SCM behavior and common service names.

## Risks
The main risk is target-state mutation: creating services, changing service config, service account details, failure actions, privileges, triggers, and stopping a real crypto service can affect the remote machine. The class-name check `self.__class__.__name__ == 'SMBTransport'` appears suspicious because concrete classes are `SCMRTestsSMBTransport` and `SCMRTestsTCPTransport`, so the encrypted-password branch may be unreachable. Several tests are skipped or commented because behavior is unresolved. Binary parsing in `query_failure_actions()` assumes exact SCMR layout offsets.

## Test Signals
The strongest signals are configuration round trips, failure-action array count synchronization, omitted action-list preservation, buffer-size retry correctness, service enum/status parsing into `SERVICE_STATUS_PROCESS`, expected service already running/not active/dependent-services errors, and successful handle close/delete cleanup. Skipped tests mark incomplete coverage for service groups, notifications, and control-service extended calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_scmr.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_srvs.py -->
# sources/user-network-fs/impacket/tests/dcerpc/test_srvs.py

## Purpose
This file is a remote integration suite for the Server Service RPC interface (`srvsvc`). It validates Impacket request classes and helper wrappers for connection, file, session, share, server information, transport, file security, path/name canonicalization, DFS, server alias, and share deletion operations.

## Important APIs, Types, and Functions
`SRVSTests` binds `srvs.MSRPC_UUID_SRVS` on `\\PIPE\\srvsvc` with authentication. It uses low-level request classes such as `NetrShareEnum`, `NetrShareAdd`, `NetrServerGetInfo`, `NetrpGetFileSecurity`, and `NetprPathCanonicalize`, plus helper wrappers such as `hNetrShareEnum`, `hNetrServerDiskEnum`, and `hNetprNameValidate`. Data structures include share info levels 0/1/2/501/502/503, `SERVER_ALIAS_INFO_0`, security descriptor buffers, `NULL`, and `OWNER_SECURITY_INFORMATION`.

## Control Flow
Each test connects, builds a request for one or more information levels, sends it, and dumps responses. Paired raw/helper tests mirror the same API coverage. Many enum and get-info calls switch union tags and levels in-place to verify multiple discriminated-union layouts. Share lifecycle tests add `BETUSHARE`, delete it directly, delete it through start/commit, or delete it with `NetrShareDelEx`. File/session tests first enumerate then act on the first returned entry.

## State and Persistence Behavior
The file can modify real server state: temporary shares are created/deleted, IPC$ share remarks are edited then restored, sessions or open files may be closed, server aliases are added/deleted, and file security may be read and written back on `C$\\Windows`. DFS calls mostly expect unsupported or bad-stub responses but still target server configuration APIs. Some disabled `tes_` and `ttt_` methods are intentionally not discovered by unittest.

## Dependencies and Integration Points
Dependencies include `impacket.dcerpc.v5.srvs`, shared DCE/RPC harness configuration, the target machine name, administrative shares (`IPC$`, `C$`), Windows server service behavior, and filesystem/security state on the target. It exposes both NDR and NDR64 SMB transport subclasses via `pytest.mark.remote`.

## Risks
The suite assumes returned enum buffers are non-empty and that built-in shares and files exist, which can fail on hardened or idle systems. Tests may close their own pipe/session, acknowledged by accepted `STATUS_PIPE_BROKEN`, `STATUS_FILE_CLOSED`, and invalid-handle errors. Several cleanup paths are not protected by `finally`, so failed share or alias tests can leave `BETUSHARE` or `BETOALIAS`. String comparisons for unsupported DFS/alias behavior are brittle, and mutating IPC$ remarks or file security on system paths is high impact.

## Test Signals
Signals include successful marshalling of many info-level unions, expected DFS and alias unsupported errors, expected `ERROR_MORE_DATA`/status variants in close/delete paths, restoration of share remarks, add/delete lifecycle success for shares and aliases, and successful round trip of security descriptor data. The misspelled `tes_` and `ttt_` methods are visible coverage candidates but not active tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_srvs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_tsch.py -->
# sources/user-network-fs/impacket/tests/dcerpc/test_tsch.py

## Purpose
This file tests three related scheduled-task RPC interfaces: legacy ATSVC (`atsvc`), task account security (`sasec`), and modern Task Scheduler Service (`tsch`). It validates job add/enum/get/delete, account credential calls, task scheduler version/retrieve/folder/enum/run/instance/stop/rename/runtime/info/enabled APIs, and both raw request and helper wrapper paths.

## Important APIs, Types, and Functions
`ATSVCTests`, `SASECTests`, and `TSCHTests` all inherit `DCERPCTests`, bind to `\\PIPE\\atsvc`, authenticate, and request packet privacy. `AT_INFO` is the common ATSVC job structure. `TSCHTests.get_tsch_test_path()` generates unique folder names with UUIDs, and `delete_tsch_test_path()` tolerates missing-path errors. Tests use `tsch` request classes and helpers such as `hSchRpcCreateFolder`, `hSchRpcEnumTasks`, `hSchRpcRun`, and `hSchRpcEnableTask`.

## Control Flow
ATSVC tests create jobs that run command-shell output redirection, enumerate or query them, then delete by job id. TSCH tests often open a second DCE connection to ATSVC to create an `AtN` job, then use TSCH to retrieve, enumerate, run, inspect, or stop that task before deleting it through ATSVC. Folder tests create a random scheduler folder, enumerate root folders, and delete in `finally`. Many tests catch `ERROR_NOT_SUPPORTED`, missing-path HRESULTs, `SCHED_E_TASK_NOT_RUNNING`, `ERROR_INVALID_FUNCTION`, or `E_NOTIMPL` as acceptable environment outcomes.

## State and Persistence Behavior
The file creates scheduled jobs, temporary scheduler folders, and may run tasks that write output under `%SYSTEMROOT%\\Temp\\BTO` or `%SYSTEMROOT%\\Temp\\ANI`. It also sets task scheduler account information through SASEC using configured test credentials. Some job cleanup is explicit after successful setup, but not always protected by `finally`, so a failure between add and delete can leave jobs or output files on the target.

## Dependencies and Integration Points
The suite depends on Impacket's `tsch`, `atsvc`, and `sasec` modules, `impacket.system_errors.ERROR_NOT_SUPPORTED`, shared credentials, UUID generation, Windows Task Scheduler/AT service support level, and the presence of sample built-in task `\\Microsoft\\Windows\\Defrag\\ScheduledDefrag`. It exposes remote SMB transport classes for NDR and NDR64 for each interface class.

## Risks
Remote task creation and execution is high impact. Tests can execute command lines on the target, alter scheduler account settings, enable built-in tasks, and leave scheduler artifacts if cleanup is bypassed. Many APIs are OS-version dependent, so the suite intentionally accepts unsupported/not-implemented responses. Some tests print and pass on broad TSCH errors, reducing failure precision.

## Test Signals
Signals include successful ATSVC job lifecycle, TSCH visibility of legacy AT jobs, unique folder create/enumerate/delete behavior, task run GUID handling, expected scheduler not-running/not-scheduled states, account-info calls accepting or returning expected missing-file errors, and helper/raw API parity. Skipped `SchRpcRegisterTask` documents an unimplemented/disabled test area.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_tsch.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_wkst.py -->
# sources/user-network-fs/impacket/tests/dcerpc/test_wkst.py

## Purpose
This file tests Impacket's Workstation Service RPC (`wkst`) client definitions against a live `\\PIPE\\wkssvc` endpoint. It covers workstation info query/set, logged-on user and transport enumeration, use connection add/enum/get/delete, workstation statistics, domain join/unjoin/rename/name validation, alternate computer names, primary computer name, and computer-name enumeration.

## Important APIs, Types, and Functions
`WKSTTests` binds `wkst.MSRPC_UUID_WKST` over SMB named pipe and authenticates. It uses raw request classes such as `NetrWkstaGetInfo`, `NetrWkstaSetInfo`, `NetrUseAdd`, `NetrJoinDomain2`, and `NetrEnumerateComputerNames`, plus helper wrappers such as `hNetrWkstaGetInfo`, `hNetrUseAdd`, `hNetrValidateName2`, and `hNetrEnumerateComputerNames`. It constructs `LPUSE_INFO_1` for mapped-use tests and uses `NULL` for optional RPC pointers.

## Control Flow
Tests connect, populate request structures, submit them, and dump responses. Info-level tests repeat calls at levels 100, 101, 102, and 502. Set-info tests query level 502, save `wki502_dormant_file_limit`, set it to 500, verify by re-query, and restore. Use tests attempt to map local `Z:` to `\\\\127.0.0.1\\c$`, then enumerate, get info, and delete; they skip later calls for the NDR64 transfer syntax. Domain-management tests intentionally pass dummy credentials/password buffers and accept expected errors.

## State and Persistence Behavior
The suite can alter real workstation state. The level-502 dormant file limit is temporarily changed and restored. Use tests may add a local drive mapping. Domain join/unjoin/rename and alternate-name APIs are invoked but usually expect invalid-password/not-supported errors. No local persistent state is stored by the tests themselves.

## Dependencies and Integration Points
Dependencies include `impacket.dcerpc.v5.wkst`, shared remote test configuration, Windows Workstation Service, administrative `c$` share access on loopback, transfer syntax constants from `DCERPCTests`, and OS/domain policy behavior. Remote subclasses cover SMB NDR and NDR64.

## Risks
Some tests mutate workstation configuration or try domain-management calls; running against non-disposable hosts is risky. Use mapping cleanup is best-effort and may be skipped on access-denied or pipe-disconnected paths. Error validation relies heavily on string fragments such as `ERROR_INVALID_PASSWORD`, `0x8001011c`, and `ERROR_NOT_SUPPORTED`, which may vary. The NDR64 early return means use enum/get/delete coverage is intentionally incomplete for that syntax.

## Test Signals
Signals include successful info-level decoding, set/query/restore of workstation level 502, tolerated invalid-function/access-denied responses, expected domain-management failures with dummy credentials, and helper/raw parity across most operations. Remote marks and NDR/NDR64 subclasses identify it as an infrastructure-dependent integration suite.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dcerpc/test_wkst.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/__init__.py -->
# sources/user-network-fs/impacket/tests/dot11/__init__.py

## Purpose
This package initializer marks `impacket/tests/dot11` as a Python test package. It contains only the shebang, copyright/license header, and no executable imports or package-level fixtures.

## Important APIs, Types, and Functions
There are no classes, functions, variables, or exported test helpers. Its only functional role is package discovery/compatibility for the sibling dot11 unittest modules.

## Control Flow
No runtime control flow exists. Importing the package executes no side effects beyond loading the empty module.

## State and Persistence Behavior
No state is created, mutated, cached, or persisted.

## Dependencies and Integration Points
It integrates indirectly with Python's import system and test discovery. Sibling files import from `impacket.dot11` and `impacket.ImpactDecoder`, but this initializer does not wire those imports.

## Risks
Risk is minimal. Future maintainers should avoid adding side effects here because it would affect all dot11 test imports.

## Test Signals
There are no direct test signals. A successful import of sibling tests implicitly validates that the package initializer does not interfere with discovery.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_Dot11Base.py -->
# sources/user-network-fs/impacket/tests/dot11/test_Dot11Base.py

## Purpose
This unit test validates core `Dot11` frame-control parsing and mutation. It checks header/tail sizing, version/type/subtype extraction, individual bit flags, combined type/subtype setting, and final serialized bytes for a crafted control frame.

## Important APIs, Types, and Functions
`TestDot11Common` constructs `Dot11` from a fixed byte string. It exercises `get_header_size`, `get_tail_size`, `get_version/set_version`, `get_type/set_type`, `get_subtype/set_subtype`, flag getters/setters (`toDS`, `fromDS`, `moreFrag`, `retry`, `powerManagement`, `moreData`, `order`), `set_type_n_subtype`, and `get_packet`. `Dot11Types` supplies named constants.

## Control Flow
`setUp()` creates a fresh `Dot11` instance for each test, so mutations are isolated. Each test reads the initial parsed value, writes a replacement, and asserts the updated value. The final test sets a power-save poll type/subtype and multiple flags, then compares the complete packet bytes.

## State and Persistence Behavior
State is in-memory only inside the `Dot11` object. Mutator tests verify that bit-level changes update the serialized packet. No files, network, or shared state are touched.

## Dependencies and Integration Points
The file depends on `unittest`, `impacket.dot11.Dot11`, and `Dot11Types`. It is a local unit test and does not require the remote DCE/RPC infrastructure.

## Risks
The disabled WEP bit test leaves one frame-control bit without active coverage. Tests assert exact byte order and bit layout, so they are sensitive to intentional representation changes but useful for regression detection.

## Test Signals
Signals are direct equality assertions for bitfield getters/setters and a complete packet byte comparison, providing strong regression coverage for frame-control packing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_Dot11Base.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_Dot11Decoder.py -->
# sources/user-network-fs/impacket/tests/dot11/test_Dot11Decoder.py

## Purpose
This unit test validates the 802.11 decoder chain in `impacket.ImpactDecoder.Dot11Decoder`. It decodes a captured WEP-protected data frame and verifies the resulting protocol hierarchy.

## Important APIs, Types, and Functions
`TestDot11Decoder` uses `Dot11Decoder().decode()`, then walks `child()` links through `Dot11`, `Dot11DataFrame`, `Dot11WEP`, and encrypted payload/data nodes. It uses `six.PY2` to account for Python 2 class string formatting. Optional WEP-key paths reference LLC and WEP data verification but are inactive because `self.WEPKey` is `None`.

## Control Flow
`setUp()` decodes a static `WEPData` byte string once per test and records successive child nodes. Tests compare class string representations for the top decoder layers. If a WEP key were supplied, additional child nodes would be initialized and validated; otherwise tests return early or assert that the undecoded payload is `ImpactPacket.Data`.

## State and Persistence Behavior
All state is local to decoded packet objects. No persistence or external I/O occurs.

## Dependencies and Integration Points
The file integrates `ImpactDecoder` with `impacket.dot11` packet classes and `ImpactPacket.Data`. It is a unit-level signal that decoder dispatch connects frame-control parsing to protocol object construction.

## Risks
Most encrypted-payload coverage is inactive because there is no WEP key, so LLC decoding and decrypted payload assertions are not normally exercised. Class checks rely on string formatting, which is less robust than `isinstance` and keeps compatibility branches for Python 2.

## Test Signals
Signals include hierarchy construction from raw bytes, correct dispatch to `Dot11DataFrame` and `Dot11WEP`, and fallback to opaque `ImpactPacket.Data` when encrypted data is not decrypted.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_Dot11Decoder.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_Dot11HierarchicalUpdate.py -->
# sources/user-network-fs/impacket/tests/dot11/test_Dot11HierarchicalUpdate.py

## Purpose
This file tests `ProtocolPacket` parent/child composition semantics. It verifies that nested packet serialization, size calculations, body views, and parent-child references update correctly when a child or parent body is modified.

## Important APIs, Types, and Functions
`PacketTest` is a minimal `ProtocolPacket` subclass with fixed header size 7 and tail size 5. `TestDot11HierarchicalUpdate` uses `load_packet`, `contains`, `load_body`, `get_packet`, `get_size`, `get_header_size`, `get_body_size`, `get_tail_size`, `body.get_buffer_as_string`, `get_body_as_string`, `parent`, and `child`.

## Control Flow
`setUp()` builds three nested raw packets, loads them into `PacketTest` instances, and links `packet3 -> packet2 -> packet1` using `contains()`. Tests first verify initial serialization and sizes, then modify `packet1` body and check that ancestors reflect the new child bytes. The final test calls `packet2.load_body(...)` and verifies that replacing a parent body detaches the previous child.

## State and Persistence Behavior
State consists of in-memory packet buffers and hierarchy pointers. The important state transition is child detachment when a packet body is overwritten directly, preventing stale child references.

## Dependencies and Integration Points
The test depends on `impacket.dot11.ProtocolPacket`, but it exercises generic packet composition behavior used by dot11 and likely other packet layers.

## Risks
The synthetic packets use ASCII-size headers/tails and fixed sizes, so they validate hierarchy mechanics rather than protocol-specific parsing. Duplicate test method descriptions are benign but make failures less descriptive.

## Test Signals
Signals include exact serialized nested byte strings, exact size arithmetic before and after mutation, body-buffer propagation up the hierarchy, and correct parent/child pointer detachment.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_Dot11HierarchicalUpdate.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameControlACK.py -->
# sources/user-network-fs/impacket/tests/dot11/test_FrameControlACK.py

## Purpose
This unit test validates parsing and mutation of 802.11 ACK control-frame bodies.

## Important APIs, Types, and Functions
`TestDot11FrameControlACK` uses `Dot11` to parse frame control, `Dot11Types` constants to assert type/subtype identity, and `Dot11ControlFrameACK` for body-level accessors. It exercises `get_header_size`, `get_tail_size`, `get_duration/set_duration`, and `get_ra/set_ra`.

## Control Flow
`setUp()` parses a static ACK frame, asserts it is a control acknowledgment, constructs the ACK body object from `d.get_body_as_string()`, and attaches it with `d.contains(self.ack)`. Tests then validate size and mutate duration and receiver address.

## State and Persistence Behavior
State is local packet-buffer mutation only. Address setters update an array-like field copied back into the frame body.

## Dependencies and Integration Points
The file integrates top-level `Dot11` frame-control parsing with the specialized ACK control-frame class.

## Risks
The test does not assert final full-frame serialization after mutations, only accessor round trips. It also assumes `get_ra()` returns an object supporting `tolist()` and item assignment.

## Test Signals
Signals include correct ACK subtype dispatch, ACK body size of 8 bytes with no tail, little-endian duration handling, and receiver-address round-trip mutation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameControlACK.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameControlCFEnd.py -->
# sources/user-network-fs/impacket/tests/dot11/test_FrameControlCFEnd.py

## Purpose
This unit test validates 802.11 CF-End control-frame body parsing and field mutation.

## Important APIs, Types, and Functions
It uses `Dot11`, `Dot11Types`, and `Dot11ControlFrameCFEnd`. Covered accessors are header/tail size, `get_duration/set_duration`, `get_ra/set_ra`, and `get_bssid/set_bssid`.

## Control Flow
`setUp()` parses a fixed CF-End frame, asserts control type/subtype/type-subtype constants, creates `Dot11ControlFrameCFEnd` from the top-level body, and attaches it as a child. Tests validate the 14-byte control body and mutate duration, receiver address, and BSSID.

## State and Persistence Behavior
Only in-memory packet field state changes. No external state or persistence.

## Dependencies and Integration Points
The file tests the integration between generic frame-control decoding and a specialized control-frame body class with two MAC-address fields.

## Risks
Coverage is field-level and does not assert complete serialized packet bytes after mutation. It assumes byte arrays are mutable and expose `tolist()`.

## Test Signals
Signals include exact subtype recognition, expected broadcast RA and BSSID bytes from the sample, duration endian correctness, and setter/getter round trips for both address fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameControlCFEnd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameControlCFEndCFACK.py -->
# sources/user-network-fs/impacket/tests/dot11/test_FrameControlCFEndCFACK.py

## Purpose
This file validates parsing and mutation for combined CF-End + CF-ACK 802.11 control frames.

## Important APIs, Types, and Functions
It uses `Dot11`, `Dot11Types`, and `Dot11ControlFrameCFEndCFACK`. Accessors under test are body size, tail size, duration, receiver address, and BSSID getters/setters.

## Control Flow
`setUp()` parses a static frame, verifies the control subtype and combined type/subtype constant, creates the specialized body parser from the generic body string, and links it as a child. Tests assert initial field values, mutate selected bytes or duration, and re-read through getters.

## State and Persistence Behavior
State is confined to the in-memory packet object and its mutable address buffers.

## Dependencies and Integration Points
The test checks that the generic dot11 frame layer and the CF-End-CF-ACK body class agree on body boundaries and subtype semantics.

## Risks
No final packet-level serialization is asserted after mutation. The static sample is the only fixture, so malformed or truncated variants are not covered.

## Test Signals
Signals include exact duration `0xEDDE`, body size of 14 bytes, correct RA/BSSID extraction, and address mutation persistence through setters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameControlCFEndCFACK.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameControlCTS.py -->
# sources/user-network-fs/impacket/tests/dot11/test_FrameControlCTS.py

## Purpose
This unit test validates Clear-To-Send control-frame parsing for 802.11.

## Important APIs, Types, and Functions
It uses `Dot11`, `Dot11Types`, and `Dot11ControlFrameCTS`, covering `get_header_size`, `get_tail_size`, `get_duration/set_duration`, and `get_ra/set_ra`.

## Control Flow
`setUp()` decodes a static CTS frame, asserts control and CTS subtype constants, constructs the CTS body from the parent body bytes, and attaches it with `contains()`. Tests verify the body size and mutate duration and receiver address.

## State and Persistence Behavior
All state is local in packet buffers. Mutations verify field-level updates only.

## Dependencies and Integration Points
The file verifies the specialized CTS body parser's alignment with the generic `Dot11` body boundary and type/subtype logic.

## Risks
It does not validate full packet bytes after setter calls, and only one fixture is used. Address mutation assumes a mutable array-like return value.

## Test Signals
Signals include CTS subtype recognition, 8-byte control body size, expected initial duration 4667, and RA round-trip mutation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameControlCTS.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameControlPSPoll.py -->
# sources/user-network-fs/impacket/tests/dot11/test_FrameControlPSPoll.py

## Purpose
This unit test validates Power Save Poll control-frame parsing and mutation.

## Important APIs, Types, and Functions
It uses `Dot11`, `Dot11Types`, and `Dot11ControlFramePSPoll`. Covered fields are AID, BSSID, transmitter address, header size, and tail size via `get_aid/set_aid`, `get_bssid/set_bssid`, and `get_ta/set_ta`.

## Control Flow
`setUp()` parses a static PS-Poll frame, confirms control type and PS-Poll subtype constants, constructs the specialized body parser, and attaches it to the parent. Tests check body dimensions, mutate AID, mutate BSSID endpoints, and mutate TA endpoints.

## State and Persistence Behavior
State is local to packet buffers. The test verifies that setter methods update the mutable in-memory representation.

## Dependencies and Integration Points
This integrates the generic dot11 parser with the PS-Poll body layout, which differs from other control frames by using AID instead of a standard duration field.

## Risks
The test covers field access but not serialized full-frame output after mutation. It does not cover boundary behavior for AID reserved bits.

## Test Signals
Signals include subtype recognition, 14-byte body size, initial AID `0xAFF1`, BSSID and TA extraction, and setter/getter round trips.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameControlPSPoll.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameControlRTS.py -->
# sources/user-network-fs/impacket/tests/dot11/test_FrameControlRTS.py

## Purpose
This file validates Request-To-Send control-frame parsing and mutation.

## Important APIs, Types, and Functions
It uses `Dot11`, `Dot11Types`, and `Dot11ControlFrameRTS`. Covered body APIs are size getters, `get_duration/set_duration`, `get_ra/set_ra`, and `get_ta/set_ta`.

## Control Flow
`setUp()` parses a static RTS frame, asserts control type and RTS subtype constants, creates the specialized RTS body object from the parent body, and links it as a child. Tests verify body size, duration, receiver address, and transmitter address mutations.

## State and Persistence Behavior
No external state exists. Mutations are packet-buffer updates inside the test instance.

## Dependencies and Integration Points
The test checks agreement between top-level `Dot11` frame-control parsing and the RTS body layout containing both RA and TA fields.

## Risks
No full serialized packet assertion follows setter calls, and only one sample frame is covered.

## Test Signals
Signals include exact RTS subtype recognition, 14-byte body size, initial duration `0x181`, and address setter round trips for RA and TA.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameControlRTS.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameData.py -->
# sources/user-network-fs/impacket/tests/dot11/test_FrameData.py

## Purpose
This file validates parsing and mutation of a standard 802.11 data frame body.

## Important APIs, Types, and Functions
`TestDot11DataFrames` uses `Dot11`, `Dot11Types`, and `Dot11DataFrame`. It covers header/tail size, duration, address1/address2/address3 getters and setters, sequence-control accessors, fragment-number masking, sequence-number masking, and `get_frame_body`.

## Control Flow
`setUp()` parses a fixed data frame, asserts data type/subtype constants, builds `Dot11DataFrame` from the parent body bytes, and attaches it. Tests mutate duration and address fields, set sequence-control fields, verify bit masking for 4-bit fragment and 12-bit sequence numbers, and compare payload bytes for a frame without address4.

## State and Persistence Behavior
State is local in packet objects. The important behavior is mutation of packed sequence-control subfields without corrupting unrelated bits.

## Dependencies and Integration Points
The test integrates top-level dot11 frame-control parsing with the data-frame body parser and payload extraction used before LLC/IP decoding.

## Risks
It covers a no-address4 data frame only, leaving ToDS/FromDS combinations with a fourth address untested. It does not assert full-packet serialization after each setter.

## Test Signals
Signals include type/subtype recognition, exact header size of 22 bytes, duration and MAC address round trips, fragment/sequence bit masking, and exact frame-body payload comparison.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameData.py -->

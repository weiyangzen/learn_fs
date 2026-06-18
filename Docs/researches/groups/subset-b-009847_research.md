# Research: subset-b-009847

Grouped research for Samba RPC client support files under `sources/user-network-fs/samba/source3/rpc_client`. Each section is source-tree aligned and bounded by reconciliation markers for per-file extraction.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_winreg_spoolss.c -->
# sources/user-network-fs/samba/source3/rpc_client/cli_winreg_spoolss.c

## Purpose
`cli_winreg_spoolss.c` is Samba's winreg-backed persistence layer for spoolss printer metadata. It maps spoolss server operations onto Windows-compatible registry keys under `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Print`, `HKLM\SYSTEM\CurrentControlSet\Control\Print`, forms, package installation, driver, core-driver, and printer-specific subkeys. The file lets the spoolss RPC server and printing migration code create printers, read and update `PRINTER_INFO_2`, preserve security descriptors, manage printer data values, enumerate/delete printer subkeys, maintain change IDs, manage forms, and store printer driver/package metadata.

## Important APIs, Types, And Functions
Public entry points are the `winreg_*` functions declared in `cli_winreg_spoolss.h`: `winreg_create_printer()`, `winreg_update_printer()`, `winreg_get_printer()`, `winreg_get/set_*_secdesc()`, printer dataex CRUD/enumeration helpers, form helpers, driver helpers, core-driver helpers, and driver-package helpers. Static helpers centralize key construction and conversions: `winreg_printer_openkey()`, `winreg_printer_open_core_driver()`, `winreg_printer_opendriver()`, `winreg_enumval_to_dword/sz/multi_sz()`, date/version string conversion, and `winreg_printer_rev_changeid()`.

The file contains the built-in Windows form table `builtin_forms1[]`, and uses spoolss generated structures such as `spoolss_SetPrinterInfo2`, `spoolss_PrinterInfo2`, `spoolss_DeviceMode`, `spoolss_FormInfo1`, `spoolss_DriverInfo8`, `spoolss_CorePrinterDriver`, and `spoolss_PrinterEnumValues`.

## Control Flow
Most operations open HKLM, open or create a target key, perform one or more winreg RPC calls, translate `NTSTATUS` into `WERROR`, and close policy handles on all exit paths. Printer creation first skips existing printers, otherwise creates the main printer key plus `DsDriver`, `DsSpooler`, and printer-data subkeys, writes DS spooler defaults, builds a minimal `SetPrinterInfo2`, creates a default security descriptor, and calls `winreg_update_printer()`.

`winreg_update_printer()` is bitmask-driven: each `SPOOLSS_PRINTER_INFO_*` flag writes a named registry value. Devmodes are optionally synthesized, validated against the NDR size, marshalled, and stored as binary. Security descriptors are delegated to `winreg_set_printer_secdesc()`. Reads invert that flow by enumerating values, converting matched registry types into `PrinterInfo2`, pulling `Default DevMode`, creating a fallback devmode if configured, loading the security descriptor, and mapping OS/2 drivers when needed.

Forms combine immutable `builtin_forms1[]` entries with registry values stored as 32-byte binary records. Drivers are normalized through `driver_info_ctr_to_info8()` and stored under environment/version/driver-name keys. Core drivers and driver packages are stored under `PackageInstallation\<architecture>`.

## State And Persistence
Persistent state is remote/local registry data accessed over a winreg DCE/RPC binding. Printer records include names, port, processor, datatype, devmode, security descriptor, `ChangeID`, arbitrary printer data, forms, driver metadata, core-driver metadata, and package paths. Change IDs are generated from process uptime in milliseconds, not from a global durable counter. The code also consults Samba runtime state such as loadparm service numbers, DNS/workgroup data, machine/domain SIDs, remote architecture, and default-devmode settings.

## Dependencies And Integration Points
This file depends on generated `ndr_winreg_c`, `ndr_spoolss`, security NDR, Samba registry utilities, `cli_winreg.h`, `init_spoolss.h`, `nt_printing.h`, OS/2 driver mapping, secrets, loadparm, SID/security helpers, and the spoolss RPC server utility layer. Main integration points are `source3/rpc_server/spoolss/srv_spoolss_util.c`, `srv_spoolss_nt.c`, `printing/nt_printing.c`, `printing/nt_printing_ads.c`, and `printing/nt_printing_migrate.c`.

## Risks
The code is broad and repetitive, so registry value names, access mode, and handle cleanup must stay consistent. `ChangeID` can collide or move backward across process restarts despite needing monotonic client-visible behavior during a spooler lifetime. Devmode validation assumes callers supply coherent generated structures. Security descriptor repair fills missing owner/group/DACL/SACL from old descriptors, which is correct for Windows compatibility but can hide incomplete caller input. Some form paths contain fixed placeholder indexes and one rename branch appears counterintuitive because it deletes when names compare equal. Driver date/version conversions depend on US date strings and four-part version formatting. The key paths and default values are compatibility contracts with Windows spooler clients.

## Test Signals
Useful signals are Samba spoolss RPC torture and blackbox printer tests, driver upload/migration tests, print server restart/cache tests that observe `ChangeID`, registry-backed printer enumeration, SetPrinter/GetPrinter round trips with devmode and security descriptors, form add/set/delete/get including builtin protection, and driver/core-driver/package add/get/delete cycles. Integration tests should exercise both internal spoolss utility wrappers and direct winreg-backed paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_winreg_spoolss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_winreg_spoolss.h -->
# sources/user-network-fs/samba/source3/rpc_client/cli_winreg_spoolss.h

## Purpose
`cli_winreg_spoolss.h` exposes the spoolss-over-winreg helper API implemented by `cli_winreg_spoolss.c`. It is the public contract used by Samba's spoolss server, print migration, and printing subsystems to store and retrieve printer configuration through the winreg RPC pipe.

## Important APIs, Types, And Functions
The header defines `enum spoolss_PrinterInfo2Mask`, a bitmask describing which fields in `spoolss_SetPrinterInfo2` should be written by `winreg_update_printer()`, plus `SPOOLSS_PRINTER_INFO_ALL`. It declares functions for printer lifecycle, printer info, security descriptors, arbitrary data values, subkey enumeration/deletion, change ID update/read, forms, driver metadata, driver lists, core drivers, and driver packages.

Important declarations include `winreg_create_printer()`, `winreg_update_printer()`, `winreg_get_printer()`, `winreg_get/set_printer_secdesc()`, `winreg_get/set_printserver_secdesc()`, `winreg_set/get/enum/delete_printer_dataex()`, `winreg_enum/delete_printer_key()`, `winreg_printer_*form1()`, `winreg_add/get/del_driver()`, `winreg_get_driver_list()`, `winreg_add/get_core_driver()`, and `winreg_add/get/del_driver_package()`.

## Control Flow
The header has no runtime control flow. It organizes the exported registry-backed operations into a stable C interface that accepts `TALLOC_CTX`, `dcerpc_binding_handle`, printer/share names, generated spoolss structures, and output pointers. Callers are expected to own the RPC binding and pass talloc contexts for returned structures.

## State And Persistence
The header declares functions that mutate persistent registry state but does not hold state itself. Its bitmask constants control selective persistence of `PRINTER_INFO_2` fields.

## Dependencies And Integration Points
It includes `replace.h` and generated `spoolss.h`, forward-declares `struct dcerpc_binding_handle`, and is included by spoolss server utility code, print migration code, and registry-backed printing helpers.

## Risks
The bitmask values are ABI-like local contracts with the implementation. Adding `PrinterInfo2` fields or changing mask values without updating `winreg_update_printer()` can silently drop or miswrite state. Documentation in the header has minor typos, but the function prototypes are the important contract.

## Test Signals
Compile coverage catches signature drift. Behavioral tests should cover each exported operation through spoolss server wrappers, especially selective `info2_mask` updates, security descriptor defaulting, dataex operations, form builtin handling, and driver/package persistence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_winreg_spoolss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/init_lsa.c -->
# sources/user-network-fs/samba/source3/rpc_client/init_lsa.c

## Purpose
`init_lsa.c` provides small initializers for LSA string structures and builders for encrypted trusted-domain authentication blobs used by LSA RPC calls. It prepares both legacy RC4 and newer AES-protected trust domain password payloads.

## Important APIs, Types, And Functions
String helpers are `init_lsa_String()`, `init_lsa_StringLarge()`, `init_lsa_AsciiString()`, and `init_lsa_AsciiStringLarge()`. Trust helpers are `rpc_lsa_encrypt_trustdom_info()` and `rpc_lsa_encrypt_trustdom_info_aes()`. They populate `trustDomainPasswords`, `AuthenticationInformation`, `lsa_TrustDomainInfoAuthInfoInternal`, and `lsa_TrustDomainInfoAuthInfoInternalAES` structures.

## Control Flow
String helpers assign pointers and, for `lsa_String`, set byte length and size from `strlen_m()`. The RC4 trust flow converts old/new incoming/outgoing cleartext passwords from Unix charset to UTF-16, stamps all four auth entries with the current NT time, fills a confounder, NDR-marshals `trustDomainPasswords`, then encrypts the resulting blob with ARCFOUR using the session key. The AES flow builds the same plaintext, generates a salt, and calls `samba_gnutls_aead_aes_256_cbc_hmac_sha512_encrypt()` with LSA-specific encryption and MAC salts, storing ciphertext and auth data.

## State And Persistence
The file persists no global state. It allocates returned blobs under caller-provided talloc contexts and uses current time plus random confounder/salt values, so output is intentionally non-deterministic. Password buffers remain in talloc allocations used for the marshalled/encrypted blobs.

## Dependencies And Integration Points
Dependencies include generated LSA and DRS blob NDR, `dcerpc_lsa.h`, Samba charset conversion, random buffer helpers, GnuTLS cipher APIs, and Samba AEAD helper salts. Callers include `rpcclient/cmd_lsarpc.c` and LSA RPC torture tests for trusted domain password operations.

## Risks
The functions return `bool`, so detailed conversion, NDR, or crypto failures are collapsed. The RC4 helper calls `gnutls_cipher_init()` and encrypt without checking their return codes. Password inputs are expected non-NULL and are measured with `strlen()`. The AES helper rejects ciphertext shorter than 520 bytes, a protocol-shape assumption that should be preserved by tests.

## Test Signals
Relevant signals are LSA torture tests around trusted domain auth info, rpcclient trust password commands, invalid/null password input coverage, RC4/AES round-trip decryption compatibility, and tests verifying generated blobs have current/previous incoming/outgoing entries with expected timestamps and auth types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/init_lsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/init_lsa.h -->
# sources/user-network-fs/samba/source3/rpc_client/init_lsa.h

## Purpose
`init_lsa.h` declares helper functions for initializing LSA string wrappers and encrypting trusted-domain auth info for LSA RPC clients.

## Important APIs, Types, And Functions
The header forward-declares generated LSA string types and declares `init_lsa_String()`, `init_lsa_StringLarge()`, `init_lsa_AsciiString()`, `init_lsa_AsciiStringLarge()`, `rpc_lsa_encrypt_trustdom_info()`, and `rpc_lsa_encrypt_trustdom_info_aes()`.

## Control Flow
There is no runtime logic. The prototypes define a caller contract: pass caller-owned strings and a session key, receive talloc-allocated internal auth info structures through output pointers.

## State And Persistence
The header carries no state. The declared encryption helpers produce transient RPC payloads rather than durable local persistence.

## Dependencies And Integration Points
It is consumed by rpcclient LSA command code and torture tests, and it depends on generated LSA auth-info structures being visible to the including translation unit.

## Risks
The API exposes nullable `const char *` parameters but the implementation expects valid strings. Callers need to validate inputs before invoking it. Return type is `bool`, limiting diagnostics.

## Test Signals
Build coverage catches generated type/signature drift. Behavioral coverage belongs with `init_lsa.c`: trust-domain password set/query flows, AES and RC4 compatibility, and failure handling for allocation/conversion errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/init_lsa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/init_samr.c -->
# sources/user-network-fs/samba/source3/rpc_client/init_samr.c

## Purpose
`init_samr.c` builds encrypted SAMR password buffers for password-change and account-management RPC calls. It supports legacy RC4 formats and the AES/HMAC-SHA512 encrypted password structure.

## Important APIs, Types, And Functions
Exports are `init_samr_CryptPasswordEx()`, `init_samr_CryptPassword()`, and `init_samr_CryptPasswordAES()`. They populate `samr_CryptPasswordEx`, `samr_CryptPassword`, and `samr_EncryptedPasswordAES`. The file uses `encode_rc4_passwd_buffer()`, `encode_pw_buffer()`, `encode_pwd_buffer514_from_str()`, GnuTLS ARCFOUR, and Samba AEAD helpers with SAMR-specific salts.

## Control Flow
`init_samr_CryptPasswordEx()` delegates directly to `encode_rc4_passwd_buffer()`. `init_samr_CryptPassword()` encodes a 516-byte Unicode password buffer, initializes an ARCFOUR cipher from the session key, encrypts the fixed-size buffer, and maps GnuTLS failures to NTSTATUS. `init_samr_CryptPasswordAES()` validates the output pointer, encodes a 514-byte plaintext password buffer, encrypts it with AES-256-CBC/HMAC-SHA512 using the supplied salt and session key, wipes the stack plaintext with `BURN_DATA()`, copies the salt into the output, sets ciphertext length/data, and leaves `PBKDF2Iterations` as zero.

## State And Persistence
The file does not persist state. It writes caller-supplied output structs and talloc-allocated ciphertext. Sensitive plaintext is stack-local in the AES path and explicitly burned; the RC4 paths rely on helper behavior and output buffers.

## Dependencies And Integration Points
Dependencies include libcli auth password encoders, generated SAMR RPC types, GnuTLS, and Samba crypto helper salts. Callers include `rpcclient/cmd_samr.c`, join/password-change code, NetAPI user code, source4 libnet password code, and SAMR torture tests.

## Risks
Session key and salt sizes are assumed to match protocol expectations; the AES path asserts salt length matches the output struct. RC4 remains required for older protocol compatibility but is cryptographically legacy. The fixed buffer sizes are protocol-specific and must not be changed casually. `init_samr_CryptPasswordEx()` relies entirely on delegated error handling.

## Test Signals
SAMR torture tests exercise password set/change paths with RC4 and AES. Additional signals include invalid output pointer handling, malformed salt length assertions in debug builds, GnuTLS failure mapping, and server-side acceptance of generated password buffers in join, rpcclient, and NetAPI flows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/init_samr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/init_samr.h -->
# sources/user-network-fs/samba/source3/rpc_client/init_samr.h

## Purpose
`init_samr.h` declares SAMR password encryption buffer initializers used by RPC client and account-management code.

## Important APIs, Types, And Functions
It declares `init_samr_CryptPasswordEx()`, `init_samr_CryptPassword()`, and `init_samr_CryptPasswordAES()`. Inputs are cleartext password strings, session keys, and for AES a salt plus talloc context; outputs are generated SAMR encrypted password structures.

## Control Flow
There is no runtime control flow. The header's contract separates legacy RC4 formats from the AES encrypted password format.

## State And Persistence
No state is held in the header. The implementation creates transient encrypted RPC payloads only.

## Dependencies And Integration Points
The declarations are consumed by rpcclient SAMR commands, domain join/password-change code, NetAPI user management, source4 password tooling, and SAMR torture tests. Including code must have generated SAMR and Samba base types available.

## Risks
Callers must supply valid session keys and salt sizes. The API does not encode ownership details beyond the AES `mem_ctx`, so callers must understand which output buffers are talloc-owned.

## Test Signals
Compile tests catch signature drift. Runtime coverage comes from password set/change RPC paths, AES password buffer tests, and negative tests for invalid parameters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/init_samr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/init_spoolss.c -->
# sources/user-network-fs/samba/source3/rpc_client/init_spoolss.c

## Purpose
`init_spoolss.c` provides spoolss structure conversion and default-construction helpers shared by RPC client/server printing code. It handles time/version parsing, printer-data NDR unions, `PrinterInfo2` to `SetPrinterInfo2` mapping, driver-info normalization to level 8, default devmode creation, default printer security descriptors, environment shortening, and user-level initialization.

## Important APIs, Types, And Functions
Exports are `init_systemtime()`, `spoolss_Time_to_time_t()`, `spoolss_timestr_to_NTTIME()`, `spoolss_driver_version_to_qword()`, `pull_spoolss_PrinterData()`, `push_spoolss_PrinterData()`, `spoolss_printerinfo2_to_setprinterinfo2()`, `driver_info_ctr_to_info8()`, `spoolss_create_default_devmode()`, `spoolss_create_default_secdesc()`, `spoolss_get_short_filesys_environment()`, and `spoolss_init_spoolss_UserLevel1()`.

## Control Flow
The conversion helpers perform direct field mapping or NDR union push/pull. `driver_info_ctr_to_info8()` switches on add-driver levels 3, 6, and 8, copying progressively richer fields into a normalized `spoolss_DriverInfo8`. `spoolss_create_default_devmode()` allocates a minimal Letter/portrait devmode with NT4+ spec defaults. `spoolss_create_default_secdesc()` builds ACEs for Everyone print access, domain admins or domain administrator where available, builtin Administrators, and Print Operators, then creates a self-relative descriptor owned by builtin Administrators. `spoolss_init_spoolss_UserLevel1()` fills client/user strings and configurable client OS version defaults.

## State And Persistence
The file does not persist state directly, but its default devmode/security descriptor outputs are later stored in registry-backed printer metadata. It reads global loadparm values, machine/domain SID state, secrets, and DC role to shape defaults.

## Dependencies And Integration Points
Dependencies include generated spoolss NDR, security descriptor helpers, secrets, machine SID helpers, global SIDs, and loadparm. It integrates with `cli_winreg_spoolss.c`, spoolss server code, print migration, and client RPC commands.

## Risks
Default security descriptor semantics are compatibility-sensitive and depend on domain role and secrets availability. `spoolss_Time_to_time_t()` uses local `mktime()` semantics. Date parsing expects `MM/DD/YYYY`, with `01/01/1601` special-cased to zero. Driver version parsing truncates each component to 16 bits. `driver_info_ctr_to_info8()` shallow-copies most strings, so source lifetime must cover use until persisted or copied.

## Test Signals
Good coverage includes default devmode round trips, default security descriptor SID/ACE expectations in DC and member modes, driver level 3/6/8 normalization, printer-data union push/pull by registry type, date/version parse/format compatibility with `cli_winreg_spoolss.c`, and configurable spoolss client OS values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/init_spoolss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/init_spoolss.h -->
# sources/user-network-fs/samba/source3/rpc_client/init_spoolss.h

## Purpose
`init_spoolss.h` declares the spoolss initialization, conversion, and default object helpers used by print RPC client/server support code.

## Important APIs, Types, And Functions
The header exposes time conversion, driver version parsing, printer-data NDR union push/pull, `PrinterInfo2` to `SetPrinterInfo2` mapping, add-driver-info normalization, default devmode/security descriptor creation, architecture name shortening, and `spoolss_UserLevel1` initialization.

## Control Flow
There is no runtime logic. It defines a compact API surface for helpers that are implemented in `init_spoolss.c` and consumed by winreg-backed printer persistence and spoolss server routines.

## State And Persistence
The header itself stores nothing. Its declared constructors return talloc-owned structures that callers may persist through registry or RPC state.

## Dependencies And Integration Points
Consumers need generated spoolss and winreg types. Primary integration is `cli_winreg_spoolss.c`, spoolss server implementation, printing migration, and printer administration tools.

## Risks
Because the header is a shared print subsystem contract, signature changes can break several server and client paths. Callers need to respect talloc ownership and the shallow-copy behavior of conversion helpers.

## Test Signals
Compile coverage plus spoolss printer create/update, driver upload, default security descriptor, and NDR printer data tests are the strongest signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/init_spoolss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/local_np.c -->
# sources/user-network-fs/samba/source3/rpc_client/local_np.c

## Purpose
`local_np.c` connects Samba code to a local RPC named pipe served by `samba-dcerpcd`. It builds a named-pipe-auth request, connects to a Unix socket under the configured RPC pipe directory, performs the auth handshake, wraps the socket in an authenticated `tstream`, and starts `samba-dcerpcd` on demand when permitted and not already running.

## Important APIs, Types, And Functions
Public APIs are `local_np_connect_send()`, `local_np_connect_recv()`, and synchronous `local_np_connect()`. Internal async state machines are `np_sock_connect_send()/recv()` for socket connection/auth, and `start_rpc_host_send()/recv()` for spawning `samba-dcerpcd`. Key state structs are `np_sock_connect_state`, `start_rpc_host_state`, and `local_np_connect_state`.

## Control Flow
`local_np_connect_send()` validates the pipe name by lowercasing it and rejecting `..` or slash components, constructs `<socket_dir>/np/<pipe>`, builds a level-8 `named_pipe_auth_req`, fills transport, remote/local names and addresses, copies session info, and adds an NPA flags SID carrying `NEED_IDLE` and winbind-environment flags. It then calls `np_sock_connect_send()`.

`np_sock_connect_send()` creates a Unix socket, temporarily becomes root for connect, uses blocking connect as a workaround, switches back to nonblocking, wraps the fd in `tstream_bsd_existing_socket()`, NDR-marshals the auth request, writes it, reads a length-prefixed reply, validates level 8, and converts the stream with `tstream_npa_existing_stream()`. If initial connect fails, `local_np_connect_connected()` may spawn `samba-dcerpcd --libexec-rpcds --np-helper --ready-signal-fd=...` with `posix_spawn()` and retry once.

## State And Persistence
Runtime state is entirely per-request talloc/tevent state, socket fd ownership, copied session info, and tstream ownership. The only durable side effect is starting a helper process. It reads global configuration such as `external_rpc_pipe:socket_dir`, `rpc start on demand helpers`, dynamic config/log paths, debug level, and winbind environment.

## Dependencies And Integration Points
Dependencies include tevent async APIs, async socket connect, tsocket/tstream, named-pipe-auth NDR, NPA tstream wrappers, auth session copying, security token/SID manipulation, winbind client environment detection, loadparm, and `samba-dcerpcd`. It integrates with local RPC clients that need NCALRPC/local named-pipe access and with `source3/rpc_server/rpc_host.c`.

## Risks
The code temporarily elevates to root for Unix socket connect and process spawn, so cleanup and privilege drop paths are important. The pipe-name validation is a key path traversal guard. The initial blocking connect can stall if OS behavior changes. Adding an NPA flags SID assumes none is already present and rejects tokens containing one. On-demand spawning is intentionally disabled when config prohibits it, so callers must handle connection failure. `local_np_connect_recv()` does not call `tevent_req_received()` on success, which matches some local patterns but requires caller cleanup.

## Test Signals
Tests should cover successful connection to a running helper, start-on-demand retry, disabled start-on-demand failure, invalid pipe names, long socket paths, NPA level mismatch, session-info propagation, `need_idle_server` flag propagation, winbind-off flag behavior, and synchronous wrapper cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/local_np.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/local_np.h -->
# sources/user-network-fs/samba/source3/rpc_client/local_np.h

## Purpose
`local_np.h` declares the API for connecting to local Samba RPC named pipes through `samba-dcerpcd` and authenticated `tstream` transport.

## Important APIs, Types, And Functions
It declares async `local_np_connect_send()`, `local_np_connect_recv()`, and synchronous `local_np_connect()`. Parameters capture pipe name, DCE/RPC transport type, remote/local endpoint identity, auth session info, need-idle-server flag, and output `tstream_context`.

## Control Flow
No logic is implemented in the header. The async contract follows Samba's tevent send/recv pattern; the synchronous helper hides event-context allocation and polling.

## State And Persistence
The header stores no state. The implementation returns an owned `tstream_context` and may start a local helper process.

## Dependencies And Integration Points
It includes tsocket and RPC transport enum declarations, forward-declares `auth_session_info`, and is consumed by local RPC client paths that need named-pipe streams.

## Risks
Callers must keep endpoint/session inputs coherent because they are transmitted to the helper for authorization context. The sync helper can block while connecting/spawning.

## Test Signals
Compile coverage plus local named-pipe connection tests, invalid argument tests, and helper-spawn behavior validate this API.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/local_np.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/py_mdscli.c -->
# sources/user-network-fs/samba/source3/rpc_client/py_mdscli.c

## Purpose
`py_mdscli.c` exposes Samba's mdssvc client helper API to Python as module `mdscli`. It wraps Spotlight/mdssvc connection, search, result retrieval, path lookup, search close, and disconnect operations around Python talloc objects.

## Important APIs, Types, And Functions
The module defines Python types `mdscli.conn` and `mdscli.ctx.search`. Connection methods are `sharepath()`, `search(pipe, query, basepath)`, and `disconnect(pipe)`. Search methods are `get_results(pipe)` and `close(pipe)`. Constructors are `conn_new()` and `search_new()`, and `MODULE_INIT_FUNC(mdscli)` registers both types. It uses `mdscli_connect/search/get_results/get_path/close_search/disconnect` async send/recv functions.

## Control Flow
Every method validates that `pipe` is a `samba.dcerpc.base.ClientConnection`, extracts the underlying `dcerpc_InterfaceObject`, retrieves the talloc-backed C context from `self`, starts the relevant mdssvc async request on `pipe->ev`, polls that same event context, then converts NTSTATUS failures to Python exceptions. `search_get_results()` loops while the server returns `NT_STATUS_PENDING`, sleeping one second between polls, then maps CNIDs to paths by issuing `mdscli_get_path_send()` for each result and appending Unicode strings to a Python list.

## State And Persistence
Python objects own `struct mdscli_ctx` and `struct mdscli_search_ctx` through pytalloc. No durable state is stored by this wrapper, but server-side mdssvc search contexts must be closed or disconnected through the wrapped API. Temporary talloc stackframes are freed on exit paths.

## Dependencies And Integration Points
Dependencies include Python C API, pytalloc, Samba Python module helpers, DCE/RPC Python utilities, tevent NTSTATUS polling, `cli_mdssvc.h`, and private mdssvc client structures. Build integration appears in `source3/wscript_build` as Python module `samba/samba3/mdscli.so`; command-line integration exists in `source3/utils/mdsearch.c` for the C client side.

## Risks
The wrapper deliberately avoids sync mdssvc helpers because Python DCE/RPC bindings use a specific event context; using the wrong context can hang. `search_get_results()` sleeps and repolls synchronously, which can block Python callers. Some paths raise through macros after allocating Python objects, so reference cleanup must remain careful. Constructors accept raw strings for share/mountpoint/query/basepath and depend on lower layers for semantic validation.

## Test Signals
Signals include Python import/type construction, invalid pipe type errors, mdssvc connect/search/result path mapping against a test share with Spotlight enabled, pending-result polling, no-more-matches handling, close/disconnect idempotence, and Python reference leak checks around error paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/py_mdscli.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/rpc_client.h -->
# sources/user-network-fs/samba/source3/rpc_client/rpc_client.h

## Purpose
`rpc_client.h` defines the source3 RPC pipe client object shape and internal/external visibility boundary for RPC client internals.

## Important APIs, Types, And Functions
The central type is `struct rpc_pipe_client`, with list links, printer username, destination host, slash server name, public `dcerpc_binding_handle`, and conditionally hidden internals. Internals include named-pipe `cli_state`, association/connection pointers, auth data, presentation context id, interface table, transfer syntax, and verified-pcontext flag. Macros `SOURCE3_LIBRPC_INTERNALS_BEGIN/END` hide internals unless `SOURCE3_LIBRPC_INTERNALS` is defined.

## Control Flow
The header has no runtime control flow. It controls compile-time access to structure fields and includes RPC/ndr/transport definitions needed by client implementations.

## State And Persistence
`rpc_pipe_client` is runtime connection state only. It tracks RPC association, binding, authentication, selected NDR interface, and transport linkage; it does not persist to disk.

## Dependencies And Integration Points
It depends on generated DCE/RPC types, `librpc/rpc/dcerpc.h`, NDR helpers, and `rpc_transport.h`. It is integrated with `cli_pipe.c`, pipe authentication, named-pipe transports, and higher-level RPC client commands.

## Risks
The conditional field-hiding pattern means code compiled without internals should not depend on layout. Any change to `rpc_pipe_client` internals can affect source3 RPC connection setup, authentication, and presentation-context verification.

## Test Signals
Compile coverage across internal and external users is key. Runtime signals are successful RPC bind/auth/call paths over all supported transports and tests that exercise printer-specific username/destination fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/rpc_client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/rpc_transport.h -->
# sources/user-network-fs/samba/source3/rpc_client/rpc_transport.h

## Purpose
`rpc_transport.h` defines the asynchronous transport abstraction used by source3 RPC clients to move DCE/RPC PDUs over sockets, SMB named pipes, or generic tstreams.

## Important APIs, Types, And Functions
The core type is `struct rpc_cli_transport`, with transport kind, async `read_send/read_recv`, `write_send/write_recv`, optional transact-style `trans_send/trans_recv`, connection check, timeout setter, and private state pointer. It declares constructors `rpc_transport_np_init_send/recv()`, `rpc_transport_sock_init()`, `rpc_transport_tstream_init()`, and accessor `rpc_transport_get_tstream()`.

## Control Flow
No runtime logic is in the header. The abstraction lets `cli_pipe.c` issue reads/writes or use the optional named-pipe transact optimization when available.

## State And Persistence
The struct holds runtime transport state and callbacks only. Persistence is outside this layer.

## Dependencies And Integration Points
It depends on `librpc/rpc/dcerpc.h`, `cli_state`, tevent, and tstream types. Implementations are `rpc_transport_np.c`, `rpc_transport_sock.c`, and `rpc_transport_tstream.c`; consumers include RPC bind/call code and WSP/mdssvc clients.

## Risks
Callback contracts allow short reads/writes, so callers must handle fragmentation. `trans_send` is optional, and fallback paths must remain tested. Timeout semantics can differ by concrete transport.

## Test Signals
Transport tests should exercise read/write over socket and named pipe, optional transact use over SMB named pipes, timeout changes, disconnection detection, short I/O handling, and constructor failure cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/rpc_transport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/rpc_transport_np.c -->
# sources/user-network-fs/samba/source3/rpc_client/rpc_transport_np.c

## Purpose
`rpc_transport_np.c` initializes an RPC transport over an SMB named pipe by opening the pipe on an existing `cli_state` connection and wrapping the resulting `tstream` in the common RPC transport abstraction.

## Important APIs, Types, And Functions
Exports are `rpc_transport_np_init_send()` and `rpc_transport_np_init_recv()`. Internal state `rpc_transport_np_init_state` tracks the chosen SMB session/tree, pid for SMB1, connection, timeout, absolute timeout, pipe name, retry count, event context, and final `rpc_cli_transport`.

## Control Flow
The send function selects SMB2 or SMB1 session/tcon fields from `cli_state`, strips leading backslashes from the pipe name, computes an absolute timeout, and starts `tstream_smbXcli_np_open_send()`. Completion receives a `tstream_context`. If the server returns `NT_STATUS_PIPE_NOT_AVAILABLE` before timeout expiry, it schedules a retry timer with increasing delay, matching Windows on-demand pipe server behavior. On success it calls `rpc_transport_tstream_init()` and completes.

## State And Persistence
State is per-request only. It does not persist anything, but it relies on the existing SMB connection/session/tree state staying alive for the transport.

## Dependencies And Integration Points
Dependencies include tevent NTSTATUS helpers, SMBX client base, named-pipe tstream helpers, `cli_state`, and `rpc_transport_tstream_init()`. It is used by generic RPC pipe setup and WSP client code for named-pipe RPC.

## Risks
Retry delay starts at `100 * retries` milliseconds while `retries` is incremented after scheduling, so the first retry can be immediate. The absolute timeout derives from `cli->timeout`; incorrect timeout values can cause too many retries or premature failure. Lifetime depends on the underlying SMB objects. Pipe-name normalization mutates the talloc string pointer by advancing past backslashes, so only the normalized pointer is retained.

## Test Signals
Tests should cover SMB1 and SMB2 pipe opens, leading backslash normalization, pipe-not-available retry until success, timeout expiry, constructor cleanup on open failure, and successful transact-enabled RPC over the returned transport.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/rpc_transport_np.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/rpc_transport_sock.c -->
# sources/user-network-fs/samba/source3/rpc_client/rpc_transport_sock.c

## Purpose
`rpc_transport_sock.c` adapts an existing socket file descriptor into the common RPC transport abstraction.

## Important APIs, Types, And Functions
The single export is `rpc_transport_sock_init(TALLOC_CTX *mem_ctx, int fd, struct rpc_cli_transport **presult)`. It uses `set_blocking(fd, false)`, `tstream_bsd_existing_socket()`, and `rpc_transport_tstream_init()`.

## Control Flow
The function marks the fd nonblocking, wraps it as a BSD `tstream_context`, then delegates to the tstream transport initializer. On tstream transport initialization failure it frees the intermediate stream and returns the NTSTATUS error.

## State And Persistence
No persistent state exists. Ownership of the fd moves into the tstream on success, and then into the RPC transport state.

## Dependencies And Integration Points
It depends on tsocket/tstream support and `rpc_transport_tstream.c`. It is used wherever source3 RPC clients already have a connected socket rather than an SMB named pipe.

## Risks
`set_blocking()` return is not checked, so a failure to mark nonblocking may only appear later as I/O behavior. Callers must pass a valid connected fd and must not close it after successful initialization. Transact optimization is unavailable for plain sockets because the tstream transport only enables it for SMB named-pipe streams.

## Test Signals
Socketpair-based tests should verify successful initialization, nonblocking I/O, failed wrapping on invalid fds, cleanup on `rpc_transport_tstream_init()` failure, and read/write behavior through the common transport.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/rpc_transport_sock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/rpc_transport_tstream.c -->
# sources/user-network-fs/samba/source3/rpc_client/rpc_transport_tstream.c

## Purpose
`rpc_transport_tstream.c` implements the generic `rpc_cli_transport` callbacks on top of Samba `tstream_context`. It provides queued asynchronous reads, writes, timeout handling, connection checks, and an SMB named-pipe transact optimization.

## Important APIs, Types, And Functions
Public functions are `rpc_transport_tstream_init()` and `rpc_transport_get_tstream()`. Internal state `rpc_tstream_state` owns the stream, read queue, write queue, and timeout. Callback implementations are `rpc_tstream_read_send/recv()`, `rpc_tstream_write_send/recv()`, `rpc_tstream_trans_send/recv()`, `rpc_tstream_is_connected()`, and `rpc_tstream_set_timeout()`.

## Control Flow
Initialization creates a transport, state, read/write tevent queues, moves in the caller's stream, sets a 10-second default timeout, installs read/write callbacks, and enables transact callbacks only when `tstream_is_smbXcli_np()` is true. Reads use `tstream_readv_pdu_queue_send()` with a one-vector provider capped at `UINT16_MAX`. Writes use `tstream_writev_queue_send()`. Both set endtimes and disconnect the stream on lower-level failure.

`rpc_tstream_trans_send()` checks whether the stream is connected and whether both queues are empty; only then does it ask SMB named-pipe tstream to use transact. It starts write and read requests in parallel on the respective queues, reads up to `max_rdata_len`, and returns the reply buffer.

## State And Persistence
State is runtime-only and talloc-owned under the transport. Failures free the stream to mark disconnection. Timeout is stored in milliseconds and may also be propagated to SMB named-pipe tstreams.

## Dependencies And Integration Points
Dependencies include tevent queues, tstream APIs, SMB named-pipe tstream helpers, NTSTATUS/unix error mapping, and `cli_pipe.c`. It is the common backend for socket and named-pipe transports.

## Risks
The read vector caps a single read to `UINT16_MAX`, so higher layers must be prepared for short reads. In the transact receive path, `rep.iov_len` remains the requested max length rather than the actual byte count returned by `tstream_readv_pdu_queue_recv()`, which is a subtle contract worth checking against consumers. Endtime setup failures return a posted request without an explicit error in some paths. Disconnection is represented by freeing the stream, so callbacks must not use stale stream pointers after an error.

## Test Signals
Tests should cover queued concurrent read/write ordering, timeout expiry, disconnect detection for SMB named pipes and generic streams, short read handling, transact use only when queues are empty, reply length correctness, and `set_timeout()` behavior on connected and disconnected streams.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/rpc_transport_tstream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/util_netlogon.c -->
# sources/user-network-fs/samba/source3/rpc_client/util_netlogon.c

## Purpose
`util_netlogon.c` provides deep-copy and mapping helpers for Netlogon validation and domain-controller discovery structures. It is used to move authentication validation data between NETLOGON union levels and Samba server-info/auth layers without aliasing caller-owned memory.

## Important APIs, Types, And Functions
Exports are `copy_netr_SamBaseInfo()`, `copy_netr_SamInfo3()`, `copy_netr_SamInfo6()`, `map_validation_to_info3()`, `map_validation_to_info6()`, `map_info3_to_validation()`, `map_info6_to_validation()`, and `copy_netr_DsRGetDCNameInfo()`. The `COPY_LSA_STRING` macro duplicates optional LSA string fields.

## Control Flow
Base copy starts with a struct assignment, then deep-copies all pointer fields: account/full names, scripts, profile/home paths, group RID arrays, logon server/domain strings, and domain SID. Info3 and Info6 copy helpers allocate a fresh target, copy base info, then deep-copy extra SID arrays; Info6 also copies DNS domain and principal name. Validation mapping switches on validation level 3 or 6, either deep-copying the matching structure or constructing the other shape from the common base plus SID array. Info-to-validation helpers allocate a `union netr_Validation`, copy the info structure into the proper arm, and set validation level. DC name info copy duplicates all string fields, allowing optional forest/site names to remain NULL.

## State And Persistence
The file has no persistent state. All returned structures are talloc-owned under caller contexts. It intentionally avoids pointer aliasing from source validation data.

## Dependencies And Integration Points
Dependencies include generated Netlogon types, Samba security/SID helpers, talloc, and NTSTATUS memory macros. Callers include rpcclient Netlogon commands, winbind dual server handling, auth/server-info conversion paths, and code that copies DC locator results.

## Risks
The initial struct assignment in `copy_netr_SamBaseInfo()` copies pointer values before replacing known pointer fields; future generated struct changes could add pointer fields that require explicit deep-copy updates. The mapping helpers only accept validation levels 3 and 6 and return `NT_STATUS_BAD_VALIDATION_CLASS` otherwise. Output pointers are not cleared on failure, so callers should only consume them on OK status.

## Test Signals
Tests should verify deep-copy independence by freeing source structures after copy, level 3/6 validation mapping in both directions, SID and group array preservation, optional Info6 DNS/principal fields, unsupported validation-level errors, null validation errors, and DC locator copy behavior with optional NULL forest/site fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/util_netlogon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/util_netlogon.h -->
# sources/user-network-fs/samba/source3/rpc_client/util_netlogon.h

## Purpose
`util_netlogon.h` declares Netlogon copy and validation mapping helpers for authentication and RPC client code.

## Important APIs, Types, And Functions
It declares deep-copy helpers for `netr_SamBaseInfo`, `netr_SamInfo3`, `netr_SamInfo6`, and `netr_DsRGetDCNameInfo`, plus conversion helpers between `union netr_Validation` levels and concrete SamInfo3/SamInfo6 structures.

## Control Flow
No logic is implemented in the header. The API follows NTSTATUS-returning C helper conventions with talloc contexts and output pointers.

## State And Persistence
The header stores no state. Implementations allocate transient copied structures for callers.

## Dependencies And Integration Points
Consumers must include generated Netlogon types. The helpers are integrated with winbind, auth server-info conversion, rpcclient Netlogon commands, and DC locator handling.

## Risks
The contract is limited to validation levels 3 and 6. Callers must check NTSTATUS before using output pointers and must manage talloc ownership.

## Test Signals
Compile coverage plus Netlogon validation mapping tests, auth server-info conversion tests, and DC locator copy tests validate the API.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/util_netlogon.h -->

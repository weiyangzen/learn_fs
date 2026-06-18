# Research Group subset-b-007699

This grouped report covers the Windows OpenAFS authentication, logon, RPC token, share, and cache-manager access files assigned to `subset-b-007699`. Each file section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afskfw.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/afskfw.c

## Purpose
`afskfw.c` is the Kerberos for Windows integration layer that bridges Kerberos v5 credential caches, Microsoft LSA Kerberos credentials, and OpenAFS token management on Windows. It initializes delayed Kerberos libraries, imports credentials, maps principals to cells, renews tickets/tokens, obtains AFS service tickets, converts them into `ktc_token` records, and installs those tokens into the running `TransarcAFSDaemon` cache manager.

## Important APIs, Types, And Functions
The public API exported through `afskfw.h` includes `KFW_initialize`, `KFW_is_available`, `KFW_AFS_get_cred`, token destroy/renew helpers, service-start wait, KDC probe, cellconfig lookup, LSA principal lookup, file-cache ACL helpers, cache-copy helpers, and default realm lookup. Internal state is organized by `struct principal_ccache_data` and `struct cell_principal_map` from `afskfw-int.h`: one list tracks principal-to-ccache metadata, LSA origin, expiration, and renewability; the other tracks which principal has active tokens for each cell. The core credential path is `KFW_AFS_get_cred` -> `KFW_kinit` when a password is supplied -> `KFW_AFS_klog` to acquire and install AFS tokens. `KFW_import_windows_lsa`, `KFW_import_ccache_data`, `KFW_AFS_update_princ_ccache_data`, `KFW_AFS_update_cell_princ_map`, `KFW_AFS_renew_expiring_tokens`, and `KFW_AFS_renew_token_for_cell` keep process-local credential metadata synchronized with existing Kerberos caches and installed AFS tokens.

## Control Flow
Initialization is guarded by a named mutex and a static flag. `KFW_initialize` delay-loads Kerberos/Heimdal glue, enables DES support, optionally imports Microsoft LSA credentials, scans all ccaches, renews expiring tokens, and renews the root-cell token. Availability is registry-gated by `EnableKFW` under current-user then local-machine OpenAFS keys, then by whether Kerberos function pointers were loaded.

Credential acquisition begins by resolving OpenAFS cell configuration via registry, cellservdb, or DNS. The code derives a Kerberos realm from host realm lookup or uppercase cell name, normalizes dotted usernames when configured for Kerberos 4 compatibility, resolves or creates a principal-specific ccache, performs `krb5_get_init_creds_password` when a password is available, and calls `KFW_AFS_klog`. `KFW_AFS_klog` checks that `TransarcAFSDaemon` is running, builds service principals in fallback order (`afs/cell@clientrealm`, `afs/cell@cellrealm`, `afs@cellrealm`), converts the returned Kerberos v5 ticket into an rxkad v5 token with a derived DES session key, avoids reinstalling an identical token, optionally maps or registers the user through pts, and calls `ktc_SetToken`.

Renewal uses the in-memory principal ccache list. Entries close to expiration are renewed with `krb5_get_renewed_creds`, then all active cells mapped to that principal are re-klogged. LSA-origin entries are treated specially because Microsoft can refresh TGTs outside this process. Destruction by cell or principal destroys MIT ccaches only when doing so will not obviously break other active cell mappings, then marks mappings inactive.

## State And Persistence
Most state is process-local linked-list state, not persisted directly: principal cache metadata and cell-principal mappings are rebuilt by scanning Kerberos ccaches and installed AFS tokens. Persistent configuration comes from Windows registry OpenAFS settings, Kerberos profile/appdefaults, cell registry/cellservdb/DNS cell lookup, and the Microsoft LSA cache. Credential cache persistence depends on Kerberos ccache type: API/MSLSA caches and temporary FILE ccaches are used. `KFW_AFS_copy_cache_to_system_file`, `KFW_AFS_set_file_cache_dacl`, `KFW_AFS_obtain_user_temp_directory`, and `KFW_AFS_copy_file_cache_to_default_cache` support copying credential caches between SYSTEM and user contexts with protected ACLs. Tokens themselves are stored by the cache manager through `ktc_SetToken` and removed with `ktc_ForgetAllTokens` or ccache destruction paths.

## Dependencies And Integration Points
This file depends on Windows registry, SCM, LSA, security descriptors, Userenv, SSPI-era security APIs, delayed Kerberos/Heimdal compatibility APIs, OpenAFS cell configuration, ptserver, ktc token APIs, rxkad token formats, cache-manager root-cell lookup, and the `TransarcAFSDaemon` service. It integrates directly with `afslogon.c` for integrated Windows logon, with cache-manager token state via `ktc_*`, and with registry knobs such as `EnableKFW`, `AcceptDottedPrincipalNames`, and Kerberos ticket lifetime settings.

## Risks And Edge Cases
The process-local linked lists are not protected by explicit locks outside initialization, so multi-threaded callers could race map and cache updates. Several delete loops update the list pointer without advancing on nonmatching nodes, which makes correctness dependent on the first entry matching or external call patterns. The service wait loop uses a logically impossible condition (`running || stopped` negated with `||`) but returns internally on concrete states, so behavior relies on the body exits. Kerberos principal fallback and dotted-name conversion are compatibility-sensitive. AFS token installation requires DES key derivation for rxkad compatibility, which is security-sensitive and legacy. Registry and ccache buffer handling is mostly bounded by StringCb/StringCch calls, but many paths continue after partial failures and use static buffers for returned reasons or realms.

## Test Signals
Useful tests include registry-gated `KFW_is_available` behavior, LSA import modes, root-cell and explicit-cell lookup through registry/file/DNS, dotted-principal conversion, password kinit plus token install, service-not-running error paths, service-principal fallback order, token renewal near expiration, multi-cell token refresh for one principal, destroy-by-cell preserving shared principals, protected FILE ccache ACL creation, and KDC probing return-code classification. Integration tests need a running Windows OpenAFS client, a reachable Kerberos realm, and assertions against installed `ktc` tokens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afskfw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afskfw.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/afskfw.h

## Purpose
`afskfw.h` is the public interface for the Windows Kerberos for Windows/OpenAFS bridge implemented by `afskfw.c`. It exposes initialization, availability checks, credential acquisition, token renewal/destruction, cell configuration, LSA principal access, and file credential-cache helper routines to the Windows logon provider and related utilities.

## Important APIs, Types, And Constants
The header imports OpenAFS authentication, cell configuration, cache-manager config, and rxkad definitions. It defines cell and host size constants (`CELL_MAXNAMELEN`, `MAXHOSTCHARS`, `MAXHOSTSPERCELL`), the AFSD service name `TRANSARCAFSDAEMON`, Kerberos/AFS compatibility error values, probe credentials (`PROBE_USERNAME`, `PROBE_PASSWORD_LEN`), and `DO_NOT_REGISTER_VARNAME`, which suppresses pts auto-registration during selected logon paths. Exported functions include `KFW_AFS_get_cred`, `KFW_AFS_renew_expiring_tokens`, `KFW_AFS_renew_token_for_cell`, `KFW_AFS_destroy_tickets_for_cell`, `KFW_AFS_destroy_tickets_for_principal`, `KFW_probe_kdc`, `KFW_AFS_get_cellconfig`, and SYSTEM/user ccache copy helpers reserved for `afslogon.dll`.

## Control Flow And Integration
The header separates general KFW operations from `afslogon.dll`-only cache migration calls. Consumers typically call `KFW_is_available` or `KFW_initialize`, then use `KFW_AFS_get_cred` for integrated token creation, renewal functions during credential maintenance, and destroy helpers at logoff or explicit unlog. `afslogon.c` uses this contract to choose between KFW and legacy `ka_UserAuthenticateGeneral2`.

## State And Persistence
No storage is declared here, but the API implies three persistent surfaces: registry-configured KFW behavior, Kerberos ccaches including LSA and FILE caches, and installed AFS tokens. The cache copy helpers indicate cross-logon-session movement of credential files with Windows ACL protection.

## Dependencies, Risks, And Test Signals
Because the header exposes Windows types such as `BOOL`, `DWORD`, and `HANDLE`, it is Windows-only and must be included after suitable platform headers in consumers. Risks are mainly ABI drift: declarations here must match `afskfw.c` and any delayed Kerberos compatibility signatures. Test signals are compile coverage for all consumers, integrated logon using `KFW_AFS_get_cred`, logoff cleanup via destroy helpers, LSA principal lookup, and file ccache copy behavior under restricted user tokens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afskfw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afslogon.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/afslogon.c

## Purpose
`afslogon.c` implements the OpenAFS Windows network provider and Winlogon notification behavior. It participates in Windows interactive logon, reads domain/user OpenAFS logon policy from the registry, starts or waits for the OpenAFS service, creates authentication groups/PAGs, obtains AFS tokens using either KFW or legacy kaserver authentication, returns optional logon scripts, and removes or preserves tokens at logoff depending on policy and profile location.

## Important APIs And Functions
Network-provider entry points are `DllEntryPoint`, `NPGetCaps`, `NPLogonNotify`, and `NPPasswordChangeNotify`. Winlogon event handlers include `AFS_Startup_Event`, `AFS_Logon_Event`, `AFS_Logoff_Event`, and optional `KFW_Logon_Event`. Support functions include `AfsLogonInit`, `DebugEvent`, `AFSWillAutoStart`, `IsServiceRunning`, `IsServiceStartPending`, `StartTheService`, `FindFullDomainName`, `GetDomainLogonOptions`, `GetFileCellName`, `UnicodeStringToANSI`, `ObtainTokens`, `IsPathInAfs`, and `NetUserGetProfilePath`.

`LogonOptions_t` from `afslogon.h` is the central configuration carrier: logon option bits, fail-silent behavior, retry/sleep intervals, SMB name, logon script, flags (`LOCAL`, `REMOTE`, `AD_REALM`, `LSA`), extra cells, mapped username, and realm.

## Control Flow
On DLL attach the module starts Winsock and creates an initialization mutex. `AfsLogonInit` initializes OpenAFS path state and only initializes legacy `ka` state when KFW is unavailable. `NPLogonNotify` handles MSV1_0 and Kerberos interactive logons. It loads trace/debug flags, converts the Windows interactive logon structure from Unicode, strips a realm embedded in the username if present, reads effective domain/user configuration, sets the returned logon script, determines whether AFSD is autostart, obtains the root cell for integrated logon, optionally checks AD home-path cell placement, creates a PAG/auth group, starts AFSD if needed, then loops while the service is starting/running and retries token acquisition until success, timeout, or an unretryable error.

`ObtainTokens` impersonates the logon security context, uses KFW when available, imports LSA credentials when the username/realm maps directly to the LSA Kerberos principal, builds `user@realm`, obtains a token for the selected cell, and optionally obtains tokens for each configured `TheseCells` entry. Without KFW, it calls `ka_UserAuthenticateGeneral2`. After integrated KFW logon, `NPLogonNotify` destroys SYSTEM-held tickets for the user, maps errors to network-provider status, clears logon scripts on hard integrated failures, frees allocated option strings, and zeroes the password.

Logoff behavior reads `LogoffPreserveTokens`. If tokens should be removed, remote logons try to discover the profile path through AD SID lookup, local domain fallback, NetUser profile lookup, or user profile directory. Tokens are preserved when the profile is in AFS to avoid breaking profile unload; otherwise `ktc_ForgetAllTokens` removes them. `AFS_Logon_Event` also establishes a WNet connection to the local AFS redirector using the LSA principal or domain username.

## State And Persistence
Persistent input is almost entirely registry policy under OpenAFS service/provider keys and per-domain/per-user subkeys. `LogonScript`, `TheseCells`, username mapping, realm mapping, retry timing, fail-silent policy, trace/debug settings, logoff token preservation, and integrated-logon enablement are registry-controlled. Runtime state includes global `TraceOption`, `Debug`, DLL init state, the AFSD service state, Windows logon LUID/security context, token state in the cache manager, and optional logon script memory returned to MPR/Winlogon. Passwords are stack-buffered and cleared before return.

## Dependencies And Integration Points
The file depends on Windows MPR/network-provider APIs, Winlogon notification structures, LSA, SSPI, NetAPI, registry APIs, service-control APIs, Userenv, WNet, OpenAFS pioctl, ktc/kautils, `afskfw` KFW routines, `logon_ad.cpp` helpers (`LogonSSP`, `AFSCreatePAG`, AD home-path queries), and cache-manager root-cell lookup. It is the main consumer of `afskfw.h` in this subset.

## Risks And Edge Cases
Logon code runs in sensitive Windows authentication paths, so hangs, UI prompts, or service waits can affect desktop availability. Registry lookup is intentionally permissive and falls back through user/domain/global keys, which can make policy precedence hard to reason about. Several conversions reject multibyte ANSI code pages, limiting non-ASCII usernames/domains. The service-start loop uses short sleeps and retry counters; incorrect service state can produce silent skips depending on `failSilently`. Some allocated fields such as `opt.username` are not freed on all paths visible in this file, while `opt.logonScript` ownership transfers to Windows unless later freed on failure. Authentication failure mapping avoids `WN_NO_NETWORK` to keep other providers' scripts running, which means callers see a broader network error.

## Test Signals
Test with KFW enabled/disabled, MSV1_0 and Kerberos interactive payloads, local versus remote domains, username containing `@realm`, registry precedence for domain/user/provider keys, `TheseCells` multi-cell acquisition, autostart service startup/retry/failure, fail-silent versus interactive warning behavior, empty passwords, AD home directory in and out of AFS, logoff token preservation with AFS profiles, logon script expansion with `%s`, and secure password zeroing/error cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afslogon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afslogon.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/afslogon.h

## Purpose
`afslogon.h` declares the Windows network-provider interface and shared logon configuration structures for OpenAFS integrated logon. It centralizes registry value names, default policy values, trace/logon flag macros, length limits, exported NP entry points, debugging helpers, and AD/PAG helper prototypes used by `afslogon.c` and companion logon modules.

## Important APIs, Types, And Constants
Registry constants cover service/provider domain configuration, retry and sleep intervals, fail-silent policy, trace/debug flags, logon options, logon script, realm, username mapping, `TheseCells`, and logoff token preservation. `LogonOptions_t` carries effective policy and allocated strings for one logon. Macros classify trace (`ISLOGONTRACE`), integrated logon (`ISLOGONINTEGRATED`), and flags for remote, AD realm, and LSA credentials. Public declarations include `DllEntryPoint`, `NPGetCaps`, `NPLogonNotify`, `NPPasswordChangeNotify`, debug functions, service status helpers, `GetDomainLogonOptions`, cell/home-path lookup helpers, `AFSCreatePAG`, and `LogonSSP`.

## Control Flow And Integration
The header is consumed by the network-provider DLL implementation and AD helper code. `afslogon.c` fills `LogonOptions_t` from registry policy, passes it into token acquisition and home-path discovery, and uses the declared external helper functions to impersonate logon sessions and create auth groups.

## State, Dependencies, Risks, And Test Signals
This header has no storage besides `extern DWORD TraceOption`, but its struct contains owning pointers that callers must free consistently. It depends on Windows NPAPI, SSPI context handles, LSA/security types, and OpenAFS conventions. ABI risks include static declaration of `UnicodeStringToANSI` in a header and tight coupling to registry string names. Test signals are compile coverage across C/C++ consumers, correct struct initialization/freeing, registry value compatibility, and network-provider entry-point signature matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afslogon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsrpc.idl -->
# sources/distributed-fs/openafs/src/WINNT/afsd/afsrpc.idl

## Purpose
`afsrpc.idl` defines a small Microsoft RPC interface named `afsrpc` for setting and retrieving an 8-byte AFS session key associated with a UUID. It is part of Windows-specific token/session-key exchange support.

## Important APIs And Types
The interface uses an implicit binding handle `hAfsHandle`, UUID `2131bed0-5484-11d2-b6c6-006097221e3d`, and version `1.0`. It declares a local copy of a DCE-style UUID structure as `afs_uuid_t`. The two remote procedures are `AFSRPC_SetToken([in] afs_uuid_t uuid, [in] unsigned char sessionKey[8])` and `AFSRPC_GetToken([in] afs_uuid_t uuid, [out] unsigned char sessionKey[8])`, both returning `long` status codes.

## Control Flow, State, And Integration
The IDL only specifies the wire contract. Runtime behavior depends on generated MIDL stubs and server/client implementations elsewhere in the Windows AFSD tree. Conceptually, callers bind through `hAfsHandle`, identify a token/session by UUID, and exchange the fixed rxkad/DES-sized session key. State is external to this file and likely lives in the RPC server or cache-manager process.

## Dependencies, Risks, And Test Signals
The file depends on Microsoft RPC/MIDL semantics and DCE UUID layout compatibility. The fixed 8-byte key size reflects rxkad/DES-era token material and should be treated as legacy-sensitive. Test signals include MIDL generation, client/server ABI compatibility, successful set/get round trips for multiple UUIDs, not-found handling, and access-control checks in the implementation using these stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsrpc.idl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsshare.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/afsshare.c

## Purpose
`afsshare.c` implements the `afsshare.exe` utility for creating, updating, or deleting OpenAFS Windows submount registry entries. A submount maps a short share-like name to an AFS mount path relative to the configured mount root when possible.

## Important APIs And Control Flow
`main` accepts `afsshare.exe <submount> [<afs mount path>]`. With only a submount argument, it deletes that value from `HKLM\<OpenAFS>\Submounts`. With a path argument, it reads `MountRoot` from the AFSD service parameters, strips that prefix from the requested AFS path if present, and writes the resulting string as a `REG_EXPAND_SZ` value named by the submount. Registry opens use `KEY_WOW64_64KEY` when running under WOW64, via `IsWow64()`.

## State And Persistence
All persistent state is in HKLM OpenAFS registry keys. The tool writes nonvolatile submount values and reads the service `MountRoot`, defaulting to `/afs` when the setting is unavailable. It does not contact the cache manager or validate that the target AFS path exists.

## Dependencies, Risks, And Test Signals
The utility depends on Windows registry APIs, OpenAFS registry path macros, and administrator permissions to modify HKLM. Risks include accepting arbitrary submount/value names, no path validation, and behavior differences under 32-bit processes on 64-bit Windows if WOW64 redirection is wrong. Test signals include argument count errors, deletion success/failure codes, setting a path under and outside `MountRoot`, missing `MountRoot` fallback, access denied handling, and 32-bit/64-bit registry view behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/afsshare.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cklog.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cklog.c

## Purpose
`cklog.c` implements a Windows command-line authentication utility equivalent to `klog` for obtaining AFS kaserver credentials. It parses username, password, cell, lifetime, and behavior flags, authenticates through `ka_UserAuthenticateGeneral`, and optionally supports legacy ticket-file output when not built for `AFS_KERBEROS_ENV`.

## Important APIs And Functions
The executable initializes Winsock, uses the OpenAFS `cmd` parser, and defines `CommandProc` as the command handler. Supported options are `-principal`, `-password`, `-cell`, `-servers` (reported unavailable), `-pipe`, `-silent`, `-lifetime`, `-setpag`, and `-tmp`; `-x` is obsolete/no-op. Helper functions are `getpipepass`, bounded `good_gets`, and `read_pw_string`, which disables console echo while reading a password.

## Control Flow
`main` creates syntax, registers options, dispatches, and exits with the command code. `CommandProc` clears command-line arguments to reduce password exposure, determines silent/pipe/setpag/tmp modes, initializes the local cell and ka library, parses explicit cell and principal values, falls back to `USERNAME` or `GetUserName`, copies and clears any password argument, parses lifetime in `hh[:mm[:ss]]`, reads the password from stdin or no-echo console when needed, calls `ka_UserAuthenticateGeneral`, clears the password buffer, and returns the authentication code.

## State And Persistence
The command changes process memory and obtains AFS authentication state through the ka/ktc stack; there is no direct registry or file persistence in the normal `AFS_KERBEROS_ENV` build. Command-line password and copied password buffers are zeroed. The `-tmp` ticket-file path is disabled under the current compile-time define.

## Dependencies, Risks, And Test Signals
Dependencies include Winsock, OpenAFS command parser, `kautils`, cell config, and Windows console APIs. Risks include legacy kaserver authentication, a declared but unused `-setpag` mode in this implementation, unsupported `-servers`, and password exposure windows before argument clearing. Test signals include principal parsing with instance/cell, long cell/password rejection, lifetime parsing boundaries, pipe and no-echo password reads, silent-mode error suppression, default username fallback, failed and successful ka authentication, and password buffer zeroing after auth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cklog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm.h

## Purpose
`cm.h` is a foundational Windows cache-manager header. In this subset it mainly establishes pthread mode, imports RX/VLDB/AFS interfaces and cache-manager errors, defines common cache-manager operation flags, volume-type indexes, the default callback port, and a shared lock hierarchy used across AFSD modules.

## Important APIs, Types, And Constants
Operation flags include creation, case folding, exclusive create, symlink following, 8.3-name restriction, mount-point suppression, directory search, path checking, no-probe cell lookup, and DFS referral handling. Volume indexes `RWVOL`, `ROVOL`, and `BACKVOL` are used as array indexes in volume structures. Lock hierarchy constants assign numeric ordering to redirector, SMB, scache, daemon, buffer, volume, user, cell, server, callback, DNLC, freelance, ACL, EACCES, token, and syscfg locks.

## Control Flow, State, And Integration
The header has no executable control flow or storage, but it affects lock initialization and ordering in files such as `cm_aclent.c`, where `cm_aclLock` uses `LOCK_HIERARCHY_ACL_GLOBAL`. Its flags are consumed by cache-manager lookup, cell, and volume operations throughout the Windows AFSD tree.

## Risks And Test Signals
The main risk is lock-order drift: changing hierarchy values can introduce deadlocks or false lock-order assertions. Flag values are ABI-like within the cache-manager code and must remain compatible with callers. Test signals are compile coverage, lock-order assertion tests, callback-port behavior, and path/namei operations that combine flags such as casefold, no-probe, and DFS referral.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_access.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_access.c

## Purpose
`cm_access.c` decides whether cached access-right information is sufficient for a user/scache request and forces status/callback fetches when it is not. It bridges public directory rights, per-user ACL cache entries from `cm_aclent.c`, Unix mode bits, DFS/per-file access policy, and callback validity.

## Important APIs And State
The exported functions are `cm_HaveAccessRights` and `cm_GetAccessRights`. Globals are `cm_deleteReadOnly`, which controls whether SMB delete is removed for read-only mode bits, and `cm_accessPerFileCheck`, which forces rights checks on the file itself instead of parent directory ACLs. Rights come from `scp->anyAccess`, per-user `cm_FindACLCache`, Unix mode bits, creator identity, and AFS PRSFS bits.

## Control Flow
`cm_HaveAccessRights` is called with the target scache write-locked and must not block on expensive fetches. It chooses the ACL scache: directories, per-file-check mode, DFS volumes, and missing volumes use the file itself; normal files use the parent directory. If the parent scache is not available or lacks a callback, it returns false so callers can stabilize and fetch. Once it has an ACL scache, it grants immediately when requested rights are covered by public `anyAccess`; otherwise it checks the per-user ACL cache. It then masks READ/WRITE/DELETE based on Unix mode bits, grants READ/WRITE when the creator has INSERT, implies LOCK from WRITE, and returns whether the answer is authoritative.

`cm_GetAccessRights` performs the blocking side. For directories/per-file/DFS cases it forces callback and status on the target. For normal files it releases the target lock, obtains the parent scache, forces callback/status on the parent, releases it, and reacquires the target lock.

## Dependencies And Integration
This file depends on scache, volume, ACL cache, callbacks, sync operations, request flags, logging, and AFS rights constants. It is called from scache/status and ioctl paths before deciding whether server RPCs are needed.

## Risks And Test Signals
The main risks are lock ordering around parent scache acquisition, stale callback use, races noted by comments, and subtle rights masking that can over- or under-grant local operations before server validation. Test signals include directory versus file checks, parent scache unavailable, callback revoked during checks, DFS volume behavior, `cm_accessPerFileCheck`, read-only delete policy for SMB, creator-with-insert behavior, write implying lock, and retry loops around `cm_GetAccessRights`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_access.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_access.h

## Purpose
`cm_access.h` declares the cache-manager access-right API used by scache and request handling code. It exposes the nonblocking cached-rights check, the blocking fetch path, and the per-file access-check configuration flag.

## APIs And Integration
`cm_HaveAccessRights(struct cm_scache *scp, struct cm_user *up, struct cm_req *reqp, afs_uint32 rights, afs_uint32 *outRights)` reports whether local cache state can answer a rights question and returns the rights found. `cm_GetAccessRights(struct cm_scache *scp, struct cm_user *up, struct cm_req *reqp)` forces the status/callback work needed to populate rights. `cm_accessPerFileCheck` is externally configured, read by `cm_access.c`, and also consulted by other cache-manager modules.

## State, Risks, And Test Signals
The header depends on `cm_user.h` for user/request type visibility and forward-visible scache declarations. Risks are mostly contract-related: callers must hold the scache lock as required by the implementation and loop around races where cached rights cannot be stabilized. Test signals are compile coverage, callers respecting lock preconditions, and runtime behavior with `cm_accessPerFileCheck` toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_access.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_aclent.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_aclent.c

## Purpose
`cm_aclent.c` implements the Windows cache-manager ACL entry cache. It stores per-user random access rights for scache objects, expires entries according to token/TGT lifetime, maintains an LRU queue over a fixed memory-mapped entry array, invalidates redirector objects/volumes when credentials change, and validates internal pointer integrity.

## Important APIs And State
The global lock is `cm_aclLock`. Main functions are `cm_InitACLCache`, `cm_FindACLCache`, `cm_AddACLCache`, `cm_FreeAllACLEnts`, `cm_InvalidateACLUser`, `cm_ResetACLCache`, `cm_ValidateACLCache`, `cm_ShutdownACLCache`, `cm_TGTLifeTime`, and internal `GetFreeACLEnt`/`CleanupACLEnt`. Entries are `cm_aclent_t` records from `cm_aclent.h` linked both in a global LRU queue and in each scache's `randomACLp` list.

## Control Flow
Initialization creates the lock once and, for a new cache file, zeroes the ACL memory region, stamps every entry with `CM_ACLENT_MAGIC`, and links all entries into the LRU queue. Reopening an existing cache clears user pointers and token lifetimes. `cm_AddACLCache` computes the user's token lifetime for the scache cell, updates an existing user entry or evicts the LRU tail, links the entry into the scache list, holds the user, stores rights and lifetime, and moves it to the LRU head. `cm_FindACLCache` scans the scache list under scache write lock and `cm_aclLock`; expired entries are cleaned and moved to the LRU tail, while hits return rights and move to the LRU head.

Invalidation can target all entries for one scache, one user on one scache, or all scaches/volumes for a user and optional cell. `cm_ResetACLCache` scans the scache hash table, invalidates matching user entries, clears EACCES cache entries, and asks the redirector to invalidate objects and volumes with `AFS_INVALIDATE_CREDS`. Validation walks the LRU queue forward and backward, checking pointer ranges, magic values, and loops.

## Dependencies And Integration
The file depends on global `cm_data` memory layout, scache/user/cell/volume structures, OpenAFS locks and queues, token/user cell state, callback checks, redirector invalidation (`RDR_InvalidateObject`, `RDR_InvalidateVolume`), and EACCES cache clearing. It is integrated with status fetches that populate `CallerAccess` and with token-change paths in user/ioctl code.

## Risks And Test Signals
Correctness depends on strict lock ordering between scache locks and `cm_aclLock`; `GetFreeACLEnt` temporarily drops and reacquires the ACL lock to lock an evicted entry's scache. Stale pointer validation assumes the memory-map region ordering of acl/scache/dnlc base addresses. Expiration depends on user token lifetime and can force server refetch after token renewal/loss. Test signals include cold and reopened cache initialization, LRU hit/miss/eviction order, expired entry cleanup, user reference hold/release balance, invalidate-one-user behavior with redirector callback, reset by cell and global reset, validation failures for corrupted queues, and token-renewal-driven ACL invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_aclent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_aclent.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_aclent.h

## Purpose
`cm_aclent.h` defines the ACL cache entry structure and declares the ACL cache API for the Windows cache manager. It is the shared contract between access checks, status population, token-change handling, and cache initialization.

## Important Types And APIs
`cm_aclent_t` contains an LRU queue node, magic value, per-scache linked-list pointer, back pointer to the scache, held user pointer, cached random access rights, and token/TGT expiration time. `CM_ACLENT_MAGIC` supports cache validation. The declared API covers initialization, lookup, allocation helper declaration, insertion/update, freeing all entries on an scache, invalidating one user, validation, shutdown, resetting entries for a cell/user, and retrieving token lifetime for a user/cell.

## State, Dependencies, And Integration
The header exposes `cm_aclLock`, which protects both global LRU state and ACL entry mutation. It depends on OpenAFS queue/lock types and cache-manager user/cell/scache types. `cm_access.c` uses lookup results to answer access-right checks; `cm_scache.c` adds entries from server status; token and ioctl paths reset ACL state when credentials change.

## Risks And Test Signals
The static `GetFreeACLEnt` prototype in a header mirrors an implementation-private helper and is unusual; it can trigger warnings or confusion if included broadly. Callers must honor implementation lock requirements even though only prototypes are visible here. Test signals are ABI-compatible struct layout for memory-mapped cache data, lock initialization, add/find/free/reset behavior, and validation catching bad magic or pointer corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_aclent.h -->

# Research: subset-b-007743

Grouped research for the OpenAFS Windows KFW dynamic loader and NetIDMgr public API headers. Each section preserves its source path for deterministic split into the final source-tree-aligned reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-krb.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-krb.h

## Purpose

This header declares the dynamically loaded Kerberos 4 (`krbv4w32.dll`) API surface used by OpenAFS Windows/KFW integration. It does not implement Kerberos logic; it defines function-pointer typedefs through `TYPEDEF_FUNC()` so client code can bind optional KRB4 entry points at runtime instead of taking a static link dependency.

## Important APIs, Types, and Functions

- `KRB4_DLL` names the target DLL as `krbv4w32.dll`.
- `krb_err_text(status)` redirects to the dynamically bound `pget_krb_err_txt_entry(status)` pointer.
- Ticket/cache APIs include `tkt_string`, `tf_init`, `tf_get_pname`, `tf_get_pinst`, `tf_get_cred`, `tf_save_cred`, `tf_close`, `krb_set_tkt_string`, `dest_tkt`, and `krb_save_credentials`.
- Authentication and ticket construction APIs include `krb_sendauth`, `krb_mk_req`, `k_decomp_ticket`, `create_ciph`, `send_to_kdc`, and `krb_get_pw_in_tkt`.
- Principal, host, and realm helpers include `krb_getrealm`, `krb_realmofhost`, `krb_get_phost`, `krb_get_lrealm`, `krb_get_tf_fullname`, `krb_get_tf_realm`, `kname_parse`, `k_isinst`, `k_isrealm`, `k_isname`, `k_gethostname`, and `krb_get_krbhst`.
- Error/debug hooks include `get_krb_err_txt`, `get_krb_err_txt_entry`, `krb_err_func`, `set_krb_debug`, `set_krb_ap_req_debug`, `initialize_krb_error_func`, `initialize_kadm_error_table`, and `lsh_LoadKrb4LeashErrorTables`.
- Password administration and lifetime conversion include `kadm_change_your_password`, `krb_life_to_time`, and `krb_time_to_life`.

## Control Flow

The header contributes declarations to a load table elsewhere. A caller creates `FUNC_INFO` rows with `MAKE_FUNC_INFO(function_name)` and calls `LoadFuncs(KRB4_DLL, ...)`. Runtime calls then go through global pointer variables such as `pkrb_mk_req`. There is no local branching beyond preprocessor include guards and the `krb_err_text` macro.

## State and Persistence Behavior

The loaded functions operate on Kerberos 4 ticket files, credential records, realm configuration, host discovery, password state, and error-table state inside the external KRB4 and Leash DLLs. The header itself stores no state, but the pointer variables produced by `DECL_FUNC_PTR()` are process-global when defined by consumers. Ticket-file APIs are stateful and can mutate local ticket cache contents.

## Dependencies and Integration Points

Depends on `loadfuncs.h` for dynamic loading macros and on `<krb.h>` for KRB4 structures such as `KTEXT`, `CREDENTIALS`, `C_Block`, and `Key_schedule`. It integrates with Windows calling conventions (`PASCAL`, `CALLCONV_C`, `FAR`, `LPSTR`, `HANDLE`, `HMODULE`) and bridges OpenAFS to legacy Kerberos 4 and Leash functionality without requiring the DLL at process startup.

## Risks

- KRB4 support is legacy and cryptographically obsolete; callers should avoid expanding use beyond compatibility paths.
- Several functions accept raw mutable `char *` buffers and fixed-size structures; buffer lifetime and size checks are entirely caller-owned.
- The header contains duplicate `TYPEDEF_FUNC` declarations for `krb_mk_req` and `krb_getrealm`; this is benign only if the macro expansion tolerates repeated identical typedefs.
- Dynamic loading can leave some function pointers NULL if `LoadFuncs()` is called with `go_on`; every call site must guard optional symbols.
- Calling-convention mismatches against DLL exports would fail at runtime or corrupt the stack on 32-bit builds.

## Test Signals

Build tests should verify this header compiles for 32-bit and 64-bit Windows with the available KFW headers. Runtime tests should cover successful `LoadFuncs(KRB4_DLL, ...)`, missing-DLL behavior, partial symbol failures, and guarded behavior when optional KRB4 functions are absent. Integration tests should exercise ticket-file read/write paths only in an isolated test credential cache.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-krb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-krb5.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-krb5.h

## Purpose

This header declares a large dynamic-binding surface for Kerberos 5 (`krb5_32.dll` or `krb5_64.dll`). It lets OpenAFS Windows code use MIT KFW/KRB5 functions through function pointers discovered with `LoadFuncs()` rather than through static linking.

## Important APIs, Types, and Functions

- `KRB5_DLL` selects `krb5_64.dll` on `_WIN64`, otherwise `krb5_32.dll`.
- Memory ownership APIs cover `krb5_free_principal`, `krb5_free_authenticator`, `krb5_free_addresses`, `krb5_free_authdata`, `krb5_free_ticket(s)`, `krb5_free_kdc_req/rep`, `krb5_free_cred(s)`, `krb5_free_keyblock(_contents)`, `krb5_free_data(_contents)`, `krb5_free_unparsed_name`, and related free routines.
- Crypto and checksum APIs include `krb5_c_encrypt`, `krb5_c_decrypt`, `krb5_c_encrypt_length`, `krb5_c_block_size`, `krb5_c_make_random_key`, `krb5_c_random_make_octets`, `krb5_c_random_seed`, `krb5_c_string_to_key`, `krb5_c_enctype_compare`, `krb5_c_make_checksum`, `krb5_c_verify_checksum`, and `krb5_c_keyed_checksum_types`.
- Context, principal, realm, and configuration APIs include `krb5_init_context`, `krb5_free_context`, `krb5_parse_name`, `krb5_unparse_name`, `krb5_set_principal_realm`, `krb5_principal_compare`, `krb5_build_principal(_ext)`, `krb5_get_default_realm`, `krb5_set_default_realm`, `krb5_get_host_realm`, `krb5_get_realm_domain`, `krb5_get_default_config_files`, and realm iterators.
- Credential acquisition and validation APIs include `krb5_get_in_tkt`, password/skey/keytab variants, `krb5_get_init_creds_password`, `krb5_get_init_creds_keytab`, option setters, `krb5_verify_init_creds`, `krb5_get_validated_creds`, `krb5_get_renewed_creds`, and password-change helpers.
- Credential cache and keytab APIs include `krb5_cc_resolve`, `krb5_cc_default(_name)`, `krb5_cc_set_default_name`, `krb5_cc_initialize`, `krb5_cc_destroy`, `krb5_cc_store_cred`, `krb5_cc_retrieve_cred`, `krb5_cc_start_seq_get`, `krb5_cc_next_cred`, `krb5_cc_end_seq_get`, `krb5_cc_remove_cred`, `krb5_kt_resolve`, `krb5_kt_default`, `krb5_kt_get_entry`, and keytab sequence functions.
- Protocol helpers include `krb5_mk_req`, `krb5_mk_req_extended`, `krb5_rd_req`, `krb5_mk_rep`, `krb5_rd_rep`, `krb5_mk_safe`, `krb5_rd_safe`, `krb5_mk_priv`, `krb5_rd_priv`, `krb5_sendauth`, `krb5_recvauth`, credential forwarding and credential message functions.
- Compatibility and diagnostics include `krb5_425_conv_principal`, `krb5_524_conv_principal`, `krb5_decode_ticket`, `krb5_locate_kdc`, `krb5_get_error_message`, and `krb5_free_error_message`.

## Control Flow

Like the other loadfuncs headers, this file only declares pointer types. The expected flow is: assemble a `FUNC_INFO` table for these symbol names, call `LoadFuncs(KRB5_DLL, ...)`, then route all KRB5 operations through `p<symbol>` variables. The groups in the file roughly follow free functions, crypto, validation helpers, context/authentication, string conversions, initial credential APIs, realm iteration, and lower-level cache/keytab routines.

## State and Persistence Behavior

The declarations expose stateful KRB5 objects: `krb5_context`, `krb5_auth_context`, credential caches, keytabs, replay caches, allocated principals/data, and credential structures. The header persists only process-global function pointers in consumers; the external DLL owns contexts, allocations, config discovery, default realm state, and cache/keytab persistence. Many APIs return allocated objects that must be released with matching `krb5_free_*` calls.

## Dependencies and Integration Points

Depends on `loadfuncs.h` and `<krb5.h>`, including KRB5 calling-convention macros. It integrates OpenAFS with MIT Kerberos for Windows, credential cache management, ticket acquisition, auth context setup, AP-REQ/AP-REP exchange, password change, keytab access, and KRB4/KRB5 conversion compatibility.

## Risks

- The header mirrors a particular KFW/MIT Kerberos ABI. Symbol drift across installed Kerberos versions can cause partial loads.
- Function-pointer declarations must exactly match calling convention and parameter types; mismatches are runtime-critical on Windows.
- A partial load must not be treated as full capability; every consumer of less common APIs should handle NULL function pointers.
- Memory ownership is complex: many APIs allocate nested KRB5 objects that require a matching free routine from the same DLL instance.
- Some declarations are explicitly marked as not present in `krb5.h` or "more", increasing risk of version-specific exports.
- Crypto and credential APIs manipulate sensitive key/password data and should avoid logging buffers or leaving copied plaintext in long-lived memory.

## Test Signals

Compile tests should cover both `_WIN64` and 32-bit DLL name selection. Loader tests should verify all expected symbols against supported KFW versions and should explicitly exercise partial-load behavior. Integration tests should cover context initialization/free, ccache default resolution, principal parse/unparse, initial credential option setup, and matching free routines under leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-krb5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-krb524.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-krb524.h

## Purpose

This small header declares dynamic bindings for the Kerberos 5 to Kerberos 4 conversion DLL, `krb524.dll`. It supports compatibility code that needs to convert a KRB5 credential into a KRB4 `CREDENTIALS` record.

## Important APIs, Types, and Functions

- `KRB524_DLL` names `krb524.dll`.
- `krb524_init_ets(krb5_context)` initializes error tables for the conversion library.
- `krb524_convert_creds_kdc(krb5_context, krb5_creds *, CREDENTIALS *)` converts KRB5 credentials to KRB4 credentials through the KDC path.

## Control Flow

The file contributes two symbol typedefs to a dynamic load table. Callers first load `krb524.dll`, initialize error tables, then call the conversion function when a KRB4 credential is needed from a KRB5 credential.

## State and Persistence Behavior

The header itself stores no state. The external DLL may initialize process-local error-table state, and conversion depends on the caller-provided `krb5_context`, KDC configuration, and output `CREDENTIALS` storage. The conversion result may be saved later by KRB4 ticket APIs, but this header does not perform persistence.

## Dependencies and Integration Points

Depends on `loadfuncs.h`, `<krb5.h>`, and `<krb.h>`. It bridges the KRB5 and KRB4 compatibility layers used by OpenAFS Windows code that still needs KRB4 token/ticket support.

## Risks

- The KRB524 compatibility path may be absent on modern Kerberos installations.
- KRB4 output credentials are legacy-sensitive material and should be handled as short-lived compatibility artifacts.
- Conversion may require KDC support and network reachability; callers should distinguish load failure, conversion failure, and KDC policy failure.

## Test Signals

Test missing-DLL behavior and successful symbol resolution independently. If a test KDC supports KRB524 conversion, verify a known KRB5 credential converts to a KRB4 `CREDENTIALS` object and that failure paths leave the destination structure in a predictable state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-krb524.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-leash.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-leash.h

## Purpose

This header declares dynamic bindings for the MIT Leash Windows DLL (`leashw32.dll` or `leashw64.dll`). It exposes interactive credential acquisition, password change, credential listing/destruction, import/renewal, and Leash default preference APIs to OpenAFS Windows code.

## Important APIs, Types, and Functions

- `LEASH_DLL` selects `leashw64.dll` on `_WIN64`, otherwise `leashw32.dll`.
- Dialog/UI APIs: `Leash_kinit_dlg`, `Leash_kinit_dlg_ex`, `Leash_changepwd_dlg`, and `Leash_changepwd_dlg_ex`.
- Credential lifecycle APIs: `Leash_kinit`, `Leash_kinit_ex`, `Leash_klist`, `Leash_kdestroy`, `Leash_renew`, `Leash_import`, and `Leash_importable`.
- Password and error helpers: `Leash_checkpwd`, `Leash_changepwd`, `Leash_get_lsh_errno`, `Leash_set_help_file`, `Leash_get_help_file`, and `Leash_timesync`.
- Defaults and policy knobs include get/set/reset triplets for lifetime, renew-till, forwardable, no-addresses, proxiable, public IP, KRB4 usage, min/max life and renewal bounds, renewable, lock-file locations, uppercase realm, MSLSA import, and preserve-kinit-settings.
- `Leash_reset_defaults` resets Leash preference defaults.

## Control Flow

This file only declares function-pointer types. A caller loads `LEASH_DLL`, resolves the symbols into `pLeash_*` function pointers, then drives either UI flows or noninteractive credential operations through those pointers. Defaults are read, modified, or reset one option at a time.

## State and Persistence Behavior

The external Leash DLL owns persistent defaults, ticket cache changes, import state, help file path, last Leash error, and renewal behavior. The header only defines the bindings. Many default setters appear to persist user or machine preference state through Leash/KFW configuration mechanisms.

## Dependencies and Integration Points

Depends on `loadfuncs.h` and `<leashwin.h>` for `LPLSH_DLGINFO`, `LPLSH_DLGINFO_EX`, and `TICKETINFO`. It integrates OpenAFS Windows user workflows with Kerberos credential acquisition and Leash preference management.

## Risks

- UI dialog functions require valid `HWND` ownership and should run on an appropriate UI thread.
- `char *` password/principal buffers carry sensitive data; callers must manage lifetime, encoding, and clearing.
- Default setters can persist configuration changes with broad user-visible impact.
- KRB4-related defaults are compatibility-sensitive and may be ignored or unsupported by modern Leash builds.
- The trailing comment says not all functions are present, so consumers should expect an incomplete binding surface.

## Test Signals

Loader tests should assert DLL name selection by architecture and expected symbol availability for supported Leash versions. UI tests should isolate dialog entry points behind mocks or manual harnesses. Preference tests should verify get/set/reset round trips in a disposable profile or registry hive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-leash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-lsa.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-lsa.h

## Purpose

This header declares dynamic bindings to Windows LSA/security APIs from `secur32.dll` and `advapi32.dll`. It supports integration with the Windows Local Security Authority, especially locating authentication packages and interacting with logon-session data.

## Important APIs, Types, and Functions

- `SECUR32_DLL` names `secur32.dll`; `ADVAPI32_DLL` names `advapi32.dll`.
- `LsaConnectUntrusted` opens an untrusted LSA connection.
- `LsaLookupAuthenticationPackage` resolves an authentication package ID.
- `LsaCallAuthenticationPackage` sends package-specific requests.
- `LsaFreeReturnBuffer` releases buffers returned by LSA.
- `LsaNtStatusToWinError` maps `NTSTATUS` to Win32 error codes.
- `LsaGetLogonSessionData` retrieves logon session metadata.

## Control Flow

The expected sequence is to dynamically load the security DLL, bind LSA functions, connect to LSA, look up an authentication package, call into it, translate errors as needed, and release returned buffers. The header itself only provides function-pointer typedefs.

## State and Persistence Behavior

The header stores no state. The external LSA APIs operate on process handles, authentication-package state, return buffers, and OS logon sessions. Callers must close or release OS resources using the appropriate Windows APIs and `LsaFreeReturnBuffer`.

## Dependencies and Integration Points

Depends on `loadfuncs.h` and Windows security types such as `NTSTATUS`, `PLSA_STRING`, `PSECURITY_LOGON_SESSION_DATA`, `PLUID`, and `HANDLE`. It likely integrates Kerberos credential import/export with MSLSA logon sessions.

## Risks

- LSA calls are privilege- and policy-sensitive; behavior differs by Windows version, logon type, and process token.
- Return buffers must be freed with LSA APIs, not normal heap free.
- Authentication package request structures are not declared here, so type mismatch risk sits at call sites.
- Dynamic loading can fail on older or restricted systems, and callers need fallback behavior.

## Test Signals

Tests should cover missing-symbol handling, `NTSTATUS` to Win32 conversion, successful untrusted LSA connection on supported Windows, and proper buffer release. Integration tests should use non-destructive read-only logon-session queries where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-lsa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-profile.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-profile.h

## Purpose

This header declares dynamic bindings for the Kerberos profile library (`xpprof32.dll` or `xpprof64.dll`). It lets OpenAFS/KFW code read, enumerate, update, and flush Kerberos profile configuration without a static dependency.

## Important APIs, Types, and Functions

- `PROFILE_DLL` selects `xpprof64.dll` on `_WIN64`, otherwise `xpprof32.dll`.
- Initialization and lifecycle: `profile_init`, `profile_init_path`, `profile_flush`, `profile_abandon`, and `profile_release`.
- Reads and enumeration: `profile_get_values`, `profile_get_string`, `profile_get_integer`, `profile_get_relation_names`, `profile_get_subsection_names`, `profile_iterator_create`, `profile_iterator`, and `profile_iterator_free`.
- Memory cleanup: `profile_free_list` and `profile_release_string`.
- Mutation APIs: `profile_update_relation`, `profile_clear_relation`, `profile_rename_section`, and `profile_add_relation`.

## Control Flow

Callers load the DLL, initialize a `profile_t` from file specs or a path list, perform lookup/iteration/mutation calls, then either flush changes or abandon/release the profile. Iterators are explicit objects that must be freed after traversal.

## State and Persistence Behavior

The external profile library owns parsed profile state and writes modifications to profile files when flushed. `profile_abandon` discards a profile handle without committing changes, while `profile_release` and `profile_flush` determine handle lifetime and persistence semantics according to the profile library. Returned lists and strings require library-specific release functions.

## Dependencies and Integration Points

Depends on `loadfuncs.h` and `<profile.h>`. It integrates with Kerberos profile configuration, likely including realm, domain, KDC, and library default settings consumed by KRB5/Leash paths.

## Risks

- Mutating profile relations can change global Kerberos behavior for the user or machine.
- Callers must pair allocated return values with `profile_free_list` or `profile_release_string`.
- Profile path parsing and write permissions vary by Windows environment.
- Partial dynamic loads can leave mutation APIs unavailable even if read APIs load.

## Test Signals

Use temporary profile files to test initialization, string/integer lookup, relation enumeration, add/update/clear/rename, flush, and abandon behavior. Loader tests should verify architecture-specific DLL naming and missing-DLL failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-profile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-wshelper.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-wshelper.h

## Purpose

This header declares dynamic bindings for the KFW Winsock/helper DLL (`wshelp32.dll` or `wshelp64.dll`). It exposes resolver, DNS packet, Hesiod, host identity, and OS helper functions to OpenAFS Windows code.

## Important APIs, Types, and Functions

- `WSHELPER_DLL` selects `wshelp64.dll` on `_WIN64`, otherwise `wshelp32.dll`.
- Host/service lookup APIs include `rgethostbyname`, `rgethostbyaddr`, `rgetservbyname`, `gethinfobyname`, `getmxbyname`, `getrecordbyname`, `rrhost`, `wsh_gethostname`, and `wsh_getdomainname`.
- Address and OS helpers include `inet_aton`, `WhichOS`, and `WSHGetHostID`.
- Resolver APIs include `res_init`, `res_setopts`, `res_getopts`, `res_mkquery`, `res_send`, `res_querydomain`, `res_search`, `dn_comp`, and `rdn_expand`.
- Hesiod APIs include `hes_to_bind`, `hes_resolve`, `hes_error`, `hes_getmailhost`, `hes_getservbyname`, `hes_getpwnam`, and `hes_getpwuid`.

## Control Flow

Callers load `WSHELPER_DLL`, resolve the helper symbols, optionally initialize resolver state with `res_init`, and then use resolver/Hesiod calls for name, service, mailhost, passwd, DNS, and host-ID operations. The header does not implement lookup logic.

## State and Persistence Behavior

The external DLL owns resolver options and any static buffers returned by resolver/Hesiod functions. `res_setopts` and `res_getopts` imply process-local resolver state. The header itself holds only dynamically populated function pointers in consumers.

## Dependencies and Integration Points

Depends on `loadfuncs.h` and `<wshelper.h>`, along with Winsock structs such as `hostent`, `servent`, `in_addr`, and helper structs like `rrec`, `hes_postoffice`, and `passwd`. It integrates OpenAFS/KFW with DNS and Hesiod naming services used in older MIT environments.

## Risks

- Several classic resolver APIs return pointers to static storage and are not generally thread-safe.
- DNS packet APIs require caller-provided buffers and lengths; malformed inputs can lead to truncation or parse errors.
- Hesiod and legacy resolver behavior may be unavailable in modern deployments.
- The declaration for `rgetservbyname` returns `struct servent` by value, while many resolver APIs traditionally return a pointer; call sites must match the actual DLL ABI.

## Test Signals

Tests should cover DLL load by architecture, resolver initialization, host/service lookups using controlled names, DNS query buffer sizing, and behavior when Hesiod is not configured. Static-buffer callers should be reviewed under concurrent use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-wshelper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs.c -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs.c

## Purpose

This file implements the generic Windows DLL dynamic loader helper used by the KFW loadfuncs headers. It provides `LoadFuncs()` to populate function-pointer variables from named exports and `UnloadFuncs()` to clear those pointers and release a DLL handle.

## Important APIs, Types, and Functions

- `UnloadFuncs(FUNC_INFO fi[], HINSTANCE h)` iterates the function table, sets every target pointer to NULL, and calls `FreeLibrary(h)` if a module handle was supplied.
- `LoadFuncs(const char *dll_name, FUNC_INFO fi[], HINSTANCE *ph, int *pindex, int cleanup, int go_on, int silent)` loads the named DLL and resolves each export listed in `fi`.
- `LoadLibrary`, `GetProcAddress`, `FreeLibrary`, and `SetErrorMode(SEM_FAILCRITICALERRORS)` are the Windows APIs used for loading and error-dialog suppression.

## Control Flow

`LoadFuncs()` initializes optional outputs (`*ph = 0`, `*pindex = -1`) and clears all pointer variables in the `FUNC_INFO` array. If `silent` is true, it temporarily changes the process error mode before `LoadLibrary()` to suppress critical-error UI. It then resolves functions in order. If `go_on` is false, lookup stops at the first missing symbol; if true, lookup continues and records any missing-symbol error. On error with `cleanup` and not `go_on`, it clears all function pointers, frees the library, and returns 0. Otherwise it stores the module handle if requested and returns 0 for any missing symbol or 1 for complete success.

`UnloadFuncs()` is simpler: clear every pointer and free the module if non-NULL.

## State and Persistence Behavior

The functions mutate caller-provided function-pointer storage. They do not keep their own registry of loaded libraries, so callers are responsible for holding `HINSTANCE` values and calling `UnloadFuncs()` at the right time. `LoadFuncs()` can leave partially populated pointer tables when `go_on` is true or when `cleanup` is false.

## Dependencies and Integration Points

Includes `<windows.h>` and `loadfuncs.h`. It is the implementation backend for all `loadfuncs-*.h` dynamic wrappers. It integrates with the process module loader and process error mode.

## Risks

- `fi` is assumed non-NULL and terminated by `END_FUNC_INFO`; a malformed table can overrun.
- `SetErrorMode` changes process-global state temporarily and is not thread-isolated.
- If `go_on` is true, the function can return failure while still leaving successfully resolved pointers and a loaded module handle.
- If `cleanup` is false and a required symbol is missing, callers must understand that partial pointer state remains.
- Function pointer variables are not synchronized; concurrent load/unload around active calls can race.

## Test Signals

Unit tests can load a known system DLL with known exports, verify `pindex`, success status, and pointer population, then unload and confirm pointers are cleared. Negative tests should cover missing DLL, missing export with `cleanup` true/false, `go_on` true/false, and `silent` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs.h

## Purpose

This header defines the small dynamic-loader abstraction shared by the KFW loadfuncs wrappers. It describes how named DLL exports map to caller-owned function-pointer variables and declares the loader/unloader functions implemented in `loadfuncs.c`.

## Important APIs, Types, and Functions

- `FUNC_INFO` contains `void **func_ptr_var` and `char *func_name`, pairing storage for a function pointer with the export name to resolve.
- `DECL_FUNC_PTR(x)` declares a function pointer variable named `p<x>` using typedef `FP_<x>`.
- `MAKE_FUNC_INFO(x)` creates a `FUNC_INFO` entry for variable `p<x>` and export name `x`.
- `END_FUNC_INFO` terminates a `FUNC_INFO` array.
- `TYPEDEF_FUNC(ret, call, name, args)` defines function pointer type `FP_<name>`.
- `LoadFuncs()` and `UnloadFuncs()` are declared for runtime loading and cleanup.

## Control Flow

Consumer headers use `TYPEDEF_FUNC` to declare pointer types for each external symbol. Consumer source files use `DECL_FUNC_PTR` to define storage and `MAKE_FUNC_INFO` rows to form a NULL-terminated table. `LoadFuncs()` populates the table, and `UnloadFuncs()` clears it.

## State and Persistence Behavior

This header does not store state. It standardizes process-global or module-global pointer variables in consumers and an external DLL handle passed to the loader/unloader. Loaded state persists until the caller invokes `UnloadFuncs()` or the process exits.

## Dependencies and Integration Points

Includes `<windows.h>` and wraps declarations in `extern "C"` for C++ compatibility. It is used by KRB4, KRB5, KRB524, Leash, LSA, profile, and wshelper dynamic-binding headers.

## Risks

- `char *func_name` is not `const char *`, although macro-generated names are string literals.
- The macros assume a strict naming convention (`FP_name` and `pname`), which makes generated declarations easy to misuse if a symbol is renamed.
- Storing function pointers through `void **` is common for this Windows pattern but not strictly portable C.
- The API leaves thread-safety and lifetime discipline to callers.

## Test Signals

Compile tests should instantiate a small typedef/pointer/table using all macros. Runtime tests belong with `loadfuncs.c` and should verify pointer clearing and export lookup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/hashtable.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/hashtable.h

## Purpose

This NetIDMgr utility header declares a simple caller-synchronized hashtable abstraction with caller-supplied hash, compare, add-reference, and delete-reference callbacks. It stores key/data associations by reference, not by copying.

## Important APIs, Types, and Functions

- `hash_function_t` computes a `khm_int32` hash from a key.
- `comp_function_t` compares two keys with strcmp-style ordering.
- `add_ref_function_t` and `del_ref_function_t` are lifecycle hooks invoked when entries are added, replaced, removed, or table-deleted.
- `hash_bin` stores `void *data`, `void *key`, and linked-list fields through `LDCL`.
- `hashtable` stores bin count, callback pointers, and an array of bin heads.
- `hash_new_hashtable`, `hash_del_hashtable`, `hash_add`, `hash_del`, `hash_lookup`, and `hash_exist` are the core table operations.
- `hash_string` and `hash_string_comp` are helpers for NULL-terminated wide-string keys.

## Control Flow

Creation fixes the bin count and callback functions. `hash_add()` hashes the key, removes an existing equal-key association if present, stores the new key/data pair by reference, and invokes the add-ref hook. `hash_del()` removes the matching association and invokes the delete-ref hook. Lookup and existence checks hash and compare keys in a bin chain. Deleting the table walks remaining entries and invokes delete-ref hooks.

## State and Persistence Behavior

The hashtable owns its internal bin nodes and bin array, but it does not own key or data memory unless callbacks implement ownership. Keys should either be constants or embedded in the data object so key lifetime follows data lifetime. No persistence is performed.

## Dependencies and Integration Points

Depends on NetIDMgr base definitions in `<khdefs.h>` and linked-list macros in `<khlist.h>`. It is a generic in-memory utility for NetIDMgr components that need keyed lookup and optional reference accounting.

## Risks

- The API is explicitly not thread-safe; callers must serialize operations on a table.
- Because keys and data are stored by reference, dangling pointers are easy if callers free objects before removal.
- Replacement calls the delete-ref hook for the old object before add-ref for the new one; hooks must tolerate that ordering.
- `hash_lookup()` returning NULL is defined as equivalent to nonexistence, so storing NULL data is not supported.
- Hash function quality and bin count directly affect performance.

## Test Signals

Unit tests should cover create/delete, add/lookup/exist/delete, replacement with equal keys, hook invocation counts, wide-string hash/compare behavior, and caller-side locking assumptions. Tests should also cover NULL keys if the chosen comparator supports them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/hashtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kconfig.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kconfig.h

## Purpose

This header declares the NetIDMgr configuration provider API. It exposes a hierarchical, layered configuration model over user, machine, and schema stores, with typed values, shadow spaces, schema loading, enumeration, mutation, and removal.

## Important APIs, Types, and Functions

- `kconf_schema` describes schema entries: name, type, default value, and description.
- Value/schema types are `KC_NONE`, `KC_SPACE`, `KC_ENDSPACE`, `KC_INT32`, `KC_INT64`, `KC_STRING`, and `KC_BINARY`.
- Store/behavior flags include `KCONF_FLAG_ROOT`, `KCONF_FLAG_USER`, `KCONF_FLAG_MACHINE`, `KCONF_FLAG_SCHEMA`, `KCONF_FLAG_TRAILINGVALUE`, `KCONF_FLAG_WRITEIFMOD`, `KCONF_FLAG_IFMODCI`, and `KCONF_FLAG_NOPARSENAME`.
- Limits include `KCONF_MAXCCH_NAME`, `KCONF_MAX_DEPTH`, `KCONF_MAXCCH_PATH`, and `KCONF_MAXCCH_STRING`.
- Space lifecycle APIs: `khc_open_space`, `khc_shadow_space`, `khc_close_space`, `khc_get_config_space_name`, `khc_get_config_space_parent`, `khc_enum_subspaces`, and `khc_remove_space`.
- Read APIs: `khc_read_string`, `khc_read_multi_string`, `khc_read_int32`, `khc_read_int64`, and `khc_read_binary`.
- Write APIs: `khc_write_string`, `khc_write_multi_string`, `khc_write_int32`, `khc_write_int64`, and `khc_write_binary`.
- Metadata and schema APIs: `khc_get_type`, `khc_value_exists`, `khc_remove_value`, `khc_load_schema`, and `khc_unload_schema`.

## Control Flow

Clients open a configuration space relative to an optional parent, optionally creating it and choosing visible stores. Reads search visible stores by precedence, with user before machine before schema, and also consult shadow spaces for missing values. Writes target the top writable store visible through the handle. Schema loading uses a structured sequence of space-start, value, and space-end records. Enumeration returns subspace handles incrementally, freeing the previous handle as the next one is requested.

## State and Persistence Behavior

Configuration handles refer to persistent user and machine stores, plus read-only schema defaults. The comments indicate the Windows implementation maps spaces to registry keys, making name/path limits hard constraints. `KCONF_FLAG_WRITEIFMOD` avoids unnecessary writes by comparing with the effective read value. Shadowing is per-handle, not global, and does not transfer ownership of the lower handle.

## Dependencies and Integration Points

Depends on `<khdefs.h>` and `<mstring.h>`. It integrates NetIDMgr plugins and core code with Windows-backed application configuration, schema defaults, and identity/plugin settings. Identity configuration in `kcreddb.h` uses this provider through `kcdb_identity_get_config()`.

## Risks

- `KCONF_FLAG_WRITEIFMOD` and `KCONF_FLAG_NOPARSENAME` both use `0x00000040`; this overlap is surprising and requires implementation/context discipline to avoid ambiguous behavior.
- Binary values are unsupported by schema and are not affected by write-if-mod behavior.
- Handles can include layered stores and shadows; write behavior may differ from effective read behavior.
- Enumeration returns the union of stores and ignores shadowed spaces, which may surprise callers expecting only the restricted domain.
- Registry-backed persistence means permission and virtualization behavior can vary by process token and Windows version.

## Test Signals

Tests should use isolated registry/config roots where available. Cover open/create/close, path parsing and no-parse names, user/machine/schema precedence, shadow fallback, read/write for each type, buffer sizing with NULL buffers, schema load/unload, remove value/space, and enumeration handle lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kconfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kcreddb.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kcreddb.h

## Purpose

This header declares the NetIDMgr credentials database (KCDB) API. It covers identities, identity-provider callbacks, credential sets, individual credentials, attribute data types, attribute registration, credential type registration, generic record access, time/string conversion helpers, and KCDB notification operation constants.

## Important APIs, Types, and Functions

- Common limits include max name and description lengths and `KCDB_CBSIZE_AUTO`.
- Identity definitions include valid-name limits/chars, identity flags (`DEFAULT`, `SEARCHABLE`, `HIDDEN`, `VALID`, `INVALID`, `EXPIRED`, `EMPTY`, `RENEWABLE`, `INTERACT`, credential-derived flags, `STICKY`, and internal/config/activity flags), `kcdb_ident_name_xfer`, and `kcdb_ident_info`.
- Identity-provider APIs include `kcdb_identpro_validate_name`, `kcdb_identpro_validate_identity`, `kcdb_identpro_canon_name`, `kcdb_identpro_compare_name`, `kcdb_identpro_set_default`, `kcdb_identpro_set_searchable`, `kcdb_identpro_update`, `kcdb_identpro_get_ui_cb`, and `kcdb_identpro_notify_create`.
- Identity lifecycle and attributes include `kcdb_identity_create/delete`, `kcdb_identity_set_flags/get_flags`, `kcdb_identity_get_name`, `kcdb_identity_set_default`, `kcdb_identity_get_default`, `kcdb_identity_get_config`, `kcdb_identity_hold/release`, provider/type get/set APIs, equality, attribute/property get/set APIs, enumeration, and refresh.
- Credential-set callbacks and APIs include `kcdb_cred_apply_func`, `kcdb_cred_filter_func`, `kcdb_cred_comp_func`, `kcdb_credset_create/delete`, `collect`, `collect_filtered`, `flush`, `extract`, `extract_filtered`, `get_cred`, `find_filtered`, `find_cred`, delete/add by index/reference, `get_size`, `purge`, `apply`, `sort`, `seal`, and `unseal`.
- Credential definitions include credential flags (`DELETED`, `RENEWABLE`, `INITIAL`, `EXPIRED`, `INVALID`, `SELECTED`), `kcdb_cred_request`, and APIs for create, duplicate, update, attribute get/set, name, identity, serial, type, flags, hold/release/delete, compare attributes, and equality.
- Data type APIs define `kcdb_type`, conversion/validation/comparison/dup callbacks, type flags, registration/lookup, and built-in types (`VOID`, `STRING`, `DATE`, `INTERVAL`, `INT32`, `INT64`, `DATA`).
- Utility conversions cover `time_t` to/from `FILETIME` intervals, FILETIME arithmetic/comparison, interval string formatting/parsing, and ANSI/Unicode conversion.
- Attribute APIs define `kcdb_attrib`, computed attribute callbacks, registration/lookup/description/listing, flags (`REQUIRED`, `COMPUTED`, `SYSTEM`, `HIDDEN`, `PROPERTY`, `VOLATILE`, `ALTVIEW`, `TRANSIENT`), built-in attribute IDs, and names.
- Credential type APIs define `kcdb_credtype`, credential type ID ranges, `AUTO`, `ALL`, `INVALID`, registration, descriptor lifetime, name/description lookup, subscription lookup, and ID lookup.
- Generic buffer APIs let callers get/set attributes through a record handle for both identities and credentials.
- KCDB notification operation constants cover insert, delete, modify, activate/deactivate, hide/unhide, search flag changes, and new default identity.

## Control Flow

KCDB clients typically create/open identities, create temporary credential sets while enumerating an external provider, populate credentials, then collect those credentials into the root credential store. `kcdb_credset_collect()` is the key synchronization path: it selects credentials by identity/type or filter, adds missing credentials, updates existing credentials with non-null fields, applies additive selected flags specially, and removes destination credentials absent from the source. UI-visible credentials live in the root store; non-root sets are temporary and generally do not emit notifications.

Identity operations validate and canonicalize through the registered identity provider, maintain reference-counted handles, and refresh flags from root credentials and provider status. Credential operations use record-like attributes typed through registered `kcdb_type` handlers. Credential and identity handles must be held/released explicitly. Credential sets can be sealed to make them temporarily read-only, including sealed selected-credential snapshots in UI contexts.

## State and Persistence Behavior

The KCDB maintains in-memory identities, credentials, root credential store, registered data types, registered attributes, registered credential types, provider subscription state, and default identity state. Identity configuration can persist through `kcdb_identity_get_config()` and the configuration provider. Credentials themselves appear in-memory and provider-fed; persistence of actual external credentials is owned by providers. Deleted identities and credentials are marked inactive/deleted and are removed once references are released.

## Dependencies and Integration Points

Depends on `<khdefs.h>`, `<time.h>`, Windows `FILETIME`, message/subscription handles, configuration APIs, identity provider messages, and UI code. It is the central integration contract between NetIDMgr core, credential providers, identity providers, UI selection/action logic, and plugin-defined credential/attribute types.

## Risks

- `kcdb_identity_set_flags()` is explicitly non-atomic; callers must re-read flags after failures.
- `kcdb_credset_collect()` can delete all root-store credentials not present in a source set if called with wildcard identity/type, making filter correctness critical.
- Credential-set iteration can race with concurrent modifications and may not exhaustively cover or uniquely return matches across repeated calls.
- Reference lifetimes are strict: released handles must not be re-held, and descriptor handles from get-info APIs require matching release calls.
- Computed/volatile/transient attributes have non-obvious update semantics; missing transient attributes remove destination values during updates.
- Type and attribute callbacks must validate buffer sizes correctly, especially with `KCDB_CBSIZE_AUTO`.
- Credential type count is capped by `KCDB_CREDTYPE_MAX_ID`; plugins must unregister on unload.

## Test Signals

Tests should cover identity name validation/canonicalization, create/open/delete, default identity transitions, provider absence behavior, reference hold/release discipline, identity config creation, flag side effects, and identity refresh. Credential tests should cover temporary set creation, collect/add/update/delete deltas, wildcard safety, filters, seal/unseal behavior, purge of deleted entries, sort ordering, credential equality, attribute set/get by ID and name, computed and transient attributes, type/attribute/credtype registration lifecycle, time conversion helpers, and root-store notification emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kcreddb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khaction.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khaction.h

## Purpose

This header declares NetIDMgr UI action, menu, accelerator, and action-context APIs. It describes how commands are represented, how custom menus and plugin actions are created, and how the current credential/identity selection context is captured and passed to actions.

## Important APIs, Types, and Functions

- `khui_action` describes standard and custom actions: command ID, action type, optional name, internal icon/string/help resource indices, custom caption/tooltip/listener/user data, and state.
- Action types and states include trigger/toggle types and enabled, disabled, checked, hot, and deleted states.
- `khui_action_ref` points to actions by command ID or direct action pointer and carries menu flags such as submenu, separator, by-reference, and default.
- `khui_menu_def` describes menus associated with an action or ad-hoc command, with constant or allocated item lists.
- Menu APIs include `khui_menu_create`, `khui_menu_dup`, `khui_menu_delete`, `khui_menu_insert_action`, `khui_menu_remove_action`, `khui_menu_get_size`, `khui_menu_get_action`, and `khui_find_menu`.
- `khui_scope` classifies UI selection as none, identity, credential type, group, or single credential.
- `khui_header` and `khui_action_context` represent outline group headers, selected identity/credential/type, selected credential set, selected count, and optional parameter data.
- Context APIs include `khui_context_set`, `khui_context_set_ex`, `khui_context_set_indirect`, `khui_context_get`, `khui_context_create`, `khui_context_release`, `khui_context_reset`, `khui_context_refresh`, and `khui_context_cursor_filter`.
- Action APIs include `khui_action_trigger`, `khui_find_action`, `khui_action_create`, `khui_action_delete`, `khui_action_get_data`, `khui_find_named_action`, `khui_enable_actions`, `khui_enable_action`, `khui_check_radio_action`, and `khui_check_action`.
- Accelerator helpers include `khui_get_cmd_accel_string` and, under `NOEXPORT`, global accelerator initialization.

## Control Flow

Menus are created or duplicated, populated with action references, and later rendered or traversed by UI code. Custom actions are created with captions, tooltips, user data, type, and an optional message subscription; triggering posts or dispatches an action message to the listener. UI selection changes call `khui_context_set()` or `_set_ex()`, which holds referenced identity/credential objects, extracts selected credentials from a source set, and updates side effects such as action enabled/checked state. Actions can be triggered with an explicit context or the current context.

## State and Persistence Behavior

The action system maintains registered actions, menu associations, global/current UI context, held identity/credential references, selected credential sets, and action state bits. Custom menu definitions created by `khui_menu_create()` or `khui_menu_dup()` are caller-owned and must be deleted. Custom action listeners are retained by the action system and released when no longer needed. No persistent storage is declared here, although named actions must not collide with configuration node names.

## Dependencies and Integration Points

The header depends on NetIDMgr types from surrounding includes, KCDB handles/credential types, message subscriptions, and Windows UI resources under `_WIN32` or internal `NOEXPORT` sections. It integrates the credential database with NetIDMgr menus, toolbar actions, context menus, keyboard accelerators, and plugin-defined commands.

## Risks

- Menu definitions are explicitly not thread-safe; concurrent modification can corrupt item arrays or invalidate returned references.
- Context setters should only be called from the UI thread.
- `khui_menu_get_action()` returns references invalidated by later menu modifications.
- Context structures returned by `khui_context_get()` must not be modified before release because release uses them to drop holds.
- Custom action deletion marks action contents invalid; plugins should delete only during unload and avoid triggering stale command IDs.
- Listener ownership is transferred: callers should not release the subscription after passing it to `khui_action_create()`.

## Test Signals

Tests should cover menu create/duplicate/delete, insertion/removal at specific indices and append behavior, separator/submenu/default flags, size and item retrieval invalidation rules, action create/delete/find-by-name/user-data, enable/check/radio state transitions, context set/get/release/reset with held identity and credential handles, cursor filtering against selected credential sets, and action trigger dispatch to a test subscription.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khaction.h -->

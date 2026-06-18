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

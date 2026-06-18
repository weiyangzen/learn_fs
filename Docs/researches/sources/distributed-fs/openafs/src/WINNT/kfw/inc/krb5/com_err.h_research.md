## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/com_err.h

Purpose: Public MIT common-error library header used by Kerberos 5 and generated error tables.

Important APIs/types/functions: Defines `errcode_t`, `et_old_error_hook_func`, `struct error_table`, and public APIs `com_err`, `com_err_va`, `error_message`, `add_error_table`, and `remove_error_table`. Non-Windows builds also expose `set_com_err_hook` and `reset_com_err_hook`.

Control flow: Libraries register generated `struct error_table` instances, callers format/report errors through `com_err` or retrieve text with `error_message`, and registered tables can be removed.

State and persistence: Error table registry and optional hooks are process-global implementation state. No file persistence.

Dependencies and integration points: Includes `win-mac.h` on Windows for calling conventions and `stdarg.h` for varargs. Used by K5 core errors, profile errors, Kadmin errors, KerberosIV generated errors, and `loadfuncs-com_err.h`.

Risks: Windows intentionally hides global hook APIs to avoid cross-application display hooks. Returned strings are observer/dependent memory and must not be freed by callers. Calling convention macros must match the loaded DLL.

Test signals: Register/remove table tests, `error_message` fallback tests, varargs formatting through `com_err_va`, and dynamic-load tests that confirm `KRB5_CALLCONV`/`KRB5_CALLCONV_C` signatures match `comerr32.dll` or `comerr64.dll`.

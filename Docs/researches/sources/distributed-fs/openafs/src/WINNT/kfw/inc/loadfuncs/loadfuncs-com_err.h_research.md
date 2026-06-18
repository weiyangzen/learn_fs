## sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-com_err.h

Purpose: Dynamic-load function typedef list for the KfW com_err DLL.

Important APIs/types/functions: Includes `loadfuncs.h` and `<com_err.h>`, selects `COMERR_DLL` as `comerr64.dll` on `_WIN64` or `comerr32.dll` otherwise, and declares `TYPEDEF_FUNC` entries for `com_err`, `com_err_va`, `error_message`, `add_error_table`, and `remove_error_table` using K5 calling conventions.

Control flow: The loadfuncs framework resolves com_err exports at runtime, allowing OpenAFS/KfW glue to format errors and register/unregister error tables without static linking.

State and persistence: Header has no state. Loaded function pointers/module handles live in loadfuncs code; the com_err DLL owns process-global error table registry state.

Dependencies and integration points: Depends on K5 `com_err.h` types and `KRB5_CALLCONV` macros. Integrates generated Kerberos/profile/Leash error tables with dynamically loaded KfW com_err.

Risks: DLL bitness must match process bitness. Varargs function pointer calls must use the exact calling convention. Including the old K4 `com_err.h` instead of K5 would produce incompatible prototypes.

Test signals: Dynamic-load both bitness-specific DLL names in matching environments; resolve all exports; register a generated error table and verify `error_message`; exercise `com_err_va` with varargs forwarding.

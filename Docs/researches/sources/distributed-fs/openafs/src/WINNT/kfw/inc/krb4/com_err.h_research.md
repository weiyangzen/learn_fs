## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/com_err.h

Purpose: Provides a small Kerberos IV-era substitute for MIT `com_err`, exposing error formatting, table-name lookup, and hook registration.

Important APIs/types/functions: Defines `err_func` as `LPSTR (*)(int,long)`; declares `com_err`, `mbprintf`, `error_message`, `error_table_name`, `set_com_err_hook`, and `reset_com_err_hook`. Under `WIN16`, public symbols are exported functions plus global function pointers; under other builds they are direct functions.

Control flow: This header only declares the API. Runtime callers report an error through `com_err`, which may dispatch to a hook installed with `set_com_err_hook`; `error_message` maps numeric table codes to strings.

State and persistence: Hook state and error tables live in the linked com_err implementation. No file persistence, but hook changes are process-global.

Dependencies and integration points: Pulls in `stdarg.h`, Windows `LPSTR` conventions, and K4 generated error-table headers such as `kadm_err.h` and `krberr.h`. Load-function wrappers in this tree use the newer K5 com_err header, so callers must include the matching variant.

Risks: The substitute uses mutable global hooks and non-const `LPSTR` return types. `LPSTR` is conditionally defined only off Windows, so include order matters on Windows. WIN16 function-pointer indirection can crash if not initialized.

Test signals: Compile under `_WIN32`, non-Windows, and legacy WIN16 macro sets; verify hook install/reset behavior, varargs formatting, table-name lookup, and compatibility with generated K4 error table initialization.

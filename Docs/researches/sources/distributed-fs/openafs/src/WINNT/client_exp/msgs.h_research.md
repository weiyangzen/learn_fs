## sources/distributed-fs/openafs/src/WINNT/client_exp/msgs.h

Purpose: Declares the message formatting and string-loading helpers shared by the Explorer extension.

Important APIs/types: `ShowMessageBox`, `GetMessageString`, and `LoadString` are exported to local C++ modules. Default parameters let callers omit button flags and help IDs.

Control flow/state: Header has no logic; it defines varargs contracts tied to string-table format tokens.

Dependencies/integration: Includes `resource.h` and assumes MFC `CString` and Win32 `UINT` are in scope from `stdafx.h`.

Risks/tests: Varargs contracts are unchecked by the compiler. Test compile order, default parameters, and all resource format strings against call sites.

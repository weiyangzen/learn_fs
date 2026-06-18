# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/GetWebDll/GetWebDllFun.h

Purpose: C ABI export header for GetWebDll setup helper functions.

Important APIs/types/functions: declares `GetWebPage(LPSTR lpErrMsg, LPSTR lpFile, LPSTR lpCmdLine)`, `GetUserLogon(LPSTR lpUserName)`, and `BrowseFile(HWND hwndOwner, LPSTR lpstrTitle, LPSTR lpFileFullName, INT fullsize)` with `__declspec(dllexport)` and `extern "C"` guards.

Control flow: setup code can load/link these functions without C++ name mangling. The functions are implemented in `GetWebDll.cpp`.

State/persistence: no state in the header. `GetWebPage()` persists downloaded content to a file; `BrowseFile()` mutates the caller's filename buffer.

Dependencies/integration: depends on Windows/MFC type definitions being available before inclusion. It forms the boundary between InstallShield/native setup callers and the MFC DLL implementation.

Risks/test signals: this header uses `dllexport`, not an import/export macro, so it is tailored to building the DLL rather than consuming it from all contexts. ABI tests should verify calling convention assumptions, buffer sizes, and unmangled export names.

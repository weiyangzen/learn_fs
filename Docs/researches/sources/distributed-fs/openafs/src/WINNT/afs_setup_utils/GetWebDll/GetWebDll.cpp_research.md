# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/GetWebDll/GetWebDll.cpp

Purpose: implements an MFC extension DLL used by setup utilities to download a web page to a file, get the current user logon name, and display a file browser dialog.

Important APIs/types/functions: `CGetWebDllApp` is the MFC application object. `CTearSession` subclasses `CInternetSession` and reports connection status. `CTearException` carries local error codes. `StripTags()` removes HTML tags across buffer boundaries with static tag state. Exported `GetWebPage()` performs HTTP GET and writes response text to `lpFile`; `GetUserLogon()` wraps `GetUserName()`; `BrowseFile()` wraps `GetOpenFileName()`.

Control flow: `GetWebPage()` validates URL/output parameters, creates a `CFile`, parses only `http://` URLs with `AfxParseURL()`, opens a WinINet HTTP request with fixed headers, handles HTTP denied by invoking WinINet's password UI, follows one redirect by parsing `Location:`, then reads strings into a 1024-byte buffer and writes them to the output file. It catches `CInternetException`, `CFileException`, and `CTearException`, cleans up `CHttpFile`, `CHttpConnection`, and session objects, and returns a numeric setup-facing code.

State/persistence: global flags control strip/progress/access behavior, but the exported functions expose no setter in this file. `StripTags()` retains static cross-call tag state. The persistent effect is the downloaded output file. The error-message copy uses the existing length of `lpErrMsg` as the copy bound, so callers must preinitialize that buffer correctly or risk truncation/no copy.

Dependencies/integration: depends on MFC, WinINet, common dialog APIs, and `GetWebDllFun.h` exports. It is likely loaded by InstallShield/custom setup logic needing CellServDB or update data.

Risks/test signals: transport is HTTP-only with hard-coded request headers and minimal redirect handling. The code writes string lengths with `strlen()` even under `TCHAR`, and does not robustly bound URL/file copies. Tests should cover bad parameters, non-HTTP URLs, redirects without `Location`, denied authentication paths, output file errors, tag stripping across reads, and `BrowseFile()` offset calculation.

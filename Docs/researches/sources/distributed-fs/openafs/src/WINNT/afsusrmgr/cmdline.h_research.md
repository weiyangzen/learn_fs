# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/cmdline.h

Purpose: declares the Account Manager startup command-line result enum and parser entry point.

Important API/types: `CMDLINEOP` has `opCLOSEAPP`, `opNORMAL`, and `opNOCELLDIALOG`. `ParseCommandLine(LPTSTR pszCmdLine)` returns one of these to guide startup.

Control flow contract: application initialization calls `ParseCommandLine`; `opCLOSEAPP` aborts startup, `opNOCELLDIALOG` means an open-cell task has already been started, and `opNORMAL` proceeds to interactive cell selection.

State and persistence: no state in the header.

Dependencies/integration: depends on Windows/TCHAR types from the umbrella include chain.

Risks/test signals: parser side effects are not visible in the type signature: it opens admin-server connections, sets credentials, and may start tasks. Tests should verify startup handles each enum result correctly.

# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/progress_dlg.h

Purpose: C ABI declaration header for setup progress dialog helpers.

Important APIs/types/functions: declares `BOOL ShowProgressDialog(char *pszMsg)` and `void HideProgressDialog(void)` inside `extern "C"` guards for C++ consumers.

Control flow: callers show the dialog before a long task and hide it afterward.

State/persistence: no header state; implementation owns process-global dialog handles and message pointer.

Dependencies/integration: requires Windows `BOOL` type. Used by `afs_setup_utils.cpp` and implemented by `progress_dlg.cpp`.

Risks/test signals: header has no include guard. Compile tests should catch repeated inclusion issues and C/C++ linkage compatibility.

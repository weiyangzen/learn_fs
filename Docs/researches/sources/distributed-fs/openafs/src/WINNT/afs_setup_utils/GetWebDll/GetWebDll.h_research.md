# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/GetWebDll/GetWebDll.h

Purpose: main MFC header for the GetWebDll project.

Important APIs/types/functions: declares `CGetWebDllApp` as the DLL's `CWinApp`, `CTearSession` as the HTTP session subclass with an `OnStatusCallback()` override, and `CTearException` as a dynamic MFC exception carrying `m_nErrorCode`.

Control flow: consumers include `stdafx.h` first, then this header. Runtime behavior is implemented in `GetWebDll.cpp`; the header only binds class declarations and message-map macros.

State/persistence: no direct state. It defines object shapes that use MFC module state and exception allocation.

Dependencies/integration: requires MFC headers through `stdafx.h` and includes local `resource.h`. It is coupled to MFC ClassWizard conventions and the exported procedural functions in `GetWebDllFun.h`.

Risks/test signals: exported functions that call MFC must use `AFX_MANAGE_STATE()` in implementation if this DLL is dynamically linked to MFC; the source comments emphasize this but the exports should be checked. Compile tests should verify include order and message-map linkage.

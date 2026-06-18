# sources/distributed-fs/openafs/src/WINNT/client_exp/afs_shl_ext.h

Purpose: declares the MFC application object for the OpenAFS shell extension DLL.

Important types/APIs: `CAfsShlExt : public CWinApp` with constructor and `InitInstance` override; declares global `theApp`.

Control flow: MFC calls `InitInstance` during DLL initialization; COM class factories are registered in the implementation.

State/persistence: the app object holds normal MFC application state; no direct persistence in header.

Dependencies/integration: requires `stdafx.h` before inclusion, includes `resource.h`, and uses MFC message-map macros.

Risks: standard MFC extension pattern but tied to precompiled header ordering. Header exposes minimal shell-extension functionality; COM classes are elsewhere.

Test signals: DLL load with MFC state, resource availability, and global app initialization.

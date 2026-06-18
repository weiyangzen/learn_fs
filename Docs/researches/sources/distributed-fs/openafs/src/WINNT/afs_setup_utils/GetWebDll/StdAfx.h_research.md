# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/GetWebDll/StdAfx.h

Purpose: precompiled-header include for the MFC GetWebDll project.

Important APIs/types/functions: defines `VC_EXTRALEAN`, includes core MFC (`afxwin.h`, `afxext.h`), optional OLE/ODBC/DAO headers, IE4 common controls, common controls, and `afxinet.h` for WinINet/MFC internet classes.

Control flow: no runtime behavior. It controls the compilation environment and must be included before project headers expecting MFC declarations.

State/persistence: no state.

Dependencies/integration: tightly couples the DLL to MFC and Visual C++ precompiled-header conventions.

Risks/test signals: build configuration must match optional `_AFX_NO_*` feature macros. Tests are compile/link checks for MFC dynamic/static configurations and WinINet class availability.

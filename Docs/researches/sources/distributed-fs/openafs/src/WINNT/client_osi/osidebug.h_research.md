<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osidebug.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osidebug.h

Purpose: Declares resource IDs, window procedure prototypes, remote-debug client format cache shape, and small compatibility macros for the OSI remote-debug GUI.

Important APIs, types, and functions: Button/control IDs include `IDM_CMD1` through `IDM_CMD4`, `IDM_NAME`, `IDM_TYPES`, `IDM_RESULTS`, and `IDM_STATUS`; dialog/menu IDs include `IDM_ABOUT`, `IDM_HELP`, `IDM_FILEBOX`, and `IDM_FILENAME`. `dbrpc_v1_0_c_ifspecp` accounts for exported RPC interface indirection. `main_formatCache_t` stores cached type/region/index label and format data. The header declares `InitApplication`, `InitInstance`, `MainWndProc`, `About`, `FileProc`, `main_SetStatus`, and the global `main_screenText`.

Control flow and state: The format cache supports `osidebug.c` by memoizing format lookups, including negative entries where `labelp == NULL`. UI resource IDs drive `WM_COMMAND` routing and dialog callbacks.

Persistence and dependencies: No persistence. Depends on Win32 `HWND`, `HANDLE`, `RPC_IF_HANDLE`, and the generated RPC client symbol. The `GET_WM_HSCROLL_*` macros preserve compatibility between Win32 and older Windows message packing.

Integration points: Tied directly to `osidebug.c`, resource scripts, and generated `dbrpc` client stubs.

Risks: The header exposes globals and old-style prototypes. Resource ID collisions would break message routing. The manual declaration of `dbrpc_v1_0_c_ifspecp` is linker-specific and brittle.

Test signals: Build/link the GUI against generated RPC stubs, verify resource IDs match `.rc` resources, and exercise dialog callbacks on both WIN32 macro paths where relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osidebug.h -->

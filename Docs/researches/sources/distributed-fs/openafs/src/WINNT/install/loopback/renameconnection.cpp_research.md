<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/loopback/renameconnection.cpp -->
## sources/distributed-fs/openafs/src/WINNT/install/loopback/renameconnection.cpp

Purpose: Renames a Windows network connection identified by adapter GUID, using supported shell-folder APIs when available and an older `netshell.dll` fallback otherwise.

Important APIs, types, and functions: `rename_shellfolder` creates the Network Connections shell folder (`CLSID_NetworkConnections`), parses the adapter display name `::{GUID}`, and calls `IShellFolder::SetNameOf`. `RenameConnection` first calls `rename_shellfolder`; if it returns `E_NOTIMPL`, it loads `netshell.dll`, resolves undocumented `HrRenameConnection`, converts the GUID string to a CLSID, and calls the fallback.

Control flow and state: COM is initialized inside `rename_shellfolder` and uninitialized before returning. The fallback is only attempted for `E_NOTIMPL`, not all failures. Return value is `0` on success and `-1` on failure.

Persistence and dependencies: Persists the network connection display name. Depends on COM, shell APIs, Network Connections shell folder, and optionally `netshell.dll`.

Integration points: Called by `InstallLoopBack` after reading `NetCfgInstanceId`.

Risks: `pShellFolder` and `pShellMalloc` release handling is incomplete; COM interfaces are not released in all paths. `CoInitialize` return is ignored. The fallback uses an undocumented API. GUID length validation only checks `MAX_PATH`, not GUID syntax before shell parse.

Test signals: Rename on XP-era and newer platforms, fallback path simulation, invalid GUID/name handling, and COM leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/loopback/renameconnection.cpp -->

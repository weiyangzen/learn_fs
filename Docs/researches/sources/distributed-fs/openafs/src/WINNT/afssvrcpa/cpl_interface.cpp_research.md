<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcpa/cpl_interface.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcpa/cpl_interface.cpp

## Purpose
Implements the Windows Control Panel applet entry point for launching OpenAFS server configuration.

## Important APIs, Types, And Functions
`CPlApplet` handles CPL messages. `GetInstallDir` reads the server install directory from the registry. `LoadResString` loads localized strings.

## Control Flow
`CPL_INIT` loads modules/resources and builds the executable path. `CPL_GETCOUNT` returns one item. `CPL_NEWINQUIRE` fills icon/name/info. `CPL_DBLCLK` runs `afssvrcfg.exe`; `CPL_EXIT` frees resources.

## State And Persistence
Static module handles and app/path buffers; reads registry install directory but writes nothing.

## Dependencies And Integration Points
Uses Win32 CPL APIs, OpenAFS registry constants, `RegOpenKeyAlt`, and `TaLocale`.

## Risks And Edge Cases
Fixed buffers plus `strcpy`/`sprintf` risk overflow. Missing registry path yields a likely invalid executable path. `WinExec` is legacy with weak diagnostics.

## Test Signals
Applet load, resource/icon loading, valid/missing registry keys, long paths, and double-click launch failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcpa/cpl_interface.cpp -->

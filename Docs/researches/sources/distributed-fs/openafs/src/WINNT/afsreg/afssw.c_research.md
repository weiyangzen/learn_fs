# sources/distributed-fs/openafs/src/WINNT/afsreg/afssw.c

## Purpose
Implements convenience accessors for OpenAFS software configuration in the Windows registry: server/client install directories, client CellServDB directory, client cell name, and installed client/server version numbers.

## Important APIs, Types, And Functions
Exported functions include `afssw_GetServerInstallDir`, `afssw_GetClientInstallDir` (implemented but not declared in the companion header), `afssw_GetClientCellServDBDir`, `afssw_GetClientCellName`, `afssw_SetClientCellName`, `afssw_GetServerVersion`, and `afssw_GetClientVersion`. Private helpers are `StringDataRead`, `StringDataWrite`, and `DwordDataRead`.

## Control Flow
String reads open a configured registry key, use `RegQueryValueAlt`, validate `REG_SZ`, and return an allocated buffer. String writes create/open the target key and set a `REG_SZ` value. DWORD reads validate `REG_DWORD`. `afssw_GetClientInstallDir` falls back from the normal client software key to the legacy client-tools key. `afssw_GetClientCellServDBDir` prefers the `AFSCONF` environment variable, then the OpenAFS `CellServDBDir` registry value, then `All Users\Application Data\OpenAFS\Client` if it contains `CellServDB`, and finally the client install directory.

## State And Persistence
Reads expose persistent installer/service registry values. `afssw_SetClientCellName` writes the client service `Parameters\Cell` value. Returned string buffers are heap-allocated and owned by the caller. The CellServDB directory lookup also observes process environment and filesystem existence of a CellServDB file.

## Dependencies And Integration Points
The module depends on `afsreg.h`, `afssw.h`, `nterr_nt2unix` error mapping, Win32 registry APIs, `SHGetFolderPath`, and file existence checks through `CreateFile`. It is used by configuration tools such as `regman.c` and likely server/client setup code.

## Risks And Test Signals
Risks include undeclared `afssw_GetClientInstallDir` in `afssw.h`, string buffer/path truncation around fixed 512-byte `wdir`, mixed slash conventions while constructing default server paths, and reliance on legacy registry keys. Test signals include reading all install/version values from test registry fixtures, setting and re-reading the client cell, exercising `AFSCONF` override, and validating fallback to common appdata when `CellServDB` exists.

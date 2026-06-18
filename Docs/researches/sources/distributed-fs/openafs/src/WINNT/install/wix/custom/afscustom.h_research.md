<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/wix/custom/afscustom.h -->
## sources/distributed-fs/openafs/src/WINNT/install/wix/custom/afscustom.h

Purpose: Declares OpenAFS WiX/MSI custom action exports, helper functions, registry/service constants, and MSI error codes.

Important APIs, types, and functions: `MSIDLLEXPORT` expands to `UINT __stdcall`. Helper macros `CHECK`, `CHECKX`, and `CHECK2` jump to `_cleanup`. Constants define provider-order registry path/value, service names (`TransarcAFSDaemon`, `AFSRedirector`, `LanmanWorkstation`), provider-order result codes, and MSI error codes. Helper prototypes include `npi_CheckAndAddRemove`, `InstNetProvider`, `ShowMsiError`, `ConfigService`, and admin group functions. Export prototypes include network provider install/uninstall, redirector provider install/uninstall, client/server service configuration, abort, NSIS uninstall, and admin group create/remove.

Control flow and state: The header establishes the MSI custom action ABI consumed by WiX tables and implemented in `afscustom.cpp`.

Persistence and dependencies: Implementations persist registry/service/group state. Header depends on Windows, SetupAPI, MSI query, stdio/string, and NetAPI headers.

Integration points: Included by `afscustom.cpp` and used to export functions from the custom action DLL.

Risks: Export declarations omit explicit return type before macro names in old C/C++ style (`MSIDLLEXPORT InstallNetProvider`), relying on compiler tolerance. Several implemented exports for registry backup/detection are not declared here. Cleanup macros require local labels and `msiErr` variables in callers that use them.

Test signals: Build with modern compiler warnings, verify DLL exports match WiX custom action names, and check header coverage for all implemented custom actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/wix/custom/afscustom.h -->

# sources/distributed-fs/openafs/src/WINNT/client_cpa/resource.h

Purpose: defines resource identifiers used by the OpenAFS Control Panel applet.

Important identifiers: string IDs `IDS_CPL_NAME_NT`, `IDS_CPL_DESC_NT`, `IDS_CPL_NAME_95`, `IDS_CPL_DESC_95`, `IDS_CPL_NAME_CCENTER`, and `IDS_CPL_DESC_CCENTER` supply localized applet name/description variants. Icon IDs `IDI_AFSD` and `IDI_CCENTER` select the normal AFS client icon or configuration-center icon.

Control flow: no executable code. The IDs are consumed by `cpl_interface.cpp` through `GetString` and `TaLocale_LoadIcon`.

State/persistence: none.

Dependencies/integration: synchronized with applet `.rc` resources and localized satellite resources. The numeric values are part of the resource ABI for the applet binary.

Risks: mismatched IDs between this header and resource scripts can produce wrong labels or missing icons. String IDs start at zero, so lookup helpers must correctly support zero-valued resource IDs.

Test signals: resource compilation, localized resource load tests, and manual CPL inspection for each client-installed/NT branch.

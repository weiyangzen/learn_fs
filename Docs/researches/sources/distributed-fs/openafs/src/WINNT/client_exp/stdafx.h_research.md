## sources/distributed-fs/openafs/src/WINNT/client_exp/stdafx.h

Purpose: Defines the shared precompiled include surface for client-exp modules.

Important APIs/types: Sets `VC_EXTRALEAN`, `ISOLATION_AWARE_ENABLED`, disables MFC DB/DAO support, includes MFC core/extensions/OLE/common-controls headers, defines `UNCHECKED`/`CHECKED`, and includes `help.h`, `TaLocale.h`, and `afxdlgs.h`.

Control flow/state: No runtime logic; compile-time feature macros influence all including translation units.

Dependencies/integration: Central to all MFC dialog and shell extension builds. Debug builds can remap `new` to `DEBUG_NEW`.

Risks/tests: Global macros can affect Windows/MFC behavior across the project. Test with OLE support enabled/disabled, Unicode/non-Unicode builds, common-control manifests, and include order with Winsock users.

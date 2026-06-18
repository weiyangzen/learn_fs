<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/afsapplib.h -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/afsapplib.h

Purpose: public header for the Windows AFS Application Library. It aggregates common UI, dialog, tasking, credential, remote-admin, image, help, and utility APIs for OpenAFS Windows tools.

Important APIs/types/functions: defines `EXPORTED`, instance macros, `cchNAME`, and debug normalization. Includes TaLocale and many AfsAppLib component headers. Declares app name/main-window APIs, remote admin-server open/close/client-id APIs, cell-list management, browse user/group and fileset dialogs, cover-window APIs, credential dialogs/checks, task queue APIs, error dialogs, modeless dialog pump helpers, window data helpers, image-list helpers, help registration, font/instance helpers, animation, time conversion, error translation, local-cell lookup, and `REALLOC` via `AfsAppLib_ReallocFunction()`.

Control flow: applications include this single header, set instance/main-window/app-name state, then call specialized AfsAppLib functions. If the admin-server client header is already included, this header conditionally includes `al_admsvr.h` to remap `asc_*` calls through AfsAppLib.

State and persistence: the header declares APIs whose implementations maintain UI globals, modeless-dialog lists, task queues, settings, credentials, and admin-server client state. The header itself has no storage.

Dependencies/integration: integrates Windows APIs, TaLocale resources, OpenAFS admin client/server types, and local helper components such as hash lists, resize, subclassing, custom controls, settings, fast lists, wizard/progress, and regex.

Risks and test signals: this is a broad umbrella header with conditional macro remapping, so include order matters. Tests should compile consumers with and without `TAAFSADMSVRCLIENT_H`, DLL export/import modes, and direct `asc_*` use through AfsAppLib. API tests should also cover `REALLOC` growth and ownership conventions for returned lists/strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/afsapplib.h -->

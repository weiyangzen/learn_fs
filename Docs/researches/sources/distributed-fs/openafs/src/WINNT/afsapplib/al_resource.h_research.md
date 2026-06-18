## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_resource.h

Purpose: Defines numeric resource, dialog, control, bitmap, icon, and string identifiers for the app library's Win32 resources.

Important APIs and definitions: String IDs cover credential and browse/error messages. Control IDs include open-cell, credentials, bad-credentials, browse, cover, and error controls. Dialog IDs include `IDD_APPLIB_OPENCELL`, `IDD_APPLIB_CREDENTIALS`, `IDD_APPLIB_ERROR`, `IDD_APPLIB_BADCREDS`, `IDD_APPLIB_COVER`, and browse dialogs. Icon/bitmap IDs cover AFS object icons and spinner frames.

Control flow: Header-only constants; used by resource scripts and C++ code for dialog/control lookup and localized string loading.

State and persistence: None, but numeric stability is part of the binary/resource contract.

Dependencies and integration points: Shared by implementation files, language resource `.rc` files, and Visual Studio resource tooling (`APSTUDIO_INVOKED` block).

Risks: Duplicate numeric IDs exist for `IDC_COVER_BORDER` and `IDC_BROWSE_TYPE` by design or accident; code must only use them in disjoint dialogs. Changing values can break existing resource scripts or compiled dialogs.

Test signals: Resource compiler checks, dialog smoke tests for every ID looked up by code, and icon/image-list load tests.

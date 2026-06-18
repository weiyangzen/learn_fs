## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_misc.cpp

Purpose: Provides library startup, image-list/icon helpers, spinner animation, AFS error translation, cell-list management, time/credential utility functions, reallocation, and font creation.

Important APIs and functions: `DllEntryPoint` initializes locale, error translation, common controls, and custom control classes. `AfsAppLib_CreateImageList`/`AfsAppLib_AddToImageList` build standard AFS object icon lists. `AfsAppLib_StartAnimation`/`StopAnimation` animate static icons. `AfsAppLib_TranslateErrorFunc` and `AfsAppLib_TranslateError` bridge admin-server/local utility error text. Cell APIs include `AfsAppLib_GetCellList`, `AfsAppLib_AddToCellList`, and `AfsAppLib_FreeCellList`. Utility APIs include `AfsAppLib_IsTimeInFuture`, `AfsAppLib_UnixTimeToSystemTime`, `AfsAppLib_SplitCredentials`, `AfsAppLib_GetLocalCell`, `AfsAppLib_ReallocFunction`, and `AfsAppLib_CreateFont`.

Control flow: DLL attach registers custom controls and error translation. Error translation prefers admin server, otherwise opens `AfsAdminUtil.dll`. Cell list reading enumerates registry subkeys, ensures the local cell is first, and trims null tail entries. Local cell lookup caches the first successful result in a static buffer. Animation uses a timer hook storing frame index in window data.

State and persistence: Holds process-level module handles, cached app instance, cached local cell, static animation icons, and registry-backed cell list entries. `AfsAppLib_AddToCellList` persists cells by creating registry keys.

Dependencies and integration points: Integrates with `TaLocale`, dynamic link helpers, `TaAfsAdmSvrClient`, image list common controls, custom control registration functions, registry APIs, and `SetErrorTranslationFunction`.

Risks: Static caches are not synchronized. Animation icons are never destroyed. Some registry operations use legacy `RegOpenKey`/`RegEnumKey`. `AfsAppLib_CreateFont` mutates the loaded resource string while parsing and assumes comma sections exist. Time conversion has manual FILETIME offset logic and elapsed mode subtracts fields from 1970/1/1.

Test signals: Load/unload DLL, verify every custom class registers; test 16/32 icon list sizes; animate start/stop; translate AFS/admin/unknown statuses; enumerate/persist cells; local cell fallback; Unix time conversion including elapsed; font resource parsing.

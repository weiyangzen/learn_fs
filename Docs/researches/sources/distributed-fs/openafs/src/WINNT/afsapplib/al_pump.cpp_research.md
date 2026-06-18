## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_pump.cpp

Purpose: Provides the main message pump's modeless-dialog routing and a small per-window key/value storage facility.

Important APIs and functions: `AfsAppLib_RegisterModelessDialog`, `AfsAppLib_IsModelessDialogMessage`, `AfsAppLib_SetPumpRoutine`, and `AfsAppLib_MainPump` manage modeless dialog dispatch. `GetWindowDataField`, `GetWindowData`, and `SetWindowData` associate named `UINT_PTR` values with HWNDs. Hook procedures `Modeless_HookProc` and `WindowData_HookProc` remove entries on `WM_DESTROY`.

Control flow: Registered modeless dialogs are stored in `aModeless`; the main pump calls `IsDialogMessage` or property-sheet equivalents before ordinary translate/dispatch. Window data maps field names to numeric indexes and stores per-window arrays grown on demand. Destroy hooks clear modeless/window-data entries and free arrays.

State and persistence: Global dynamic arrays for modeless HWNDs, field names, window data, and two lazily allocated critical sections. No durable persistence.

Dependencies and integration points: Uses `subclass.h`, property sheet helpers, `REALLOC`, and app-wide message pump setup. Animation in `al_misc.cpp` uses window data for current frame.

Risks: `GetWindowData` and `SetWindowData` enter `pcsData` and call `GetWindowDataField`, which also enters the same critical section; Win32 critical sections are reentrant for the owning thread, but this subtle dependency matters. Brush/object cleanup is not relevant here, but global arrays never shrink. Using text field names has typo/collision risk.

Test signals: Register/destroy modeless dialogs, property sheet page closure, custom pump routine execution, multiple fields per window, overwriting/clearing values, and destroy cleanup.

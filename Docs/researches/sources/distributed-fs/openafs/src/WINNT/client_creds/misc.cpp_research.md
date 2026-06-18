# sources/distributed-fs/openafs/src/WINNT/client_creds/misc.cpp

Purpose: miscellaneous utilities for dynamic allocation, reminder persistence, time conversion, and tab child lookup.

Important APIs/functions: `AfsCredsReallocFunction`, `LoadRemind`, `SaveRemind`, `TimeToSystemTime`, `GetTabParam`, and `GetTabChild`.

Control flow: the realloc helper grows arrays in increments, zeroes new storage, copies old data, and frees old storage. Reminder helpers read/write per-cell DWORD values under `HKCU\...\Reminders`. Tab helpers query common-control item lParams and find the active dialog child under a tab control.

State/persistence: writes `g.aCreds[i].fRemind` to registry and defaults reminders to enabled when no registry value exists. Uses OpenAFS allocation wrappers.

Dependencies/integration: used by credential enumeration, tab repopulation, and dialog update code. Depends on `TaLocale`/dialog allocation helpers through `afscreds.h` and registry view helper `IsWow64`.

Risks: array growth can overflow `cbElement * cNew` on pathological sizes. Reminder value names are raw cell names, so unusual cell-name characters could affect registry behavior. `GetTabChild` assumes dialog class `#32770`.

Test signals: realloc growth/copy/zero behavior, registry reminder default/read/write, time conversion around local timezone/DST, and tab-child lookup after tab changes.

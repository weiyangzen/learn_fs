# sources/distributed-fs/openafs/src/WINNT/client_config/tab_prefs.cpp

## Purpose
`tab_prefs.cpp` implements the Server Preferences tab for viewing, importing, adding, editing, ranking, and applying file-server and VL-server preferences.

## Important APIs, Types, and Functions
Key routines are `PrefsTab_DlgProc`, `PrefsTab_OnInitDialog`, `PrefsTab_CommitChanges`, `PrefsTab_OnApply`, `PrefsTab_OnRefresh`, `PrefsTab_OnFillList`, `PrefsTab_OnUpDown`, `PrefsTab_OnAdd/Edit/Import`, `PrefsTab_MergeServerPrefs`, `PrefsTab_AddItem`, refresh/name-resolution thread routines, sort/hash callbacks, and `PrefsEdit_*`.

## Control Flow
Initialization sets list columns and starts refresh. Refresh spawns a thread that retrieves server preferences through `Config_GetServerPrefs`, merges new values into `g.Configuration`, fills the list, starts a background reverse-DNS thread, and enables controls based on service state. Users can switch between FS/VL lists, adjust ranks, add/edit servers, or import text files containing server/rank pairs. Apply sends changed preferences back through `Config_SetServerPrefs`.

## State and Persistence Behavior
`g.Configuration.pFServers` and `pVLServers` hold mutable preference arrays. `SERVERPREF.fChanged` marks entries to send on apply; `g.Configuration.fChangedPrefs` gates apply. Background thread state is guarded by a critical section in static `l`.

## Dependencies and Integration Points
The tab integrates with `config.cpp` pioctl server-pref APIs, Winsock DNS, custom fastlist/spinner controls, the hashlist utility for merging, and General tab commit ordering through `PrefsTab_CommitChanges`.

## Risks and Edge Cases
Thread cancellation appears inverted: setting `*pfStopFlag = FALSE` when a thread is active does not request stop if the worker exits on true. `PrefsTab_MergeServerPrefs` copies `sizeof(SERVERPREFS)` into a `SERVERPREF` slot, which is likely a memory-corrupting bug. Threads update UI controls directly from worker threads, a Win32 threading risk. Import allocates `sizeof(TCHAR) * (cbLength + 2)` for byte length and reads bytes into a TCHAR buffer, unsafe for Unicode.

## Test Signals
Tests should cover stopped-service disabling, pioctl refresh/apply, FS/VL switching, rank changes and sorting, add/edit duplicate handling, import parsing, merge de-duplication, background reverse-DNS updates, and thread cancellation/race behavior.

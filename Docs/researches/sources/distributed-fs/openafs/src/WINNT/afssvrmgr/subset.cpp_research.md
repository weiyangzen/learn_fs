# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/subset.cpp

Purpose: Implements server subset filtering for a cell, including in-memory monitor decisions, subset edit UI, load/save dialogs, and registry persistence.

Important APIs/functions: `Subsets_fMonitorServer` evaluates whether a server is included based on inclusive (`pszMonitored`) or exclusive (`pszUnmonitored`) multistrings. `Subsets_SetMonitor` mutates a subset for one server. `ShowSubsetsDialog` opens the modal property sheet. `Subsets_OnApply` copies dialog state into global `g.sub` and starts `taskAPPLY_SUBSET`. `Subsets_SaveIfDirty` prompts save/discard/cancel for modified subsets. `Subsets_EnumSubsets`, `Subsets_SaveSubset`, and `Subsets_LoadSubset` use registry keys. `Subsets_CopySubset`/`Subsets_FreeSubset` manage allocation. The open/save dialog supports list, delete, and rename.

Control flow: The edit sheet receives a copy of `g.sub`. Checkbox list changes create a subset if needed, rebuild monitored/unmonitored multistrings from UI, update display name, and mark the sheet dirty. Load replaces the current subset with registry-loaded content; save prompts for a name and writes the current server list. Apply swaps `g.sub` to a copy of dialog state and triggers refresh. The open/save dialog enumerates subset registry subkeys and supports overwrite confirmation and rename by load-save-delete.

State and persistence: `SUBSET` contains `szSubset`, `fModified`, and either an inclusive or exclusive allocated multistring. Registry persistence uses `REGVAL_INCLUSIVE` as a DWORD and stores each server name as a value set to `"X"` under a subset subkey. `OpenSubsetsKey/OpenSubsetsSubKey` are external helpers. `g.sub` is the active filter.

Dependencies/integration: Uses prop sheet cache (`pcGENERAL`), global cell/server identities, task `taskSUBSET_TO_LIST`, `taskAPPLY_SUBSET`, resource dialogs, listbox/listview helpers, and registry APIs.

Risks: `Subsets_SaveSubset` does not clear old registry values before writing new entries unless `OpenSubsetsSubKey` with create mode replaces/cleans externally; stale values could persist. Inclusive/exclusive semantics are compact but easy to misinterpret: a single checked server uses `pszMonitored`, otherwise unchecked servers use `pszUnmonitored`. `Subsets_OnApply` passes the original `sub` to `taskAPPLY_SUBSET` after copying it into `g.sub`, so task ownership/lifetime must be checked elsewhere. Rename overwrite prompt formats `lpp->szSubset` instead of the proposed text in one branch, which may display the wrong name.

Test signals: No subset, single-server subset, all/none toggles, inclusive vs exclusive save/load round-trip, dirty save/discard/cancel, subset delete, rename into existing name, case-insensitive long/short server matching, and refresh after apply.

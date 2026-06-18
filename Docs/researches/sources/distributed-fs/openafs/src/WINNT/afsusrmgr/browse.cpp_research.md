# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/browse.cpp

Purpose: implements a reusable modal browse dialog for selecting AFS Account Manager users and/or groups, with pattern search, optional exclusion list filtering, and name-to-ASID translation.

Important APIs/functions: `ShowBrowseDialog` chooses the dialog template and returns selected objects. `Browse_DlgProc` handles delayed search timers, commands, async task completions, and list notifications. `Browse_OnInitDialog` configures title/prompt/cell/type controls and initial list population. `Browse_UpdateDialog` starts `taskUSER_ENUM` or `taskGROUP_ENUM`. `Browse_OnEndTask_EnumObjects` populates the FastList. `Browse_OnOK` starts `taskLIST_TRANSLATE`; `Browse_OnEndTask_Translate` transfers the selected ASID list back to the caller.

Control flow: typing in the pattern field starts a 650ms debounce timer before requery. While querying, the list shows a non-selectable "querying" row and `fQuerying` suppresses selection feedback. OK disables controls and translates typed names, allowing manual entry independent of visible list selection.

State and persistence: state is held in caller-owned `BROWSE_PARAMS`, including `fQuerying`, selected objects, and display name. No registry writes occur.

Dependencies/integration: uses `TaAfsUsrMgr.h`, `usr_col.h`, admin-server client APIs (`asc_CellNameGet_Fast`, `asc_ObjectPropertiesGet_Fast`, ASID list helpers), FastList, task queue, and localized resources.

Risks: `Browse_OnEndTask_EnumObjects` loops over `TASKDATA(ptp)->pAsidList` after only an outer success guard; if the task succeeds with a null list, it can dereference null. `fQuerying` is a boolean in the header but incremented/decremented as a counter. Multiple outstanding enum tasks can complete out of order and overwrite newer results. Tests should cover debounce ordering, skip-list filtering, multi-select formatting, manual translation failure, and ownership transfer of `pObjectsSelected`.

## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/display.cpp

Purpose: maintains list display population, active-tab selection helpers, FastList view refresh, lazy item text, column sorting, and work animation.

Important APIs/types/functions: `Display_StartWorking`/`StopWorking` reference-count the animation. `Display_Populate*List` reads tab filter text and starts `taskUPD_USERS`, `taskUPD_GROUPS`, or `taskUPD_MACHINES`. `Display_OnEndTask_Upd*` reconciles returned `ASIDLIST`s into FastList controls. `Display_RefreshView`, `Display_RefreshView_Fast`, `Display_SelectAll`, `Display_GetSelectedList`, `Display_GetSelectedCount`, `Display_GetActiveTab`, `Display_HandleColumnNotify`, `Display_GetItemText`, and `Display_GetImageIcons` form the display API.

Control flow: population starts only when `g.idCell` exists and the relevant list control is live. Completion handlers ignore stale async results by comparing `TASKDATA(ptp)->szPattern` to the current global pattern. They build a `HASHLIST` of returned ASIDs, remove no-longer-present FastList items, add new ones, and update title text. FastList lazy text callbacks call user/group/machine column functions based on the `VIEWINFO` cookie.

State and persistence behavior: uses global filter strings (`g.szPatternUsers`, `g.szPatternGroups`, `g.szPatternMachines`) and restored view/icon state (`gr.viewUsr`, `gr.viewGrp`, `gr.viewMch`, `gr.ivUsr`, `gr.ivGrp`, `gr.ivMch`). Column resize/click events store sort/column state through `FL_StoreView`.

Dependencies and integration points: depends on FastList, AfsAppLib image lists/animation, task packets, `usr_col`, `grp_col`, `mch_col`, `Main_SetMenus`, and OpenAFS admin cache APIs. It is the bridge between async task results and visible objects.

Risks: `l_cReqAnimation` must stay balanced across all task paths; extra stops hide active work, missing stops leave animation running. Several functions discover the active list by probing for group, then user, then machine list controls; dialog-layout changes could break this. `Display_GetImageIcons` has alert logic stubbed as always false.

Test signals: start overlapping refreshes, change search filters before completion, switch tabs during refresh, resize/click columns, select all, sort numeric and alphabetic columns, and verify no stale results replace current lists.

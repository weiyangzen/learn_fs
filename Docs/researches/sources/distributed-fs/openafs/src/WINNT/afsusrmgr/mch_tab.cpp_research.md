## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_tab.cpp

Purpose: dialog procedure for the Machines tab, mirroring the Groups tab for machine-account search, display, and command routing.

Important APIs/types/functions: `Machines_DlgProc`, `Machines_EnableButtons`, local search timer constants, and static debounce state.

Control flow: initialization configures FastList image lists/view, lazy text callback, saved machine pattern, and initial population. Pattern edits debounce via timer before `Display_PopulateMachineList`. Context menus call `OnRightClick(pmMACHINE, ...)`; commands route through `OnContextCommand`; selection/double-click update menus/buttons or open properties.

State and persistence behavior: interacts with `g.szPatternMachines`, `gr.viewMch`, and `gr.ivMch`.

Dependencies and integration points: depends on display helpers, command routing, FastList, main menu state, and machine column metadata.

Risks: duplicated structure with `grp_tab.cpp` can drift. Properties/membership buttons are enabled purely by selection count; deeper command handlers decide whether selected machine ASIDs map to supported user property flows.

Test signals: quick filter typing, refresh debounce, right-click menu, double-click properties, selection enablement, and tab switch/destruction during pending timer.

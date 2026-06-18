# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_search.cpp

Purpose: implements the advanced user search dialog and default search settings.

Important APIs and control flow: `Users_SetDefaultSearchParams` resets `AFSADMSVR_SEARCH_PARAMS` to `SEARCH_NO_LIMITATIONS`. `Users_ShowAdvancedSearch` opens `IDD_SEARCH_USERS`. Initialization mirrors `gr.SearchUsers` into radio buttons and date controls. OK updates `gr.SearchUsers` for all users, account expiration before a date, or password expiration before a date; if the structure changed, it calls `Display_PopulateList`.

State and dependencies: persistent search state lives in global `gr.SearchUsers`; this module only edits it. Dependencies include date controls (`DA_SetDate`, `DA_GetDate`), resource IDs, and display population.

Risks and test signals: date values are only meaningful for the selected search type, so tests should verify switching search modes preserves expected dates and triggers refresh only when the effective structure changes.

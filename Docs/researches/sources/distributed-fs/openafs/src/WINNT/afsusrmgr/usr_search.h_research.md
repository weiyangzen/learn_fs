# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_search.h

Purpose: declares the advanced user search helpers.

Important APIs/types: exports `Users_ShowAdvancedSearch(HWND hParent)` and `Users_SetDefaultSearchParams(LPAFSADMSVR_SEARCH_PARAMS)`.

State and dependencies: depends on AFS admin search parameters and Windows UI handles. Search persistence is external in global preferences.

Risks and test signals: callers should refresh user lists after changed search settings. Tests should verify default parameters and dialog-to-global update behavior.

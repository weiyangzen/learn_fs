# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_getdates.cpp

Purpose: Implements UI to query modification dates for a server file and its `.BAK`/`.OLD` variants.

Important APIs/functions: `Server_GetDates` opens/focuses singleton input dialog. `Server_GetDates_DlgProc` enumerates servers and validates filename. `Server_GetDates_OnOK` opens a results dialog. `Server_GetDates_Results_OnInitDialog` starts `taskSVR_GETDATES`. `Server_GetDates_Results_OnEndTask_InitDialog` formats up to three returned date strings into result controls.

Control flow: Server combo starts disabled during `taskSVR_ENUM_TO_COMBOBOX`. OK in the first dialog allocates a results packet and destroys the input dialog. Results dialog starts the actual getdates task, fills server/filename labels, then shows itself after task completion.

State and persistence: `SVR_GETDATES_PARAMS` stores server identity and filename. No persisted state.

Dependencies/integration: Uses prop cache, server enumeration, task data string fields (`pszText1..3`), and resource formatting.

Risks: Results dialog allocates a copy of input params for the task but the original `lppIn` lifetime depends on first dialog destruction; current flow fills labels immediately before destruction side effects matter. No error message is shown on failed getdates in this file.

Test signals: Empty filename validation, server enum failure, success with one/two/three returned dates, task failure, duplicate input dialog focus, and lifecycle around input/result dialogs.

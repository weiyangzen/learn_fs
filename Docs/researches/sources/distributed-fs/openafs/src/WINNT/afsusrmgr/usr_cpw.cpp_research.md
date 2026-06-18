# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_cpw.cpp

Purpose: implements the change-password/server-key dialog for a single user.

Important APIs and control flow: `User_ShowChangePassword` opens `IDD_USER_PASSWORD`. The dialog initializes by fetching current user properties and displaying the target user name; it lets the operator choose automatic or manual key version and string-derived or raw key data. `User_Password_OnType` enables OK only when a string password is present or `ScanServerKey` accepts raw key text. `User_Password_OnRandom` starts `taskGET_RANDOM_KEY`, and `User_Password_OnEndTask_Random` formats returned key bytes into the raw-key field. `User_Password_OnOK` builds `USER_CPW_PARAMS` and starts `taskUSER_CPW`.

State and dependencies: the target `ASID` is stored in `DWLP_USER`; real mutation is delegated to `task.cpp`. Dependencies include `usr_col` for display names, server-key scan/format helpers, spinner helpers, and the task framework.

Risks and test signals: raw key validation, manual key-version bounds, and random-key task failure handling are key risk points. Tests should cover string vs data paths, automatic vs manual versions, random-key failure disabling, and task payload contents.

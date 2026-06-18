# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_create.cpp

Purpose: implements the new-user dialog and default creation settings.

Important APIs and control flow: `User_SetDefaultCreateParams` initializes `USERPROPINFO` defaults for KAS/PTS creation, tickets, quota, ACLs, password policy, and lockout. `User_ShowCreate` copies persisted defaults from `gr.CreateUser`, opens `IDD_NEWUSER`, and frees temporary membership/ownership lists. The dialog validates password presence and confirmation, supports auto/manual UID, disables manual UID for multiple names, opens the advanced property sheet for initial properties/memberships, splits names into a multi-string, and starts `taskUSER_CREATE`.

State and dependencies: `CREATEUSERDLG` holds dialog-local password, UID, and advanced property state. Defaults are saved back to `gr.CreateUser` after successful OK. Cell max user ID is fetched asynchronously via `taskOBJECT_GET` to show the next auto ID.

Risks and test signals: multi-name parsing and UID behavior are sensitive; auto/manual ID must be disabled correctly for batch creation. Password validation is UI-side only before task delegation. Test single and multiple names, separator handling, password mismatch, advanced membership preservation, and object-get failure or stale max-ID display.

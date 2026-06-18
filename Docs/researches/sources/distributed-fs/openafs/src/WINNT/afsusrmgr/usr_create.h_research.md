# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_create.h

Purpose: declares new-user creation helpers for the Windows User Manager.

Important APIs/types: `User_SetDefaultCreateParams` fills a `USERPROPINFO` structure with baseline new-user defaults, and `User_ShowCreate` opens the modal create dialog.

State and dependencies: depends on `USERPROPINFO` from `usr_prop.h`, Windows dialog handles, and global runtime settings in the implementation. The header has no state.

Risks and test signals: creation defaults are part of user-visible behavior, so tests should verify the defaults after reset/startup and that callers use `User_ShowCreate` rather than constructing task payloads inconsistently.

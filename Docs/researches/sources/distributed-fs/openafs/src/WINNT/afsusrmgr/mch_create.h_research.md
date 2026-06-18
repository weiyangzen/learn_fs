## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_create.h

Purpose: declares machine creation defaults and dialog launcher.

Important APIs/types/functions: `Machine_SetDefaultCreateParams(LPUSERPROPINFO lpp)` and `Machine_ShowCreate(HWND hParent)`.

Control flow: startup initializes default machine creation state; command dispatch opens the new-machine dialog.

State and persistence behavior: default initializer fills `gr.CreateMachine` with machine-specific user property defaults.

Dependencies and integration points: depends on `USERPROPINFO` from user property modules.

Risks: machine defaults share a user-property structure, so user-only fields must remain deliberately disabled/zero for machine accounts.

Test signals: fresh settings should produce PTS-only machine defaults, no KAS creation, and expected quota/permission values.

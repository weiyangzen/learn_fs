## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_create.h

Purpose: declares group creation defaults and dialog launcher.

Important APIs/types/functions: `Group_SetDefaultCreateParams(LPGROUPPROPINFO lpp)` and `Group_ShowCreate(HWND hParent)`.

Control flow: startup calls the default initializer for first-run restored settings; command handling calls `Group_ShowCreate` from `M_GROUP_CREATE`.

State and persistence behavior: default initializer prepares a `GROUPPROPINFO` that later lives in `gr.CreateGroup`.

Dependencies and integration points: depends on `GROUPPROPINFO` from `grp_prop.h` via the broader include graph.

Risks: changing `GROUPPROPINFO` requires updating default initialization or new groups may inherit undefined permissions.

Test signals: fresh settings should produce predictable access controls, owner/creator blanks, and no preselected members.

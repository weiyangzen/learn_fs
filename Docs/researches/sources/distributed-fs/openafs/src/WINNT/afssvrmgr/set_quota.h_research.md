# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_quota.h

Purpose: Declares quota edit/display APIs and the task packet used to apply a new fileset quota.

Important APIs/types: `SET_SETQUOTA_APPLY_PARAMS` contains the target fileset identity and quota in KB. `Filesets_SetQuota` applies or prompts, `Filesets_PickQuota` opens the picker, and `Filesets_DisplayQuota` renders quota usage into a dialog.

Control flow/state: UI callers can pass zero to prompt the user or a nonzero quota for immediate async application.

Dependencies/integration: Requires `LPIDENT`, `size_t`, `HWND`, and `LPFILESETSTATUS` from the server manager framework.

Risks/test signals: Ensure callers understand that zero means "ask" rather than "set unlimited quota"; if the lower task layer supports zero quota semantics, this API cannot express it directly.

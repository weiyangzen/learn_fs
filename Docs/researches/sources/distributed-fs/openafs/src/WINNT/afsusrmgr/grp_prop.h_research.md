## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_prop.h

Purpose: defines group property-sheet tabs, data model, and public property APIs.

Important APIs/types/functions: `GROUPPROPTAB` includes `gptANY`, `gptPROBLEMS`, `gptGENERAL`, and `gptMEMBERS`; `nGROUPPROPTAB_MAX` is 3. `GROUPPROPINFO` contains selected groups, modal/deletion flags, owner window handle, general permission values and mixed flags, owner/creator strings, and member/owned-group ASID lists. Public functions are `Group_ShowProperties` overloads and `Group_FreeProperties`.

Control flow: callers either pass an `LPASIDLIST` for existing groups or a prepared `GROUPPROPINFO` for advanced creation. Target tab selects initial property-sheet tab.

State and persistence behavior: the structure is the mutable state for property dialogs and is reused as part of `gr.CreateGroup` defaults.

Dependencies and integration points: depends on OpenAFS account access enums, ASID lists, and dialog/window types from the shared application headers.

Risks: fields with `_Mixed` flags must be interpreted together with values; forgetting to preserve mixed fields can overwrite multi-selection properties. Ownership flags (`fDeleteMeOnClose`, `fShowModal`) control lifetime and must be set by every caller.

Test signals: validate initialization for existing single, existing multi, and new-group advanced cases; check no stale ASID lists survive after `Group_FreeProperties`.

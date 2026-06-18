# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/browse.h

Purpose: declares the reusable Account Manager browse dialog parameter block and entry point.

Important API/types: `BROWSE_PARAMS` includes parent/help/title/prompt/check resources, type mask (`TYPE_USER`/`TYPE_GROUP`), optional objects-to-skip, output selected ASID list, multiple-selection flag, display name buffer, and internal query flag. `ShowBrowseDialog` returns `TRUE` only when a non-empty selected list is available.

Control flow contract: callers allocate and initialize `BROWSE_PARAMS`, call the modal dialog, then own `pObjectsSelected` on success. `fQuerying` is marked internal and reset by the implementation.

State and persistence: no persistent state; output is returned in the same struct.

Dependencies/integration: depends on `HWND`, resource ids, `ASOBJTYPE`, `LPASIDLIST`, `cchNAME`, and task/list helpers included elsewhere.

Risks/test signals: header declares `fQuerying` as `BOOL` despite counter-like use. Callers must free `pObjectsSelected`. Tests should check both one-type and two-type template selection.

## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_delete.h

Purpose: declares the machine-account delete dialog entry point.

Important APIs/types/functions: `Machine_ShowDelete(LPASIDLIST pMachineList)`.

Control flow: command dispatch passes homogeneous machine selections to this function.

State and persistence behavior: no persistent state; selected ASID list is dialog-owned after the call.

Dependencies and integration points: integrates with command selection classification and user-delete task infrastructure.

Risks: API cannot enforce that ASIDs are machine accounts; callers must pre-filter.

Test signals: call path should only be reachable for names accepted by `fIsMachineAccount`.

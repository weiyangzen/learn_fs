# sources/distributed-fs/openafs/src/opr/proc.h

Purpose: public declaration for OPR process information utilities.

Important APIs/types/functions: declares `afs_int32 opr_procsize(void)`.

Control flow: no runtime logic.

State and persistence: no state.

Dependencies/integration: requires `afs_int32` typedef visible from includers. Installed as `opr/proc.h`.

Risks and test signals: low-risk declaration header; compile coverage verifies correct include context.

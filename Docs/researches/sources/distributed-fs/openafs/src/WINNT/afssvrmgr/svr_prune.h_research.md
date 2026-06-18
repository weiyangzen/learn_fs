# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_prune.h

Purpose: Declares server prune task packet and UI entry point.

Important APIs/types: `SVR_PRUNE_PARAMS` carries server identity and booleans for deleting `.BAK`, `.OLD`, and core files. `Server_Prune` opens the prune dialog with default options.

Control flow/state: The dialog fills the packet and starts `taskSVR_PRUNE`.

Dependencies/integration: Used by server maintenance menu commands.

Risks/test signals: Because defaults are true, command callers should be deliberate when invoking this destructive maintenance UI.

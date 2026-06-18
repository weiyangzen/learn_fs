# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_rename.h

Purpose: Defines the init/apply packets and exported entry points for fileset rename.

Important APIs/types: `SET_RENAME_INIT_PARAMS` carries requested identity and resolved RW identity. `SET_RENAME_APPLY_PARAMS` carries the RW fileset and destination name. `Filesets_ShowRename` starts the workflow; `Filesets_OnEndTask_ShowRename` is the task completion hook.

Control flow/state: The init task mutates `lpiRW`; the completion handler owns the transition into modal UI and apply task.

Dependencies/integration: Consumed by command/task dispatch code that routes `taskSET_RENAME_INIT` completions.

Risks/test signals: Validate packet ownership and deletion across success, cancel, and failure paths.

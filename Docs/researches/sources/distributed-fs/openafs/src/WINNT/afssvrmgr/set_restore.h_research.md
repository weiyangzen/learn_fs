# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_restore.h

Purpose: Declares the restore task packet and UI entry point.

Important APIs/types: `SET_RESTORE_PARAMS` contains target identity, fileset name, dump filename, and incremental flag. `Filesets_Restore(LPIDENT)` opens the restore workflow with an optional parent identity.

Control flow/state: The packet is owned by the modal dialog until OK; on OK it is passed to `taskSET_RESTORE`.

Dependencies/integration: Requires `LPIDENT`, path constants, and task handling from the server manager.

Risks/test signals: Ensure the task interprets `lpi` correctly as either aggregate target for create or fileset target for overwrite.

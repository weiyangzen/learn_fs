# sources/distributed-fs/lizardfs/src/master/filesystem_snapshot.h

Purpose: declares snapshot configuration loading and snapshot/clone entry points for the master filesystem.

Important APIs/types/functions: `fs_read_snapshot_config_file()` loads process-level snapshot batching; `fs_snapshot()` registers a snapshot task from source inode to destination parent/name with overwrite, missing-source, initial batch, callback, and job id parameters; `fs_clone_node()` clones a single node to a destination inode/name.

Control flow: callers use the header to enter the validated asynchronous snapshot path or lower-level clone path. The callback signature receives task status as an integer.

State and persistence behavior: no direct state in the header; implementations use metadata task state and changelogs.

Dependencies/integration: includes `filesystem.h` for node types and `fs_context.h` for authenticated operation context. Used by client request handlers and restore/task code.

Risks and test signals: the API exposes byte-sized booleans rather than strong types for overwrite and ignore-missing flags. Tests should verify flag interpretation and that clone callers pass already-validated contexts.

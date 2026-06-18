# sources/distributed-fs/lizardfs/src/common/exit_status.h

Purpose: centralizes process exit status constants.

Important APIs/types/functions: defines `LIZARDFS_EXIT_STATUS_SUCCESS`, `LIZARDFS_EXIT_STATUS_NOT_ALIVE`, `LIZARDFS_EXIT_STATUS_ERROR`, and `LIZARDFS_EXIT_STATUS_GENTLY_KILL`.

Control flow: no runtime flow; included by binaries/scripts that need consistent status codes.

State and persistence: none.

Dependencies and integration: includes `platform.h`. Used by daemon entry points and control tools.

Risks: macro constants are untyped and globally visible.

Test signals: no direct tests; correctness is convention/integration based.

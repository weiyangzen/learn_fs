# sources/distributed-fs/lizardfs/src/tools/get_trashtime.cc

Purpose: Implements `lizardfs gettrashtime` and deprecated recursive wrapper, reporting trash retention time for objects.

Important APIs/types/functions: `get_trashtime_run`; `rget_trashtime_run`; static `get_trashtime`; `CLTOMA_FUSE_GETTRASHTIME`; `MATOCL_FUSE_GETTRASHTIME`.

Control flow: Parses recursive and number-format flags, sends a legacy request with inode and mode, validates the response, prints one trashtime in normal mode, or sorts and prints recursive file/directory count buckets by trashtime.

State and persistence: Read-only. Uses global output formatting state.

Dependencies and integration: Uses `datapack`, `mfserr`, and shared master connection helpers. It complements `set_trashtime.cc`.

Risks and test signals: Manual length validation must match master protocol, including normal-mode length of 16 bytes after query id. No direct tests in this subset.

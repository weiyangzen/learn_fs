# File Research: sources/cow-pools/openzfs/module/zfs/zcp_synctask.c

## Summary
Implements ZCP `zfs.sync` and `zfs.check` submodules. It wraps selected DSL sync tasks so channel programs can dry-run or execute dataset mutations.

## Main Responsibilities
- Provides generic sync-task execution for ZCP callbacks.
- Exposes clone, destroy, promote, rollback, snapshot, rename snapshot, inherit property, bookmark, and set property operations.
- Runs checks in both dry-run and sync modes.
- Enforces sync-context requirements for actual mutation.
- Estimates per-call MOS space usage for channel-program space accounting.
- Returns error codes and optional error-detail nvlists to Lua.

## Key APIs
- `zcp_load_synctask_lib()`
- Internal wrapper: `zcp_synctask_wrapper()`
- Internal operations: `zcp_synctask_clone()`, `zcp_synctask_destroy()`, `zcp_synctask_promote()`, `zcp_synctask_rollback()`, `zcp_synctask_snapshot()`, `zcp_synctask_rename_snapshot()`, `zcp_synctask_inherit_prop()`, `zcp_synctask_bookmark()`, `zcp_synctask_set_prop()`

## Important Behavior
`zcp_sync_task()` first calls the DSL check function. In check mode it returns that result without syncing. In sync mode it requires the enclosing channel program to have been invoked with sync enabled, then calls the sync function when the check succeeds.

Operations that allocate temporary nvlists register ZCP cleanup handlers so Lua errors free them. Snapshot and clone record possible new zvol names in `zri_new_zvols` so minor nodes can be created later in open context.

## State and Synchronization
The module runs inside the transaction supplied by `zcp_eval()`. It uses `zri_space_used` plus static block-modified estimates to avoid exceeding unreserved pool space during a single program.

## Risks
Space use is an approximation based on average block shifts and triple-ditto MOS assumptions. Some operations return structured conflict details, so callers must handle a second return value. Actual `zfs.sync` calls in open-context programs are fatal Lua errors.

# File Research: sources/cow-pools/openzfs/module/zfs/zcp_set.c

## Summary
Implements channel-program support for setting user properties.

## Main Responsibilities
- Checks whether a requested property set is currently allowed.
- Restricts support to user properties.
- Applies local user-property values in syncing context.

## Key APIs
- `zcp_set_prop_check()`
- `zcp_set_prop_sync()`

## Important Behavior
`zcp_set_prop_check()` rejects non-user properties with `EINVAL`, builds a one-property nvlist, and delegates validation to `dsl_props_set_check()`.

`zcp_set_prop_sync()` obtains the current ZCP pool from `zcp_run_info()`, holds the dataset, constructs a local-source nvlist, calls `dsl_props_set_sync_impl()`, and releases the dataset.

## Risks
Only user properties are supported. `zcp_set_user_prop()` relies on `zcp_dataset_hold()` longjmp behavior for fatal dataset lookup errors, so callers must be prepared for Lua error unwinding.

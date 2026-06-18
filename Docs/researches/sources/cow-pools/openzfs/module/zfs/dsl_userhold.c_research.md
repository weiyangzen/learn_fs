# File Research: sources/cow-pools/openzfs/module/zfs/dsl_userhold.c

## Role

Implements user holds and releases for ZFS snapshots, including persistent holds, temporary holds tied to an onexit minor, hold listing, error-list reporting, and deferred snapshot destruction when the last hold is released.

## Hold Path

- `dsl_dataset_user_hold_check_one()` validates hold tag length, temporary tag length limits, and per-snapshot tag uniqueness.
- `dsl_dataset_user_hold_check()` requires userrefs support, detects duplicate snapshot/tag pairs, validates snapshot names and tags, records successful holds in `dduha_chkholds`, and records `ENOENT` in the caller error list without failing the whole batch.
- `dsl_dataset_user_hold_sync_one_impl()` creates the userrefs ZAP on first hold, increments `ds_userrefs`, stores the tag timestamp, records temporary holds in pool-level hold state, and logs history.
- `dsl_onexit_hold_cleanup()` registers cleanup callbacks for temporary holds.
- `dsl_dataset_user_hold()` wraps the batch in a sync task and returns success when at least the valid existing snapshots were held according to the lzc_hold semantics.

## Temporary Hold Cleanup

- `dsl_dataset_user_release_onexit()` reopens the pool by name, verifies the spa load guid still matches, and releases temporary holds when the owning process exits.
- Temporary hold cleanup groups tags by dataset object string so they can be released even after normal name-based lookup would be inconvenient.

## Release Path

- `dsl_dataset_user_release_impl()` handles normal name-based release and temporary object-id release.
- Kernel builds unmount snapshots before release because releasing holds may allow deferred destruction.
- `dsl_dataset_user_release_check_one()` verifies the target is a snapshot, checks each requested hold tag in the userrefs ZAP, records missing tags in the error list, and marks deferred-destroy snapshots for destruction if the released holds are the final references.
- `dsl_dataset_user_release_sync_one()` removes temporary pool holds, removes userrefs ZAP entries, decrements `ds_userrefs`, and logs history.
- `dsl_dataset_user_release_sync()` releases all checked holds and calls `dsl_destroy_snapshot_sync_impl()` for snapshots that became destroyable.
- `dsl_dataset_user_release()` releases persistent holds.
- `dsl_dataset_user_release_tmp()` releases temporary holds by dataset object id.

## Listing

`dsl_dataset_get_holds()` opens the pool and dataset, walks the dataset userrefs ZAP if present, and returns hold tag names mapped to stored timestamps.

## Error Handling

Missing snapshots or missing hold tags are recorded in caller-provided error nvlists where the API contract permits partial success. Non-`ENOENT` validation errors abort the batch before sync-side mutation.

## Research Notes

The file’s core invariant is that hold creation and release are staged through sync-task check lists. Sync functions operate only on previously validated entries, which keeps batch semantics atomic for non-missing-object errors while still reporting per-entry `ENOENT` details.

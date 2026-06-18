<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/pts/afs_ptsAdmin.h -->
# sources/distributed-fs/openafs/src/libadmin/pts/afs_ptsAdmin.h

## Purpose
Defines the public libadmin PTS administration interface. It names maximum PTS string/list sizes, exposes user and group access enums, declares user/group result and update structures, and prototypes all user, group, membership, ownership, and listing operations implemented by `afs_ptsAdmin.c`.

## Important APIs, Types, And Functions
The key constants are `PTS_MAX_NAME_LEN` and `PTS_MAX_GROUPS`, intentionally matching ptserver limits. `pts_UserEntry_t` and `pts_GroupEntry_t` carry IDs, owner/creator names, membership counts, quotas, and access settings. `pts_UserUpdateEntry_t` is gated by `PTS_USER_UPDATE_GROUP_CREATE_QUOTA` and `PTS_USER_UPDATE_PERMISSIONS`; `pts_GroupUpdateEntry_t` contains the five group permission fields. The API surface is the `pts_*` function family for create/get/modify/delete/rename/max-ID/list operations.

## Control Flow
Callers open an admin cell elsewhere, call the appropriate `pts_*` operation with that opaque handle, and inspect the boolean return plus optional `afs_status_t`. List APIs use the standard `Begin`/`Next`/`Done` pattern and pass an opaque iterator pointer between calls.

## State And Persistence
The header stores no state. Its structures describe snapshots or updates for persistent PTS database entries, while iterator IDs are opaque transient handles allocated by the implementation.

## Dependencies And Integration Points
The header includes `afs/param.h` and `afs/afs_Admin.h`, uses `ADMINAPI` linkage, and is consumed by libadmin callers and tests. The constants and enum semantics must remain aligned with `ptserver` and `afs_ptsAdmin.c` bit encoding.

## Risks And Test Signals
The main risks are ABI drift, enum value changes that break flag translation, and callers underallocating buffers for `Next` outputs. Compile coverage plus API tests for every declared function are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/pts/afs_ptsAdmin.h -->

# File Research: sources/cow-pools/openzfs/module/zfs/dsl_deleg.c

## Role

`dsl_deleg.c` implements ZFS delegated administration permissions stored in DSL directory ZAP objects. It handles granting, revoking, listing, checking, inheriting create-time permissions, and destroying delegation metadata.

## Permission Storage Model

Delegated permissions are stored through a two-level ZAP layout. The first-level ZAP maps a “who key” to a jump object. The jump object contains individual permissions or permission-set names.

Who-key classes encode target and scope, including:

- User, group, everyone.
- Local versus descendent permissions.
- Permission sets granted to users/groups/everyone.
- Create-time permissions and create-time permission sets.
- Named permission sets and nested named sets.

The comment at the top of the file documents key forms such as `ul$<id>`, `gd$<id>`, `El$`, `c-$`, and `s-$@<name>`.

## Major Responsibilities

- Validate whether a caller may delegate or undelegate permissions.
- Apply delegated permission changes in sync tasks.
- Retrieve all delegated permissions from a dataset up through ancestors.
- Evaluate access for a dataset, including local/descendent inheritance and named permission sets.
- Copy create-time delegated permissions from ancestors to newly created datasets.
- Destroy delegation ZAP objects during DSL directory destruction.
- Respect pool feature availability and global delegation enablement.

## Important Functions

- `dsl_deleg_can_allow()`: requires `allow` permission and verifies the caller also has each permission being delegated. It refuses delegation of `allow` itself.
- `dsl_deleg_can_unallow()`: requires `allow` and restricts undelegation to the caller’s own user entries.
- `dsl_deleg_set()`: public sync-task wrapper for grant/revoke operations.
- `dsl_deleg_set_sync()`: creates delegation ZAPs and jump objects as needed, then updates permissions.
- `dsl_deleg_unset_sync()`: removes permissions or whole who-key jump objects, destroying empty jump objects.
- `dsl_deleg_get()`: walks from the target DSL directory up to root and builds an nvlist of delegated permissions by source dataset.
- `dsl_deleg_access_impl()`: core access check for a held dataset and credential.
- `dsl_deleg_access()`: pool/dataset hold wrapper for permission checking by dataset name.
- `dsl_deleg_set_create_perms()`: copies ancestor create-time permissions into a new dataset for the creating UID.
- `dsl_deleg_destroy()`: destroys all jump objects and the base delegation ZAP.
- `dsl_delegation_on()`: checks SPA delegation enablement.

## Access Check Flow

`dsl_deleg_access_impl()` first rejects checks when delegation is disabled or the pool lacks delegated-permission support. It determines whether to start with local or descendent scope: snapshots are treated as descendent-only, while heads start local and then move to descendent as ancestors are traversed.

For each DSL directory from the dataset upward:

1. Non-global-zone callers are constrained by `zoned`/`zoned_uid` properties.
2. User, group, everyone, and supplemental group permission sets are loaded into an AVL tree.
3. Named sets are recursively expanded through nested set references.
4. The requested permission is checked against matching sets.
5. If sets do not grant it, direct user/group/everyone permissions are checked.

## Concurrency and Syncing

Permission mutations are performed through `dsl_sync_task()`. The check phase verifies the `SPA_VERSION_DELEGATED_PERMS` feature and that the target DSL directory exists. Sync functions mutate MOS ZAP objects and log pool history records.

Access checks require the DSL pool config to be held and use held dataset/directory structures for stable traversal.

## Interactions

- `dsl_dataset_create_sync()` calls `dsl_deleg_set_create_perms()` for new dataset creation.
- `dsl_dir_destroy_sync()` in destroy code calls `dsl_deleg_destroy()` when removing a DSL directory.
- `zfs_deleg_whokey()` from `zfs_deleg.h` centralizes who-key formatting.
- Credentials are inspected through `crgetuid`, `crgetgid`, `crgetngroups`, and `crgetgroups`.

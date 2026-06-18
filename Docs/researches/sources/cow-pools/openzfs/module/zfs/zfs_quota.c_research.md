# File Research: sources/cow-pools/openzfs/module/zfs/zfs_quota.c

## Summary
Implements ZPL user, group, and project quota helpers. It translates znode/SA bonus data into DMU ownership accounting, enumerates quota ZAP objects, reads or writes per-id quotas, and checks whether block or object usage exceeds explicit or default quotas.

## Main Responsibilities
- Extract file accounting identity from old `DMU_OT_ZNODE` bonuses or modern `DMU_OT_SA` bonuses.
- Map `zfs_userquota_prop_t` values to the backing DMU/ZAP objects.
- Enumerate many user/group/project usage or quota records with serialized ZAP cursors.
- Look up one user/group/project usage or quota value.
- Set per-user, per-group, or per-project block and object quotas.
- Enforce block and object quotas for writes, clones, rewrites, and object creation paths.

## Key APIs
- `zpl_get_file_info()`.
- `zfs_userspace_many()`, `zfs_userspace_one()`.
- `zfs_set_userquota()`.
- `zfs_id_overblockquota()`, `zfs_id_overobjquota()`, `zfs_id_overquota()`.

## Important Behavior
`zpl_get_file_info()` is the low-level DMU accounting parser. For legacy znodes it reads uid, gid, and generation from `znode_phys_t`; for SA bonuses it validates SA magic/header size, handles byte-swapped headers, reads fixed SA offsets for uid/gid/generation/flags, and uses `ZFS_DEFAULT_PROJID` unless the `ZFS_PROJID` flag is present.

Quota enumeration requires the relevant feature to be present: userspace accounting, user object accounting, or project quota accounting. Object-usage properties use the `DMU_OBJACCT_PREFIX` namespace and skip entries from the opposite quota type.

`zfs_set_userquota()` creates the quota ZAP object lazily, records it in the master node, handles FUID dirty state, removes entries for zero quotas, and updates entries for nonzero quotas.

The over-quota checks use explicit quota objects first and fall back to dataset default quota fields. They skip enforcement during ZIL replay and trigger quota accounting upgrades when the objset is upgradable but not yet present.

## Dependencies
Depends on DMU objset quota feature probes and upgrades, ZAP lookup/update/cursor APIs, FUID string conversion, project-id validation, and `zfsvfs_t` cached quota object/default fields.

## Risks
The SA parsing path assumes current fixed offsets for ZPL SA attributes, so it depends on the SA layout contract staying compatible. Enforcement intentionally returns false while replaying, so replay callers must only apply already-authorized log records. Default quota fallback means missing ZAP entries do not necessarily mean unlimited usage.

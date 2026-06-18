# File Research: sources/block-storage/lvm2/tools/lvchange.c

## Purpose
`lvchange.c` implements the many `lvchange` command variants. It changes LV properties, activation state, monitoring/polling, refresh state, persistent device numbers, RAID resync/rebuild/sync actions, cache/writecache settings, VDO settings, integrity settings, tags, profiles, activation-skip, autoactivation, compression, and deduplication.

## Metadata Commit Model
The file uses internal bits `MR_COMMIT` and `MR_RELOAD` so helpers can request either metadata commit only or metadata commit plus table reload. `_commit_reload()` applies the requested operation.

## Major Operation Groups
Property helpers handle permissions, pool discard/zero settings, allocation, error-when-full, read-ahead, persistent major/minor numbers, tags, profiles, activation-skip, autoactivation, compression, and deduplication.

Cache/VDO/integrity helpers update writecache settings, cache mode/policy, VDO parameters, and dm-integrity settings with type-specific validation and active-LV restrictions.

RAID helpers implement resync, rebuild, writemostly/writebehind, recovery rates, and sync actions. Resync can deactivate active LVs, detach and wipe metadata/log devices, reattach them, commit metadata, reactivate, and back up.

Activation helpers handle foreign VG restrictions, activation-skip policy, snapshot-origin behavior, autoactivation filters, no-autoactivate flags, background polling, component LV activation prompts, and deactivation-friendly processing of component LVs.

## Command Entry Points
Exported handlers include `lvchange_properties_cmd()`, `lvchange_activate_cmd()`, `lvchange_refresh_cmd()`, `lvchange_resync_cmd()`, `lvchange_syncaction_cmd()`, `lvchange_rebuild_cmd()`, `lvchange_monitor_poll_cmd()`, `lvchange_persistent_cmd()`, and fallback `lvchange()` for missing command-definition function mappings.

## Integration Notes
Most command entry points call `process_each_lv()` with a check callback and a single-LV callback. They set command context flags for lockd, missing PV handling, activation mode, device-name mismatch tolerance, component LV processing, and foreign VG inclusion.

## Risks
The file has a large state space involving LV visibility, component LV exceptions, lockd state, active/inactive state, segment type, metadata commit grouping, and backward-compatible mixed activation/property behavior. New options must be classified correctly as group-commit or direct-commit operations.

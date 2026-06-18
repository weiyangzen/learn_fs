# Research: sources/distributed-fs/eos/mgm/ofs/cmds/FsConfigListener.inc

## Purpose

`FsConfigListener.inc` implements MGM background listeners for global configuration changes and filesystem status/geotag changes. It applies remote-master configuration on slaves, updates filesystem view structures when geotags change, and initiates drain status transitions when a master observes filesystem operational errors.

## Important APIs, Types, and Functions

- `processIncomingMgmConfigurationChange(key)` reads a global config value and either enforces access/iostat config or applies namespaced map/fs/quota/vid/policy config through the config engine and FsView.
- `ProcessGeotagChange(queue)` compares a filesystem's previous geotag in tree views with the new stat geotag and updates node/group/space `GeoTree` memberships.
- `FileSystemMonitorThread(ThreadAssistant&)` subscribes to `stat.errc`, `stat.geotag`, `configstatus`, and `stat.boot`, updates scheduler disk statuses, and marks disks drain on master-side ops errors.
- `FsConfigListener(ThreadAssistant&)` consumes global config change events from `MgmConfigQueue`; slaves apply modifications and deletions.

## Control Flow

Configuration changes without explicit namespaces are treated as access or iostat configuration and applied globally. Namespaced changes are set in `mConfigEngine`; `fs:` changes additionally take a write lock and reapply filesystem config after unregistering first, `quota:` changes are deferred to master reload, and other namespaced keys call `ApplyEachConfig`.

Geotag processing reads the filesystem under `FsView::ViewMutex`, gets fsid and new geotag, compares with the current tree membership, then upgrades to write locking and erases/reinserts the fsid in node, group, and space geo trees when changed.

The filesystem monitor registers interest filters, then processes events until termination. On master nodes, non-geotag events read fs id/status/error/space, update scheduler statuses, and if an operational error is present with suitable config/boot state, mark the filesystem drain and update scheduler state. The global config listener only applies events on slaves.

## State and Persistence Behavior

This file mutates in-memory and configured MGM state: config-engine values, FsView filesystem configuration, geo tree memberships, filesystem config status, scheduler disk status, and deletion of config keys. It intentionally skips quota updates on slaves because they could disturb namespace state and should reload on master transition.

## Dependencies and Integration Points

Dependencies include `FsView`, `FileSystem`, `FsNode`, `FsGroup`, `FsSpace`, `GeoTree`, config engine, access config, IO stats, messaging realm listeners, global config listener, filesystem scheduler, master/slave state, and `ThreadAssistant`. It is an integration layer between QDB/MQ events and the MGM's runtime scheduling/configuration views.

## Risks and Edge Cases

- Lock upgrade in geotag handling releases read lock before acquiring write lock; filesystem data can change between snapshot and update.
- Slave fs config applies unregister-first behavior to avoid stale state, but incorrect ordering can briefly remove fs entries from views.
- Quota changes are skipped on slaves; tests must ensure eventual master reload covers them.
- Drain triggering depends on combined `errc`, config status, and boot status; wrong enum parsing can over-drain or under-drain disks.
- Scheduler update failures are logged but do not roll back FsView state.

## Test Signals

Tests should cover access/iostat config changes, map/fs/vid/policy key application, config deletion, slave-only global application, quota skip, geotag no-op and changed updates across node/group/space trees, filesystem missing/initial-state skips, scheduler disk status updates, ops-error drain transition, and thread termination.

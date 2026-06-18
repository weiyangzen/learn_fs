# sources/distributed-fs/lizardfs/src/master/filesystem.cc

## Purpose
`filesystem.cc` owns the lifecycle of the master filesystem metadata subsystem. It defines the global `FilesystemMetadata *gMetadata`, master-only configuration flags, goal definitions, metadata dumper, and checksum background updater, then wires metadata load, lock handling, periodic dumping, event-loop callbacks, master promotion, reload, unload, and termination behavior. The same file also has the `METARESTORE` personality path for opening, dumping, and closing metadata from recovery tools.

## Important APIs and control flow
Public lifecycle functions include `fs_init`, `fs_loadall`, `fs_unload`, `fs_term`, `fs_unlock`, `fs_reload`, `fs_become_master`, `fs_storeall` for metarestore, and `fs_disable_metadata_dump_on_exit`. `fs_init(bool doLoad)` reads config, opens the metadata lockfile, initializes changelog handling, loads metadata for master or requested shadow startup, registers reload/promotion/timer/poll/destructor callbacks, and starts master-specific periodic loops when the process is master. `fs_loadall()` allocates metadata, initializes chunk state, migrates old changelogs, rejects dirty `metadata.mfs.tmp`, loads `metadata.mfs`, and optionally applies changelogs for auto-recovery or shadow mode. `metadataPollServe()` commits or rolls back asynchronous metadata dumps and broadcasts the result to clients.

## State and persistence
Global state includes `gMetadata`, `gStoredPreviousBackMetaCopies`, `gDisableChecksumVerification`, `gChecksumBackgroundUpdater`, and master-only `gGoalDefinitions`, `metadataDumper`, `gAtimeDisabled`, `gMagicAutoFileRepair`, and operation delay timers. Persistence is managed through metadata lockfiles, changelogs, foreground dumps on shutdown, periodic background dumps, and optional metarestore-assisted dumping. A clean shutdown removes the lockfile only after a successful metadata store. A quick stop writes a `quick_stop` lockfile message so later startup knows changelogs are required; a no-metadata stop writes `no_metadata`.

## Dependencies and integration points
This file coordinates `cfg`, `event_loop`, `Lockfile`, `changelog`, `chunks`, `datacachemgr`, `goal_config_loader`, `filesystem_store`, `filesystem_periodic`, `filesystem_snapshot`, `MetadataDumper`, `restore`, client sessions, metaloggers, and metadataserver personality promotion. Goal config loading prefers a configured file, then `/etc` default, then default built-in goals.

## Risks and test signals
The highest-risk behavior is startup and shutdown ordering: dirty temp metadata files, stale lockfile handling, and the distinction between master, shadow, and metarestore personalities decide whether metadata is trusted or changelogs are replayed. Background dump failure can trigger checksum recalculation only when the dumper used metarestore. Useful tests are clean shutdown/removal of lockfiles, quick stop lockfile messages, auto-recovery from changelogs, shadow-to-master promotion with loaded metadata, malformed goal config rejection, disabled checksum verification, and failed background dump result broadcasts.

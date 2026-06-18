# sources/distributed-fs/ceph/src/mds/Migrator.cc

## Purpose

`Migrator.cc` implements Ceph MDS subtree and capability migration. It coordinates exporting authority and cached metadata from one MDS rank to another, importing that data on the destination, notifying bystander ranks of authority changes, handling failure/reversal, and moving client capabilities.

## Important APIs, Types, and Functions

- `export_state_t` tracks exporter state, peer, transaction id, waiting bystanders, imported cap acknowledgements, mutation locks, approximate export size, freeze diagnostics, and parent split-export coordination.
- `import_state_t` tracks importer state, peer, transaction id, bystanders, bounds, updated scatterlocks, forced sessions, peer cap exports, and mutation locks.
- `dispatch()` routes all migration message types: discover/prep/export/finish/cancel, notify/notifyack, cap export/ack, and gather caps.
- Export entry points are `export_dir()`, `export_dir_nicely()`, `maybe_do_queued_export()`, `dispatch_export_dir()`, `export_frozen()`, `export_go()`, `export_go_synced()`, and `export_finish()`.
- Import entry points are `handle_export_discover()`, `handle_export_prep()`, `handle_export_dir()`, `import_logged_start()`, `handle_export_finish()`, and `import_finish()`.
- Reversal and failure paths include `export_try_cancel()`, `export_reverse()`, `import_reverse()`, `import_reverse_unfreeze()`, and `handle_mds_failure_or_stop()`.
- Serialization helpers include `encode_export_prep_trace()`, `decode_export_prep_trace()`, `encode_export_inode()`, `encode_export_dir()`, `decode_import_inode()`, and `decode_import_dir()`.
- Capability-only migration is handled by `export_caps()`, `handle_export_caps()`, `logged_import_caps()`, `handle_export_caps_ack()`, and `handle_gather_caps()`.

## Control Flow

An export starts only if the source dir is auth, active, exportable, not frozen, not quiesced, not system/root-ineligible, and the destination rank is active. The exporter auth-pins and marks the dir exporting, starts an internal `CEPH_MDS_OP_EXPORTDIR` request, then acquires locks. Large subtrees can be split by `maybe_split_export()` into child exports governed by a shared parent record.

For a whole-subtree export, the exporter sends `MExportDirDiscover`, freezes the tree, receives discover ack, releases request locks, then waits for the freeze. Once frozen, it grabs required locks, encodes export bounds/traces in `MExportDirPrep`, flushes affected client sessions, waits for prep ack and bystander warnings, syncs the log, adjusts subtree auth to ambiguous, subtracts balancer popularity, encodes the full subtree into `MExportDir`, and sends it to the importer.

The importer creates `IMPORT_DISCOVERING` state, discovers/pins the root inode, decodes the prep root and traces, opens and pins bounds, adjusts bounded subtree auth to ambiguous, freezes the import region, and acks prep. On actual export data it logs `EImportStart`, force-opens sessions, decodes dirs/dentries/inodes/caps into cache, records peer cap exports, and then sends `MExportDirAck` with imported cap ids after `import_logged_start()`.

After exporter receives ack it logs `EExport`, notifies bystanders, sends final finish to importer, locally transitions exported objects to replica state, clears bounds, unfreezes, drops locks/pins, and trims cache. Importer finalizes caps, logs `EImportFinish(true)`, processes delayed expires, unfreezes, evaluates imported caps, and may re-export empty imports.

## State and Persistence Behavior

Migration state is held in `export_state` and `import_state`. Persistent recovery points are journal entries: `EExport`, `EImportStart`, `EImportFinish`, and `ESessions`. The code carefully orders auth changes, journaling, and finish messages so recovery can disambiguate ambiguous imports and exports. Runtime pins include auth pins, `PIN_EXPORTBOUND`, `PIN_IMPORTING`, `PIN_IMPORTBOUND`, `PIN_IMPORTINGCAPS`, and `PIN_EXPORTINGCAPS`.

## Dependencies and Integration Points

The file integrates with `MDSRank`, `MDCache`, `CDir`, `CInode`, `CDentry`, `Locker`, `Server`, `MDBalancer`, `MDLog`, `MDSMap`, `Mutation`, capability classes, migration message classes, and journal event classes. It also uses config options such as `mds_max_export_size`, `mds_inject_migrator_session_race`, and `mds_kill_export_at`/`mds_kill_import_at` failure-injection gates.

## Risks

- This is a distributed state machine with many legal intermediate states; missing one cleanup path can leave frozen trees, stale auth, or leaked pins.
- Lock ordering is critical around frozen trees, quiesce, scatter locks, and remote auth pins.
- Export splitting depends on size estimates and parent restart bookkeeping.
- Failure handling must distinguish failed peer, failed bystander, and local recovery states.
- Wire encoding is versioned in many nested buffers; incompatible decode changes can break migration.
- Forced session open/close and cap handoff must remain journaled and ordered with client notifications.

## Test Signals

High-value tests include successful export/import, export cancellation at every state, importer cancellation at every state, destination failure before ack, bystander failure during warning/notify, split export retry, stale freeze detection, cap-only export, ambiguous import recovery, forced-session race injection, and all `mds_kill_export_at`/`mds_kill_import_at` gates. Assertions in `audit()` and `dump_export_states()` provide useful invariant probes.

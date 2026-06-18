# sources/distributed-fs/coda/coda-src/scripts/partial-reinit.sh

Purpose: generates a recovery script to recreate existing volumes after a partial server reinitialization and lists volumes that will not be recreated.

Control flow: prompts if `/tmp/reinit_script` already exists, removes old generated files, emits a shell script header, scans `/vice/vol/VolumeList` excluding partition, backup, and restored entries, maps each volume id to a replicated id in `/vice/db/VRList`, appends `volutil create_rep <part> <name> <repid> <volid>` lines to a temp script, builds `/tmp/not_created` for volumes absent from the generated script, warns if nonempty, then moves the temp script to `/tmp/reinit_script` and marks it executable.

State/persistence: writes `/tmp/reinit_script*` and `/tmp/not_created`; reads `/vice/vol/VolumeList` and `/vice/db/VRList`. It does not execute volume recreation.

Dependencies, risks, tests: depends on exact field positions and shell prompt behavior. Risks include predictable `/tmp` paths, grep substring false positives when mapping ids, no locking, and accidental overwrite after confirmation. Test generated commands from sample VolumeList/VRList, volumes without repid warnings, exclusion of backups/restored volumes, and pre-existing script prompt.

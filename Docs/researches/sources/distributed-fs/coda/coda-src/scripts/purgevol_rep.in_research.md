# sources/distributed-fs/coda/coda-src/scripts/purgevol_rep.in

Purpose: dry-run or destructive purge of a replicated volume and its replicas from Coda servers and SCM metadata.

Control flow: loads `server.conf`, requires SCM host, parses `--kill` to enable destructive mode, queries `getvolinfo` for replica/server mapping, loops replicas, obtains each server's volume list, finds volume ids with matching replica ids, and either prints or executes `volutil purge`. In kill mode it removes the replicated volume id from `dumplist`, removes the volume row from `VRList`, rebuilds VRDB with `volutil makevrdb`, and rebuilds VLDB with `bldvldb.sh`.

State/persistence: destructive mode deletes server volumes and edits `$vicedir/db/dumplist`, `VRList`, VRDB, and VLDB. Dry-run mode is read-only.

Dependencies, risks, tests: depends on `getvolinfo` output format, `volutil`, `bldvldb.sh`, and SCM config. Risks include a likely bug using `$SCM` uppercase when only `scm` is set, unanchored `grep "$REPVOLNAME"`, parsing human-readable `getvolinfo`, and no rollback after partial purge. Test dry-run output, `--kill` with controlled fixtures, uppercase `$SCM` failure, volume names that are regex prefixes, and multi-replica metadata cleanup.

# sources/distributed-fs/coda/coda-src/scripts/coda-server-logrotate

Purpose: simple Coda server log rotation utility.

Control flow: loads `server.conf` through `codaconfedit`, defaults `vicedir` to `/vice`, defines `rotate` to shift suffixes `-9` through `-0` up one generation and move the active file to `-0`, rotates `$vicedir/srv/SrvLog`, `$vicedir/srv/SrvErr`, and `$vicedir/auth2/AuthLog`, then sends `SIGHUP` to codasrv/auth2 pids if pid files exist.

State/persistence: renames log files in server/auth directories and signals daemons to reopen logs. It does not compress, remove old `-10` files, or use locks.

Dependencies, risks, tests: depends on `codaconfedit`, pid files, `seq`, and daemons handling `SIGHUP`. Risks include `seq` portability, race with active log writers, stale pid-file signaling, and unbounded suffixes beyond `-10` if repeated external manipulation occurs. Test with missing logs, full suffix chain, stale pid files, and daemon reopen behavior after rotation.

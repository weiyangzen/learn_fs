# sources/distributed-fs/coda/coda-src/scripts/startserver.in

Purpose: wrapper to rotate logs and start the Coda file server (`codasrv`) with configured RVM flags.

Control flow: ignores `SIGHUP`, loads `server.conf` when available, defaults `vicedir`, runs `coda-server-logrotate`, removes `$vicedir/srv/CRASH`, sets `-zombify` if `$vicedir/srv/ZOMBIFY` exists, derives `RVMFLAGS` from old `$vicedir/srv.conf` only when modern `server.conf` is absent, then exec-style invokes `codasrv` with passed arguments, zombify flag, and RVM flags.

State/persistence: rotates logs, removes crash marker, reads config and optional zombify marker. The daemon itself handles persistent volume/RVM state.

Dependencies, risks, tests: depends on generated `@sbindir@` paths, `coda-server-logrotate`, `codasrv`, and old/new config conventions. Risks include no explicit `exec`, word splitting in `$RVMFLAGS`, possible missing logrotate failure handling, and treating any `ZOMBIFY` file as active flag. Test with server.conf present/absent, old srv.conf `-rvm` line, marker files, forwarded args, and logrotation failure.

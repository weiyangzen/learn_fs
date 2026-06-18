## sources/distributed-fs/openafs/src/kauth/test/test_kaserver

Purpose: `test_kaserver` is a csh integration script that starts a temporary kaserver, seeds a test database, exercises authentication and password/key operations, and tears the server down.

Important control flow: it prepares `/tmp/db`, launches `kaserver` with `-noauth` through `background`, aliases `kasu` to run `kas` against the local host, creates/admin-enables users and the `afs` service, sets the AuthServer.Admin password, stops the noauth server, restarts with `-fastkeys`, generates a temporary script that runs `tokens` and `klog`, calls `test_badtix`, then performs additional create/password/delete/setkey/setfields/list operations before killing the server.

State and persistence: creates and deletes files in `/tmp/db`, `/tmp/pid`, and `/tmp/foo`; starts/stops background kaserver processes; writes a temporary KA database. It depends on `$user` from the shell environment.

Dependencies and integration points: requires csh, built `background`, `kaserver`, `kas`, `klog`, `kpasswd`, `test_badtix`, `/usr/vice/etc` cellservdb, and historically `/usr/andy/bin/tokens`.

Risks: hard-coded `/tmp` paths and external tool paths make this fragile. It kills PIDs from `/tmp/pid`, so stale files are dangerous. It assumes local hostname service setup and a mutable temp database. Not portable to systems without csh or those historical paths.

Test signals: success is the script completing under `-e`; failures abort. It is included by `runtest` after `test_interim_ktc`.

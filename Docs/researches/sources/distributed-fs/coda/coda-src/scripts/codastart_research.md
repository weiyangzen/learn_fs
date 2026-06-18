# sources/distributed-fs/coda/coda-src/scripts/codastart

Purpose: minimal server startup wrapper for a configured Coda server.

Control flow: compares `/vice/hostname` with `/vice/db/scm`. On the SCM it starts `updatesrv` and `auth2`; on non-SCM servers it starts `auth2 -chk`. It then starts `updateclnt -h <scm>` and finally `startserver`.

State/persistence: directly launches daemon processes in the background except for `startserver`, which runs in the foreground of the script unless that script detaches internally. It reads fixed `/vice` files and does not consult `server.conf`.

Dependencies, risks, tests: depends on absolute `/vice` layout, `updatesrv`, `auth2`, `updateclnt`, and `startserver` in `PATH`. Risks include no error checking, no pid management, duplicate daemon starts, and fixed config path ignoring alternate `vicedir`. Test SCM/non-SCM branches, missing files, PATH setup, and repeated invocation behavior.

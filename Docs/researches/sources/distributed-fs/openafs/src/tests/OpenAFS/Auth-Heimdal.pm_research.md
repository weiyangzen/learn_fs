# sources/distributed-fs/openafs/src/tests/OpenAFS/Auth-Heimdal.pm

## Purpose
`Auth-Heimdal.pm` is a small legacy Perl authentication helper for Heimdal-style test cells. It reads the local cell, derives an uppercase realm, and provides admin/user authentication commands.

## Important APIs, types, and functions
The package is `OpenAFS::Auth`. It defines `getcell`, `getrealm`, `authadmin`, and `authuser`.

## Control flow
`getcell` opens `$openafsdirpath->{'afsconfdir'}/ThisCell`, reads and chomps the cell name, and returns it. `getrealm` repeats the read and uppercases the cell name. `authadmin` and `authuser` build `kinit -k -t /usr/afs/etc/krb5.keytab <principal>@REALM ; afslog` command strings and execute them with `system`.

## State and persistence behavior
It reads `ThisCell`, reads a fixed keytab path, obtains Kerberos credentials, and obtains AFS tokens through `afslog`. It does not persist module-local state.

## Dependencies and integration points
It depends on `OpenAFS::Dirpath`, Heimdal `kinit`, `afslog`, a keytab at `/usr/afs/etc/krb5.keytab`, and the test harness expecting an `OpenAFS::Auth` package.

## Risks
Commands are executed through the shell without return-code checks. Realm derivation by uppercasing the cell is simplistic. The keytab path is hard-coded and the module name collides with other `OpenAFS::Auth` implementations.

## Test signals
Verify `ThisCell` missing/readable cases, uppercase realm derivation, successful admin/user keytab login, and failure propagation expectations in the harness.

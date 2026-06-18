# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/core-site.xml

## Purpose
This test `core-site.xml` provides baseline Hadoop common configuration for unit and integration tests. It supplies temporary-directory defaults, FTP localhost credentials, simple authentication, and fixed NFS test ports.

## Important Properties
The file sets `hadoop.tmp.dir=build/test`, `fs.ftp.user.localhost=user`, `fs.ftp.password.localhost=password`, `hadoop.security.authentication=simple`, `nfs3.server.port=2079`, and `nfs3.mountd.port=4272`.

## Control Flow
There is no executable logic. Hadoop test code loads it through `Configuration`, and downstream components branch on authentication mode, temporary path, FTP credential lookup, or NFS port allocation.

## State And Persistence
The XML itself is static. It causes runtime state under `build/test` and may bind local ports 2079 and 4272 in NFS-related tests.

## Dependencies And Integration Points
It integrates with Hadoop Common tests, FTP filesystem tests, and NFS gateway tests. The FTP credentials line up with localhost-specific FTP contract tests and avoid prompting or relying on production credential stores.

## Risks
Hard-coded ports can collide with local services or parallel test runs. The placeholder FTP password is test-only but should not leak into production config. Changing `hadoop.security.authentication` from `simple` would alter many test assumptions.

## Test Signals
Signals include configuration-loading tests, FTP contract tests that resolve localhost credentials, NFS tests that bind the configured ports, and security tests expecting simple auth unless they override it.

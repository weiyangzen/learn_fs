# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/contract/ftp.xml

## Purpose
`ftp.xml` is a Hadoop filesystem contract-test configuration for FTP-backed filesystems, especially remote Unix FTP targets. It declares which filesystem behaviors the generic contract test suite should expect or skip.

## Important Properties
The fixture disables root tests with `fs.contract.test.root-tests-enabled=false`, marks FTP as case-sensitive, and declares no append, no block locality, no concat, no seek support, no Unix permission support, strict exceptions enabled, and seek-past-EOF rejected. It marks atomic directory delete and atomic rename as supported.

## Control Flow
There is no executable control flow. Hadoop `Configuration` and contract test code load the XML and branch test expectations from the `fs.contract.*` keys. A false capability suppresses or alters tests that would otherwise assume HDFS-like semantics.

## State And Persistence
The file is a static test resource. It persists only declarative capability values and does not create runtime state. Its values can influence tests that reach an external FTP server configured elsewhere.

## Dependencies And Integration Points
It integrates with Hadoop's filesystem contract test framework and FTP filesystem implementation. Credentials and host-specific settings come from other configuration, notably the test `core-site.xml` entries for localhost FTP user/password.

## Risks
The risk is capability drift: if FTP behavior changes but this fixture is not updated, the contract suite may either hide real regressions or assert invalid semantics. Enabling root tests or seek incorrectly could make tests destructive or flaky against external servers.

## Test Signals
Contract test outcomes for FTP are the main signal. Failures around rename atomicity, EOF seeking, strict exception type expectations, and permissions indicate mismatch between fixture claims and actual FTP filesystem behavior.

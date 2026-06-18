<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/TestDtFetcher.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/TestDtFetcher.java

## Purpose
Implements a test `DtFetcher` service provider used by `TestDtUtilShell` to simulate delegation-token acquisition without contacting an external service.

## Important APIs, Types, And Functions
Implements `DtFetcher.getServiceName`, `isTokenRequired`, and `addDelegationTokens`. It reuses `TestDtUtilShell.SERVICE_GET` and `TestDtUtilShell.MOCK_TOKEN`.

## Control Flow
When the shell asks for a token matching the service, `addDelegationTokens` inserts the predefined mock token into the supplied `Credentials` and returns it. `isTokenRequired` always returns true.

## State And Persistence
No local state is stored. The only mutation is adding a token to the caller-provided `Credentials` object.

## Dependencies And Integration Points
Depends on Hadoop `Configuration`, `Credentials`, `Token`, `Text`, and the `DtFetcher` plugin contract. It integrates with shell discovery of token fetchers for `dtutil get`.

## Risks
Because it shares static test constants with `TestDtUtilShell`, changes to those constants alter fetcher behavior. It does not validate URL or renewer input, so it is only a deterministic test double.

## Test Signals
`TestDtUtilShell` observes tokens of kind `testTokenKindGet` and service `testTokenServiceGet` in output files after `get` operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/TestDtFetcher.java -->

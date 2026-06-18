<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/TestDtUtilShell.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/TestDtUtilShell.java

## Purpose
Tests `DtUtilShell` command behavior for printing, editing, appending, removing, fetching, formatting, and importing Hadoop delegation-token files.

## Important APIs, Types, And Functions
Targets `DtUtilShell.run`, `Credentials.writeTokenStorageFile`, `Credentials.readTokenStorageStream`, `Token.encodeToUrlString`, and the test fetcher path. Helper `makeTokenFile` writes either protobuf or legacy writable credential files.

## Control Flow
Each test creates local credential files in setup, runs shell commands with argument arrays, and inspects captured output or resulting files. `print` covers all tokens, legacy files, and alias filtering. `edit`, `append`, and `remove` mutate files then print to verify results. `get` uses `TestDtFetcher`, with optional `-service`, `-alias`, and `-format` flags. `import` decodes a URL token string into a credentials file and optionally rewrites the service alias.

## State And Persistence
The test writes token-storage files under a temporary local filesystem directory and deletes the whole directory after each test. It captures shell output in a `ByteArrayOutputStream`.

## Dependencies And Integration Points
Depends on Hadoop `Credentials`, local `FileSystem`, token serialization formats, Mockito spies, and the `DtFetcher` test provider. It validates the command-line token utility's file and provider integration.

## Risks
Output checks use substring matching, so formatting regressions can slip through if key substrings remain. Static local filesystem setup happens at class load and can fail early. The test depends on provider discovery for the test `DtFetcher`.

## Test Signals
Signals are zero shell return codes, output containing or excluding expected token kind/service/alias strings, Mockito verification of writable vs protobuf read paths, and imported base64 URL strings appearing in printed credentials.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/TestDtUtilShell.java -->

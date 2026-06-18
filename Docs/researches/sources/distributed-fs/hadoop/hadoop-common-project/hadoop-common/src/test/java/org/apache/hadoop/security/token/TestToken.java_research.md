<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/TestToken.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/TestToken.java

## Purpose
Tests core `Token` serialization, URL-safe encoding/decoding, argument validation, identifier decoding, and empty-token equality.

## Important APIs, Types, And Functions
Targets `Token.write`, `readFields`, `encodeToUrlString`, `decodeFromUrlString`, `decodeIdentifier`, equality, and constructors. Helpers `checkEqual`, `isEqual`, and `checkUrlSafe` validate field equivalence and URL-safe character sets.

## Control Flow
Serialization writes a token to `DataOutputBuffer` and reads it back. Encoding loops over representative strings, creates tokens using the same bytes/text values, encodes and decodes them, and checks equality plus URL-safe characters. Decode sanity intercepts null input. Identifier decoding creates a delegation token through `TestDelegationTokenSecretManager` and confirms a distinct but equal identifier object is reconstructed.

## State And Persistence
State is in-memory buffers and a started delegation-token secret manager for one test. No files are written.

## Dependencies And Integration Points
Depends on Hadoop IO buffers, `Text`, `HadoopIllegalArgumentException`, delegation token test classes, and `LambdaTestUtils.intercept`. It validates token serialization contracts consumed by credential files, HTTP delegation auth, and secret managers.

## Risks
The secret manager started in `testDecodeIdentifier` is not stopped in the visible test body, so thread cleanup depends on broader test behavior or short-lived intervals. Encoding tests use platform default charset via `String.getBytes()`.

## Test Signals
Signals are round-trip equality, URL-safe encoded strings, null decode rejection, distinct/equal decoded identifiers, and equality of default, zero-length, and null-field empty tokens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/TestToken.java -->

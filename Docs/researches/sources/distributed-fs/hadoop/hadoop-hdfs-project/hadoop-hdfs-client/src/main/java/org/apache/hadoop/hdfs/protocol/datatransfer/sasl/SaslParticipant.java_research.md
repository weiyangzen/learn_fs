# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/SaslParticipant.java

## Purpose
`SaslParticipant` abstracts over `SaslClient` and `SaslServer`, which have similar operations but no shared interface. It provides a single helper used by HDFS data transfer SASL client/server negotiation code.

## Important APIs, Types, and Functions
Static factory methods create server or client participants using `FastSaslServerFactory` or `FastSaslClientFactory`, mechanism from `SaslMechanismFactory`, protocol `hdfs`, and server name `0`. Factories are lazily initialized static fields.

`createFirstMessage` is client-only and returns the initial response or an empty byte array. `evaluateChallengeOrResponse` delegates to client `evaluateChallenge` or server `evaluateResponse`. `getNegotiatedQop`, `isNegotiatedQopPrivacy`, `wrap`, `unwrap`, and `isComplete` delegate to the active SASL object. `createStreamPair` wraps streams in Hadoop `SaslInputStream` and `SaslOutputStream`. `toString` identifies `SaslServer` or `SaslClient`.

## Control Flow
Each instance wraps exactly one of `SaslClient` or `SaslServer`; the other field is null. Methods branch on which side is active.

## State and Persistence Behavior
SASL negotiation state lives inside the wrapped `SaslClient` or `SaslServer`. Static factories are cached process-wide. There is no persistence.

## Dependencies and Integration Points
It depends on Java SASL APIs, Hadoop fast SASL factories, `SaslMechanismFactory`, Hadoop SASL streams, and `IOStreamPair`. It is used by `SaslDataTransferClient` and corresponding server-side SASL utilities.

## Risks and Edge Cases
Static factory initialization is not synchronized, though duplicate initialization is likely harmless. `Objects.requireNonNull` fails if a requested mechanism cannot create a client/server. `createFirstMessage` throws for server instances. Correct QOP privacy detection depends on negotiated property strings.

## Test Signals
SASL data transfer tests cover this indirectly. Focused tests with mock callback handlers should cover client/server creation, initial response handling, QOP reporting, wrap/unwrap after completion, and stream pair creation.

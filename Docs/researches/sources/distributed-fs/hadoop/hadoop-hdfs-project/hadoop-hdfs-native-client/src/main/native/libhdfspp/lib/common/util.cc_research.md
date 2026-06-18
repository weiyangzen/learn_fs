<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/util.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/util.cc

## Purpose
Implements common utility functions for status conversion, protobuf framing, random client naming, base64 encoding, safe socket shutdown, high-bit tests, and C protobuf shutdown.

## Important APIs, Types, And Functions
Functions include `ToStatus`, `ReadDelimitedPBMessage`, `SerializeDelimitedProtobufMessage`, `DelimitedPBMessageSize`, `GetRandomClientName`, `Base64Encode`, `SafeDisconnect`, `IsHighBitSet`, and `ShutdownProtobufLibrary_C`.

## Control Flow
Boost errors become OK or status with error value/message. Protobuf helpers read/write Java-compatible varint-delimited messages. Random client names combine process id, thread id, and OpenSSL random bytes. `SafeDisconnect` tries socket shutdown and close separately and returns a first error string instead of throwing.

## State And Persistence
No persistent state is kept. Random output depends on OpenSSL RNG. Protobuf library shutdown affects process-global protobuf state.

## Dependencies And Integration Points
Used by continuations, RPC, block reader, DataNode connection, C utility API, and client identity creation.

## Risks
`ReadDelimitedPBMessage` ignores the return value of `ReadVarint32` and can parse invalid streams poorly. Base64 is custom code and should be tested against standard vectors. `GetRandomClientName` returns null on RNG failure and callers must handle that path. `ShutdownProtobufLibrary_C` is process-global and unsafe if called while protobuf is still in use.

## Test Signals
Tests should cover protobuf round trips and malformed input, Boost error conversion, random-name uniqueness/failure handling, base64 vectors, socket close error strings, high-bit checks, and C protobuf shutdown placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/util.cc -->

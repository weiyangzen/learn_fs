# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/SaslResponseWithNegotiatedCipherOption.java

## Purpose
`SaslResponseWithNegotiatedCipherOption` is a small package-private response container for a SASL payload plus the cipher option negotiated by the server.

## Important APIs, Types, and Functions
The constructor stores a `byte[] payload` and a `CipherOption cipherOption`. Fields are final and package-visible.

## Control Flow
`DataTransferSaslUtil.readSaslMessageAndNegotiatedCipherOption` creates this object after parsing a server response. `SaslDataTransferClient.doSaslHandshake` evaluates the payload and unwraps/uses the cipher option if privacy was negotiated.

## State and Persistence Behavior
It is immutable by reference, though the payload byte array is mutable by callers. There is no persistence.

## Dependencies and Integration Points
It depends on Hadoop crypto `CipherOption` and the SASL utility/client classes in the same package.

## Risks and Edge Cases
Null cipher option is valid and means no separate crypto stream suite was negotiated; callers then fall back to SASL streams. Payload may be empty or null depending on protobuf response content.

## Test Signals
Encrypted transfer tests should assert negotiated and non-negotiated cipher option paths.

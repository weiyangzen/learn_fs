# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/InvalidMagicNumberException.java

Purpose: Signals that a SASL data-transfer negotiation did not begin with the expected magic number, and records whether the failed handshake was for encryption.

Important APIs and types: `InvalidMagicNumberException` extends `IOException`. The constructor formats the received value against `DataTransferSaslUtil.SASL_TRANSFER_MAGIC_NUMBER` and stores `handshake4Encryption`. `isHandshake4Encryption()` exposes that flag.

Control flow: Created by SASL negotiation code immediately after reading an unexpected magic number.

State and persistence behavior: Carries the formatted message, stack trace, and boolean handshake context for error handling. No persistent state is changed.

Dependencies and integration points: Depends on `DataTransferSaslUtil.SASL_TRANSFER_MAGIC_NUMBER` and is thrown by `SaslDataTransferServer`/related SASL paths when peers speak the wrong preamble or an old/non-SASL protocol.

Risks: The magic number is logged/formatted in hex; diagnostics depend on accurately preserving the received value. The encryption flag affects client/server interpretation of fallback or error behavior.

Test signals: Tests should feed invalid magic numbers for encrypted and non-encrypted handshakes, assert message contents and `isHandshake4Encryption()`, and verify caller error handling.

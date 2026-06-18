# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/DataTransferSaslUtil.java

## Purpose
`DataTransferSaslUtil` implements shared SASL negotiation helpers for HDFS data transfer. It handles QOP validation, configuration translation, SASL message framing, cipher-suite negotiation, crypto stream wrapping, and protocol-specific error mapping.

## Important APIs, Types, and Functions
`SASL_TRANSFER_MAGIC_NUMBER` is `0xDEADBEEF`, sent by clients to identify SASL negotiation instead of a normal data transfer version. `checkSaslComplete` verifies completion and ensures negotiated QOP is one of the requested values, treating null as `auth`. `requestedQopContainsPrivacy` checks for `auth-conf`.

`createSaslPropertiesForEncryption` builds privacy SASL properties with server auth and a digest cipher algorithm. `encryptionKeyToPassword` base64-encodes encryption keys for SASL password use. `getPeerAddress` parses a `Peer` remote address string into an `InetAddress`.

`getSaslPropertiesResolver` translates `dfs.data.transfer.protection` into `hadoop.rpc.protection`, selects the resolver class, and returns null when data transfer SASL protection is not configured.

SASL message readers parse `DataTransferEncryptorMessageProto` via `vintPrefixed`; `ERROR_UNKNOWN_KEY` maps to `InvalidEncryptionKeyException`, access-token errors map to `InvalidBlockTokenException`, generic errors map to `IOException`, and success invokes a handler. Variants read payloads, negotiation cipher options, negotiated cipher option, or handshake secrets.

`negotiateCipherOption` accepts configured AES/CTR/NoPadding or SM4/CTR/NoPadding, generates in/out keys and IVs through `CryptoCodec`, and returns a `CipherOption` if the client offered a supported suite. `createStreamPair` wraps underlying streams in `CryptoInputStream` and `CryptoOutputStream`, reversing in/out keys depending on server/client side. `wrap` and `unwrap` protect cipher keys through the SASL participant. Send helpers write delimited `DataTransferEncryptorMessageProto` messages with status, payload, optional cipher options, optional handshake secret, and optional access-token error flag.

## Control Flow
The negotiation flow uses delimited protobuf messages after the magic number. Client and server exchange SASL payloads, optionally negotiate a cipher suite when privacy is requested, validate QOP, unwrap/wrap cipher keys, and finally switch to either SASL streams or crypto streams.

## State and Persistence Behavior
The class is stateless. Negotiated keys/IVs are generated per handshake and are not persisted. Configuration drives resolver selection, QOP, cipher suite, and key bit length.

## Dependencies and Integration Points
It depends on Hadoop configuration keys, `SaslPropertiesResolver`, Java SASL constants, crypto APIs (`CipherOption`, `CipherSuite`, `CryptoCodec`, crypto streams), HDFS peer/protobuf/PB helper classes, block token exceptions, and shaded protobuf/Guava. It is used by `SaslDataTransferClient` and server-side SASL data transfer code.

## Risks and Edge Cases
Security risks are high: QOP validation must reject downgrade, cipher suite config must reject unsupported names, key/IV direction must be correct for client vs server, and protocol errors must retain specific exception types for retry. `getPeerAddress` depends on remote address string format. `assert codec != null` is not a runtime check when assertions are disabled, so invalid crypto provider setup can fail later. Only one configured cipher suite string is accepted.

## Test Signals
`TestEncryptedTransfer` and `TestSaslDataTransfer` cover encrypted and SASL negotiation. Focused tests should cover QOP validation, no-config resolver returning null, invalid cipher suite errors, AES and SM4 negotiation, error status mapping, handshake secret read/write, access-token error mapping, and stream key direction.

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/HdfsKMSUtil.java

`HdfsKMSUtil` centralizes HDFS client key-provider and encrypted-input helpers. It resolves KMS provider URIs, validates encryption metadata, obtains crypto codecs, decrypts encrypted data encryption keys, and wraps encrypted input streams.

Important APIs are `createKeyProvider()`, `getCryptoProtocolVersion()`, `getCryptoCodec()`, `getKeyProviderUri()`, `getKeyProvider()`, `getKeyProviderMapKey()`, `createWrappedInputStream()`, and package-visible `decryptEncryptedDataEncryptionKey()`.

Provider URI resolution first checks UGI credential secrets keyed by NameNode URI, then uses the NameNode default KMS URI unless configured to ignore it, then falls back to local configuration. Resolved URIs are cached back into credentials. Stream wrapping validates protocol support, creates a codec for the cipher suite, decrypts the EDEK through `KeyProviderCryptoExtension`, and returns a `CryptoInputStream`.

State is static key-name configuration plus credential-secret caching on supplied UGIs; decrypted material is only passed into returned crypto streams. Dependencies include `KMSUtil`, `KeyProvider`, `KeyProviderTokenIssuer`, `FileEncryptionInfo`, `CryptoCodec`, `CryptoInputStream`, UGI credentials, and `DFSUtilClient`.

Risks include stale credential-cached KMS URIs, unsupported crypto protocol versions, unknown cipher suites, missing codec classes, missing key providers, and decrypt failures surfaced as `IOException`. Test signals include credential override, NameNode URI usage, ignore-NN-default behavior, local fallback, no-provider nulls, protocol/cipher errors, decrypt success/failure, and map-key shape.

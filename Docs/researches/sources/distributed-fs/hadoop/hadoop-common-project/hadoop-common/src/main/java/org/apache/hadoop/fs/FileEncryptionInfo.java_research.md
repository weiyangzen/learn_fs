# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileEncryptionInfo.java

## Purpose

`FileEncryptionInfo` is a private Hadoop value object that carries the encryption metadata needed to access an encrypted file. It records the cipher suite, crypto protocol version, encrypted data encryption key, initialization vector, encryption-zone key name, and encryption-zone key-version name.

The class is serializable and immutable by field reference. It is not a cryptographic engine; it is metadata passed between filesystem implementations, clients, and encryption-aware code.

## Important APIs and types

- Constructor: `FileEncryptionInfo(CipherSuite suite, CryptoProtocolVersion version, byte[] edek, byte[] iv, String keyName, String ezKeyVersionName)`.
- Accessors: `getCipherSuite`, `getCryptoProtocolVersion`, `getEncryptedDataEncryptionKey`, `getIV`, `getKeyName`, and `getEzKeyVersionName`.
- Stringification: `toString` and `toStringStable`, both currently rendering the same fields, with EDEK and IV hex-encoded through Apache Commons Codec `Hex`.

## Control flow

Construction is the only meaningful control path. It checks all arguments for non-null values and validates that `iv.length` equals `suite.getAlgorithmBlockSize()`. After validation, all constructor arguments are assigned to final fields.

Getter methods return the stored values directly. `toString` and `toStringStable` build a structured string with cipher/protocol names and hex encodings of the key material bytes.

## State and persistence behavior

The object holds final references to encryption metadata. It implements `Serializable` with a fixed `serialVersionUID`, but it does not define custom Java serialization or Hadoop `Writable` behavior. The `byte[]` fields are not defensively copied on construction or on getter return, so external code retaining the input arrays or mutating arrays returned by getters can change the object's effective contents.

The class exposes EDEK and IV in `toString`/`toStringStable` as hex strings. These are encrypted or public-ish operational metadata rather than plaintext keys, but they remain sensitive diagnostic material.

## Dependencies and integration points

The class depends on `CipherSuite` and `CryptoProtocolVersion` from `org.apache.hadoop.crypto`, Hadoop `Preconditions`, Apache Commons Codec hex encoding, and Java serialization. It is used by filesystem encryption integration points, especially HDFS encryption zones and client-side stream setup that needs key material identifiers and IVs.

`toStringStable` is explicitly preserved for CLI backward compatibility, making its output format part of a user-visible compatibility surface even though the class itself is private audience.

## Risks and edge cases

- Byte-array aliasing allows mutation after construction and through getters.
- `toString` prints hex EDEK and IV, so logs containing this object may expose encryption metadata.
- Only IV length is validated against the cipher suite; EDEK length and key-version naming semantics are left to producers/consumers.
- `toStringStable` currently duplicates `toString`, so future field additions must avoid changing `toStringStable` unless a major compatibility break is intended.

## Test signals

Tests should cover constructor null rejection for every parameter, IV length validation against the selected `CipherSuite`, accessor round trips, byte-array aliasing expectations, stable string output compatibility, and hex rendering of EDEK/IV values. Integration tests should validate that encrypted file status/open paths preserve key name and EZ key-version metadata.

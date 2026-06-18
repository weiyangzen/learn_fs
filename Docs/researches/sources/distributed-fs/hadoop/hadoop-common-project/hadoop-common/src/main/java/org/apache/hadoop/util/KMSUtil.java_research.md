# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/KMSUtil.java

## Purpose

`KMSUtil` provides utility conversions and provider lookup helpers for Hadoop Key Management Server clients and key-provider metadata.

## Important APIs, Types, And Functions

Important APIs include `getKeyProvider(Configuration, String)`, `createKeyProviderFromUri(Configuration, URI)`, metadata-to/from-map conversion, encrypted-key-version serialization/deserialization helpers, and base64 material encoding/decoding. It handles KMS REST field names from `KMSRESTConstants`.

## Control Flow, State, And Persistence

Provider lookup resolves URIs through `KeyProviderFactory` and validates that a provider exists. Conversion helpers map `KeyProvider.Metadata`, key versions, and `EncryptedKeyVersion` objects to REST-compatible `Map` structures and back, including dates, versions, cipher, bit length, description, attributes, IV, encrypted material, and encryption key/version names. State is transient conversion data; persistence occurs in external KMS/key-provider systems.

## Dependencies And Integration Points

It depends on Commons Codec `Base64`, Hadoop `Configuration`, `KeyProvider`, `KeyProviderFactory`, `KMSClientProvider`, `KMSRESTConstants`, and KMS crypto extension types. It is a bridge between Java key-provider APIs and REST payloads.

## Risks And Test Signals

Incorrect map keys or base64 conversions can make encrypted keys undecryptable or incompatible across KMS versions. Tests should cover provider URI success/failure, metadata round trips, encrypted-key round trips, null/optional attributes, date handling, and malformed REST maps.

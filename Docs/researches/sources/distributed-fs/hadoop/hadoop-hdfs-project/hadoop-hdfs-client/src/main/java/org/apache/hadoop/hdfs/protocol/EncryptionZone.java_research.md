# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/EncryptionZone.java

## Purpose
`EncryptionZone` is a public/evolving DTO representing an HDFS encryption zone. It carries a unique ID for batched listing, the zone root path, cipher suite, crypto protocol version, and key name.

## APIs and Behavior
The constructor initializes final fields. Accessors expose all fields. `equals`, `hashCode`, and `toString` include ID, path, suite, version, and key name, using Commons Lang builders for equality/hash.

## State, Dependencies, and Integration
The object is immutable and integrates with `ClientProtocol.getEZForPath`, `listEncryptionZones`, `EncryptionZoneIterator`, and file encryption metadata. Dependencies include Hadoop crypto types `CipherSuite` and `CryptoProtocolVersion`.

## Risks and Test Signals
The class performs no null validation, so malformed protocol conversion can create zones with missing suite/version/key. Tests should cover equality, listing cursor IDs, string rendering without leaking sensitive key material beyond key name, and compatibility across crypto protocol versions.

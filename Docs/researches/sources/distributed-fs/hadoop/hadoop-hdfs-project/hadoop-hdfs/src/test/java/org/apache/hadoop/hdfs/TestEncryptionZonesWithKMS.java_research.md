# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestEncryptionZonesWithKMS.java

## Purpose
Runs the base encryption-zone suite with a MiniKMS-backed provider and adds KMS-specific tests for EDEK cache population, cache warmup after NameNode restart, and KMS delegation-token retrieval through DFS and WebHDFS.

## Important APIs and Types
Extends `TestEncryptionZones`. Uses `MiniKMS`, `KMSClientProvider`, `LoadBalancingKMSClientProvider`, `KMSDelegationToken`, `Whitebox.getInternalState`, `WebHdfsFileSystem.addDelegationTokens`, and NameNode EDEK cache loader configuration.

## Control Flow
`setup()` creates a unique MiniKMS config directory, starts MiniKMS, then invokes the inherited JKS-oriented setup with `getKeyProviderURI()` overridden to a `kms://` URI. `setProvider()` is intentionally empty because the KMS provider is resolved through configuration rather than manually installed into the DFS client. Extra tests create zones and inspect the underlying KMS client queue, call `fs.addDelegationTokens` twice to verify token reuse, restart the NameNode with zero EDEK cache-loader delay and wait for cache refill, and validate that WebHDFS returns a KMS delegation token.

## State, Persistence, Dependencies, Integration
State includes MiniKMS process/configuration, KMS client provider queues, NameNode EDEK cache state, and user credentials. Integration points are the inherited encryption-zone tests plus real KMS protocol wiring, delegation-token extension support, and cache-loader startup behavior.

## Risks and Test Signals
Signals are positive queue sizes for zone keys, stable token counts, KMS token kind from WebHDFS, and cache refill after restart. Risks include MiniKMS lifecycle failures and reflective access to provider internals, but the subclass gives stronger coverage than mocked providers.

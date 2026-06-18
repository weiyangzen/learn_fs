# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/DefaultS3ClientFactory.java

Purpose: default S3A factory for AWS SDK v2 synchronous clients, asynchronous clients, and transfer managers. It centralizes HTTP client setup, endpoint/region configuration, request checksum policy, credentials, S3 Express session behavior, plugins, metrics, retry policy, custom headers, requester-pays, user agent suffix, access grants, and optional HTTP signer configuration.

Important APIs/types: extends `Configured` and implements `S3ClientFactory`. Public methods are `createS3Client(URI, S3ClientCreationParameters)`, `createS3AsyncClient(URI, S3ClientCreationParameters)`, and `createS3TransferManager(S3AsyncClient)`. Internal helpers include generic `configureClientBuilder`, protected `createClientOverrideConfiguration`, `configureEndpointAndRegion`, static `getS3Endpoint`, static `getS3RegionFromEndpoint`, and `maybeApplyS3AccessGrantsConfigurations`.

Control flow: sync client creation builds an Apache HTTP client with proxy config, then applies shared builder settings. Async client creation builds a Netty client, configures multipart thresholds, and enables multipart only when client-side encryption and analytics accelerator are disabled. Shared configuration sets endpoint/region, optional MD5 plugin, checksum calculation/validation modes, S3 Access Grants, path-style access, override config, credential provider, S3 Express session auth, metrics, and optional custom HTTP signer.

State and persistence behavior: factory is mostly stateless beyond inherited Hadoop `Configuration` and exactly-once loggers. Created clients hold configured connection pools, credentials, metrics publishers, plugins, and region/endpoint state.

Dependencies and integration points: depends heavily on AWS SDK v2 S3, HTTP, retry, metrics, and plugin APIs; Hadoop `AWSClientConfig`; S3A constants; signer factory; request factory parameters; and S3A instrumentation. It is the integration point where user config becomes actual AWS SDK client behavior.

Risks: endpoint/region decisions are subtle. FIPS mode rejects non-central endpoints; central endpoint avoids explicit override to prevent AWS SDK issue behavior; empty configured region intentionally falls back to SDK region chain; absent region uses `us-east-2` for cross-region access. Multipart async behavior is disabled with CSE or analytics accelerator. Checksum and MD5 defaults can affect third-party S3 stores.

Test signals: tests should cover endpoint URI normalization, secure vs insecure protocol, VPC endpoint region parsing, central endpoint fallback, FIPS rejection, cross-region flag, requester-pays header, custom headers, user-agent suffix, metrics publisher, access grants plugin and fallback, HTTP signer activation, async multipart gating, and checksum/MD5 policies.

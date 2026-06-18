# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/HdfsDtFetcher.java

Purpose: Implements the `DtFetcher` SPI for HDFS delegation token acquisition. It lets generic token-fetching tools obtain HDFS tokens without compile-time coupling to a specific filesystem implementation.

Important APIs and functions: `getServiceName()` returns `hdfs`. `isTokenRequired()` delegates to `UserGroupInformation.isSecurityEnabled()`. `addDelegationTokens(Configuration, Credentials, String, String)` normalizes an HDFS URL, opens a `FileSystem`, requests a delegation token for the renewer, adds it to `Credentials`, and returns it.

Control flow: If the supplied URL lacks the `hdfs` scheme prefix, the method prepends `hdfs://`. It creates the filesystem from the URI and configuration, calls `getDelegationToken`, errors if null, then stores the token under its service.

State and persistence behavior: The fetcher itself is stateless. Successful calls mutate the supplied `Credentials` by adding the token. Any persistent token storage is handled by the caller that owns those credentials.

Dependencies and integration points: Depends on Hadoop `DtFetcher`, `FileSystem`, `Credentials`, UGI, token APIs, `HdfsConstants.HDFS_URI_SCHEME`, and runtime SPI discovery. `WebHdfsDtFetcher` and `SWebHdfsDtFetcher` reuse this implementation with different schemes.

Risks: URL normalization is simple prefix checking; malformed authorities can still flow to `FileSystem.get`. A null token is escalated as an IOException after logging. The filesystem object is not explicitly closed here, relying on `FileSystem` caching/lifecycle.

Test signals: Token fetch tests should cover secure vs insecure `isTokenRequired`, URLs with and without scheme, token addition to credentials, null token failure, invalid URI handling, and SPI lookup for the HDFS service name.

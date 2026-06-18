# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsTokens.java

## Purpose
`TestWebHdfsTokens` validates WebHDFS and SWebHDFS delegation-token behavior across simple, Kerberos-secured, token-only, and expired-token flows. It focuses on when `WebHdfsFileSystem.toUrl` should fetch tokens, which HTTP operations require Kerberos authentication instead of a delegation token, and whether token service/kind values returned by NameNode JSON survive conversion into Hadoop `Token` objects.

## Important APIs, types, and functions
- `initEnv()` sets Kerberos mode on the shared `conf` and installs a testing login user, giving mock WebHDFS instances a secure-client context without starting a cluster.
- `initSecureConf(Configuration)` creates a `MiniKdc`, principal/keytab files, SPNEGO HTTP authentication settings, HDFS Kerberos principals, block tokens, HTTPS keystore resources, and HTTP/HTTPS listener addresses for a secure `MiniDFSCluster`.
- `spyWebhdfsInSecureSetup()` initializes a `WebHdfsFileSystem` against `webhdfs://127.0.0.1:0` and wraps it with Mockito.
- `checkNoTokenForOperation(HttpOpParam.Op)` asserts that token management operations do not recursively fetch or install delegation tokens.
- `validateLazyTokenFetch(UserGroupInformation, Configuration)` is the core integration scenario. It creates WebHDFS clients as a Kerberos UGI, performs token ops and ordinary file ops, cancels/renews tokens, checks replacement of expired tokens, closes file systems, and verifies interaction counts on token methods.
- `getTokenOwner(Token<?>)` clones a WebHDFS token, changes its kind to `HDFS_DELEGATION_KIND`, decodes the identifier, and returns the token owner.

## Control flow
The light tests use a spied `WebHdfsFileSystem` to call `toUrl` for different operation classes and verify token-fetch call counts. The operation-class tests iterate all `GetOpParam`, `PutOpParam`, `PostOpParam`, and `DeleteOpParam` values and assert only delegation-token management operations require auth. `testLazyTokenFetchForWebhdfs` builds a real secure MiniDFSCluster once, logs in via keytab, and runs the same lazy-token lifecycle against both `swebhdfs` and `webhdfs` URIs. `testSetTokenServiceAndKind` starts a mostly simple cluster but enables delegation-token use, injects a custom `URLConnectionFactory` that appends `service=foo&kind=bar`, and verifies both `getDelegationToken` and a lower-level `FsPathResponseRunner` decode token kind/service correctly.

## State and persistence behavior
The class owns static MiniKdc state, keytab/keystore directories, principal strings, and shared `conf`. The secure flow writes temporary KDC/keytab/SSL files under `GenericTestUtils.getTestDir` and classpath SSL config directories, then removes them in `destroy()`. `validateLazyTokenFetch` mutates the active UGI token set and WebHDFS internal renew token; it explicitly resets UGI after the secure cluster test to avoid leaking Kerberos mode into later tests.

## Dependencies and integration points
This test integrates `MiniKdc`, `MiniDFSCluster`, Hadoop HTTP authentication filters, `KeyStoreTestUtil`, `WebHdfsFileSystem`, `JsonUtilClient`, WebHDFS resource parameters, and HDFS delegation-token identifiers. Mockito is used to assert client-internal call order without replacing server-side token logic. It depends on HDFS configs for HTTPS, Kerberos principals, block access tokens, data-transfer protection, and forced NameNode delegation-token use.

## Risks and edge cases
The secure setup is expensive and sensitive to local host naming, Windows localhost behavior, keystore cleanup, and shared static UGI state. The tests intentionally use `127.0.0.1:0` for spy-only URL generation, so those branches do not validate real connectivity. `testSetTokenServiceAndKind` relies on appending query parameters through a custom connection factory; URL or JSON response changes could break the intended coverage. Token replacement assertions are interaction-count-sensitive and may fail if WebHDFS retry internals change while preserving behavior.

## Test signals
Strong signals include coverage for no-recursive-token-fetch on token operations, lazy token acquisition on first non-token op, reuse of renew tokens, expired-token replacement, UGI-provided token reuse/replacement rules, close-time token cancellation semantics, WebHDFS/SWebHDFS parity, and token kind/service parsing. Failures typically indicate regressions in WebHDFS auth query construction, delegation-token caching, expired-token recovery, or secure MiniDFSCluster setup.

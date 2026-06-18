# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/HttpFSKerberosAuthenticationHandlerForTesting.java

## Purpose
This test authentication handler avoids real Kerberos initialization while preserving delegation-token manager setup for HttpFS tests.

## Important APIs, Types, and Functions
It extends `KerberosDelegationTokenAuthenticationHandler`. `init(Properties config)` overrides the parent to call only `initTokenManager(config)`. `destroy()` is a no-op.

## Control Flow
When configured in tests, servlet authentication initialization skips Kerberos principal/keytab login and initializes only the token manager portions needed for token-related behavior.

## State and Persistence
It may initialize token manager state through the inherited helper. It does not create Kerberos login state and does not clean token manager state in `destroy`.

## Dependencies and Integration Points
It depends on Hadoop security's delegation-token web authentication handler and is intended for HttpFS server tests that need Kerberos-mode code paths without a KDC.

## Risks
Because `destroy` is a no-op, inherited cleanup is skipped; this is acceptable in short-lived tests but would not be suitable for production. It can mask bugs in real Kerberos initialization.

## Test Signals
The class is test-only infrastructure. It signals that HttpFS authentication tests distinguish token-manager behavior from real Kerberos login behavior.

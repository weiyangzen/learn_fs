<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSAuthenticationFilter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSAuthenticationFilter.java

## Purpose
`HttpFSAuthenticationFilter` customizes Hadoop delegation-token authentication for HttpFS. It pulls authentication properties from the active `HttpFSServerWebApp` configuration, loads the signing secret, exposes proxy-user configuration, and selects the WebHDFS or SWebHDFS delegation token kind based on SSL.

## Important APIs, Types, And Functions
The class extends `DelegationTokenAuthenticationFilter`. Constants define accepted configuration prefixes: `httpfs.authentication.` and `hadoop.http.authentication.`. `getConfiguration` uses `HttpServer2.getFilterProperties`, enforces a `signature.secret.file` property, reads the secret unless a random signer provider is already installed, calls `setAuthHandlerClass`, and sets `KerberosDelegationTokenAuthenticationHandler.TOKEN_KIND`. `getProxyuserConfiguration` rewrites `httpfs.proxyuser.*` properties to Hadoop proxyuser keys by removing the `httpfs.` prefix. `isRandomSecret` checks the servlet context's signer secret provider.

## Control Flow
During filter initialization, Hadoop auth calls `getConfiguration`. The method reads server config via the HttpFS singleton, materializes `Properties`, validates/reads the signature secret, configures the auth handler, and returns auth properties to the parent filter. Proxy user data is pulled separately by `getProxyuserConfiguration`.

## State And Persistence
The filter stores no long-lived local state. The signature secret is read from disk at initialization and injected into the returned properties. Proxy-user data remains in Hadoop `Configuration`.

## Dependencies And Integration Points
It integrates with `HttpFSServerWebApp`, `HttpFSServerWebServer.SSL_ENABLED_KEY`, Hadoop auth, delegation-token handlers, servlet context signer providers, and WebHDFS token-kind constants.

## Risks
Missing, unreadable, or empty signature secret files fail initialization. Random secret mode bypasses file reading only when the servlet context provider class is exactly `RandomSignerSecretProvider`. Prefix rewriting for proxy users depends on the `httpfs.` prefix length and should be kept consistent with auth config names.

## Test Signals
Tests should cover secret-file loading, empty secret rejection, random-secret bypass, SSL vs non-SSL token kind, and proxyuser key rewriting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/HttpFSAuthenticationFilter.java -->

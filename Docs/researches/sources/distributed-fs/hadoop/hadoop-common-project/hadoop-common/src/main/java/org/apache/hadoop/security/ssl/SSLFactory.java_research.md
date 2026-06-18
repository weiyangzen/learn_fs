# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/SSLFactory.java

## Purpose

`SSLFactory` creates configured SSL contexts, engines, socket factories, and hostname verifiers for Hadoop HTTP clients and servers.

## Important APIs, Types, and Functions

It defines mode enum `CLIENT`/`SERVER`, config keys for client/server SSL resources, client cert requirements, hostname verifier, enabled protocols, keystore/truststore settings, and cipher include/exclude lists. Key methods are constructor, `readSSLConfiguration`, `init`, `destroy`, `createSSLEngine`, `createSSLServerSocketFactory`, `createSSLSocketFactory`, `getHostnameVerifier`, `isClientCertRequired`, and `configure(HttpURLConnection)`.

## Control Flow

The constructor reads the mode-specific SSL configuration resource or falls back to input config if unavailable, instantiates the configured `KeyStoresFactory`, reads enabled protocols and cipher filters, and stores client-cert requirements. `init` initializes stores, creates a TLS `SSLContext`, initializes it with key/trust managers, caches client socket factory, and resolves hostname verifier. Server engines set server mode, client auth, enabled protocols, and filtered cipher suites. HTTPS connections are configured with the client socket factory and verifier.

## State and Persistence Behavior

State includes configuration, mode, SSL context, cached socket factory, hostname verifier, keystores factory, enabled protocols, and cipher filters. It reads XML config and keystore/truststore files through the keystore factory; persistence is external.

## Dependencies and Integration Points

It depends on JSSE, `FileBasedKeyStoresFactory` by default, Hadoop `Configuration`, `ReflectionUtils`, `ConnectionConfigurator`, `SSLHostnameVerifier`, and Hadoop HTTP client/server setup.

## Risks and Edge Cases

Mode-specific methods throw if called in the wrong mode. Fallback to input configuration only occurs when the SSL resource is not loadable. Cipher include/exclude filters can produce an empty enabled suite list. `context.getDefaultSSLParameters().setProtocols` does not itself configure all future sockets; engines are explicitly configured.

## Test Signals

Tests should cover client/server modes, missing mode rejection, SSL resource fallback, custom keystore factory, verifier name selection and invalid verifier failure, enabled protocol setting, cipher include/exclude filtering, HTTPS configuration, and destroy delegation.

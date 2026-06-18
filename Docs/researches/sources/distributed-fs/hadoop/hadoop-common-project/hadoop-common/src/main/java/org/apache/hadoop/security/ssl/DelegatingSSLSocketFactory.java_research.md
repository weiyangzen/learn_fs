# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/DelegatingSSLSocketFactory.java

## Purpose

`DelegatingSSLSocketFactory` is a singleton `SSLSocketFactory` that can use WildFly OpenSSL or JSSE, with compatibility modes for Java 8 GCM cipher behavior.

## Important APIs, Types, and Functions

The `SSLChannelMode` enum includes `OpenSSL`, `Default`, `Default_JSSE`, and `Default_JSSE_with_GCM`. Static APIs are `initializeDefaultFactory`, `getDefaultFactory`, and test-only `resetDefaultFactory`. Instance APIs expose provider name, channel mode, cipher suites, and all socket creation overloads.

## Control Flow

Initialization creates the singleton once. `Default` attempts OpenSSL registration and `openssl.TLS` context initialization, falling back to JSSE on linkage/algorithm/runtime errors. Explicit `OpenSSL` fails if binding fails. JSSE modes use the default context. On Java 8 in `Default_JSSE`, GCM cipher suites are removed before sockets are configured.

## State and Persistence Behavior

State is a static singleton plus instance provider name, SSL context, selected ciphers, channel mode, and OpenSSL registration flag. No file persistence is used.

## Dependencies and Integration Points

It depends on JSSE, WildFly OpenSSL by fully qualified reference inside the binding method, SLF4J, and Java util logging. It is primarily used by Hadoop components that optionally prefer OpenSSL-backed sockets.

## Risks and Edge Cases

`getDefaultFactory` may return null if initialization was not called. Singleton initialization means later preferred modes are ignored until reset in tests. Cipher filtering only removes `_GCM_` names in one mode on Java 8. OpenSSL provider loading depends on optional classpath/native setup.

## Test Signals

Tests should cover each mode, default fallback, singleton reset, provider name, cipher list cloning, Java 8 GCM filtering, all socket overloads setting enabled ciphers, and behavior when WildFly OpenSSL is absent.

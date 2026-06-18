# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestWildflyAndOpenSSLBinding.java

## Purpose

`TestWildflyAndOpenSSLBinding.java` validates S3A network binding for SSL channel modes, especially graceful downgrade behavior when WildFly OpenSSL classes or native libraries are unavailable.

## Important APIs, Types, and Functions

The suite tests `NetworkBinding.bindSSLChannelMode(Configuration, ApacheHttpClient.Builder)` with `DelegatingSSLSocketFactory.SSLChannelMode` values `Default`, `OpenSSL`, `Default_JSSE`, and `Default_JSSE_with_GCM`. `setup()` detects `org.wildfly.openssl.OpenSSLProvider` on the classpath.

## Control Flow

Each test resets the default socket factory, sets `SSL_CHANNEL_MODE`, invokes the binding helper, and inspects the resulting `DelegatingSSLSocketFactory` channel mode. Assumptions split WildFly-present and WildFly-absent paths.

## State and Persistence Behavior

The test mutates global `DelegatingSSLSocketFactory` default state and resets it before each bind. Configuration state is local and no network calls are made.

## Dependencies and Integration Points

This covers Apache AWS SDK HTTP client setup, Hadoop SSL socket factory selection, and optional WildFly OpenSSL provider discovery.

## Risks and Edge Cases

Global socket-factory state makes reset behavior critical. The OpenSSL outcome is environment-sensitive: WildFly classes may exist without native OpenSSL loading successfully.

## Test Signals

Signals include `IllegalArgumentException` for an unknown mode, `NoClassDefFoundError` when OpenSSL is requested without WildFly, downgrade from `Default` to `Default_JSSE` without WildFly, and exact JSSE/GCM mode preservation.
